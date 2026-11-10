"""Shared causal multiscale-DC research utilities for roadmap phases 20-24.

This module is intentionally research-scoped. Phase 25 will decide the final
package boundaries after the exploratory representation and model contracts are
understood. No function in this module constructs a trading signal.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

from dc_basics.core import dc_live_features, parse_dc_events
from dc_basics.data import load_close, ratio_ladder, threshold_catalog, validate_thresholds
from dc_basics.enums import DcMode
from dc_basics.events import prepare_threshold_event_ledger
from dc_basics.live import build_causal_running_extreme


class StructuralRegime(StrEnum):
    BROAD_COHERENCE = "broad_coherence"
    SHALLOW_COUNTER = "shallow_counter"
    DEEP_COUNTER = "deep_counter"
    FRAGMENTED = "fragmented"


class ObservationClock(StrEnum):
    BAR = "bar_time"
    UNION_EVENT = "union_event_time"


class FeatureTier(StrEnum):
    STRUCTURAL = "structural"
    DYNAMIC = "dynamic"
    FULL = "full"


class ModelFamily(StrEnum):
    KMEANS = "kmeans"
    GAUSSIAN_MIXTURE = "gaussian_mixture"
    NORMAL_HMM = "normal_hmm"
    STUDENTT_HMM = "studentt_hmm"


REGIME_ORDER = (
    StructuralRegime.BROAD_COHERENCE.value,
    StructuralRegime.SHALLOW_COUNTER.value,
    StructuralRegime.DEEP_COUNTER.value,
    StructuralRegime.FRAGMENTED.value,
)
REGIME_CODE = {label: code for code, label in enumerate(REGIME_ORDER)}
MODE_MAP = {1.0: DcMode.UP.value, -1.0: DcMode.DOWN.value}
UNMATCHED_REGIME_CODE = -1
MIN_CONTINUOUS_UNIQUE_VALUES = 3
DEFAULT_MIN_EMISSION_VARIANCE = 1e-2
# A single repeated training value covering at least this share of rows behaves like a category.
# Example: at union events the scale that just fired has mode age 0 and reversal progress 0, so
# ``log1p_mode_age_00`` is exactly 0 on about half the GBPUSD training rows. A Gaussian or Student-t
# state can isolate such a point mass with its variance pinned at the floor and gain likelihood that
# says nothing about the continuous part of the feature.
DEFAULT_MAX_POINT_MASS_SHARE = 0.20
# Warn when preparation drops more than this share of any structural class.
MAX_SILENT_CLASS_DROP_SHARE = 0.01


@dataclass(frozen=True)
class TimeSplit:
    train_end: pd.Timestamp
    validation_end: pd.Timestamp


@dataclass
class PreparedData:
    clock: ObservationClock
    tier: FeatureTier
    feature_columns: list[str]
    frame: pd.DataFrame
    split: TimeSplit
    scaler: StandardScaler
    frames: dict[str, pd.DataFrame]
    arrays: dict[str, np.ndarray]
    removed_feature_columns: tuple[str, ...]
    dropped_rows: int
    dropped_regime_counts: dict[str, int]
    removed_feature_reasons: dict[str, str] = field(default_factory=dict)
    training_point_mass_share: dict[str, float] = field(default_factory=dict)


@dataclass
class CandidateFit:
    family: ModelFamily
    n_states: int
    random_state: int
    model: Any
    states: dict[str, np.ndarray]
    probabilities: dict[str, np.ndarray]
    mapped_regimes: dict[str, np.ndarray]
    semantic_map: dict[int, int | None]
    log_likelihoods: dict[str, float]
    confidence_scale: float | None
    min_emission_variance: float
    error: str | None = None


@dataclass
class CandidateSelection:
    fits: list[CandidateFit]
    table: pd.DataFrame
    stability: pd.DataFrame
    selected_fit: CandidateFit | None


def _configuration_lookup(threshold_count: int) -> dict[int, str]:
    lookup = {}
    for code in range(2**threshold_count):
        modes = [DcMode.UP.value if code & (1 << index) else DcMode.DOWN.value for index in range(threshold_count)]
        lookup[code] = "/".join(modes)
    return lookup


def _causal_running_extreme(prices: pd.Series, live: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return the live mode's causal running extreme, its age in bars, and a run identifier.

    The extreme itself comes from :func:`dc_basics.live.build_causal_running_extreme`, the same
    primitive the three-to-five-scale live notebooks use, so there is one implementation.
    """
    mode = live["direction"]
    known = mode.notna()
    mode_start = known & mode.ne(mode.shift())
    run_id = mode_start.cumsum()
    positions = np.arange(len(prices), dtype=np.int64)
    start_position = pd.Series(np.where(mode_start, positions, np.nan), index=prices.index).ffill()
    age = pd.Series(positions - start_position, index=prices.index, dtype=np.float64).where(known)
    extreme = build_causal_running_extreme(prices, live)
    return extreme, age, run_id


def build_multiscale_state(
    prices: pd.Series, thresholds: tuple[float, ...], firing_window: int = 240, include_scale_state: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None]:
    validate_thresholds(thresholds)
    if firing_window < 1:
        raise ValueError("firing_window must be positive.")
    catalog = threshold_catalog(thresholds)
    threshold_count = len(thresholds)
    positions = np.arange(len(prices), dtype=np.int64)
    matrices: dict[str, list[np.ndarray]] = {
        "mode_sign": [],
        "mode_age": [],
        "live_tmv": [],
        "live_t": [],
        "live_r": [],
        "progress": [],
        "dcc": [],
        "dcc_count": [],
        "dcc_rate": [],
        "completed_tmv": [],
        "completed_t": [],
        "completed_r": [],
    }
    scale_parts = []

    for threshold_index, theta in enumerate(thresholds):
        threshold_id = f"T{threshold_index + 1:02d}"
        live = dc_live_features(prices, theta=theta)
        events = prepare_threshold_event_ledger(
            parse_dc_events(prices=prices, theta=theta), threshold_id, threshold_index, theta
        )
        event_lookup = events.set_index("dcc_idx")

        extreme, mode_age, run_id = _causal_running_extreme(prices, live)
        upward_progress = (prices - extreme) / extreme / theta
        downward_progress = (extreme - prices) / extreme / theta
        progress = pd.Series(
            np.where(live["direction"].eq(1.0), downward_progress, upward_progress),
            index=prices.index,
            dtype=np.float64,
        ).where(live["direction"].notna())
        dcc = (live["upward_dcc"] | live["downward_dcc"]).astype(bool)
        dcc_count = dcc.astype(np.int64).rolling(firing_window, min_periods=1).sum()
        completed_tmv = prices.index.to_series().map(event_lookup["tmv"]).ffill()
        completed_t = prices.index.to_series().map(event_lookup["t"]).ffill()
        completed_r = prices.index.to_series().map(event_lookup["r"]).ffill()
        max_live_tmv = live["tmv_current"].groupby(run_id).cummax().where(live["direction"].notna())

        matrices["mode_sign"].append(live["direction"].to_numpy(dtype=np.float64))
        matrices["mode_age"].append(mode_age.to_numpy(dtype=np.float64))
        matrices["live_tmv"].append(live["tmv_current"].to_numpy(dtype=np.float64))
        matrices["live_t"].append(live["t_current"].to_numpy(dtype=np.float64))
        matrices["live_r"].append(live["rdc_current"].to_numpy(dtype=np.float64))
        matrices["progress"].append(progress.to_numpy(dtype=np.float64))
        matrices["dcc"].append(dcc.to_numpy(dtype=bool))
        matrices["dcc_count"].append(dcc_count.to_numpy(dtype=np.float64))
        matrices["dcc_rate"].append((dcc_count / firing_window).to_numpy(dtype=np.float64))
        matrices["completed_tmv"].append(completed_tmv.to_numpy(dtype=np.float64))
        matrices["completed_t"].append(completed_t.to_numpy(dtype=np.float64))
        matrices["completed_r"].append(completed_r.to_numpy(dtype=np.float64))

        if include_scale_state:
            event_id = prices.index.to_series().map(event_lookup["event_id"])
            completed_information_time = prices.index.to_series().map(event_lookup["information_time"]).ffill()
            scale_parts.append(pd.DataFrame({
                "time": prices.index,
                "feature_information_time": prices.index,
                "bar_position": positions,
                "threshold_index": threshold_index,
                "threshold_id": threshold_id,
                "threshold": theta,
                "price": prices.to_numpy(dtype=np.float64),
                "mode": live["direction"].map(MODE_MAP).to_numpy(),
                "mode_sign": live["direction"].to_numpy(dtype=np.float64),
                "mode_age_bars": mode_age.to_numpy(dtype=np.float64),
                "upward_dcc": live["upward_dcc"].to_numpy(dtype=bool),
                "downward_dcc": live["downward_dcc"].to_numpy(dtype=bool),
                "dcc_flag": dcc.to_numpy(dtype=bool),
                "dcc_event_id": event_id.to_numpy(),
                "completed_event_information_time": completed_information_time.to_numpy(),
                "completed_tmv": completed_tmv.to_numpy(dtype=np.float64),
                "completed_t": completed_t.to_numpy(dtype=np.float64),
                "completed_r": completed_r.to_numpy(dtype=np.float64),
                "live_tmv": live["tmv_current"].to_numpy(dtype=np.float64),
                "live_t": live["t_current"].to_numpy(dtype=np.float64),
                "live_r": live["rdc_current"].to_numpy(dtype=np.float64),
                "max_live_tmv": max_live_tmv.to_numpy(dtype=np.float64),
                "running_extreme": extreme.to_numpy(dtype=np.float64),
                "reversal_progress": progress.to_numpy(dtype=np.float64),
                "dcc_count_window": dcc_count.to_numpy(dtype=np.float64),
                "dcc_rate_per_bar": (dcc_count / firing_window).to_numpy(dtype=np.float64),
            }))

    arrays = {name: np.column_stack(values) for name, values in matrices.items()}
    known = np.isfinite(arrays["mode_sign"]).all(axis=1)
    signs = arrays["mode_sign"][known].astype(np.int8)
    times = prices.index[known]
    known_positions = positions[known]
    boundaries = signs[:, :-1] != signs[:, 1:]
    boundary_count = boundaries.sum(axis=1).astype(np.int64)
    small_breadth = np.where(boundary_count > 0, np.argmax(boundaries, axis=1) + 1, threshold_count)
    outer_breadth = np.where(boundary_count > 0, np.argmax(boundaries[:, ::-1], axis=1) + 1, threshold_count)
    current_run = np.ones(len(times), dtype=np.int64)
    longest_run = np.ones(len(times), dtype=np.int64)
    for index in range(1, threshold_count):
        current_run = np.where(signs[:, index] == signs[:, index - 1], current_run + 1, 1)
        longest_run = np.maximum(longest_run, current_run)
    weights = 1 << np.arange(threshold_count, dtype=np.int64)
    configuration_code = ((signs > 0).astype(np.int64) * weights).sum(axis=1)
    configuration = pd.Series(configuration_code, index=times).map(_configuration_lookup(threshold_count))
    dcc_known = arrays["dcc"][known]
    dcc_count_this_bar = dcc_known.sum(axis=1).astype(np.int64)

    global_state = pd.DataFrame({
        "time": times,
        "feature_information_time": times,
        "bar_position": known_positions,
        "price": prices.iloc[known_positions].to_numpy(dtype=np.float64),
        "threshold_count": threshold_count,
        "configuration_code": configuration_code,
        "configuration": configuration.to_numpy(),
        "broad_agreement": boundary_count == 0,
        "coherent_frontier": boundary_count <= 1,
        "direction_boundaries": boundary_count,
        "directional_runs": boundary_count + 1,
        "fragmentation": boundary_count / (threshold_count - 1),
        "small_contiguous_breadth": small_breadth,
        "outer_contiguous_breadth": outer_breadth,
        "small_contiguous_fraction": small_breadth / threshold_count,
        "outer_contiguous_fraction": outer_breadth / threshold_count,
        "longest_directional_run": longest_run,
        "counter_scale_depth": np.where(
            boundary_count == 0, 0.0, np.where(boundary_count == 1, small_breadth, np.nan)
        ),
        "signed_mode_balance": signs.mean(axis=1),
        "outer_mode": np.where(signs[:, -1] > 0, DcMode.UP.value, DcMode.DOWN.value),
        "small_mode": np.where(signs[:, 0] > 0, DcMode.UP.value, DcMode.DOWN.value),
        "mean_mode_age_bars": np.nanmean(arrays["mode_age"][known], axis=1),
        "max_mode_age_bars": np.nanmax(arrays["mode_age"][known], axis=1),
        "mean_reversal_progress": np.nanmean(arrays["progress"][known], axis=1),
        "max_reversal_progress": np.nanmax(arrays["progress"][known], axis=1),
        "dcc_count_this_bar": dcc_count_this_bar,
        "union_event": dcc_count_this_bar > 0,
        "multi_scale_same_bar": dcc_count_this_bar > 1,
        "hierarchy_dcc_count_window": arrays["dcc_count"][known].sum(axis=1),
        "hierarchy_dcc_rate": arrays["dcc_rate"][known].mean(axis=1),
    }).set_index("time", drop=False)

    for index in range(threshold_count):
        suffix = f"{index:02d}"
        global_state[f"mode_sign_{suffix}"] = signs[:, index]
        global_state[f"mode_age_bars_{suffix}"] = arrays["mode_age"][known, index]
        global_state[f"live_tmv_{suffix}"] = arrays["live_tmv"][known, index]
        global_state[f"live_t_{suffix}"] = arrays["live_t"][known, index]
        global_state[f"live_r_{suffix}"] = arrays["live_r"][known, index]
        global_state[f"reversal_progress_{suffix}"] = arrays["progress"][known, index]
        global_state[f"dcc_flag_{suffix}"] = dcc_known[:, index]
        global_state[f"dcc_rate_{suffix}"] = arrays["dcc_rate"][known, index]
        global_state[f"completed_tmv_{suffix}"] = arrays["completed_tmv"][known, index]
        global_state[f"completed_t_{suffix}"] = arrays["completed_t"][known, index]
        global_state[f"completed_r_{suffix}"] = arrays["completed_r"][known, index]
        if index < threshold_count - 1:
            global_state[f"edge_disagreement_{suffix}"] = boundaries[:, index]

    global_state = add_interpretable_regimes(global_state)
    scale_state = pd.concat(scale_parts, ignore_index=True) if include_scale_state else None
    return catalog, global_state, scale_state


def add_interpretable_regimes(global_state: pd.DataFrame) -> pd.DataFrame:
    frame = global_state.copy()
    depth_fraction = frame["small_contiguous_breadth"] / frame["threshold_count"]
    broad = frame["direction_boundaries"].eq(0)
    coherent = frame["direction_boundaries"].eq(1)
    structural = np.select(
        [broad, coherent & depth_fraction.le(0.5), coherent & depth_fraction.gt(0.5)],
        [
            StructuralRegime.BROAD_COHERENCE.value,
            StructuralRegime.SHALLOW_COUNTER.value,
            StructuralRegime.DEEP_COUNTER.value,
        ],
        default=StructuralRegime.FRAGMENTED.value,
    )
    frame["counter_depth_fraction"] = np.where(coherent, depth_fraction, np.where(broad, 0.0, np.nan))
    frame["structural_regime"] = structural
    frame["structural_regime_code"] = frame["structural_regime"].map(REGIME_CODE).astype(np.int8)
    directed = np.where(
        broad,
        "broad_" + frame["outer_mode"].astype(str),
        np.where(
            coherent,
            frame["structural_regime"].astype(str)
            + "_"
            + frame["small_mode"].astype(str)
            + "_against_"
            + frame["outer_mode"].astype(str),
            "fragmented_outer_" + frame["outer_mode"].astype(str),
        ),
    )
    frame["directed_regime"] = directed
    return frame


def time_split(index: pd.DatetimeIndex, train_fraction: float = 0.60, validation_fraction: float = 0.20) -> TimeSplit:
    if train_fraction <= 0.0 or validation_fraction <= 0.0 or train_fraction + validation_fraction >= 1.0:
        raise ValueError("Fractions must define non-empty train, validation, and test partitions.")
    train_position = max(1, int(len(index) * train_fraction)) - 1
    validation_position = max(train_position + 1, int(len(index) * (train_fraction + validation_fraction))) - 1
    return TimeSplit(train_end=index[train_position], validation_end=index[validation_position])


def model_frame(global_state: pd.DataFrame, tier: FeatureTier) -> tuple[pd.DataFrame, list[str]]:
    """Build continuous-only emission features while retaining direct geometry for diagnostics.

    Mode signs, boundary counts, fragmentation, counter depth, and direction balance are
    discrete hierarchy descriptors. They remain in ``global_state`` and define the direct
    comparator, but feeding them to diagonal continuous densities rewards states that pin a
    category at the covariance floor. Emission tiers therefore use only causal continuous
    measurements. State relationships to the direct taxonomy are evaluated after fitting.
    """
    frame = global_state.copy()
    threshold_count = int(frame["threshold_count"].iloc[0])
    structural = []
    dynamic = []
    full = []
    for index in range(threshold_count):
        suffix = f"{index:02d}"
        age_column = f"log1p_mode_age_{suffix}"
        frame[age_column] = np.log1p(frame[f"mode_age_bars_{suffix}"])
        structural.extend([f"reversal_progress_{suffix}", age_column])
        live_tmv_column = f"log1p_live_tmv_{suffix}"
        live_r_column = f"log_live_r_{suffix}"
        frame[live_tmv_column] = np.log1p(frame[f"live_tmv_{suffix}"].clip(lower=0.0))
        frame[live_r_column] = np.log(frame[f"live_r_{suffix}"].clip(lower=1e-12))
        dynamic.extend([live_tmv_column, live_r_column])
        completed_tmv_column = f"log1p_completed_tmv_{suffix}"
        completed_t_column = f"log1p_completed_t_{suffix}"
        completed_r_column = f"log_completed_r_{suffix}"
        frame[completed_tmv_column] = np.log1p(frame[f"completed_tmv_{suffix}"].clip(lower=0.0))
        frame[completed_t_column] = np.log1p(frame[f"completed_t_{suffix}"].clip(lower=0.0))
        frame[completed_r_column] = np.log(frame[f"completed_r_{suffix}"].clip(lower=1e-12))
        full.extend([completed_tmv_column, completed_t_column, completed_r_column])

    structural.extend(["mean_reversal_progress", "max_reversal_progress"])
    columns = structural
    if tier in {FeatureTier.DYNAMIC, FeatureTier.FULL}:
        columns = columns + dynamic
    if tier is FeatureTier.FULL:
        columns = columns + full
    return frame, columns


def prepare_data(
    global_state: pd.DataFrame, clock: ObservationClock, tier: FeatureTier, split: TimeSplit | None = None,
    max_point_mass_share: float | None = DEFAULT_MAX_POINT_MASS_SHARE,
    frozen_feature_columns: list[str] | tuple[str, ...] | None = None,
) -> PreparedData:
    """Build the train-scaled continuous emission matrix for one clock and feature tier.

    Features are screened on the training partition only. A feature is removed when it is
    training-constant, has fewer than ``MIN_CONTINUOUS_UNIQUE_VALUES`` distinct values, or when one
    repeated value covers at least ``max_point_mass_share`` of training rows (a zero-inflated
    point mass that a continuous density would isolate at its variance floor). Pass ``None`` to
    disable the point-mass screen. Every removal is recorded with its reason.

    ``frozen_feature_columns`` skips the screen and uses exactly the given columns, in order. Use
    it when a feature set chosen on a pilot market must be transferred unchanged; point-mass
    shares are still recorded so a frozen feature that is zero-inflated elsewhere stays visible.
    """
    frame, feature_columns = model_frame(global_state, tier)
    if clock is ObservationClock.UNION_EVENT:
        frame = frame.loc[frame["union_event"]].copy()
    if split is None:
        split = time_split(global_state.index)
    if max_point_mass_share is not None and not 0.0 < max_point_mass_share <= 1.0:
        raise ValueError("max_point_mass_share must lie in (0, 1], or be None.")

    training_source = frame.loc[frame.index <= split.train_end]
    removed_feature_columns = []
    removed_feature_reasons: dict[str, str] = {}
    training_point_mass_share: dict[str, float] = {}
    retained_feature_columns = []
    if frozen_feature_columns is not None:
        unknown = sorted(set(frozen_feature_columns) - set(feature_columns))
        if unknown:
            raise ValueError(f"Frozen feature columns are not produced by tier {tier.value}: {unknown}")
    for column in feature_columns:
        finite = pd.to_numeric(training_source[column], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        point_mass_share = float(finite.value_counts(normalize=True).iloc[0]) if len(finite) else np.nan
        training_point_mass_share[column] = point_mass_share
        if frozen_feature_columns is not None:
            if column not in frozen_feature_columns:
                removed_feature_columns.append(column)
                removed_feature_reasons[column] = "not_in_frozen_feature_set"
            continue
        if finite.nunique() < MIN_CONTINUOUS_UNIQUE_VALUES or float(finite.std(ddof=0)) <= 1e-12:
            removed_feature_columns.append(column)
            removed_feature_reasons[column] = "training_constant_or_discrete"
        elif max_point_mass_share is not None and point_mass_share >= max_point_mass_share:
            removed_feature_columns.append(column)
            removed_feature_reasons[column] = f"point_mass_share_{point_mass_share:.3f}"
        else:
            retained_feature_columns.append(column)
    feature_columns = list(frozen_feature_columns) if frozen_feature_columns is not None else retained_feature_columns
    if not feature_columns:
        raise ValueError("No continuous emission feature survived the training-variation screen.")

    before_counts = frame["structural_regime"].value_counts().reindex(REGIME_ORDER, fill_value=0)
    finite_mask = np.isfinite(frame[feature_columns].to_numpy(dtype=np.float64)).all(axis=1)
    valid_mask = finite_mask & frame["structural_regime_code"].notna().to_numpy()
    dropped = frame.loc[~valid_mask]
    dropped_regime_counts = (
        dropped["structural_regime"].value_counts().reindex(REGIME_ORDER, fill_value=0).astype(int).to_dict()
    )
    frame = frame.loc[valid_mask].copy()
    after_counts = frame["structural_regime"].value_counts().reindex(REGIME_ORDER, fill_value=0)
    lost_classes = before_counts.index[(before_counts > 0) & after_counts.eq(0)].tolist()
    if lost_classes:
        raise AssertionError(f"Feature preparation removed every row for structural classes: {lost_classes}")
    drop_share = (before_counts - after_counts).div(before_counts.where(before_counts > 0))
    heavy_drops = drop_share.loc[drop_share.gt(MAX_SILENT_CLASS_DROP_SHARE)]
    if not heavy_drops.empty:
        warnings.warn(
            "Feature preparation dropped more than "
            f"{MAX_SILENT_CLASS_DROP_SHARE:.0%} of rows for structural classes: "
            + ", ".join(f"{name} {share:.1%}" for name, share in heavy_drops.items()),
            stacklevel=2,
        )

    train_mask = frame.index <= split.train_end
    validation_mask = (frame.index > split.train_end) & (frame.index <= split.validation_end)
    test_mask = frame.index > split.validation_end
    frames = {
        "train": frame.loc[train_mask].copy(),
        "validation": frame.loc[validation_mask].copy(),
        "test": frame.loc[test_mask].copy(),
    }
    if any(part.empty for part in frames.values()):
        raise ValueError("At least one chronological partition is empty.")
    scaler = StandardScaler().fit(frames["train"][feature_columns])
    arrays = {
        name: np.clip(scaler.transform(part[feature_columns]), -10.0, 10.0).astype(np.float64)
        for name, part in frames.items()
    }
    return PreparedData(
        clock=clock,
        tier=tier,
        feature_columns=feature_columns,
        frame=frame,
        split=split,
        scaler=scaler,
        frames=frames,
        arrays=arrays,
        removed_feature_columns=tuple(removed_feature_columns),
        dropped_rows=int((~valid_mask).sum()),
        dropped_regime_counts=dropped_regime_counts,
        removed_feature_reasons=removed_feature_reasons,
        training_point_mass_share=training_point_mass_share,
    )


def _soft_membership(distances: np.ndarray, scale: float) -> np.ndarray:
    """Convert distances to descriptive memberships using a training-frozen scale."""
    scale = max(float(scale), 1e-12)
    logits = -distances / scale
    logits -= logits.max(axis=1, keepdims=True)
    values = np.exp(logits)
    return values / values.sum(axis=1, keepdims=True)


def semantic_state_map(states: np.ndarray, baseline_codes: np.ndarray, n_states: int) -> dict[int, int | None]:
    """Map supported states one-to-one to supported training classes; leave surplus states unmatched."""
    contingency = np.zeros((n_states, len(REGIME_ORDER)), dtype=np.int64)
    for state, code in zip(states, baseline_codes, strict=True):
        contingency[int(state), int(code)] += 1
    supported_states = np.flatnonzero(contingency.sum(axis=1) > 0)
    supported_codes = np.flatnonzero(contingency.sum(axis=0) > 0)
    mapping: dict[int, int | None] = {state: None for state in range(n_states)}
    if supported_states.size and supported_codes.size:
        rows, columns = linear_sum_assignment(-contingency[np.ix_(supported_states, supported_codes)])
        for row, column in zip(rows, columns, strict=True):
            mapping[int(supported_states[int(row)])] = int(supported_codes[int(column)])
    return mapping


def semantic_state_name(regime_code: int | None) -> str:
    """Return a stable annotation without inventing a class for unsupported states."""
    if regime_code is None or int(regime_code) == UNMATCHED_REGIME_CODE:
        return "unmatched"
    return REGIME_ORDER[int(regime_code)]


def fit_candidate(
    prepared: PreparedData, family: ModelFamily, n_states: int = 4, random_state: int = 17,
    max_iter: int = 40, n_restarts: int = 2,
    min_emission_variance: float = DEFAULT_MIN_EMISSION_VARIANCE,
) -> CandidateFit:
    arrays = prepared.arrays
    lengths = {name: len(values) for name, values in arrays.items()}
    all_values = np.vstack([arrays["train"], arrays["validation"], arrays["test"]])
    slices = {
        "train": slice(0, lengths["train"]),
        "validation": slice(lengths["train"], lengths["train"] + lengths["validation"]),
        "test": slice(lengths["train"] + lengths["validation"], len(all_values)),
    }
    try:
        if family is ModelFamily.KMEANS:
            model = KMeans(n_clusters=n_states, n_init=20, random_state=random_state).fit(arrays["train"])
            states = {name: model.predict(values) for name, values in arrays.items()}
            training_distances = model.transform(arrays["train"])
            confidence_scale = max(float(np.nanmedian(training_distances)), 1e-12)
            probabilities = {
                name: _soft_membership(model.transform(values), confidence_scale)
                for name, values in arrays.items()
            }
            log_likelihoods = {name: np.nan for name in arrays}
        elif family is ModelFamily.GAUSSIAN_MIXTURE:
            confidence_scale = None
            model = GaussianMixture(
                n_components=n_states,
                covariance_type="diag",
                reg_covar=min_emission_variance,
                max_iter=max_iter,
                n_init=n_restarts,
                random_state=random_state,
            ).fit(arrays["train"])
            states = {name: model.predict(values) for name, values in arrays.items()}
            probabilities = {name: model.predict_proba(values) for name, values in arrays.items()}
            log_likelihoods = {name: float(model.score_samples(values).sum()) for name, values in arrays.items()}
        else:
            confidence_scale = None
            from dc_basics.hmm import DistType, InferenceMode, create_simple_hmm_instance

            distribution = DistType.NORMAL if family is ModelFamily.NORMAL_HMM else DistType.STUDENTT
            model = create_simple_hmm_instance(
                distribution,
                n_states=n_states,
                random_state=random_state,
                max_iter=max_iter,
                inference_mode=InferenceMode.FILTERING,
                covariance_type="diag",
                min_cov=min_emission_variance,
                n_restarts=n_restarts,
            )
            model.fit(arrays["train"])
            all_probabilities = model.predict_proba(all_values)
            probabilities = {name: all_probabilities[part] for name, part in slices.items()}
            states = {name: np.argmax(values, axis=1) for name, values in probabilities.items()}
            log_likelihoods = {name: model.log_likelihood(values) for name, values in arrays.items()}

        train_codes = prepared.frames["train"]["structural_regime_code"].to_numpy(dtype=np.int64)
        mapping = semantic_state_map(states["train"], train_codes, n_states)
        mapped = {
            name: np.array([
                UNMATCHED_REGIME_CODE if mapping[int(state)] is None else int(mapping[int(state)])
                for state in values
            ], dtype=np.int64)
            for name, values in states.items()
        }
        return CandidateFit(
            family=family,
            n_states=n_states,
            random_state=random_state,
            model=model,
            states=states,
            probabilities=probabilities,
            mapped_regimes=mapped,
            semantic_map=mapping,
            log_likelihoods=log_likelihoods,
            confidence_scale=confidence_scale,
            min_emission_variance=min_emission_variance,
        )
    except Exception as error:
        return CandidateFit(
            family=family,
            n_states=n_states,
            random_state=random_state,
            model=None,
            states={},
            probabilities={},
            mapped_regimes={},
            semantic_map={},
            log_likelihoods={},
            confidence_scale=None,
            min_emission_variance=min_emission_variance,
            error=f"{type(error).__name__}: {error}",
        )


def dwell_lengths(states: np.ndarray) -> np.ndarray:
    if len(states) == 0:
        return np.array([], dtype=np.int64)
    changes = np.flatnonzero(np.r_[True, states[1:] != states[:-1], True])
    return np.diff(changes).astype(np.int64)


def transition_matrix(states: np.ndarray, n_states: int) -> np.ndarray:
    counts = np.zeros((n_states, n_states), dtype=np.int64)
    if len(states) > 1:
        np.add.at(counts, (states[:-1], states[1:]), 1)
    totals = counts.sum(axis=1, keepdims=True)
    return np.divide(counts, totals, out=np.zeros_like(counts, dtype=float), where=totals > 0)


def emission_variance_diagnostics(fit: CandidateFit) -> tuple[float, int, float]:
    """Return minimum fitted variance, floor-hit count, and floor-hit share."""
    if fit.error is not None or fit.family is ModelFamily.KMEANS:
        return np.nan, 0, np.nan
    if fit.family is ModelFamily.GAUSSIAN_MIXTURE:
        variances = np.asarray(fit.model.covariances_, dtype=np.float64).ravel()
    else:
        variances = np.concatenate([
            np.asarray(parameters["covs"], dtype=np.float64).ravel()
            for parameters in fit.model.parameters
        ])
    if variances.size == 0:
        return np.nan, 0, np.nan
    tolerance = fit.min_emission_variance * (1.0 + 1e-6)
    floor_hits = int(np.count_nonzero(variances <= tolerance))
    return float(np.nanmin(variances)), floor_hits, floor_hits / len(variances)


def training_classes_without_state(fit: CandidateFit, prepared: PreparedData) -> tuple[str, ...]:
    """Name direct classes present in training that no fitted state was mapped to.

    This happens when K is smaller than the number of supported classes, or when one state
    absorbs two classes. Such a class is still in the data; it simply has no model state of its own.
    """
    if fit.error is not None:
        return ()
    training_codes = set(prepared.frames["train"]["structural_regime_code"].astype(int))
    mapped_codes = {int(code) for code in fit.semantic_map.values() if code is not None}
    return tuple(REGIME_ORDER[code] for code in sorted(training_codes - mapped_codes))


def _diagonal(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    return np.diag(values) if values.ndim == 2 else values.ravel()


def emission_feature_log_density(fit: CandidateFit, values: np.ndarray) -> np.ndarray:
    """Return per-feature emission log densities with shape ``(rows, states, features)``.

    All density candidates use diagonal covariances, so a state's emission log density is the
    sum of these per-feature terms. Summing over the last axis reproduces the model's own
    per-state emission log probability.
    """
    if fit.error is not None or fit.family is ModelFamily.KMEANS:
        raise ValueError("Per-feature log densities need a fitted density model.")
    x = np.asarray(values, dtype=np.float64)[:, None, :]
    if fit.family is ModelFamily.GAUSSIAN_MIXTURE:
        means = np.asarray(fit.model.means_, dtype=np.float64)
        variances = np.asarray(fit.model.covariances_, dtype=np.float64)
        return -0.5 * np.log(2.0 * np.pi * variances)[None] - 0.5 * (x - means[None]) ** 2 / variances[None]
    parameters = fit.model.parameters
    means = np.vstack([np.asarray(state["means"], dtype=np.float64).ravel() for state in parameters])
    variances = np.vstack([_diagonal(state["covs"]) for state in parameters])
    if fit.family is ModelFamily.NORMAL_HMM:
        return -0.5 * np.log(2.0 * np.pi * variances)[None] - 0.5 * (x - means[None]) ** 2 / variances[None]
    from scipy.special import gammaln

    dofs = np.vstack([
        np.broadcast_to(np.asarray(state["dofs"], dtype=np.float64).ravel(), (means.shape[1],))
        for state in parameters
    ])
    squared = (x - means[None]) ** 2 / variances[None]
    return (
        gammaln((dofs + 1.0) / 2.0)[None] - gammaln(dofs / 2.0)[None]
        - 0.5 * np.log(dofs * np.pi * variances)[None]
        - (dofs[None] + 1.0) / 2.0 * np.log1p(squared / dofs[None])
    )


def emission_feature_contributions(
    fit: CandidateFit, prepared: PreparedData, partition: str = "validation",
) -> pd.DataFrame:
    """Show which features supply a density model's likelihood on one partition.

    ``weighted_log_density`` is the mean over rows of the state-probability-weighted per-feature
    emission log density (filtered probabilities for HMMs, mixture memberships for the mixture).
    ``gain_vs_standard_normal`` subtracts the same feature's mean log density under one standard
    normal, the natural reference for train-standardised inputs. A feature with a large gain and
    states at the variance floor is buying likelihood by isolating values, not by describing a
    continuous distribution.
    """
    if fit.error is not None or fit.family is ModelFamily.KMEANS:
        return pd.DataFrame()
    values = prepared.arrays[partition]
    weights = np.asarray(fit.probabilities[partition], dtype=np.float64)
    per_feature = emission_feature_log_density(fit, values)
    weighted = np.einsum("tk,tkj->j", weights, per_feature) / len(values)
    reference = (-0.5 * np.log(2.0 * np.pi) - 0.5 * values**2).mean(axis=0)
    if fit.family is ModelFamily.GAUSSIAN_MIXTURE:
        variances = np.asarray(fit.model.covariances_, dtype=np.float64)
    else:
        variances = np.vstack([_diagonal(state["covs"]) for state in fit.model.parameters])
    floor_states = (variances <= fit.min_emission_variance * (1.0 + 1e-6)).sum(axis=0)
    table = pd.DataFrame({
        "weighted_log_density": weighted,
        "gain_vs_standard_normal": weighted - reference,
        "states_at_variance_floor": floor_states.astype(np.int64),
        "training_point_mass_share": [
            prepared.training_point_mass_share.get(column, np.nan) for column in prepared.feature_columns
        ],
    }, index=pd.Index(prepared.feature_columns, name="feature"))
    total_gain = table["gain_vs_standard_normal"].sum()
    table["share_of_total_gain"] = table["gain_vs_standard_normal"] / total_gain if total_gain else np.nan
    return table.sort_values("gain_vs_standard_normal", ascending=False)


def candidate_summary(fit: CandidateFit, prepared: PreparedData) -> dict[str, object]:
    record: dict[str, object] = {
        "family": fit.family.value,
        "n_states": fit.n_states,
        "clock": prepared.clock.value,
        "tier": prepared.tier.value,
        "feature_count": len(prepared.feature_columns),
        "removed_feature_count": len(prepared.removed_feature_columns),
        "prepared_rows_dropped": prepared.dropped_rows,
        "error": fit.error,
    }
    if fit.error is not None:
        return record
    validation_states = fit.states["validation"]
    validation_probabilities = fit.probabilities["validation"]
    validation_baseline = prepared.frames["validation"]["structural_regime_code"].to_numpy(dtype=np.int64)
    occupancy = np.bincount(validation_states, minlength=fit.n_states) / len(validation_states)
    dwell = dwell_lengths(validation_states)
    validation_ll = fit.log_likelihoods.get("validation", np.nan)
    validation_ll_per_row = validation_ll / len(validation_states) if np.isfinite(validation_ll) else np.nan
    mapped_validation = fit.mapped_regimes["validation"]
    mapped_mask = mapped_validation != UNMATCHED_REGIME_CODE
    mapping_coverage = float(mapped_mask.mean())
    mapped_agreement = (
        float(np.mean(validation_baseline[mapped_mask] == mapped_validation[mapped_mask]))
        if mapped_mask.any() else np.nan
    )
    minimum_variance, floor_hit_count, floor_hit_share = emission_variance_diagnostics(fit)
    record.update({
        "validation_log_likelihood_per_row": validation_ll_per_row,
        "minimum_state_occupancy": occupancy.min(),
        "switch_rate": np.mean(validation_states[1:] != validation_states[:-1]),
        "median_dwell": float(np.median(dwell)),
        "mean_max_probability": float(validation_probabilities.max(axis=1).mean()),
        "baseline_adjusted_rand": adjusted_rand_score(validation_baseline, validation_states),
        "baseline_nmi": normalized_mutual_info_score(validation_baseline, validation_states),
        "semantic_mapping_coverage": mapping_coverage,
        "baseline_mapped_agreement": mapped_agreement,
        "training_classes_without_state": training_classes_without_state(fit, prepared),
        "minimum_fitted_variance": minimum_variance,
        "variance_floor_hit_count": floor_hit_count,
        "variance_floor_hit_share": floor_hit_share,
    })
    return record


def filtering_prefix_invariant(
    fit: CandidateFit, prepared: PreparedData, prefix_rows: int | None = None,
) -> bool | None:
    if fit.error is not None or fit.family not in {ModelFamily.NORMAL_HMM, ModelFamily.STUDENTT_HMM}:
        return None
    values = np.vstack([prepared.arrays["train"], prepared.arrays["validation"], prepared.arrays["test"]])
    if prefix_rows is None:
        prefix_rows = len(prepared.arrays["train"]) + min(500, len(prepared.arrays["validation"]))
    prefix_rows = min(prefix_rows, len(values))
    full = fit.model.predict_proba(values)[:prefix_rows]
    prefix = fit.model.predict_proba(values[:prefix_rows])
    return bool(np.allclose(full, prefix, rtol=1e-10, atol=1e-12))


def select_hmm_candidates(
    prepared: PreparedData, families: tuple[ModelFamily, ...], state_counts: tuple[int, ...], *,
    random_state: int, stability_seeds: tuple[int, ...], max_iter: int, n_restarts: int,
    minimum_validation_occupancy: float, minimum_restart_ari: float,
    min_emission_variance: float = DEFAULT_MIN_EMISSION_VARIANCE,
) -> CandidateSelection:
    """Fit and select candidates using validation-only causality, occupancy, and restart stability gates."""
    fits = []
    selection_records = []
    stability_records = []
    for family in families:
        for n_states in state_counts:
            fit = fit_candidate(
                prepared, family, n_states, random_state, max_iter=max_iter, n_restarts=n_restarts,
                min_emission_variance=min_emission_variance,
            )
            fits.append(fit)
            record = candidate_summary(fit, prepared)
            prefix_pass = filtering_prefix_invariant(fit, prepared)
            record["filtering_prefix_invariant"] = prefix_pass
            validation_aris = []
            for seed in stability_seeds:
                refit = fit_candidate(
                    prepared, family, n_states, seed, max_iter=max_iter, n_restarts=n_restarts,
                    min_emission_variance=min_emission_variance,
                )
                ari = (
                    adjusted_rand_score(fit.states["validation"], refit.states["validation"])
                    if fit.error is None and refit.error is None else np.nan
                )
                validation_aris.append(ari)
                stability_records.append({
                    "family": family.value,
                    "n_states": n_states,
                    "seed": seed,
                    "error": refit.error,
                    "validation_ari_vs_primary": ari,
                    "validation_log_likelihood_per_row": (
                        refit.log_likelihoods["validation"] / len(prepared.frames["validation"])
                        if refit.error is None else np.nan
                    ),
                    "prefix_invariant": filtering_prefix_invariant(refit, prepared),
                })
            finite_aris = np.asarray(validation_aris, dtype=np.float64)
            stability_complete = len(finite_aris) == len(stability_seeds) and np.isfinite(finite_aris).all()
            minimum_ari = float(np.min(finite_aris)) if stability_complete and finite_aris.size else np.nan
            record["minimum_restart_validation_ari"] = minimum_ari
            record["restart_stability_complete"] = stability_complete
            record["eligible"] = (
                fit.error is None
                and prefix_pass is True
                and record.get("minimum_state_occupancy", 0.0) >= minimum_validation_occupancy
                and stability_complete
                and minimum_ari >= minimum_restart_ari
            )
            selection_records.append(record)

    table = pd.DataFrame.from_records(selection_records)
    stability = pd.DataFrame.from_records(stability_records)
    eligible = table.loc[table["eligible"]].copy()
    selected_fit = None
    if not eligible.empty:
        selected_row = eligible.sort_values("validation_log_likelihood_per_row", ascending=False).iloc[0]
        selected_fit = next(
            fit for fit in fits
            if fit.family.value == selected_row["family"] and fit.n_states == int(selected_row["n_states"])
        )
    return CandidateSelection(fits=fits, table=table, stability=stability, selected_fit=selected_fit)


def add_future_diagnostics(global_state: pd.DataFrame, horizons: tuple[int, ...] = (6, 24, 96)) -> pd.DataFrame:
    frame = global_state.copy()
    log_price = np.log(frame["price"])
    one_bar_return = log_price.diff()
    for horizon in horizons:
        frame[f"future_return_{horizon}"] = log_price.shift(-horizon) - log_price
        frame[f"future_abs_return_{horizon}"] = frame[f"future_return_{horizon}"].abs()
        future_variance = one_bar_return.pow(2).rolling(horizon).sum().shift(-horizon)
        frame[f"future_realized_vol_{horizon}"] = np.sqrt(future_variance)
        frame[f"future_dcc_count_{horizon}"] = (
            frame["dcc_count_this_bar"].rolling(horizon).sum().shift(-horizon)
        )
        frame[f"configuration_changes_{horizon}"] = frame["configuration_code"].shift(-horizon).ne(
            frame["configuration_code"]
        )
    return frame


def _omega_squared_codes(y: np.ndarray, codes: np.ndarray) -> float:
    """Omega-squared for finite values ``y`` and integer group codes ``codes``."""
    counts = np.bincount(codes)
    present = counts > 0
    group_count = int(present.sum())
    if len(y) <= group_count or group_count < 2 or np.var(y) == 0.0:
        return np.nan
    sums = np.bincount(codes, weights=y)
    group_means = np.divide(sums, counts, out=np.zeros_like(sums), where=present)
    grand = y.mean()
    between = float((counts[present] * (group_means[present] - grand) ** 2).sum())
    total = float(((y - grand) ** 2).sum())
    within = total - between
    mean_square_within = within / (len(y) - group_count)
    numerator = between - (group_count - 1) * mean_square_within
    denominator = total + mean_square_within
    return float(max(numerator / denominator, 0.0)) if denominator > 0.0 else np.nan


def omega_squared(values: pd.Series, labels: pd.Series) -> float:
    """Bias-corrected one-way effect size for a categorical grouping."""
    valid = values.notna() & labels.notna()
    y = values.loc[valid].to_numpy(dtype=np.float64)
    _, codes = np.unique(labels.loc[valid].to_numpy(), return_inverse=True)
    return _omega_squared_codes(y, codes.astype(np.int64))


def block_bootstrap_omega_difference(
    values: pd.Series, model_labels: pd.Series, baseline_labels: pd.Series, *,
    n_bootstrap: int = 499, block_length: int = 20, confidence: float = 0.90, random_state: int = 17,
) -> dict[str, float]:
    """Moving-block bootstrap interval for omega-squared(model) minus omega-squared(baseline).

    Rows are resampled in contiguous chronological blocks, with values and both labelings kept
    together, because forward-window diagnostics on neighbouring rows overlap and are serially
    dependent. The interval describes sampling uncertainty of the difference on this partition.
    """
    valid = values.notna() & model_labels.notna() & baseline_labels.notna()
    y = values.loc[valid].to_numpy(dtype=np.float64)
    _, model_codes = np.unique(model_labels.loc[valid].to_numpy(), return_inverse=True)
    _, baseline_codes = np.unique(baseline_labels.loc[valid].to_numpy(), return_inverse=True)
    model_codes = model_codes.astype(np.int64)
    baseline_codes = baseline_codes.astype(np.int64)
    observed = _omega_squared_codes(y, model_codes) - _omega_squared_codes(y, baseline_codes)
    result = {"difference": observed, "ci_low": np.nan, "ci_high": np.nan, "bootstrap_draws": 0}
    rows = len(y)
    if not np.isfinite(observed) or n_bootstrap < 1 or rows < 2 * block_length:
        return result
    rng = np.random.default_rng(random_state)
    block_count = int(np.ceil(rows / block_length))
    offsets = np.arange(block_length)
    draws = np.empty(n_bootstrap, dtype=np.float64)
    for draw in range(n_bootstrap):
        starts = rng.integers(0, rows - block_length + 1, size=block_count)
        index = (starts[:, None] + offsets[None, :]).ravel()[:rows]
        draws[draw] = (
            _omega_squared_codes(y[index], model_codes[index])
            - _omega_squared_codes(y[index], baseline_codes[index])
        )
    finite = draws[np.isfinite(draws)]
    if finite.size:
        tail = (1.0 - confidence) / 2.0
        result.update({
            "ci_low": float(np.quantile(finite, tail)),
            "ci_high": float(np.quantile(finite, 1.0 - tail)),
            "bootstrap_draws": int(finite.size),
        })
    return result


def incremental_usefulness(
    frame: pd.DataFrame, diagnostic_columns: list[str], model_column: str, baseline_columns: dict[str, str], *,
    n_bootstrap: int = 499, block_length: int = 20, confidence: float = 0.90, random_state: int = 17,
) -> pd.DataFrame:
    """Compare a model partition with the stronger of several direct baselines, per diagnostic.

    For each diagnostic the baseline with the larger observed omega-squared is the comparator.
    The verdict is computed, not written by hand:

    - ``adds_beyond_baselines``: the bootstrap interval of model minus best baseline is above 0;
    - ``baseline_separates_more``: the interval is below 0;
    - ``no_information_beyond_baseline``: the interval contains 0.
    """
    records = []
    for diagnostic_index, column in enumerate(diagnostic_columns):
        baseline_omegas = {
            name: omega_squared(frame[column], frame[label]) for name, label in baseline_columns.items()
        }
        best_baseline = max(
            baseline_omegas, key=lambda name: -np.inf if not np.isfinite(baseline_omegas[name])
            else baseline_omegas[name]
        )
        interval = block_bootstrap_omega_difference(
            frame[column], frame[model_column], frame[baseline_columns[best_baseline]],
            n_bootstrap=n_bootstrap, block_length=block_length, confidence=confidence,
            random_state=random_state + diagnostic_index,
        )
        if not np.isfinite(interval["ci_low"]):
            verdict = "insufficient_sample"
        elif interval["ci_low"] > 0.0:
            verdict = "adds_beyond_baselines"
        elif interval["ci_high"] < 0.0:
            verdict = "baseline_separates_more"
        else:
            verdict = "no_information_beyond_baseline"
        records.append({
            "diagnostic": column,
            "model_omega_squared": omega_squared(frame[column], frame[model_column]),
            **{f"{name}_omega_squared": value for name, value in baseline_omegas.items()},
            "best_baseline": best_baseline,
            "model_minus_best_baseline": interval["difference"],
            "ci_low": interval["ci_low"],
            "ci_high": interval["ci_high"],
            "verdict": verdict,
        })
    return pd.DataFrame.from_records(records).set_index("diagnostic")


def permutation_omega_test(
    values: pd.Series, labels: pd.Series, *, n_permutations: int = 500, random_state: int = 17,
) -> dict[str, float]:
    """Compare observed omega-squared with a label-permutation null."""
    valid = values.notna() & labels.notna()
    clean_values = values.loc[valid].reset_index(drop=True)
    clean_labels = labels.loc[valid].reset_index(drop=True)
    observed = omega_squared(clean_values, clean_labels)
    if not np.isfinite(observed) or n_permutations < 1:
        return {"omega_squared": observed, "null_p95": np.nan, "permutation_p_value": np.nan}
    rng = np.random.default_rng(random_state)
    null_values = np.empty(n_permutations, dtype=np.float64)
    label_values = clean_labels.to_numpy(copy=True)
    for index in range(n_permutations):
        permuted = pd.Series(rng.permutation(label_values))
        null_values[index] = omega_squared(clean_values, permuted)
    return {
        "omega_squared": observed,
        "null_p95": float(np.nanquantile(null_values, 0.95)),
        "permutation_p_value": float((1 + np.count_nonzero(null_values >= observed)) / (n_permutations + 1)),
    }


def state_profile(frame: pd.DataFrame, state_column: str, value_columns: list[str]) -> pd.DataFrame:
    return frame.groupby(state_column, observed=True)[value_columns].agg(["count", "median", "mean"])


def plot_price_states(
    frame: pd.DataFrame, state_column: str, title: str, probability_columns: list[str] | None = None,
    last_n: int = 8_000,
) -> go.Figure:
    view = frame.tail(last_n).copy()
    states = view[state_column].astype(str)
    labels = list(pd.unique(states))
    palette = ["#2563eb", "#f97316", "#16a34a", "#dc2626", "#7c3aed", "#0891b2"]
    color_map = {label: palette[index % len(palette)] for index, label in enumerate(labels)}
    rows = 2 if probability_columns else 1
    heights = [0.72, 0.28] if rows == 2 else [1.0]
    figure = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=heights, vertical_spacing=0.06)
    figure.add_trace(go.Scatter(
        x=view.index,
        y=view["price"],
        mode="lines",
        name="Close",
        line={"color": "#94a3b8", "width": 0.8},
    ), row=1, col=1)
    for label in labels:
        selected = states.eq(label)
        figure.add_trace(go.Scatter(
            x=view.index[selected],
            y=view.loc[selected, "price"],
            mode="markers",
            name=label,
            marker={"size": 3.0, "color": color_map[label]},
        ), row=1, col=1)
    if probability_columns:
        for index, column in enumerate(probability_columns):
            figure.add_trace(go.Scatter(
                x=view.index,
                y=view[column],
                mode="lines",
                name=column,
                line={"width": 1.0, "color": palette[index % len(palette)]},
            ), row=2, col=1)
        figure.update_yaxes(title="Filtered probability", range=[0.0, 1.0], row=2, col=1)
    figure.update_layout(title=title, template="plotly_white", height=700, hovermode="x unified")
    figure.update_yaxes(title="Close", row=1, col=1)
    return figure


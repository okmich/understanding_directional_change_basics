"""Shared causal multiscale-DC research utilities for roadmap phases 20-24.

This module is intentionally research-scoped. Phase 25 will decide the final
package boundaries after the exploratory representation and model contracts are
understood. No function in this module constructs a trading signal.
"""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass
class CandidateFit:
    family: ModelFamily
    n_states: int
    random_state: int
    model: Any
    states: dict[str, np.ndarray]
    probabilities: dict[str, np.ndarray]
    mapped_regimes: dict[str, np.ndarray]
    semantic_map: dict[int, int]
    log_likelihoods: dict[str, float]
    error: str | None = None


def _configuration_lookup(threshold_count: int) -> dict[int, str]:
    lookup = {}
    for code in range(2**threshold_count):
        modes = [DcMode.UP.value if code & (1 << index) else DcMode.DOWN.value for index in range(threshold_count)]
        lookup[code] = "/".join(modes)
    return lookup


def _causal_running_extreme(prices: pd.Series, live: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    mode = live["direction"]
    known = mode.notna()
    mode_start = known & mode.ne(mode.shift())
    run_id = mode_start.cumsum()
    positions = np.arange(len(prices), dtype=np.int64)
    start_position = pd.Series(np.where(mode_start, positions, np.nan), index=prices.index).ffill()
    age = pd.Series(positions - start_position, index=prices.index, dtype=np.float64).where(known)
    running_high = prices.groupby(run_id).cummax()
    running_low = prices.groupby(run_id).cummin()
    extreme = pd.Series(
        np.where(mode.eq(1.0), running_high, running_low),
        index=prices.index,
        dtype=np.float64,
    ).where(known)
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
    frame = global_state.copy()
    threshold_count = int(frame["threshold_count"].iloc[0])
    structural = []
    dynamic = []
    full = []
    for index in range(threshold_count):
        suffix = f"{index:02d}"
        age_column = f"log1p_mode_age_{suffix}"
        frame[age_column] = np.log1p(frame[f"mode_age_bars_{suffix}"])
        structural.extend([f"mode_sign_{suffix}", f"reversal_progress_{suffix}", age_column])
        live_tmv_column = f"log1p_live_tmv_{suffix}"
        live_r_column = f"log_live_r_{suffix}"
        frame[live_tmv_column] = np.log1p(frame[f"live_tmv_{suffix}"].clip(lower=0.0))
        frame[live_r_column] = np.log(frame[f"live_r_{suffix}"].clip(lower=1e-12))
        dynamic.extend([live_tmv_column, live_r_column, f"dcc_rate_{suffix}"])
        completed_tmv_column = f"log1p_completed_tmv_{suffix}"
        completed_t_column = f"log1p_completed_t_{suffix}"
        completed_r_column = f"log_completed_r_{suffix}"
        frame[completed_tmv_column] = np.log1p(frame[f"completed_tmv_{suffix}"].clip(lower=0.0))
        frame[completed_t_column] = np.log1p(frame[f"completed_t_{suffix}"].clip(lower=0.0))
        frame[completed_r_column] = np.log(frame[f"completed_r_{suffix}"].clip(lower=1e-12))
        full.extend([completed_tmv_column, completed_t_column, completed_r_column])

    structural.extend([
        "fragmentation",
        "counter_depth_fraction",
        "signed_mode_balance",
        "mean_reversal_progress",
        "max_reversal_progress",
    ])
    dynamic.append("hierarchy_dcc_rate")
    columns = structural
    if tier in {FeatureTier.DYNAMIC, FeatureTier.FULL}:
        columns = columns + dynamic
    if tier is FeatureTier.FULL:
        columns = columns + full
    return frame, columns


def prepare_data(
    global_state: pd.DataFrame, clock: ObservationClock, tier: FeatureTier, split: TimeSplit | None = None,
) -> PreparedData:
    frame, feature_columns = model_frame(global_state, tier)
    if clock is ObservationClock.UNION_EVENT:
        frame = frame.loc[frame["union_event"]].copy()
    frame = frame.dropna(subset=feature_columns + ["structural_regime_code"]).copy()
    if split is None:
        split = time_split(global_state.index)
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
    return PreparedData(clock, tier, feature_columns, frame, split, scaler, frames, arrays)


def _soft_membership(distances: np.ndarray) -> np.ndarray:
    scale = float(np.nanmedian(distances))
    scale = max(scale, 1e-12)
    logits = -distances / scale
    logits -= logits.max(axis=1, keepdims=True)
    values = np.exp(logits)
    return values / values.sum(axis=1, keepdims=True)


def semantic_state_map(states: np.ndarray, baseline_codes: np.ndarray, n_states: int) -> dict[int, int]:
    contingency = np.zeros((n_states, len(REGIME_ORDER)), dtype=np.int64)
    for state, code in zip(states, baseline_codes, strict=True):
        contingency[int(state), int(code)] += 1
    rows, columns = linear_sum_assignment(-contingency)
    mapping = {int(row): int(column) for row, column in zip(rows, columns, strict=True)}
    for state in range(n_states):
        if state not in mapping:
            mapping[state] = int(np.argmax(contingency[state]))
    return mapping


def fit_candidate(
    prepared: PreparedData, family: ModelFamily, n_states: int = 4, random_state: int = 17,
    max_iter: int = 40, n_restarts: int = 2,
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
            probabilities = {name: _soft_membership(model.transform(values)) for name, values in arrays.items()}
            log_likelihoods = {name: np.nan for name in arrays}
        elif family is ModelFamily.GAUSSIAN_MIXTURE:
            model = GaussianMixture(
                n_components=n_states,
                covariance_type="diag",
                reg_covar=1e-5,
                max_iter=max_iter,
                n_init=n_restarts,
                random_state=random_state,
            ).fit(arrays["train"])
            states = {name: model.predict(values) for name, values in arrays.items()}
            probabilities = {name: model.predict_proba(values) for name, values in arrays.items()}
            log_likelihoods = {name: float(model.score_samples(values).sum()) for name, values in arrays.items()}
        else:
            from dc_basics.hmm import DistType, InferenceMode, create_simple_hmm_instance

            distribution = DistType.NORMAL if family is ModelFamily.NORMAL_HMM else DistType.STUDENTT
            model = create_simple_hmm_instance(
                distribution,
                n_states=n_states,
                random_state=random_state,
                max_iter=max_iter,
                inference_mode=InferenceMode.FILTERING,
                covariance_type="diag",
                min_cov=1e-5,
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
            name: np.array([mapping[int(state)] for state in values], dtype=np.int64)
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


def candidate_summary(fit: CandidateFit, prepared: PreparedData) -> dict[str, object]:
    record: dict[str, object] = {
        "family": fit.family.value,
        "n_states": fit.n_states,
        "clock": prepared.clock.value,
        "tier": prepared.tier.value,
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
    record.update({
        "validation_log_likelihood_per_row": validation_ll_per_row,
        "minimum_state_occupancy": occupancy.min(),
        "switch_rate": np.mean(validation_states[1:] != validation_states[:-1]),
        "median_dwell": float(np.median(dwell)),
        "mean_max_probability": float(validation_probabilities.max(axis=1).mean()),
        "baseline_adjusted_rand": adjusted_rand_score(validation_baseline, fit.mapped_regimes["validation"]),
        "baseline_nmi": normalized_mutual_info_score(validation_baseline, fit.mapped_regimes["validation"]),
        "baseline_mapped_agreement": np.mean(validation_baseline == fit.mapped_regimes["validation"]),
    })
    return record


def filtering_prefix_invariant(fit: CandidateFit, prepared: PreparedData, prefix_rows: int = 500) -> bool | None:
    if fit.error is not None or fit.family not in {ModelFamily.NORMAL_HMM, ModelFamily.STUDENTT_HMM}:
        return None
    values = np.vstack([prepared.arrays["train"], prepared.arrays["validation"], prepared.arrays["test"]])
    prefix_rows = min(prefix_rows, len(values))
    full = fit.model.predict_proba(values)[:prefix_rows]
    prefix = fit.model.predict_proba(values[:prefix_rows])
    return bool(np.allclose(full, prefix, rtol=1e-10, atol=1e-12))


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


def eta_squared(values: pd.Series, labels: pd.Series) -> float:
    valid = values.notna() & labels.notna()
    y = values.loc[valid].to_numpy(dtype=np.float64)
    groups = labels.loc[valid].to_numpy()
    if len(y) == 0 or np.var(y) == 0.0:
        return np.nan
    grand = y.mean()
    between = 0.0
    for group in np.unique(groups):
        selected = y[groups == group]
        between += len(selected) * (selected.mean() - grand) ** 2
    total = ((y - grand) ** 2).sum()
    return float(between / total) if total > 0.0 else np.nan


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


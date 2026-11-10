"""Causal pre-resolution live panels for arbitrary threshold ladders.

A live panel has one row per bar of an active adjacent contest, from the stage
start through the bar *before* the stage resolution. Every feature on a row is
computed from information available on that bar; outcome columns are attached
only for diagnostic comparison and are flagged as hindsight.

Two counts are zero by construction inside such a panel:

- the active stage's *lower* clock cannot fire, because any lower-scale DCC
  flips the lower mode away from the target and is therefore the rejection (or
  ambiguous) resolution bar, which is excluded;
- the active stage's *upper* clock cannot fire, because an upper-scale DCC is
  the propagation resolution bar, which is also excluded.

The informative activity is on clocks *below* the active lower clock (for
example small DCCs during a medium-to-large stage). It is reported as
``sub_lower_dccs`` and ``sub_lower_dcc_rate``.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from .events import enum_value
from .live import calculate_target_progress

COMPLETED_LEG_COLUMNS = ("tmv", "t", "r")
AUC_INSUFFICIENT_SAMPLE = "insufficient_sample"
AUC_CONSTANT_BY_CONSTRUCTION = "constant_by_construction"
AUC_CONSTANT_IN_SAMPLE = "constant_in_sample"


@dataclass(frozen=True)
class LivePanelContext:
    """Causal inputs shared by every stage of a live panel.

    ``event_ledgers`` is optional. When it is supplied (one completed-event
    ledger per scale, as built by :func:`dc_basics.events.prepare_event_ledger`),
    every row also carries the completed seed-leg and stage-start-leg TMV/T/R,
    i.e. the *completed initiation features* known at the seed and hand-off
    information times.
    """

    prices: pd.Series
    mode_frame: pd.DataFrame
    live_frames: Mapping[Any, pd.DataFrame]
    running_extremes: Mapping[Any, pd.Series]
    thresholds: Mapping[Any, float]
    dcc_cumulative: Mapping[Any, np.ndarray]
    scale_order: Sequence[Any]
    hierarchy_columns: Sequence[str] = ()
    event_ledgers: Mapping[Any, pd.DataFrame] | None = None


def _value(row: object, name: str, default: object = pd.NA) -> object:
    if isinstance(row, pd.Series):
        return row.get(name, default)
    return getattr(row, name, default)


def _spec_scales(specification: object) -> tuple[Any, Any]:
    if isinstance(specification, Mapping):
        return specification["lower"], specification["upper"]
    lower, upper = specification
    return lower, upper


def _stage_scales(stage_value: str, stage_specs: Mapping[Any, object]) -> tuple[Any, Any]:
    for key, specification in stage_specs.items():
        if enum_value(key) == stage_value:
            return _spec_scales(specification)
    raise KeyError(f"No scale specification exists for stage {stage_value!r}.")


def _scale_index(scale_order: Sequence[Any], scale: Any) -> int:
    names = [enum_value(item) for item in scale_order]
    return names.index(enum_value(scale))


def build_completed_leg_lookups(event_ledgers: Mapping[Any, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Index each completed-event ledger by event ID for exact-key joins."""
    lookups: dict[str, pd.DataFrame] = {}
    for scale, ledger in event_ledgers.items():
        required = {"event_id", "information_time", *COMPLETED_LEG_COLUMNS}
        missing = required.difference(ledger.columns)
        if missing:
            raise KeyError(f"{enum_value(scale)} ledger is missing {sorted(missing)}.")
        lookup = ledger.set_index("event_id")[["information_time", *COMPLETED_LEG_COLUMNS]]
        if lookup.index.has_duplicates:
            raise AssertionError(f"{enum_value(scale)} ledger has duplicate event IDs.")
        lookups[enum_value(scale)] = lookup
    return lookups


def _completed_leg(lookups: Mapping[str, pd.DataFrame], scale: Any, event_id: object,
                   expected_information_time: object, role: str) -> pd.Series:
    scale_name = enum_value(scale)
    if scale_name not in lookups:
        raise KeyError(f"No completed-event ledger was supplied for scale {scale_name!r}.")
    if pd.isna(event_id) or event_id not in lookups[scale_name].index:
        raise KeyError(f"{role} event {event_id!r} is not in the {scale_name} ledger.")
    leg = lookups[scale_name].loc[event_id]
    # Exact-key integrity: the completed leg must become known on the very DCC
    # that starts the lineage or stage. Joining a neighbouring event fails here.
    if leg["information_time"] != expected_information_time:
        raise AssertionError(
            f"{role} event {event_id!r} became known at {leg['information_time']}, "
            f"not at the {role} time {expected_information_time}."
        )
    return leg


def build_live_stage_part(stage_row: object, lineage: object, context: LivePanelContext,
                          lower_scale: Any, upper_scale: Any,
                          completed_legs: Mapping[str, pd.DataFrame] | None = None) -> pd.DataFrame:
    """Build causal rows strictly before one stage's resolution bar."""
    start_position = int(_value(stage_row, "start_position"))
    resolution_position = int(_value(stage_row, "resolution_position"))
    positions = np.arange(start_position, resolution_position, dtype=np.int64)
    if positions.size == 0:
        raise AssertionError("A strict-clean stage contains no pre-resolution bars.")
    stage_start_time = _value(stage_row, "start_time")
    if context.prices.index[start_position] != stage_start_time:
        raise AssertionError("A stage start_time does not match its start_position bar.")

    lower_name = enum_value(lower_scale)
    upper_name = enum_value(upper_scale)
    target_mode = str(_value(stage_row, "target_mode"))
    path_prices = context.prices.iloc[positions].to_numpy(dtype=np.float64)
    start_price = float(context.prices.iloc[start_position])
    direction_sign = 1.0 if target_mode == "up" else -1.0
    signed_excursion = (path_prices / start_price - 1.0) * direction_sign
    lower_theta = float(context.thresholds[lower_scale])
    upper_extremes = context.running_extremes[upper_scale].iloc[positions].to_numpy(dtype=np.float64)
    target_progress = calculate_target_progress(
        path_prices, upper_extremes, target_mode, float(context.thresholds[upper_scale])
    )

    lower_modes = context.mode_frame[f"{lower_name}_mode"].iloc[positions]
    upper_modes = context.mode_frame[f"{upper_name}_mode"].iloc[positions]
    if not lower_modes.eq(target_mode).all():
        raise AssertionError(f"{lower_name} mode changed before stage resolution.")
    origin_mode = _value(lineage, "origin_mode", pd.NA)
    upper_valid = upper_modes.eq(origin_mode) if pd.notna(origin_mode) else upper_modes.ne(target_mode)
    if not upper_valid.all():
        raise AssertionError(f"{upper_name} mode changed before stage resolution.")
    if np.nanmax(target_progress) >= 1.0 + 1e-10:
        raise AssertionError("Upper-threshold progress crossed one before stage resolution.")

    lower_live = context.live_frames[lower_scale].iloc[positions]
    upper_live = context.live_frames[upper_scale].iloc[positions]
    elapsed = positions - start_position

    lineage_id = _value(stage_row, "lineage_id", _value(lineage, "seed_small_event_id"))
    seed_event_id = _value(lineage, "seed_small_event_id", lineage_id)
    seed_time = _value(lineage, "seed_time")
    seed_position = _value(lineage, "seed_position", pd.NA)
    if pd.isna(seed_position):
        seed_position = context.prices.index.get_loc(seed_time)
    seed_position = int(seed_position)
    if seed_position > start_position:
        raise AssertionError("A stage starts before its lineage seed.")

    nested_counts = {
        scale: values[positions] - values[start_position]
        for scale, values in context.dcc_cumulative.items()
    }
    # The active lower and upper clocks cannot fire inside the panel (see the
    # module docstring). Verify that rather than report a constant feature.
    for scale in (lower_scale, upper_scale):
        if scale in nested_counts and np.any(nested_counts[scale] != 0):
            raise AssertionError(
                f"{enum_value(scale)} DCC inside a pre-resolution {lower_name}->{upper_name} panel."
            )
    lower_index = _scale_index(context.scale_order, lower_scale)
    sub_lower_scales = list(context.scale_order)[:lower_index]
    missing_scales = [enum_value(scale) for scale in sub_lower_scales if scale not in nested_counts]
    if missing_scales:
        raise KeyError(f"dcc_cumulative is missing sub-lower scales {missing_scales}.")
    sub_lower_dccs = np.zeros(positions.size, dtype=np.int64)
    for scale in sub_lower_scales:
        sub_lower_dccs = sub_lower_dccs + nested_counts[scale]

    terminal_time = _value(lineage, "terminal_time")
    part_data: dict[str, object] = {
        "lineage_id": lineage_id,
        "seed_small_event_id": seed_event_id,
        "seed_time": seed_time,
        "stage": str(_value(stage_row, "stage")),
        "stage_order": int(_value(stage_row, "stage_order")),
        "stage_start_event_id": _value(stage_row, "initiating_event_id"),
        "stage_start_time": stage_start_time,
        "time": context.prices.index[positions],
        "bar_position": positions,
        "elapsed_bars": elapsed,
        "lineage_age_bars": positions - seed_position,
        "price": path_prices,
        "origin_mode": origin_mode,
        "target_mode": target_mode,
        "attained_depth": int(_value(stage_row, "attained_depth_before")),
        "lower_tmv_live": lower_live["tmv_current"].to_numpy(),
        "lower_t_live": lower_live["t_current"].to_numpy(),
        "lower_r_live": lower_live["rdc_current"].to_numpy(),
        "upper_tmv_live": upper_live["tmv_current"].to_numpy(),
        "upper_t_live": upper_live["t_current"].to_numpy(),
        "upper_r_live": upper_live["rdc_current"].to_numpy(),
        "post_start_excursion_theta": signed_excursion / lower_theta,
        "max_favorable_excursion_theta": np.maximum.accumulate(signed_excursion / lower_theta),
        "max_adverse_excursion_theta": np.maximum.accumulate(
            np.maximum(-signed_excursion / lower_theta, 0.0)
        ),
        "target_progress": target_progress,
        "max_target_progress": np.maximum.accumulate(target_progress),
        "future_stage_outcome": _value(stage_row, "outcome"),
        "stage_outcome_information_time": _value(stage_row, "resolution_time"),
        "future_terminal_depth": int(_value(lineage, "terminal_depth")),
        "future_terminal_outcome": _value(lineage, "terminal_outcome"),
        "terminal_outcome_information_time": terminal_time,
    }
    information_time_columns = ["time", "seed_time", "stage_start_time"]

    if completed_legs is None and context.event_ledgers is not None:
        completed_legs = build_completed_leg_lookups(context.event_ledgers)
    if completed_legs is not None:
        seed_leg = _completed_leg(completed_legs, context.scale_order[0], seed_event_id, seed_time, "seed")
        stage_leg = _completed_leg(
            completed_legs, lower_scale, _value(stage_row, "initiating_event_id"), stage_start_time,
            "stage-start",
        )
        for prefix, leg in (("seed_leg", seed_leg), ("stage_start_leg", stage_leg)):
            for column in COMPLETED_LEG_COLUMNS:
                part_data[f"{prefix}_{column}"] = float(leg[column])
            part_data[f"{prefix}_information_time"] = leg["information_time"]
            information_time_columns.append(f"{prefix}_information_time")

    hierarchy = context.mode_frame.iloc[positions]
    for column in context.hierarchy_columns:
        part_data[column] = hierarchy[column].to_numpy()
    for scale, counts in nested_counts.items():
        part_data[f"nested_{enum_value(scale)}_dccs"] = counts
    part_data["sub_lower_scale_count"] = len(sub_lower_scales)
    part_data["sub_lower_dccs"] = sub_lower_dccs

    part = pd.DataFrame(part_data)
    part["sub_lower_dcc_rate"] = np.divide(part["sub_lower_dccs"], np.maximum(part["elapsed_bars"], 1))
    part["progress_drawdown"] = part["max_target_progress"] - part["target_progress"]
    # The latest information time among every input the row's features use.
    # It equals ``time`` only if no joined input became known after the bar.
    part["feature_information_time"] = part[information_time_columns].max(axis=1)
    part["stage_outcome_is_hindsight"] = part["time"].lt(_value(stage_row, "resolution_time"))
    part["terminal_outcome_is_hindsight"] = part["time"].lt(terminal_time)
    return part


def build_live_panel(stages: pd.DataFrame, lineages: pd.DataFrame, context: LivePanelContext,
                     stage_specs: Mapping[Any, object]) -> pd.DataFrame:
    """Build a complete causal live panel from canonical stage rows."""
    lineage_id_column = "lineage_id" if "lineage_id" in lineages else "seed_small_event_id"
    lineage_lookup = lineages.set_index(lineage_id_column, drop=False)
    completed_legs = (
        build_completed_leg_lookups(context.event_ledgers) if context.event_ledgers is not None else None
    )
    parts = []
    for stage_row in stages.itertuples(index=False):
        lineage = lineage_lookup.loc[stage_row.lineage_id]
        if isinstance(lineage, pd.DataFrame):
            raise AssertionError("A lineage ID maps to multiple terminal records.")
        lower_scale, upper_scale = _stage_scales(str(stage_row.stage), stage_specs)
        parts.append(build_live_stage_part(
            stage_row, lineage, context, lower_scale, upper_scale, completed_legs=completed_legs
        ))
    if not parts:
        raise ValueError("No live stages were supplied.")
    return pd.concat(parts, ignore_index=True)


def constant_by_construction_features(stage_specs: Mapping[Any, object],
                                      scale_order: Sequence[Any]) -> dict[str, frozenset[str]]:
    """List, per stage, live features that cannot vary inside a pre-resolution panel."""
    first_scale = enum_value(scale_order[0])
    constant: dict[str, frozenset[str]] = {}
    for stage, specification in stage_specs.items():
        lower, upper = (enum_value(scale) for scale in _spec_scales(specification))
        names = {f"nested_{lower}_dccs", f"nested_{upper}_dccs"}
        if lower == first_scale:
            names.update({"sub_lower_dccs", "sub_lower_dcc_rate"})
        constant[enum_value(stage)] = frozenset(names)
    return constant


def _finite_float(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce").astype(np.float64)
    return numeric.where(np.isfinite(numeric))


def _auc_record(target: pd.Series, values: pd.Series, min_class_count: int) -> dict[str, object]:
    values = _finite_float(values)
    valid = values.notna()
    feature_values = values.loc[valid]
    feature_target = target.loc[valid]
    propagated = int(feature_target.sum())
    rejected = int(len(feature_target) - propagated)
    record: dict[str, object] = {
        "valid_rows": int(valid.sum()),
        "raw_auc_for_higher_value": np.nan,
        "orientation_free_auc": np.nan,
    }
    if min(propagated, rejected) < min_class_count:
        record["stronger_value_direction"] = AUC_INSUFFICIENT_SAMPLE
    elif feature_values.nunique() < 2:
        record["stronger_value_direction"] = AUC_CONSTANT_IN_SAMPLE
    else:
        raw_auc = float(roc_auc_score(feature_target, feature_values))
        record["raw_auc_for_higher_value"] = raw_auc
        record["orientation_free_auc"] = max(raw_auc, 1.0 - raw_auc)
        record["stronger_value_direction"] = "higher" if raw_auc >= 0.5 else "lower"
    return record


def summarize_checkpoint_overlap(rows: pd.DataFrame, features: Sequence[str], *,
                                 group_columns: Sequence[str] = ("stage", "elapsed_bars"),
                                 outcome_column: str = "future_stage_outcome",
                                 positive_outcome: str = "propagated",
                                 min_class_count: int = 20,
                                 constant_by_construction: Mapping[str, frozenset[str]] | None = None,
                                 ) -> pd.DataFrame:
    """Orientation-free AUC of each causal feature against the later outcome.

    The AUC is an in-sample, outcome-conditioned *diagnostic*. A value is
    reported only when both classes have at least ``min_class_count`` rows.
    ``stronger_value_direction`` is ``higher``/``lower`` when an AUC exists, and
    otherwise names why it does not: ``insufficient_sample``,
    ``constant_by_construction`` or ``constant_in_sample``.
    """
    constant_by_construction = constant_by_construction or {}
    records = []
    for group_key, group in rows.groupby(list(group_columns), sort=True):
        key = group_key if isinstance(group_key, tuple) else (group_key,)
        key_values = dict(zip(group_columns, key, strict=True))
        target = group[outcome_column].eq(positive_outcome).astype(np.int8)
        propagated = int(target.sum())
        constant_names = constant_by_construction.get(str(key_values.get("stage", "")), frozenset())
        for feature in features:
            if feature in constant_names:
                record = {
                    "valid_rows": len(group),
                    "raw_auc_for_higher_value": np.nan,
                    "orientation_free_auc": np.nan,
                    "stronger_value_direction": AUC_CONSTANT_BY_CONSTRUCTION,
                }
            else:
                record = _auc_record(target, group[feature], min_class_count)
            records.append({
                **key_values,
                "surviving_attempts": len(group),
                "propagated_survivors": propagated,
                "rejected_survivors": len(group) - propagated,
                "feature": feature,
                **record,
            })
    return pd.DataFrame.from_records(records)


def auc_table_with_counts(summary: pd.DataFrame, *, index: str | Sequence[str] = "elapsed_bars",
                          features: Sequence[str] | None = None) -> pd.DataFrame:
    """Pivot orientation-free AUC with the class counts that support it.

    Cells without an AUC show the reason (for example ``insufficient_sample``)
    instead of a blank, so a missing value is never mistaken for 0.5.
    """
    index_columns = [index] if isinstance(index, str) else list(index)
    selected = summary if features is None else summary.loc[summary["feature"].isin(features)]
    cell = selected["orientation_free_auc"].map(lambda value: f"{value:.3f}" if pd.notna(value) else "")
    cell = cell.where(selected["orientation_free_auc"].notna(), selected["stronger_value_direction"])
    table = selected.assign(cell=cell).pivot_table(
        index=index_columns, columns="feature", values="cell", aggfunc="first"
    )
    if features is not None:
        table = table[[feature for feature in features if feature in table.columns]]
    counts = selected.groupby(index_columns, sort=True)[["propagated_survivors", "rejected_survivors"]].first()
    return counts.join(table)


def compare_initiation_and_live_features(rows: pd.DataFrame, initiation_features: Sequence[str],
                                         live_features: Sequence[str], *,
                                         order_column: str = "stage_start_time",
                                         outcome_column: str = "future_stage_outcome",
                                         positive_outcome: str = "propagated",
                                         n_splits: int = 5,
                                         min_class_count: int = 20) -> dict[str, object]:
    """Ask whether live geometry adds information beyond completed initiation features.

    ``rows`` must be one row per attempt, all observed at the same checkpoint,
    so both feature sets describe the *same* survivor cohort. Two logistic
    models are fitted with forward-chaining folds ordered by ``order_column``
    (each fold is scored by a model trained only on earlier attempts):

    - initiation only (completed seed / hand-off leg TMV, T, R);
    - initiation plus live features.

    The pooled out-of-fold AUC of each model, and their difference, are
    returned together with the best univariate in-sample AUC of each feature
    set. This is a diagnostic of incremental information, not a forecast.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import QuantileTransformer

    all_features = list(dict.fromkeys([*initiation_features, *live_features]))
    clean = rows.copy()
    for feature in all_features:
        clean[feature] = _finite_float(clean[feature])
    clean = clean.dropna(subset=all_features)
    sort_columns = [order_column, "lineage_id"] if "lineage_id" in clean else [order_column]
    clean = clean.sort_values(sort_columns, kind="mergesort")
    target = clean[outcome_column].eq(positive_outcome).astype(np.int8).to_numpy()
    propagated = int(target.sum())
    rejected = int(len(target) - propagated)
    result: dict[str, object] = {
        "attempts": len(rows),
        "complete_rows": len(clean),
        "propagated": propagated,
        "rejected": rejected,
        "best_initiation_feature": pd.NA,
        "best_initiation_auc": np.nan,
        "best_live_feature": pd.NA,
        "best_live_auc": np.nan,
        "oos_rows": 0,
        "oos_auc_initiation": np.nan,
        "oos_auc_initiation_plus_live": np.nan,
        "oos_auc_gain": np.nan,
        "status": AUC_INSUFFICIENT_SAMPLE,
    }
    if min(propagated, rejected) < min_class_count:
        return result

    target_series = pd.Series(target, index=clean.index)
    for label, feature_set in (("initiation", initiation_features), ("live", live_features)):
        best = None
        for feature in feature_set:
            record = _auc_record(target_series, clean[feature], min_class_count)
            if pd.notna(record["orientation_free_auc"]) and (
                best is None or record["orientation_free_auc"] > best[1]
            ):
                best = (feature, record["orientation_free_auc"])
        if best is not None:
            result[f"best_{label}_feature"], result[f"best_{label}_auc"] = best

    predictions = {"initiation": [], "initiation_plus_live": []}
    scored_targets = []
    for train_index, test_index in TimeSeriesSplit(n_splits=n_splits).split(clean):
        if len(np.unique(target[train_index])) < 2:
            continue
        scored_targets.append(target[test_index])
        for label, feature_set in (("initiation", list(initiation_features)),
                                   ("initiation_plus_live", all_features)):
            model = make_pipeline(
                QuantileTransformer(output_distribution="normal",
                                    n_quantiles=min(100, len(train_index))),
                LogisticRegression(max_iter=1000),
            )
            model.fit(clean.iloc[train_index][feature_set], target[train_index])
            predictions[label].append(model.predict_proba(clean.iloc[test_index][feature_set])[:, 1])
    if not scored_targets:
        result["status"] = "no_scorable_fold"
        return result
    scored = np.concatenate(scored_targets)
    result["oos_rows"] = int(scored.size)
    if len(np.unique(scored)) < 2:
        result["status"] = "single_class_out_of_fold"
        return result
    base_auc = float(roc_auc_score(scored, np.concatenate(predictions["initiation"])))
    full_auc = float(roc_auc_score(scored, np.concatenate(predictions["initiation_plus_live"])))
    result.update({
        "oos_auc_initiation": base_auc,
        "oos_auc_initiation_plus_live": full_auc,
        "oos_auc_gain": full_auc - base_auc,
        "status": "ok",
    })
    return result

"""Causal pre-resolution live panels for arbitrary threshold ladders."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .events import enum_value
from .live import calculate_target_progress


@dataclass(frozen=True)
class LivePanelContext:
    prices: pd.Series
    mode_frame: pd.DataFrame
    live_frames: Mapping[Any, pd.DataFrame]
    running_extremes: Mapping[Any, pd.Series]
    thresholds: Mapping[Any, float]
    dcc_cumulative: Mapping[Any, np.ndarray]
    scale_order: Sequence[Any]
    hierarchy_columns: Sequence[str] = ()


def _value(row: object, name: str, default: object = pd.NA) -> object:
    if isinstance(row, pd.Series):
        return row.get(name, default)
    return getattr(row, name, default)


def _stage_scales(stage_value: str, stage_specs: Mapping[Any, object]) -> tuple[Any, Any]:
    for key, specification in stage_specs.items():
        if enum_value(key) != stage_value:
            continue
        if isinstance(specification, Mapping):
            return specification["lower"], specification["upper"]
        lower, upper = specification
        return lower, upper
    raise KeyError(f"No scale specification exists for stage {stage_value!r}.")


def build_live_stage_part(stage_row: object, lineage: object, context: LivePanelContext,
                          lower_scale: Any, upper_scale: Any) -> pd.DataFrame:
    """Build causal rows strictly before one stage's resolution bar."""
    start_position = int(_value(stage_row, "start_position"))
    resolution_position = int(_value(stage_row, "resolution_position"))
    positions = np.arange(start_position, resolution_position, dtype=np.int64)
    if positions.size == 0:
        raise AssertionError("A strict-clean stage contains no pre-resolution bars.")

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
    nested_counts = {
        scale: values[positions] - values[start_position]
        for scale, values in context.dcc_cumulative.items()
    }
    lineage_id = _value(stage_row, "lineage_id", _value(lineage, "seed_small_event_id"))
    terminal_time = _value(lineage, "terminal_time")
    part_data: dict[str, object] = {
        "lineage_id": lineage_id,
        "seed_small_event_id": _value(lineage, "seed_small_event_id", lineage_id),
        "seed_time": _value(lineage, "seed_time"),
        "stage": str(_value(stage_row, "stage")),
        "stage_order": int(_value(stage_row, "stage_order")),
        "stage_start_event_id": _value(stage_row, "initiating_event_id"),
        "stage_start_time": _value(stage_row, "start_time"),
        "time": context.prices.index[positions],
        "bar_position": positions,
        "elapsed_bars": elapsed,
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
    hierarchy = context.mode_frame.iloc[positions]
    for column in context.hierarchy_columns:
        part_data[column] = hierarchy[column].to_numpy()
    for scale, counts in nested_counts.items():
        part_data[f"nested_{enum_value(scale)}_dccs"] = counts
    part_data["nested_lower_dccs"] = nested_counts[lower_scale]

    part = pd.DataFrame(part_data)
    part["nested_lower_dcc_rate"] = np.divide(
        part["nested_lower_dccs"], np.maximum(part["elapsed_bars"], 1)
    )
    part["progress_drawdown"] = part["max_target_progress"] - part["target_progress"]
    part["feature_information_time"] = part["time"]
    part["stage_outcome_is_hindsight"] = part["time"].lt(_value(stage_row, "resolution_time"))
    part["terminal_outcome_is_hindsight"] = part["time"].lt(terminal_time)
    return part


def build_live_panel(stages: pd.DataFrame, lineages: pd.DataFrame, context: LivePanelContext,
                     stage_specs: Mapping[Any, object]) -> pd.DataFrame:
    """Build a complete causal live panel from canonical stage rows."""
    lineage_id_column = "lineage_id" if "lineage_id" in lineages else "seed_small_event_id"
    lineage_lookup = lineages.set_index(lineage_id_column, drop=False)
    parts = []
    for stage_row in stages.itertuples(index=False):
        lineage = lineage_lookup.loc[stage_row.lineage_id]
        if isinstance(lineage, pd.DataFrame):
            raise AssertionError("A lineage ID maps to multiple terminal records.")
        lower_scale, upper_scale = _stage_scales(str(stage_row.stage), stage_specs)
        parts.append(build_live_stage_part(stage_row, lineage, context, lower_scale, upper_scale))
    if not parts:
        raise ValueError("No live stages were supplied.")
    return pd.concat(parts, ignore_index=True)

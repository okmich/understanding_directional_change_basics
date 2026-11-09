"""Shared adjacent-scale contest and nesting mechanics."""

from enum import Enum

import numpy as np
import pandas as pd

from .events import enum_value
from .enums import AttemptOutcome


def build_adjacent_attempts(frame: pd.DataFrame, lower_scale: str | Enum, upper_scale: str | Enum) -> pd.DataFrame:
    """Resolve counter-scale attempts between one adjacent threshold pair.

    A lower-scale DCC seeds an attempt only when it moves against the upper
    scale's mode known immediately before that bar. The outcome is hindsight;
    ``resolution_time`` is the first bar on which it becomes knowable.
    """
    lower_name = enum_value(lower_scale)
    upper_name = enum_value(upper_scale)
    records: list[dict[str, object]] = []
    active: dict[str, object] | None = None
    rows = frame.reset_index(names="time")
    lower_mode_column = f"{lower_name}_mode"
    upper_mode_column = f"{upper_name}_mode"
    lower_event_column = f"{lower_name}_event_id"
    upper_event_column = f"{upper_name}_event_id"
    lower_dcc_columns = [f"{lower_name}_upward_dcc", f"{lower_name}_downward_dcc"]
    upper_dcc_columns = [f"{upper_name}_upward_dcc", f"{upper_name}_downward_dcc"]
    edge = f"{lower_name}->{upper_name}"

    for bar_position, row in enumerate(rows.itertuples(index=False)):
        lower_dcc = bool(any(getattr(row, column) for column in lower_dcc_columns))
        upper_dcc = bool(any(getattr(row, column) for column in upper_dcc_columns))
        current_lower_mode = getattr(row, lower_mode_column)
        current_upper_mode = getattr(row, upper_mode_column)
        lower_event_id = getattr(row, lower_event_column)
        upper_event_id = getattr(row, upper_event_column)

        if lower_dcc and pd.isna(lower_event_id):
            raise AssertionError(f"A {lower_name} DCC has no event identifier.")
        if upper_dcc and pd.isna(upper_event_id):
            raise AssertionError(f"An {upper_name} DCC has no event identifier.")

        if active is not None:
            upper_propagated = upper_dcc and current_upper_mode == active["target_mode"]
            lower_rejected = lower_dcc and current_lower_mode != active["target_mode"]
            if upper_propagated or lower_rejected:
                if upper_propagated and lower_rejected:
                    outcome = AttemptOutcome.AMBIGUOUS
                    resolution_event_id = f"{lower_event_id}|{upper_event_id}"
                elif upper_propagated:
                    outcome = AttemptOutcome.PROPAGATED
                    resolution_event_id = upper_event_id
                else:
                    outcome = AttemptOutcome.REJECTED
                    resolution_event_id = lower_event_id
                active.update({
                    "outcome": outcome.value,
                    "resolution_event_id": resolution_event_id,
                    "resolution_time": row.time,
                    "resolution_position": bar_position,
                    "resolution_bars": bar_position - int(active["start_position"]),
                })
                records.append(active)
                active = None
                continue

        if active is not None or not lower_dcc or bar_position == 0:
            continue
        prior_upper_mode = rows.iloc[bar_position - 1][upper_mode_column]
        if pd.isna(prior_upper_mode) or pd.isna(current_lower_mode) or current_lower_mode == prior_upper_mode:
            continue

        active = {
            "edge": edge,
            "lower_scale": lower_name,
            "upper_scale": upper_name,
            "initiating_event_id": lower_event_id,
            "start_time": row.time,
            "start_position": bar_position,
            "target_mode": current_lower_mode,
            "prior_upper_mode": prior_upper_mode,
        }
        if upper_dcc and current_upper_mode == current_lower_mode:
            active.update({
                "outcome": AttemptOutcome.PROPAGATED.value,
                "resolution_event_id": upper_event_id,
                "resolution_time": row.time,
                "resolution_position": bar_position,
                "resolution_bars": 0,
            })
            records.append(active)
            active = None

    if active is not None:
        active.update({
            "outcome": AttemptOutcome.UNRESOLVED.value,
            "resolution_event_id": pd.NA,
            "resolution_time": pd.NaT,
            "resolution_position": pd.NA,
            "resolution_bars": pd.NA,
        })
        records.append(active)
    return pd.DataFrame.from_records(records)


def build_nesting_intervals(lower_events: pd.DataFrame, upper_events: pd.DataFrame,
                            lower_scale: str | Enum, upper_scale: str | Enum) -> pd.DataFrame:
    """Count lower-scale DCCs inside each completed upper-scale interval."""
    lower_name = enum_value(lower_scale)
    upper_name = enum_value(upper_scale)
    lower_positions = lower_events["dcc_pos"].to_numpy(dtype=np.int64)
    intervals = upper_events[["event_id", "direction", "dcc_idx", "dcc_pos"]].copy()
    intervals = intervals.rename(columns={
        "event_id": "upper_event_id",
        "direction": "upper_completed_direction",
        "dcc_idx": "information_time",
    })
    intervals["interval_start_position"] = intervals["dcc_pos"].shift(1)
    intervals["interval_start_time"] = intervals["information_time"].shift(1)
    intervals = intervals.dropna(subset=["interval_start_position"]).copy()
    intervals["interval_start_position"] = intervals["interval_start_position"].astype(np.int64)
    left_edges = np.searchsorted(lower_positions, intervals["interval_start_position"], side="right")
    right_edges = np.searchsorted(lower_positions, intervals["dcc_pos"], side="right")
    intervals["lower_dcc_count"] = right_edges - left_edges
    if not intervals["lower_dcc_count"].ge(1).all():
        raise AssertionError(f"An {upper_name} interval contains no {lower_name} DCC.")
    if not intervals["lower_dcc_count"].mod(2).eq(1).all():
        raise AssertionError(f"{lower_name.title()} DCC counts must be odd.")
    intervals["prior_rejections"] = (intervals["lower_dcc_count"] - 1) // 2
    intervals["interval_bars"] = intervals["dcc_pos"] - intervals["interval_start_position"]
    intervals["edge"] = f"{lower_name}->{upper_name}"
    return intervals

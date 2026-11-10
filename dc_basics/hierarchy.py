"""Shared adjacent-scale contest and nesting mechanics.

Two near-invariants hold on almost every real path but are *not* guaranteed by
multiplicative thresholds:

1. the lower clock confirms a reversal before (or on the same bar as) the upper
   clock, so every upper reversal is preceded by a lower counter-attempt;
2. consequently the number of lower DCCs between consecutive upper DCCs is
   positive and odd.

Because the thresholds are relative to *different* running extremes, the upper
clock can occasionally confirm first (the relative failure window is roughly
``theta_lower ** 2``). These functions therefore report violations explicitly
instead of crashing or silently dropping them:

- :func:`find_upper_led_reversals` lists upper DCCs that flipped the upper mode
  while the lower mode still pointed the other way;
- :func:`build_nesting_intervals` flags intervals whose lower count is not
  positive and odd (``parity_violation``);
- :func:`summarize_nesting_parity` gives the per-edge audit.
"""

import warnings
from enum import Enum

import numpy as np
import pandas as pd

from .events import enum_value
from .enums import AttemptOutcome


def _scan_adjacent_contest(frame: pd.DataFrame, lower_scale: str | Enum,
                           upper_scale: str | Enum) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Walk one adjacent pair bar by bar; return (attempts, upper-led reversals)."""
    lower_name = enum_value(lower_scale)
    upper_name = enum_value(upper_scale)
    records: list[dict[str, object]] = []
    upper_led_records: list[dict[str, object]] = []
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

        if (
            active is None
            and upper_dcc
            and pd.notna(current_upper_mode)
            and pd.notna(current_lower_mode)
            and current_upper_mode != current_lower_mode
            and bar_position > 0
        ):
            # The upper clock confirmed a reversal while the lower clock still
            # pointed the other way: no lower counter-attempt preceded it.
            upper_led_records.append({
                "edge": edge,
                "lower_scale": lower_name,
                "upper_scale": upper_name,
                "upper_event_id": upper_event_id,
                "time": row.time,
                "position": bar_position,
                "new_upper_mode": current_upper_mode,
                "lower_mode": current_lower_mode,
                "lower_dcc_same_bar": lower_dcc,
            })

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
    upper_led = pd.DataFrame.from_records(upper_led_records, columns=[
        "edge", "lower_scale", "upper_scale", "upper_event_id", "time", "position",
        "new_upper_mode", "lower_mode", "lower_dcc_same_bar",
    ])
    return pd.DataFrame.from_records(records), upper_led


def build_adjacent_attempts(frame: pd.DataFrame, lower_scale: str | Enum, upper_scale: str | Enum) -> pd.DataFrame:
    """Resolve counter-scale attempts between one adjacent threshold pair.

    A lower-scale DCC seeds an attempt only when it moves against the upper
    scale's mode known immediately before that bar. The outcome is hindsight;
    ``resolution_time`` is the first bar on which it becomes knowable.

    A seed DCC and the upper DCC on the same bar give a zero-bar
    ``propagated`` attempt (same-bar propagation). ``ambiguous_same_bar`` is a
    different case: opposing lower and upper DCCs resolving an *active*
    attempt on one bar.

    Rarely the upper clock reverses first, while the lower mode still points
    the other way. Such reversals belong to no attempt; they are reported by
    :func:`find_upper_led_reversals`, and this function warns when any exist.
    """
    attempts, upper_led = _scan_adjacent_contest(frame, lower_scale, upper_scale)
    if not upper_led.empty:
        warnings.warn(
            f"{len(upper_led)} {enum_value(upper_scale)} reversal(s) were confirmed before any "
            f"{enum_value(lower_scale)} counter-attempt; see find_upper_led_reversals().",
            stacklevel=2,
        )
    return attempts


def find_upper_led_reversals(frame: pd.DataFrame, lower_scale: str | Enum,
                             upper_scale: str | Enum) -> pd.DataFrame:
    """List upper DCCs that reversed the upper mode before the lower clock did.

    These are the exceptions to "the smaller clock confirms first". Each row is
    an upper DCC after which the upper mode differs from the lower mode while
    no counter-attempt was active. The lower clock usually catches up on a
    later bar without seeding a new attempt.
    """
    return _scan_adjacent_contest(frame, lower_scale, upper_scale)[1]


def build_nesting_intervals(lower_events: pd.DataFrame, upper_events: pd.DataFrame,
                            lower_scale: str | Enum, upper_scale: str | Enum) -> pd.DataFrame:
    """Count lower-scale DCCs inside each completed upper-scale interval.

    An interval runs from one upper DCC (exclusive) to the next (inclusive).
    The count is normally positive and odd, and ``(count - 1) / 2`` lower
    counter-attempts were rejected inside it. Intervals that break that
    near-invariant are kept and flagged with ``parity_violation``; their
    ``prior_rejections`` is missing because the pairing argument fails.
    """
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
    intervals["parity_violation"] = intervals["lower_dcc_count"].lt(1) | intervals["lower_dcc_count"].mod(2).eq(0)
    intervals["prior_rejections"] = (
        ((intervals["lower_dcc_count"] - 1) // 2).astype("Int64").mask(intervals["parity_violation"])
    )
    intervals["interval_bars"] = intervals["dcc_pos"] - intervals["interval_start_position"]
    intervals["edge"] = f"{lower_name}->{upper_name}"
    violations = int(intervals["parity_violation"].sum())
    if violations:
        warnings.warn(
            f"{violations} {upper_name} interval(s) contain a non-odd number of {lower_name} DCCs "
            "(the upper clock confirmed first); they are flagged with parity_violation.",
            stacklevel=2,
        )
    return intervals


def summarize_nesting_parity(intervals: pd.DataFrame) -> pd.DataFrame:
    """Per-edge audit of the positive-and-odd nesting near-invariant."""
    summary = intervals.groupby("edge", sort=False).agg(
        upper_intervals=("upper_event_id", "size"),
        parity_violations=("parity_violation", "sum"),
        empty_intervals=("lower_dcc_count", lambda counts: int(counts.lt(1).sum())),
    )
    summary["violation_share"] = summary["parity_violations"] / summary["upper_intervals"]
    return summary

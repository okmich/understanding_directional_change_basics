"""Two-threshold disagreement episodes and causal trajectory panels."""

import numpy as np
import pandas as pd

from .enums import AttemptOutcome, DcMode


def build_disagreement_episodes(frame: pd.DataFrame, close: pd.Series) -> pd.DataFrame:
    """Pin each small DCC against the prior large mode until causal resolution."""
    required = {
        "small_mode", "large_mode", "small_event_id", "small_upward_dcc",
        "small_downward_dcc", "large_upward_dcc", "large_downward_dcc",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise KeyError(f"frame is missing required columns: {sorted(missing)}")
    if not frame.index.equals(close.index):
        raise ValueError("frame and close must have identical indices.")

    records: list[dict[str, object]] = []
    active: dict[str, object] | None = None
    rows = frame.reset_index(names="time")
    for bar_position, row in enumerate(rows.itertuples(index=False)):
        small_dcc = bool(row.small_upward_dcc or row.small_downward_dcc)
        large_dcc = bool(row.large_upward_dcc or row.large_downward_dcc)
        if active is not None:
            large_propagated = large_dcc and row.large_mode == active["target_small_mode"]
            small_rejected = small_dcc and row.small_mode != active["target_small_mode"]
            if large_propagated or small_rejected:
                if large_propagated and small_rejected:
                    outcome = AttemptOutcome.AMBIGUOUS
                elif large_propagated:
                    outcome = AttemptOutcome.PROPAGATED
                else:
                    outcome = AttemptOutcome.REJECTED
                active.update({
                    "outcome": outcome.value,
                    "resolution_time": row.time,
                    "information_time": row.time,
                    "resolution_position": bar_position,
                    "resolution_bars": bar_position - int(active["start_position"]),
                    "resolution_price": float(close.iloc[bar_position]),
                })
                records.append(active)
                active = None
                continue

        if active is not None or not small_dcc or bar_position == 0:
            continue
        prior_large_mode = rows.iloc[bar_position - 1]["large_mode"]
        if pd.isna(prior_large_mode) or pd.isna(row.small_mode) or row.small_mode == prior_large_mode:
            continue
        active = {
            "small_event_id": row.small_event_id,
            "start_time": row.time,
            "start_position": bar_position,
            "start_price": float(close.iloc[bar_position]),
            "target_small_mode": row.small_mode,
            "new_small_mode": row.small_mode,
            "prior_large_mode": prior_large_mode,
        }
        if large_dcc and row.large_mode == row.small_mode:
            active.update({
                "outcome": AttemptOutcome.PROPAGATED.value,
                "resolution_time": row.time,
                "information_time": row.time,
                "resolution_position": bar_position,
                "resolution_bars": 0,
                "resolution_price": float(close.iloc[bar_position]),
            })
            records.append(active)
            active = None

    if active is not None:
        active.update({
            "outcome": AttemptOutcome.UNRESOLVED.value,
            "resolution_time": pd.NaT,
            "information_time": pd.NaT,
            "resolution_position": pd.NA,
            "resolution_bars": pd.NA,
            "resolution_price": np.nan,
        })
        records.append(active)
    episodes = pd.DataFrame.from_records(records)
    if episodes.empty:
        raise ValueError("No counter-large small-DCC episodes were found.")
    return episodes


def build_counter_scale_trajectory_panel(episodes: pd.DataFrame, close: pd.Series,
                                         small_context: pd.DataFrame, *, mode_frame: pd.DataFrame,
                                         large_running_extreme: pd.Series, small_theta: float,
                                         large_theta: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build causal rows strictly before each two-scale attempt resolves."""
    resolved = episodes.loc[episodes["outcome"].isin([
        AttemptOutcome.PROPAGATED.value,
        AttemptOutcome.REJECTED.value,
    ])].copy()
    eligible = resolved.loc[resolved["resolution_bars"].gt(0)].copy()
    eligible["attempt_id"] = eligible["small_event_id"]
    eligible["future_outcome"] = eligible["outcome"]
    trajectory_parts = []

    for attempt in eligible.itertuples(index=False):
        start_position = int(attempt.start_position)
        resolution_position = int(attempt.resolution_position)
        positions = np.arange(start_position, resolution_position, dtype=np.int64)
        attempt_prices = close.iloc[positions].to_numpy(dtype=np.float64)
        target_mode = attempt.target_small_mode
        direction_sign = 1.0 if target_mode == DcMode.UP.value else -1.0
        post_dcc_excursion = (
            (attempt_prices / float(attempt.start_price) - 1.0) * direction_sign / small_theta
        )
        running_extreme = large_running_extreme.iloc[positions].to_numpy(dtype=np.float64)
        if attempt.prior_large_mode == DcMode.UP.value:
            large_progress = (running_extreme - attempt_prices) / running_extreme / large_theta
        else:
            large_progress = (attempt_prices - running_extreme) / running_extreme / large_theta
        if not mode_frame["small_mode"].iloc[positions].eq(target_mode).all():
            raise AssertionError(f"Small mode changed before attempt {attempt.small_event_id} resolved.")
        if not mode_frame["large_mode"].iloc[positions].eq(attempt.prior_large_mode).all():
            raise AssertionError(f"Large mode changed before attempt {attempt.small_event_id} resolved.")
        if np.nanmax(large_progress) >= 1.0 + 1e-10:
            raise AssertionError(f"Large-DCC progress crossed one before attempt {attempt.small_event_id} resolved.")

        part = pd.DataFrame({
            "attempt_id": attempt.small_event_id,
            "time": close.index[positions],
            "bar_position": positions,
            "elapsed_bars": positions - start_position,
            "price": attempt_prices,
            "target_small_mode": target_mode,
            "new_small_mode": target_mode,
            "prior_large_mode": attempt.prior_large_mode,
            "small_tmv_live": small_context["tmv_current"].iloc[positions].to_numpy(),
            "small_t_live": small_context["t_current"].iloc[positions].to_numpy(),
            "small_rdc_live": small_context["rdc_current"].iloc[positions].to_numpy(),
            "post_dcc_excursion_theta": post_dcc_excursion,
            "max_post_dcc_excursion_theta": np.maximum.accumulate(post_dcc_excursion),
            "large_running_extreme": running_extreme,
            "large_dcc_progress": large_progress,
            "future_outcome": attempt.outcome,
            "outcome_information_time": attempt.resolution_time,
        })
        part["feature_information_time"] = part["time"]
        part["outcome_is_hindsight"] = part["time"].lt(attempt.resolution_time)
        trajectory_parts.append(part)

    if not trajectory_parts:
        raise ValueError("No non-immediate resolved counter-scale trajectories were found.")
    trajectories = pd.concat(trajectory_parts, ignore_index=True)
    if not trajectories["outcome_is_hindsight"].all():
        raise AssertionError("A trajectory row contains an outcome already known at that bar.")
    live_features = ["small_tmv_live", "small_t_live", "small_rdc_live", "large_dcc_progress"]
    if trajectories[live_features].isna().any().any():
        raise AssertionError("A live feature is missing inside an active attempt.")
    return trajectories, eligible

import warnings
from enum import StrEnum

import numpy as np
import pandas as pd
import pytest

from dc_basics import dc_live_features, parse_dc_events, prepare_event_ledger
from dc_basics.hierarchy import (
    build_adjacent_attempts,
    build_nesting_intervals,
    find_upper_led_reversals,
    summarize_nesting_parity,
)
from dc_basics.live import build_causal_running_extreme, calculate_target_progress


class Scale(StrEnum):
    SMALL = "small"
    MEDIUM = "medium"


def contest_frame() -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=7, freq="5min")
    return pd.DataFrame({
        "small_mode": ["up", "down", "down", "down", "down", "up", "down"],
        "medium_mode": ["up", "up", "up", "down", "down", "down", "down"],
        "small_upward_dcc": [False, False, False, False, False, True, False],
        "small_downward_dcc": [False, True, False, False, False, False, True],
        "medium_upward_dcc": [False] * 7,
        "medium_downward_dcc": [False, False, False, True, False, False, False],
        "small_event_id": [pd.NA, "S1", pd.NA, pd.NA, pd.NA, "S2", "S3"],
        "medium_event_id": [pd.NA, pd.NA, pd.NA, "M1", pd.NA, pd.NA, pd.NA],
    }, index=index)


def test_adjacent_attempts_record_propagation_and_rejection_resolution() -> None:
    attempts = build_adjacent_attempts(contest_frame(), Scale.SMALL, Scale.MEDIUM)

    assert attempts["outcome"].tolist() == ["propagated", "rejected"]
    assert attempts["resolution_bars"].tolist() == [2, 1]
    assert attempts["resolution_event_id"].tolist() == ["M1", "S3"]
    assert attempts["resolution_time"].ge(attempts["start_time"]).all()


def test_same_bar_opposing_resolutions_remain_ambiguous() -> None:
    frame = contest_frame().iloc[:3].copy()
    frame.iloc[2, frame.columns.get_loc("small_mode")] = "up"
    frame.iloc[2, frame.columns.get_loc("medium_mode")] = "down"
    frame.iloc[2, frame.columns.get_loc("small_upward_dcc")] = True
    frame.iloc[2, frame.columns.get_loc("medium_downward_dcc")] = True
    frame.iloc[2, frame.columns.get_loc("small_event_id")] = "S2"
    frame.iloc[2, frame.columns.get_loc("medium_event_id")] = "M1"

    attempts = build_adjacent_attempts(frame, Scale.SMALL, Scale.MEDIUM)
    assert attempts.loc[0, "outcome"] == "ambiguous_same_bar"
    assert attempts.loc[0, "resolution_event_id"] == "S2|M1"


def test_nesting_counts_are_odd_and_encode_prior_rejections() -> None:
    times = pd.date_range("2024-01-01", periods=9, freq="5min")
    lower_positions = [1, 2, 4, 5, 6, 8]
    lower = pd.DataFrame({"dcc_pos": lower_positions})
    upper = pd.DataFrame({
        "event_id": ["M1", "M2", "M3"],
        "direction": ["up", "down", "up"],
        "dcc_idx": times[[0, 4, 8]],
        "dcc_pos": [0, 4, 8],
    })

    intervals = build_nesting_intervals(lower, upper, Scale.SMALL, Scale.MEDIUM)
    assert intervals["lower_dcc_count"].tolist() == [3, 3]
    assert intervals["prior_rejections"].tolist() == [1, 1]
    assert not intervals["parity_violation"].any()


def upper_first_counterexample() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Ten bars on which the 0.4% clock reverses down while the 0.2% clock is still up.

    Multiplicative thresholds measure from different running extremes, so the
    larger clock can confirm first inside a window of roughly theta_small**2.
    """
    closes = [101, 100.5, 99.0, 100.0, 99.8, 99.6002, 99.7995, 99.59999, 99.5, 99.0]
    prices = pd.Series(closes, index=pd.date_range("2024-01-01", periods=len(closes), freq="5min"), dtype=float)
    frame = pd.DataFrame(index=prices.index)
    ledgers = {}
    for scale, prefix, theta in (("small", "S", 0.002), ("large", "L", 0.004)):
        ledgers[scale] = prepare_event_ledger(parse_dc_events(prices=prices, theta=theta), prefix, scale, theta)
        live = dc_live_features(prices, theta=theta)
        frame[f"{scale}_mode"] = live["direction"].map({1.0: "up", -1.0: "down"})
        frame[f"{scale}_upward_dcc"] = live["upward_dcc"].astype(bool)
        frame[f"{scale}_downward_dcc"] = live["downward_dcc"].astype(bool)
        frame[f"{scale}_event_id"] = frame.index.to_series().map(ledgers[scale].set_index("dcc_idx")["event_id"])
    return frame, ledgers


def test_upper_clock_can_confirm_first_and_is_reported_not_crashed() -> None:
    frame, ledgers = upper_first_counterexample()
    assert frame.loc[frame.index[7], ["small_mode", "large_mode"]].tolist() == ["up", "down"]

    upper_led = find_upper_led_reversals(frame, "small", "large")
    assert upper_led["upper_event_id"].tolist() == ["L2"]
    assert upper_led["position"].tolist() == [7]
    with pytest.warns(UserWarning, match="before any small counter-attempt"):
        attempts = build_adjacent_attempts(frame, "small", "large")
    assert "L2" not in set(attempts["resolution_event_id"].dropna())

    with pytest.warns(UserWarning, match="non-odd number"):
        intervals = build_nesting_intervals(ledgers["small"], ledgers["large"], "small", "large")
    violating = intervals.loc[intervals["parity_violation"]]
    assert violating["upper_event_id"].tolist() == ["L2"]
    assert violating["lower_dcc_count"].tolist() == [2]
    assert violating["prior_rejections"].isna().all()
    audit = summarize_nesting_parity(intervals)
    assert int(audit.loc["small->large", "parity_violations"]) == 1


def test_ordinary_paths_emit_no_parity_warning() -> None:
    times = pd.date_range("2024-01-01", periods=9, freq="5min")
    lower = pd.DataFrame({"dcc_pos": [1, 2, 4, 5, 6, 8]})
    upper = pd.DataFrame({
        "event_id": ["M1", "M2", "M3"], "direction": ["up", "down", "up"],
        "dcc_idx": times[[0, 4, 8]], "dcc_pos": [0, 4, 8],
    })
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        build_nesting_intervals(lower, upper, Scale.SMALL, Scale.MEDIUM)
        build_adjacent_attempts(contest_frame(), Scale.SMALL, Scale.MEDIUM)


def test_live_extreme_and_target_progress_are_causal() -> None:
    close = pd.Series([100.0, 102.0, 101.0, 99.0, 98.0])
    live = pd.DataFrame({"direction": [np.nan, 1.0, 1.0, -1.0, -1.0]})
    extreme = build_causal_running_extreme(close, live)

    assert np.isnan(extreme.iloc[0])
    assert extreme.iloc[1:].tolist() == [102.0, 102.0, 99.0, 98.0]
    progress = calculate_target_progress(np.array([100.0, 101.0]), np.array([99.0, 99.0]), "up", 0.02)
    np.testing.assert_allclose(progress, [0.5050505050505051, 1.0101010101010102])

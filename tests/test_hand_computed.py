"""Hand-computed answers for the core semantics (final-review follow-up).

The other suites mostly compare the library with itself (three lineage views built by one
tracer, a prefix build against a full build). Here every expected value is written out by
hand from a small path whose answer can be read off the page, so a plausible one-line defect
-- a seed rule that peeks at the same or next bar, a terminal depth off by one, a hindsight
outcome stamped at the seed, a wrong DCC direction, a mislabelled resample -- fails a test.
"""

import numpy as np
import pandas as pd
import pytest

from dc_basics import parse_dc_events, prepare_event_ledger
from dc_basics.data import load_close
from dc_basics.hierarchy import build_adjacent_attempts
from dc_basics.lineage import build_lineage_tables, build_three_scale_linkages

SCALES = ("small", "medium", "large")
BARS = 21
# (bar, scale, new mode). Every scale starts "up".
DCCS = [
    (2, "small", "down"),    # A: seed; rejected when small turns back up at bar 4
    (4, "small", "up"),
    (6, "small", "down"),    # B: seed; medium confirms at bar 8, large at bar 10 -> reaches large
    (8, "medium", "down"),
    (10, "large", "down"),
    (12, "small", "up"),     # C: seed and medium on the same bar -> zero-bar propagation,
    (12, "medium", "up"),    #    then medium turns back at bar 14 -> stopped below large
    (14, "medium", "down"),
    (16, "small", "down"),   # small rejoins the hierarchy: no attempt (it moves with medium)
    (18, "small", "up"),     # D: seed; nothing resolves before the sample ends -> unresolved
]


def hand_frame() -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=BARS, freq="5min")
    frame = pd.DataFrame(index=index)
    counters = {scale: 0 for scale in SCALES}
    for scale in SCALES:
        modes, mode = [], "up"
        events = {bar: new_mode for bar, dcc_scale, new_mode in DCCS if dcc_scale == scale}
        frame[f"{scale}_upward_dcc"] = False
        frame[f"{scale}_downward_dcc"] = False
        frame[f"{scale}_event_id"] = pd.Series(pd.NA, index=index, dtype=object)
        for bar in range(BARS):
            if bar in events:
                mode = events[bar]
                counters[scale] += 1
                frame.iloc[bar, frame.columns.get_loc(f"{scale}_{mode}ward_dcc")] = True
                frame.iloc[bar, frame.columns.get_loc(f"{scale}_event_id")] = f"{scale[0].upper()}{counters[scale]}"
            modes.append(mode)
        frame[f"{scale}_mode"] = modes
    return frame


@pytest.fixture(scope="module")
def hand_lineages() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = hand_frame()
    small_medium = build_adjacent_attempts(frame, "small", "medium")
    medium_large = build_adjacent_attempts(frame, "medium", "large")
    lineages, stages = build_lineage_tables(small_medium, [medium_large], SCALES)
    return small_medium, lineages.set_index("lineage_id"), stages


def test_adjacent_attempts_match_the_hand_answer(hand_lineages) -> None:
    small_medium, _, _ = hand_lineages
    index = hand_frame().index
    expected = pd.DataFrame({
        "initiating_event_id": ["S1", "S3", "S4", "S6"],
        "start_position": [2, 6, 12, 18],
        "target_mode": ["down", "down", "up", "up"],
        "prior_upper_mode": ["up", "up", "down", "down"],
        "outcome": ["rejected", "propagated", "propagated", "unresolved_at_sample_end"],
        "resolution_event_id": ["S2", "M1", "M2", pd.NA],
        "resolution_time": [index[4], index[8], index[12], pd.NaT],
    })
    actual = small_medium[list(expected.columns)].reset_index(drop=True)
    for column in expected:
        assert actual[column].astype(object).where(actual[column].notna(), None).tolist() == \
            expected[column].astype(object).where(expected[column].notna(), None).tolist(), column


def test_seed_rule_reads_the_upper_mode_on_the_previous_bar(hand_lineages) -> None:
    """C's seed (bar 12) meets a medium DCC on the same bar: still a seed, resolved in zero bars."""
    small_medium, _, _ = hand_lineages
    c = small_medium.loc[small_medium["initiating_event_id"].eq("S4")].iloc[0]
    assert c["prior_upper_mode"] == "down" and c["outcome"] == "propagated"
    assert int(c["resolution_bars"]) == 0


def test_lineages_match_the_hand_answer(hand_lineages) -> None:
    _, lineages, _ = hand_lineages
    index = hand_frame().index
    expected = {
        #       depth, max_attained, terminal_event, terminal_time, same_bar_stages, resolved, strict_clean
        "S1": (0, 0, "S2", index[4], 0, True, True),
        "S3": (2, 2, "L1", index[10], 0, True, True),
        "S4": (1, 1, "M3", index[14], 1, True, False),
        "S6": (None, 0, None, None, 0, False, False),
    }
    assert sorted(lineages.index) == sorted(expected)
    for lineage_id, (depth, attained, event, time, same_bar, resolved, strict) in expected.items():
        row = lineages.loc[lineage_id]
        assert (None if pd.isna(row["terminal_depth"]) else int(row["terminal_depth"])) == depth, lineage_id
        assert int(row["max_attained_depth"]) == attained, lineage_id
        assert int(row["same_bar_stage_count"]) == same_bar, lineage_id
        assert bool(row["resolved_lineage"]) is resolved, lineage_id
        assert bool(row["strict_clean"]) is strict, lineage_id
        if resolved:
            assert row["terminal_event_id"] == event, lineage_id
            assert row["terminal_time"] == time, lineage_id
            assert row["outcome_information_time"] == time, lineage_id
        else:
            assert pd.isna(row["outcome_information_time"]), lineage_id
        # The outcome is never knowable at the seed bar.
        assert bool(row["terminal_label_hindsight_at_seed"]), lineage_id


def test_three_scale_view_agrees_with_the_hand_answer() -> None:
    frame = hand_frame()
    wide = build_three_scale_linkages(
        build_adjacent_attempts(frame, "small", "medium"), build_adjacent_attempts(frame, "medium", "large")
    ).set_index("seed_small_event_id")
    assert wide.loc["S3", "terminal_outcome"] == "reached_large"
    assert wide.loc["S1", "terminal_outcome"] == "stopped_below_medium"
    assert wide.loc["S4", "terminal_outcome"] == "stopped_below_large"
    assert bool(wide.loc["S4", "small_medium_same_bar"]) and not bool(wide.loc["S3", "small_medium_same_bar"])


def test_stage_frames_in_the_wrong_order_are_refused() -> None:
    frame = hand_frame()
    small_medium = build_adjacent_attempts(frame, "small", "medium")
    medium_large = build_adjacent_attempts(frame, "medium", "large")
    with pytest.raises(ValueError, match="ladder expects"):
        build_lineage_tables(medium_large, [small_medium], SCALES)


def test_ledger_direction_columns_match_the_hand_answer() -> None:
    values = np.array([100, 101, 103, 102, 100, 98, 99, 101, 104, 102, 99, 97, 100], dtype=float)
    prices = pd.Series(values, index=pd.date_range("2024-01-01", periods=len(values), freq="5min"))
    ledger = prepare_event_ledger(parse_dc_events(prices, 0.02), "S", "small", 0.02)
    # Completed legs: up (to 103), down (to 98), up (to 104), down (to 97).
    assert ledger["completed_leg_direction"].tolist() == ["up", "down", "up", "down"]
    # The DCC that completes an up leg is a downward confirmation and switches the live mode down.
    assert ledger["dcc_direction"].tolist() == ["down", "up", "down", "up"]
    assert ledger["new_live_mode"].tolist() == ["down", "up", "down", "up"]


@pytest.mark.parametrize(("convention", "expected"), [
    # Native bars stamped 10:00..10:35 with closes 1..8.
    ("open", {"10:00": 3.0, "10:15": 6.0}),                   # [10:00,10:15) -> close of 10:10; partial 10:30 bin dropped
    ("close", {"10:00": 1.0, "10:15": 4.0, "10:30": 7.0}),    # (09:45,10:00] -> 10:00; partial (10:30,10:45] dropped
])
def test_resampling_conventions_match_the_hand_answer(tmp_path, convention: str, expected: dict) -> None:
    index = pd.date_range("2024-01-01 10:00", "2024-01-01 10:35", freq="5min")
    pd.DataFrame({"close": np.arange(1.0, 9.0)}, index=index).to_parquet(tmp_path / "X.parquet")
    sampled = load_close(tmp_path, "X", 15, convention)
    assert dict(zip(sampled.index.strftime("%H:%M"), sampled.to_numpy())) == expected


def test_unlinked_lineage_has_no_terminal_depth() -> None:
    """Large flips before medium (an upper-led reversal), so medium's hand-off seeds no next contest.

    bar 2: small down (seed S1)   bar 3: large down (upper-led)   bar 4: medium down (hand-off M1)
    M1 moves with large's prior mode, so no medium->large attempt exists: the lineage is unlinked
    after medium -- attained depth 1, but no terminal depth.
    """
    global DCCS, BARS
    saved = DCCS, BARS
    DCCS, BARS = [(2, "small", "down"), (3, "large", "down"), (4, "medium", "down")], 8
    try:
        frame = hand_frame()
    finally:
        DCCS, BARS = saved
    small_medium = build_adjacent_attempts(frame, "small", "medium")
    with pytest.warns(UserWarning, match="reversal"):
        medium_large = build_adjacent_attempts(frame, "medium", "large")
    assert medium_large.empty or not medium_large["initiating_event_id"].eq("M1").any()

    lineages, _ = build_lineage_tables(small_medium, [medium_large], SCALES)
    row = lineages.set_index("lineage_id").loc["S1"]
    assert row["terminal_kind"] == "unlinked"
    assert pd.isna(row["terminal_depth"]) and not bool(row["resolved_lineage"])
    assert int(row["max_attained_depth"]) == 1
    assert row["terminal_event_id"] == "M1" and row["terminal_time"] == frame.index[4]

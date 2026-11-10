"""One lineage semantics across 3-, 4- and 5-scale ladders (review finding M10)."""

import numpy as np
import pandas as pd
import pytest

from dc_basics import dc_live_features, parse_dc_events, prepare_event_ledger
from dc_basics.hierarchy import build_adjacent_attempts
from dc_basics.lineage import (
    build_five_scale_linkages,
    build_four_scale_linkages,
    build_lineage_tables,
    build_scale_linkages,
    build_three_scale_linkages,
)

SCALES = ("small", "medium", "large", "macro", "outer")
THRESHOLDS = dict(zip(SCALES, (0.002, 0.003, 0.0045, 0.00675, 0.010125), strict=True))
MODE_MAP = {1.0: "up", -1.0: "down"}


def _values(series: pd.Series) -> list[object]:
    return series.astype(object).where(series.notna(), None).tolist()


@pytest.fixture(scope="module")
def ladder() -> dict[str, object]:
    rng = np.random.default_rng(7)
    index = pd.date_range("2024-01-01", periods=20_000, freq="5min")
    prices = pd.Series(100.0 * np.exp(np.cumsum(rng.normal(0.0, 0.0008, len(index)))), index=index)
    mode_frame = pd.DataFrame(index=index)
    for scale in SCALES:
        theta = THRESHOLDS[scale]
        ledger = prepare_event_ledger(parse_dc_events(prices=prices, theta=theta), scale[0].upper(), scale, theta)
        live = dc_live_features(prices, theta=theta)
        mode_frame[f"{scale}_mode"] = live["direction"].map(MODE_MAP)
        mode_frame[f"{scale}_upward_dcc"] = live["upward_dcc"].astype(bool)
        mode_frame[f"{scale}_downward_dcc"] = live["downward_dcc"].astype(bool)
        mode_frame[f"{scale}_event_id"] = index.to_series().map(ledger.set_index("dcc_idx")["event_id"])
    attempts = {
        f"{lower}_to_{upper}": build_adjacent_attempts(mode_frame, lower, upper)
        for lower, upper in zip(SCALES[:-1], SCALES[1:], strict=True)
    }
    small_attempts = attempts["small_to_medium"]
    previous = mode_frame[[f"{scale}_mode" for scale in SCALES]].shift(1)
    previous = previous.loc[pd.DatetimeIndex(small_attempts["start_time"])]
    eligible = (previous.notna().all(axis=1) & previous.nunique(axis=1).eq(1)).to_numpy()
    seeds = small_attempts.loc[eligible].copy()
    assert len(seeds) > 50
    return {"attempts": attempts, "seeds": seeds}


def test_wide_and_narrow_five_scale_views_share_semantics(ladder: dict[str, object]) -> None:
    attempts, seeds = ladder["attempts"], ladder["seeds"]
    narrow, stages = build_five_scale_linkages(seeds, attempts)
    wide = build_scale_linkages(seeds, list(attempts.values())[1:], SCALES)
    canonical, canonical_stages = build_lineage_tables(seeds, list(attempts.values())[1:], SCALES)

    for column in ("terminal_depth", "terminal_time", "terminal_position", "terminal_event_id",
                   "origin_mode", "target_mode", "max_attained_depth", "same_bar_stage_count",
                   "resolved_lineage", "strict_clean"):
        assert _values(narrow[column]) == _values(wide[column]) == _values(canonical[column]), column
    pd.testing.assert_frame_equal(stages, canonical_stages)
    assert narrow["origin_mode"].notna().all()
    assert narrow["origin_mode"].ne(narrow["target_mode"]).all()
    assert narrow["resolved_lineage"].eq(narrow["terminal_depth"].notna()).all()
    assert narrow.loc[narrow["resolved_lineage"], "terminal_outcome"].str.match(r"(reached|stopped)_").all()
    unresolved = ~narrow["resolved_lineage"]
    assert narrow.loc[unresolved, "terminal_depth"].isna().all()


def test_lower_ladders_are_truncations_of_the_five_scale_lineage(ladder: dict[str, object]) -> None:
    attempts, seeds = ladder["attempts"], ladder["seeds"]
    stage_frames = list(attempts.values())
    five, _ = build_five_scale_linkages(seeds, attempts)
    three = build_three_scale_linkages(seeds, stage_frames[1])
    four = build_four_scale_linkages(seeds, stage_frames[1], stage_frames[2])

    for ladder_size, table in ((3, three), (4, four)):
        top_depth = ladder_size - 1
        reached_top = five["max_attained_depth"].ge(top_depth)
        # Any five-scale lineage that confirmed the top scale of a shorter ladder
        # must be a completed top-depth lineage there.
        assert table.loc[reached_top, "terminal_depth"].eq(top_depth).all()
        # Below the top scale, the shorter ladder sees exactly the same stages.
        stopped_below = five["resolved_lineage"] & five["terminal_depth"].lt(top_depth)
        assert _values(table.loc[stopped_below, "terminal_depth"]) == _values(five.loc[stopped_below, "terminal_depth"])
        assert table.loc[stopped_below, "terminal_time"].equals(five.loc[stopped_below, "terminal_time"])


def test_strict_clean_removes_only_propagations(ladder: dict[str, object]) -> None:
    attempts, seeds = ladder["attempts"], ladder["seeds"]
    lineages, stages = build_five_scale_linkages(seeds, attempts)
    same_bar = stages.loc[pd.to_numeric(stages["resolution_bars"], errors="coerce").eq(0)]
    assert same_bar["outcome"].eq("propagated").all()

"""End-to-end prefix invariance (review finding M17).

A causal object built from ``prices[:k]`` must agree with the same object built
from the full path on everything that was knowable by bar ``k``. Each test
builds both versions and compares them. That catches any construction that
quietly reads later bars, which the in-notebook audits cannot do: they inspect
one finished table, where a leaked value looks like any other value.

The cut points straddle the 60/20/20 train/validation/test boundaries of the
synthetic path.
"""

import warnings

import numpy as np
import pandas as pd
import pytest

from dc_basics import (
    build_adjacent_attempts,
    build_lineage_tables,
    dc_live_features,
    parse_dc_events,
    prepare_event_ledger,
)
from dc_multiscale_research import build_multiscale_state

ROWS = 6_000
CUT_POSITIONS = (2_999, 3_600, 4_801)
SCALES = ("small", "medium", "large", "macro")
THRESHOLDS = dict(zip(SCALES, (0.002, 0.003, 0.0045, 0.00675), strict=True))
MODE_MAP = {1.0: "up", -1.0: "down"}
UNRESOLVED = "unresolved_at_sample_end"


@pytest.fixture(scope="module")
def prices() -> pd.Series:
    rng = np.random.default_rng(20261110)
    index = pd.date_range("2024-01-01", periods=ROWS, freq="5min")
    return pd.Series(100.0 * np.exp(np.cumsum(rng.normal(0.0, 0.0008, ROWS))), index=index, name="close")


def _ledgers(path: pd.Series) -> dict[str, pd.DataFrame]:
    return {
        scale: prepare_event_ledger(parse_dc_events(prices=path, theta=theta), scale[0].upper(), scale, theta)
        for scale, theta in THRESHOLDS.items()
    }


def _mode_frame(path: pd.Series, ledgers: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frame = pd.DataFrame(index=path.index)
    for scale, theta in THRESHOLDS.items():
        live = dc_live_features(path, theta=theta)
        frame[f"{scale}_mode"] = live["direction"].map(MODE_MAP)
        frame[f"{scale}_upward_dcc"] = live["upward_dcc"].astype(bool)
        frame[f"{scale}_downward_dcc"] = live["downward_dcc"].astype(bool)
        frame[f"{scale}_event_id"] = path.index.to_series().map(ledgers[scale].set_index("dcc_idx")["event_id"])
    return frame


def _attempts(frame: pd.DataFrame) -> list[pd.DataFrame]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)  # upper-led reversals are audited elsewhere
        return [build_adjacent_attempts(frame, lower, upper) for lower, upper in zip(SCALES[:-1], SCALES[1:])]


def _broad_agreement_seeds(frame: pd.DataFrame, small_attempts: pd.DataFrame) -> pd.DataFrame:
    previous = frame[[f"{scale}_mode" for scale in SCALES]].shift(1)
    previous = previous.loc[pd.DatetimeIndex(small_attempts["start_time"])]
    eligible = (previous.notna().all(axis=1) & previous.nunique(axis=1).eq(1)).to_numpy()
    return small_attempts.loc[eligible].reset_index(drop=True)


@pytest.fixture(scope="module")
def full_objects(prices: pd.Series) -> dict[str, object]:
    ledgers = _ledgers(prices)
    frame = _mode_frame(prices, ledgers)
    return {"ledgers": ledgers, "frame": frame, "attempts": _attempts(frame)}


def _same(left: pd.DataFrame, right: pd.DataFrame) -> None:
    pd.testing.assert_frame_equal(
        left.reset_index(drop=True), right.reset_index(drop=True), check_dtype=False, check_index_type=False
    )


@pytest.mark.parametrize("cut", CUT_POSITIONS)
def test_completed_event_ledgers_are_prefix_invariant(prices: pd.Series, full_objects: dict, cut: int) -> None:
    cut_time = prices.index[cut]
    prefix = _ledgers(prices.iloc[: cut + 1])
    for scale in SCALES:
        full = full_objects["ledgers"][scale]
        known = full.loc[full["information_time"].le(cut_time)]
        assert len(known) > 10, scale
        _same(known, prefix[scale])


@pytest.mark.parametrize("cut", CUT_POSITIONS)
def test_live_features_and_mode_frame_are_prefix_invariant(prices: pd.Series, full_objects: dict, cut: int) -> None:
    prefix_prices = prices.iloc[: cut + 1]
    for theta in THRESHOLDS.values():
        pd.testing.assert_frame_equal(
            dc_live_features(prices, theta=theta).iloc[: cut + 1], dc_live_features(prefix_prices, theta=theta)
        )
    prefix_frame = _mode_frame(prefix_prices, _ledgers(prefix_prices))
    pd.testing.assert_frame_equal(full_objects["frame"].iloc[: cut + 1], prefix_frame)


@pytest.mark.parametrize("cut", CUT_POSITIONS)
def test_adjacent_attempts_are_prefix_invariant(prices: pd.Series, full_objects: dict, cut: int) -> None:
    cut_time = prices.index[cut]
    prefix_prices = prices.iloc[: cut + 1]
    prefix_attempts = _attempts(_mode_frame(prefix_prices, _ledgers(prefix_prices)))
    seed_columns = ["edge", "initiating_event_id", "start_time", "start_position", "target_mode", "prior_upper_mode"]

    for full, prefix in zip(full_objects["attempts"], prefix_attempts, strict=True):
        started = full.loc[full["start_time"].le(cut_time)].reset_index(drop=True)
        prefix = prefix.reset_index(drop=True)
        _same(started[seed_columns], prefix[seed_columns])

        resolved_in_prefix = prefix["outcome"].ne(UNRESOLVED).to_numpy()
        assert resolved_in_prefix.any()
        _same(started.loc[resolved_in_prefix], prefix.loc[resolved_in_prefix])
        # An attempt still open at the cut must resolve strictly later in the full sample.
        still_open = started.loc[~resolved_in_prefix]
        assert (still_open["outcome"].eq(UNRESOLVED) | still_open["resolution_time"].gt(cut_time)).all()


@pytest.mark.parametrize("cut", CUT_POSITIONS)
def test_exact_lineages_are_prefix_invariant(prices: pd.Series, full_objects: dict, cut: int) -> None:
    cut_time = prices.index[cut]
    full_attempts = full_objects["attempts"]
    full_lineages, full_stages = build_lineage_tables(
        _broad_agreement_seeds(full_objects["frame"], full_attempts[0]), full_attempts[1:], SCALES
    )

    prefix_prices = prices.iloc[: cut + 1]
    prefix_frame = _mode_frame(prefix_prices, _ledgers(prefix_prices))
    prefix_attempts = _attempts(prefix_frame)
    prefix_lineages, prefix_stages = build_lineage_tables(
        _broad_agreement_seeds(prefix_frame, prefix_attempts[0]), prefix_attempts[1:], SCALES
    )

    full_by_id = full_lineages.set_index("lineage_id")
    prefix_by_id = prefix_lineages.set_index("lineage_id")
    assert prefix_by_id.index.isin(full_by_id.index).all()
    seed_columns = ["seed_time", "seed_position", "origin_mode", "target_mode"]
    _same(full_by_id.loc[prefix_by_id.index, seed_columns], prefix_by_id[seed_columns])

    # A lineage whose terminal label was knowable by the cut must match the full-sample lineage exactly.
    settled = prefix_by_id["resolved_lineage"] & prefix_by_id["outcome_information_time"].le(cut_time)
    assert settled.any()
    _same(full_by_id.loc[prefix_by_id.index[settled]], prefix_by_id.loc[settled])

    # Every stage resolved by the cut is identical, including its exact hand-off event IDs.
    resolved_stages = prefix_stages.loc[prefix_stages["outcome"].ne(UNRESOLVED)]
    keys = ["lineage_id", "stage_order"]
    merged = resolved_stages.merge(full_stages, on=keys, suffixes=("", "_full"), validate="one_to_one")
    for column in ("initiating_event_id", "start_time", "outcome", "resolution_event_id", "resolution_time"):
        assert merged[column].astype(object).equals(merged[f"{column}_full"].astype(object)), column


@pytest.mark.parametrize("cut", CUT_POSITIONS)
def test_multiscale_state_is_prefix_invariant_on_every_column(prices: pd.Series, cut: int) -> None:
    thresholds = tuple(THRESHOLDS.values())
    _, full_global, full_scale = build_multiscale_state(prices, thresholds, firing_window=60)
    _, prefix_global, prefix_scale = build_multiscale_state(prices.iloc[: cut + 1], thresholds, firing_window=60)

    common = prefix_global.index.intersection(full_global.index)
    assert len(common) == len(prefix_global) > 0
    pd.testing.assert_frame_equal(full_global.loc[common], prefix_global.loc[common])

    cut_time = prices.index[cut]
    time_column = "time" if "time" in full_scale.columns else None
    if time_column is None:
        full_known = full_scale.loc[full_scale.index.get_level_values(0) <= cut_time]
    else:
        full_known = full_scale.loc[full_scale[time_column].le(cut_time)]
    _same(full_known, prefix_scale)

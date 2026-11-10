"""Live-panel invariants on a synthetic three-scale path.

The panel must stop before each stage resolution, so the active stage's own
lower and upper clocks can never fire inside it. The informative count is the
activity on clocks below the active lower clock.
"""

from enum import StrEnum

import numpy as np
import pandas as pd
import pytest

from dc_basics.audit import audit_live_panel
from dc_basics.core import dc_live_features, parse_dc_events
from dc_basics.events import prepare_event_ledger
from dc_basics.hierarchy import build_adjacent_attempts
from dc_basics.lineage import build_three_scale_linkages, build_wide_stage_table
from dc_basics.live import build_causal_running_extreme
from dc_basics.live_panel import (
    AUC_CONSTANT_BY_CONSTRUCTION,
    AUC_CONSTANT_IN_SAMPLE,
    AUC_INSUFFICIENT_SAMPLE,
    LivePanelContext,
    build_live_panel,
    compare_initiation_and_live_features,
    constant_by_construction_features,
    summarize_checkpoint_overlap,
)
from dc_basics.live_plotting import (
    DEFAULT_TRAJECTORY_FEATURES,
    FIRST_STAGE_TRAJECTORY_FEATURES,
    plot_stage_trajectories,
)


class Scale(StrEnum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


SCALE_ORDER = (Scale.SMALL, Scale.MEDIUM, Scale.LARGE)
THRESHOLDS = {Scale.SMALL: 0.002, Scale.MEDIUM: 0.004, Scale.LARGE: 0.006}
PREFIXES = {Scale.SMALL: "S", Scale.MEDIUM: "M", Scale.LARGE: "L"}
STAGE_SPECS = {
    "small_to_medium": (Scale.SMALL, Scale.MEDIUM),
    "medium_to_large": (Scale.MEDIUM, Scale.LARGE),
}


def synthetic_prices() -> pd.Series:
    rng = np.random.default_rng(7)
    returns = rng.normal(0.0, 0.0008, 6000)
    index = pd.date_range("2024-01-01", periods=returns.size, freq="5min")
    return pd.Series(100.0 * np.exp(np.cumsum(returns)), index=index, name="SYN")


def build_three_scale_inputs(prices: pd.Series) -> dict[str, object]:
    ledgers, live_frames = {}, {}
    mode_frame = pd.DataFrame(index=prices.index)
    for scale in SCALE_ORDER:
        theta = THRESHOLDS[scale]
        ledgers[scale] = prepare_event_ledger(parse_dc_events(prices=prices, theta=theta), PREFIXES[scale],
                                              scale, theta)
        live_frames[scale] = dc_live_features(prices, theta=theta)
        mode_frame[f"{scale}_mode"] = live_frames[scale]["direction"].map({1.0: "up", -1.0: "down"})
        mode_frame[f"{scale}_upward_dcc"] = live_frames[scale]["upward_dcc"].astype(bool)
        mode_frame[f"{scale}_downward_dcc"] = live_frames[scale]["downward_dcc"].astype(bool)
        mode_frame[f"{scale}_event_id"] = mode_frame.index.to_series().map(
            ledgers[scale].set_index("dcc_idx")["event_id"]
        )
    small_medium = build_adjacent_attempts(mode_frame, Scale.SMALL, Scale.MEDIUM)
    medium_large = build_adjacent_attempts(mode_frame, Scale.MEDIUM, Scale.LARGE)
    prior = mode_frame[[f"{scale}_mode" for scale in SCALE_ORDER]].shift(1)
    prior = prior.loc[pd.DatetimeIndex(small_medium["start_time"])]
    seeds = small_medium.loc[(prior.notna().all(axis=1) & prior.nunique(axis=1).eq(1)).to_numpy()]
    linkages = build_three_scale_linkages(seeds, medium_large)
    resolved = linkages.loc[linkages["terminal_depth"].notna()]
    stage_one_end = resolved["terminal_position"].where(resolved["terminal_depth"].eq(0), resolved["medium_position"])
    stage_two_live = resolved["terminal_depth"].eq(0) | pd.to_numeric(resolved["terminal_position"]).gt(
        pd.to_numeric(resolved["medium_position"])
    )
    strict = resolved.loc[
        resolved["terminal_label_hindsight_at_seed"]
        & ~resolved["small_medium_same_bar"]
        & ~resolved["medium_large_same_bar"]
        & pd.to_numeric(stage_one_end).gt(resolved["seed_position"])
        & stage_two_live
    ].copy()
    dcc_cumulative = {
        scale: (mode_frame[f"{scale}_upward_dcc"] | mode_frame[f"{scale}_downward_dcc"])
        .astype(np.int64).cumsum().to_numpy()
        for scale in (Scale.SMALL, Scale.MEDIUM)
    }
    context = LivePanelContext(
        prices=prices,
        mode_frame=mode_frame,
        live_frames=live_frames,
        running_extremes={scale: build_causal_running_extreme(prices, live_frames[scale]) for scale in SCALE_ORDER},
        thresholds=THRESHOLDS,
        dcc_cumulative=dcc_cumulative,
        scale_order=SCALE_ORDER,
        event_ledgers=ledgers,
    )
    return {"context": context, "strict": strict, "stages": build_wide_stage_table(strict, SCALE_ORDER)}


@pytest.fixture(scope="module")
def three_scale() -> dict[str, object]:
    inputs = build_three_scale_inputs(synthetic_prices())
    inputs["panel"] = build_live_panel(inputs["stages"], inputs["strict"], inputs["context"], STAGE_SPECS)
    return inputs


def test_panel_passes_the_information_time_audit(three_scale: dict[str, object]) -> None:
    panel = three_scale["panel"]
    strict = three_scale["strict"]
    expected = {stage: int(strict["terminal_depth"].ge(order).sum()) for order, stage in enumerate(STAGE_SPECS)}
    audit = audit_live_panel(panel, expected_stage_counts=expected)
    assert audit["lineages"] == len(strict)
    assert panel["time"].lt(panel["stage_outcome_information_time"]).all()


def test_active_lower_and_upper_clocks_never_fire_inside_the_panel(three_scale: dict[str, object]) -> None:
    panel = three_scale["panel"]
    stage_one = panel.loc[panel["stage"].eq("small_to_medium")]
    stage_two = panel.loc[panel["stage"].eq("medium_to_large")]
    # The removed ``nested_lower_dccs`` feature was exactly these counts: zero everywhere.
    assert stage_one["nested_small_dccs"].eq(0).all()
    assert stage_one["nested_medium_dccs"].eq(0).all()
    assert stage_two["nested_medium_dccs"].eq(0).all()
    assert "nested_lower_dccs" not in panel and "nested_lower_dcc_rate" not in panel


def test_sub_lower_activity_is_informative_in_later_stages(three_scale: dict[str, object]) -> None:
    panel = three_scale["panel"]
    stage_one = panel.loc[panel["stage"].eq("small_to_medium")]
    stage_two = panel.loc[panel["stage"].eq("medium_to_large")]
    assert stage_one["sub_lower_scale_count"].eq(0).all()
    assert stage_one["sub_lower_dccs"].eq(0).all()
    assert stage_two["sub_lower_scale_count"].eq(1).all()
    assert stage_two["sub_lower_dccs"].gt(0).any()
    assert stage_two["sub_lower_dccs"].equals(stage_two["nested_small_dccs"])
    expected_rate = stage_two["sub_lower_dccs"] / np.maximum(stage_two["elapsed_bars"], 1)
    np.testing.assert_allclose(stage_two["sub_lower_dcc_rate"], expected_rate)


def test_lineage_age_counts_from_the_seed_not_the_stage(three_scale: dict[str, object]) -> None:
    panel = three_scale["panel"]
    stage_one = panel.loc[panel["stage"].eq("small_to_medium")]
    stage_two = panel.loc[panel["stage"].eq("medium_to_large")]
    assert stage_one["lineage_age_bars"].equals(stage_one["elapsed_bars"])
    assert stage_two["lineage_age_bars"].gt(stage_two["elapsed_bars"]).all()


def test_completed_initiation_legs_are_joined_by_exact_event_id(three_scale: dict[str, object]) -> None:
    panel = three_scale["panel"]
    ledgers = three_scale["context"].event_ledgers
    small = ledgers[Scale.SMALL].set_index("event_id")
    medium = ledgers[Scale.MEDIUM].set_index("event_id")
    stage_two = panel.loc[panel["stage"].eq("medium_to_large")].drop_duplicates("lineage_id")
    np.testing.assert_allclose(stage_two["seed_leg_r"], small.loc[stage_two["seed_small_event_id"], "r"])
    np.testing.assert_allclose(stage_two["stage_start_leg_tmv"], medium.loc[stage_two["stage_start_event_id"], "tmv"])
    assert stage_two["stage_start_leg_information_time"].eq(stage_two["stage_start_time"]).all()
    assert panel["feature_information_time"].eq(panel["time"]).all()


def test_joining_the_wrong_completed_leg_fails(three_scale: dict[str, object]) -> None:
    context = three_scale["context"]
    shifted = context.event_ledgers[Scale.SMALL].copy()
    # Every ID still exists, but now points at the neighbouring completed leg.
    shifted["event_id"] = np.roll(shifted["event_id"].to_numpy(), 1)
    broken = LivePanelContext(**{**context.__dict__, "event_ledgers": {**context.event_ledgers, Scale.SMALL: shifted}})
    with pytest.raises(AssertionError, match="became known"):
        build_live_panel(three_scale["stages"], three_scale["strict"], broken, STAGE_SPECS)


def test_constant_by_construction_registry() -> None:
    constant = constant_by_construction_features(STAGE_SPECS, SCALE_ORDER)
    assert constant["small_to_medium"] == {
        "nested_small_dccs", "nested_medium_dccs", "sub_lower_dccs", "sub_lower_dcc_rate",
    }
    assert constant["medium_to_large"] == {"nested_medium_dccs", "nested_large_dccs"}


def test_checkpoint_overlap_explains_every_missing_auc() -> None:
    rng = np.random.default_rng(3)
    outcome = np.repeat(["propagated", "rejected"], [40, 30])
    rows = pd.DataFrame({
        "stage": "medium_to_large",
        "elapsed_bars": 0,
        "future_stage_outcome": outcome,
        "informative": np.where(outcome == "propagated", 1.0, 0.0) + rng.normal(0, 0.1, outcome.size),
        "flat": 1.0,
        "nested_medium_dccs": 0,
    })
    summary = summarize_checkpoint_overlap(
        rows, ["informative", "flat", "nested_medium_dccs"],
        constant_by_construction={"medium_to_large": frozenset({"nested_medium_dccs"})},
    ).set_index("feature")
    assert summary.loc["informative", "orientation_free_auc"] > 0.95
    assert summary.loc["informative", "stronger_value_direction"] == "higher"
    assert summary.loc["flat", "stronger_value_direction"] == AUC_CONSTANT_IN_SAMPLE
    assert summary.loc["nested_medium_dccs", "stronger_value_direction"] == AUC_CONSTANT_BY_CONSTRUCTION

    small = summarize_checkpoint_overlap(rows.iloc[25:45], ["informative"], min_class_count=20)
    assert small.loc[0, "stronger_value_direction"] == AUC_INSUFFICIENT_SAMPLE
    assert np.isnan(small.loc[0, "orientation_free_auc"])


def test_incremental_comparison_detects_live_information() -> None:
    rng = np.random.default_rng(11)
    size = 400
    live = rng.normal(size=size)
    outcome = np.where(live + rng.normal(0, 0.5, size) > 0.0, "propagated", "rejected")
    rows = pd.DataFrame({
        "lineage_id": [f"S{number}" for number in range(size)],
        "stage_start_time": pd.date_range("2024-01-01", periods=size, freq="h"),
        "future_stage_outcome": outcome,
        "seed_leg_r": rng.lognormal(size=size),
        "target_progress": live,
    })
    result = compare_initiation_and_live_features(rows, ["seed_leg_r"], ["target_progress"])
    assert result["status"] == "ok"
    assert result["oos_auc_initiation_plus_live"] > 0.8
    assert result["oos_auc_gain"] > 0.2
    assert result["best_live_feature"] == "target_progress"

    tiny = compare_initiation_and_live_features(rows.iloc[:15], ["seed_leg_r"], ["target_progress"])
    assert tiny["status"] == AUC_INSUFFICIENT_SAMPLE


def test_default_trajectory_features_skip_zero_by_construction_counts(three_scale: dict[str, object]) -> None:
    # A three-scale panel has no hierarchy columns; add the one the defaults plot.
    panel = three_scale["panel"].assign(direction_boundaries=0)
    assert "sub_lower_dcc_rate" in DEFAULT_TRAJECTORY_FEATURES
    assert not any(feature.startswith("nested_lower") for feature in DEFAULT_TRAJECTORY_FEATURES)
    first = plot_stage_trajectories(panel, "small_to_medium", 40, symbol="SYN")
    later = plot_stage_trajectories(panel, "medium_to_large", 40, symbol="SYN")
    assert [annotation.text for annotation in first.layout.annotations] == list(
        FIRST_STAGE_TRAJECTORY_FEATURES.values()
    )
    assert [annotation.text for annotation in later.layout.annotations] == list(
        DEFAULT_TRAJECTORY_FEATURES.values()
    )


@pytest.mark.parametrize("cut", (2_999, 4_200))
def test_live_panel_is_prefix_invariant(three_scale: dict[str, object], cut: int) -> None:
    """Rebuilding everything from ``prices[:cut + 1]`` reproduces the full-sample panel rows (review M17).

    Only lineages that were already fully resolved by the cut can enter the prefix
    panel; each of their rows, live features and hindsight labels included, must
    match the full-sample build exactly.
    """
    prefix_inputs = build_three_scale_inputs(synthetic_prices().iloc[: cut + 1])
    prefix_panel = build_live_panel(
        prefix_inputs["stages"], prefix_inputs["strict"], prefix_inputs["context"], STAGE_SPECS
    )
    full_panel = three_scale["panel"]
    keys = ["lineage_id", "stage_order", "time"]
    assert len(prefix_panel) > 100
    assert prefix_panel["lineage_id"].isin(full_panel["lineage_id"]).all()
    expected = (
        full_panel.loc[full_panel["lineage_id"].isin(prefix_panel["lineage_id"])]
        .sort_values(keys).reset_index(drop=True)
    )
    pd.testing.assert_frame_equal(expected, prefix_panel.sort_values(keys).reset_index(drop=True))

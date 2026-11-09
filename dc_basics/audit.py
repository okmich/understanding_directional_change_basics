"""Reusable causality and linkage audits."""

from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd


DEFAULT_LIVE_FEATURES = (
    "lower_tmv_live", "lower_t_live", "lower_r_live",
    "upper_tmv_live", "upper_t_live", "upper_r_live",
    "target_progress", "max_target_progress",
)


def audit_live_panel(panel: pd.DataFrame, *, expected_stage_counts: Mapping[str, int] | None = None,
                     required_features: Sequence[str] = DEFAULT_LIVE_FEATURES,
                     require_seed_identity: bool = True) -> pd.Series:
    """Assert the information-time contract and summarize a causal live panel."""
    if panel.empty:
        raise AssertionError("The live panel is empty.")
    if not panel["stage_outcome_is_hindsight"].all():
        raise AssertionError("A live row includes a stage outcome already known on that bar.")
    if not panel["terminal_outcome_is_hindsight"].all():
        raise AssertionError("A live row includes a terminal outcome already known on that bar.")
    if not panel["feature_information_time"].eq(panel["time"]).all():
        raise AssertionError("A live feature has an invalid information timestamp.")
    if panel[list(required_features)].isna().any().any():
        raise AssertionError("A required causal live feature is missing.")
    if np.nanmax(panel["target_progress"]) >= 1.0 + 1e-10:
        raise AssertionError("Pre-resolution target progress reached the upper DCC threshold.")

    observed_stage_counts = panel.groupby("stage")["lineage_id"].nunique().to_dict()
    if expected_stage_counts is not None and observed_stage_counts != dict(expected_stage_counts):
        raise AssertionError("Live-panel stage counts disagree with exact linkage.")
    changed_seed_ids = 0
    if require_seed_identity and "seed_small_event_id" in panel:
        seed_counts = panel.groupby("lineage_id")["seed_small_event_id"].nunique()
        changed_seed_ids = int(seed_counts.ne(1).sum())
        if changed_seed_ids:
            raise AssertionError("A lineage changed its immutable seed ID.")

    summary: dict[str, object] = {
        "lineages": panel["lineage_id"].nunique(),
        "active_pre_resolution_rows": len(panel),
        "maximum_pre_resolution_progress": panel["target_progress"].max(),
        "seed_ids_that_changed": changed_seed_ids,
    }
    summary.update({f"{stage}_lineages": count for stage, count in observed_stage_counts.items()})
    for column in panel.columns:
        if column.startswith("nested_") and column.endswith("_dccs"):
            summary[f"maximum_{column}"] = panel[column].max()
    return pd.Series(summary, name="value")


def count_events_inside(positions: np.ndarray, start_position: int, end_position: int) -> int:
    left = np.searchsorted(positions, start_position, side="right")
    right = np.searchsorted(positions, end_position, side="right")
    return int(right - left)


def summarize_stage(sample: pd.DataFrame, stage_name: str) -> dict[str, object]:
    resolved = sample.loc[sample["outcome"].isin(["propagated", "rejected"])]
    propagated = resolved["outcome"].eq("propagated")
    return {
        "stage": stage_name,
        "attempts": len(sample),
        "resolved_attempts": len(resolved),
        "propagation_rate": propagated.mean() if len(resolved) else np.nan,
        "median_resolution_bars": resolved["resolution_bars"].median(),
        "same_bar_rate": resolved["resolution_bars"].eq(0).mean() if len(resolved) else np.nan,
    }

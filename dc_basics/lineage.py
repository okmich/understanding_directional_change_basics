"""Cross-threshold hand-offs and small-origin lineage construction."""

from collections.abc import Mapping, Sequence
from enum import Enum

import pandas as pd

from .enums import AttemptOutcome
from .events import enum_value


def _edge_name(lower: str, upper: str) -> str:
    return f"{lower}_{upper}"


def build_scale_linkages(seed_attempts: pd.DataFrame, later_attempts: Sequence[pd.DataFrame],
                         scales: Sequence[str | Enum]) -> pd.DataFrame:
    """Build a wide small-origin lineage across an arbitrary ordered scale ladder."""
    scale_names = tuple(enum_value(scale) for scale in scales)
    if len(scale_names) < 3 or len(later_attempts) != len(scale_names) - 2:
        raise ValueError("later_attempts must contain one frame for every edge after the seed edge.")
    lookups = []
    for stage_index, attempts in enumerate(later_attempts, start=1):
        if attempts["initiating_event_id"].duplicated().any():
            lower = scale_names[stage_index]
            raise AssertionError(f"A {lower} event initiates more than one next-scale attempt.")
        lookups.append(attempts.set_index("initiating_event_id", drop=False))

    records: list[dict[str, object]] = []
    edge_count = len(scale_names) - 1
    for seed in seed_attempts.itertuples(index=False):
        origin_mode = seed.prior_upper_mode
        target_mode = seed.target_mode
        record: dict[str, object] = {
            "seed_small_event_id": seed.initiating_event_id,
            "seed_time": seed.start_time,
            "seed_position": seed.start_position,
            "origin_mode": origin_mode,
            "target_mode": target_mode,
            "terminal_event_id": pd.NA,
            "terminal_time": pd.NaT,
            "terminal_position": pd.NA,
            "terminal_depth": pd.NA,
            "terminal_outcome": pd.NA,
        }
        for scale in scale_names[1:-1]:
            record.update({
                f"{scale}_event_id": pd.NA,
                f"{scale}_time": pd.NaT,
                f"{scale}_position": pd.NA,
            })
        for lower, upper in zip(scale_names[:-1], scale_names[1:], strict=True):
            edge = _edge_name(lower, upper)
            record.update({
                f"{edge}_outcome": pd.NA,
                f"{edge}_bars": pd.NA,
                f"{edge}_same_bar": False,
            })

        current = pd.Series(seed._asdict())
        for stage_index, (lower, upper) in enumerate(zip(scale_names[:-1], scale_names[1:], strict=True)):
            if stage_index > 0:
                lookup = lookups[stage_index - 1]
                handoff_event_id = record[f"{lower}_event_id"]
                if handoff_event_id not in lookup.index:
                    record.update({
                        "terminal_time": record[f"{lower}_time"],
                        "terminal_position": record[f"{lower}_position"],
                        "terminal_outcome": f"unlinked_after_{lower}",
                    })
                    break
                current = lookup.loc[handoff_event_id]
                if isinstance(current, pd.DataFrame):
                    raise AssertionError("A hand-off event maps to multiple adjacent attempts.")
                if current["start_time"] != record[f"{lower}_time"]:
                    raise AssertionError(f"The shared {lower} event has inconsistent timestamps.")
                if current["target_mode"] != target_mode:
                    raise AssertionError("A linked stage changed the immutable target mode.")
                if current["prior_upper_mode"] != origin_mode:
                    raise AssertionError("A linked stage changed the immutable origin mode.")

            edge = _edge_name(lower, upper)
            outcome = current["outcome"]
            record[f"{edge}_outcome"] = outcome
            record[f"{edge}_bars"] = current["resolution_bars"]
            record[f"{edge}_same_bar"] = current["resolution_bars"] == 0

            if outcome == AttemptOutcome.PROPAGATED.value:
                if stage_index == edge_count - 1:
                    record.update({
                        "terminal_event_id": current["resolution_event_id"],
                        "terminal_time": current["resolution_time"],
                        "terminal_position": current["resolution_position"],
                        "terminal_depth": edge_count,
                        "terminal_outcome": f"reached_{upper}",
                    })
                    break
                record.update({
                    f"{upper}_event_id": current["resolution_event_id"],
                    f"{upper}_time": current["resolution_time"],
                    f"{upper}_position": current["resolution_position"],
                })
                continue

            record.update({
                "terminal_event_id": current["resolution_event_id"],
                "terminal_time": current["resolution_time"],
                "terminal_position": current["resolution_position"],
            })
            if outcome == AttemptOutcome.REJECTED.value:
                record.update({
                    "terminal_depth": stage_index,
                    "terminal_outcome": f"stopped_below_{upper}",
                })
            elif outcome == AttemptOutcome.AMBIGUOUS.value:
                record["terminal_outcome"] = f"ambiguous_{lower}_{upper}"
            elif outcome == AttemptOutcome.UNRESOLVED.value:
                record["terminal_outcome"] = f"unresolved_below_{upper}"
            else:
                raise ValueError(f"Unexpected stage outcome: {outcome}")
            break
        records.append(record)

    linkages = pd.DataFrame.from_records(records)
    linkages["terminal_depth"] = linkages["terminal_depth"].astype("Int64")
    for column in [column for column in linkages if column.endswith("_same_bar")]:
        linkages[column] = linkages[column].eq(True)
    linkages["outcome_information_time"] = linkages["terminal_time"]
    linkages["terminal_label_hindsight_at_seed"] = linkages["terminal_time"].gt(linkages["seed_time"])
    linkages["total_resolution_bars"] = (
        pd.to_numeric(linkages["terminal_position"], errors="coerce") - linkages["seed_position"]
    )
    return linkages


def build_three_scale_linkages(seeds: pd.DataFrame, second_stage: pd.DataFrame) -> pd.DataFrame:
    return build_scale_linkages(seeds, [second_stage], ("small", "medium", "large"))


def build_four_scale_linkages(seeds: pd.DataFrame, stage_two: pd.DataFrame,
                              stage_three: pd.DataFrame) -> pd.DataFrame:
    return build_scale_linkages(seeds, [stage_two, stage_three], ("small", "medium", "large", "macro"))


def build_five_scale_linkages(seed_attempts: pd.DataFrame,
                              stage_attempts: Mapping[str | Enum, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build canonical narrow lineage/stage tables for any mapping of four adjacent stages."""
    stage_order = tuple(stage_attempts)
    lookups = {
        stage: attempts.set_index("initiating_event_id", drop=False)
        for stage, attempts in stage_attempts.items()
    }
    stopped_outcomes = [
        f"stopped_below_{enum_value(stage).split('_to_')[-1]}" for stage in stage_order
    ]
    final_scale = enum_value(stage_order[-1]).split("_to_")[-1]
    lineage_records: list[dict[str, object]] = []
    stage_records: list[dict[str, object]] = []

    for seed in seed_attempts.itertuples(index=False):
        lineage_id = seed.initiating_event_id
        target_mode = seed.target_mode
        current_attempt = pd.Series(seed._asdict())
        terminal_depth = pd.NA
        terminal_outcome: str | None = None
        terminal_time = pd.NaT
        terminal_position = pd.NA
        handoff_failure_stage = pd.NA
        same_bar_stage_count = 0
        prior_resolution_event_id: object = None

        for stage_index, stage in enumerate(stage_order):
            if stage_index > 0:
                lookup = lookups[stage]
                if prior_resolution_event_id not in lookup.index:
                    terminal_outcome = "unlinked_handoff"
                    handoff_failure_stage = enum_value(stage)
                    break
                current_attempt = lookup.loc[prior_resolution_event_id]
                if isinstance(current_attempt, pd.DataFrame):
                    raise AssertionError("A hand-off event maps to multiple adjacent attempts.")
            if current_attempt["target_mode"] != target_mode:
                raise AssertionError("A linked stage changed the immutable target mode.")

            stage_records.append({
                "lineage_id": lineage_id,
                "target_mode": target_mode,
                "stage": enum_value(stage),
                "stage_order": stage_index,
                "attained_depth_before": stage_index,
                "initiating_event_id": current_attempt["initiating_event_id"],
                "start_time": current_attempt["start_time"],
                "start_position": int(current_attempt["start_position"]),
                "outcome": current_attempt["outcome"],
                "resolution_event_id": current_attempt["resolution_event_id"],
                "resolution_time": current_attempt["resolution_time"],
                "resolution_position": current_attempt["resolution_position"],
                "resolution_bars": current_attempt["resolution_bars"],
            })
            prior_resolution_event_id = current_attempt["resolution_event_id"]
            if pd.notna(current_attempt["resolution_bars"]) and int(current_attempt["resolution_bars"]) == 0:
                same_bar_stage_count += 1

            outcome = current_attempt["outcome"]
            if outcome == AttemptOutcome.PROPAGATED.value:
                if stage_index == len(stage_order) - 1:
                    terminal_depth = len(stage_order)
                    terminal_outcome = f"reached_{final_scale}"
                    terminal_time = current_attempt["resolution_time"]
                    terminal_position = current_attempt["resolution_position"]
                continue
            terminal_depth = stage_index
            terminal_time = current_attempt["resolution_time"]
            terminal_position = current_attempt["resolution_position"]
            if outcome == AttemptOutcome.REJECTED.value:
                terminal_outcome = stopped_outcomes[stage_index]
            elif outcome == AttemptOutcome.AMBIGUOUS.value:
                terminal_outcome = "ambiguous_stage"
            elif outcome == AttemptOutcome.UNRESOLVED.value:
                terminal_outcome = "unresolved_stage"
            else:
                raise ValueError(f"Unexpected stage outcome: {outcome}")
            break

        lineage_records.append({
            "lineage_id": lineage_id,
            "target_mode": target_mode,
            "seed_time": seed.start_time,
            "seed_position": int(seed.start_position),
            "terminal_depth": terminal_depth,
            "terminal_outcome": terminal_outcome,
            "terminal_time": terminal_time,
            "terminal_position": terminal_position,
            "handoff_failure_stage": handoff_failure_stage,
            "same_bar_stage_count": same_bar_stage_count,
        })

    lineages = pd.DataFrame.from_records(lineage_records)
    stages = pd.DataFrame.from_records(stage_records)
    resolved_outcomes = set(stopped_outcomes) | {f"reached_{final_scale}"}
    lineages["resolved_lineage"] = lineages["terminal_outcome"].isin(resolved_outcomes)
    lineages["strict_clean"] = lineages["resolved_lineage"] & lineages["same_bar_stage_count"].eq(0)
    return lineages, stages


def build_wide_stage_table(linkages: pd.DataFrame, scales: Sequence[str | Enum]) -> pd.DataFrame:
    """Convert a resolved wide 3/4-scale linkage table to canonical stage rows."""
    scale_names = tuple(enum_value(scale) for scale in scales)
    records: list[dict[str, object]] = []
    for lineage in linkages.itertuples(index=False):
        depth = int(lineage.terminal_depth)
        for stage_index, (lower, upper) in enumerate(zip(scale_names[:-1], scale_names[1:], strict=True)):
            if depth < stage_index:
                break
            if stage_index == 0:
                start_event_id = lineage.seed_small_event_id
                start_time = lineage.seed_time
                start_position = int(lineage.seed_position)
            else:
                start_event_id = getattr(lineage, f"{lower}_event_id")
                start_time = getattr(lineage, f"{lower}_time")
                start_position = int(getattr(lineage, f"{lower}_position"))
            propagated = depth >= stage_index + 1
            if propagated and stage_index < len(scale_names) - 2:
                resolution_event_id = getattr(lineage, f"{upper}_event_id")
                resolution_time = getattr(lineage, f"{upper}_time")
                resolution_position = int(getattr(lineage, f"{upper}_position"))
            else:
                resolution_event_id = lineage.terminal_event_id
                resolution_time = lineage.terminal_time
                resolution_position = int(lineage.terminal_position)
            records.append({
                "lineage_id": lineage.seed_small_event_id,
                "target_mode": lineage.target_mode,
                "stage": f"{lower}_to_{upper}",
                "stage_order": stage_index,
                "attained_depth_before": stage_index,
                "initiating_event_id": start_event_id,
                "start_time": start_time,
                "start_position": start_position,
                "outcome": (
                    AttemptOutcome.PROPAGATED.value if propagated else AttemptOutcome.REJECTED.value
                ),
                "resolution_event_id": resolution_event_id,
                "resolution_time": resolution_time,
                "resolution_position": resolution_position,
                "resolution_bars": resolution_position - start_position,
            })
    return pd.DataFrame.from_records(records)

"""Cross-threshold hand-offs and small-origin lineage construction.

One canonical tracer, :func:`build_lineage_tables`, follows each seed through
the adjacent contests by exact event ID. The older entry points are views of
that one result, so every ladder size shares one set of semantics:

- ``terminal_depth`` is defined only for *resolved* lineages (reached the top
  scale, or stopped by a rejection). Ambiguous, unresolved and unlinked
  lineages have ``terminal_depth`` missing; ``max_attained_depth`` records how
  many hand-offs they had confirmed before ending.
- ``terminal_time`` / ``terminal_position`` are the bar on which the lineage's
  fate became knowable. For an unlinked lineage that is the hand-off bar whose
  upper event initiated no next-scale attempt; for an unresolved lineage it is
  missing.
- Every hand-off is checked: the next attempt must start on the hand-off bar
  and keep the immutable target and origin modes.
- ``origin_mode`` (the agreed mode before the seed) is emitted in every view.

Two table shapes are offered:

- *wide* (:func:`build_scale_linkages`, ``build_three_scale_linkages``,
  ``build_four_scale_linkages``): one row per seed with per-scale hand-off and
  per-edge outcome columns. Outcome labels: ``reached_<top>``,
  ``stopped_below_<upper>``, ``ambiguous_<lower>_<upper>``,
  ``unresolved_below_<upper>``, ``unlinked_after_<lower>``.
- *narrow* (:func:`build_five_scale_linkages`): a lineage table plus one row
  per traversed stage. Outcome labels: ``reached_<top>``,
  ``stopped_below_<upper>``, ``ambiguous_stage``, ``unresolved_stage``,
  ``unlinked_handoff``.

Both carry ``resolved_lineage`` (terminal depth is defined),
``same_bar_stage_count`` and ``strict_clean`` (resolved and no zero-bar stage).
A zero-bar stage can only be a propagation (a rejection needs a later lower
DCC), so every lineage that ``strict_clean`` drops reached at least the first
upper scale: the strict-clean first-stage rate is biased low by construction.
Later conditional rates need not be, because ``strict_clean`` drops whole
lineages and a dropped lineage can still be rejected at a later stage. Use
``resolved_lineage`` for probability ladders and ``strict_clean`` where a
non-empty live interval is required.
"""

from collections.abc import Mapping, Sequence
from enum import Enum

import pandas as pd

from .enums import AttemptOutcome
from .events import enum_value

_RESOLVED_KINDS = ("reached", "stopped")


def _edge_name(lower: str, upper: str) -> str:
    return f"{lower}_{upper}"


def _stage_name(lower: str, upper: str) -> str:
    return f"{lower}_to_{upper}"


def _check_edge(attempts: pd.DataFrame, lower: str, upper: str, role: str) -> None:
    """Refuse an attempt table built for a different adjacent pair than the ladder expects.

    Passing stage frames in the wrong order would otherwise turn most lineages into
    silent ``unlinked`` rows rather than an error.
    """
    if attempts.empty or "edge" not in attempts:
        return
    expected = f"{lower}->{upper}"
    found = sorted(set(attempts["edge"].astype(str)))
    if found != [expected]:
        raise ValueError(f"{role} attempts are for edge(s) {found}, but the ladder expects {expected!r}.")


def _stage_lookups(stage_attempts: Sequence[pd.DataFrame], scale_names: Sequence[str]) -> list[pd.DataFrame]:
    lookups = []
    for stage_index, attempts in enumerate(stage_attempts, start=1):
        _check_edge(attempts, scale_names[stage_index], scale_names[stage_index + 1], f"Stage {stage_index + 1}")
        if attempts["initiating_event_id"].duplicated().any():
            raise AssertionError(f"A {scale_names[stage_index]} event initiates more than one next-scale attempt.")
        lookups.append(attempts.set_index("initiating_event_id", drop=False))
    return lookups


def _trace_lineages(seed_attempts: pd.DataFrame, later_attempts: Sequence[pd.DataFrame],
                    scale_names: Sequence[str],
                    stage_labels: Sequence[str]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Follow every seed through exact event-ID hand-offs (the single implementation)."""
    if len(scale_names) < 3 or len(later_attempts) != len(scale_names) - 2:
        raise ValueError("later_attempts must contain one frame for every edge after the seed edge.")
    if len(stage_labels) != len(scale_names) - 1:
        raise ValueError("stage_labels must name every adjacent edge.")
    _check_edge(seed_attempts, scale_names[0], scale_names[1], "Seed")
    lookups = _stage_lookups(later_attempts, scale_names)
    edge_count = len(scale_names) - 1
    lineages: list[dict[str, object]] = []
    stages: list[dict[str, object]] = []

    for seed in seed_attempts.itertuples(index=False):
        seed_row = pd.Series(seed._asdict())
        lineage_id = seed.initiating_event_id
        origin_mode = seed.prior_upper_mode
        target_mode = seed.target_mode
        lineage: dict[str, object] = {
            "lineage_id": lineage_id,
            "seed_time": seed.start_time,
            "seed_position": int(seed.start_position),
            "origin_mode": origin_mode,
            "target_mode": target_mode,
            "terminal_kind": None,
            "terminal_stage_index": pd.NA,
            "terminal_event_id": pd.NA,
            "terminal_time": pd.NaT,
            "terminal_position": pd.NA,
            "terminal_depth": pd.NA,
            "max_attained_depth": 0,
            "same_bar_stage_count": 0,
            "handoffs": {},
            "edges": {},
        }
        current = seed_row
        for stage_index, (lower, upper) in enumerate(zip(scale_names[:-1], scale_names[1:], strict=True)):
            if stage_index > 0:
                handoff_event_id, handoff_time, handoff_position = lineage["handoffs"][lower]
                lookup = lookups[stage_index - 1]
                if handoff_event_id not in lookup.index:
                    lineage.update({
                        "terminal_kind": "unlinked",
                        "terminal_stage_index": stage_index,
                        "terminal_event_id": handoff_event_id,
                        "terminal_time": handoff_time,
                        "terminal_position": handoff_position,
                    })
                    break
                current = lookup.loc[handoff_event_id]
                if isinstance(current, pd.DataFrame):
                    raise AssertionError("A hand-off event maps to multiple adjacent attempts.")
                if current["start_time"] != handoff_time:
                    raise AssertionError(f"The shared {lower} event has inconsistent timestamps.")
            if current["target_mode"] != target_mode:
                raise AssertionError("A linked stage changed the immutable target mode.")
            if current["prior_upper_mode"] != origin_mode:
                raise AssertionError("A linked stage changed the immutable origin mode.")

            outcome = current["outcome"]
            resolution_bars = current["resolution_bars"]
            same_bar = bool(pd.notna(resolution_bars) and int(resolution_bars) == 0)
            lineage["same_bar_stage_count"] += int(same_bar)
            lineage["edges"][_edge_name(lower, upper)] = (outcome, resolution_bars, same_bar)
            stages.append({
                "lineage_id": lineage_id,
                "target_mode": target_mode,
                "stage": stage_labels[stage_index],
                "stage_order": stage_index,
                "attained_depth_before": stage_index,
                "initiating_event_id": current["initiating_event_id"],
                "start_time": current["start_time"],
                "start_position": int(current["start_position"]),
                "outcome": outcome,
                "resolution_event_id": current["resolution_event_id"],
                "resolution_time": current["resolution_time"],
                "resolution_position": current["resolution_position"],
                "resolution_bars": resolution_bars,
            })

            if outcome == AttemptOutcome.PROPAGATED.value:
                lineage["max_attained_depth"] = stage_index + 1
                if stage_index == edge_count - 1:
                    lineage.update({
                        "terminal_kind": "reached",
                        "terminal_stage_index": stage_index,
                        "terminal_event_id": current["resolution_event_id"],
                        "terminal_time": current["resolution_time"],
                        "terminal_position": current["resolution_position"],
                        "terminal_depth": edge_count,
                    })
                    break
                lineage["handoffs"][upper] = (
                    current["resolution_event_id"], current["resolution_time"], current["resolution_position"],
                )
                continue

            lineage.update({
                "terminal_stage_index": stage_index,
                "terminal_event_id": current["resolution_event_id"],
                "terminal_time": current["resolution_time"],
                "terminal_position": current["resolution_position"],
            })
            if outcome == AttemptOutcome.REJECTED.value:
                lineage.update({"terminal_kind": "stopped", "terminal_depth": stage_index})
            elif outcome == AttemptOutcome.AMBIGUOUS.value:
                lineage["terminal_kind"] = "ambiguous"
            elif outcome == AttemptOutcome.UNRESOLVED.value:
                lineage["terminal_kind"] = "unresolved"
            else:
                raise ValueError(f"Unexpected stage outcome: {outcome}")
            break
        lineages.append(lineage)
    return lineages, stages


def _finish_common_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame["terminal_depth"] = frame["terminal_depth"].astype("Int64")
    frame["outcome_information_time"] = frame["terminal_time"]
    # An outcome that is never resolved in the sample is also unknown at the seed.
    frame["terminal_label_hindsight_at_seed"] = (
        frame["terminal_time"].isna() | frame["terminal_time"].gt(frame["seed_time"])
    )
    frame["total_resolution_bars"] = (
        pd.to_numeric(frame["terminal_position"], errors="coerce") - frame["seed_position"]
    )
    frame["resolved_lineage"] = frame["terminal_depth"].notna()
    frame["strict_clean"] = frame["resolved_lineage"] & frame["same_bar_stage_count"].eq(0)
    return frame


def build_lineage_tables(seed_attempts: pd.DataFrame, later_attempts: Sequence[pd.DataFrame],
                         scales: Sequence[str | Enum]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Canonical narrow lineage and stage tables for any ordered scale ladder.

    Returns ``(lineages, stages)``. ``lineages`` has one row per seed with a
    neutral ``terminal_kind`` (``reached``/``stopped``/``ambiguous``/
    ``unresolved``/``unlinked``); ``stages`` has one row per traversed stage.
    """
    scale_names = tuple(enum_value(scale) for scale in scales)
    stage_labels = [_stage_name(lower, upper) for lower, upper in zip(scale_names[:-1], scale_names[1:], strict=True)]
    lineage_records, stage_records = _trace_lineages(seed_attempts, later_attempts, scale_names, stage_labels)
    lineages = pd.DataFrame.from_records([
        {key: value for key, value in record.items() if key not in ("handoffs", "edges")}
        for record in lineage_records
    ])
    return _finish_common_columns(lineages), pd.DataFrame.from_records(stage_records)


def build_scale_linkages(seed_attempts: pd.DataFrame, later_attempts: Sequence[pd.DataFrame],
                         scales: Sequence[str | Enum]) -> pd.DataFrame:
    """Build a wide small-origin lineage across an arbitrary ordered scale ladder."""
    scale_names = tuple(enum_value(scale) for scale in scales)
    stage_labels = [_stage_name(lower, upper) for lower, upper in zip(scale_names[:-1], scale_names[1:], strict=True)]
    lineage_records, _ = _trace_lineages(seed_attempts, later_attempts, scale_names, stage_labels)
    top_scale = scale_names[-1]

    records: list[dict[str, object]] = []
    for lineage in lineage_records:
        kind = lineage["terminal_kind"]
        stage_index = lineage["terminal_stage_index"]
        lower, upper = scale_names[stage_index], scale_names[stage_index + 1]
        terminal_outcome = {
            "reached": f"reached_{top_scale}",
            "stopped": f"stopped_below_{upper}",
            "ambiguous": f"ambiguous_{lower}_{upper}",
            "unresolved": f"unresolved_below_{upper}",
            "unlinked": f"unlinked_after_{lower}",
        }[kind]
        record: dict[str, object] = {
            "seed_small_event_id": lineage["lineage_id"],
            "seed_time": lineage["seed_time"],
            "seed_position": lineage["seed_position"],
            "origin_mode": lineage["origin_mode"],
            "target_mode": lineage["target_mode"],
            "terminal_event_id": lineage["terminal_event_id"],
            "terminal_time": lineage["terminal_time"],
            "terminal_position": lineage["terminal_position"],
            "terminal_depth": lineage["terminal_depth"],
            "terminal_outcome": terminal_outcome,
        }
        for scale in scale_names[1:-1]:
            event_id, time, position = lineage["handoffs"].get(scale, (pd.NA, pd.NaT, pd.NA))
            record.update({f"{scale}_event_id": event_id, f"{scale}_time": time, f"{scale}_position": position})
        for edge_lower, edge_upper in zip(scale_names[:-1], scale_names[1:], strict=True):
            edge = _edge_name(edge_lower, edge_upper)
            outcome, bars, same_bar = lineage["edges"].get(edge, (pd.NA, pd.NA, False))
            record.update({f"{edge}_outcome": outcome, f"{edge}_bars": bars, f"{edge}_same_bar": same_bar})
        record.update({
            "max_attained_depth": lineage["max_attained_depth"],
            "same_bar_stage_count": lineage["same_bar_stage_count"],
        })
        records.append(record)

    linkages = pd.DataFrame.from_records(records)
    for column in [column for column in linkages if column.endswith("_same_bar")]:
        linkages[column] = linkages[column].eq(True)
    return _finish_common_columns(linkages)


def build_three_scale_linkages(seeds: pd.DataFrame, second_stage: pd.DataFrame) -> pd.DataFrame:
    return build_scale_linkages(seeds, [second_stage], ("small", "medium", "large"))


def build_four_scale_linkages(seeds: pd.DataFrame, stage_two: pd.DataFrame,
                              stage_three: pd.DataFrame) -> pd.DataFrame:
    return build_scale_linkages(seeds, [stage_two, stage_three], ("small", "medium", "large", "macro"))


def build_five_scale_linkages(seed_attempts: pd.DataFrame,
                              stage_attempts: Mapping[str | Enum, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build narrow lineage/stage tables for an ordered mapping of adjacent stages.

    Stage keys must be named ``<lower>_to_<upper>`` and chain (each stage's
    upper scale is the next stage's lower scale). The first mapping value is
    the full seed-edge attempt table; ``seed_attempts`` is the eligible subset.
    """
    stage_keys = tuple(stage_attempts)
    stage_labels = [enum_value(stage) for stage in stage_keys]
    pairs = [label.split("_to_") for label in stage_labels]
    if any(len(pair) != 2 for pair in pairs):
        raise ValueError("Stage names must have the form '<lower>_to_<upper>'.")
    if any(left[1] != right[0] for left, right in zip(pairs[:-1], pairs[1:], strict=True)):
        raise ValueError("Stages must chain: each upper scale must be the next stage's lower scale.")
    scale_names = (pairs[0][0], *[upper for _, upper in pairs])
    later_attempts = [stage_attempts[stage] for stage in stage_keys[1:]]
    lineage_records, stage_records = _trace_lineages(seed_attempts, later_attempts, scale_names, stage_labels)
    final_scale = scale_names[-1]

    records: list[dict[str, object]] = []
    for lineage in lineage_records:
        kind = lineage["terminal_kind"]
        stage_index = lineage["terminal_stage_index"]
        terminal_outcome = {
            "reached": f"reached_{final_scale}",
            "stopped": f"stopped_below_{scale_names[stage_index + 1]}",
            "ambiguous": "ambiguous_stage",
            "unresolved": "unresolved_stage",
            "unlinked": "unlinked_handoff",
        }[kind]
        records.append({
            "lineage_id": lineage["lineage_id"],
            "target_mode": lineage["target_mode"],
            "seed_time": lineage["seed_time"],
            "seed_position": lineage["seed_position"],
            "terminal_depth": lineage["terminal_depth"],
            "terminal_outcome": terminal_outcome,
            "terminal_time": lineage["terminal_time"],
            "terminal_position": lineage["terminal_position"],
            "handoff_failure_stage": stage_labels[stage_index] if kind == "unlinked" else pd.NA,
            "same_bar_stage_count": lineage["same_bar_stage_count"],
            "origin_mode": lineage["origin_mode"],
            "terminal_event_id": lineage["terminal_event_id"],
            "max_attained_depth": lineage["max_attained_depth"],
        })
    lineages = _finish_common_columns(pd.DataFrame.from_records(records))
    return lineages, pd.DataFrame.from_records(stage_records)


def build_wide_stage_table(linkages: pd.DataFrame, scales: Sequence[str | Enum]) -> pd.DataFrame:
    """Convert a resolved wide 3/4-scale linkage table to canonical stage rows."""
    scale_names = tuple(enum_value(scale) for scale in scales)
    if linkages["terminal_depth"].isna().any():
        raise ValueError("build_wide_stage_table requires resolved lineages (terminal_depth defined).")
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
                "stage": _stage_name(lower, upper),
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

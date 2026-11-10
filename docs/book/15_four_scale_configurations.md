# Chapter 15 — Sixteen configurations and coherent depth

## Purpose

Learn why four modes require structural shape, not merely a count of up and down directions.

## Configuration geometry

Four binary clocks produce $2^4=16$ ordered configurations `(small, medium, large, macro)`.

Examples:

- `down/down/up/up` has one boundary. Opposition has reached medium while large and macro remain up. This is a coherent depth-2 frontier.
- `down/up/down/down` has two boundaries. Although three modes are down, the ordered structure is fragmented.

Two summaries answer different questions:

- **agreement breadth:** how many scales match a reference such as macro;
- **direction-boundary count:** how many adjacent mode changes occur across the ordered vector.

One boundary can represent a coherent propagation frontier. Two or more boundaries imply fragmentation, for which a single coherent depth is undefined. All-equal vectors represent broad agreement.

Code note: the notebooks' `coherent_frontier` flag is True for at most one boundary, so it includes broad agreement as well as every single-boundary counter depth. Use `direction_boundaries == 1` when you mean exactly one live front.

## Ratio geometry

Equally spaced absolute thresholds do not have equal ratios. For a 0.2/0.4/0.6/0.8 ladder, adjacent ratios are 2.0, 1.5, and 1.33. Each edge therefore has a different propagation hurdle and event frequency.

## Lab

Run [4_threshold_dc.ipynb](../../4_threshold_dc.ipynb).

Inspect all four ledgers, sixteen configurations, legal transitions, same-bar ambiguity, adjacent contests, nesting, and price examples of broad coherence, shallow opposition, deep propagation, and fragmentation.

## Mandatory exercises

1. Read all configurations in scale order, not as an unordered vote.
2. Compare `down/down/up/up` with `down/up/down/down`.
3. Give two configurations with equal agreement breadth but different boundary counts.
4. Explain why coherent depth is undefined for a fragmented vector.
5. Relate the three adjacent ratios to their event and propagation frequencies.
6. Explain why three edge tables are not yet one four-scale lineage.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- Direction counts lose scale order; boundary count restores it.
- `down/down/up/up` is one coherent boundary; `down/up/down/down` has two and is fragmented.
- Coherent depth is undefined when multiple boundaries exist.
- `coherent_frontier` means at most one boundary, so it includes broad agreement; "exactly one boundary" is `direction_boundaries == 1`.
- Linear absolute spacing creates unequal adjacent ratios and edge behavior.

</details>

## Locked in

> Agreement breadth counts directions; boundary count preserves their scale order. Both are needed to distinguish coherence from fragmentation.

## Do not conclude

A coherent frontier is a current structural description, not a promise that propagation will continue.


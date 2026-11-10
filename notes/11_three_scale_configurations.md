# Chapter 11 — The eight three-scale configurations

## Purpose

Add a medium clock and learn to read a propagation ladder before linking any outcomes.

## Ordered configurations

Always read `(small, medium, large)` from left to right:

| Configurations | Structural reading |
|---|---|
| `up/up/up`, `down/down/down` | broad agreement |
| `down/up/up`, `up/down/down` | small-scale pullback or rebound |
| `down/down/up`, `up/up/down` | propagation has reached medium, not large |
| `down/up/down`, `up/down/up` | medium fragmentation |

The configuration is the current vector of three causal modes. It does not contain completed-leg direction, next-event direction, or terminal propagation depth.

## Two adjacent contests

Three scales create two separate building blocks:

1. small versus medium;
2. medium versus large.

A medium-to-large contest can contain multiple small-to-medium cycles. This is the beginning of the fractal intuition, but the clocks remain exact event processes rather than a visual metaphor.

Adjacent ratios matter. With 0.2%, 0.4%, and 0.6%, the small-to-medium ratio is 2.0 while medium-to-large is 1.5. Their event counts and propagation frequencies should not be assumed equal.

## Lab

Run [3_threshold_dc.ipynb](../3_threshold_dc.ipynb).

Inspect all three ledgers, configuration occupancy, legal transitions, adjacent contests, nesting counts, and the configuration casebook. When multiple components change on one close, mark the intrabar order unknown.

## Mandatory exercises

1. Read all eight configurations aloud in scale order.
2. For each configuration class, identify which scale has confirmed the target direction.
3. Name the exact DCC that changes one selected component.
4. Compare the two adjacent edges and explain why their ratios matter.
5. Explain the odd nesting count under clean completed upper intervals and list the boundary conditions that can break it, including the rare upper clock that confirms first (a flagged `parity_violation`).

## Completion gate G7 — Three-threshold mechanics

Before linkage, the learner must be able to:

1. Explain why the three clocks remain independent on one price path.
2. Read every `(small, medium, large)` configuration without confusing completed legs with live modes.
3. Identify broad agreement, a small pullback, propagation to medium, and medium fragmentation.
4. Name the exact DCC that changes each configuration component.
5. Explain why intrabar order is unknowable for same-bar multi-scale changes on close-only data.
6. Count small DCCs inside medium intervals and medium DCCs inside large intervals.
7. Explain the (near-invariant) odd nesting counts, how they encode rejected attempts, and what a flagged `parity_violation` means.
8. Distinguish a small-to-medium contest from a medium-to-large contest.
9. Identify the exact resolution bar for each adjacent-scale outcome.
10. Explain why edges with threshold ratios 2.0 and 1.5 need not behave alike.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- `up/up/up` and `down/down/down` are broad agreement.
- `down/up/up` and `up/down/down` are small-only opposition.
- `down/down/up` and `up/up/down` show propagation through medium.
- `down/up/down` and `up/down/up` are fragmented.
- The 2.0 and 1.5 adjacent ratios imply different edge behavior.

</details>

## Locked in

> Three scales turn binary propagation into a ladder: a disturbance may remain small, reach medium, or reach large.

## Do not conclude

A current `down/down/up` shape says where confirmation has reached, not where it will terminate.


# Chapter 18 — Five clocks and grid design

## Purpose

Use five thresholds to read a fuller scale profile and learn that the threshold grid itself is part of the model specification.

## Five is a teaching choice

Multithreshold Directional Change is real; five thresholds is not a canonical market calibration. Five is useful here because it exposes broad agreement, several propagation depths, and fragmented shapes while remaining visually inspectable.

The lab compares two grids sharing the same 0.20% small clock:

- **linear:** 0.20%, 0.40%, 0.60%, 0.80%, 1.00%;
- **constant ratio 1.5:** 0.20%, 0.30%, 0.45%, 0.675%, 1.0125%.

The linear grid has adjacent ratios 2.0, 1.5, 1.33, and 1.25. The geometric grid holds every ratio at 1.5. Both are causal descriptions of the same price path, but they ask different scale questions.

## Why the ratio matters

An adjacent ratio affects how much farther the lower-scale disturbance must travel before the upper clock confirms. It therefore affects event counts, nesting, stage duration, propagation frequency, and sample adequacy.

The link to propagation frequency is close to arithmetic. As in Chapter 10, each upper interval holds one propagation and $(n+1)/2$ lower attempts, so an adjacent rate is about $2/(N_{lower}/N_{upper}+1)$. The notebook prints this beside the observed rate for every edge. Equal ratios therefore give similar rates, and the linear grid's shrinking ratios give rising rates. Neither pattern says that upper-scale propagation is economically easier or harder.

No grid is “best” without a predeclared objective. Selecting the grid that later produces the most attractive regime or performance is leakage.

## How the primary grid is chosen

The notebook's interpretation lock uses a rule fixed before any outcome is seen: every hand-off should ask the same relative scale question, so the primary ladder must hold the adjacent ratio constant. The constant-ratio grid meets that rule by construction; the linear grid does not.

Clock adequacy is a minimum condition, not a selection criterion. On the lab sample it does not separate the grids anyway: both grids produce all 32 configurations and the same number of outer events. Observed propagation rates are recorded only as a post-hoc note after the lock, never as a reason for it.

## Lab

Run [5_threshold_dc.ipynb](../../5_threshold_dc.ipynb) through the clock and grid comparisons.

Verify that the two small clocks are identical, then identify where their higher-scale states diverge. Read those divergences as different observer grids, not contradictory truths.

## Mandatory exercises

1. Explain why five thresholds is useful but noncanonical.
2. Compute every adjacent ratio for both grids.
3. Explain why the small ledgers match and higher ledgers differ.
4. Choose a grid for a stated structural question before viewing outcomes.
5. Explain why an attractive ex-post propagation rate cannot select the grid.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- Five is a pedagogical scale count, not a standard calibration.
- Linear ratios are 2.0, 1.5, 1.33, and 1.25; the geometric ladder holds 1.5.
- Shared small thresholds produce the same small clock; different higher thresholds produce different causal hierarchies.
- Grid choice must follow a predeclared structural objective, not ex-post outcomes. Here the rule is a constant adjacent ratio, so every hand-off asks the same relative question; adequacy does not separate the grids (both show 32 configurations and the same outer-event count).
- Adjacent propagation rates are close to $2/(N_{lower}/N_{upper}+1)$: equal ratios give similar rates, shrinking linear ratios give rising rates, and neither is economic evidence.

</details>

## Locked in

> A threshold grid defines the scale questions the system asks; it is model specification, not neutral preprocessing.

## Do not conclude

Different grid readings do not imply that one parser is wrong. They reflect different definitions of meaningful scale.


# Chapter 16 — Three-stage linkage

## Purpose

Extend exact genealogy through small, medium, large, and macro without changing the root.

## Lineage construction

A strict root requires broad agreement on the previous bar. The initiating small DCC establishes the target direction and immutable lineage ID.

The possible stages are:

1. small to medium;
2. medium to large;
3. large to macro.

Each propagated stage resolves on an exact upper-scale DCC. That event ID must initiate the next contest. Medium and large event IDs are hand-off keys, never replacement seeds.

## Terminal depth

- depth 0: Stage 1 rejected;
- depth 1: medium attained, Stage 2 rejected;
- depth 2: large attained, Stage 3 rejected;
- depth 3: macro attained.

Depth becomes attained at the corresponding upper DCC. Terminal depth remains unknown until the active stage resolves. A depth-3 lineage may contain retracements and many lower-scale cycles; it is a genealogy of confirmations, not one monotonic leg.

## Cohort discipline

Two cohorts are used, and they are not interchangeable:

- **All resolved:** every lineage with a terminal depth, meaning it reached macro or was stopped by a rejection. Ambiguous, unresolved, and unlinked lineages have no terminal depth, so they stay explicit in the audits and are excluded from every probability ladder. This is the unbiased cohort for reach probabilities.
- **Strict clean:** resolved lineages whose every stage has at least one unresolved bar, which excludes same-bar stages. Live-interval work needs it. A same-bar stage can only be a propagation, because a rejection needs a later lower DCC, so strict-clean filtering removes propagations only and biases every conditional reach rate low.

Conditional reach rates multiply by the chain rule within one cohort.

## Lab

Run [4_threshold_dc_linkage.ipynb](../../../4_threshold_dc_linkage.ipynb).

Trace at least one lineage at each terminal depth and audit every hand-off against exact event IDs, direction, prior mode, and timestamp.

## Mandatory exercises

1. Explain why broad agreement on the previous bar gives definite ancestry.
2. Trace a depth-3 lineage without re-rooting it.
3. Identify the DCC that attains each depth.
4. Explain why linked and unconditional edge rates differ here but coincide at three scales.
5. Derive the three-factor cumulative reach identity without independence.
6. Explain why the strict-clean ladder is biased low relative to the all-resolved ladder.

## Locked in

> A four-scale lineage is one small-origin genealogy advanced by three exact confirmation hand-offs.

## Do not conclude

Terminal-depth frequencies summarize a declared cohort. They are not universal transition laws or trading alpha.


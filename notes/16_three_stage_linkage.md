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
- **Strict clean:** resolved lineages whose every stage has at least one unresolved bar, which excludes same-bar stages. Live-interval work needs it. A same-bar stage can only be a propagation, because a rejection needs a later lower DCC, so every lineage strict-clean drops reached at least medium and its P(reach medium) is biased low by construction. Later conditional rates need not be: the filter drops whole lineages, and a dropped lineage can still be rejected at a later stage.

Conditional reach rates multiply by the chain rule within one cohort.

## Lab

Run [4_threshold_dc_linkage.ipynb](../4_threshold_dc_linkage.ipynb).

Trace at least one lineage at each terminal depth and audit every hand-off against exact event IDs, direction, prior mode, and timestamp.

## Mandatory exercises

1. Explain why broad agreement on the previous bar gives definite ancestry.
2. Trace a depth-3 lineage without re-rooting it.
3. Identify the DCC that attains each depth.
4. Explain why the linked medium-to-large rate differs from the unconditional edge rate here, while each ladder's top edge coincided.
5. Derive the three-factor cumulative reach identity without independence.
6. Explain which strict-clean rate is biased low by construction (the first stage), and why later strict-clean rates need not be.

## Completion gate G12 — Four-threshold linkage

Before live development, the learner must be able to:

1. Require broad agreement on the bar before a valid root.
2. Keep the small event as immutable lineage ID through all stages.
3. Use medium and large event IDs as exact hand-off keys.
4. Explain why event-ID equality is stronger than timestamp proximity.
5. Define terminal depths 0 through 3 and the DCC where each depth is attained.
6. Explain why terminal depth remains hindsight until lineage resolution.
7. Keep same-bar, ambiguous, unresolved, and unlinked paths explicit.
8. Derive linked conditional reach rates without assuming independence, for both the all-resolved cohort and the strict-clean cohort (whose first-stage rate is biased low).
9. Explain why a depth-3 lineage need not be monotonic.
10. Explain why the intermediate linked rate differs from the unconditional edge rate at four scales, while each ladder's top edge coincided.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- Broad agreement on the prior bar gives the seed a definite origin.
- Medium and large IDs are exact hand-offs; the small ID remains root.
- Terminal depths 0–3 identify the stage of final rejection or macro attainment.
- A deep lineage may contain retracements; confirmation genealogy does not require monotonic price.
- The linked medium-to-large rate differs from the unconditional edge rate here because a root needs four-scale agreement; the top edge (large-to-macro) coincided, as did medium-to-large at three scales.
- Report reach rates on the all-resolved cohort. The strict-clean cohort drops lineages with a same-bar stage (always a propagation), so its first-stage rate is biased low; it is for live-interval work.

</details>

## Locked in

> A four-scale lineage is one small-origin genealogy advanced by three exact confirmation hand-offs.

## Do not conclude

Terminal-depth frequencies summarize a declared cohort. They are not universal transition laws or trading alpha.


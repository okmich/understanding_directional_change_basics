# Chapter 13 — Two-stage causal live development

## Purpose

Observe a linked lineage while its next confirmation is still unknown.

## State machine

The causal read is:

```text
idle
  -> Stage 1 after the small seed leaves broad agreement
  -> Stage 2 only after the exact medium DCC confirms the target
  -> terminal when the active contest rejects or propagates
```

The small seed ID and timestamp never change. During Stage 2, the medium event is the hand-off key. Later small DCCs are nested activity inside the same lineage, not new roots.

## Live rows

For each active stage, measure only through the bar before resolution:

- stage age (`elapsed_bars`) and lineage age since the seed (`lineage_age_bars`);
- lower- and upper-scale live TMV/T/R;
- target progress toward the upper DCC;
- current and maximum excursion;
- attained depth;
- activity on clocks below the active lower clock (`sub_lower_dccs`, `sub_lower_dcc_rate`), which in a three-scale ladder means small DCCs during Stage 2;
- the completed initiation legs: TMV/T/R of the leg confirmed by the seed DCC and, in Stage 2, of the leg confirmed by the medium hand-off DCC, each stamped with its own information time;
- current hierarchy configuration.

Target progress can be positive at checkpoint zero because the lower-scale DCC requires a nonzero move from the relevant upper-scale running extreme. Its exact geometry must be read from the stage definitions rather than assumed to start at zero.

The active stage's own clocks cannot fire inside its panel. A lower-scale DCC flips the lower mode away from the target, and an upper-scale DCC confirms propagation; either one is the resolution bar, which is excluded. Their nested counts are therefore zero by construction. Nested activity can only come from clocks below the lower clock, so Stage 1, whose lower clock is small, has none.

Stage-1 propagation becomes known at the medium DCC. At that moment attained depth becomes one, yet terminal depth remains unknown because Stage 2 has just begun.

## Lab

Run [3_threshold_dc_live_development.ipynb](../../3_threshold_dc_live_development.ipynb).

Audit timestamps, fixed checkpoints, overlap, survivor trajectories, and a full pinned-seed/hand-off casebook. Confirm that no feature row includes its resolution bar.

Overlap AUCs are shown beside their propagated and rejected survivor counts, and are withheld when either group has fewer than 20 survivors. Live Audit 2b compares live geometry with the completed initiation legs on the same survivor cohort.

## Mandatory exercises

1. Follow one lineage from idle through Stage 1 and Stage 2.
2. Explain why the medium event changes stage but not lineage identity.
3. Separate causal attained depth from hindsight terminal depth on three bars.
4. Explain the survivor composition at later checkpoints.
5. Decide whether live progress adds information beyond elapsed time and the completed initiation legs, using Live Audit 2b, which compares both on the same survivor cohort.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- The small seed remains lineage identity; the medium event only advances the stage.
- Later small DCCs inside Stage 2 are nested activity.
- Stage-1 propagation can be known while Stage-2 and terminal depth remain unknown.
- Every row's feature time is current; its stage and terminal outcome-information times are later.
- The active lower and upper clocks cannot fire inside a stage panel, because either DCC is the resolution bar. Nested activity therefore comes only from clocks below the lower clock, and Stage 1 has none.
- Whether live progress adds information is judged against the completed seed and hand-off legs on the same survivor cohort (Live Audit 2b). A positive out-of-sample gain is diagnostic, not a forecast.

</details>

## Locked in

> A lineage is stateful: the seed persists, exact confirmations advance the active stage, and each live row stops before the outcome becomes known.

## Do not conclude

An outcome-conditioned trajectory is a diagnostic explanation of path development, not a deployable forecast merely because its features are causal.


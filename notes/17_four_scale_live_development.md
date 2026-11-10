# Chapter 17 — Four-scale causal live development

## Purpose

Read a three-stage lineage bar by bar while preserving both its active contest and the shape of the whole hierarchy.

## Stage-local and hierarchy-wide information

Each live row contains two complementary views:

- **stage-local:** lower/upper modes, live TMV/T/R, target progress, stage and lineage age, the completed seed and hand-off legs, and activity on clocks below the active lower clock;
- **hierarchy-wide:** the four-mode vector, macro agreement breadth, direction-boundary count, and attained depth.

The active stage tells you which confirmation is being contested. The full vector tells you whether smaller clocks are coherent or fragmented while that contest remains unresolved.

Macro agreement breadth cannot identify a coherent frontier by itself. Two vectors can match macro at the same number of scales while having different boundary counts.

That difference needs room to appear. In Stage 1 the whole vector is fixed, and in Stage 2 only the small mode is free, so breadth and boundary count are deterministic functions of each other there and give identical AUCs. They can disagree only from Stage 3 on, when small and medium can each be in either mode.

## Timing discipline

The small seed persists through all three stages. Medium and large DCCs advance the active stage. Every stage panel ends one bar before its resolution. Attained depth is causal; terminal depth is an outcome label until the lineage ends.

Later small DCCs are expected inside Stage 2 or Stage 3. They change nested activity and may fragment the live vector without creating a new root.

The active stage's own lower and upper clocks cannot fire inside its panel, because either DCC is the resolution bar. Their counts are zero by construction; nested activity is measured on the clocks below the active lower clock.

## Lab

Run [4_threshold_dc_live_development.ipynb](../4_threshold_dc_live_development.ipynb).

Inspect timing audits, checkpoints, overlap (with survivor counts beside every AUC), Live Audit 2b on completed initiation features, trajectories, hierarchy-shape occupancy, and the terminal-depth casebook. In Live Audit 2b, an initiation-only out-of-sample AUC below 0.5 is worse than chance and inflates a plain gain, so credit the live path only when the plus-live AUC beats both 0.5 and the initiation model (`oos_auc_gain_over_floor` > 0), and compare with the live-only AUC. At elapsed 0 there is no live path yet.

## Mandatory exercises

1. Name the lower and upper clock in each stage.
2. Find an unresolved Stage-3 interval that becomes fragmented.
3. Compare agreement breadth with boundary count on that interval, and explain why a Stage-2 interval could not separate them.
4. Explain why later-checkpoint AUC is not an initiation forecast.
5. Decide whether live geometry adds information beyond completed seed and hand-off features, using Live Audit 2b.
6. Explain why none of the result is yet trading alpha.

## Completion gate G13 — Four-threshold causal live development

Before five thresholds, the learner must be able to:

1. Preserve the immutable seed through three stages.
2. Explain why hand-off DCCs change the active stage but not the root.
3. Verify that every stage excludes its resolution bar.
4. Identify the lower and upper TMV/T/R clock in each stage.
5. Distinguish causal attained depth from future terminal depth.
6. Explain nested DCCs on clocks below the active lower clock, why the active clocks' own counts are zero by construction, and unresolved fragmentation in later stages.
7. Explain what direction-boundary count adds beyond threshold progress.
8. Distinguish macro-agreement breadth from a coherent propagation frontier, and explain why the two coincide in Stages 1–2.
9. Explain later-checkpoint survival selection and why higher later AUC is not an initiation forecast.
10. State whether live geometry adds information beyond completed initiation features, without making an alpha claim.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- Stage-local features identify the active contest; hierarchy-wide features identify surrounding coherence or fragmentation.
- Agreement breadth and boundary count are not substitutes, but they can only differ from Stage 3 on. In Stages 1–2 they are deterministic functions of each other, so their AUCs coincide.
- Later checkpoints are survival-selected, and later AUC cannot be backdated to initiation.
- Deep attained depth remains distinct from unknown terminal depth.

</details>

## Locked in

> The active edge describes the current contest; the ordered mode vector describes the surrounding hierarchy. Neither replaces the other.

## Do not conclude

Deep attained propagation confirms scale reach to date. It does not reveal terminal depth or post-confirmation continuation.


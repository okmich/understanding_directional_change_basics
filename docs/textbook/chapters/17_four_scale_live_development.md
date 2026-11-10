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

Run [4_threshold_dc_live_development.ipynb](../../../4_threshold_dc_live_development.ipynb).

Inspect timing audits, checkpoints, overlap (with survivor counts beside every AUC), Live Audit 2b on completed initiation features, trajectories, hierarchy-shape occupancy, and the terminal-depth casebook.

## Mandatory exercises

1. Name the lower and upper clock in each stage.
2. Find an unresolved Stage-3 interval that becomes fragmented.
3. Compare agreement breadth with boundary count on that interval, and explain why a Stage-2 interval could not separate them.
4. Explain why later-checkpoint AUC is not an initiation forecast.
5. Decide whether live geometry adds information beyond completed seed and hand-off features, using Live Audit 2b.
6. Explain why none of the result is yet trading alpha.

## Locked in

> The active edge describes the current contest; the ordered mode vector describes the surrounding hierarchy. Neither replaces the other.

## Do not conclude

Deep attained propagation confirms scale reach to date. It does not reveal terminal depth or post-confirmation continuation.


# Chapter 21 — Five-scale causal live development

## Purpose

Measure the richest hierarchy while each of four possible stages remains unresolved.

## Active-stage features

Each live row must identify:

- immutable seed and active stage;
- lower target mode and upper origin mode;
- lower- and upper-scale live TMV/T/R;
- progress toward the active upper-scale DCC;
- lineage age (`lineage_age_bars`) and stage age (`elapsed_bars`);
- DCC counts and firing rates on clocks below the active lower clock (`sub_lower_dccs`, `sub_lower_dcc_rate`);
- completed prior-leg TMV/T/R confirmed by the seed and hand-off DCCs (`seed_leg_*`, `stage_start_leg_*`);
- attained depth;
- full mode vector, outer agreement breadth, and boundary count.

Target progress uses the active upper scale's running extreme and must remain below one on every pre-resolution row. If it reaches the confirmation boundary, that bar is the resolution and is excluded.

For the same reason the active lower and upper clocks never fire inside a stage panel: a lower DCC would be the rejection bar and an upper DCC the propagation bar. Their nested counts are zero by construction and carry no information. Nested activity is the activity on the clocks below the active lower clock, so Stage 1 has none.

Live TMV/T/R describe unfinished paths. Completed prior-leg TMV/T/R describe confirmed historical legs. They may appear together in a research table only with unambiguous names and timestamps. The panel carries both, as `lower_*_live` / `upper_*_live` and `seed_leg_*` / `stage_start_leg_*`, and Live Audit 2c asks whether the live path adds information beyond the completed legs on the same survivor cohort.

## Interpreting later checkpoints

As stage age increases, resolved paths leave the cohort. A rising later propagation share does not show that waiting causes propagation. Outcome-conditioned AUC can reveal when paths diverge, but remains diagnostic because the group label comes from the future.

## Lab

Run [5_threshold_dc_live_development.ipynb](../../../5_threshold_dc_live_development.ipynb).

Use fixed checkpoints, survivor trajectories, shape occupancy, and depth casebooks to identify which live features gain separation only after the path develops. Live Audit 2b checks whether the raw direction is consistent for up and down targets, and Live Audit 2c compares live geometry with the completed prior legs. AUCs are withheld when either outcome has fewer than 20 survivors.

## Mandatory exercises

1. Verify progress remains below one in the live panel.
2. Explain why lower mode is target and upper mode is origin.
3. Contrast sub-lower DCC count, firing rate, breadth, and boundary count on a Stage-3 or Stage-4 interval, and explain why breadth and boundary count cannot differ in Stages 1–2.
4. Explain why the active lower clock's own DCC count is zero by construction inside a stage panel.
5. Identify a feature whose separation appears only later, explain survival conditioning, and check whether its direction agrees for up and down targets.
6. Explain why depth four confirms reach but not continuation or profit.

## Locked in

> The live panel is a causal movie of unresolved geometry; future terminal depth may annotate that movie for diagnosis but never enter its frames.

## Do not conclude

Diagnostic separation is not a calibrated prediction and does not establish economic value after costs.


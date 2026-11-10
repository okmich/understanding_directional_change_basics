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

Run [5_threshold_dc_live_development.ipynb](../5_threshold_dc_live_development.ipynb).

Use fixed checkpoints, survivor trajectories, shape occupancy, and depth casebooks to identify which live features gain separation only after the path develops. Live Audit 2b checks whether the raw direction is consistent for up and down targets, and Live Audit 2c compares live geometry with the completed prior legs. An initiation-only out-of-sample AUC below 0.5 is worse than chance and inflates a plain gain, so credit the live path only when the plus-live AUC beats both 0.5 and the initiation model (`oos_auc_gain_over_floor` > 0), and compare with the live-only AUC. At elapsed 0 there is no live path yet. AUCs are withheld when either outcome has fewer than 20 survivors.

## Mandatory exercises

1. Verify progress remains below one in the live panel.
2. Explain why lower mode is target and upper mode is origin.
3. Contrast sub-lower DCC count, firing rate, breadth, and boundary count on a Stage-3 or Stage-4 interval, and explain why breadth and boundary count cannot differ in Stages 1–2.
4. Explain why the active lower clock's own DCC count is zero by construction inside a stage panel.
5. Identify a feature whose separation appears only later, explain survival conditioning, and check whether its direction agrees for up and down targets.
6. Explain why depth four confirms reach but not continuation or profit.

## Completion gate G17 — Five-threshold causal live development

Before robustness, the learner must be able to:

1. Preserve the seed through every confirmed hand-off.
2. Verify that panel rows stop before stage resolution and progress stays below one.
3. Use the active upper-scale running extreme for target progress.
4. Keep lower mode as target and upper mode as origin during a contest.
5. Distinguish live TMV/T/R from completed prior-leg TMV/T/R, and test whether the live path adds information beyond the completed legs.
6. Interpret sub-lower-scale DCC counts, firing rates, agreement breadth, and direction-boundary count as distinct causal path features (breadth and boundary count only from Stage 3 on), and explain why the active lower and upper clocks' counts are zero by construction.
7. Explain survivor selection and why waiting does not cause propagation.
8. Identify features that separate outcomes only after the path develops.
9. Check directional consistency of those relationships.
10. Explain why outer propagation neither forecasts continuation nor establishes profitability.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- Pre-resolution target progress remains below one by construction.
- The lower mode is target and the upper mode is origin during each adjacent contest.
- Sub-lower DCC counts and firing rates, breadth, and boundary count describe different aspects of the path. The active lower and upper clocks' own counts are zero by construction and carry no information.
- Outcome separation appearing later must be interpreted with survivor selection and direction checks (Live Audit 2b splits by target mode).
- Live TMV/T/R describe the unfinished path; `seed_leg_*` and `stage_start_leg_*` are completed legs known at the seed and hand-off times. Live Audit 2c tests what the live path adds beyond them.

</details>

## Locked in

> The live panel is a causal movie of unresolved geometry; future terminal depth may annotate that movie for diagnosis but never enter its frames.

## Do not conclude

Diagnostic separation is not a calibrated prediction and does not establish economic value after costs.


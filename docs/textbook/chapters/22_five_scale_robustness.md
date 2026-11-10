# Chapter 22 — Five-scale robustness

## Purpose

Test whether the full hierarchy survives changes in market, absolute scale, period, direction, and grid geometry.

## Frozen comparison matrix

[5_threshold_dc_robustness.ipynb](../../../5_threshold_dc_robustness.ipynb) predeclares six cases:

- GBPUSD constant-ratio ladders starting at 15, 20, and 25 basis points;
- EURUSD and USDJPY constant-ratio ladders starting at 20 basis points;
- GBPUSD linear 20/40/60/80/100 basis points as grid sensitivity.

The constant-ratio 20-basis-point ladder is primary. It does not lose that role if another case later displays a more attractive propagation rate.

## Adequacy before percentages

Report outer-event counts and stage counts before interpreting rates. The notebook's lineage-accounting table assigns every eligible root to exactly one category, and the categories must sum to the root count:

- strict-clean;
- resolved with a same-bar stage;
- ambiguous;
- unresolved (right-censored);
- unlinked.

All 32 configurations need not appear equally. Exact terminal-depth probabilities are expected to be case-specific.

The depth ladder is shown for two cohorts. A same-bar stage can only be a propagation, so dropping lineages that contain one removes only propagations. The strict-clean ladder therefore sits below the all-resolved ladder at every depth. Use the all-resolved ladder to describe linked depth. Use strict-clean only where a non-empty live interval is required: checkpoints and live AUCs.

The robust claims concern recurrence of:

- broad agreement;
- fragmentation;
- state entropy;
- a linked depth ladder;
- survival conditioning;
- any directional consistency in live progress.

A relationship confined to one target direction or calendar third is weak evidence. Calendar thirds split every case on the same dates. Direction and calendar ranges use only strata with an adequate number of attempts.

Live activity on the lower scale of a stage is zero by construction, because the first lower DCC resolves the stage. The informative firing-density feature is small-clock activity inside Stages 2–4 (`nested_small_dccs`). Constant features are labelled as such rather than as small samples.

Changing absolute scale with fixed ratios differs from changing grid geometry with a similar outer scale. The former shifts all clocks; the latter changes the relative spacing among clocks.

## Mandatory exercises

1. Explain why all cases use common calendar coverage.
2. Identify the comparison axis changed by each case.
3. Check sample adequacy and the lineage accounting before comparing terminal-depth percentages, and explain why the strict-clean ladder is lower than the all-resolved ladder.
4. State which qualitative structures recur and which numbers do not.
5. Identify direction or period concentration.
6. Explain why the grid is part of model specification.
7. State why these audits still do not establish profitability.

## Locked in

> A robust hierarchy preserves causal meanings and recurring structural relationships across fixed comparisons; it does not preserve exact occupancy or depth probabilities.

## Do not conclude

Do not optimize the grid from these results. Any later model choice must be training-only and evaluated walk-forward.


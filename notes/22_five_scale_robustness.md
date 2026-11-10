# Chapter 22 — Five-scale robustness

## Purpose

Test whether the full hierarchy survives changes in market, absolute scale, period, direction, and grid geometry.

## Frozen comparison matrix

[5_threshold_dc_robustness.ipynb](../5_threshold_dc_robustness.ipynb) predeclares six cases:

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

The depth ladder is shown for two cohorts. A same-bar stage can only be a propagation, so every lineage dropped for containing one reached at least medium, and the strict-clean P(reach medium) sits below the all-resolved one by construction. Later rates usually sit below too, but not always: the filter drops whole lineages, and some of them were rejected at a later stage (the macro-to-outer rate comes out higher under strict-clean in some cases). Use the all-resolved ladder to describe linked depth. Use strict-clean only where a non-empty live interval is required: checkpoints and live AUCs.

The robust claims concern recurrence of:

- broad agreement;
- fragmentation;
- state entropy;
- a linked depth ladder, with one caveat: in every case the number of depth-4 lineages equals the number of outer events, so cumulative outer reach is N_outer / N_roots, arithmetic like the adjacent-rate identity in Chapter 18;
- survival conditioning;
- directional consistency in live progress, which this notebook does not test across cases (only the GBPUSD 20 bp primary case splits progress AUC by direction, in `5_threshold_dc_live_development` Live Audit 2b).

A relationship confined to one target direction or calendar third is weak evidence. Calendar thirds split every case on the same dates. Direction and calendar ranges use only strata with an adequate number of attempts.

Live activity on the lower scale of a stage is zero by construction, because the first lower DCC resolves the stage. The informative firing-density feature is small-clock activity inside Stages 2–4 (`nested_small_dccs`). Constant features are labelled as such rather than as small samples.

Changing absolute scale with fixed ratios differs from changing grid geometry with a similar outer scale. The former shifts all clocks; the latter changes the relative spacing among clocks.

## Mandatory exercises

1. Explain why all cases use common calendar coverage.
2. Identify the comparison axis changed by each case.
3. Check sample adequacy and the lineage accounting before comparing terminal-depth percentages, and explain which part of the strict-clean ladder is lower by construction and which is only usually lower.
4. State which qualitative structures recur and which numbers do not.
5. Identify direction or period concentration.
6. Explain why the grid is part of model specification.
7. State why these audits still do not establish profitability.

## Completion gate G18 — Five-threshold robustness

Before arbitrary-N representation, the learner must be able to:

1. Use common calendar intervals and predeclare all cases.
2. Identify which comparison changes symbol, scale, or grid geometry.
3. Keep the constant-ratio primary ladder fixed even if another case has a higher ex-post propagation rate.
4. Report outer-event counts and the lineage accounting (eligible roots, strict-clean, resolved with a same-bar stage, ambiguous, unresolved, unlinked) before percentages.
5. Explain unequal occupancy across the 32 configurations.
6. Test recurrence of agreement, fragmentation, entropy, and the depth ladder, using all resolved lineages for the ladder and explaining why the strict-clean first-stage rate is biased downward and why later rates can go either way.
7. Treat exact depth probabilities as case-specific.
8. Audit survivor selection, direction concentration, and sample-period concentration.
9. Explain what changes under fixed ratios versus a linear grid.
10. Treat the grid as part of model specification, not neutral preprocessing.
11. Separate structural robustness from profitability and require training-only, walk-forward model selection.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- Compare cases only after checking outer-event and lineage sample adequacy. The lineage accounting must reconcile: strict-clean + resolved-with-same-bar + ambiguous + unresolved + unlinked = eligible roots.
- Only propagations can be same-bar, so every lineage strict-clean drops reached medium: its first-stage rate is biased down, its later rates are not guaranteed to be. Describe depth with the all-resolved ladder.
- Cross-symbol, absolute-scale, and grid-geometry comparisons change different axes.
- The primary ladder remains primary regardless of attractive ex-post rates.
- Robust conclusions are qualitative structural recurrences; exact occupancies and depths are case-specific.

</details>

## Locked in

> A robust hierarchy preserves causal meanings and recurring structural relationships across fixed comparisons; it does not preserve exact occupancy or depth probabilities.

## Do not conclude

Do not optimize the grid from these results. Any later model choice must be training-only and evaluated walk-forward.


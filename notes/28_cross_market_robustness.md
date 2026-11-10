# Chapter 28 — Cross-market robustness

> **Interpretation checkpoint:** The notebook has been executed, but this chapter remains provisional until G24 is answered across all declared cases.

## Purpose

Test whether the representation, direct taxonomy, and frozen modeling procedure retain coherent meaning across markets and sampling choices.

## Structural matrix

[24_cross_market_robustness.ipynb](../24_cross_market_robustness.ipynb) retains all 45 predeclared structural cases, including inadequate cases. Threshold ladders and frequencies are fixed across symbols rather than optimized market by market, and comparisons use common calendar coverage.

Report early/middle/late occupancy ranges so period instability is visible. The three periods are equal calendar thirds of the common interval, so every market and sampling frequency is split at the same dates; splitting by row position would put the boundaries on different dates for markets with different trading hours. A result that requires deleting weak cases or inventing a new story for every symbol is non-transfer.

The native bars are stamped at their open (the MetaTrader convention of the source files). Fifteen- and thirty-minute bars keep that convention: each is labelled by its interval open and carries the last native close inside the interval.

## Frozen model procedure

Select the HMM family and state count on GBP validation only after the prefix, occupancy, and restart-stability gates. External markets may refit parameters under the same frozen procedure, but they may not reselect family, state count, features, mapping rules, or adequacy standards. In particular, the emission features screened on GBP training rows are passed unchanged to every market; a frozen feature that turns out to be zero-inflated elsewhere is listed, not silently dropped. Apply and report the same eligibility gates externally; an ineligible market stays in the table.

For every primary market, report:

- filtering causality and prefix invariance;
- occupancy, restart stability, variance-floor exposure, and eligibility;
- confidence, persistence, and switching;
- relationships to direction-neutral and direction-aware direct baselines;
- omega-squared and permutation evidence for diagnostic usefulness;
- a block-bootstrap interval for the model's margin over the stronger direct baseline, with its computed verdict (a market whose interval contains zero adds no information beyond the baseline, even when its model looks well behaved);
- actual price-path casebooks.

Previously inspected markets cannot be represented as untouched confirmation. They are robustness evidence within an explored research program.

## Mandatory exercises

1. Account for all 45 cases, including inadequate ones.
2. Explain why common calendar coverage and fixed ladders matter.
3. Verify that only GBP validation selected the model specification.
4. Verify identical eligibility rules on every external market and retain failures.
5. Compare structural recurrence with model-state recurrence using both direct baselines.
6. Identify any symbol-specific rule or interpretation.
7. Review casebooks for economic intelligibility, keeping raw state IDs visible.
8. State what evidence would require a genuinely untouched future sample.

## Completion gate G24 — Cross-market robustness

Before making a transferable regime claim, the learner must be able to:

1. Retain every declared case, including inadequate cases.
2. Fix threshold ladders and frequencies across symbols rather than optimizing per market.
3. Use common calendar coverage and report instability across three calendar thirds shared by every market and sampling frequency.
4. Select model family and state count on the declared validation market only after prefix, occupancy, and restart gates.
5. Refit the frozen procedure externally without reselection.
6. Apply and report the same eligibility rules externally without dropping failures.
7. Compare permutation-audited diagnostic separation with structural and direction-aware baselines, and report a market whose block-bootstrap margin over the stronger baseline contains zero as adding no information beyond the baseline.
8. Keep raw-state price-path casebooks economically intelligible and mark ineligible cases.
9. Recognize symbol-specific rules or stories as non-transfer.
10. Avoid calling previously inspected markets untouched external confirmation.

**Current status:** Notebook source revised after the 2026-11-10 review; rerun pending; learner interpretation pending.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

There is no acceptable answer that drops inconvenient cases. A passing response must:

- account for all 45 declared structural cases;
- preserve common dates, fixed ladders, and frozen adequacy rules;
- select model specification only on GBP validation;
- refit but not reselect externally;
- apply identical eligibility rules externally and retain failures;
- compare permutation-audited separation with both direct baselines, and state "no information beyond baseline" for every market whose bootstrap verdict says so;
- report instability across shared calendar thirds, and inadequate cases;
- reject symbol-specific reinterpretation as non-transfer;
- avoid calling explored markets untouched confirmation.

</details>

## Locked in

> Transfer means one frozen causal procedure retains interpretable structure across markets without market-specific reselection or storytelling.

## Do not conclude

Cross-market state stability is not a trading strategy. Economic value remains a separate, cost-aware, conditionally evaluated research question.


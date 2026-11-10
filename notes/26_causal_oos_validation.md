# Chapter 26 — Causal and out-of-sample validation

> **Interpretation checkpoint:** The notebook has been executed, but this chapter remains provisional until you write and pass G22.

## Purpose

Select a state model without allowing the test partition, future observations, or semantic relabeling to influence the choice.

## Three-way chronology

Use chronological train, validation, and test partitions:

- train fits scaling, parameters, and semantic mapping;
- validation selects the eligible family/state count under predeclared rules;
- test is opened once for the frozen choice.

Because this repository's history has already been explored, “test” here is exploratory OOS evidence, not untouched external confirmation.

## Causal audits

The selected model must pass:

- **filtered-prefix invariance:** filtering a prefix alone gives the same probabilities as the corresponding prefix of a longer run;
- **occupancy floor:** no validation state silently collapses below the predeclared minimum;
- **restart stability:** every candidate clears a predeclared minimum adjusted-Rand agreement across independent seeds before likelihood ranking;
- **immutable mapping:** validation and test do not rename states;
- **joint persistence review:** dwell time, confidence, and switching are interpreted together.

Adjusted Rand agreement measures whether restarts partition observations similarly. It does not verify economic semantics.

## Incremental usefulness

Compare diagnostic future separation with both the direction-neutral structural baseline and the direction-aware direct baseline. Use bias-corrected omega-squared and a label-permutation null rather than raw in-sample eta-squared. The model must add more than a probabilistic renaming of observable geometry. Future activity or volatility can be used as diagnostic outcomes, not causal inputs. Directional alpha is outside this phase.

Two cautions keep this honest. Raw eta-squared grows with the number of groups even when nothing is there, so a five-state model beats a three- or four-class baseline by construction; omega-squared corrects for that. And forward windows on neighbouring events overlap, so rows are serially dependent: an independent-row permutation null is optimistic. The notebook therefore also puts a moving-block bootstrap interval on the model's margin over the stronger direct baseline and computes a verdict from it. `no_information_beyond_baseline` means the interval contains zero.

## Where the likelihood comes from

Validation likelihood ranks eligible candidates, so its source must be visible. With diagonal covariances each candidate's log density splits exactly by feature. If most of the gain comes from features whose states sit at the variance floor, the ranking measures how well a model isolates repeated values, not how well it describes the data.

## Lab

Run [22_causal_oos_validation.ipynb](../22_causal_oos_validation.ipynb) and reconstruct the selection decision from validation evidence only.

## Mandatory exercises

1. Hide the test table and select the model from validation evidence.
2. Explain and verify prefix invariance.
3. Reconstruct eligibility: prefix causality, occupancy, complete restarts, and the minimum restart-ARI threshold.
4. Compare test persistence with confidence and switching.
5. Verify that raw state partitions, not semantic names, drive ARI and NMI.
6. Compare omega-squared and permutation evidence against both direct comparators, then read the block-bootstrap interval and verdict for the model's margin over the stronger one.
7. Explain why the result is exploratory OOS.
8. Use the per-feature likelihood table to check that the selected model's advantage does not come from floored features.

## Completion gate G22 — Causal and out-of-sample validation

Before economic interpretation, the learner must be able to:

1. Select on validation likelihood and eligibility rules without consulting test results.
2. Preserve train-only scaling and semantic mapping.
3. Pass filtered-prefix invariance.
4. Enforce a predeclared validation occupancy floor.
5. Require every candidate to clear a predeclared restart-stability threshold before likelihood ranking.
6. Keep unsupported semantic states unmatched and compute partition metrics on raw state IDs.
7. Evaluate test persistence jointly with confidence and switching.
8. Compare bias-corrected, permutation-audited diagnostic separation against direction-neutral and direction-aware baselines, and read the model's margin over the stronger baseline from a block-bootstrap interval and its computed verdict.
9. Avoid directional-alpha or trading claims.
10. Label previously explored history as exploratory OOS evidence rather than untouched confirmation.
11. Inspect per-feature likelihood contributions and variance-floor hits before trusting likelihood differences between candidates.

**Current status:** Notebook source revised after the 2026-11-10 review; rerun pending; learner interpretation pending.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

The final response must reconstruct the notebook's validation-only selection. It should verify:

- test results did not choose the family or state count;
- prefix invariance, occupancy floor, and immutable mapping pass;
- every eligible candidate clears the predeclared restart-ARI threshold;
- persistence is interpreted with confidence and switching;
- raw states drive partition metrics;
- bias-corrected, permutation-audited separation is compared with direction-neutral and direction-aware baselines;
- the block-bootstrap verdict, not a hand-picked positive difference, decides whether the model adds information beyond the stronger baseline;
- the test remains exploratory because the history was previously inspected.

</details>

## Locked in

> Train creates the model, validation chooses it, and test describes the frozen choice; none may reach backward in time.

## Do not conclude

Diagnostic future separation is not directional alpha, and a previously explored test period is not final external validation.


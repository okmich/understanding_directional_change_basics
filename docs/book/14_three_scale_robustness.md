# Chapter 14 — Three-scale robustness

## Purpose

Close the three-threshold phase by testing whether linkage and live-development interpretations recur under controlled changes.

## Predeclared comparisons

[3_threshold_dc_robustness.ipynb](../../3_threshold_dc_robustness.ipynb) asks two different questions:

1. **Cross-symbol:** keep 20/40/60 basis points fixed and change GBPUSD, EURUSD, and USDJPY.
2. **Absolute scale:** keep GBPUSD and the 1:2:3 ladder shape while changing 15/30/45, 20/40/60, and 25/50/75 basis points.

All symbols use a common date interval. Cases are declared before results. A failed or inadequate case remains visible; it is not a reason to retune the ladder.

## Structural versus numerical claims

Event counts, durations, terminal-depth probabilities, and occupancy should vary. The structural questions are whether:

- exact lineage semantics survive;
- attained and terminal depth retain their meanings;
- live progress adds separation after initiation when the comparison is made on the same survivor cohort;
- the raw direction of any association recurs;
- results are not confined to one direction, period, symbol, or ladder;
- direct geometry remains the baseline a future classifier must beat.

Later-checkpoint AUC is diagnostic and survival-conditioned even though every feature on its row is causal.

Comparing the AUC of 20-bar survivors with the AUC of the full initiation cohort mixes two effects: information that develops along the path, and the change in which attempts are still in the sample. Audit 6 separates them. `auc_change_same_cohort` compares the 20-bar survivors with the same lineages at initiation; `survivor_selection_effect` is the initiation AUC of those survivors minus that of the full cohort. It also asks whether live geometry adds out-of-sample information beyond the completed seed and hand-off legs, with each attempt scored by a model fitted only on earlier attempts. An AUC is withheld when either outcome has fewer than 20 survivors.

## Mandatory exercises

1. Explain why common calendar coverage matters.
2. Classify each reported conclusion as mechanical, structural, or case-specific.
3. Compare event counts and durations across absolute scales.
4. Identify any dependence on direction or sample period.
5. Explain whether live development adds more than completed initiation geometry, using Audit 6's same-cohort AUC change and out-of-sample gain.
6. State why structural robustness is not profitability.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- Common dates prevent period composition from masquerading as symbol effects.
- Predeclared cases prevent result-driven threshold selection.
- Exact probabilities are case-specific; identity and timing semantics are structural.
- Live-progress evidence must be checked across direction, period, symbol, and ladder and compared with initiation geometry.
- Compare 20-bar survivors with the same lineages at initiation. Comparing them with the full initiation cohort mixes information gain with survivor selection; Audit 6 reports the two separately.

</details>

## Locked in

> Robust multiscale intuition preserves meanings and qualitative relationships while allowing frequencies, durations, and probabilities to change.

## Do not conclude

These are predeclared structural comparisons, not model selection and not a walk-forward trading test.


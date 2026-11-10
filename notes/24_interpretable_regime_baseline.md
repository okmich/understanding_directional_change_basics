# Chapter 24 — The interpretable regime baseline

> **Interpretation checkpoint:** The notebook has been executed, but this chapter remains provisional until you write and pass G20 in your own words.

## Purpose

Create a direct, causal structural taxonomy before asking a probabilistic model to discover states.

## Frozen four-class taxonomy

The baseline separates structural shape from direction:

- `broad_coherence`: no direction boundary;
- `shallow_counter`: one coherent boundary with counter depth no more than half the ladder;
- `deep_counter`: one coherent boundary with counter depth greater than half the ladder;
- `fragmented`: more than one direction boundary.

Direction is recorded separately through the small and outer modes. A broad up hierarchy and broad down hierarchy share a structural shape but not a direction.

The class uses current causal geometry only. “Deep” means a larger fraction of scales currently confirms the counter direction. It does not mean future propagation to the outer scale.

## Why this is a baseline

The taxonomy is deterministic, transparent, and reproducible. It is not ground truth. It compresses the ordered hierarchy according to choices we declared. A probabilistic model is useful only if it adds something beyond renaming these classes: uncertainty, persistence, compression, or stable diagnostic separation.

Broad coherence is not automatically a profitable trend. Fragmentation is not automatically bad. Those are economic hypotheses requiring separate evidence.

## Keep the comparator out of the emission density

The ordered mode vector, boundary count, fragmentation, direction, and event counts are discrete structural geometry. Keep them in the direct baseline and diagnostic tables. Do not feed them to a diagonal Gaussian or Student-t density as though they were continuous measurements: a component can gain artificial likelihood by pinning a category at its minimum variance.

The probabilistic comparison therefore uses causal continuous measurements such as mode age, reversal progress, live TMV, and live R. Features with no training variation are removed. So are zero-inflated features in which one repeated value covers at least 20% of training rows: at a union event the scale that just fired has mode age 0 and reversal progress 0, and a continuous density would isolate that point mass at its variance floor exactly as it would a category. Preprocessing must report every removed feature with its reason, report rows dropped by structural class, and fail if it silently erases a class such as `fragmented`.

`counter_depth_fraction` is undefined for fragmented rows, because two or more boundaries have no single depth. That is why it stays a direct-baseline descriptor and is never an emission input: a missing value in a model input would delete exactly the fragmented rows.

## Lab

Run [20_interpretable_regime_baseline.ipynb](../20_interpretable_regime_baseline.ipynb).

Compare bar-time and union-event occupancy, causal feature distributions, persistence, transitions, and the structural/dynamic/full continuous-emission tiers. Verify the class-retention audit before fitting a model.

## Mandatory exercises

1. Explain why shape and direction are separate axes.
2. Classify hand-worked vectors without using future outcomes.
3. Explain why fragmented vectors have no single depth.
4. Compare bar-time and event-time occupancy.
5. Explain why discrete hierarchy geometry is a comparator rather than a continuous emission input.
6. Verify that preprocessing retains fragmented observations and reports every dropped class count.
7. State exactly what a later model must add beyond this baseline.

## Completion gate G20 — Interpretable regime baseline

Before probabilistic modeling, the learner must be able to:

1. Separate structural shape from direction.
2. Explain why broad coherence is not automatically a profitable trend.
3. Define shallow and deep counter-moves by scale fraction rather than future propagation.
4. Explain why fragmented structure has no valid single propagation depth and verify that preprocessing retains it.
5. Explain bar-time versus event-time occupancy.
6. Treat the direct taxonomy as a comparator rather than ground truth.
7. Keep discrete hierarchy geometry out of continuous emission densities.
8. Report every removed emission feature with its reason (training-constant, nearly discrete, or a zero-inflated point mass covering at least 20% of training rows) and dropped rows by structural class.
9. State what a later model must add: calibrated confidence, persistence, compression, or useful separation.

**Current status:** Notebook executed with the current code on 2026-11-10; learner interpretation pending.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

The final response must use the notebook output. Its logic should establish:

- structural class and direction are separate;
- shallow/deep are current scale fractions, not future outcomes;
- fragmented states have no single depth;
- preprocessing must retain fragmented observations or report and reject total class loss;
- bar and event clocks yield different occupancy;
- the taxonomy is a transparent comparator, not truth;
- discrete hierarchy geometry is not a valid continuous-density input, and neither is a zero-inflated point mass such as mode age 0 on the scale that just fired.

Do not mark G20 passed until you state what later models must add beyond the direct taxonomy.

</details>

## Locked in

> The direct taxonomy is an interpretable causal comparator, not a true hidden regime label.

## Do not conclude

Do not equate broad coherence with trend profit or use the taxonomy as supervised truth for model accuracy.


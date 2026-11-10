# Chapter 25 — Clustering, mixtures, and filtered HMMs

> **Interpretation checkpoint:** The notebook has been executed, but this chapter remains provisional until you write and pass G21.

## Purpose

Compare probabilistic and non-probabilistic state models under one frozen feature, clock, split, and semantic-mapping contract.

## Model differences

[21_probabilistic_regime_models.ipynb](../../../21_probabilistic_regime_models.ipynb) compares four-state candidates:

- **K-means:** contemporaneous hard clusters;
- **Gaussian mixture:** contemporaneous soft membership;
- **Normal HMM:** Gaussian emissions plus filtered Markov history;
- **Student-t HMM:** heavier-tailed emissions plus filtered Markov history.

K-means and the mixture classify the current feature vector. Only the HMM carries a state transition process and filtered history.

Every candidate receives the same train-scaled continuous feature matrix. The notebook reports every feature removed on training rows, with its reason: zero training variation, too few distinct values, or a zero-inflated point mass (one repeated value covering at least 20% of rows, such as mode age 0 on the scale that just fired). For density models it also reports how many fitted diagonal variances sit on the declared floor and splits each candidate's validation log density by feature. High posterior confidence accompanied by many floor hits, or a likelihood gain concentrated in floored features, is a numerical warning, not strong economic evidence.

## Semantic mapping

Raw state numbers are arbitrary. Map supported states to supported direct classes using the training partition only and a one-to-one assignment. A state mapped to `fragmented` means it overlapped that direct class most strongly in training. A surplus or unsupported state remains `unmatched`; do not reuse a convenient class name. In every case the raw state remains the fitted object, not the taxonomy itself.

Scaling is also fitted on training rows only. Validation and test may be transformed and filtered, never used to revise names.

## Observation clock

Union-event time is the primary experiment. A bar-time sensitivity models a different population: every bar transition rather than transitions among event-bearing observations. Persistence cannot be compared without naming the clock. The frozen full-history bar-time fit exceeded a 60-minute cell limit in the reference environment, so it remains an explicit opt-in robustness exercise. That operational failure is not evidence for or against its economic usefulness.

## Evaluation questions

Inspect likelihood, occupancy, confidence, persistence, switching, baseline overlap, restart stability, and actual price paths. High confidence or persistence is not sufficient: a collapsed or sticky state model can be confidently unhelpful.

The notebook refits every family with independent seeds and reports the validation adjusted-Rand agreement with the primary fit. Here that is descriptive; Chapter 26 turns a predeclared minimum into an eligibility rule.

## Mandatory exercises

1. Explain the temporal difference between mixture membership and an HMM posterior.
2. Explain why smoothing is excluded from deployable state paths.
3. Audit that semantic mapping is training-only, one-to-one, and permits `unmatched` states.
4. Explain why discrete geometry is compared after fitting rather than treated as a continuous observation.
5. Interpret posterior confidence together with variance-floor diagnostics.
6. Compare event-time and bar-time transition meanings and computational burden.
7. State why agreement with the direct taxonomy is descriptive rather than accuracy.
8. Read the restart-stability table and say which families produce a partition stable enough to name.
9. Use the per-feature likelihood table to explain where a density model's advantage comes from.

## Locked in

> A probabilistic state model must be judged as its own causal object; training-only names merely help us talk about it.

## Do not conclude

Do not select a model because its labels look familiar, balanced, persistent, or confident. Selection belongs to the next phase.


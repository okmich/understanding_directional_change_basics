# Understanding Directional Change from First Principles

## Textbook source-of-truth manifest

**Subtitle:** An intuition-first, causality-safe journey from one threshold to multiscale market regimes  
**Manifest status:** Active  
**Textbook status:** Concise first draft of Chapters 0–30 and the solution guide complete; technical and pedagogical review pending  
**Primary learner:** The repository author, followed by technically serious public readers  
**Last structural review:** 2026-11-10

---

## 1. Authority and scope

This manifest is the source of truth for the textbook's:

- teaching sequence;
- chapter and lab mapping;
- prerequisite graph;
- mandatory interpretation exercises;
- progression criteria;
- content status;
- terminology and evidence standards.

It does **not** replace the executable sources:

1. `dc_basics/` and its tests define implementation semantics and invariants.
2. The notebooks define the executable experiments, figures, tables, and empirical results.
3. This manifest defines how those sources become a coherent textbook and when a learner is ready to advance.

If two sources conflict, resolve the conflict explicitly. Do not silently rewrite the textbook around it. The implementation and notebook must first be reconciled, then this manifest and the affected chapter must be updated.

---

## 2. Intellectual provenance and acknowledgements

Directional Change is not an invention of this repository or textbook. This work stands on a research tradition developed over several decades.

The foundational credit belongs to Dominique M. Guillaume, Michel M. Dacorogna, Rakhal R. Davé, Ulrich A. Müller, Richard B. Olsen, and Olivier V. Pictet. Their 1997 study introduced Directional Change to the financial-market literature as part of an event-based view of high-frequency foreign-exchange data and intrinsic time.

Special credit belongs to **Jun Chen and Edward P. K. Tsang**, authors of *Detecting Regime Change in Computational Finance: Data Science, Machine Learning and Algorithmic Trading*. Their book is the principal intellectual catalyst for this textbook's study of Directional Change indicators, Hidden Markov Models, regime characterization, causal market monitoring, and the distinction between retrospective regime discovery and live regime tracking.

Richard B. Olsen deserves additional acknowledgement as a foundational co-author, long-standing advocate of intrinsic-time market analysis, and author of the foreword to Chen and Tsang's book. The broader Directional Change research program—including work by James B. Glattfelder, Alexandre Dupuis, Edward P. K. Tsang, Jun Chen, Monira Aloud, and their collaborators—developed the scaling-law, indicator, market-profiling, regime-analysis, and application literature from which this project learns.

The contribution of this textbook is narrower and pedagogical:

- reconstruct the ideas from rudimentary mechanics upward;
- make information timing and causal provenance explicit at every step;
- connect single-threshold intuition to exact multiscale event-ID lineages;
- turn executable notebook completion gates into mandatory interpretation exercises;
- provide a reproducible learning path that distinguishes observable structure from hindsight outcomes and trading claims.

It must never imply that this repository originated Directional Change, overshoot analysis, TMV/T/R indicators, intrinsic-time analysis, or Directional Change regime modeling.

### Required attribution policy

Every public manuscript produced from this repository must:

1. include an acknowledgements or intellectual-provenance section in its front matter;
2. cite the foundational 1997 paper when Directional Change is first introduced;
3. cite Chen and Tsang's book when introducing the regime-change research program, TMV/T/R-based regime characterization, or the motivating HMM workflow;
4. cite the relevant primary paper when presenting a published indicator, scaling law, formalism, or empirical claim;
5. label reproduced or adapted definitions, equations, tables, and figures accurately;
6. distinguish reproduction, pedagogical re-expression, implementation choice, empirical extension, and genuinely new contribution;
7. preserve attribution in notebook narratives, textbook chapters, generated documentation, and derivative repositories;
8. avoid implying conceptual originality merely because the implementation was independently written.

### Core bibliography

The bibliography will grow during chapter construction. These references are mandatory anchors:

1. Guillaume, D. M., Dacorogna, M. M., Davé, R. R., Müller, U. A., Olsen, R. B., and Pictet, O. V. (1997). “From the Bird's Eye to the Microscope: A Survey of New Stylized Facts of the Intra-Daily Foreign Exchange Markets.” *Finance and Stochastics*, 1(2), 95–129. <https://doi.org/10.1007/s007800050018>.
2. Glattfelder, J. B., Dupuis, A., and Olsen, R. B. (2011). “Patterns in High-Frequency FX Data: Discovery of 12 Empirical Scaling Laws.” *Quantitative Finance*, 11(4), 599–614. <https://doi.org/10.1080/14697688.2010.481632>.
3. Tsang, E. P. K., and Chen, J. (2018). “Regime Change Detection Using Directional Change Indicators in the Foreign Exchange Market to Chart Brexit.” *IEEE Transactions on Emerging Topics in Computational Intelligence*, 2(3), 185–193. <https://doi.org/10.1109/TETCI.2017.2775235>.
4. Chen, J., and Tsang, E. P. K. (2018). “Classification of Normal and Abnormal Regimes in Financial Markets.” *Algorithms*, 11(12), 202. <https://doi.org/10.3390/a11120202>.
5. Chen, J., and Tsang, E. P. K. (2021). *Detecting Regime Change in Computational Finance: Data Science, Machine Learning and Algorithmic Trading*. CRC Press, first edition. ISBN 978-0-367-53628-2.
6. Tsang, E. P. K. (2022). “Directional Change for Handling Tick-to-Tick Data.” *Journal of Chinese Economic and Business Studies*, 20(2), 171–182. <https://doi.org/10.1080/14765284.2021.1989883>.

The final bibliography must be checked against the primary publications before release. Secondary summaries may help discover sources but must not be the authority for technical or historical claims.

---

## 3. Book mission

The book develops directional-change intuition from first principles. Its destination is the ability to look at a causal multiscale state and explain, without hindsight:

> Small-scale activity is intense, propagation has reached the medium scales but not the large scales, and the broader structure remains intact.

The book is successful when the learner can:

- reconstruct directional-change confirmations by hand;
- distinguish the completed prior leg from the newly confirmed live mode;
- state exactly when every value becomes knowable;
- read independent DC clocks on one price path;
- follow an immutable small-scale seed through exact event-ID hand-offs;
- distinguish current state, attained depth, terminal outcome, and future label;
- interpret survival-conditioned live development correctly;
- represent an arbitrary threshold hierarchy causally;
- judge whether a probabilistic model adds information beyond directly observed geometry;
- separate structural description from a trading or profitability claim.

### Non-goals

The book does not:

- begin with a trading strategy;
- treat a DC state as an entry or exit signal by default;
- call diagnostic hindsight labels deployable targets;
- optimize thresholds against future profitability during intuition building;
- treat an HMM state name as objective market truth;
- accept aggregate fit, persistence, confidence, or Sharpe as sufficient evidence;
- hide ambiguous, unresolved, same-bar, unlinked, or inadequately sampled cases.

---

## 4. Governing learning contract

Every chapter follows the same order:

1. **Street-level intuition** — explain the market action in ordinary language.
2. **Formal definition** — introduce the exact event, variable, or state.
3. **Information timing** — identify what is known, at which timestamp, and under which event ID.
4. **Notebook lab** — produce the evidence on an actual price path.
5. **Visual interpretation** — inspect the relevant bars and events rather than relying only on summary tables.
6. **Causal versus hindsight audit** — separate live measurements from later outcomes.
7. **Transfer exercise** — reproduce the reasoning on another symbol, period, frequency, or threshold ladder.
8. **Locked-in statement** — write the compact intuition that must remain true after details are forgotten.

Running a notebook is necessary but not sufficient. A phase is complete only after its completion gate is answered in the learner's own words and supported by notebook evidence.

### Mandatory evidence for every completion gate

Each gate response must contain, where applicable:

- a plain-language explanation;
- the formal event or state definition;
- the information timestamp and relevant event ID;
- at least one referenced chart or casebook path;
- at least one referenced table, count, or distribution;
- an explicit causal-versus-hindsight statement;
- one misconception the evidence rules out;
- one transfer check or reason transfer remains unproven;
- a final locked-in statement.

### Pass standard

A completion gate passes only when the learner can answer it without copying notebook prose and can apply the answer to a previously unseen chart segment. Numerical recall is not required unless the number is part of a definition. Mechanical, timing, and causal distinctions are required.

---

## 5. Status vocabulary

| Status | Meaning |
|---|---|
| `READY_TO_WRITE` | Executable evidence and gate exist; chapter prose can be authored. |
| `LAB_RUN_INTERPRETATION_PENDING` | Notebook executed, but its gate has not yet been interpreted and passed. |
| `DRAFTING` | Chapter prose or exercises are actively being written. |
| `DRAFTED` | Chapter exists but has not passed technical and pedagogical review. |
| `REVIEWED` | Chapter matches code, notebook evidence, causality rules, and prerequisites. |
| `ENGINEERING_COMPLETE` | Supporting code/repository work is done; reader-facing treatment may remain. |
| `PARTIAL` | Some evidence or curation exists, but the declared phase is incomplete. |
| `PENDING` | Work has not started. |

The status of a notebook execution and the status of its interpretation must always be tracked separately.

---

## 6. Standard chapter anatomy

Every substantive chapter uses this structure:

1. **Why this chapter exists**
2. **Prerequisite intuition**
3. **Street explanation**
4. **Definitions and notation**
5. **Information-timing contract**
6. **Worked hand example**
7. **Lab orientation**
8. **What to observe in the outputs**
9. **Price-path casebook**
10. **Common misreadings**
11. **Causal versus hindsight audit**
12. **Mandatory completion-gate exercises**
13. **Transfer exercise**
14. **Locked-in intuition**
15. **What this chapter does not establish**

Answers and instructor notes must be kept separate from the main exercise prompt so the learner must interpret the evidence before seeing a reference answer.

---

## 7. Master table of contents and lab map

| Part | Chapter | Roadmap phase | Primary lab or source | Current content status |
|---|---:|---:|---|---|
| 0 — How to Think About DC | 0. The pre-exploration contract | 0 | [Root causality contract](../README.md#causality-contract), `dc_basics/events.py`, `tests/test_core.py` | `DRAFTED` |
| I — One Threshold | 1. Directional-change mechanics | 1 | `1_threshold_dc_explore.ipynb` | `DRAFTED` |
| I — One Threshold | 2. TMV, T, R, and overshoot | 1 | `1_threshold_dc_explore.ipynb` | `DRAFTED` |
| I — One Threshold | 3. Event-time state models | 2 | `1_threshold_dc.ipynb` | `DRAFTED` |
| I — One Threshold | 4. What HMM states mean economically | 2 | `1_threshold_dc.ipynb`, Audits 1–7 | `DRAFTED` |
| I — One Threshold | 5. Distribution choices and cross-symbol reproduction | 2–3 | `1_threshold_dc_explore_hmm_dist.ipynb`; single-threshold reruns | `DRAFTED` |
| II — Two Thresholds | 6. Two independent clocks | 4 | `2_threshold_dc.ipynb` | `DRAFTED` |
| II — Two Thresholds | 7. Agreement, disagreement, propagation, and rejection | 4 | `2_threshold_dc.ipynb` | `DRAFTED` |
| II — Two Thresholds | 8. The initiating small DCC and prior-leg evidence | 5 | `2_threshold_dc_event_characteristics.ipynb` | `DRAFTED` |
| II — Two Thresholds | 9. Causal counter-leg development and survival | 5 | `2_threshold_dc.ipynb` live audits | `DRAFTED` |
| II — Two Thresholds | 10. Two-threshold robustness | 6 | `2_threshold_dc_robustness.ipynb` | `DRAFTED` |
| III — Three Thresholds | 11. The eight three-scale configurations | 7 | `3_threshold_dc.ipynb` | `DRAFTED` |
| III — Three Thresholds | 12. Exact event-ID linkage | 8 | `3_threshold_dc_linkage.ipynb` | `DRAFTED` |
| III — Three Thresholds | 13. Two-stage causal live development | 9 | `3_threshold_dc_live_development.ipynb` | `DRAFTED` |
| III — Three Thresholds | 14. Three-scale interpretation and robustness | 10 | `3_threshold_dc_robustness.ipynb` | `DRAFTED` |
| IV — Four Thresholds | 15. Sixteen configurations and coherent depth | 11 | `4_threshold_dc.ipynb` | `DRAFTED` |
| IV — Four Thresholds | 16. Three-stage linkage | 12 | `4_threshold_dc_linkage.ipynb` | `DRAFTED` |
| IV — Four Thresholds | 17. Four-scale causal live development | 13 | `4_threshold_dc_live_development.ipynb` | `DRAFTED` |
| V — Five Thresholds | 18. Five clocks and grid design | 14–15 | `5_threshold_dc.ipynb` | `DRAFTED` |
| V — Five Thresholds | 19. The 32 configurations | 15 | `5_threshold_dc.ipynb` | `DRAFTED` |
| V — Five Thresholds | 20. Four-stage linkage | 16 | `5_threshold_dc_linkage.ipynb` | `DRAFTED` |
| V — Five Thresholds | 21. Five-scale causal live development | 17 | `5_threshold_dc_live_development.ipynb` | `DRAFTED` |
| V — Five Thresholds | 22. Grid and cross-market robustness | 18 | `5_threshold_dc_robustness.ipynb` | `DRAFTED` |
| VI — Arbitrary N | 23. A causal representation for N thresholds | 19 | `multiscale_representation_design.ipynb` | `DRAFTED` |
| VI — Arbitrary N | 24. The interpretable regime baseline | 20 | `20_interpretable_regime_baseline.ipynb` | `DRAFTING` — G20 interpretation pending |
| VII — Probabilistic Regimes | 25. Clustering, mixtures, and filtered HMMs | 21 | `21_probabilistic_regime_models.ipynb` | `DRAFTING` — G21 interpretation pending |
| VII — Probabilistic Regimes | 26. Causal and out-of-sample validation | 22 | `22_causal_oos_validation.ipynb` | `DRAFTING` — G22 interpretation pending |
| VII — Probabilistic Regimes | 27. Economic interpretation without a trading claim | 23 | `23_economic_interpretation.ipynb` | `DRAFTING` — G23 state cards pending |
| VII — Probabilistic Regimes | 28. Cross-market robustness | 24 | `24_cross_market_robustness.ipynb` | `DRAFTING` — G24 interpretation pending |
| VIII — Research Engineering | 29. A causality-safe reusable library | 25–27 | `dc_basics/`, `dc_multiscale_research.py`, `tests/` | `DRAFTED` |
| VIII — Research Engineering | 30. Reproducibility and release discipline | 28–29 | textbook sources and clean-environment run | `DRAFTED` |

---

## 8. Progression graph

The reader must follow this dependency order:

```text
Pre-exploration contract
    -> one-threshold mechanics
    -> one-threshold event-state interpretation
    -> cross-symbol reproduction
    -> two-threshold mechanics
    -> two-threshold causal relationships
    -> two-threshold robustness
    -> three-threshold mechanics
    -> exact linkage
    -> causal live development
    -> robustness
    -> four-threshold hierarchy
    -> five-threshold hierarchy and grid design
    -> arbitrary-N representation
    -> interpretable baseline
    -> probabilistic models
    -> causal/OOS validation
    -> economic interpretation
    -> cross-market robustness
    -> release-quality engineering
```

The number of thresholds may increase only after the learner can explain the current hierarchy's mechanics, linkage, live development, and timing. A classifier may be introduced only after the arbitrary-N representation and direct structural baseline are understood.

---

## 9. Mandatory completion-gate registry

The exercises below are the minimum required gates. Chapter drafts may add exercises but may not remove or weaken these.

### G0 — Pre-exploration contract

Before Chapter 1, the learner must be able to:

1. Explain why every calculated value needs an information timestamp and event ID.
2. Distinguish a completed-event value from a live/current-event value.
3. Explain why a final extreme, completed overshoot, or future outcome cannot be used before confirmation.
4. State why intuition and causal semantics precede model complexity.
5. Explain why diagnostic hindsight may be useful for research but cannot be treated as a deployable input.

**Locked-in statement:** A value is not causal merely because its formula uses past-looking words; it is causal only if every input was knowable at the decision timestamp.

### G1 — Single-threshold mechanics, TMV, T, and R

Before Chapter 3, the learner must be able to:

1. Mark upward and downward DCC confirmations on a raw price chart and state which threshold condition was satisfied.
2. Explain that a DCC in the opposite direction confirms the end extreme of the prior mode and begins the new live mode.
3. Reconstruct several events by hand, including the previous extreme, confirmation bar, TMV, T, R, and overshoot.
4. Explain what `T = 1` means and why its frequency helps diagnose an overly small threshold.
5. Compare the mean, median, and tail of TMV, T, and R, including their right-skewness.
6. Compare TMV and R by direction without assuming directional symmetry.
7. Explain why event observations are path-dependent and not an IID sample of bars.
8. Read the most recent price-path casebook and say what each completed leg and new live mode means economically.

**Locked-in statement:** A downward DCC confirms the prior peak and switches the live DC mode down; the completed upward leg's statistics become known at that confirmation.

### G2 — Single-threshold filtered HMM and Audits 1–7

Before using more than one threshold, the learner must be able to:

1. Explain why the HMM is trained on the event series rather than every price bar.
2. Distinguish an event-time state from its forward-filled, bar-time visualization.
3. Explain why the displayed state can occupy most bars even when its event count is less dominant.
4. Interpret state separation in log-R, TMV–T geometry, and filtered-posterior space.
5. Explain why `fast_R` and `slow_R` are model-relative semantic labels, not thresholds read directly from one R value.
6. Show how the previous filtered belief can make visually similar current observations receive different states.
7. Distinguish filtered probabilities from smoothed probabilities and state why only filtering is causal here.
8. Explain whether the current state is descriptive of the completed event, predictive of the next event, or both, using the out-of-sample audit evidence. Forward claims must rest on the model-free Audit 6b targets, because Audit 6's next-label target is computed from the current filtered probability.
9. Read recent events as an economic casebook: current DCC and completed-leg fields are known; the next extreme, next DCC, and next state remain future information.
10. State why state occupancy, confidence, or apparent visual fit is not a trading claim.

**Locked-in statement:** The filtered state is a causal, history-conditioned description of the completed event stream; its bar mapping does not turn it into a directional forecast.

### G3 — Distribution and cross-symbol reproduction

Before Chapter 6, the learner must be able to:

1. Explain why raw R need not be log-transformed for every distribution family.
2. Compare Normal, Student-t, Lambda, and other supported candidates using convergence, raw-R-scale likelihood (with the Jacobian for every density over log R, including LogNormal), stability across folds and seeds, occupancy, and economic interpretability rather than label balance alone.
3. Explain why different emission families may assign different labels to the same region.
4. Reproduce the definitions, plots, filtering, and audits on another symbol without changing the interpretation after seeing results.
5. Identify which conclusions transfer across EURUSD and US500 and which are threshold-, symbol-, or sample-specific.

**Locked-in statement:** A distribution is useful when its causal states are stable, identifiable, and interpretable out of sample—not because it creates aesthetically balanced labels.

### G4 — Two-threshold mechanics

Before studying outcome relationships, the learner must be able to:

1. Explain why two thresholds create two independent event clocks on the same price path.
2. Read all four ordered mode configurations and separate broad agreement from a counter-scale move.
3. State what a small DCC sees that the large threshold ignores.
4. Explain when repeated small events remain trapped inside one unresolved large event.
5. Distinguish a currently observed disagreement from later propagation or rejection.
6. Identify the exact large or small DCC that resolves an episode and makes its outcome knowable.
7. Explain same-bar ambiguity under close-only observation.
8. Interpret nesting counts and the rejected attempts encoded inside an upper-scale interval, and explain why "the small clock confirms first" and odd parity are near-invariants under multiplicative thresholds rather than laws.

**Locked-in statement:** Small-scale opposition is observable now; whether it propagates to the large clock is future information until the resolving DCC.

### G5 — Two-threshold causal relationships and live development

Before robustness or a third threshold, the learner must be able to:

1. Explain that the initiating small DCC simultaneously completes the prior small leg and begins the new counter-scale mode.
2. Identify which prior-leg TMV, T, and R values are causally known at initiation.
3. Explain why those completed features may overlap heavily between later propagated and rejected outcomes.
4. Define propagation as the upper-scale DCC confirming the target direction and rejection as the lower clock reversing before that confirmation.
5. Pin the initiating small event and follow elapsed time, current excursion, maximum excursion, live TMV/T/R, and progress toward the large threshold.
6. Explain why live TMV may start near or above one and why current excursion can fall while maximum excursion retains path information.
7. Identify the resolution bar and exclude it from every pre-resolution live panel.
8. Explain why later checkpoints contain only surviving unresolved attempts.
9. Explain why outcome-conditioned medians or AUCs are diagnostic hindsight even when every input feature is causal.
10. Compare actual paths in a nearest-opposite-outcome casebook and state why visual similarity at initiation does not imply identical outcomes.

**Locked-in statement:** The seed fixes the question, the live panel describes how the contest develops, and the outcome label remains hindsight until resolution.

### G6 — Two-threshold robustness

Before Chapter 11, the learner must be able to:

1. Reproduce the full analysis on another market and multiple predeclared threshold pairs.
2. Separate structural conclusions from exact propagation rates, durations, and event counts.
3. Explain how absolute thresholds and their ratio change the two clocks.
4. Report inadequate, unresolved, ambiguous, and same-bar cohorts rather than filtering them silently.
5. State whether initiation overlap and live-development relationships recur across symbols, directions, periods, and threshold pairs.
6. Explain why recurring structure still does not establish economic profitability.
7. Use the event-count identity, propagation rate ≈ $2/(N_S/N_L+1)$, to explain why a change of threshold ratio moves the propagation rate far more than a change of absolute scale.
8. Separate information gained by watching a fixed survivor cohort from the change of cohort caused by survivor selection.

### G7 — Three-threshold mechanics

Before linkage, the learner must be able to:

1. Explain why the three clocks remain independent on one price path.
2. Read every `(small, medium, large)` configuration without confusing completed legs with live modes.
3. Identify broad agreement, a small pullback, propagation to medium, and medium fragmentation.
4. Name the exact DCC that changes each configuration component.
5. Explain why intrabar order is unknowable for same-bar multi-scale changes on close-only data.
6. Count small DCCs inside medium intervals and medium DCCs inside large intervals.
7. Explain the (near-invariant) odd nesting counts, how they encode rejected attempts, and what a flagged `parity_violation` means.
8. Distinguish a small-to-medium contest from a medium-to-large contest.
9. Identify the exact resolution bar for each adjacent-scale outcome.
10. Explain why edges with threshold ratios 2.0 and 1.5 need not behave alike.

### G8 — Three-threshold exact linkage

Before live development, the learner must be able to:

1. Explain why the medium event ID is the valid hand-off key between the two adjacent building blocks.
2. Explain why a broad-agreement origin gives the small disturbance definite ancestry.
3. Distinguish terminal depths 0, 1, and 2 from causal attained depth.
4. Explain why, with three-scale broad-agreement roots, linked Stage-2 rates coincide with unconditional medium-to-large rates, and which narrower roots, lineage filters or deeper hand-offs make them differ.
5. Derive the linked probability product without making an independence assumption, and explain why it holds by arithmetic rather than testing anything.
6. Recognize small-scale cycles inside an unresolved medium-to-large contest.
7. Identify the DCC on which each depth is attained and each terminal outcome becomes known.
8. Retain same-bar, ambiguous, unresolved, and unlinked cases explicitly, and explain why the strict-clean cohort (no same-bar stage) gives reach rates biased low relative to the all-resolved cohort.
9. Explain why a linked lineage is a genealogy of confirmations, not necessarily one monotonic price move.

### G9 — Three-threshold causal live development

Before robustness, the learner must be able to:

1. Explain why the initiating small event ID remains the lineage ID through both stages.
2. Treat the medium event ID as a hand-off key rather than a replacement seed.
3. Treat later small DCCs during Stage 2 as nested activity rather than new roots.
4. Explain why target progress can already be positive at checkpoint zero.
5. Verify that every live trajectory stops before its resolution bar.
6. Identify the information timestamp for every live measurement.
7. Name the DCC that makes each stage outcome knowable.
8. Explain how Stage-1 propagation can be known while terminal depth remains unknown.
9. Explain survival selection at later checkpoints.
10. Separate causal inputs from diagnostic, outcome-conditioned medians and AUCs, and withhold AUCs when either outcome has fewer than 20 survivors.
11. Explain why the active lower and upper clocks cannot fire inside a pre-resolution panel, so nested activity comes only from clocks below the lower clock.

### G10 — Three-threshold interpretation and robustness

Before four thresholds, the learner must be able to:

1. Explain common-date restriction and why cases are predeclared.
2. Separate structural conclusions from case-specific numbers.
3. Explain expected changes in event counts and durations with absolute threshold scale.
4. Preserve the original small lineage ID through the medium hand-off.
5. Distinguish attained depth from terminal depth.
6. Explain positive checkpoint-zero progress and survival-conditioned later cohorts.
7. Treat outcome AUC as diagnostic even when its input features are causal.
8. Test whether live progress adds recurring information beyond completed initiation features, on the same survivor cohort, keeping information gain separate from survivor selection.
9. Check dependence on direction, period, symbol, and threshold ladder.
10. Explain why robustness of structure is neither trading profitability nor permission to skip walk-forward evaluation.

### G11 — Four-threshold mechanics

Before four-scale linkage, the learner must be able to:

1. Read all configurations in small/medium/large/macro order.
2. Distinguish coherent depth-2 opposition from a fragmented configuration with the same direction count.
3. Explain why agreement breadth does not uniquely identify structural shape.
4. Leave coherent counter depth undefined when multiple direction boundaries exist.
5. Explain same-bar ambiguity and identify the DCC changing each component.
6. Explain why equally spaced thresholds have unequal adjacent ratios and how ratios affect event counts and propagation rates.
7. Interpret odd nested counts and prior rejection pairs, including the rare flagged parity violation.
8. Explain why three adjacent-edge tables are not yet a linked lineage.
9. Identify broad coherence, shallow disturbance, deep propagation, and fragmentation on actual price paths.
10. Explain why `coherent_frontier` (at most one boundary) includes broad agreement, and use `direction_boundaries == 1` for a single live counter-move front.

### G12 — Four-threshold linkage

Before live development, the learner must be able to:

1. Require broad agreement on the bar before a valid root.
2. Keep the small event as immutable lineage ID through all stages.
3. Use medium and large event IDs as exact hand-off keys.
4. Explain why event-ID equality is stronger than timestamp proximity.
5. Define terminal depths 0 through 3 and the DCC where each depth is attained.
6. Explain why terminal depth remains hindsight until lineage resolution.
7. Keep same-bar, ambiguous, unresolved, and unlinked paths explicit.
8. Derive linked conditional reach rates without assuming independence, for both the all-resolved (unbiased) and strict-clean (biased-low) cohorts.
9. Explain why a depth-3 lineage need not be monotonic.
10. Explain why linked stage rates differ from unconditional edge rates at four scales but coincide at three.

### G13 — Four-threshold causal live development

Before five thresholds, the learner must be able to:

1. Preserve the immutable seed through three stages.
2. Explain why hand-off DCCs change the active stage but not the root.
3. Verify that every stage excludes its resolution bar.
4. Identify the lower and upper TMV/T/R clock in each stage.
5. Distinguish causal attained depth from future terminal depth.
6. Explain nested DCCs on clocks below the active lower clock, why the active clocks' own counts are zero by construction, and unresolved fragmentation in later stages.
7. Explain what direction-boundary count adds beyond threshold progress.
8. Distinguish macro-agreement breadth from a coherent propagation frontier, and explain why the two coincide in Stages 1–2.
9. Explain later-checkpoint survival selection and why higher later AUC is not an initiation forecast.
10. State whether live geometry adds information beyond completed initiation features, without making an alpha claim.

### G14–G15 — Five-threshold mechanics, interpretation, and grid design

Before five-scale linkage, the learner must be able to:

1. Explain why multithreshold DC is real but five thresholds is not a canonical calibration.
2. Derive the 32 possible mode configurations.
3. Read every configuration in small/medium/large/macro/outer order.
4. Distinguish one coherent propagation boundary from two-or-more-boundary fragmentation.
5. Explain why agreement breadth does not uniquely identify shape.
6. Compare the linear ladder's changing ratios with a constant-ratio ladder.
7. Explain how ratios affect events, nesting, and adjacent propagation, including why an adjacent propagation rate is approximately $2/(N_{lower}/N_{upper}+1)$.
8. Explain why different causal readings from two grids are not contradictory.
9. Preserve same-bar ambiguity and confirmation-time semantics for TMV/T/R and outcomes.
10. Explain why no grid is superior without a predeclared objective and out-of-sample validation.
11. State the predeclared geometric rule that selects the primary grid, and keep observed propagation rates out of that justification.

### G16 — Five-threshold linkage

Before live development, the learner must be able to:

1. Require broad agreement before a valid root and preserve the immutable small seed through four hand-offs.
2. Find each stage using its exact resolution event ID rather than nearest-time matching.
3. Define terminal depths 0 through 4 and distinguish them from causal attained depth.
4. Explain why depth zero is a real attempt and depth four is confirmation of outer-scale propagation, not continuation.
5. Exclude same-bar stages from the strict-clean live cohort, distinguish a same-bar (zero-length) propagation from an ambiguous stage, and explain why the strict-clean ladder is biased low relative to the all-resolved ladder.
6. Multiply conditional reach rates without asserting stage independence.
7. Quantify lower-scale activity strictly before each stage's resolving DCC while a later stage remains unresolved.
8. Check depth stability by direction and sample third.
9. Explain why linkage is structural description rather than a trading signal.

### G17 — Five-threshold causal live development

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

### G18 — Five-threshold robustness

Before arbitrary-N representation, the learner must be able to:

1. Use common calendar intervals and predeclare all cases.
2. Identify which comparison changes symbol, scale, or grid geometry.
3. Keep the constant-ratio primary ladder fixed even if another case has a higher ex-post propagation rate.
4. Report outer-event counts and the lineage accounting (eligible roots, strict-clean, resolved with a same-bar stage, ambiguous, unresolved, unlinked) before percentages.
5. Explain unequal occupancy across the 32 configurations.
6. Test recurrence of agreement, fragmentation, entropy, and the depth ladder, using all resolved lineages for the ladder and explaining why the strict-clean ladder is biased downward.
7. Treat exact depth probabilities as case-specific.
8. Audit survivor selection, direction concentration, and sample-period concentration.
9. Explain what changes under fixed ratios versus a linear grid.
10. Treat the grid as part of model specification, not neutral preprocessing.
11. Separate structural robustness from profitability and require training-only, walk-forward model selection.

### G19 — Arbitrary-N causal representation

Before fitting a regime classifier, the learner must be able to:

1. Explain why `scale_state` is the canonical arbitrary-N node representation.
2. Derive exactly `N - 1` adjacent edge states for `N` thresholds.
3. Retain the ordered mode vector even when breadth and fragmentation summaries exist.
4. Include threshold values and adjacent ratios in the representation contract.
5. Distinguish current-leg from completed-leg TMV/T/R and leg excursion from reversal progress.
6. Distinguish current adjacent disagreement from later propagation or rejection.
7. Keep attained depth causal and terminal depth diagnostic until resolution.
8. Exclude the resolution bar and mark same-bar transitions ambiguous under close-only observation.
9. Explain why bar time and union-event time produce different populations.
10. Exclude full-sample normalization from a deployable representation.
11. Explain why fragmented states cannot be reduced faithfully to one propagation-depth number.
12. Pass the same construction and identity checks for two through five thresholds.
13. Keep `lineage_resolutions` diagnostic and never backward-join it into `lineage_state`.
14. Show that the notebook's explicit builders and `dc_multiscale_research.build_multiscale_state` produce identical shared columns, so the representation has one implementation.

### G20 — Interpretable regime baseline

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

**Current status:** Notebook source revised after the 2026-11-10 review; rerun pending; learner interpretation pending.

### G21 — Probabilistic regime models

Before model selection, the learner must be able to:

1. Explain that K-means and mixtures classify the current observation while an HMM carries filtered state history.
2. Use filtered, not smoothed, probabilities for causal HMM output.
3. Preserve training-only one-to-one semantic mapping and leave surplus states unmatched.
4. Keep raw state IDs primary and treat agreement with the direct taxonomy as descriptive.
5. Explain why persistence or confidence alone is not usefulness, especially when variances hit their floor.
6. Distinguish the transition processes and computational burdens of bar-time and event-time HMMs.
7. Defer model selection to the predeclared causal/OOS phase.
8. Read restart stability (adjusted Rand agreement across seeds) for every family before any selection.
9. Explain, feature by feature, where a density model's likelihood comes from, and why zero-inflated point masses are screened out of continuous emissions.

**Current status:** Notebook source revised after the 2026-11-10 review; rerun pending; learner interpretation pending.

### G22 — Causal and out-of-sample validation

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

### G23 — Economic interpretation

For each inferred state, the learner must be able to state:

1. Its raw state ID and separate training-only overlap annotation.
2. Its hierarchy shape and direction balance.
3. Whether it is agreement, a coherent frontier, or fragmentation.
4. Its scale ages, reversal pressure, and DCC activity.
5. Its filtered confidence, persistence, restart stability, and variance-floor warning.
6. Its observed transition structure.
7. Which later activity or volatility differences are diagnostic outcomes rather than causal inputs.
8. Whether it adds a stable distinction beyond both direct baselines.
9. Why the state still does not specify a position, entry, exit, or expected net return.

**Current status:** Notebook source revised after the 2026-11-10 review; rerun pending; learner interpretation pending.

### G24 — Cross-market robustness

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

### G25–G27 — Research engineering and repository extraction

Before release, the maintainer must verify:

1. Repeated mechanics, linkage, live-panel, audit, and plotting code lives in reusable modules rather than being independently reimplemented in notebooks.
2. The repository contains local implementations of required directional-change functionality and does not depend on private source repositories.
3. Tests cover timestamp causality, event identity, nesting parity, exact hand-offs, same-bar ambiguity, and resolution-bar exclusion.
4. Notebooks remain readable laboratories rather than hidden application layers.
5. Public examples do not depend on unavailable private data paths without an explicit data-acquisition or sample-data alternative.

### G28–G29 — Textbook and reproducibility release

The book is release-ready only when:

1. Every chapter follows the standard anatomy.
2. Every gate has an exercise prompt, learner response space, and separate reference answer.
3. Every figure and table can be traced to a notebook cell and declared dataset/configuration.
4. Every causal claim identifies its information timestamp.
5. Every hindsight result is labelled diagnostic.
6. A clean environment can execute the documented lab path with pinned dependencies.
7. Private paths, credentials, and machine-specific assumptions are removed or parameterized.
8. The full manuscript passes technical, causal, pedagogical, and reproducibility review.

---

## 10. Notebook-to-chapter source index

| Notebook | Textbook role | Gate owner |
|---|---|---|
| `1_threshold_dc_explore.ipynb` | Single-clock mechanics and TMV/T/R EDA | G1 |
| `1_threshold_dc.ipynb` | Filtered event-state model and Audits 1–7 | G2 |
| `1_threshold_dc_explore_hmm_dist.ipynb` | Emission-family and transform comparison | G3 |
| `2_threshold_dc.ipynb` | Two clocks, disagreement episodes, live counter-leg audits | G4–G5 |
| `2_threshold_dc_event_characteristics.ipynb` | Initiation evidence and outcome-conditioned diagnostics | G5 |
| `2_threshold_dc_robustness.ipynb` | Two-threshold symbol, absolute-scale and ratio robustness | G6 |
| `3_threshold_dc.ipynb` | Three-clock mechanics and eight configurations | G7 |
| `3_threshold_dc_linkage.ipynb` | Exact two-stage genealogy | G8 |
| `3_threshold_dc_live_development.ipynb` | Causal pre-resolution stage panels | G9 |
| `3_threshold_dc_robustness.ipynb` | Three-scale transfer and stability | G10 |
| `4_threshold_dc.ipynb` | Four-clock mechanics and sixteen configurations | G11 |
| `4_threshold_dc_linkage.ipynb` | Exact three-stage genealogy | G12 |
| `4_threshold_dc_live_development.ipynb` | Four-scale causal live paths | G13 |
| `5_threshold_dc.ipynb` | Five-clock mechanics, 32 configurations, and grid comparison | G14–G15 |
| `5_threshold_dc_linkage.ipynb` | Exact four-stage genealogy | G16 |
| `5_threshold_dc_live_development.ipynb` | Five-scale causal live paths | G17 |
| `5_threshold_dc_robustness.ipynb` | Grid, symbol, direction, period, and scale robustness | G18 |
| `multiscale_representation_design.ipynb` | Arbitrary-N causal schema | G19 |
| `20_interpretable_regime_baseline.ipynb` | Direct structural comparator | G20 |
| `21_probabilistic_regime_models.ipynb` | Clustering, mixtures, and filtered HMMs | G21 |
| `22_causal_oos_validation.ipynb` | Validation/test discipline and causal audits | G22 |
| `23_economic_interpretation.ipynb` | State casebooks and economic meaning | G23 |
| `24_cross_market_robustness.ipynb` | Frozen-procedure external transfer | G24 |

---

## 11. Interpretation record required for every lab

Each completed lab must produce a compact interpretation record with these fields:

```text
lab_id:
run_date:
symbol_period_frequency:
thresholds_or_grid:
mechanical_observations:
causally_known_fields:
hindsight_or_diagnostic_fields:
casebook_examples:
distribution_or_transition_evidence:
misconceptions_corrected:
transfer_evidence:
remaining_uncertainty:
locked_in_statement:
gate_status: not_started | attempted | passed | revisit
```

The record stores interpretation, not notebook output. Large tables and figures remain in the executable notebook and are referenced by stable section or cell labels.

---

## 12. Notation and semantic invariants

The textbook must use these distinctions consistently:

- **DCC:** the confirmation event at which the threshold condition becomes satisfied.
- **Live mode:** the new direction confirmed by the latest DCC.
- **Completed leg:** the prior directional leg whose endpoint is confirmed by the new DCC.
- **TMV, T, R:** attributes of a specified leg or live path; every use must say which.
- **Event time:** observations indexed by DCC events.
- **Bar time:** observations indexed by raw price bars.
- **Seed:** the immutable initiating small DCC that roots a lineage.
- **Hand-off:** an exact resolution-event-ID connection to the next adjacent-scale contest.
- **Attained depth:** the greatest confirmed scale reached so far; causal.
- **Terminal depth:** the final depth after lineage resolution; hindsight until resolved.
- **Agreement breadth:** number or fraction of scales matching the reference direction.
- **Direction-boundary count:** number of adjacent direction changes across the ordered hierarchy.
- **Coherent frontier:** exactly one ordered boundary separating target-side and origin-side modes. Code note: the `coherent_frontier` flag in `dc_basics.configuration` and `dc_multiscale_research` is `direction_boundaries <= 1`, so it also includes broad agreement (zero boundaries). Use `direction_boundaries == 1` when the strict concept is meant, and say which one a table reports.
- **Fragmentation:** multiple direction boundaries; not reducible to one propagation depth.
- **Current state:** information available at the observation timestamp.
- **Outcome label:** a later propagated/rejected or terminal result; diagnostic before resolution.
- **Filtered probability:** a state probability using observations no later than the current timestamp.
- **Smoothed probability:** a probability using later observations; diagnostic only in this book's causal analyses.

No chapter may use `state`, `regime`, `direction`, `event`, `leg`, or `outcome` ambiguously when a more precise term is available.

---

## 13. Causality and evaluation rules

Every lab and chapter must obey these rules:

1. Attach an information timestamp and event identity to derived event values.
2. Exclude a stage's resolution bar from its pre-resolution live panel.
3. Never backward-join terminal outcomes or future resolution records into causal feature rows.
4. Mark close-only same-bar cross-scale order as ambiguous.
5. Fit scalers, semantic mappings, thresholds, and model choices on the declared training data only.
6. Use filtered rather than smoothed state probabilities for deployable descriptions.
7. Preserve unresolved, ambiguous, unlinked, collapsed, and inadequate cases in audits.
8. Separate event-weighted from bar-weighted statistics.
9. Treat outcome-conditioned plots, AUCs, and medians as diagnostic unless a predeclared forward evaluation establishes otherwise.
10. Compare probabilistic models with the direct causal structural baseline.
11. Do not infer profitability from structural recurrence, model fit, persistence, confidence, or future volatility separation.
12. Any later trading study must add realistic costs, execution timing, conditional performance analysis, out-of-sample testing, and trade-level price/PnL visualization.

---

## 14. Textbook construction order

The manuscript should be built in vertical slices rather than by drafting all prose before exercises:

1. **Pilot slice:** Chapters 0–2, including figures, hand calculations, lab guide, exercises, answers, and review.
2. **One-threshold completion:** Chapters 3–5.
3. **Two-threshold foundation:** Chapters 6–10.
4. **Hierarchy ladder:** Chapters 11–22.
5. **Representation:** Chapters 23–24, after G20 interpretation is passed.
6. **Probabilistic section:** Chapters 25–28, only after G21–G24 are interpreted and passed.
7. **Engineering and appendices:** Chapters 29–30 and release material.

The pilot slice establishes the permanent voice, notation, figure style, exercise format, and answer depth for the rest of the book.

---

## 15. Planned appendices

| Appendix | Purpose |
|---|---|
| A. Notation and equations | Canonical DC, TMV, T, R, progress, breadth, and boundary definitions. |
| B. Event and live-panel schemas | Field-level information timing and identifiers. |
| C. Configuration atlas | Ordered mode configurations for two through five thresholds. |
| D. Causality audit checklist | Reusable checks for every new feature and label. |
| E. Plot-reading guide | DCC markers, segments, modes, lineages, checkpoints, and ambiguity. |
| F. Common misconceptions | Completed leg versus live mode, state versus outcome, event versus bar occupancy, confidence versus usefulness. |
| G. Exercise solutions | Reference interpretations kept separate from prompts. |
| H. API and module guide | `dc_basics/`, multiscale research helpers, plotting, and tests. |
| I. Reproduction guide | Environment, data contract, execution order, and expected artifacts. |
| J. Glossary | Stable reader-facing terminology. |

---

## 16. Current roadmap state

| Roadmap phase | Evidence state | Interpretation state | Textbook state |
|---:|---|---|---|
| 0–19 | Labs and structural work complete | Foundational interpretation complete | Ready to write |
| 20–24 | Notebooks run successfully | Mandatory interpretation pending | Blocked from final chapter prose |
| 25 | Modularization complete at the notebook-safe boundary | Engineering review complete | Ready for Chapter 29 treatment |
| 26 | Foundational invariant tests exist | Coverage expansion remains part of release work | Partial |
| 27 | Standalone repository created | Public pedagogical curation remains | Partial |
| 28 | Manifest, Chapters 0–30, and separate solution guide drafted | Technical/pedagogical review and G20–G24 integration remain | In progress |
| 29 | Not started | Not started | Pending |

---

## 17. Change control

Any change to chapter order, core terminology, a completion gate, or causal semantics must update this manifest in the same change set.

For every structural revision:

1. record the reason;
2. identify affected chapters, notebooks, and gates;
3. state whether the revision changes interpretation or only presentation;
4. rerun affected invariants when semantics change;
5. preserve a visible distinction between historical evidence and newly generated evidence.

### Decision log

| Date | Decision | Reason |
|---|---|---|
| 2026-11-10 | Use the roadmap as the textbook spine. | It preserves the actual order in which the intuition was acquired. |
| 2026-11-10 | Make notebook completion gates mandatory chapter exercises. | Execution alone does not demonstrate understanding. |
| 2026-11-10 | Keep phases 20–24 marked interpretation-pending despite successful runs. | Model outputs must be interpreted before becoming textbook claims. |
| 2026-11-10 | Store the manifest in `docs/`. | Documentation is the authoritative home for the textbook blueprint. |
| 2026-11-10 | Make intellectual provenance and primary-source attribution mandatory. | The textbook teaches and extends an established Directional Change research tradition. |
| 2026-11-10 | Complete a succinct notebook-companion draft for Chapters 0–30. | The notebooks remain the evidence; chapters prepare and consolidate their interpretation. |

---

## 18. Immediate next action

Review the first draft in this order:

1. Perform the pilot technical and pedagogical review on Chapters 0–2, establishing the permanent voice and exercise depth.
2. Verify Chapters 3–23 and 29–30 against their notebooks, code, and completion gates.
3. Write and pass interpretation records G20–G24, then replace the provisional portions of Chapters 24–28 with evidence-backed conclusions.
4. Add stable notebook section anchors, selected figures, and hand-worked examples only after the prose and semantics are approved.
5. Run the final link, attribution, and clean-environment checks before marking any chapter `REVIEWED`.

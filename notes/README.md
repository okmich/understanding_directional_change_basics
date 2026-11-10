# Understanding Directional Change from First Principles

*An intuition-first, causality-safe journey from one threshold to multiscale market regimes*

**Author:** Michael Enudi

This is a concise companion to the executable notebooks in the repository. Read a chapter, run its lab, inspect the actual paths, and answer the completion gate before continuing. The prose supplies intuition and causal semantics; the notebooks supply evidence.

## Front matter

### Why these notes exist

Directional Change replaces a fixed sampling clock with events created by the price path. That simple change is easy to code and surprisingly easy to misunderstand. The difficult ideas are not the threshold comparisons themselves; they are the meanings of confirmation, retrospective extremes, independent clocks, linked lineages, and information timing.

### Mission

The notes develop directional-change intuition from first principles. Its destination is the ability to look at a causal multiscale state and explain, without hindsight:

> Small-scale activity is intense, propagation has reached the medium scales but not the large scales, and the broader structure remains intact.

The notes succeed when the learner can:

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

#### Non-goals

The notes do not:

- begin with a trading strategy;
- treat a DC state as an entry or exit signal by default;
- call diagnostic hindsight labels deployable targets;
- optimize thresholds against future profitability during intuition building;
- treat an HMM state name as objective market truth;
- accept aggregate fit, persistence, confidence, or Sharpe as sufficient evidence;
- hide ambiguous, unresolved, same-bar, unlinked, or inadequately sampled cases.

## How to use the notes

1. Read the front matter below, then only the chapter assigned to the next lab.
2. Run the linked notebook without changing its definitions.
3. Inspect the price-path casebooks, not only summary tables.
4. Write your answers to the chapter exercises before expanding the chapter's completion-gate guidance.
5. Advance only when you can apply the locked-in statement to an unseen chart segment.


### Credits and acknowledgements

Directional Change is not an invention of this repository or notes. This work stands on a research tradition developed over several decades.

The foundational credit belongs to Dominique M. Guillaume, Michel M. Dacorogna, Rakhal R. Davé, Ulrich A. Müller, Richard B. Olsen, and Olivier V. Pictet. Their 1997 study introduced Directional Change to the financial-market literature as part of an event-based view of high-frequency foreign-exchange data and intrinsic time.

Special credit belongs to **Jun Chen and Edward P. K. Tsang**, authors of *Detecting Regime Change in Computational Finance: Data Science, Machine Learning and Algorithmic Trading*. Their book is the principal intellectual catalyst for this notes's study of Directional Change indicators, Hidden Markov Models, regime characterization, causal market monitoring, and the distinction between retrospective regime discovery and live regime tracking.

Richard B. Olsen deserves additional acknowledgement as a foundational co-author, long-standing advocate of intrinsic-time market analysis, and author of the foreword to Chen and Tsang's book. The broader Directional Change research program—including work by James B. Glattfelder, Alexandre Dupuis, Edward P. K. Tsang, Jun Chen, Monira Aloud, and their collaborators—developed the scaling-law, indicator, market-profiling, regime-analysis, and application literature from which this project learns.

The contribution of these notes is narrower and pedagogical:

- reconstruct the ideas from rudimentary mechanics upward;
- make information timing and causal provenance explicit at every step;
- connect single-threshold intuition to exact multiscale event-ID lineages;
- turn executable notebook completion gates into mandatory interpretation exercises;
- provide a reproducible learning path that distinguishes observable structure from hindsight outcomes and trading claims.

It must never imply that this repository originated Directional Change, overshoot analysis, TMV/T/R indicators, intrinsic-time analysis, or Directional Change regime modeling.

#### Required attribution policy

Every public manuscript produced from this repository must:

1. include the credits and acknowledgements section;
2. cite the foundational 1997 paper when Directional Change is first introduced;
3. cite Chen and Tsang's book when introducing the regime-change research program, TMV/T/R-based regime characterization, or the motivating HMM workflow;
4. cite the relevant primary paper when presenting a published indicator, scaling law, formalism, or empirical claim;
5. label reproduced or adapted definitions, equations, tables, and figures accurately;
6. distinguish reproduction, pedagogical re-expression, implementation choice, empirical extension, and genuinely new contribution;
7. preserve attribution in notebook narratives, notes chapters, generated documentation, and derivative repositories;
8. avoid implying conceptual originality merely because the implementation was independently written.


### Notation and semantic invariants

| Symbol | Meaning |
|---|---|
| $P_i$ | Close price at bar position $i$ |
| $\theta$ | Directional-change threshold as a price fraction |
| EXT | A peak or trough, known retrospectively after reversal confirmation |
| DCC | The bar that confirms a directional change |
| TMV | Completed price displacement measured in units of $\theta$ |
| $T$ | Bars between the completed leg's start and end extremes |
| $R$ | Completed return per bar: $\mathrm{TMV}\,\theta/T$ |
| mode | Current confirmed direction at one threshold |
| seed | Initiating small DCC that permanently identifies a lineage |
| attained depth | Largest scale already confirmed by the lineage |
| terminal depth | Final scale reached, known only when the lineage resolves |

The main labs use symmetric thresholds: `alpha = 1.0`. The local parser supports an asymmetric downward threshold through `alpha`, but that extension is not part of the core intuition sequence.

#### Semantic invariants

The notes must use these distinctions consistently:

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
- **Smoothed probability:** a probability using later observations; diagnostic only in these notes' causal analyses.

No chapter may use `state`, `regime`, `direction`, `event`, `leg`, or `outcome` ambiguously when a more precise term is available.

### The three questions to ask everywhere

1. **What ended?** Identify the completed leg and its retrospective endpoint.
2. **What is live now?** Identify the mode or unresolved contest after confirmation.
3. **What is still unknown?** Identify the future DCC, outcome, or terminal depth.

If a paragraph, feature, plot, or model cannot answer those three questions, its semantics are incomplete.

### Evidence language

The notes use four levels of claim:

- **Mechanical:** true by construction or invariant.
- **Descriptive:** observed in this sample.
- **Diagnostic:** uses a future outcome to understand present causal features.
- **Deployable:** computed causally and validated under a predeclared out-of-sample procedure.

None of these terms means profitable. A trading claim would require a separate decision rule, costs, execution timing, conditional evaluation, and trade-level inspection.

### Causality and evaluation rules

Every lab and chapter must obey these rules:

1. Attach an information timestamp and event identity to derived event values.
2. Exclude a stage's resolution bar from its pre-resolution live panel.
3. Never backward-join terminal outcomes or future resolution records into causal feature rows.
4. Mark close-only same-bar cross-scale order as ambiguous.
5. Fit scalers, semantic mappings, and thresholds on the declared training data only; choose models on validation data; never let test data inform either.
6. Use filtered rather than smoothed state probabilities for deployable descriptions.
7. Preserve unresolved, ambiguous, unlinked, collapsed, and inadequate cases in audits.
8. Separate event-weighted from bar-weighted statistics.
9. Treat outcome-conditioned plots, AUCs, and medians as diagnostic unless a predeclared forward evaluation establishes otherwise.
10. Compare probabilistic models with the direct causal structural baseline.
11. Do not infer profitability from structural recurrence, model fit, persistence, confidence, or future volatility separation.
12. Any later trading study must add realistic costs, execution timing, conditional performance analysis, out-of-sample testing, and trade-level price/PnL visualization.

## Contents

Each chapter's roadmap phase, primary lab and current status.

### Part 0 — How to think about Directional Change

| Chapter | Roadmap phase | Primary lab or source | Status |
|---|---:|---|---|
| [0. The pre-exploration contract](00_pre_exploration_contract.md) | 0 | [Root causality contract](../README.md#causality-contract), `dc_basics/events.py`, `tests/test_core.py` | `DRAFTED` |

### Part I — One threshold

| Chapter | Roadmap phase | Primary lab or source | Status |
|---|---:|---|---|
| [1. Directional-change mechanics](01_directional_change_mechanics.md) | 1 | `1_threshold_dc_explore.ipynb` | `DRAFTED` |
| [2. TMV, T, R, and overshoot](02_tmv_t_r_overshoot.md) | 1 | `1_threshold_dc_explore.ipynb` | `DRAFTED` |
| [3. Event-time state models](03_event_time_state_models.md) | 2 | `1_threshold_dc.ipynb` | `DRAFTED` |
| [4. What an HMM state means economically](04_hmm_economic_meaning.md) | 2 | `1_threshold_dc.ipynb`, Audits 1–7 | `DRAFTED` |
| [5. Distribution choice and reproduction](05_distribution_and_reproduction.md) | 2–3 | `1_threshold_dc_explore_hmm_dist.ipynb`; single-threshold reruns | `DRAFTED` |

### Part II — Two thresholds

| Chapter | Roadmap phase | Primary lab or source | Status |
|---|---:|---|---|
| [6. Two independent clocks](06_two_independent_clocks.md) | 4 | `2_threshold_dc.ipynb` | `DRAFTED` |
| [7. Agreement, propagation, and rejection](07_agreement_propagation_rejection.md) | 4 | `2_threshold_dc.ipynb` | `DRAFTED` |
| [8. The initiating small DCC](08_initiating_small_dcc.md) | 5 | `2_threshold_dc_event_characteristics.ipynb` | `DRAFTED` |
| [9. Counter-leg development and survival](09_counter_leg_survival.md) | 5 | `2_threshold_dc.ipynb` live audits | `DRAFTED` |
| [10. Two-threshold robustness](10_two_threshold_robustness.md) | 6 | `2_threshold_dc_robustness.ipynb` | `DRAFTED` |

### Part III — Three thresholds

| Chapter | Roadmap phase | Primary lab or source | Status |
|---|---:|---|---|
| [11. The eight three-scale configurations](11_three_scale_configurations.md) | 7 | `3_threshold_dc.ipynb` | `DRAFTED` |
| [12. Exact event-ID linkage](12_exact_event_id_linkage.md) | 8 | `3_threshold_dc_linkage.ipynb` | `DRAFTED` |
| [13. Two-stage causal live development](13_two_stage_live_development.md) | 9 | `3_threshold_dc_live_development.ipynb` | `DRAFTED` |
| [14. Three-scale robustness](14_three_scale_robustness.md) | 10 | `3_threshold_dc_robustness.ipynb` | `DRAFTED` |

### Part IV — Four thresholds

| Chapter | Roadmap phase | Primary lab or source | Status |
|---|---:|---|---|
| [15. Sixteen configurations and coherent depth](15_four_scale_configurations.md) | 11 | `4_threshold_dc.ipynb` | `DRAFTED` |
| [16. Three-stage linkage](16_three_stage_linkage.md) | 12 | `4_threshold_dc_linkage.ipynb` | `DRAFTED` |
| [17. Four-scale causal live development](17_four_scale_live_development.md) | 13 | `4_threshold_dc_live_development.ipynb` | `DRAFTED` |

### Part V — Five thresholds

| Chapter | Roadmap phase | Primary lab or source | Status |
|---|---:|---|---|
| [18. Five clocks and grid design](18_five_clocks_grid_design.md) | 14–15 | `5_threshold_dc.ipynb` | `DRAFTED` |
| [19. Reading the 32 configurations](19_thirty_two_configurations.md) | 15 | `5_threshold_dc.ipynb` | `DRAFTED` |
| [20. Four-stage linkage](20_four_stage_linkage.md) | 16 | `5_threshold_dc_linkage.ipynb` | `DRAFTED` |
| [21. Five-scale causal live development](21_five_scale_live_development.md) | 17 | `5_threshold_dc_live_development.ipynb` | `DRAFTED` |
| [22. Five-scale robustness](22_five_scale_robustness.md) | 18 | `5_threshold_dc_robustness.ipynb` | `DRAFTED` |

### Part VI — Arbitrary N

| Chapter | Roadmap phase | Primary lab or source | Status |
|---|---:|---|---|
| [23. A causal representation for N thresholds](23_arbitrary_n_representation.md) | 19 | `multiscale_representation_design.ipynb` | `DRAFTED` |
| [24. The interpretable regime baseline](24_interpretable_regime_baseline.md) | 20 | `20_interpretable_regime_baseline.ipynb` | `DRAFTING` — G20 interpretation pending |

### Part VII — Probabilistic regimes

| Chapter | Roadmap phase | Primary lab or source | Status |
|---|---:|---|---|
| [25. Clustering, mixtures, and filtered HMMs](25_probabilistic_regime_models.md) | 21 | `21_probabilistic_regime_models.ipynb` | `DRAFTING` — G21 interpretation pending |
| [26. Causal and out-of-sample validation](26_causal_oos_validation.md) | 22 | `22_causal_oos_validation.ipynb` | `DRAFTING` — G22 interpretation pending |
| [27. Economic interpretation without a trading claim](27_economic_interpretation.md) | 23 | `23_economic_interpretation.ipynb` | `DRAFTING` — G23 state cards pending |
| [28. Cross-market robustness](28_cross_market_robustness.md) | 24 | `24_cross_market_robustness.ipynb` | `DRAFTING` — G24 interpretation pending |

### Part VIII — Research engineering

| Chapter | Roadmap phase | Primary lab or source | Status |
|---|---:|---|---|
| [29. A causality-safe reusable library](29_reusable_library.md) | 25–27 | `dc_basics/`, `dc_multiscale_research.py`, `tests/` | `DRAFTED` |
| [30. Reproducibility and release discipline](30_reproducibility_release.md) | 28–29 | notes sources and clean-environment run | `DRAFTED` |


The number of thresholds may increase only after the learner can explain the current hierarchy's mechanics, linkage, live development, and timing. A classifier may be introduced only after the arbitrary-N representation and direct structural baseline are understood.

## Completion gates

Running a notebook is necessary but not sufficient. A phase is complete only after its completion gate is answered in the learner's own words and supported by notebook evidence.

Each gate sits at the end of the chapter that closes its roadmap phase, just before that chapter's completion-gate guidance.

## Core bibliography

The bibliography will grow during chapter construction. These references are mandatory anchors:

1. Guillaume, D. M., Dacorogna, M. M., Davé, R. R., Müller, U. A., Olsen, R. B., and Pictet, O. V. (1997). “From the Bird's Eye to the Microscope: A Survey of New Stylized Facts of the Intra-Daily Foreign Exchange Markets.” *Finance and Stochastics*, 1(2), 95–129. <https://doi.org/10.1007/s007800050018>.
2. Glattfelder, J. B., Dupuis, A., and Olsen, R. B. (2011). “Patterns in High-Frequency FX Data: Discovery of 12 Empirical Scaling Laws.” *Quantitative Finance*, 11(4), 599–614. <https://doi.org/10.1080/14697688.2010.481632>.
3. Tsang, E. P. K., and Chen, J. (2018). “Regime Change Detection Using Directional Change Indicators in the Foreign Exchange Market to Chart Brexit.” *IEEE Transactions on Emerging Topics in Computational Intelligence*, 2(3), 185–193. <https://doi.org/10.1109/TETCI.2017.2775235>.
4. Chen, J., and Tsang, E. P. K. (2018). “Classification of Normal and Abnormal Regimes in Financial Markets.” *Algorithms*, 11(12), 202. <https://doi.org/10.3390/a11120202>.
5. Chen, J., and Tsang, E. P. K. (2021). *Detecting Regime Change in Computational Finance: Data Science, Machine Learning and Algorithmic Trading*. CRC Press, first edition. ISBN 978-0-367-53628-2.
6. Tsang, E. P. K. (2022). “Directional Change for Handling Tick-to-Tick Data.” *Journal of Chinese Economic and Business Studies*, 20(2), 171–182. <https://doi.org/10.1080/14765284.2021.1989883>.

The final bibliography must be checked against the primary publications before release. Secondary summaries may help discover sources but must not be the authority for technical or historical claims.


## Decision log

| Date | Decision | Reason |
|---|---|---|
| 2026-11-10 | Build the first edition on the research roadmap: Chapters 0–30 as concise notebook companions, each mandatory completion gate at the end of the chapter that closes its phase, phases 20–24 kept interpretation-pending, intellectual provenance mandatory, and this README in `/notes` as the single source of truth. | The roadmap preserves the order in which the intuition was acquired; the notebooks remain the evidence, and execution alone does not demonstrate understanding. |


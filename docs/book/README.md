# Understanding Directional Change from First Principles

This is a concise companion to the executable notebooks in the repository. Read a chapter, run its lab, inspect the actual paths, and answer the completion gate before continuing. The prose supplies intuition and causal semantics; the notebooks supply evidence.

## How to use the book

1. Read the front matter below, then only the chapter assigned to the next lab.
2. Run the linked notebook without changing its definitions.
3. Inspect the price-path casebooks, not only summary tables.
4. Write your answers to the chapter exercises before expanding the chapter's completion-gate guidance.
5. Advance only when you can apply the locked-in statement to an unseen chart segment.

Running a notebook is not the same as passing its gate. A gate requires a plain-language explanation, the relevant event and information time, notebook evidence, and a causal-versus-hindsight distinction.

## Front matter

### Why this book exists

Directional Change replaces a fixed sampling clock with events created by the price path. That simple change is easy to code and surprisingly easy to misunderstand. The difficult ideas are not the threshold comparisons themselves; they are the meanings of confirmation, retrospective extremes, independent clocks, linked lineages, and information timing.

This book therefore moves slowly through the mechanics and quickly through the prose. The notebooks are the laboratories. The chapters tell you what question each laboratory answers, what you may know at the observation time, and what conclusion would be too strong.

### Intellectual provenance

Foundational credit belongs to Dominique M. Guillaume, Michel M. Dacorogna, Rakhal R. Davé, Ulrich A. Müller, Richard B. Olsen, and Olivier V. Pictet. The regime-analysis journey is especially indebted to Jun Chen and Edward P. K. Tsang and their book *Detecting Regime Change in Computational Finance: Data Science, Machine Learning and Algorithmic Trading*.

Our contribution is an independent, causality-focused teaching sequence: reconstruct the mechanics, attach information times and event IDs, build exact multiscale lineages, and require interpretation before modeling. The full attribution policy and core bibliography are maintained in the [manifest](../TEXTBOOK_MANIFEST.md#2-intellectual-provenance-and-acknowledgements).

### Minimal notation

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

### The three questions to ask everywhere

1. **What ended?** Identify the completed leg and its retrospective endpoint.
2. **What is live now?** Identify the mode or unresolved contest after confirmation.
3. **What is still unknown?** Identify the future DCC, outcome, or terminal depth.

If a paragraph, feature, plot, or model cannot answer those three questions, its semantics are incomplete.

### Evidence language

The book uses four levels of claim:

- **Mechanical:** true by construction or invariant.
- **Descriptive:** observed in this sample.
- **Diagnostic:** uses a future outcome to understand present causal features.
- **Deployable:** computed causally and validated under a predeclared out-of-sample procedure.

None of these terms means profitable. A trading claim would require a separate decision rule, costs, execution timing, conditional evaluation, and trade-level inspection.

## Contents

### Part 0 — How to think about Directional Change

- [Chapter 0 — The pre-exploration contract](00_pre_exploration_contract.md)

### Part I — One threshold

- [Chapter 1 — Directional-change mechanics](01_directional_change_mechanics.md)
- [Chapter 2 — TMV, T, R, and overshoot](02_tmv_t_r_overshoot.md)
- [Chapter 3 — Event-time state models](03_event_time_state_models.md)
- [Chapter 4 — What an HMM state means economically](04_hmm_economic_meaning.md)
- [Chapter 5 — Distribution choice and reproduction](05_distribution_and_reproduction.md)

### Part II — Two thresholds

- [Chapter 6 — Two independent clocks](06_two_independent_clocks.md)
- [Chapter 7 — Agreement, propagation, and rejection](07_agreement_propagation_rejection.md)
- [Chapter 8 — The initiating small DCC](08_initiating_small_dcc.md)
- [Chapter 9 — Counter-leg development and survival](09_counter_leg_survival.md)
- [Chapter 10 — Two-threshold robustness](10_two_threshold_robustness.md)

### Part III — Three thresholds

- [Chapter 11 — The eight three-scale configurations](11_three_scale_configurations.md)
- [Chapter 12 — Exact event-ID linkage](12_exact_event_id_linkage.md)
- [Chapter 13 — Two-stage causal live development](13_two_stage_live_development.md)
- [Chapter 14 — Three-scale robustness](14_three_scale_robustness.md)

### Part IV — Four thresholds

- [Chapter 15 — Sixteen configurations and coherent depth](15_four_scale_configurations.md)
- [Chapter 16 — Three-stage linkage](16_three_stage_linkage.md)
- [Chapter 17 — Four-scale causal live development](17_four_scale_live_development.md)

### Part V — Five thresholds

- [Chapter 18 — Five clocks and grid design](18_five_clocks_grid_design.md)
- [Chapter 19 — Reading the 32 configurations](19_thirty_two_configurations.md)
- [Chapter 20 — Four-stage linkage](20_four_stage_linkage.md)
- [Chapter 21 — Five-scale causal live development](21_five_scale_live_development.md)
- [Chapter 22 — Five-scale robustness](22_five_scale_robustness.md)

### Part VI — Arbitrary N

- [Chapter 23 — A causal representation for N thresholds](23_arbitrary_n_representation.md)
- [Chapter 24 — The interpretable regime baseline](24_interpretable_regime_baseline.md)

### Part VII — Probabilistic regimes

- [Chapter 25 — Clustering, mixtures, and filtered HMMs](25_probabilistic_regime_models.md)
- [Chapter 26 — Causal and out-of-sample validation](26_causal_oos_validation.md)
- [Chapter 27 — Economic interpretation without a trading claim](27_economic_interpretation.md)
- [Chapter 28 — Cross-market robustness](28_cross_market_robustness.md)

### Part VIII — Research engineering

- [Chapter 29 — A causality-safe reusable library](29_reusable_library.md)
- [Chapter 30 — Reproducibility and release discipline](30_reproducibility_release.md)

## Governing documents

- [Textbook source-of-truth manifest](../TEXTBOOK_MANIFEST.md)

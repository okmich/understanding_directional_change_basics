# Purpose, provenance, and notation

## Why this book exists

Directional Change replaces a fixed sampling clock with events created by the price path. That simple change is easy to code and surprisingly easy to misunderstand. The difficult ideas are not the threshold comparisons themselves; they are the meanings of confirmation, retrospective extremes, independent clocks, linked lineages, and information timing.

This book therefore moves slowly through the mechanics and quickly through the prose. The notebooks are the laboratories. The chapters tell you what question each laboratory answers, what you may know at the observation time, and what conclusion would be too strong.

## Intellectual provenance

Foundational credit belongs to Dominique M. Guillaume, Michel M. Dacorogna, Rakhal R. Davé, Ulrich A. Müller, Richard B. Olsen, and Olivier V. Pictet. The regime-analysis journey is especially indebted to Jun Chen and Edward P. K. Tsang and their book *Detecting Regime Change in Computational Finance: Data Science, Machine Learning and Algorithmic Trading*.

Our contribution is an independent, causality-focused teaching sequence: reconstruct the mechanics, attach information times and event IDs, build exact multiscale lineages, and require interpretation before modeling. The full attribution policy and core bibliography are maintained in the [manifest](../TEXTBOOK_MANIFEST.md#2-intellectual-provenance-and-acknowledgements).

## Minimal notation

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

## The three questions to ask everywhere

1. **What ended?** Identify the completed leg and its retrospective endpoint.
2. **What is live now?** Identify the mode or unresolved contest after confirmation.
3. **What is still unknown?** Identify the future DCC, outcome, or terminal depth.

If a paragraph, feature, plot, or model cannot answer those three questions, its semantics are incomplete.

## Evidence language

The book uses four levels of claim:

- **Mechanical:** true by construction or invariant.
- **Descriptive:** observed in this sample.
- **Diagnostic:** uses a future outcome to understand present causal features.
- **Deployable:** computed causally and validated under a predeclared out-of-sample procedure.

None of these terms means profitable. A trading claim would require a separate decision rule, costs, execution timing, conditional evaluation, and trade-level inspection.


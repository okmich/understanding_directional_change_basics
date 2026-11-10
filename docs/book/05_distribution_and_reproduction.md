# Chapter 5 — Distribution choice and reproduction

## Purpose

Test whether the apparent states survive reasonable emission assumptions and another market. Distribution choice is part of the model, not an aesthetic setting.

## Match support to transformation

In [1_threshold_dc_explore_hmm_dist.ipynb](../../1_threshold_dc_explore_hmm_dist.ipynb):

- Normal, Student-t, and Lambda candidates use $\log(R)$ on real-valued support;
- LogNormal, Gamma, and Exponential candidates use raw positive R.

A raw-R predictive likelihood comparison must account for the log transform's Jacobian: $\log p_R(r)=\log p_{\log R}(\log r)-\log r$. The correction applies to every model whose density is over $\log R$. That includes the log-R candidates **and** pomegranate's LogNormal, whose `log_probability` evaluates the Normal density of $\log R$ and omits the $-\log R$ term. After the correction, Normal on log-R and LogNormal on raw R are the same model and must score the same; the notebook asserts this as an implementation check.

Earlier runs of this lab missed the LogNormal correction, which ranked LogNormal last by exactly the mean of $-\log R$, and started LogNormal from an unseeded random point far from the data, which made that fit irreproducible. Both are fixed in `dc_basics/hmm_support.py`. Do not reuse a family ranking from those runs.

## Selection evidence

Prefer chronological out-of-sample predictive likelihood, but also inspect:

- stability across chronological folds and seeds: the notebook's final table refits every family on expanding folds (train on 60%, 70%, 80%) and with extra seeds on the main split, each with the same number of EM restarts;
- fifth-percentile predictive scores for tail failures;
- non-collapsed occupancy;
- sequence-order premium over shuffled OOS observations;
- hard-label agreement (raw and Cohen's kappa) and the filtered-label price comparison across families;
- economic interpretability.

This lab compares families on labels and price paths; the full causal casebook (Audit 7) is in `1_threshold_dc.ipynb` for the Normal baseline. Rerun it with another family before claiming that family's states read differently on price.

Balanced labels are not an objective. A rare tail state can be valid; a beautifully balanced but unstable partition can be useless.

## Reproduction

Repeat the same definitions, split, filtering, semantic mapping, audits, and plots on a second symbol. Change the threshold only for an explicit market-scale reason, then record that change before looking at the preferred state picture.

In this repository, `1_threshold_dc.ipynb` runs the full audits on EURUSD at 0.112%, while `1_threshold_dc_explore.ipynb` and the emission-family lab use US500 at 0.30%. To reproduce Audits 1–7 on US500, set `SYMBOL` and `THETA` in `1_threshold_dc.ipynb` and record the change.

The question is not whether every percentage matches. Ask which mechanical and economic interpretations survive.

## Mandatory exercises

1. Explain why every distribution does not need log-R.
2. Explain the Jacobian adjustment in words, and why Normal on log-R and LogNormal on raw R must tie once it is applied.
3. Compare the winner by predictive fit with the winner by visual label balance, then say whether the winner's lead is larger than its fold-to-fold and seed-to-seed spread.
4. Identify one conclusion that transfers across EURUSD and US500 and one that remains case-specific.
5. Explain what a near-zero sequence-order premium says about the role of Markov dynamics.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- Real-support families can use log-R; positive-support families can model raw R.
- Density comparison across transforms requires the Jacobian so likelihoods share the raw-R scale. pomegranate's LogNormal is a density over log R too, so it needs the same correction; afterwards Normal(log R) and LogNormal(R) tie exactly.
- A lead smaller than the fold-to-fold or seed-to-seed spread is not a ranking.
- Prefer stable OOS predictive density and non-collapsed interpretable states over balanced occupancy.
- A near-zero sequence-order premium means transitions add little beyond marginal mixture partitioning.
- Transfer concerns meanings and qualitative relationships, not identical percentages.

</details>

## Locked in

> Choose an emission family for stable chronological predictive density and interpretable causal states—not for pleasing occupancy.

## Do not conclude

Cross-symbol reproduction on two markets is introductory robustness, not universal validity.


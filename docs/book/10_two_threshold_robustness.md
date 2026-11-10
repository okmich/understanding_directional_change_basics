# Chapter 10 — Two-threshold robustness

## Purpose

Decide which two-clock insights are structural and which are artifacts of one symbol or threshold pair.

## Reproduction contract

Repeat the entire sequence on another market and predeclared pairs such as 15/30, 20/40, and 25/50 basis points. Keep definitions, event genealogy, exclusions, plots, and interpretation questions fixed.

Changing absolute thresholds changes event frequency, duration, sample size, and the market movement considered meaningful. Changing the ratio changes how difficult it is for a lower-scale contest to reach the upper scale. Exact propagation rates should change; the semantic distinctions should not.

Each comparison should change one thing. The earlier labs did not: Chapters 6–7 used EURUSD at 20/40 basis points and Chapters 8–9 used USDJPY at 25/50, so a difference between them mixes market and threshold. The robustness grid separates the two.

## The propagation rate is mostly arithmetic

Between two consecutive large DCCs the small clock fires an odd number $n$ of times (nesting parity, Chapter 7). Those firings alternate seed, rejection, …, seed, and the last seed propagates. Each large interval therefore holds $(n+1)/2$ attempts and exactly one propagation. Summing over intervals:

$$\text{propagation rate} \approx \frac{N_L}{(N_S+N_L)/2} = \frac{2}{N_S/N_L + 1},$$

where $N_S$ and $N_L$ are the completed-event counts. The only slack comes from the sample edges and from rare parity exceptions, so the identity is usually exact for the all-resolved rate.

Two consequences follow. A propagation rate is not a separate behavioural fact about the market; it is fixed by how many events each clock produces. And because the event-count ratio $N_S/N_L$ moves mainly with the threshold **ratio**, a change of ratio moves the rate far more than a change of absolute scale at a fixed ratio.

## What must survive

Look for recurrence of these conclusions:

- the two clocks remain independently causal;
- initiation geometry overlaps across outcomes;
- propagation and rejection become known only at their resolving DCC;
- live development can add diagnostic separation after initiation;
- later checkpoints are survival-conditioned;
- same-bar, ambiguous, unresolved, and inadequate cases remain explicit.

Do not rank threshold pairs by an attractive ex-post propagation rate. A threshold ladder is part of the research specification.

## Separating information from survivor selection

"Progress separates outcomes better at 20 bars than at the seed" can mean two different things:

- watching the path revealed information;
- the cohort changed, because quickly resolved attempts left it.

To tell them apart, hold the cohort fixed: take the attempts that survive to 20 bars and compare their progress measured at 20 bars with **the same attempts'** progress measured at their seed. Only the difference within that fixed cohort is information gained by waiting.

## Lab

Run [2_threshold_dc_robustness.ipynb](../../2_threshold_dc_robustness.ipynb). It predeclares eight cases on one common calendar window:

- USDJPY and EURUSD at 15/30, 20/40 and 25/50 basis points;
- each symbol at 20/30 as a ratio contrast (1.5 instead of 2).

The notebook groups them into three one-variable comparisons (symbol, absolute scale, ratio) and refuses a grouping that changes two things at once.

For every case it records symbol, interval, sampling frequency, pair, event counts, episode counts, and every exclusion before any percentage:

- same-bar propagations;
- ambiguous and unresolved (right-censored) episodes;
- nesting-parity exceptions.

It then reports:

- the event-count arithmetic;
- initiation overlap;
- fixed-cohort live development;
- direction and calendar-third strata;
- an interpretation matrix.

## Mandatory exercises

1. Separate conclusions that remained true from numbers that changed.
2. Explain how absolute scale differs from threshold ratio.
3. Identify any result concentrated in one direction or period.
4. Explain why a sparse case cannot confirm or refute a relationship reliably.
5. State why structural recurrence is not evidence of net trading profitability.
6. Use the event-count identity to explain which comparison moved the propagation rate most, and why.
7. For one case, show from the fixed-cohort columns whether the 20-bar separation is information gained by waiting or a change of cohort.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- Absolute thresholds change the size of every clock; ratios change the relative propagation hurdle.
- Structural semantics should recur while event counts, durations, and rates change.
- With nesting parity, each large interval holds one propagation and $(n+1)/2$ attempts, so the all-resolved rate is about $2/(N_S/N_L+1)$. The rate follows the event-count ratio, which follows the threshold ratio, so the 20/30 vs 20/40 comparison moves it far more than 15/30 vs 25/50.
- Fixed-cohort comparison: the same 20-bar survivors measured at their seed show how much of the 20-bar separation is information rather than a change of cohort.
- Same-bar (propagation only), ambiguous, unresolved, and parity-exception counts are reported before any rate.
- Weak sample size, direction concentration, and period concentration must be reported.
- Reproduction is neither threshold optimization nor profitability evidence.

</details>

## Locked in

> Robustness means the causal interpretation recurs under predeclared changes; it does not require identical frequencies or probabilities.

## Do not conclude

This is structural reproduction, not an optimized threshold selection exercise and not untouched out-of-sample confirmation.

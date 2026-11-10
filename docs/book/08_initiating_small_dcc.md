# Chapter 8 — The initiating small DCC

## Purpose

Separate what the initiating small DCC reveals about the past from what it begins in the present.

## Two meanings at one timestamp

At a small downward DCC:

- the completed small **up leg** and its TMV, T, and R become known;
- the new live small mode becomes **down**.

At an upward DCC, the completed small down leg becomes known and the new live mode becomes up.

The completed values belong to the leg that ended. They do not measure the new counter-move. This semantic distinction is the center of [2_threshold_dc_event_characteristics.ipynb](../../2_threshold_dc_event_characteristics.ipynb).

**Lab settings change here.** Chapters 6 and 7 use EURUSD at 0.20% / 0.40% ([2_threshold_dc.ipynb](../../2_threshold_dc.ipynb)); this chapter's lab uses USDJPY at 0.25% / 0.50%. The change is deliberate: the initiation semantics must not depend on one market or pair, so meeting them again on a second market is a first, informal reproduction. The cost is that the two notebooks change symbol and pair at once. Do not attribute a numerical difference between them to either change alone. Chapter 10 separates the two with a predeclared grid on a common window.

## Causal initiation table

At the seed, attach:

- prior and new small mode;
- causal large mode;
- completed small-leg TMV, T, and R;
- live unfinished large-scale context;
- event and information IDs.

Attach propagated/rejected only as a later diagnostic label with its own resolution time.

## What the evidence can show

Compare initiation features for later propagated and rejected attempts. Heavy overlap means the prior completed leg does not uniquely determine the future contest. A difference in R must be decomposed into TMV and T because $R=\mathrm{TMV}\theta/T$.

Nearest cross-outcome pairs are especially instructive: nearly identical causal initiation geometry can lead to opposite resolutions.

## Mandatory exercises

1. At one seed, identify every field that belongs to the completed prior leg.
2. Identify every field that belongs to the new live attempt.
3. Explain the reset semantics when the large DCC occurs on the same bar.
4. Compare propagated and rejected distributions and describe their overlap, not only their means.
5. Find a nearest opposite-outcome pair and explain why it defeats a deterministic initiation rule.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- The seed reveals the completed prior leg and begins the new opposing mode simultaneously.
- Completed prior-leg TMV/T/R do not measure the new counter-leg.
- Large live context is unfinished and must not be mislabeled completed R.
- Heavy outcome overlap and nearest opposite-outcome pairs reject a deterministic initiation rule.
- This lab (USDJPY 25/50) changes both market and pair relative to Chapters 6–7 (EURUSD 20/40); a numerical difference between them cannot be attributed to either alone.

</details>

## Locked in

> The initiating DCC reveals the prior leg and starts the opposing mode at the same timestamp; those are different objects.

## Do not conclude

Outcome-conditioned initiation statistics are diagnostic. They are not a live probability model and cannot make the outcome causal before resolution.


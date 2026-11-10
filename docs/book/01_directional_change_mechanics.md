# Chapter 1 — Directional-change mechanics

## Purpose

Learn to see the event before learning any model. At one threshold, Directional Change turns a price path into alternating confirmed modes.

## Street explanation

While the process is in up mode, it keeps replacing its candidate peak whenever price rises. The peak is not final while this continues. A fall of $\theta$ from the running peak produces a **downward DCC**. That bar does two things at once:

1. retrospectively confirms the peak and the completed upward leg;
2. switches the live mode to down.

The mirror image holds in down mode: keep replacing the candidate trough until a rise of $\theta$ confirms it through an upward DCC and switches the live mode up.

This resolves the apparent paradox: a downward DCC is evidence that an upward leg ended, but it is also the start of the confirmed down mode.

## Close-bar limitation

The DCC marker is the first sampled close satisfying the threshold. Price may have crossed the threshold earlier inside the bar. With close-only data, that intrabar time and any ordering among multiple same-bar confirmations are unknown.

## Lab

Run [1_threshold_dc_explore.ipynb](../../1_threshold_dc_explore.ipynb).

Read the chart in this order:

1. Find a DCC triangle.
2. Locate the prior confirmed extreme and the newly confirmed extreme.
3. Name the completed leg.
4. Name the new live mode.
5. Check the exact threshold condition against the close prices.

The ledger states steps 3 and 4 explicitly: `direction` (also `completed_leg_direction`) is the leg that ended, and `dcc_direction` / `new_live_mode` is the direction of the confirmation and the mode that is live from `information_time` on. They are always opposite.

Inspect at least one event whose two extremes occur on consecutive bars. This is a useful stress case: $T=1$ describes the extreme-to-extreme leg, not necessarily a single bar from extreme to DCC.

## Mandatory exercises

1. Explain a downward DCC without using the word “bearish.”
2. On three selected events, reconstruct the running extreme and confirmation condition by hand.
3. Explain why the ending extreme is retrospective but the mode after the DCC is causal.
4. State what becomes ambiguous when more than one threshold confirms on the same close bar.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- A downward DCC is the first sampled close at least $\theta$ below the running peak; it confirms the peak and switches mode down.
- An upward DCC is the symmetric rise from the running trough.
- The ending extreme is retrospective; the new mode is causal at the DCC close.
- Same-bar multi-threshold order is unknowable from close-only data.

</details>

## Locked in

> A downward DCC confirms the prior peak and changes the live mode down; an upward DCC confirms the prior trough and changes the live mode up.

## Do not conclude

A DCC confirms a reversal of size $\theta$ from an extreme. It does not promise continuation, profitability, or a final economic regime.


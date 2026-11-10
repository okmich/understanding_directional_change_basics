# Chapter 4 — What an HMM state means economically

## Purpose

Move from colored states to a defensible economic sentence. The seven audits test whether the label describes current event geometry, sequence history, or later behavior.

## Reading the audits

Run the HMM coherence audits in [1_threshold_dc.ipynb](../../../1_threshold_dc.ipynb).

1. **Log-R distributions:** confirm what emission values the states tend to occupy.
2. **TMV–T space:** remember that constant R follows $\mathrm{TMV}=RT/\theta$; state separation may reflect size, duration, or both.
3. **Observation versus posterior:** inspect how current log-R and the previous belief combine.
4. **Event sequence:** look for persistence and switching in event order.
5. **Nearest opposite assignments:** find similar observations assigned differently because their histories differ.
6. **Next-event audit:** test whether the current state contains forward separation beyond current log-R. Use chronological OOS calibration, log loss, Brier score, and AUC as diagnostics. Audit 6 targets the HMM's own next label, which is computed from the current filtered probability, so adding `p_fast_r` helps there by construction. **Audit 6b** repeats the test on model-free targets—next log R, and whether the next R exceeds the training median—and is the evidence for any forward claim.
7. **Recent casebook:** read actual price paths at the DCC where the state becomes known.

## The correct market sentence

At a current DCC:

> The prior up/down leg completed with slow/fast normalized velocity; the opposite DCC has now put the process into down/up mode.

The state describes the completed leg, while the mode describes what is live. The next extreme, DCC, TMV, T, R, and state are unknown.

If Audit 6 shows little incremental forward information, that is still a useful conclusion: the HMM is a descriptive event-state compressor rather than a next-event forecaster.

## Mandatory exercises

1. Find two nearby log-R observations with different hard states and explain the Markov contribution.
2. For one recent event, separate every known field from every future field.
3. Explain why a visually fast price segment can retain a `slow_R` state.
4. State whether the fitted state predicts the next event, using only OOS evidence from the model-free Audit 6b, and explain why Audit 6 alone cannot settle it.
5. Explain why state persistence is not equivalent to economic usefulness.

## Locked in

> A state label belongs to a fitted sequential model. Its economic meaning comes from the completed-event geometry and history it summarizes, not from its color or name.

## Do not conclude

Do not retrofit a directional story to the state. Direction comes from the live DC mode; the HMM state here summarizes completed normalized velocity.


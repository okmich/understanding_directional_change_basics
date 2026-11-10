# Chapter 6 — Two independent clocks

## Purpose

Place a small and a large threshold on the same price path without treating one as a derivative of the other.

## Core idea

Each threshold owns its own running extreme, mode, DCC sequence, completed-event ledger, and live TMV/T/R clock. The small clock almost always changes first, and it changes more often, because a smaller reversal is sufficient to confirm it. The large clock ignores many of those reversals.

"Small confirms first" is a near-invariant, not a guarantee. The thresholds are multiplicative and each is measured from its own running extreme, so on rare paths the large clock confirms a reversal while the small clock still points the other way. The relative window is roughly the square of the small threshold. `find_upper_led_reversals` in `dc_basics.hierarchy` lists such cases instead of hiding them.

The four ordered mode combinations are:

| Small | Large | Current structural reading |
|---|---|---|
| up | up | upward agreement |
| down | up | small downward counter-move inside large up mode |
| down | down | downward agreement |
| up | down | small upward counter-move inside large down mode |

These are current causal states. They do not say what the next event will be.

## Information timing

A small DCC can change only the small component. A large DCC can change the large component and may occur on the same sampled bar as a small confirmation. Close-only data reveals the final same-bar configuration but not the intrabar order.

## Lab

Run [2_threshold_dc.ipynb](../2_threshold_dc.ipynb) through “Audit 2.”

Verify the event/live semantic contract separately at both scales. Then compare:

- completed-event geometry across thresholds;
- the two overlaid event ledgers;
- occupancy of the four configurations;
- the number of small DCCs inside one large interval.

## Mandatory exercises

1. Explain why the two clocks are independent although their prices are identical.
2. Find one small DCC that the large clock ignores and say exactly why.
3. Read all four configurations without using future price action.
4. Explain why occupancy is a share of bars, not a propagation probability.
5. Identify one same-bar transition and state what cannot be recovered from close data.

## Completion gate

This chapter's phase closes with [gate G4 — Two-threshold mechanics](07_agreement_propagation_rejection.md#completion-gate-g4--two-threshold-mechanics) at the end of Chapter 7. Answer it once you have finished that chapter.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- Every threshold independently tracks its extreme and confirmations.
- Small/large disagreement is a current counter-scale state, not a large-scale reversal.
- Configuration occupancy is duration-weighted bar share.
- A small DCC ignored by the large scale has not reversed far enough from the large running extreme.
- "Small confirms first" is a near-invariant. Each threshold is relative to its own running extreme, so the large clock can rarely confirm first; `find_upper_led_reversals` lists those bars.

</details>

## Locked in

> Two thresholds are two observers with different definitions of a meaningful reversal; they share a path but not a clock.

## Do not conclude

Small/large disagreement is not yet a large reversal. It is a live counter-scale contest.


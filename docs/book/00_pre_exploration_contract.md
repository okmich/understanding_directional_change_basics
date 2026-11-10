# Chapter 0 — The pre-exploration contract

## Purpose

Before calculating a single event, decide how knowledge enters the system. A price extreme is visible on a completed chart long before it was identifiable in real time. Directional Change is useful precisely because it gives that extreme a confirmation event. Ignoring the distinction destroys the causal meaning of every later result.

## Core idea

Each derived object needs two identities:

- an **event ID**, answering which event or lineage the value belongs to;
- an **information time**, answering the first bar on which the value was knowable.

An extreme's timestamp is not automatically its information time. A peak becomes confirmed only after price reverses downward by the threshold; a trough becomes confirmed only after price reverses upward by the threshold.

Completed and live values must remain separate. Completed TMV, T, and R describe the leg that ended at the confirmed extreme. Live values describe the current unfinished leg from the latest confirmed extreme to the current bar.

## Causal ledger

For every completed event, retain at least:

```text
event_id, threshold, direction,
ext_start_time, ext_end_time,
dcc_confirmation_time, information_time,
TMV, T, R
```

For every live row, retain its observation time, active event or lineage ID, current measurements, and separate future outcome-information time. Never backward-fill the outcome into the live row.

## Lab

Read the [root causality contract](../../README.md#causality-contract) and the manifest's [causality and evaluation rules](../TEXTBOOK_MANIFEST.md#13-causality-and-evaluation-rules), then inspect the event schemas in `dc_basics/events.py` and the timing tests in `tests/test_core.py`.

## Mandatory exercises

1. Draw a peak at bar 10 and its downward DCC at bar 14. Which timestamp belongs to the extreme, and which is its information time?
2. Explain why calculating an event statistic after bar 14 does not permit using it at bar 10.
3. Give one valid use and one invalid use of a future propagated/rejected label.
4. Explain why event IDs are necessary even when timestamps appear unique.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- An extreme has an occurrence time; its completed-event statistics have the later DCC information time.
- Post-confirmation calculation does not authorize backdating.
- Future outcomes may group rows diagnostically but may not enter causal features.
- Event IDs preserve identity across same timestamps, thresholds, hand-offs, and repeated joins.

</details>

## Locked in

> A value is causal only when every input was knowable at its declared information time.

## Do not conclude

Causal construction does not make a feature predictive. It only makes a later predictive test logically valid.


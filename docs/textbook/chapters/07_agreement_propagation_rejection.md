# Chapter 7 — Agreement, propagation, and rejection

## Purpose

Turn a two-clock disagreement into a precisely resolved structural question.

## The contest

Begin with both modes aligned. An opposite small DCC starts a counter-scale attempt. From that initiating bar, two clocks compete:

- **Propagation:** the large clock confirms a DCC in the small target direction before the small clock reverses.
- **Rejection:** the small clock reverses back toward the large origin direction first.

Until one of those DCCs occurs, the attempt is unresolved. The outcome is a future label even though the disagreement itself is causally observable.

## Nesting and parity

Small events alternate direction. Between suitable large-scale boundaries, an odd small-event count reflects the final small confirmation that aligns with the large transition; preceding pairs encode attempts that reversed before reaching the large scale. Check the interval definition before asserting parity, because initialization, truncation, same-bar events, and unresolved boundaries can invalidate a naive count.

Odd parity is a near-invariant under multiplicative thresholds, not a law. If the large clock confirms a reversal before the small clock (Chapter 6), that interval holds an even small count and the large reversal belongs to no small attempt. The library keeps such intervals, flags them with `parity_violation` and counts them in an audit; it does not assert them away. On the repository's data they are rare, but a synthetic ten-bar path in `tests/test_hierarchy.py` shows one.

## Resolution bar

The exact propagating large DCC or rejecting small DCC is the first bar on which the outcome becomes factual. A live feature panel must stop on the preceding bar.

Two same-bar cases need explicit and different treatment:

- **Same-bar (zero-length) propagation:** the initiating small DCC and the large DCC that joins it fire on one bar. It is a resolved propagation with zero bars and no unresolved interval.
- **Ambiguous resolution:** an active attempt sees an opposing small DCC and a propagating large DCC on one bar. Close-only data cannot order them, so the outcome stays `ambiguous_same_bar`.

A rejection always needs a later small DCC, so it can never take zero bars.

## Lab

Run “Audit 3” and “Audit 4” in [2_threshold_dc.ipynb](../../../2_threshold_dc.ipynb).

For each casebook path, answer:

1. What were the modes before the seed?
2. Which small DCC initiated opposition?
3. What remained unchanged at the large scale?
4. Which exact later DCC resolved the contest?

## Mandatory exercises

1. Define propagation and rejection without referring to a price chart's final appearance.
2. Explain why `propagated` is hindsight on every unresolved bar.
3. Reconstruct one rejected pair inside a large interval.
4. Explain why the propagation rate is conditional on the declared attempt cohort.
5. Identify an ambiguous or same-bar case and explain why it cannot be silently assigned.

## Locked in

> Small opposition is observable now; propagation or rejection becomes known only when one of the two competing clocks confirms first.

## Do not conclude

Propagation to the large mode confirms scale reach. It does not forecast continuation after the large DCC.


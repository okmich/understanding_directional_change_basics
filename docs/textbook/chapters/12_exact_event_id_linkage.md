# Chapter 12 — Exact event-ID linkage

## Purpose

Join the two adjacent contests into one genealogy rooted in a single small DCC.

## Root and hand-off

A clean root begins when all three modes were aligned on the previous bar and a small DCC creates opposition. The initiating small event ID remains the lineage ID forever.

If Stage 1 propagates, its resolving medium DCC must be the exact medium event that initiates Stage 2. Link by event-ID equality, direction, timestamp, and prior mode—not by nearest time. The medium ID is a hand-off key, not a new lineage root.

## Depth

For three thresholds:

- depth 0: rejected before medium confirmation;
- depth 1: medium confirmed, then the medium-to-large contest rejected;
- depth 2: large confirmed in the target direction.

Terminal depth is hindsight until the lineage ends. Attained depth is causal: once medium confirms, depth 1 is factual even while the terminal result remains unknown.

## Conditional probability ladder

For one consistent root cohort:

$$
P(D\ge2)=P(D\ge1)P(D\ge2\mid D\ge1).
$$

This is the chain rule, not an independence assumption. Because $D\ge2$ implies $D\ge1$, the identity holds by arithmetic in any cohort; it is a definition to understand, not a test to pass.

Only medium events descended from the declared small roots enter the linked second-stage cohort, so in general the linked rate need not equal the unconditional medium-to-large rate. With three scales and broad-agreement roots, however, the two cohorts are essentially identical. A medium DCC against large is almost always preceded by a small DCC that left three-scale agreement and propagated through that medium DCC, so almost every medium-to-large attempt is linked, and the notebook shows the two rows coinciding. The rates can differ under a narrower root (four-scale agreement in Chapter 16), under a lineage filter such as strict-clean, or at deeper hand-offs.

## Lab

Run [3_threshold_dc_linkage.ipynb](../../../3_threshold_dc_linkage.ipynb).

Audit exact keys, exclusions, linked probabilities for the all-resolved and strict-clean cohorts, nested small activity, direction/period stability, and one case at each terminal depth.

## Mandatory exercises

1. Explain why timestamp proximity can create a false genealogy.
2. Trace one depth-2 lineage through both exact event IDs.
3. State the bar on which each depth becomes attained and terminal.
4. Derive the probability product without saying “independent,” and explain why the linked and unconditional medium-to-large rates coincide in this notebook.
5. Explain why a linked lineage need not be one monotonic price leg.

## Locked in

> Linkage is a genealogy of exact confirmations: one immutable small seed, one exact hand-off, and a terminal depth known only at resolution.

## Do not conclude

Linked transition frequencies describe the hierarchy. They do not establish a forecast or trading edge.


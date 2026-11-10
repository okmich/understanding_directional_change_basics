# Chapter 19 — Reading the 32 configurations

## Purpose

Read the complete five-mode vector without reducing it prematurely to one label.

## State space

Five binary clocks create $2^5=32$ possible ordered configurations `(small, medium, large, macro, outer)`.

The same shape logic now has more resolution:

- all modes equal: broad agreement;
- exactly one boundary: a coherent propagation frontier;
- two or more boundaries: fragmentation;
- the location of the single boundary: current coherent counter depth;
- number matching outer: outer agreement breadth.

In the notebooks the boolean `coherent_frontier` means **at most one** boundary, so it includes broad agreement as a frontier of depth 0. `one_boundary_share` isolates the single-boundary states, and fragmented is everything else. Read `coherent_frontier_share` as broad agreement plus one boundary, not as one boundary alone.

Agreement breadth alone loses order. `down/down/up/up/up` and `down/up/down/up/up` can have the same number of modes matching outer, yet the first has one coherent frontier and the second is fragmented.

The 32 states need not have equal occupancy. Market persistence, threshold geometry, and bar-time weighting make some configurations common and others rare or absent.

## Causal transition reading

Each component changes only when its own DCC occurs. Multiple changes on one close are causal at that close, but their intrabar ordering is unknown. A completed event's TMV/T/R is available at its DCC; the later propagated/rejected outcome of an adjacent contest remains hindsight until resolution.

Adjacent nesting parity (an odd number of lower DCCs inside each upper interval) is a near-invariant, not a law. Under multiplicative thresholds the upper clock can, rarely, confirm first. The nesting table therefore counts parity violations instead of assuming there are none.

## Lab

Continue [5_threshold_dc.ipynb](../../../5_threshold_dc.ipynb) through configuration occupancy, ribbons, transition integrity, adjacent contests, nesting, and grid-divergence casebooks.

## Mandatory exercises

1. Derive why there are 32 configurations.
2. Read five selected vectors aloud in scale order.
3. For each, calculate agreement breadth and boundary count.
4. Explain why fragmentation cannot receive one valid coherent depth.
5. Find the notebook case where the two grids give different causal shapes and explain both readings.
6. Identify the exact DCC changing one component.

## Locked in

> The ordered mode vector is the lossless structural state; breadth, depth, and fragmentation are summaries of it.

## Do not conclude

Rare occupancy is not evidence that a valid configuration should be deleted, nor is common occupancy proof of economic usefulness.


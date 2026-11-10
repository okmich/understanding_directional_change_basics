# Chapter 23 — A causal representation for N thresholds

## Purpose

Replace threshold-specific notebook logic with one representation that means the same thing for any ordered ladder.

## Four layers

[multiscale_representation_design.ipynb](../../../multiscale_representation_design.ipynb) builds four layers.

### 1. Scale state

One causal row per time and threshold retains threshold identity, mode, mode age, DCC flags and event ID, live TMV/T/R, completed TMV/T/R with their information time, running extreme, reversal progress, and recent firing activity.

### 2. Adjacent edges

For $N$ thresholds there are exactly $N-1$ adjacent relationships. Each edge records current agreement or disagreement. Propagation and rejection are later outcomes, not edge-state fields.

### 3. Whole hierarchy

Retain the complete ordered mode vector plus summaries such as configuration code, broad agreement, coherent frontier, direction boundaries, fragmentation, contiguous breadth, signed balance, ages, progress, and hierarchy firing rate.

### 4. Optional lineage context

An active broad-root lineage may add immutable seed, active stage, attained depth, and causal live progress. Final resolutions remain in a separate diagnostic table.

## Losslessness and clocks

The ordered mode vector must remain even when summaries exist. Fragmentation cannot be reconstructed from one depth number. Threshold values and adjacent ratios belong to the representation contract.

Bar time weights duration. Union-event time samples only bars on which at least one DCC occurs. They produce different populations and different transition meanings.

## Causal rules

- Current and completed TMV/T/R must not share ambiguous names.
- Leg excursion differs from reversal progress.
- Resolution bars are absent from resolving live stages.
- Same-bar order is ambiguous with close-only data.
- No full-sample normalization belongs in deployable features.
- `lineage_resolutions` must never be backward-joined into `lineage_state`.

## Mandatory exercises

1. Derive the $N$ node and $N-1$ edge counts.
2. Reconstruct one full mode vector from its scale-state rows.
3. Show two fragmented vectors that a single depth summary cannot distinguish.
4. Compare bar-time and union-event-time occupancy.
5. Run the identity and provenance checks for two through five thresholds.
6. Run the parity check that compares the notebook's explicit builders with `dc_multiscale_research.build_multiscale_state`, and explain why a representation needs exactly one implementation once later phases depend on it.

## Locked in

> The canonical representation retains causal node states, adjacent edges, the lossless ordered hierarchy, and optional live lineage context—never future resolutions.

## Do not conclude

A rich causal representation is not automatically a useful regime model. It is the substrate against which models must earn their complexity.


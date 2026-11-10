# Chapter 23 — A causal representation for N thresholds

## Purpose

Replace threshold-specific notebook logic with one representation that means the same thing for any ordered ladder.

## Four layers

[multiscale_representation_design.ipynb](../multiscale_representation_design.ipynb) builds four layers.

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

## Completion gate G19 — Arbitrary-N causal representation

Before fitting a regime classifier, the learner must be able to:

1. Explain why `scale_state` is the canonical arbitrary-N node representation.
2. Derive exactly `N - 1` adjacent edge states for `N` thresholds.
3. Retain the ordered mode vector even when breadth and fragmentation summaries exist.
4. Include threshold values and adjacent ratios in the representation contract.
5. Distinguish current-leg from completed-leg TMV/T/R and leg excursion from reversal progress.
6. Distinguish current adjacent disagreement from later propagation or rejection.
7. Keep attained depth causal and terminal depth diagnostic until resolution.
8. Exclude the resolution bar and mark same-bar transitions ambiguous under close-only observation.
9. Explain why bar time and union-event time produce different populations.
10. Exclude full-sample normalization from a deployable representation.
11. Explain why fragmented states cannot be reduced faithfully to one propagation-depth number.
12. Pass the same construction and identity checks for two through five thresholds.
13. Keep `lineage_resolutions` diagnostic and never backward-join it into `lineage_state`.
14. Show that the notebook's explicit builders and `dc_multiscale_research.build_multiscale_state` produce identical shared columns, so the representation has one implementation.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- $N$ thresholds create $N$ scale nodes and $N-1$ adjacent edges.
- The scale state separates live and completed clocks and timestamps.
- The full ordered vector must remain because summaries cannot reconstruct fragmented shape.
- Bar time weights duration; union-event time weights event-bearing observations.
- Diagnostic resolutions must never be backward-joined to causal lineage rows.
- The notebook's explicit builders must match `dc_multiscale_research.build_multiscale_state` on every shared column; two drifting implementations would make later phases study a different object.

</details>

## Locked in

> The canonical representation retains causal node states, adjacent edges, the lossless ordered hierarchy, and optional live lineage context—never future resolutions.

## Do not conclude

A rich causal representation is not automatically a useful regime model. It is the substrate against which models must earn their complexity.


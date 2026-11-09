# Directional-change basics package

This package is the reusable spine beneath the chronological notebooks. The
notebooks retain the reasoning, audits, and scale-specific demonstrations; this
package owns mechanics that should have one implementation.

## Boundaries

- `core/`: vendored single- and dual-threshold parsing plus causal live features.
- `events.py`: stable event IDs, information timestamps, and TMV/T/R invariants.
- `hierarchy.py`: adjacent-scale propagation/rejection contests and nesting counts.
- `lineage.py`: exact event-ID hand-offs and arbitrary-depth small-origin lineages.
- `live.py`: causal running extremes and live progress toward a target DCC.
- `live_panel.py`: stage-normalized, pre-resolution causal feature panels.
- `two_scale.py`: pinned two-threshold disagreement episodes and causal paths.
- `configuration.py`: arbitrary-N mode-vector structure classification.
- `audit.py`: reusable timing, outcome-hindsight, stage-count, and identity gates.
- `plotting.py` and `live_plotting.py`: reusable price, event, HMM, hierarchy,
  and live-trajectory charts.
- `data.py`: close loading, resampling, and threshold-ladder construction.
- `hmm/`: the optional vendored pomegranate HMM wrapper used in the single-scale
  and probabilistic-regime notebooks.

`dc_multiscale_research.py` remains the compatibility facade for phases 20-24.
Its data/grid plumbing now delegates here, while its representation and model
contracts remain stable for the already-run notebooks.

Scale-specific interpretation tables and casebook selection remain in the
chronological notebooks. Stable lineage and live-panel mechanics are shared;
the notebooks still show how each scale count changes the economic questions.

## Causality contract

- A completed event's TMV, T, and R are available at its `dcc_idx` only.
- Live features use the price path through the current bar only.
- Propagated/rejected outcomes are diagnostic hindsight until their recorded
  `resolution_time`.
- A same-bar lower/upper resolution is retained as ambiguous on close-only data.

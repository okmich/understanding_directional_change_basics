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
- `live_panel.py`: stage-normalized, pre-resolution causal feature panels. Rows carry `lineage_age_bars` and activity on the clocks below the stage's lower clock (`sub_lower_*`). Pass `LivePanelContext.event_ledgers` to join the completed seed-leg and stage-start-leg TMV/T/R by exact event ID. `constant_by_construction_features`, `summarize_checkpoint_overlap` (minimum class count before any AUC), `auc_table_with_counts` and `compare_initiation_and_live_features` are the shared evaluation helpers.
- `hmm_support.py`: local HMM additions outside the vendored files (seeded LogNormal initialisation, raw-R predictive score with its Jacobian, shared `fast_R`/`slow_R` labelling, thread pinning). Imported explicitly because it needs torch.
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
- Two different same-bar cases exist and must not be conflated:
  - *same-bar (zero-length) propagation*: the seed lower DCC and the upper DCC
    that joins it fire on one bar. The attempt is `propagated` with
    `resolution_bars == 0`; its outcome is known on the seed bar, so it has no
    live interval.
  - *ambiguous*: an already active attempt sees opposing lower and upper DCCs
    on one bar (`ambiguous_same_bar`). Close-only data cannot order them, so
    the attempt keeps that explicit outcome and its lineage has no terminal
    depth.
- `strict_clean` lineages exclude every zero-length stage. Because a zero-length
  stage can only be a propagation, strict-clean reach rates are biased low;
  `resolved_lineage` is the unbiased cohort for probability ladders.
- "The smaller clock confirms first" and "an odd number of lower DCCs lies
  between consecutive upper DCCs" are near-invariants, not guarantees. With
  multiplicative thresholds the upper clock can occasionally confirm first.
  `find_upper_led_reversals` lists such reversals, and `build_nesting_intervals`
  flags them with `parity_violation` instead of raising.
- All lineage entry points share one implementation (`build_lineage_tables`):
  terminal depth is defined only for resolved lineages, and ambiguous,
  unresolved and unlinked lineages keep `max_attained_depth` instead.

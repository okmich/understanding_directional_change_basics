"""Self-contained directional-change research building blocks.

The public API is deliberately split between the lightweight directional-change
core and the optional HMM layer. Importing :mod:`dc_basics` therefore does not
require PyTorch or pomegranate unless the HMM API is explicitly requested.
"""

from .core import dc_live_features, log_r, normalise_minmax, parse_dc_events, parse_dual_dc
from .data import load_close, ratio_ladder, resolve_data_root, threshold_catalog, validate_thresholds
from .enums import AttemptOutcome, DcMode
from .events import prepare_event_ledger, prepare_threshold_event_ledger
from .hierarchy import (
    build_adjacent_attempts,
    build_nesting_intervals,
    find_upper_led_reversals,
    summarize_nesting_parity,
)
from .lineage import (
    build_five_scale_linkages,
    build_four_scale_linkages,
    build_lineage_tables,
    build_scale_linkages,
    build_three_scale_linkages,
    build_wide_stage_table,
)
from .live import build_causal_running_extreme, calculate_target_progress
from .live_panel import (
    LivePanelContext,
    auc_table_with_counts,
    build_live_panel,
    build_live_stage_part,
    compare_initiation_and_live_features,
    constant_by_construction_features,
    summarize_checkpoint_overlap,
)
from .two_scale import build_counter_scale_trajectory_panel, build_disagreement_episodes

__all__ = [
    "dc_live_features",
    "AttemptOutcome",
    "DcMode",
    "LivePanelContext",
    "auc_table_with_counts",
    "build_adjacent_attempts",
    "build_causal_running_extreme",
    "build_counter_scale_trajectory_panel",
    "build_disagreement_episodes",
    "build_five_scale_linkages",
    "build_four_scale_linkages",
    "build_lineage_tables",
    "build_live_panel",
    "build_live_stage_part",
    "build_nesting_intervals",
    "build_scale_linkages",
    "build_three_scale_linkages",
    "build_wide_stage_table",
    "calculate_target_progress",
    "compare_initiation_and_live_features",
    "constant_by_construction_features",
    "find_upper_led_reversals",
    "load_close",
    "log_r",
    "normalise_minmax",
    "parse_dc_events",
    "parse_dual_dc",
    "prepare_event_ledger",
    "prepare_threshold_event_ledger",
    "ratio_ladder",
    "resolve_data_root",
    "summarize_checkpoint_overlap",
    "summarize_nesting_parity",
    "threshold_catalog",
    "validate_thresholds",
]

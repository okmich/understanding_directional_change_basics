"""Reusable plots for causal live-development panels."""

from collections.abc import Mapping
from enum import Enum

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .events import enum_value


DEFAULT_TRAJECTORY_FEATURES = {
    "target_progress": "Progress toward upper DCC",
    "lower_r_live": "Live lower-scale R",
    "direction_boundaries": "Directional boundaries",
    "nested_lower_dcc_rate": "Nested lower-DCC rate",
}


def plot_stage_trajectories(panel: pd.DataFrame, stage: str | Enum, max_elapsed_bars: int, *, symbol: str,
                            features: Mapping[str, str] = DEFAULT_TRAJECTORY_FEATURES) -> go.Figure:
    """Plot survivor-conditioned median paths by hindsight outcome and target mode."""
    stage_name = enum_value(stage)
    selected = panel.loc[
        panel["stage"].eq(stage_name) & panel["elapsed_bars"].le(max_elapsed_bars)
    ].copy()
    summary = selected.groupby(
        ["elapsed_bars", "future_stage_outcome", "target_mode"], sort=True
    ).agg(
        survivor_count=("lineage_id", "size"),
        **{f"{feature}_median": (feature, "median") for feature in features},
    ).reset_index()
    figure = make_subplots(rows=2, cols=2, subplot_titles=list(features.values()))
    colors = {"propagated": "#2563eb", "rejected": "#f97316"}
    dashes = {"up": "solid", "down": "dash"}
    for feature_number, (feature, label) in enumerate(features.items()):
        row_number = feature_number // 2 + 1
        column_number = feature_number % 2 + 1
        for (outcome, target_mode), group in summary.groupby(
            ["future_stage_outcome", "target_mode"], sort=True
        ):
            figure.add_trace(go.Scattergl(
                x=group["elapsed_bars"],
                y=group[f"{feature}_median"],
                mode="lines",
                name=f"{outcome} | target {target_mode}",
                legendgroup=f"{outcome}_{target_mode}",
                showlegend=feature_number == 0,
                line={"color": colors[outcome], "dash": dashes[target_mode], "width": 2},
                customdata=group[["survivor_count"]].to_numpy(),
                hovertemplate=(
                    "elapsed=%{x:.0f}<br>median=%{y:.4g}<br>"
                    "survivors=%{customdata[0]:,.0f}<extra></extra>"
                ),
            ), row=row_number, col=column_number)
        figure.update_xaxes(title_text="Elapsed bars", row=row_number, col=column_number)
        figure.update_yaxes(title_text=label, row=row_number, col=column_number)
        if feature == "target_progress":
            figure.add_hline(
                y=1.0,
                line={"color": "#64748b", "dash": "dot"},
                row=row_number,
                col=column_number,
            )
    figure.update_layout(
        title=f"{symbol}: {stage_name} causal paths — colour is hindsight outcome",
        template="plotly_white",
        height=820,
        hovermode="closest",
        legend={"orientation": "h", "y": 1.08, "x": 0.0},
    )
    return figure

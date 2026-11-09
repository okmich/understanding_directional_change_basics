"""Reusable Plotly charts for directional-change research."""

from enum import StrEnum

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class _Direction(StrEnum):
    UP = "up"
    DOWN = "down"


class _AttemptOutcome(StrEnum):
    PROPAGATED = "propagated"
    REJECTED = "rejected"


class _CrossScaleRelationship(StrEnum):
    AGREEMENT = "agreement"
    DISAGREEMENT = "disagreement"


_REQUIRED_EVENT_COLUMNS = {
    "event_id",
    "direction",
    "ext_start_idx",
    "ext_start_price",
    "ext_end_idx",
    "ext_end_price",
    "dcc_idx",
    "dcc_price",
    "information_time",
    "tmv",
    "t",
    "r",
}


def _add_segment_trace(fig: go.Figure, events: pd.DataFrame, direction: _Direction, color: str) -> None:
    """Add all extreme-to-extreme segments for one direction as one trace."""
    directional_events = events.loc[events["direction"] == direction]
    x_values: list[object] = []
    y_values: list[float | None] = []

    for event in directional_events.itertuples(index=False):
        x_values.extend([event.ext_start_idx, event.ext_end_idx, None])
        y_values.extend([event.ext_start_price, event.ext_end_price, None])

    if x_values:
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode="lines",
            name=f"{direction.value.title()} EXT-to-EXT",
            line={"color": color, "width": 2.5},
            hoverinfo="skip",
        ))


def _add_event_markers(fig: go.Figure, events: pd.DataFrame, direction: _Direction, window_start: pd.Timestamp,
                       window_end: pd.Timestamp) -> None:
    """Add ending-extreme and later confirmation markers for one completed-trend direction."""
    is_up = direction == _Direction.UP
    directional_events = events.loc[events["direction"] == direction]
    extreme_events = directional_events.loc[directional_events["ext_end_idx"].between(window_start, window_end)]
    confirmation_events = directional_events.loc[directional_events["dcc_idx"].between(window_start, window_end)]

    extreme_label = "Peak EXT" if is_up else "Trough EXT"
    extreme_color = "#f59e0b" if is_up else "#3b82f6"
    extreme_symbol = "diamond"
    confirmation_label = "Downward DCC" if is_up else "Upward DCC"
    confirmation_color = "#dc2626" if is_up else "#16a34a"
    confirmation_symbol = "triangle-down" if is_up else "triangle-up"

    if not extreme_events.empty:
        fig.add_trace(go.Scatter(
            x=extreme_events["ext_end_idx"],
            y=extreme_events["ext_end_price"],
            mode="markers",
            name=extreme_label,
            marker={"color": extreme_color, "size": 9, "symbol": extreme_symbol, "line": {"color": "white", "width": 1}},
            customdata=extreme_events[["event_id", "tmv", "t", "r", "information_time"]].to_numpy(),
            hovertemplate=(
                f"{extreme_label}<br>"
                "time=%{x}<br>price=%{y:.5f}<br>event=%{customdata[0]}<br>"
                "TMV=%{customdata[1]:.4f}<br>T=%{customdata[2]} bars<br>R=%{customdata[3]:.3e}<br>"
                "known at=%{customdata[4]}<extra></extra>"
            ),
        ))

    if not confirmation_events.empty:
        fig.add_trace(go.Scatter(
            x=confirmation_events["dcc_idx"],
            y=confirmation_events["dcc_price"],
            mode="markers",
            name=confirmation_label,
            marker={
                "color": confirmation_color,
                "size": 10,
                "symbol": confirmation_symbol,
                "line": {"color": "white", "width": 1},
            },
            customdata=confirmation_events[["event_id", "tmv", "t", "r", "ext_end_idx"]].to_numpy(),
            hovertemplate=(
                f"{confirmation_label}<br>"
                "time=%{x}<br>price=%{y:.5f}<br>event=%{customdata[0]}<br>"
                "TMV=%{customdata[1]:.4f}<br>T=%{customdata[2]} bars<br>R=%{customdata[3]:.3e}<br>"
                "confirmed EXT time=%{customdata[4]}<extra></extra>"
            ),
        ))


def plot_directional_change(prices: pd.Series, events: pd.DataFrame, n_prices: int = 2_000,
                            title: str | None = None) -> go.Figure:
    """Plot the last ``n_prices`` closes with completed directional-change events overlaid."""
    if n_prices <= 0:
        raise ValueError(f"n_prices must be positive, got {n_prices}.")
    if prices.empty:
        raise ValueError("prices must not be empty.")
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise TypeError("prices must use a DatetimeIndex.")
    if not prices.index.is_monotonic_increasing:
        raise ValueError("prices must be sorted chronologically.")

    missing_columns = _REQUIRED_EVENT_COLUMNS.difference(events.columns)
    if missing_columns:
        raise KeyError(f"events is missing required columns: {sorted(missing_columns)}")

    price_window = prices.tail(n_prices)
    window_start = price_window.index[0]
    window_end = price_window.index[-1]
    visible_events = events.loc[
        (events["ext_start_idx"] <= window_end) & (events["dcc_idx"] >= window_start)
    ].copy()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=price_window.index,
        y=price_window.to_numpy(),
        mode="lines",
        name="Close",
        line={"color": "#334155", "width": 1.25},
        hovertemplate="time=%{x}<br>close=%{y:.5f}<extra></extra>",
    ))

    _add_segment_trace(fig, visible_events, _Direction.UP, "#16a34a")
    _add_segment_trace(fig, visible_events, _Direction.DOWN, "#dc2626")
    _add_event_markers(fig, visible_events, _Direction.UP, window_start, window_end)
    _add_event_markers(fig, visible_events, _Direction.DOWN, window_start, window_end)

    chart_title = title or f"{prices.name or 'Close'}: completed directional-change events"
    fig.update_layout(
        title=f"{chart_title} — last {len(price_window):,} prices",
        template="plotly_white",
        height=700,
        hovermode="closest",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0.0},
        margin={"l": 60, "r": 30, "t": 100, "b": 60},
    )
    fig.update_xaxes(title="Time", range=[window_start, window_end], showspikes=True, spikemode="across")
    fig.update_yaxes(title="Close price", fixedrange=False, showspikes=True)

    return fig


_TWO_THRESHOLD_COLORS = {
    ("small", _Direction.UP): "#16a34a",
    ("small", _Direction.DOWN): "#dc2626",
    ("large", _Direction.UP): "#2563eb",
    ("large", _Direction.DOWN): "#f59e0b",
}

_THREE_THRESHOLD_COLORS = {
    ("small", _Direction.UP): "#16a34a",
    ("small", _Direction.DOWN): "#dc2626",
    ("medium", _Direction.UP): "#2563eb",
    ("medium", _Direction.DOWN): "#f59e0b",
    ("large", _Direction.UP): "#7c3aed",
    ("large", _Direction.DOWN): "#0f766e",
}

_ATTEMPT_OUTCOME_COLORS = {
    _AttemptOutcome.PROPAGATED: "#7c3aed",
    _AttemptOutcome.REJECTED: "#64748b",
}

_CROSS_SCALE_RELATIONSHIP_COLORS = {
    _CrossScaleRelationship.AGREEMENT: "#0f766e",
    _CrossScaleRelationship.DISAGREEMENT: "#be123c",
}


def _add_hierarchy_event_traces(fig: go.Figure, events: pd.DataFrame, scale: str, theta: float,
                                window_start: pd.Timestamp, window_end: pd.Timestamp,
                                colors: dict[tuple[str, _Direction], str] | None = None,
                                leg_width: float | None = None, leg_dash: str | None = None,
                                marker_size: int | None = None) -> None:
    """Add completed legs, ending extremes, and DCCs for one hierarchy scale."""
    scale_title = scale.title()
    color_map = colors or _TWO_THRESHOLD_COLORS
    line_width = leg_width if leg_width is not None else (1.4 if scale == "small" else 3.0)
    line_dash = leg_dash if leg_dash is not None else ("solid" if scale == "small" else "dash")
    point_size = marker_size if marker_size is not None else (5 if scale == "small" else 7)

    for direction in _Direction:
        color = color_map[(scale, direction)]
        directional_events = events.loc[events["direction"].eq(direction)]
        x_values: list[object] = []
        y_values: list[float | None] = []
        for event in directional_events.itertuples(index=False):
            x_values.extend([event.ext_start_idx, event.ext_end_idx, None])
            y_values.extend([event.ext_start_price, event.ext_end_price, None])

        if x_values:
            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines",
                name=f"{scale_title} {theta:.3%} completed {direction.value} legs",
                legendgroup=f"{scale}_{direction.value}",
                line={"color": color, "width": line_width, "dash": line_dash},
                opacity=0.85,
                hoverinfo="skip",
            ))

        extreme_events = directional_events.loc[
            directional_events["ext_end_idx"].between(window_start, window_end)
        ]
        if not extreme_events.empty:
            fig.add_trace(go.Scatter(
                x=extreme_events["ext_end_idx"],
                y=extreme_events["ext_end_price"],
                mode="markers",
                name=f"{scale_title} {direction.value} ending EXT",
                legendgroup=f"{scale}_{direction.value}",
                showlegend=False,
                marker={"color": color, "size": point_size, "symbol": "diamond"},
                customdata=extreme_events[["event_id", "tmv", "t", "r", "information_time"]].to_numpy(),
                hovertemplate=(
                    f"{scale_title} {direction.value} ending EXT<br>"
                    "time=%{x}<br>price=%{y:.5f}<br>event=%{customdata[0]}<br>"
                    "TMV=%{customdata[1]:.4f}<br>T=%{customdata[2]} bars<br>R=%{customdata[3]:.3e}<br>"
                    "known at=%{customdata[4]}<extra></extra>"
                ),
            ))

        confirmation_events = directional_events.loc[
            directional_events["dcc_idx"].between(window_start, window_end)
        ]
        if confirmation_events.empty:
            continue

        live_direction = _Direction.DOWN if direction == _Direction.UP else _Direction.UP
        dcc_color = color_map[(scale, live_direction)]
        dcc_symbol = "triangle-down" if live_direction == _Direction.DOWN else "triangle-up"
        fig.add_trace(go.Scatter(
            x=confirmation_events["dcc_idx"],
            y=confirmation_events["dcc_price"],
            mode="markers",
            name=f"{scale_title} {live_direction.value} DCC",
            legendgroup=f"{scale}_{live_direction.value}",
            showlegend=False,
            marker={
                "color": dcc_color,
                "size": point_size,
                "symbol": dcc_symbol,
                "line": {"color": "white", "width": 0.75},
            },
            customdata=confirmation_events[["event_id", "tmv", "t", "r", "ext_end_idx"]].to_numpy(),
            hovertemplate=(
                f"{scale_title} {live_direction.value} DCC<br>"
                "time=%{x}<br>price=%{y:.5f}<br>completed event=%{customdata[0]}<br>"
                "TMV=%{customdata[1]:.4f}<br>T=%{customdata[2]} bars<br>R=%{customdata[3]:.3e}<br>"
                "confirmed EXT time=%{customdata[4]}<extra></extra>"
            ),
        ))


def plot_two_threshold_directional_change(prices: pd.Series, small_events: pd.DataFrame,
                                          large_events: pd.DataFrame, small_theta: float, large_theta: float,
                                          n_prices: int = 5_000, title: str | None = None) -> go.Figure:
    """Plot two independent DC event ledgers over the same close series."""
    if not 0.0 < small_theta < large_theta:
        raise ValueError("Thresholds must satisfy 0 < small_theta < large_theta.")
    if n_prices <= 0:
        raise ValueError(f"n_prices must be positive, got {n_prices}.")
    if prices.empty:
        raise ValueError("prices must not be empty.")
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise TypeError("prices must use a DatetimeIndex.")
    if not prices.index.is_monotonic_increasing:
        raise ValueError("prices must be sorted chronologically.")

    for events, scale in ((small_events, "small"), (large_events, "large")):
        missing_columns = _REQUIRED_EVENT_COLUMNS.difference(events.columns)
        if missing_columns:
            raise KeyError(f"{scale}_events is missing required columns: {sorted(missing_columns)}")

    price_window = prices.tail(n_prices)
    window_start = price_window.index[0]
    window_end = price_window.index[-1]
    visible_small = small_events.loc[
        small_events["ext_start_idx"].le(window_end) & small_events["dcc_idx"].ge(window_start)
    ]
    visible_large = large_events.loc[
        large_events["ext_start_idx"].le(window_end) & large_events["dcc_idx"].ge(window_start)
    ]

    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=price_window.index,
        y=price_window.to_numpy(),
        mode="lines",
        name="Close",
        line={"color": "#475569", "width": 1.0},
        hovertemplate="time=%{x}<br>close=%{y:.5f}<extra></extra>",
    ))
    _add_hierarchy_event_traces(fig, visible_small, "small", small_theta, window_start, window_end)
    _add_hierarchy_event_traces(fig, visible_large, "large", large_theta, window_start, window_end)

    chart_title = title or f"{prices.name or 'Close'}: two-threshold directional-change hierarchy"
    fig.update_layout(
        title=f"{chart_title} — last {len(price_window):,} prices",
        template="plotly_white",
        height=760,
        hovermode="closest",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0.0},
        margin={"l": 60, "r": 30, "t": 120, "b": 60},
    )
    fig.update_xaxes(title="Time", range=[window_start, window_end], showspikes=True, spikemode="across")
    fig.update_yaxes(title="Close price", fixedrange=False, showspikes=True)
    return fig


def plot_two_threshold_modes(prices: pd.Series, mode_frame: pd.DataFrame, n_prices: int = 5_000,
                             title: str | None = None) -> go.Figure:
    """Plot causal small- and large-threshold live modes as separate ribbons below price."""
    required_columns = {
        "small_mode", "large_mode", "small_upward_dcc", "small_downward_dcc",
        "large_upward_dcc", "large_downward_dcc",
    }
    missing_columns = required_columns.difference(mode_frame.columns)
    if missing_columns:
        raise KeyError(f"mode_frame is missing required columns: {sorted(missing_columns)}")
    if n_prices <= 0:
        raise ValueError(f"n_prices must be positive, got {n_prices}.")
    if prices.empty:
        raise ValueError("prices must not be empty.")
    if not prices.index.equals(mode_frame.index):
        raise ValueError("prices and mode_frame must have identical indices.")

    price_window = prices.tail(n_prices)
    modes = mode_frame.loc[price_window.index]
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.74, 0.13, 0.13], vertical_spacing=0.035)
    fig.add_trace(go.Scattergl(
        x=price_window.index,
        y=price_window.to_numpy(),
        mode="lines",
        name="Close",
        line={"color": "#475569", "width": 1.1},
        hovertemplate="time=%{x}<br>close=%{y:.5f}<extra></extra>",
    ), row=1, col=1)

    for row_number, scale in ((2, "small"), (3, "large")):
        for direction in _Direction:
            is_direction = modes[f"{scale}_mode"].eq(direction.value)
            ribbon = np.where(is_direction, 1.0, np.nan)
            color = _TWO_THRESHOLD_COLORS[(scale, direction)]
            fig.add_trace(go.Scattergl(
                x=modes.index,
                y=ribbon,
                mode="lines",
                name=f"{scale.title()} live {direction.value}",
                legendgroup=f"{scale}_{direction.value}_mode",
                line={"color": color, "width": 14},
                connectgaps=False,
                hovertemplate=f"{scale.title()} live mode={direction.value}<br>time=%{{x}}<extra></extra>",
            ), row=row_number, col=1)

        for direction in _Direction:
            flag = f"{scale}_{direction.value}ward_dcc"
            dcc_times = modes.index[modes[flag]]
            if len(dcc_times) == 0:
                continue
            symbol = "triangle-up" if direction == _Direction.UP else "triangle-down"
            fig.add_trace(go.Scatter(
                x=dcc_times,
                y=np.ones(len(dcc_times)),
                mode="markers",
                name=f"{scale.title()} {direction.value} DCC",
                legendgroup=f"{scale}_{direction.value}_dcc",
                marker={"color": _TWO_THRESHOLD_COLORS[(scale, direction)], "size": 6, "symbol": symbol},
                hovertemplate=f"{scale.title()} {direction.value} DCC<br>time=%{{x}}<extra></extra>",
            ), row=row_number, col=1)

        fig.update_yaxes(title_text=scale.title(), range=[0.75, 1.25], showticklabels=False, row=row_number, col=1)

    chart_title = title or f"{prices.name or 'Close'}: causal two-threshold live modes"
    fig.update_layout(
        title=f"{chart_title} — last {len(price_window):,} prices",
        template="plotly_white",
        height=760,
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0.0},
        margin={"l": 70, "r": 30, "t": 130, "b": 60},
    )
    fig.update_xaxes(title_text="Time", row=3, col=1)
    fig.update_yaxes(title_text="Close price", row=1, col=1)
    return fig


def plot_three_threshold_directional_change(prices: pd.Series, small_events: pd.DataFrame,
                                            medium_events: pd.DataFrame, large_events: pd.DataFrame,
                                            small_theta: float, medium_theta: float, large_theta: float,
                                            n_prices: int = 5_000, title: str | None = None) -> go.Figure:
    """Plot three independent DC event ledgers over the same close series."""
    if not 0.0 < small_theta < medium_theta < large_theta:
        raise ValueError("Thresholds must satisfy 0 < small_theta < medium_theta < large_theta.")
    if n_prices <= 0:
        raise ValueError(f"n_prices must be positive, got {n_prices}.")
    if prices.empty:
        raise ValueError("prices must not be empty.")
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise TypeError("prices must use a DatetimeIndex.")
    if not prices.index.is_monotonic_increasing:
        raise ValueError("prices must be sorted chronologically.")

    event_ledgers = (
        (small_events, "small", small_theta, 1.0, "solid", 4),
        (medium_events, "medium", medium_theta, 1.8, "dot", 5),
        (large_events, "large", large_theta, 3.0, "dash", 7),
    )
    for events, scale, _, _, _, _ in event_ledgers:
        missing_columns = _REQUIRED_EVENT_COLUMNS.difference(events.columns)
        if missing_columns:
            raise KeyError(f"{scale}_events is missing required columns: {sorted(missing_columns)}")

    price_window = prices.tail(n_prices)
    window_start = price_window.index[0]
    window_end = price_window.index[-1]
    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=price_window.index,
        y=price_window.to_numpy(),
        mode="lines",
        name="Close",
        line={"color": "#475569", "width": 1.0},
        hovertemplate="time=%{x}<br>close=%{y:.5f}<extra></extra>",
    ))

    for events, scale, theta, line_width, line_dash, point_size in event_ledgers:
        visible_events = events.loc[
            events["ext_start_idx"].le(window_end) & events["dcc_idx"].ge(window_start)
        ]
        _add_hierarchy_event_traces(
            fig=fig,
            events=visible_events,
            scale=scale,
            theta=theta,
            window_start=window_start,
            window_end=window_end,
            colors=_THREE_THRESHOLD_COLORS,
            leg_width=line_width,
            leg_dash=line_dash,
            marker_size=point_size,
        )

    chart_title = title or f"{prices.name or 'Close'}: three-threshold directional-change hierarchy"
    fig.update_layout(
        title=f"{chart_title} - last {len(price_window):,} prices",
        template="plotly_white",
        height=800,
        hovermode="closest",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0.0},
        margin={"l": 60, "r": 30, "t": 130, "b": 60},
    )
    fig.update_xaxes(title="Time", range=[window_start, window_end], showspikes=True, spikemode="across")
    fig.update_yaxes(title="Close price", fixedrange=False, showspikes=True)
    return fig


def plot_three_threshold_modes(prices: pd.Series, mode_frame: pd.DataFrame, n_prices: int = 5_000,
                               title: str | None = None) -> go.Figure:
    """Plot causal small-, medium-, and large-threshold live modes as separate ribbons below price."""
    required_columns = set()
    for scale in ("small", "medium", "large"):
        required_columns.update({
            f"{scale}_mode",
            f"{scale}_upward_dcc",
            f"{scale}_downward_dcc",
        })
    missing_columns = required_columns.difference(mode_frame.columns)
    if missing_columns:
        raise KeyError(f"mode_frame is missing required columns: {sorted(missing_columns)}")
    if n_prices <= 0:
        raise ValueError(f"n_prices must be positive, got {n_prices}.")
    if prices.empty:
        raise ValueError("prices must not be empty.")
    if not prices.index.equals(mode_frame.index):
        raise ValueError("prices and mode_frame must have identical indices.")

    price_window = prices.tail(n_prices)
    modes = mode_frame.loc[price_window.index]
    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.67, 0.11, 0.11, 0.11],
        vertical_spacing=0.025,
    )
    fig.add_trace(go.Scattergl(
        x=price_window.index,
        y=price_window.to_numpy(),
        mode="lines",
        name="Close",
        line={"color": "#475569", "width": 1.1},
        hovertemplate="time=%{x}<br>close=%{y:.5f}<extra></extra>",
    ), row=1, col=1)

    scale_rows = ((2, "small", 4), (3, "medium", 5), (4, "large", 6))
    for row_number, scale, marker_size in scale_rows:
        for direction in _Direction:
            is_direction = modes[f"{scale}_mode"].eq(direction.value)
            ribbon = np.where(is_direction, 1.0, np.nan)
            color = _THREE_THRESHOLD_COLORS[(scale, direction)]
            fig.add_trace(go.Scattergl(
                x=modes.index,
                y=ribbon,
                mode="lines",
                name=f"{scale.title()} live {direction.value}",
                legendgroup=f"three_{scale}_{direction.value}_mode",
                line={"color": color, "width": 13},
                connectgaps=False,
                hovertemplate=f"{scale.title()} live mode={direction.value}<br>time=%{{x}}<extra></extra>",
            ), row=row_number, col=1)

        for direction in _Direction:
            flag = f"{scale}_{direction.value}ward_dcc"
            dcc_times = modes.index[modes[flag]]
            if len(dcc_times) == 0:
                continue
            symbol = "triangle-up" if direction == _Direction.UP else "triangle-down"
            fig.add_trace(go.Scatter(
                x=dcc_times,
                y=np.ones(len(dcc_times)),
                mode="markers",
                name=f"{scale.title()} {direction.value} DCC",
                legendgroup=f"three_{scale}_{direction.value}_dcc",
                marker={
                    "color": _THREE_THRESHOLD_COLORS[(scale, direction)],
                    "size": marker_size,
                    "symbol": symbol,
                    "line": {"color": "white", "width": 0.6},
                },
                hovertemplate=f"{scale.title()} {direction.value} DCC<br>time=%{{x}}<extra></extra>",
            ), row=row_number, col=1)

        fig.update_yaxes(
            title_text=scale.title(),
            range=[0.75, 1.25],
            showticklabels=False,
            row=row_number,
            col=1,
        )

    chart_title = title or f"{prices.name or 'Close'}: causal three-threshold live modes"
    fig.update_layout(
        title=f"{chart_title} - last {len(price_window):,} prices",
        template="plotly_white",
        height=850,
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0.0},
        margin={"l": 75, "r": 30, "t": 140, "b": 60},
    )
    fig.update_xaxes(title_text="Time", row=4, col=1)
    fig.update_yaxes(title_text="Close price", row=1, col=1)
    return fig


def plot_dc_linkage_flow(linkages: pd.DataFrame, title: str | None = None) -> go.Figure:
    """Plot the terminal propagation depth of resolved small-origin three-scale linkages."""
    required_columns = {"terminal_depth"}
    missing_columns = required_columns.difference(linkages.columns)
    if missing_columns:
        raise KeyError(f"linkages is missing required columns: {sorted(missing_columns)}")
    if linkages.empty:
        raise ValueError("linkages must contain at least one resolved lineage.")
    if linkages["terminal_depth"].isna().any():
        raise ValueError("linkages must contain resolved terminal depths only.")

    depth_counts = linkages["terminal_depth"].astype(int).value_counts().reindex([0, 1, 2], fill_value=0)
    depth_zero = int(depth_counts.loc[0])
    depth_one = int(depth_counts.loc[1])
    depth_two = int(depth_counts.loc[2])
    reached_medium = depth_one + depth_two
    node_labels = [
        f"Small-origin seeds<br>n={len(linkages):,}",
        f"Stopped below medium<br>depth 0: {depth_zero:,}",
        f"Reached medium<br>n={reached_medium:,}",
        f"Stopped below large<br>depth 1: {depth_one:,}",
        f"Reached large<br>depth 2: {depth_two:,}",
    ]
    node_colors = ["#334155", "#dc2626", "#2563eb", "#f59e0b", "#16a34a"]
    link_colors = ["rgba(220, 38, 38, 0.40)", "rgba(37, 99, 235, 0.40)",
                   "rgba(245, 158, 11, 0.45)", "rgba(22, 163, 74, 0.45)"]
    figure = go.Figure(go.Sankey(
        arrangement="snap",
        node={"label": node_labels, "color": node_colors, "pad": 24, "thickness": 22},
        link={
            "source": [0, 0, 2, 2],
            "target": [1, 2, 3, 4],
            "value": [depth_zero, reached_medium, depth_one, depth_two],
            "color": link_colors,
        },
    ))
    chart_title = title or "Linked three-threshold terminal propagation depth"
    figure.update_layout(
        title=chart_title,
        template="plotly_white",
        height=560,
        margin={"l": 30, "r": 30, "t": 90, "b": 30},
    )
    return figure


def plot_dc_attempt_feature_distributions(attempts: pd.DataFrame, nbins: int = 55) -> go.Figure:
    """Compare completed-leg feature distributions by the later attempt outcome."""
    feature_labels = {
        "tmv": "log10(TMV)",
        "t": "log10(T bars)",
        "r": "log10(R)",
    }
    required_columns = {"future_outcome", *feature_labels}
    missing_columns = required_columns.difference(attempts.columns)
    if missing_columns:
        raise KeyError(f"attempts is missing required columns: {sorted(missing_columns)}")
    if attempts.empty:
        raise ValueError("attempts must not be empty.")
    if nbins <= 0:
        raise ValueError(f"nbins must be positive, got {nbins}.")

    invalid_outcomes = set(attempts["future_outcome"].dropna().unique()).difference(_AttemptOutcome)
    if invalid_outcomes:
        raise ValueError(f"Unsupported future_outcome values: {sorted(invalid_outcomes)}")
    if attempts[list(feature_labels)].le(0.0).any().any():
        raise ValueError("TMV, T, and R must all be strictly positive before log transformation.")

    fig = make_subplots(rows=1, cols=3, subplot_titles=list(feature_labels.values()))
    for column_number, (feature, axis_label) in enumerate(feature_labels.items(), start=1):
        for outcome in _AttemptOutcome:
            outcome_attempts = attempts.loc[attempts["future_outcome"].eq(outcome)]
            values = np.log10(outcome_attempts[feature].to_numpy(dtype=np.float64))
            fig.add_trace(go.Histogram(
                x=values,
                name=f"{outcome.value.title()} (n={len(outcome_attempts):,})",
                legendgroup=outcome.value,
                marker={"color": _ATTEMPT_OUTCOME_COLORS[outcome]},
                opacity=0.55,
                histnorm="probability",
                nbinsx=nbins,
                bingroup=feature,
                showlegend=column_number == 1,
                hovertemplate=f"{axis_label}=%{{x:.4f}}<br>within-outcome share=%{{y:.2%}}<extra></extra>",
            ), row=1, col=column_number)
        fig.update_xaxes(title_text=axis_label, row=1, col=column_number)
        fig.update_yaxes(title_text="Within-outcome probability" if column_number == 1 else None,
                         tickformat=".0%", row=1, col=column_number)

    fig.update_layout(
        title="Causal completed-leg features grouped by later resolution — diagnostic hindsight grouping",
        template="plotly_white",
        barmode="overlay",
        height=540,
        hovermode="closest",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.08, "xanchor": "left", "x": 0.0},
        margin={"l": 70, "r": 30, "t": 125, "b": 70},
    )
    return fig


def plot_dc_attempt_tmv_t_space(attempts: pd.DataFrame, theta: float) -> go.Figure:
    """Plot causal completed-leg TMV–T geometry with hindsight outcomes and constant-R contours."""
    required_columns = {"small_event_id", "start_time", "new_small_mode", "future_outcome", "tmv", "t", "r"}
    missing_columns = required_columns.difference(attempts.columns)
    if missing_columns:
        raise KeyError(f"attempts is missing required columns: {sorted(missing_columns)}")
    if attempts.empty:
        raise ValueError("attempts must not be empty.")
    if theta <= 0.0:
        raise ValueError(f"theta must be positive, got {theta}.")
    if attempts[["tmv", "t", "r"]].le(0.0).any().any():
        raise ValueError("TMV, T, and R must all be strictly positive.")

    invalid_outcomes = set(attempts["future_outcome"].dropna().unique()).difference(_AttemptOutcome)
    if invalid_outcomes:
        raise ValueError(f"Unsupported future_outcome values: {sorted(invalid_outcomes)}")
    invalid_directions = set(attempts["new_small_mode"].dropna().unique()).difference(_Direction)
    if invalid_directions:
        raise ValueError(f"Unsupported new_small_mode values: {sorted(invalid_directions)}")

    fig = go.Figure()
    direction_symbols = {_Direction.UP: "triangle-up", _Direction.DOWN: "triangle-down"}
    for outcome in _AttemptOutcome:
        for direction in _Direction:
            selected = attempts.loc[
                attempts["future_outcome"].eq(outcome) & attempts["new_small_mode"].eq(direction)
            ]
            fig.add_trace(go.Scattergl(
                x=selected["t"],
                y=selected["tmv"],
                mode="markers",
                name=f"{outcome.value.title()} | new small {direction.value}",
                legendgroup=f"{outcome.value}_{direction.value}",
                marker={
                    "color": _ATTEMPT_OUTCOME_COLORS[outcome],
                    "size": 7,
                    "symbol": direction_symbols[direction],
                    "opacity": 0.62,
                },
                customdata=selected[["small_event_id", "start_time", "r"]].to_numpy(),
                hovertemplate=(
                    "event=%{customdata[0]}<br>start=%{customdata[1]}<br>"
                    "T=%{x:.0f} bars<br>TMV=%{y:.4f}<br>R=%{customdata[2]:.3e}<extra></extra>"
                ),
            ))

    t_values = attempts["t"].to_numpy(dtype=np.float64)
    t_grid = np.geomspace(t_values.min(), t_values.max(), 200)
    r_quantiles = attempts["r"].quantile([0.25, 0.50, 0.75])
    for quantile, r_level in r_quantiles.items():
        fig.add_trace(go.Scatter(
            x=t_grid,
            y=r_level * t_grid / theta,
            mode="lines",
            name=f"Constant R p{quantile * 100:.0f}: {r_level:.2e}",
            legendgroup="r_contours",
            line={"color": "#111827", "width": 1.0, "dash": "dot"},
            opacity=0.55,
            hovertemplate=f"R={r_level:.3e}<extra></extra>",
        ))

    fig.update_layout(
        title="Initiating completed leg in TMV–T space — color is the later attempt outcome",
        template="plotly_white",
        height=720,
        hovermode="closest",
        xaxis={"title": "T (bars between completed-leg extremes)", "type": "log"},
        yaxis={"title": "TMV (small-threshold multiples)", "type": "log"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0.0},
        margin={"l": 80, "r": 30, "t": 130, "b": 75},
    )
    return fig


def plot_dc_relationship_feature_distributions(relationships: pd.DataFrame, feature_labels: dict[str, str],
                                               relationship_column: str, title: str, nbins: int = 55) -> go.Figure:
    """Compare logged feature distributions for causal cross-threshold agreement and disagreement."""
    required_columns = {relationship_column, *feature_labels}
    missing_columns = required_columns.difference(relationships.columns)
    if missing_columns:
        raise KeyError(f"relationships is missing required columns: {sorted(missing_columns)}")
    if relationships.empty:
        raise ValueError("relationships must not be empty.")
    if not feature_labels:
        raise ValueError("feature_labels must not be empty.")
    if nbins <= 0:
        raise ValueError(f"nbins must be positive, got {nbins}.")

    clean_relationships = relationships.dropna(subset=[relationship_column, *feature_labels]).copy()
    if clean_relationships.empty:
        raise ValueError("No complete relationship rows remain after removing missing values.")
    invalid_relationships = set(clean_relationships[relationship_column].unique()).difference(
        _CrossScaleRelationship
    )
    if invalid_relationships:
        raise ValueError(f"Unsupported relationship values: {sorted(invalid_relationships)}")
    if clean_relationships[list(feature_labels)].le(0.0).any().any():
        raise ValueError("All plotted relationship features must be strictly positive.")

    fig = make_subplots(rows=1, cols=len(feature_labels), subplot_titles=list(feature_labels.values()))
    for column_number, (feature, axis_label) in enumerate(feature_labels.items(), start=1):
        for relationship in _CrossScaleRelationship:
            selected = clean_relationships.loc[clean_relationships[relationship_column].eq(relationship)]
            values = np.log10(selected[feature].to_numpy(dtype=np.float64))
            fig.add_trace(go.Histogram(
                x=values,
                name=f"{relationship.value.title()} (n={len(selected):,})",
                legendgroup=relationship.value,
                marker={"color": _CROSS_SCALE_RELATIONSHIP_COLORS[relationship]},
                opacity=0.55,
                histnorm="probability",
                nbinsx=nbins,
                bingroup=feature,
                showlegend=column_number == 1,
                hovertemplate=f"{axis_label}=%{{x:.4f}}<br>within-group share=%{{y:.2%}}<extra></extra>",
            ), row=1, col=column_number)
        fig.update_xaxes(title_text=axis_label, row=1, col=column_number)
        fig.update_yaxes(title_text="Within-group probability" if column_number == 1 else None,
                         tickformat=".0%", row=1, col=column_number)

    fig.update_layout(
        title=title,
        template="plotly_white",
        barmode="overlay",
        height=540,
        hovermode="closest",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.08, "xanchor": "left", "x": 0.0},
        margin={"l": 70, "r": 30, "t": 130, "b": 70},
    )
    return fig


def plot_dc_counter_scale_trajectories(trajectories: pd.DataFrame, max_elapsed_bars: int = 200) -> go.Figure:
    """Plot survival-conditioned median live paths, grouped by hindsight outcome and causal direction."""
    feature_labels = {
        "small_tmv_live": "Live small TMV from confirmed EXT",
        "max_post_dcc_excursion_theta": "Maximum post-DCC excursion (small θ)",
        "small_rdc_live": "Live small RDC",
        "large_dcc_progress": "Progress toward large DCC",
    }
    required_columns = {"elapsed_bars", "future_outcome", "target_small_mode", *feature_labels}
    missing_columns = required_columns.difference(trajectories.columns)
    if missing_columns:
        raise KeyError(f"trajectories is missing required columns: {sorted(missing_columns)}")
    if trajectories.empty:
        raise ValueError("trajectories must not be empty.")
    if max_elapsed_bars < 0:
        raise ValueError(f"max_elapsed_bars must be non-negative, got {max_elapsed_bars}.")

    selected = trajectories.loc[trajectories["elapsed_bars"].le(max_elapsed_bars)].copy()
    invalid_outcomes = set(selected["future_outcome"].dropna().unique()).difference(_AttemptOutcome)
    if invalid_outcomes:
        raise ValueError(f"Unsupported future_outcome values: {sorted(invalid_outcomes)}")
    invalid_directions = set(selected["target_small_mode"].dropna().unique()).difference(_Direction)
    if invalid_directions:
        raise ValueError(f"Unsupported target_small_mode values: {sorted(invalid_directions)}")

    summary = selected.groupby(
        ["elapsed_bars", "future_outcome", "target_small_mode"], sort=True
    ).agg(
        survivor_count=("attempt_id", "size"),
        **{f"{feature}_median": (feature, "median") for feature in feature_labels},
    ).reset_index()
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=list(feature_labels.values()),
        vertical_spacing=0.16,
        horizontal_spacing=0.12,
    )
    direction_dashes = {_Direction.UP: "solid", _Direction.DOWN: "dash"}

    for feature_number, (feature, axis_label) in enumerate(feature_labels.items()):
        row_number = feature_number // 2 + 1
        column_number = feature_number % 2 + 1
        for outcome in _AttemptOutcome:
            for direction in _Direction:
                group = summary.loc[
                    summary["future_outcome"].eq(outcome)
                    & summary["target_small_mode"].eq(direction)
                ]
                fig.add_trace(go.Scattergl(
                    x=group["elapsed_bars"],
                    y=group[f"{feature}_median"],
                    mode="lines",
                    name=f"{outcome.value.title()} | new small {direction.value}",
                    legendgroup=f"{outcome.value}_{direction.value}",
                    showlegend=feature_number == 0,
                    line={
                        "color": _ATTEMPT_OUTCOME_COLORS[outcome],
                        "width": 2.0,
                        "dash": direction_dashes[direction],
                    },
                    customdata=group[["survivor_count"]].to_numpy(),
                    hovertemplate=(
                        "elapsed=%{x:.0f} bars<br>median=%{y:.4g}<br>"
                        "surviving attempts=%{customdata[0]:,.0f}<extra></extra>"
                    ),
                ), row=row_number, col=column_number)
        fig.update_xaxes(title_text="Bars since initiating small DCC", row=row_number, col=column_number)
        fig.update_yaxes(
            title_text=axis_label,
            type="log" if feature == "small_rdc_live" else "linear",
            row=row_number,
            col=column_number,
        )

    fig.update_layout(
        title=(
            "Live counter-scale paths — color is hindsight outcome; later elapsed bars condition on survival"
        ),
        template="plotly_white",
        height=850,
        hovermode="closest",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.04, "xanchor": "left", "x": 0.0},
        margin={"l": 85, "r": 30, "t": 135, "b": 75},
    )
    return fig


def plot_dc_counter_scale_price_casebook(prices: pd.Series, trajectories: pd.DataFrame,
                                         attempts: pd.DataFrame, bars_before: int = 80,
                                         bars_after: int = 80) -> go.Figure:
    """Plot selected counter-scale attempts with live causal paths and later resolution markers."""
    required_trajectory_columns = {
        "attempt_id", "time", "bar_position", "price", "small_tmv_live", "small_rdc_live",
        "large_dcc_progress", "max_post_dcc_excursion_theta",
    }
    missing_trajectory_columns = required_trajectory_columns.difference(trajectories.columns)
    if missing_trajectory_columns:
        raise KeyError(f"trajectories is missing required columns: {sorted(missing_trajectory_columns)}")
    required_attempt_columns = {
        "attempt_id", "target_small_mode", "future_outcome", "start_time", "start_position",
        "resolution_time", "resolution_position", "resolution_bars",
    }
    missing_attempt_columns = required_attempt_columns.difference(attempts.columns)
    if missing_attempt_columns:
        raise KeyError(f"attempts is missing required columns: {sorted(missing_attempt_columns)}")
    if attempts.empty:
        raise ValueError("attempts must not be empty.")
    if bars_before < 0 or bars_after < 0:
        raise ValueError("bars_before and bars_after must be non-negative.")

    fig = make_subplots(
        rows=len(attempts),
        cols=1,
        vertical_spacing=min(0.06, 0.20 / len(attempts)),
        subplot_titles=[
            (
                f"{attempt.future_outcome} | new small {attempt.target_small_mode} | "
                f"resolved in {attempt.resolution_bars:.0f} bars"
            )
            for attempt in attempts.itertuples(index=False)
        ],
    )
    direction_symbols = {_Direction.UP: "triangle-up", _Direction.DOWN: "triangle-down"}

    for row_number, attempt in enumerate(attempts.itertuples(index=False), start=1):
        outcome = _AttemptOutcome(attempt.future_outcome)
        direction = _Direction(attempt.target_small_mode)
        start_position = int(attempt.start_position)
        resolution_position = int(attempt.resolution_position)
        window_start = max(0, start_position - bars_before)
        window_end = min(len(prices), resolution_position + bars_after + 1)
        price_window = prices.iloc[window_start:window_end]
        attempt_path = trajectories.loc[trajectories["attempt_id"].eq(attempt.attempt_id)]

        fig.add_trace(go.Scattergl(
            x=price_window.index,
            y=price_window.to_numpy(),
            mode="lines",
            name="Close",
            legendgroup="close",
            showlegend=row_number == 1,
            line={"color": "#94a3b8", "width": 1.1},
            hovertemplate="time=%{x}<br>close=%{y:.5f}<extra></extra>",
        ), row=row_number, col=1)
        fig.add_trace(go.Scattergl(
            x=attempt_path["time"],
            y=attempt_path["price"],
            mode="lines",
            name="Active unresolved counter leg",
            legendgroup="active_counter_leg",
            showlegend=row_number == 1,
            line={"color": _ATTEMPT_OUTCOME_COLORS[outcome], "width": 3.0},
            customdata=attempt_path[[
                "small_tmv_live", "small_rdc_live", "large_dcc_progress", "max_post_dcc_excursion_theta",
            ]].to_numpy(),
            hovertemplate=(
                "time=%{x}<br>close=%{y:.5f}<br>live small TMV=%{customdata[0]:.3f}<br>"
                "live small RDC=%{customdata[1]:.3e}<br>large-DCC progress=%{customdata[2]:.2%}<br>"
                "max post-DCC excursion=%{customdata[3]:.3f} θ<extra></extra>"
            ),
        ), row=row_number, col=1)
        fig.add_trace(go.Scatter(
            x=[attempt.start_time],
            y=[prices.iloc[start_position]],
            mode="markers",
            name="Initiating small DCC",
            legendgroup="attempt_start",
            showlegend=row_number == 1,
            marker={
                "color": _ATTEMPT_OUTCOME_COLORS[outcome],
                "size": 9,
                "symbol": direction_symbols[direction],
                "line": {"color": "white", "width": 1},
            },
            hovertemplate="initiating small DCC<br>time=%{x}<br>price=%{y:.5f}<extra></extra>",
        ), row=row_number, col=1)
        fig.add_trace(go.Scatter(
            x=[attempt.resolution_time],
            y=[prices.iloc[resolution_position]],
            mode="markers",
            name="Resolution (hindsight from start)",
            legendgroup="attempt_resolution",
            showlegend=row_number == 1,
            marker={"color": "#111827", "size": 9, "symbol": "x"},
            hovertemplate="resolution<br>time=%{x}<br>price=%{y:.5f}<extra></extra>",
        ), row=row_number, col=1)
        fig.update_yaxes(title_text="Close", row=row_number, col=1)

    fig.update_xaxes(title_text="Time", row=len(attempts), col=1)
    fig.update_layout(
        title=(
            "Counter-scale live-leg casebook — colored segment was observable sequentially; outcome was not"
        ),
        template="plotly_white",
        height=max(780, 350 * len(attempts)),
        hovermode="closest",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0.0},
        margin={"l": 80, "r": 30, "t": 135, "b": 70},
    )
    return fig


def plot_dc_indicator_distributions(events: pd.DataFrame, nbins: int = 60,
                                    central_quantile: float = 0.99) -> go.Figure:
    """Plot direction-conditioned TMV, T, and R distributions for completed events."""
    indicator_labels = {
        "tmv": "TMV (threshold multiples)",
        "t": "T (bars)",
        "r": "R (return per bar)",
    }
    required_columns = {"direction", *indicator_labels}
    missing_columns = required_columns.difference(events.columns)
    if missing_columns:
        raise KeyError(f"events is missing required columns: {sorted(missing_columns)}")
    if events.empty:
        raise ValueError("events must not be empty.")
    if nbins <= 0:
        raise ValueError(f"nbins must be positive, got {nbins}.")
    if not 0.0 < central_quantile <= 1.0:
        raise ValueError(f"central_quantile must lie in (0, 1], got {central_quantile}.")

    invalid_directions = set(events["direction"].dropna().unique()).difference(_Direction)
    if invalid_directions:
        raise ValueError(f"Unsupported direction values: {sorted(invalid_directions)}")

    colors = {_Direction.UP: "#16a34a", _Direction.DOWN: "#dc2626"}
    fig = make_subplots(rows=1, cols=3, subplot_titles=list(indicator_labels.values()))

    for column_number, indicator in enumerate(indicator_labels, start=1):
        values = events[indicator].dropna()
        if values.empty:
            raise ValueError(f"events['{indicator}'] contains no observations.")

        lower_bound = float(values.min())
        upper_bound = float(values.quantile(central_quantile))
        padding = max((upper_bound - lower_bound) * 0.02, abs(upper_bound) * 0.002)

        for direction in _Direction:
            direction_values = events.loc[events["direction"] == direction, indicator].dropna()
            fig.add_trace(go.Histogram(
                x=direction_values,
                name=f"{direction.value.title()} (n={len(direction_values):,})",
                legendgroup=direction.value,
                marker={"color": colors[direction]},
                opacity=0.55,
                histnorm="probability",
                nbinsx=nbins,
                bingroup=indicator,
                showlegend=column_number == 1,
                hovertemplate="value=%{x:.6g}<br>within-direction share=%{y:.2%}<extra></extra>",
            ), row=1, col=column_number)

        fig.update_xaxes(range=[lower_bound - padding, upper_bound + padding], row=1, col=column_number)
        fig.update_xaxes(title_text=indicator_labels[indicator], row=1, col=column_number)
        fig.update_yaxes(title_text="Within-direction probability" if column_number == 1 else None,
                         tickformat=".0%", row=1, col=column_number)

    fig.update_layout(
        title=(
            "Completed-event indicator distributions by direction"
            f" — initial view through p{central_quantile * 100:g}"
        ),
        template="plotly_white",
        barmode="overlay",
        height=520,
        hovermode="closest",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.08, "xanchor": "left", "x": 0.0},
        margin={"l": 60, "r": 30, "t": 120, "b": 70},
    )
    fig.add_annotation(
        text="All events remain in the traces; use Autoscale to reveal the full right tails.",
        xref="paper",
        yref="paper",
        x=0.5,
        y=-0.22,
        showarrow=False,
    )

    return fig


def plot_hmm_states_on_price(prices: pd.Series, bar_states: pd.DataFrame, hmm_events: pd.DataFrame,
                             n_prices: int = 5_000, title: str | None = None,
                             oos_start_time: pd.Timestamp | None = None) -> go.Figure:
    """Plot regime-coloured prices together with the completed DC events that generated each HMM update."""
    required_bar_columns = {"state_name", "state_probability", "state_information_time", "source_event_id"}
    missing_bar_columns = required_bar_columns.difference(bar_states.columns)
    if missing_bar_columns:
        raise KeyError(f"bar_states is missing required columns: {sorted(missing_bar_columns)}")
    required_event_columns = {
        "event_id", "direction", "ext_start_idx", "ext_start_price", "ext_end_idx", "ext_end_price",
        "dcc_idx", "dcc_price", "tmv", "t", "r", "log_r", "state_name", "state_probability", "p_fast_r",
    }
    missing_event_columns = required_event_columns.difference(hmm_events.columns)
    if missing_event_columns:
        raise KeyError(f"hmm_events is missing required columns: {sorted(missing_event_columns)}")
    if n_prices <= 0:
        raise ValueError(f"n_prices must be positive, got {n_prices}.")
    if prices.empty:
        raise ValueError("prices must not be empty.")
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise TypeError("prices must use a DatetimeIndex.")
    if not prices.index.is_monotonic_increasing:
        raise ValueError("prices must be sorted chronologically.")

    price_window = prices.tail(n_prices)
    state_window = bar_states.reindex(price_window.index)
    state_colors = {"slow_R": "#2563eb", "fast_R": "#f97316"}
    direction_colors = {_Direction.UP: "#16a34a", _Direction.DOWN: "#dc2626"}
    window_start = price_window.index[0]
    window_end = price_window.index[-1]
    visible_events = hmm_events.loc[
        (hmm_events["ext_start_idx"] <= window_end) & (hmm_events["dcc_idx"] >= window_start)
    ].copy()

    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=price_window.index,
        y=price_window.to_numpy(),
        mode="lines",
        name="Close",
        line={"color": "#cbd5e1", "width": 1.0},
        hovertemplate="time=%{x}<br>close=%{y:.5f}<extra></extra>",
    ))

    observed_states = [state for state in state_colors if state_window["state_name"].eq(state).any()]
    for state_name in observed_states:
        state_mask = state_window["state_name"].eq(state_name)
        state_rows = state_window.loc[state_mask]
        fig.add_trace(go.Scattergl(
            x=state_rows.index,
            y=price_window.loc[state_mask].to_numpy(),
            mode="markers",
            name=f"Price: {state_name}",
            legendgroup=state_name,
            marker={"color": state_colors[state_name], "size": 3, "opacity": 0.45},
            customdata=state_rows[["state_probability", "state_information_time", "source_event_id"]].to_numpy(),
            hovertemplate=(
                "time=%{x}<br>close=%{y:.5f}<br>state=" + state_name + "<br>"
                "probability=%{customdata[0]:.3f}<br>state known since=%{customdata[1]}<br>"
                "source event=%{customdata[2]:.0f}<extra></extra>"
            ),
        ))

    for direction in _Direction:
        trace_events = visible_events.loc[visible_events["direction"].eq(direction)]
        if trace_events.empty:
            continue

        x_values: list[object] = []
        y_values: list[float | None] = []
        customdata: list[list[object] | None] = []
        for event in trace_events.itertuples(index=False):
            event_hover = [
                event.event_id, event.direction, event.state_name, event.r, event.log_r, event.t, event.tmv,
                event.p_fast_r, event.state_probability, event.dcc_idx,
            ]
            x_values.extend([event.ext_start_idx, event.ext_end_idx, None])
            y_values.extend([event.ext_start_price, event.ext_end_price, None])
            customdata.extend([event_hover, event_hover, None])

        fig.add_trace(go.Scattergl(
            x=x_values,
            y=y_values,
            mode="lines",
            name=f"DC {direction.value}",
            legendgroup=f"dc_{direction.value}",
            line={"color": direction_colors[direction], "width": 1.25},
            customdata=customdata,
            hovertemplate=(
                "event=%{customdata[0]:.0f}<br>direction=%{customdata[1]}<br>"
                "filtered state=%{customdata[2]}<br>R=%{customdata[3]:.3e}<br>"
                "log(R)=%{customdata[4]:.4f}<br>T=%{customdata[5]:.0f} bars<br>"
                "TMV=%{customdata[6]:.4f}<br>p(fast_R)=%{customdata[7]:.3f}<br>"
                "state probability=%{customdata[8]:.3f}<br>known at DCC=%{customdata[9]}<extra></extra>"
            ),
        ))

        dcc_is_downward = direction == _Direction.UP
        dcc_symbol = "triangle-down-open" if dcc_is_downward else "triangle-up-open"
        dcc_label = "Downward DCC" if dcc_is_downward else "Upward DCC"
        dcc_color = direction_colors[_Direction.DOWN] if dcc_is_downward else direction_colors[_Direction.UP]
        fig.add_trace(go.Scattergl(
            x=trace_events["dcc_idx"],
            y=trace_events["dcc_price"],
            mode="markers",
            name=dcc_label,
            legendgroup=f"dcc_{direction.value}",
            marker={
                "color": dcc_color,
                "size": 6,
                "symbol": dcc_symbol,
                "line": {"color": dcc_color, "width": 2},
            },
            customdata=trace_events[
                [
                    "event_id", "state_name", "r", "log_r", "t", "tmv", "p_fast_r", "state_probability",
                    "ext_end_idx",
                ]
            ].to_numpy(),
            hovertemplate=(
                f"{dcc_label}<br>time=%{{x}}<br>price=%{{y:.5f}}<br>event=%{{customdata[0]:.0f}}<br>"
                "filtered state=%{customdata[1]}<br>R=%{customdata[2]:.3e}<br>"
                "log(R)=%{customdata[3]:.4f}<br>T=%{customdata[4]:.0f} bars<br>"
                "TMV=%{customdata[5]:.4f}<br>p(fast_R)=%{customdata[6]:.3f}<br>"
                "state probability=%{customdata[7]:.3f}<br>"
                "confirmed EXT time=%{customdata[8]}<extra></extra>"
            ),
        ))

    for state_name, state_color in state_colors.items():
        state_events = visible_events.loc[visible_events["state_name"].eq(state_name)]
        if state_events.empty:
            continue
        fig.add_trace(go.Scattergl(
            x=state_events["dcc_idx"],
            y=state_events["dcc_price"],
            mode="markers",
            name=f"State at DCC: {state_name}",
            legendgroup=f"dcc_state_{state_name}",
            marker={
                "color": state_color,
                "size": 6,
                "symbol": "circle",
                "line": {"color": "white", "width": 0.75},
            },
            customdata=state_events[
                ["event_id", "direction", "r", "log_r", "t", "tmv", "p_fast_r", "state_probability"]
            ].to_numpy(),
            hovertemplate=(
                "HMM update at DCC<br>time=%{x}<br>price=%{y:.5f}<br>event=%{customdata[0]:.0f}<br>"
                "event direction=%{customdata[1]}<br>new state=" + state_name + "<br>"
                "R=%{customdata[2]:.3e}<br>log(R)=%{customdata[3]:.4f}<br>"
                "T=%{customdata[4]:.0f} bars<br>TMV=%{customdata[5]:.4f}<br>"
                "p(fast_R)=%{customdata[6]:.3f}<br>state probability=%{customdata[7]:.3f}<extra></extra>"
            ),
        ))

    if oos_start_time is not None and window_start <= oos_start_time <= window_end:
        fig.add_vline(x=oos_start_time, line={"color": "#111827", "dash": "dash", "width": 1.5})
        fig.add_annotation(
            x=oos_start_time,
            y=1.0,
            xref="x",
            yref="paper",
            text="OOS begins",
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
        )

    chart_title = title or f"{prices.name or 'Close'}: DC events and filtered event-time HMM states"
    fig.update_layout(
        title=f"{chart_title} — last {len(price_window):,} prices",
        template="plotly_white",
        height=700,
        hovermode="closest",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0.0},
        margin={"l": 60, "r": 30, "t": 100, "b": 60},
    )
    fig.update_xaxes(title="Time", range=[window_start, window_end], showspikes=True, spikemode="across")
    fig.update_yaxes(title="Close price", fixedrange=False, showspikes=True)

    return fig


def _validate_hmm_audit_events(hmm_events: pd.DataFrame, required_columns: set[str]) -> None:
    """Validate the common event table contract used by HMM audit charts."""
    missing_columns = required_columns.difference(hmm_events.columns)
    if missing_columns:
        raise KeyError(f"hmm_events is missing required columns: {sorted(missing_columns)}")
    if hmm_events.empty:
        raise ValueError("hmm_events must not be empty.")


def plot_hmm_log_r_distributions(hmm_events: pd.DataFrame, nbins: int = 50) -> go.Figure:
    """Compare log-R distributions assigned to each state in train and OOS event samples."""
    _validate_hmm_audit_events(hmm_events, {"log_r", "state_name", "sample"})
    if nbins <= 0:
        raise ValueError(f"nbins must be positive, got {nbins}.")

    state_colors = {"slow_R": "#2563eb", "fast_R": "#f97316"}
    samples = ("train", "oos")
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Training events", "OOS events"))

    for column_number, sample in enumerate(samples, start=1):
        sample_events = hmm_events.loc[hmm_events["sample"].eq(sample)]
        for state_name, state_color in state_colors.items():
            values = sample_events.loc[sample_events["state_name"].eq(state_name), "log_r"]
            fig.add_trace(go.Histogram(
                x=values,
                name=f"{state_name} (n={len(values):,})",
                legendgroup=state_name,
                marker={"color": state_color},
                opacity=0.55,
                histnorm="probability",
                nbinsx=nbins,
                bingroup=f"log_r_{sample}",
                showlegend=column_number == 1,
                hovertemplate="log(R)=%{x:.4f}<br>within-state share=%{y:.2%}<extra></extra>",
            ), row=1, col=column_number)
        fig.update_xaxes(title_text="log(R)", row=1, col=column_number)
        fig.update_yaxes(
            title_text="Within-state probability" if column_number == 1 else None,
            tickformat=".0%",
            row=1,
            col=column_number,
        )

    fig.update_layout(
        title="Audit 1 — log(R) distributions by filtered state",
        template="plotly_white",
        barmode="overlay",
        height=500,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.08, "xanchor": "left", "x": 0.0},
        margin={"l": 60, "r": 30, "t": 120, "b": 60},
    )
    return fig


def plot_hmm_tmv_t_space(hmm_events: pd.DataFrame) -> go.Figure:
    """Plot completed events in TMV-T space, coloured by filtered state and split by sample."""
    required_columns = {"event_id", "tmv", "t", "r", "state_name", "state_probability", "sample", "direction"}
    _validate_hmm_audit_events(hmm_events, required_columns)

    state_colors = {"slow_R": "#2563eb", "fast_R": "#f97316"}
    samples = ("train", "oos")
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Training events", "OOS events"))

    for column_number, sample in enumerate(samples, start=1):
        sample_events = hmm_events.loc[hmm_events["sample"].eq(sample)]
        for state_name, state_color in state_colors.items():
            state_events = sample_events.loc[sample_events["state_name"].eq(state_name)]
            fig.add_trace(go.Scattergl(
                x=state_events["t"],
                y=state_events["tmv"],
                mode="markers",
                name=state_name,
                legendgroup=state_name,
                showlegend=column_number == 1,
                marker={"color": state_color, "size": 6, "opacity": 0.55},
                customdata=state_events[
                    ["event_id", "direction", "r", "state_probability"]
                ].to_numpy(),
                hovertemplate=(
                    "event=%{customdata[0]:.0f}<br>direction=%{customdata[1]}<br>"
                    "T=%{x:.0f} bars<br>TMV=%{y:.4f}<br>R=%{customdata[2]:.3e}<br>"
                    "state probability=%{customdata[3]:.3f}<extra></extra>"
                ),
            ), row=1, col=column_number)
        fig.update_xaxes(title_text="T (bars, log scale)", type="log", row=1, col=column_number)
        fig.update_yaxes(
            title_text="TMV (threshold multiples, log scale)" if column_number == 1 else None,
            type="log",
            row=1,
            col=column_number,
        )

    fig.update_layout(
        title="Audit 2 — TMV–T geometry by filtered state",
        template="plotly_white",
        height=560,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.08, "xanchor": "left", "x": 0.0},
        margin={"l": 70, "r": 30, "t": 120, "b": 70},
    )
    return fig


def plot_hmm_probability_vs_log_r(hmm_events: pd.DataFrame) -> go.Figure:
    """Show how current log-R and the preceding posterior combine into the filtered fast-state probability."""
    required_columns = {
        "event_id", "log_r", "r", "p_fast_r", "previous_p_fast_r", "state_name", "sample", "t", "tmv",
    }
    _validate_hmm_audit_events(hmm_events, required_columns)

    state_colors = {"slow_R": "#2563eb", "fast_R": "#f97316"}
    samples = ("train", "oos")
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Training events", "OOS events"))

    for column_number, sample in enumerate(samples, start=1):
        sample_events = hmm_events.loc[hmm_events["sample"].eq(sample)]
        for state_name, state_color in state_colors.items():
            state_events = sample_events.loc[sample_events["state_name"].eq(state_name)]
            fig.add_trace(go.Scattergl(
                x=state_events["log_r"],
                y=state_events["p_fast_r"],
                mode="markers",
                name=state_name,
                legendgroup=state_name,
                showlegend=column_number == 1,
                marker={"color": state_color, "size": 6, "opacity": 0.55},
                customdata=state_events[
                    ["event_id", "previous_p_fast_r", "r", "t", "tmv"]
                ].to_numpy(),
                hovertemplate=(
                    "event=%{customdata[0]:.0f}<br>log(R)=%{x:.4f}<br>R=%{customdata[2]:.3e}<br>"
                    "previous p(fast_R)=%{customdata[1]:.3f}<br>current p(fast_R)=%{y:.3f}<br>"
                    "T=%{customdata[3]:.0f} bars<br>TMV=%{customdata[4]:.4f}<extra></extra>"
                ),
            ), row=1, col=column_number)
        fig.add_hline(y=0.5, line={"color": "#64748b", "dash": "dash", "width": 1}, row=1, col=column_number)
        fig.update_xaxes(title_text="Current log(R)", row=1, col=column_number)
        fig.update_yaxes(
            title_text="Filtered p(fast_R)" if column_number == 1 else None,
            range=[-0.02, 1.02],
            tickformat=".0%",
            row=1,
            col=column_number,
        )

    fig.update_layout(
        title="Audit 3 — current observation versus filtered fast-state probability",
        template="plotly_white",
        height=540,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.08, "xanchor": "left", "x": 0.0},
        margin={"l": 70, "r": 30, "t": 120, "b": 70},
    )
    return fig


def plot_hmm_event_time_strip(hmm_events: pd.DataFrame, train_event_count: int) -> go.Figure:
    """Plot R observations, filtered probabilities, and hard states against completed-event order."""
    required_columns = {
        "event_id", "information_time", "log_r", "r", "p_fast_r", "state_name", "state_probability", "sample",
    }
    _validate_hmm_audit_events(hmm_events, required_columns)
    if not 0 < train_event_count < len(hmm_events):
        raise ValueError("train_event_count must define a non-empty chronological train/OOS split.")

    state_colors = {"slow_R": "#2563eb", "fast_R": "#f97316"}
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.07,
        row_heights=[0.40, 0.40, 0.20],
        subplot_titles=("Observed log(R)", "Filtered p(fast_R)", "Hard filtered state"),
    )

    fig.add_trace(go.Scattergl(
        x=hmm_events["event_id"],
        y=hmm_events["log_r"],
        mode="lines+markers",
        name="log(R)",
        line={"color": "#475569", "width": 1},
        marker={"color": "#475569", "size": 3},
        customdata=hmm_events[["information_time", "r", "sample"]].to_numpy(),
        hovertemplate=(
            "event=%{x:.0f}<br>log(R)=%{y:.4f}<br>R=%{customdata[1]:.3e}<br>"
            "information time=%{customdata[0]}<br>sample=%{customdata[2]}<extra></extra>"
        ),
    ), row=1, col=1)

    fig.add_trace(go.Scattergl(
        x=hmm_events["event_id"],
        y=hmm_events["p_fast_r"],
        mode="lines",
        name="p(fast_R)",
        line={"color": "#f97316", "width": 1.5},
        customdata=hmm_events[["information_time", "log_r", "sample"]].to_numpy(),
        hovertemplate=(
            "event=%{x:.0f}<br>p(fast_R)=%{y:.3f}<br>log(R)=%{customdata[1]:.4f}<br>"
            "information time=%{customdata[0]}<br>sample=%{customdata[2]}<extra></extra>"
        ),
    ), row=2, col=1)
    fig.add_hline(y=0.5, line={"color": "#64748b", "dash": "dash", "width": 1}, row=2, col=1)

    for state_position, (state_name, state_color) in enumerate(state_colors.items()):
        state_events = hmm_events.loc[hmm_events["state_name"].eq(state_name)]
        fig.add_trace(go.Scattergl(
            x=state_events["event_id"],
            y=[state_position] * len(state_events),
            mode="markers",
            name=state_name,
            legendgroup=state_name,
            marker={"color": state_color, "size": 6, "symbol": "square"},
            customdata=state_events[
                ["information_time", "r", "p_fast_r", "state_probability", "sample"]
            ].to_numpy(),
            hovertemplate=(
                "event=%{x:.0f}<br>state=" + state_name + "<br>R=%{customdata[1]:.3e}<br>"
                "p(fast_R)=%{customdata[2]:.3f}<br>state probability=%{customdata[3]:.3f}<br>"
                "information time=%{customdata[0]}<br>sample=%{customdata[4]}<extra></extra>"
            ),
        ), row=3, col=1)

    oos_event_id = float(hmm_events.iloc[train_event_count]["event_id"])
    for row_number in (1, 2, 3):
        fig.add_vline(
            x=oos_event_id,
            line={"color": "#111827", "dash": "dash", "width": 1.25},
            row=row_number,
            col=1,
        )

    fig.update_yaxes(title_text="log(R)", row=1, col=1)
    fig.update_yaxes(title_text="p(fast_R)", range=[-0.02, 1.02], tickformat=".0%", row=2, col=1)
    fig.update_yaxes(title_text="State", tickvals=[0, 1], ticktext=["slow_R", "fast_R"], row=3, col=1)
    fig.update_xaxes(title_text="Completed-event order", row=3, col=1)
    fig.update_layout(
        title="Audit 4 — event-time observations, posterior, and state sequence",
        template="plotly_white",
        height=850,
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.03, "xanchor": "left", "x": 0.0},
        margin={"l": 80, "r": 30, "t": 120, "b": 70},
    )
    fig.add_annotation(
        x=oos_event_id,
        y=1.0,
        xref="x",
        yref="paper",
        text="OOS begins",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
    )
    return fig


def plot_hmm_model_label_shares(label_summary: pd.DataFrame) -> go.Figure:
    """Compare slow/fast event shares across HMM emission candidates in train and OOS."""
    required_columns = {"model", "sample", "state_name", "share", "event_count"}
    missing_columns = required_columns.difference(label_summary.columns)
    if missing_columns:
        raise KeyError(f"label_summary is missing required columns: {sorted(missing_columns)}")

    state_colors = {"slow_R": "#2563eb", "fast_R": "#f97316"}
    samples = ("train", "oos")
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Training events", "OOS events"))
    for column_number, sample in enumerate(samples, start=1):
        sample_summary = label_summary.loc[label_summary["sample"].eq(sample)]
        for state_name, state_color in state_colors.items():
            state_summary = sample_summary.loc[sample_summary["state_name"].eq(state_name)]
            fig.add_trace(go.Bar(
                x=state_summary["model"],
                y=state_summary["share"],
                name=state_name,
                legendgroup=state_name,
                showlegend=column_number == 1,
                marker={"color": state_color},
                customdata=state_summary[["event_count"]].to_numpy(),
                hovertemplate=(
                    "model=%{x}<br>state=" + state_name + "<br>share=%{y:.2%}<br>"
                    "events=%{customdata[0]:,.0f}<extra></extra>"
                ),
            ), row=1, col=column_number)
        fig.update_xaxes(title_text="Emission candidate", tickangle=-30, row=1, col=column_number)
        fig.update_yaxes(
            title_text="Event share" if column_number == 1 else None,
            range=[0, 1],
            tickformat=".0%",
            row=1,
            col=column_number,
        )

    fig.update_layout(
        title="HMM label distribution by emission candidate",
        template="plotly_white",
        barmode="stack",
        height=560,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.08, "xanchor": "left", "x": 0.0},
        margin={"l": 70, "r": 30, "t": 120, "b": 150},
    )
    return fig


def plot_hmm_label_agreement(agreement: pd.DataFrame, title: str) -> go.Figure:
    """Plot a square pairwise agreement or kappa matrix for HMM labels."""
    if agreement.empty or agreement.shape[0] != agreement.shape[1]:
        raise ValueError("agreement must be a non-empty square DataFrame.")
    if list(agreement.index) != list(agreement.columns):
        raise ValueError("agreement index and columns must contain the same ordered model names.")

    fig = go.Figure(go.Heatmap(
        z=agreement.to_numpy(dtype=float),
        x=agreement.columns,
        y=agreement.index,
        zmin=-1.0 if float(agreement.min().min()) < 0.0 else 0.0,
        zmax=1.0,
        colorscale="RdBu",
        reversescale=True,
        text=np.round(agreement.to_numpy(dtype=float), 3),
        texttemplate="%{text:.3f}",
        hovertemplate="model A=%{y}<br>model B=%{x}<br>value=%{z:.4f}<extra></extra>",
        colorbar={"title": "Agreement"},
    ))
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=650,
        width=760,
        margin={"l": 150, "r": 80, "t": 90, "b": 150},
    )
    fig.update_xaxes(tickangle=-35)
    return fig


def plot_hmm_model_event_strips(event_labels: pd.DataFrame, sample: str = "oos") -> go.Figure:
    """Show one equally weighted event-time state strip for each successful emission candidate."""
    required_columns = {"event_id", "model", "sample", "state_name", "p_fast_r"}
    missing_columns = required_columns.difference(event_labels.columns)
    if missing_columns:
        raise KeyError(f"event_labels is missing required columns: {sorted(missing_columns)}")

    sample_labels = event_labels.loc[event_labels["sample"].eq(sample)].copy()
    if sample_labels.empty:
        raise ValueError(f"No labels found for sample={sample!r}.")
    sample_labels["state_code"] = sample_labels["state_name"].map({"slow_R": 0.0, "fast_R": 1.0})
    state_matrix = sample_labels.pivot(index="model", columns="event_id", values="state_code")
    probability_matrix = sample_labels.pivot(index="model", columns="event_id", values="p_fast_r")

    customdata = np.stack([probability_matrix.to_numpy(dtype=float)], axis=-1)
    fig = go.Figure(go.Heatmap(
        z=state_matrix.to_numpy(dtype=float),
        x=state_matrix.columns,
        y=state_matrix.index,
        zmin=0.0,
        zmax=1.0,
        colorscale=[[0.0, "#2563eb"], [0.4999, "#2563eb"], [0.5, "#f97316"], [1.0, "#f97316"]],
        showscale=False,
        customdata=customdata,
        hovertemplate=(
            "model=%{y}<br>event=%{x:.0f}<br>state code=%{z:.0f}<br>"
            "p(fast_R)=%{customdata[0]:.3f}<extra></extra>"
        ),
    ))
    fig.update_layout(
        title=f"Event-time HMM labels across emission candidates — {sample.upper()}",
        template="plotly_white",
        height=max(360, 65 * len(state_matrix.index)),
        margin={"l": 180, "r": 30, "t": 90, "b": 70},
    )
    fig.update_xaxes(title="Completed-event order")
    fig.update_yaxes(title="Emission candidate")
    return fig


def plot_hmm_model_price_comparison(prices: pd.Series, bar_labels: pd.DataFrame, n_prices: int = 20_000) -> go.Figure:
    """Compare bar-time projections of several event-time HMM label sequences."""
    if prices.empty:
        raise ValueError("prices must not be empty.")
    if bar_labels.empty:
        raise ValueError("bar_labels must contain at least one model column.")
    if n_prices <= 0:
        raise ValueError(f"n_prices must be positive, got {n_prices}.")

    price_window = prices.tail(n_prices)
    label_window = bar_labels.reindex(price_window.index)
    model_names = list(label_window.columns)
    state_colors = {"slow_R": "#2563eb", "fast_R": "#f97316"}
    fig = make_subplots(
        rows=len(model_names),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=min(0.04, 0.18 / max(len(model_names), 1)),
        subplot_titles=model_names,
    )

    for row_number, model_name in enumerate(model_names, start=1):
        fig.add_trace(go.Scattergl(
            x=price_window.index,
            y=price_window.to_numpy(),
            mode="lines",
            name="Close",
            legendgroup="close",
            showlegend=row_number == 1,
            line={"color": "#cbd5e1", "width": 1},
            hovertemplate="time=%{x}<br>close=%{y:.5f}<extra></extra>",
        ), row=row_number, col=1)
        for state_name, state_color in state_colors.items():
            state_mask = label_window[model_name].eq(state_name)
            fig.add_trace(go.Scattergl(
                x=price_window.index[state_mask],
                y=price_window.loc[state_mask].to_numpy(),
                mode="markers",
                name=state_name,
                legendgroup=state_name,
                showlegend=row_number == 1,
                marker={"color": state_color, "size": 3, "opacity": 0.55},
                hovertemplate=(
                    "model=" + str(model_name) + "<br>time=%{x}<br>close=%{y:.5f}<br>"
                    "state=" + state_name + "<extra></extra>"
                ),
            ), row=row_number, col=1)
        fig.update_yaxes(title_text="Close", row=row_number, col=1)

    fig.update_xaxes(title_text="Time", row=len(model_names), col=1)
    fig.update_layout(
        title=f"Bar-time state projections by emission candidate — last {len(price_window):,} prices",
        template="plotly_white",
        height=max(700, 270 * len(model_names)),
        hovermode="closest",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.01, "xanchor": "left", "x": 0.0},
        margin={"l": 70, "r": 30, "t": 120, "b": 70},
    )
    return fig


def plot_hmm_next_event_outcomes(forward_events: pd.DataFrame, sample: str = "oos") -> go.Figure:
    """Compare next-event outcomes conditional on the state known at the current DCC confirmation."""
    required_columns = {
        "event_id", "next_event_id", "sample", "next_sample", "state_name", "next_r", "next_t", "next_tmv",
        "next_confirmation_gap_bars",
    }
    missing_columns = required_columns.difference(forward_events.columns)
    if missing_columns:
        raise KeyError(f"forward_events is missing required columns: {sorted(missing_columns)}")

    selected_events = forward_events.loc[
        forward_events["sample"].eq(sample) & forward_events["next_sample"].eq(sample)
    ].copy()
    if selected_events.empty:
        raise ValueError(f"No complete current-to-next event pairs found for sample={sample!r}.")

    state_colors = {"slow_R": "#2563eb", "fast_R": "#f97316"}
    outcome_specs = (
        ("next_r", "Next R", True),
        ("next_t", "Next T (bars)", True),
        ("next_tmv", "Next TMV", True),
        ("next_confirmation_gap_bars", "Bars until next DCC confirmation", True),
    )
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[spec[1] for spec in outcome_specs],
        vertical_spacing=0.16,
        horizontal_spacing=0.12,
    )

    for outcome_number, (column, axis_title, use_log_axis) in enumerate(outcome_specs):
        row_number = outcome_number // 2 + 1
        column_number = outcome_number % 2 + 1
        for state_name, state_color in state_colors.items():
            state_events = selected_events.loc[selected_events["state_name"].eq(state_name)]
            fig.add_trace(go.Box(
                x=[state_name] * len(state_events),
                y=state_events[column],
                name=state_name,
                legendgroup=state_name,
                showlegend=outcome_number == 0,
                marker={"color": state_color, "size": 4, "opacity": 0.5},
                line={"color": state_color},
                boxpoints="outliers",
                customdata=state_events[["event_id", "next_event_id"]].to_numpy(),
                hovertemplate=(
                    "current state=" + state_name + "<br>current event=%{customdata[0]:.0f}<br>"
                    "next event=%{customdata[1]:.0f}<br>value=%{y:.6g}<extra></extra>"
                ),
            ), row=row_number, col=column_number)
        fig.update_yaxes(title_text=axis_title, type="log" if use_log_axis else "linear",
                         row=row_number, col=column_number)
        fig.update_xaxes(title_text="Current filtered state", row=row_number, col=column_number)

    fig.update_layout(
        title=f"Next-event outcomes conditional on the current causal HMM state — {sample.upper()}",
        template="plotly_white",
        height=800,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.04, "xanchor": "left", "x": 0.0},
        margin={"l": 80, "r": 30, "t": 120, "b": 70},
    )
    return fig


def plot_hmm_next_state_calibration(calibration_summary: pd.DataFrame) -> go.Figure:
    """Plot OOS next-fast-state calibration for causal probability forecasts."""
    required_columns = {"model", "mean_predicted_probability", "observed_fast_rate", "event_count"}
    missing_columns = required_columns.difference(calibration_summary.columns)
    if missing_columns:
        raise KeyError(f"calibration_summary is missing required columns: {sorted(missing_columns)}")
    if calibration_summary.empty:
        raise ValueError("calibration_summary must not be empty.")

    fig = go.Figure()
    for model_name, model_summary in calibration_summary.groupby("model", sort=False):
        ordered_summary = model_summary.sort_values("mean_predicted_probability")
        fig.add_trace(go.Scatter(
            x=ordered_summary["mean_predicted_probability"],
            y=ordered_summary["observed_fast_rate"],
            mode="lines+markers",
            name=str(model_name),
            marker={"size": np.clip(np.sqrt(ordered_summary["event_count"]) * 1.5, 6, 18)},
            customdata=ordered_summary[["event_count"]].to_numpy(),
            hovertemplate=(
                "model=" + str(model_name) + "<br>mean forecast=%{x:.2%}<br>observed=%{y:.2%}<br>"
                "events=%{customdata[0]:,.0f}<extra></extra>"
            ),
        ))
    fig.add_trace(go.Scatter(
        x=[0.0, 1.0],
        y=[0.0, 1.0],
        mode="lines",
        name="Perfect calibration",
        line={"color": "#64748b", "dash": "dash", "width": 1},
        hoverinfo="skip",
    ))
    fig.update_layout(
        title="OOS calibration for the next event's fast-state probability",
        template="plotly_white",
        height=600,
        xaxis={"title": "Predicted probability of next fast_R", "range": [0, 1], "tickformat": ".0%"},
        yaxis={"title": "Observed next fast_R frequency", "range": [0, 1], "tickformat": ".0%"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.03, "xanchor": "left", "x": 0.0},
        margin={"l": 80, "r": 30, "t": 120, "b": 70},
    )
    return fig


def plot_hmm_recent_event_casebook(prices: pd.Series, casebook_events: pd.DataFrame) -> go.Figure:
    """Plot representative state transitions with causal DCC landmarks and retrospective outcomes."""
    required_columns = {
        "event_id", "transition_label", "state_name", "direction", "live_mode", "ext_start_idx",
        "ext_start_price", "ext_end_idx", "ext_end_price", "dcc_idx", "dcc_price", "tmv", "t", "r",
        "p_fast_r", "next_event_id", "next_ext_end_idx", "next_ext_end_price", "next_dcc_idx", "next_dcc_price",
        "next_state_name", "window_start", "window_end",
    }
    missing_columns = required_columns.difference(casebook_events.columns)
    if missing_columns:
        raise KeyError(f"casebook_events is missing required columns: {sorted(missing_columns)}")
    if prices.empty:
        raise ValueError("prices must not be empty.")
    if casebook_events.empty:
        raise ValueError("casebook_events must not be empty.")

    state_colors = {"slow_R": "#2563eb", "fast_R": "#f97316"}
    direction_colors = {"up": "#16a34a", "down": "#dc2626"}
    fig = make_subplots(
        rows=len(casebook_events),
        cols=1,
        vertical_spacing=min(0.05, 0.20 / len(casebook_events)),
        subplot_titles=[
            (
                f"{event.transition_label} | completed {event.direction} leg | "
                f"{event.live_mode} DCC ⇒ live {event.live_mode} | "
                f"TMV={event.tmv:.2f}, T={event.t:.0f}, R={event.r:.2e}, p(fast)={event.p_fast_r:.2f}"
            )
            for event in casebook_events.itertuples(index=False)
        ],
    )

    for row_number, event in enumerate(casebook_events.itertuples(index=False), start=1):
        price_window = prices.loc[event.window_start:event.window_end]
        state_color = state_colors[event.state_name]
        leg_color = direction_colors[event.direction]
        dcc_symbol = "triangle-down" if event.live_mode == "down" else "triangle-up"

        fig.add_trace(go.Scattergl(
            x=price_window.index,
            y=price_window.to_numpy(),
            mode="lines",
            name="Close",
            legendgroup="close",
            showlegend=row_number == 1,
            line={"color": "#64748b", "width": 1.2},
            hovertemplate="time=%{x}<br>close=%{y:.5f}<extra></extra>",
        ), row=row_number, col=1)
        fig.add_trace(go.Scatter(
            x=[event.ext_start_idx, event.ext_end_idx],
            y=[event.ext_start_price, event.ext_end_price],
            mode="lines+markers",
            name="Completed leg",
            legendgroup="completed_leg",
            showlegend=row_number == 1,
            line={"color": leg_color, "width": 2.5},
            marker={"color": leg_color, "size": 7, "symbol": "diamond"},
            hovertemplate="completed " + event.direction + " leg<br>time=%{x}<br>price=%{y:.5f}<extra></extra>",
        ), row=row_number, col=1)
        fig.add_trace(go.Scatter(
            x=[event.dcc_idx],
            y=[event.dcc_price],
            mode="markers",
            name="Current DCC (known now)",
            legendgroup="current_dcc",
            showlegend=row_number == 1,
            marker={"color": direction_colors[event.live_mode], "size": 9, "symbol": dcc_symbol},
            hovertemplate=(
                "current " + event.live_mode + " DCC<br>event=" + str(int(event.event_id)) +
                "<br>time=%{x}<br>price=%{y:.5f}<extra></extra>"
            ),
        ), row=row_number, col=1)
        fig.add_trace(go.Scatter(
            x=[event.next_ext_end_idx],
            y=[event.next_ext_end_price],
            mode="markers",
            name="Next extreme (hindsight)",
            legendgroup="next_extreme",
            showlegend=row_number == 1,
            marker={"color": "#7c3aed", "size": 8, "symbol": "x"},
            hovertemplate="next extreme — hindsight only<br>time=%{x}<br>price=%{y:.5f}<extra></extra>",
        ), row=row_number, col=1)
        fig.add_trace(go.Scatter(
            x=[event.next_dcc_idx],
            y=[event.next_dcc_price],
            mode="markers",
            name="Next DCC (hindsight)",
            legendgroup="next_dcc",
            showlegend=row_number == 1,
            marker={"color": "#111827", "size": 8, "symbol": "circle-open"},
            hovertemplate=(
                "next DCC — hindsight only<br>next event=" + str(int(event.next_event_id)) +
                "<br>next state=" + event.next_state_name + "<br>time=%{x}<br>price=%{y:.5f}<extra></extra>"
            ),
        ), row=row_number, col=1)

        fig.add_vrect(
            x0=event.dcc_idx,
            x1=event.next_dcc_idx,
            fillcolor=state_color,
            opacity=0.10,
            line_width=0,
            row=row_number,
            col=1,
        )
        fig.add_vline(
            x=event.dcc_idx,
            line={"color": direction_colors[event.live_mode], "dash": "dash", "width": 1.25},
            row=row_number,
            col=1,
        )
        fig.add_vline(
            x=event.next_dcc_idx,
            line={"color": "#111827", "dash": "dot", "width": 1.0},
            row=row_number,
            col=1,
        )
        fig.update_yaxes(title_text="Close", row=row_number, col=1)

    fig.update_xaxes(title_text="Time", row=len(casebook_events), col=1)
    fig.update_layout(
        title=(
            "Recent OOS DC/HMM casebook — shaded state starts at the current DCC; "
            "purple and black markers are hindsight"
        ),
        template="plotly_white",
        height=max(900, 340 * len(casebook_events)),
        hovermode="closest",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.01, "xanchor": "left", "x": 0.0},
        margin={"l": 80, "r": 30, "t": 140, "b": 70},
    )
    return fig

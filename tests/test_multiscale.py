import numpy as np
import pandas as pd

from dc_multiscale_research import build_multiscale_state


def oscillating_prices(rows: int = 420) -> pd.Series:
    phase = np.arange(rows, dtype=float) * (2.0 * np.pi / 28.0)
    values = 100.0 * np.exp(0.04 * np.sin(phase) + 0.0002 * np.arange(rows))
    index = pd.date_range("2024-01-01", periods=rows, freq="5min")
    return pd.Series(values, index=index, name="close")


def test_multiscale_state_is_prefix_invariant() -> None:
    prices = oscillating_prices()
    thresholds = (0.008, 0.014, 0.022)
    _, full, _ = build_multiscale_state(prices, thresholds, firing_window=20, include_scale_state=False)
    cutoff = prices.index[299]
    _, prefix, _ = build_multiscale_state(
        prices.loc[:cutoff], thresholds, firing_window=20, include_scale_state=False
    )

    common = prefix.index.intersection(full.index)
    columns = [
        "configuration_code",
        "direction_boundaries",
        "small_contiguous_breadth",
        "structural_regime",
        "dcc_count_this_bar",
    ]
    pd.testing.assert_frame_equal(full.loc[common, columns], prefix.loc[common, columns])
    assert full.loc[common, "feature_information_time"].eq(common).all()

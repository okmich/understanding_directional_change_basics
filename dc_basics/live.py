"""Causal live-development primitives shared by three-to-five-scale studies."""

import numpy as np
import pandas as pd


def build_causal_running_extreme(close: pd.Series, live: pd.DataFrame) -> pd.Series:
    """Return each live DC mode's high or low using information through that bar."""
    direction = live["direction"]
    mode_run_id = direction.ne(direction.shift()).cumsum()
    running_high = close.groupby(mode_run_id).cummax()
    running_low = close.groupby(mode_run_id).cummin()
    values = np.where(direction.eq(1.0), running_high, running_low)
    return pd.Series(values, index=close.index, dtype=np.float64).where(direction.notna())


def calculate_target_progress(price_values: np.ndarray | float, extreme_values: np.ndarray | float,
                              target_mode: str, theta: float) -> np.ndarray | float:
    """Measure signed progress toward the target mode's next DCC threshold."""
    if theta <= 0.0:
        raise ValueError("theta must be strictly positive.")
    if target_mode == "up":
        return (price_values - extreme_values) / extreme_values / theta
    if target_mode == "down":
        return (extreme_values - price_values) / extreme_values / theta
    raise ValueError(f"Unsupported target mode: {target_mode}")

"""Data loading and threshold-grid utilities shared by the notebooks."""

from pathlib import Path

import numpy as np
import pandas as pd


def validate_thresholds(thresholds: tuple[float, ...]) -> None:
    """Validate that a threshold ladder is finite, positive, and increasing."""
    if len(thresholds) < 2:
        raise ValueError("At least two thresholds are required.")
    if not all(np.isfinite(theta) and theta > 0.0 for theta in thresholds):
        raise ValueError("Thresholds must be finite and strictly positive.")
    if not all(left < right for left, right in zip(thresholds[:-1], thresholds[1:], strict=True)):
        raise ValueError("Thresholds must be strictly increasing.")


def ratio_ladder(start: float, ratio: float, threshold_count: int) -> tuple[float, ...]:
    """Construct a constant-ratio threshold ladder."""
    if start <= 0.0 or ratio <= 1.0 or threshold_count < 2:
        raise ValueError("A ratio ladder requires start > 0, ratio > 1, and at least two thresholds.")
    return tuple(start * ratio**index for index in range(threshold_count))


def load_close(data_root: Path, symbol: str, sampling_minutes: int = 5) -> pd.Series:
    """Load a positive, ordered close series and optionally downsample it causally."""
    path = data_root / f"{symbol}.parquet"
    raw = pd.read_parquet(path)
    if not isinstance(raw.index, pd.DatetimeIndex):
        if "time" not in raw.columns:
            raise TypeError(f"{path} needs a DatetimeIndex or time column.")
        raw = raw.set_index(pd.to_datetime(raw.pop("time")))
    raw = raw.sort_index()
    if raw.index.has_duplicates:
        raise ValueError(f"{symbol} has {raw.index.duplicated().sum():,} duplicate timestamps.")
    if "close" not in raw.columns:
        raise KeyError(f"{symbol} has no close column.")
    close = raw["close"].astype(np.float64).rename(symbol)
    if not np.isfinite(close.to_numpy()).all() or close.le(0.0).any():
        raise ValueError(f"{symbol} close prices must be finite and positive.")
    if sampling_minutes < 5 or sampling_minutes % 5:
        raise ValueError("sampling_minutes must be a multiple of the native five-minute interval.")
    if sampling_minutes > 5:
        rule = f"{sampling_minutes}min"
        close = close.resample(rule, label="right", closed="right").last().dropna()
        close.name = symbol
    return close


def threshold_catalog(thresholds: tuple[float, ...]) -> pd.DataFrame:
    """Describe an ordered threshold ladder without using future price data."""
    validate_thresholds(thresholds)
    records = []
    for index, theta in enumerate(thresholds):
        lower = thresholds[index - 1] if index else np.nan
        records.append({
            "threshold_index": index,
            "threshold_id": f"T{index + 1:02d}",
            "threshold": theta,
            "ratio_to_lower": theta / lower if index else np.nan,
        })
    return pd.DataFrame.from_records(records).set_index("threshold_index", drop=False)

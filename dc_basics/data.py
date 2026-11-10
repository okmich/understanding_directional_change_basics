"""Data loading and threshold-grid utilities shared by the notebooks."""

import os
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

DATA_ROOT_ENV_VAR = "DC_DATA_ROOT"
DATA_ROOT_FILE_NAME = ".dc_data_root"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
NATIVE_BAR_MINUTES = 5


def resolve_data_root(data_root: str | Path | None = None) -> Path:
    """Return the market-data directory without hard-coding a machine path.

    Resolution order:

    1. an explicit ``data_root`` argument;
    2. the ``DC_DATA_ROOT`` environment variable;
    3. the first non-empty line of a git-ignored ``.dc_data_root`` file at the
       repository root.

    The directory must contain one ``<SYMBOL>.parquet`` file per market.
    """
    source = "argument"
    candidate: str | Path | None = data_root
    if candidate is None and os.environ.get(DATA_ROOT_ENV_VAR):
        candidate, source = os.environ[DATA_ROOT_ENV_VAR], f"${DATA_ROOT_ENV_VAR}"
    if candidate is None:
        settings_path = REPOSITORY_ROOT / DATA_ROOT_FILE_NAME
        if settings_path.exists():
            lines = [line.strip() for line in settings_path.read_text(encoding="utf-8").splitlines()]
            candidate = next((line for line in lines if line and not line.startswith("#")), None)
            source = str(settings_path)
    if candidate is None:
        raise FileNotFoundError(
            "No market-data directory configured. Set the DC_DATA_ROOT environment variable, "
            f"or write the directory path on one line of {REPOSITORY_ROOT / DATA_ROOT_FILE_NAME}."
        )
    resolved = Path(candidate).expanduser()
    if source != "argument" and not source.startswith("$") and not resolved.is_absolute():
        resolved = REPOSITORY_ROOT / resolved  # a relative path in .dc_data_root means "from the repo root"
    if not resolved.is_dir():
        raise FileNotFoundError(f"Market-data directory from {source} does not exist: {resolved}")
    return resolved


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


def load_close(
    data_root: Path,
    symbol: str,
    sampling_minutes: int = NATIVE_BAR_MINUTES,
    bar_timestamp: Literal["open", "close"] = "open",
) -> pd.Series:
    """Load a positive, ordered close series and optionally downsample it causally.

    ``bar_timestamp`` states what each native timestamp means. MetaTrader-style
    exports (the FXPIG files used here) stamp a bar with its *open* time, so the
    close of the bar stamped 10:05 is first known at 10:10. Downsampling keeps
    the same convention: with ``"open"`` a 15-minute bar is labelled by its open
    and aggregates the native bars stamped [open, open + 15 min); with
    ``"close"`` it is labelled by its close and aggregates (close - 15 min, close].
    Either way the sampled close is the last native close inside the interval. A
    trailing interval that the data does not cover to its end is dropped: its last
    close is an intermediate price that would change once later bars arrive.
    """
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
    if sampling_minutes < NATIVE_BAR_MINUTES or sampling_minutes % NATIVE_BAR_MINUTES:
        raise ValueError("sampling_minutes must be a multiple of the native five-minute interval.")
    if bar_timestamp not in ("open", "close"):
        raise ValueError("bar_timestamp must be 'open' or 'close'.")
    if sampling_minutes > NATIVE_BAR_MINUTES:
        rule = f"{sampling_minutes}min"
        side = "left" if bar_timestamp == "open" else "right"
        last_native = close.index[-1]
        close = close.resample(rule, label=side, closed=side).last().dropna()
        if len(close):
            interval = pd.Timedelta(minutes=sampling_minutes)
            native = pd.Timedelta(minutes=NATIVE_BAR_MINUTES)
            # Timestamp of the last native bar that belongs inside the final interval.
            final_native = close.index[-1] + interval - native if bar_timestamp == "open" else close.index[-1]
            if last_native < final_native:
                close = close.iloc[:-1]
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

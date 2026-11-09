"""Completed-event ledger construction and causal invariants."""

from enum import Enum

import numpy as np
import pandas as pd


def enum_value(value: str | Enum) -> str:
    """Return the stable string value of a string or enum member."""
    return str(value.value) if isinstance(value, Enum) else str(value)


def prepare_event_ledger(source: pd.DataFrame, prefix: str, scale: str | Enum, theta: float) -> pd.DataFrame:
    """Attach stable IDs and information timestamps to completed DC events.

    The event's completed TMV, T, and R values become known only at ``dcc_idx``.
    The function verifies that identity and rejects duplicate information times.
    """
    scale_name = enum_value(scale)
    if source.empty:
        raise ValueError(f"No completed {scale_name}-threshold events were found.")
    ledger = source.copy()
    ledger.insert(0, "event_id", [f"{prefix}{number}" for number in range(1, len(ledger) + 1)])
    ledger.insert(1, "scale", scale_name)
    ledger.insert(2, "threshold", theta)
    ledger.insert(3, "information_time", ledger["dcc_idx"])
    if ledger["dcc_idx"].duplicated().any():
        raise AssertionError(f"{scale_name.title()} ledger contains duplicate DCC timestamps.")
    if ledger["ext_end_idx"].gt(ledger["information_time"]).any():
        raise AssertionError("An ending extreme occurs after its information time.")
    np.testing.assert_allclose(ledger["r"], ledger["tmv"] * theta / ledger["t"], rtol=1e-12, atol=1e-15)
    return ledger


def prepare_threshold_event_ledger(source: pd.DataFrame, threshold_id: str, threshold_index: int,
                                   theta: float) -> pd.DataFrame:
    """Attach stable arbitrary-N threshold IDs and causal information times."""
    if source.empty:
        raise ValueError(f"No completed events were found for {threshold_id}.")
    ledger = source.copy()
    event_ids = [f"{threshold_id}-E{number:05d}" for number in range(1, len(ledger) + 1)]
    ledger.insert(0, "event_id", event_ids)
    ledger.insert(1, "threshold_index", threshold_index)
    ledger.insert(2, "threshold_id", threshold_id)
    ledger.insert(3, "threshold", theta)
    ledger.insert(4, "information_time", ledger["dcc_idx"])
    if ledger["dcc_idx"].duplicated().any():
        raise AssertionError(f"{threshold_id} contains duplicate DCC timestamps.")
    np.testing.assert_allclose(ledger["r"], ledger["tmv"] * theta / ledger["t"], rtol=1e-12, atol=1e-15)
    return ledger

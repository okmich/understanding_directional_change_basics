"""Completed-event ledger construction and causal invariants."""

from enum import Enum

import numpy as np
import pandas as pd


def enum_value(value: str | Enum) -> str:
    """Return the stable string value of a string or enum member."""
    return str(value.value) if isinstance(value, Enum) else str(value)


_OPPOSITE_DIRECTION = {"up": "down", "down": "up"}


def add_direction_semantics(ledger: pd.DataFrame) -> pd.DataFrame:
    """Add explicit direction columns so a ledger row cannot be misread.

    The parser's ``direction`` is the direction of the *completed* leg. The DCC
    that completes an ``up`` leg is a *downward* confirmation, and it switches
    the live mode down. Three explicit columns make that visible:

    - ``completed_leg_direction``: the leg that ended (same as ``direction``);
    - ``dcc_direction``: the direction of the confirming DCC;
    - ``new_live_mode``: the mode that is live from ``information_time`` on.
    """
    directions = ledger["direction"].astype(str)
    unknown = sorted(set(directions) - set(_OPPOSITE_DIRECTION))
    if unknown:
        raise ValueError(f"Unexpected completed-leg direction values: {unknown}")
    ledger["completed_leg_direction"] = directions
    ledger["dcc_direction"] = directions.map(_OPPOSITE_DIRECTION)
    ledger["new_live_mode"] = ledger["dcc_direction"]
    return ledger


def prepare_event_ledger(source: pd.DataFrame, prefix: str, scale: str | Enum, theta: float) -> pd.DataFrame:
    """Attach stable IDs and information timestamps to completed DC events.

    The event's completed TMV, T, and R values become known only at ``dcc_idx``.
    The function verifies that identity and rejects duplicate information times.

    ``direction`` is the completed-leg direction. Use ``dcc_direction`` or
    ``new_live_mode`` for the direction of the confirmation itself.
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
    return add_direction_semantics(ledger)


def prepare_threshold_event_ledger(source: pd.DataFrame, threshold_id: str, threshold_index: int,
                                   theta: float) -> pd.DataFrame:
    """Attach stable arbitrary-N threshold IDs and causal information times.

    Applies the same invariants as :func:`prepare_event_ledger`.
    """
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
    if ledger["ext_end_idx"].gt(ledger["information_time"]).any():
        raise AssertionError(f"{threshold_id}: an ending extreme occurs after its information time.")
    np.testing.assert_allclose(ledger["r"], ledger["tmv"] * theta / ledger["t"], rtol=1e-12, atol=1e-15)
    return add_direction_semantics(ledger)

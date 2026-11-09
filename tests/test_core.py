import numpy as np
import pandas as pd

from dc_basics.core import dc_live_features, parse_dc_events
from dc_basics.events import prepare_event_ledger


def example_prices() -> pd.Series:
    values = np.array([100, 101, 103, 102, 100, 98, 99, 101, 104, 102, 99, 97, 100], dtype=float)
    index = pd.date_range("2024-01-01", periods=len(values), freq="5min")
    return pd.Series(values, index=index, name="close")


def test_completed_events_have_expected_timing_and_identity() -> None:
    prices = example_prices()
    theta = 0.02
    events = parse_dc_events(prices, theta)

    assert events["direction"].tolist() == ["up", "down", "up", "down"]
    assert events["dcc_pos"].tolist() == [4, 7, 10, 12]
    assert events["ext_end_pos"].tolist() == [2, 5, 8, 11]
    assert events["ext_end_pos"].le(events["dcc_pos"]).all()
    np.testing.assert_allclose(events["r"], events["tmv"] * theta / events["t"])


def test_event_ledger_marks_dcc_as_information_time() -> None:
    prices = example_prices()
    theta = 0.02
    events = parse_dc_events(prices, theta)
    ledger = prepare_event_ledger(events, "S", "small", theta)

    assert ledger["event_id"].tolist() == ["S1", "S2", "S3", "S4"]
    pd.testing.assert_series_equal(
        ledger["information_time"], ledger["dcc_idx"], check_names=False
    )
    assert ledger["ext_end_idx"].le(ledger["information_time"]).all()


def test_live_dcc_flags_align_with_completed_event_confirmations() -> None:
    prices = example_prices()
    events = parse_dc_events(prices, theta=0.02)
    live = dc_live_features(prices, theta=0.02)

    downward_times = events.loc[events["direction"].eq("up"), "dcc_idx"]
    upward_times = events.loc[events["direction"].eq("down"), "dcc_idx"]
    assert live.index[live["downward_dcc"]].tolist() == downward_times.tolist()
    assert live.index[live["upward_dcc"]].tolist() == upward_times.tolist()

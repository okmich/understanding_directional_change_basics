import numpy as np
import pandas as pd

from dc_multiscale_research import (
    DEFAULT_MAX_POINT_MASS_SHARE,
    FeatureTier,
    ModelFamily,
    ObservationClock,
    StructuralRegime,
    block_bootstrap_omega_difference,
    build_multiscale_state,
    emission_feature_contributions,
    emission_feature_log_density,
    fit_candidate,
    incremental_usefulness,
    omega_squared,
    permutation_omega_test,
    prepare_data,
    semantic_state_map,
    semantic_state_name,
    training_classes_without_state,
)


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


def test_feature_preparation_preserves_fragmented_rows_and_uses_continuous_emissions() -> None:
    rows = 2_000
    positions = np.arange(rows, dtype=float)
    values = 100.0 * np.exp(
        0.018 * np.sin(2.0 * np.pi * positions / 47.0)
        + 0.011 * np.sin(2.0 * np.pi * positions / 113.0)
        + 0.004 * np.sin(2.0 * np.pi * positions / 17.0)
    )
    prices = pd.Series(values, index=pd.date_range("2024-01-01", periods=rows, freq="5min"), name="close")
    thresholds = (0.005, 0.009, 0.014, 0.021, 0.032)
    _, global_state, _ = build_multiscale_state(
        prices, thresholds, firing_window=50, include_scale_state=False
    )
    prepared = prepare_data(global_state, ObservationClock.UNION_EVENT, FeatureTier.DYNAMIC)

    fragmented = StructuralRegime.FRAGMENTED.value
    assert global_state.loc[global_state["union_event"], "structural_regime"].eq(fragmented).any()
    assert prepared.frame["structural_regime"].eq(fragmented).any()
    assert prepared.dropped_regime_counts[fragmented] == 0
    assert prepared.dropped_rows == 0
    assert all(prepared.frames["train"][column].nunique() >= 3 for column in prepared.feature_columns)

    forbidden_tokens = ("mode_sign", "fragmentation", "counter_depth", "direction_boundaries", "dcc_rate")
    assert not any(token in column for column in prepared.feature_columns for token in forbidden_tokens)

    fit = fit_candidate(prepared, ModelFamily.KMEANS, n_states=4, random_state=17)
    assert fit.error is None
    expected_scale = np.median(fit.model.transform(prepared.arrays["train"]))
    assert np.isclose(fit.confidence_scale, expected_scale)


def test_semantic_mapping_leaves_surplus_states_unmatched() -> None:
    states = np.array([0, 0, 1, 1, 2, 3], dtype=np.int64)
    baseline_codes = np.array([0, 0, 1, 1, 0, 1], dtype=np.int64)
    mapping = semantic_state_map(states, baseline_codes, n_states=5)

    assert sum(code is None for code in mapping.values()) == 3
    assert {code for code in mapping.values() if code is not None} == {0, 1}
    assert mapping[4] is None
    assert semantic_state_name(None) == "unmatched"


def test_omega_squared_and_permutation_evidence_distinguish_a_strong_group_effect() -> None:
    rng = np.random.default_rng(17)
    labels = pd.Series(np.repeat(["a", "b"], 100))
    no_effect = pd.Series(rng.normal(size=200))
    strong_effect = pd.Series(np.r_[rng.normal(-3.0, 0.2, 100), rng.normal(3.0, 0.2, 100)])

    assert omega_squared(no_effect, labels) < 0.02
    assert omega_squared(strong_effect, labels) > 0.95
    evidence = permutation_omega_test(strong_effect, labels, n_permutations=99, random_state=17)
    assert evidence["omega_squared"] > evidence["null_p95"]
    assert evidence["permutation_p_value"] <= 0.02


def layered_prices(rows: int = 2_000) -> pd.Series:
    positions = np.arange(rows, dtype=float)
    values = 100.0 * np.exp(
        0.018 * np.sin(2.0 * np.pi * positions / 47.0)
        + 0.011 * np.sin(2.0 * np.pi * positions / 113.0)
        + 0.004 * np.sin(2.0 * np.pi * positions / 17.0)
    )
    return pd.Series(values, index=pd.date_range("2024-01-01", periods=rows, freq="5min"), name="close")


def test_point_mass_screen_removes_zero_inflated_features_with_reasons() -> None:
    _, global_state, _ = build_multiscale_state(
        layered_prices(), (0.005, 0.009, 0.014, 0.021, 0.032), firing_window=50, include_scale_state=False
    )
    screened = prepare_data(global_state, ObservationClock.UNION_EVENT, FeatureTier.DYNAMIC)
    unscreened = prepare_data(
        global_state, ObservationClock.UNION_EVENT, FeatureTier.DYNAMIC, max_point_mass_share=None
    )

    assert set(screened.feature_columns) <= set(unscreened.feature_columns)
    assert set(screened.removed_feature_columns) == set(screened.removed_feature_reasons)
    for column in screened.feature_columns:
        assert screened.training_point_mass_share[column] < DEFAULT_MAX_POINT_MASS_SHARE
    point_mass_removed = [
        column for column, reason in screened.removed_feature_reasons.items() if reason.startswith("point_mass")
    ]
    for column in point_mass_removed:
        assert screened.training_point_mass_share[column] >= DEFAULT_MAX_POINT_MASS_SHARE
        assert column in unscreened.feature_columns
    assert screened.dropped_rows == unscreened.dropped_rows


def test_per_feature_log_density_reconstructs_mixture_component_density() -> None:
    _, global_state, _ = build_multiscale_state(
        layered_prices(), (0.005, 0.009, 0.014, 0.021, 0.032), firing_window=50, include_scale_state=False
    )
    prepared = prepare_data(global_state, ObservationClock.UNION_EVENT, FeatureTier.DYNAMIC)
    fit = fit_candidate(prepared, ModelFamily.GAUSSIAN_MIXTURE, n_states=3, random_state=17)
    assert fit.error is None

    values = prepared.arrays["validation"]
    per_feature = emission_feature_log_density(fit, values)
    assert per_feature.shape == (len(values), 3, len(prepared.feature_columns))
    weights = np.log(fit.model.weights_)
    mixture_log_density = np.logaddexp.reduce(per_feature.sum(axis=2) + weights[None, :], axis=1)
    np.testing.assert_allclose(mixture_log_density, fit.model.score_samples(values), rtol=1e-9, atol=1e-9)

    table = emission_feature_contributions(fit, prepared, "validation")
    assert list(table.index.sort_values()) == sorted(prepared.feature_columns)
    np.testing.assert_allclose(table["share_of_total_gain"].sum(), 1.0)
    training_classes = prepared.frames["train"]["structural_regime"].nunique()
    missing = training_classes_without_state(fit, prepared)
    assert len(missing) >= training_classes - fit.n_states
    assert set(missing) <= set(prepared.frames["train"]["structural_regime"])


def test_block_bootstrap_verdicts_separate_real_and_absent_increments() -> None:
    rng = np.random.default_rng(5)
    rows = 600
    baseline = pd.Series(np.repeat(["a", "b"], rows // 2))
    model = pd.Series(np.tile(np.repeat(["x", "y", "z"], 20), rows // 60))
    noise = rng.normal(scale=0.3, size=rows)
    model_effect = pd.Series(model.map({"x": -2.0, "y": 0.0, "z": 2.0}).to_numpy() + noise)
    frame = pd.DataFrame({"model": model, "baseline": baseline, "signal": model_effect,
                          "same": baseline.map({"a": -1.0, "b": 1.0}).to_numpy() + noise})
    frame["model_copy"] = frame["baseline"]

    interval = block_bootstrap_omega_difference(
        frame["signal"], frame["model"], frame["baseline"], n_bootstrap=99, block_length=20
    )
    assert interval["ci_low"] > 0.0
    table = incremental_usefulness(
        frame, ["signal", "same"], "model", {"direct": "baseline"}, n_bootstrap=99, block_length=20
    )
    assert table.loc["signal", "verdict"] == "adds_beyond_baselines"
    assert table.loc["same", "verdict"] == "baseline_separates_more"
    renamed = incremental_usefulness(
        frame, ["same"], "model_copy", {"direct": "baseline"}, n_bootstrap=99, block_length=20
    )
    assert renamed.loc["same", "model_minus_best_baseline"] == 0.0
    assert renamed.loc["same", "verdict"] == "no_information_beyond_baseline"


def test_frozen_feature_columns_transfer_a_pilot_feature_set_unchanged() -> None:
    thresholds = (0.005, 0.009, 0.014, 0.021, 0.032)
    _, pilot_state, _ = build_multiscale_state(layered_prices(), thresholds, firing_window=50, include_scale_state=False)
    pilot = prepare_data(pilot_state, ObservationClock.UNION_EVENT, FeatureTier.DYNAMIC)
    other_prices = layered_prices(2_400).iloc[400:] * 1.1
    _, other_state, _ = build_multiscale_state(other_prices, thresholds, firing_window=50, include_scale_state=False)
    transferred = prepare_data(
        other_state, ObservationClock.UNION_EVENT, FeatureTier.DYNAMIC,
        frozen_feature_columns=pilot.feature_columns,
    )

    assert transferred.feature_columns == pilot.feature_columns
    assert all(
        reason == "not_in_frozen_feature_set" for reason in transferred.removed_feature_reasons.values()
    )
    assert set(transferred.training_point_mass_share) >= set(pilot.feature_columns)

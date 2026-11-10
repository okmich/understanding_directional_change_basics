import numpy as np
import pytest


pomegranate = pytest.importorskip("pomegranate")

from dc_basics.hmm import DistType, InferenceMode, create_simple_hmm_instance


def test_filtered_probabilities_are_prefix_invariant() -> None:
    random = np.random.default_rng(17)
    observations = np.r_[random.normal(-1.0, 0.25, 80), random.normal(1.0, 0.25, 80)].reshape(-1, 1)
    model = create_simple_hmm_instance(
        DistType.NORMAL,
        n_states=2,
        random_state=17,
        max_iter=10,
        inference_mode=InferenceMode.FILTERING,
        covariance_type="diag",
        min_cov=1e-5,
        n_restarts=1,
    )
    model.fit(observations[:100])
    full = model.predict_proba(observations)
    prefix = model.predict_proba(observations[:120])
    np.testing.assert_allclose(full[:120], prefix, rtol=1e-10, atol=1e-12)


from dc_basics.hmm_support import (  # noqa: E402
    create_hmm_instance,
    density_is_over_log_r,
    raw_r_predictive_loglik,
    semantic_r_state_order,
)


def _two_regime_positive_series(seed: int = 3) -> np.ndarray:
    """Positive R-like observations near exp(-9), with a slow and a fast regime."""
    random = np.random.default_rng(seed)
    log_values = np.r_[random.normal(-9.6, 0.3, 120), random.normal(-8.1, 0.3, 60), random.normal(-9.6, 0.3, 120)]
    return np.exp(log_values).reshape(-1, 1)


def _fit(dist_type: DistType, observations: np.ndarray, seed: int = 11):
    model = create_hmm_instance(
        dist_type,
        n_states=2,
        random_state=seed,
        max_iter=50,
        inference_mode=InferenceMode.FILTERING,
        covariance_type="diag",
        min_cov=1e-6,
        n_restarts=1,
    )
    return model.fit(observations[:240])


def test_density_is_over_log_r_covers_lognormal() -> None:
    assert density_is_over_log_r(DistType.NORMAL, observations_are_log_r=True)
    assert density_is_over_log_r(DistType.LOGNORMAL, observations_are_log_r=False)
    assert not density_is_over_log_r(DistType.GAMMA, observations_are_log_r=False)


def test_lognormal_on_raw_r_matches_normal_on_log_r_after_jacobian() -> None:
    raw_r = _two_regime_positive_series()
    log_values = np.log(raw_r)
    normal = _fit(DistType.NORMAL, log_values)
    lognormal = _fit(DistType.LOGNORMAL, raw_r)

    normal_scores = raw_r_predictive_loglik(normal, log_values, raw_r, observations_are_log_r=True)
    lognormal_scores = raw_r_predictive_loglik(lognormal, raw_r, raw_r, observations_are_log_r=False)
    assert abs(normal_scores[240:].mean() - lognormal_scores[240:].mean()) < 1e-3

    # pomegranate's LogNormal density is over log R: without the Jacobian it is off by mean(-log R).
    uncorrected = lognormal.compute_per_bar_predictive_loglik(raw_r)
    np.testing.assert_allclose(uncorrected - lognormal_scores, np.log(raw_r).reshape(-1), rtol=0, atol=1e-9)


def test_lognormal_fit_is_seeded_and_starts_from_log_space_clusters() -> None:
    raw_r = _two_regime_positive_series()
    first = _fit(DistType.LOGNORMAL, raw_r, seed=5)
    second = _fit(DistType.LOGNORMAL, raw_r, seed=5)
    first_means = np.sort([float(np.ravel(parameters["means"])[0]) for parameters in first.parameters])
    second_means = np.sort([float(np.ravel(parameters["means"])[0]) for parameters in second.parameters])
    np.testing.assert_array_equal(first_means, second_means)
    np.testing.assert_allclose(first_means, [-9.6, -8.1], atol=0.25)
    hard_states = first.predict_proba(raw_r).argmax(axis=1)
    assert np.unique(hard_states).size == 2


def test_semantic_r_state_order_uses_weighted_raw_r_on_training_rows() -> None:
    probabilities = np.array([[0.9, 0.1], [0.8, 0.2], [0.1, 0.9], [0.2, 0.8]])
    raw_r = np.array([5.0, 6.0, 1.0, 2.0])
    order, centers = semantic_r_state_order(probabilities, raw_r)
    assert order.tolist() == [1, 0]
    assert centers[0] < centers[1]

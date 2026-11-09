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

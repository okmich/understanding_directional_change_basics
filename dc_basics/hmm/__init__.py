"""Local HMM API used by the directional-change notebooks.

Only the single-distribution HMM factory used in this research journey is
exposed. Mixture HMMs and unrelated models from the source monorepo are
intentionally excluded so this folder remains independently extractable.
"""

from .pomegranate import PomegranateHMM
from .util import DistType, InferenceMode

_REMOVED_HSMM_KWARGS = frozenset({"duration_model", "duration_type", "max_duration"})


def create_simple_hmm_instance(dist_type: DistType, n_states: int = 3, *, random_state: int = 100,
                               max_iter: int = 100, inference_mode: InferenceMode = InferenceMode.FILTERING,
                               covariance_type: str = "full", min_cov: float | None = None,
                               **dist_kwargs) -> PomegranateHMM:
    """Construct the single-distribution pomegranate HMM used in the notebooks."""
    unsupported = _REMOVED_HSMM_KWARGS & dist_kwargs.keys()
    if unsupported:
        names = sorted(unsupported)
        raise TypeError(f"HSMM support was removed; unsupported arguments: {names}.")

    distributions_with_covariance = {DistType.NORMAL, DistType.STUDENTT, DistType.LOGNORMAL}
    if dist_type in distributions_with_covariance:
        dist_kwargs["covariance_type"] = covariance_type
        if min_cov is not None:
            dist_kwargs["min_cov"] = min_cov

    return PomegranateHMM(
        distribution_type=dist_type,
        n_states=n_states,
        random_state=random_state,
        max_iter=max_iter,
        inference_mode=inference_mode,
        **dist_kwargs,
    )


__all__ = [
    "DistType",
    "InferenceMode",
    "PomegranateHMM",
    "create_simple_hmm_instance",
]

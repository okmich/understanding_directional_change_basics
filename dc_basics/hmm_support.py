"""Local, non-vendored helpers for the one-threshold HMM labs.

The files under ``dc_basics/hmm`` are byte-identical copies of the signalfoundry
source (see ``VENDORED_FROM.md``) and must not be edited here. This module holds
the small corrections and shared conventions the notebooks need on top of them:

- :class:`LogSpaceInitHMM` starts LogNormal emissions from a *seeded* k-means
  pass on ``log(X)``. The vendored builder starts every LogNormal state from an
  unseeded ``mu ~ N(0, 1)``, ``sigma ~ U(0.2, 1.0)`` and ignores
  ``covariance_type`` / ``min_cov``. For directional-change R, ``log R`` sits
  near -9, so EM started many standard deviations from the data and the fit was
  neither reproducible nor reliably two-state.
- :func:`raw_r_predictive_loglik` puts every candidate's predictive
  log-likelihood on the raw-R density scale. pomegranate's
  ``LogNormal.log_probability`` returns the density of ``log X`` (it omits the
  ``-log X`` Jacobian), so a LogNormal score needs the same correction as a
  model fitted directly to ``log R``.
- :func:`semantic_r_state_order` is the one rule that names event-velocity
  states: ``slow_R`` is the state with the lower filtered-probability-weighted
  mean of raw R on the training events.
- :func:`configure_reproducible_threads` pins thread counts so reruns do not
  depend on machine load.

Importing this module requires PyTorch and pomegranate.
"""

from __future__ import annotations

import os

import numpy as np
import torch
from pomegranate.distributions import LogNormal

from .hmm import DistType, InferenceMode, PomegranateHMM, create_simple_hmm_instance

SEMANTIC_R_STATE_NAMES: tuple[str, str] = ("slow_R", "fast_R")
THREAD_ENVIRONMENT_VARIABLES: tuple[str, ...] = (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)


def configure_reproducible_threads(n_threads: int = 1) -> dict[str, str | int]:
    """Pin PyTorch and BLAS thread counts so EM reductions run in a fixed order.

    The BLAS variables only take effect if they are set before NumPy is first
    imported; the notebooks therefore also set them in their first code cell.
    ``torch.set_num_threads`` takes effect immediately.
    """
    if n_threads < 1:
        raise ValueError("n_threads must be at least 1.")
    for variable in THREAD_ENVIRONMENT_VARIABLES:
        os.environ[variable] = str(n_threads)
    torch.set_num_threads(n_threads)
    settings: dict[str, str | int] = {variable: os.environ[variable] for variable in THREAD_ENVIRONMENT_VARIABLES}
    settings["torch_num_threads"] = torch.get_num_threads()
    return settings


class LogSpaceInitHMM(PomegranateHMM):
    """PomegranateHMM whose LogNormal emissions start from seeded k-means on ``log(X)``.

    Every other distribution type behaves exactly like the vendored
    :class:`~dc_basics.hmm.PomegranateHMM`. For LogNormal emissions:

    - each restart and covariance retry runs k-means on ``log(X)`` with that
      start's seed, so the fit is reproducible for a fixed ``random_state``;
    - each state starts at its cluster's log-space mean and variance;
    - ``covariance_type`` (``"full"`` or ``"diag"``) and ``min_cov`` are honoured.
    """

    def _compute_init_stats(self, X: np.ndarray) -> dict:
        if self.distribution_type != DistType.LOGNORMAL:
            return super()._compute_init_stats(X)
        values = np.asarray(X, dtype=np.float64)
        if values.ndim == 1:
            values = values.reshape(-1, 1)
        if not np.all(np.isfinite(values)) or np.any(values <= 0.0):
            raise ValueError("LogNormal emissions need every value of X to be finite and strictly positive.")
        return self._compute_kmeans_init(np.log(values))

    def _lognormal_covariance_config(self) -> tuple[str, float]:
        covariance_type = str(self.dist_kwargs.get("covariance_type", "full")).lower()
        if covariance_type not in {"full", "diag"}:
            raise ValueError("LogSpaceInitHMM supports covariance_type 'full' or 'diag' for LogNormal emissions.")
        min_cov = self.dist_kwargs.get("min_cov")
        min_cov = 1e-12 if min_cov is None else max(float(min_cov), 1e-12)
        return covariance_type, min_cov

    def _build_distribution(self, k: int):
        stats = getattr(self, "_kmeans_stats", None)
        if self.distribution_type != DistType.LOGNORMAL or not isinstance(stats, dict) or "centroids" not in stats:
            return super()._build_distribution(k)
        covariance_type, min_cov = self._lognormal_covariance_config()
        means = np.asarray(stats["centroids"][k], dtype=np.float64).copy()
        if covariance_type == "diag":
            covs = np.maximum(np.asarray(stats["covs_diag"][k], dtype=np.float64), min_cov)
        else:
            covs = np.asarray(stats["covs_full"][k], dtype=np.float64).copy()
            covs[np.diag_indices_from(covs)] = np.maximum(np.diag(covs), min_cov)
        return LogNormal(
            means=means,
            covs=covs,
            covariance_type=covariance_type,
            min_cov=min_cov,
            dtype=torch.float64,
        )


def create_hmm_instance(dist_type: DistType, n_states: int = 3, *, random_state: int = 100,
                        max_iter: int = 100, inference_mode: InferenceMode = InferenceMode.FILTERING,
                        covariance_type: str = "full", min_cov: float | None = None,
                        **dist_kwargs) -> PomegranateHMM:
    """Drop-in replacement for ``create_simple_hmm_instance`` with seeded LogNormal starts.

    Non-LogNormal distributions are returned unchanged from the vendored factory.
    """
    model = create_simple_hmm_instance(
        dist_type,
        n_states,
        random_state=random_state,
        max_iter=max_iter,
        inference_mode=inference_mode,
        covariance_type=covariance_type,
        min_cov=min_cov,
        **dist_kwargs,
    )
    if dist_type != DistType.LOGNORMAL:
        return model
    return LogSpaceInitHMM(
        distribution_type=dist_type,
        n_states=n_states,
        random_state=random_state,
        max_iter=max_iter,
        n_restarts=model.n_restarts,
        inference_mode=model.inference_mode,
        **model.dist_kwargs,
    )


def density_is_over_log_r(dist_type: DistType, observations_are_log_r: bool) -> bool:
    """Return True when a model's emission density is a density of ``log R``.

    That holds for any model fitted to ``log R`` and also for pomegranate's
    LogNormal fitted to raw R, whose ``log_probability`` evaluates the Normal
    density of ``log R`` without the ``-log R`` Jacobian.
    """
    return bool(observations_are_log_r) or dist_type == DistType.LOGNORMAL


def raw_r_predictive_loglik(model: PomegranateHMM, observations: np.ndarray, raw_r: np.ndarray,
                            observations_are_log_r: bool) -> np.ndarray:
    """One-step-ahead predictive log-density of each event's raw R, ``log p(R_n | R_1..R_{n-1})``.

    Densities of ``log R`` are converted with the change-of-variables term
    ``log p_R(r) = log p_{log R}(log r) - log r`` so that every candidate is
    scored on the same raw-R scale.
    """
    scores = np.asarray(model.compute_per_bar_predictive_loglik(observations), dtype=np.float64)
    raw = np.asarray(raw_r, dtype=np.float64).reshape(-1)
    if raw.shape[0] != scores.shape[0]:
        raise ValueError("raw_r must contain one value per observation.")
    if density_is_over_log_r(model.distribution_type, observations_are_log_r):
        if np.any(raw <= 0.0):
            raise ValueError("Raw R must be strictly positive for the log-R Jacobian.")
        scores = scores - np.log(raw)
    return scores


def weighted_state_centers(probabilities: np.ndarray, raw_values: np.ndarray) -> np.ndarray:
    """Probability-weighted mean of ``raw_values`` for each state column."""
    probabilities = np.asarray(probabilities, dtype=np.float64)
    raw_values = np.asarray(raw_values, dtype=np.float64).reshape(-1)
    if probabilities.ndim != 2 or probabilities.shape[0] != raw_values.shape[0]:
        raise ValueError("probabilities must be (n_events, n_states) and match raw_values.")
    weights = probabilities.sum(axis=0)
    if np.any(weights <= 0.0):
        raise ValueError("At least one fitted state has zero posterior mass in training.")
    return (probabilities * raw_values[:, None]).sum(axis=0) / weights


def semantic_r_state_order(train_probabilities: np.ndarray, train_raw_r: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Order raw HMM states from slow to fast using training rows only.

    Returns ``(raw_state_order, ordered_centers)``: ``raw_state_order[0]`` is the
    raw state named ``slow_R`` (lower filtered-probability-weighted mean raw R
    over the training events) and ``raw_state_order[-1]`` is ``fast_R``.
    """
    centers = weighted_state_centers(train_probabilities, train_raw_r)
    order = np.argsort(centers, kind="stable")
    return order, centers[order]


__all__ = [
    "SEMANTIC_R_STATE_NAMES",
    "THREAD_ENVIRONMENT_VARIABLES",
    "LogSpaceInitHMM",
    "configure_reproducible_threads",
    "create_hmm_instance",
    "density_is_over_log_r",
    "raw_r_predictive_loglik",
    "semantic_r_state_order",
    "weighted_state_centers",
]

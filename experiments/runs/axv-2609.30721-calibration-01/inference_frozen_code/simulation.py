"""Synthetic paired classifier predictions with sliding-window dependence.

The data-generating process is a Gaussian latent-variable model. The shared
window term is constructed from raw sample shocks.  Raw shocks may be IID or a
stationary AR(1), so dependence can arise both from shared samples and from
correlation beyond the mechanical overlap span.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

import numpy as np
from numpy.typing import NDArray
from scipy.signal import lfilter
from scipy.stats import norm


FloatArray = NDArray[np.float64]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration for one independently generated synthetic test set."""

    n_subjects: int = 24
    n_sessions: int = 2
    base_nonoverlap_windows: int = 64
    window_size: int = 64
    overlap: float = 0.75
    accuracy_a: float = 0.80
    accuracy_b: float = 0.80
    sigma_subject: float = 0.45
    sigma_session: float = 0.25
    sigma_window: float = 0.75
    sigma_model: float = 0.60
    rho_pair: float = 0.50
    raw_ar_phi: float = 0.0

    def __post_init__(self) -> None:
        if self.n_subjects < 2:
            raise ValueError("n_subjects must be at least 2")
        if self.n_sessions < 1 or self.base_nonoverlap_windows < 2:
            raise ValueError(
                "n_sessions >= 1 and base_nonoverlap_windows >= 2 are required"
            )
        if self.window_size < 2:
            raise ValueError("window_size must be at least 2")
        if not 0.0 <= self.overlap < 1.0:
            raise ValueError("overlap must be in [0, 1)")
        if not 0.0 < self.accuracy_a < 1.0 or not 0.0 < self.accuracy_b < 1.0:
            raise ValueError("accuracies must be strictly between 0 and 1")
        if not 0.0 <= self.rho_pair <= 1.0:
            raise ValueError("rho_pair must be in [0, 1]")
        if not -1.0 < self.raw_ar_phi < 1.0:
            raise ValueError("raw_ar_phi must be strictly between -1 and 1")
        scales = (
            self.sigma_subject,
            self.sigma_session,
            self.sigma_window,
            self.sigma_model,
        )
        if any(value < 0 for value in scales) or not any(value > 0 for value in scales):
            raise ValueError("standard deviations must be nonnegative and not all zero")

    @property
    def stride(self) -> int:
        return max(1, int(round(self.window_size * (1.0 - self.overlap))))

    @property
    def realized_overlap(self) -> float:
        return 1.0 - self.stride / self.window_size

    @property
    def raw_length(self) -> int:
        """Fixed raw duration shared by all overlap conditions."""

        return self.base_nonoverlap_windows * self.window_size

    @property
    def n_windows(self) -> int:
        return 1 + (self.raw_length - self.window_size) // self.stride

    @property
    def overlap_span_windows(self) -> int:
        """Interpretable default block length ceil(L / S)."""

        return ceil(self.window_size / self.stride)

    @property
    def total_latent_variance(self) -> float:
        return (
            self.sigma_subject**2
            + self.sigma_session**2
            + self.sigma_window**2
            + self.sigma_model**2
        )

    @property
    def raw_window_sum_variance(self) -> float:
        """Analytic variance of one length-L sum from the raw process."""

        return ar1_window_sum_variance(self.window_size, self.raw_ar_phi)


@dataclass(frozen=True)
class SimulatedPredictions:
    """Paired correctness indicators with shape (subject, session, window)."""

    correct_a: BoolArray
    correct_b: BoolArray
    config: SimulationConfig

    @property
    def true_values(self) -> dict[str, float]:
        return {
            "accuracy_a": self.config.accuracy_a,
            "accuracy_b": self.config.accuracy_b,
            "difference": self.config.accuracy_a - self.config.accuracy_b,
        }

    def statistic_tensor(self) -> FloatArray:
        """Return A, B, and paired A-B observations in the last dimension."""

        a = self.correct_a.astype(np.float64)
        b = self.correct_b.astype(np.float64)
        return np.stack((a, b, a - b), axis=-1)


def _paired_normal(
    shape: tuple[int, ...], rho: float, rng: np.random.Generator
) -> tuple[FloatArray, FloatArray]:
    """Return two standard-normal arrays with elementwise correlation rho."""

    common = rng.standard_normal(shape)
    independent_a = rng.standard_normal(shape)
    independent_b = rng.standard_normal(shape)
    shared_scale = np.sqrt(rho)
    private_scale = np.sqrt(1.0 - rho)
    return (
        shared_scale * common + private_scale * independent_a,
        shared_scale * common + private_scale * independent_b,
    )


def ar1_window_sum_variance(window_size: int, phi: float) -> float:
    """Return ``Var(sum_{t=1}^L x_t)`` for a unit-variance AR(1)."""

    if window_size < 1:
        raise ValueError("window_size must be positive")
    if not -1.0 < phi < 1.0:
        raise ValueError("phi must be strictly between -1 and 1")
    lags = np.arange(1, window_size, dtype=np.float64)
    return float(
        window_size
        + 2.0 * np.sum((window_size - lags) * np.power(phi, lags))
    )


def ar1_window_sum_covariance(window_size: int, shift: int, phi: float) -> float:
    """Covariance of two length-L AR(1) sums separated by ``shift`` samples."""

    if window_size < 1 or shift < 0:
        raise ValueError("window_size must be positive and shift nonnegative")
    if not -1.0 < phi < 1.0:
        raise ValueError("phi must be strictly between -1 and 1")
    left = np.arange(window_size, dtype=np.int64)[:, None]
    right = shift + np.arange(window_size, dtype=np.int64)[None, :]
    distances = np.abs(right - left)
    return float(np.power(phi, distances).sum())


def ar1_window_correlation(window_size: int, shift: int, phi: float) -> float:
    """Correlation of two analytically standardized AR(1) window sums."""

    return ar1_window_sum_covariance(window_size, shift, phi) / ar1_window_sum_variance(
        window_size, phi
    )


def stationary_ar1(
    innovations: FloatArray, phi: float
) -> FloatArray:
    """Filter standard-normal innovations into a stationary unit-variance AR(1).

    The first state is set to the first standard-normal innovation, which is
    already distributed according to the stationary marginal.  ``phi=0``
    returns the original array without a copy, preserving the legacy IID path.
    """

    values = np.asarray(innovations, dtype=np.float64)
    if values.shape[-1] < 1:
        raise ValueError("innovations must have a nonempty time axis")
    if not -1.0 < phi < 1.0:
        raise ValueError("phi must be strictly between -1 and 1")
    if phi == 0.0:
        return values
    innovation_scale = np.sqrt(1.0 - phi**2)
    initial_state = ((1.0 - innovation_scale) * values[..., 0])[..., None]
    filtered, _ = lfilter(
        (innovation_scale,),
        (1.0, -phi),
        values,
        axis=-1,
        zi=initial_state,
    )
    return np.asarray(filtered, dtype=np.float64)


def _window_aggregate(raw: FloatArray, config: SimulationConfig) -> FloatArray:
    """Convert raw shocks into normalized sliding-window sums."""

    cumulative = np.concatenate(
        (
            np.zeros((config.n_subjects, config.n_sessions, 1), dtype=np.float64),
            np.cumsum(raw, axis=-1),
        ),
        axis=-1,
    )
    starts = np.arange(config.n_windows) * config.stride
    ends = starts + config.window_size
    sums = cumulative[..., ends] - cumulative[..., starts]
    return sums / np.sqrt(config.raw_window_sum_variance)


def simulate_predictions(
    config: SimulationConfig, rng: np.random.Generator
) -> SimulatedPredictions:
    """Simulate paired correctness indicators for two classifiers.

    Since every latent component is Gaussian and the total variance is known,
    choosing ``mu = Phi^-1(p) * sqrt(total_variance)`` makes each model's
    marginal probability of a correct prediction exactly ``p``.
    """

    subject_a, subject_b = _paired_normal(
        (config.n_subjects, 1, 1), config.rho_pair, rng
    )
    session_a, session_b = _paired_normal(
        (config.n_subjects, config.n_sessions, 1), config.rho_pair, rng
    )
    raw_a, raw_b = _paired_normal(
        (config.n_subjects, config.n_sessions, config.raw_length),
        config.rho_pair,
        rng,
    )
    raw_a = stationary_ar1(raw_a, config.raw_ar_phi)
    raw_b = stationary_ar1(raw_b, config.raw_ar_phi)
    window_a = _window_aggregate(raw_a, config)
    window_b = _window_aggregate(raw_b, config)
    model_a, model_b = _paired_normal(
        (config.n_subjects, config.n_sessions, config.n_windows),
        config.rho_pair,
        rng,
    )

    latent_a = (
        config.sigma_subject * subject_a
        + config.sigma_session * session_a
        + config.sigma_window * window_a
        + config.sigma_model * model_a
    )
    latent_b = (
        config.sigma_subject * subject_b
        + config.sigma_session * session_b
        + config.sigma_window * window_b
        + config.sigma_model * model_b
    )
    total_sd = np.sqrt(config.total_latent_variance)
    mu_a = norm.ppf(config.accuracy_a) * total_sd
    mu_b = norm.ppf(config.accuracy_b) * total_sd

    score_a = mu_a + latent_a
    score_b = mu_b + latent_b
    return SimulatedPredictions(score_a > 0.0, score_b > 0.0, config)

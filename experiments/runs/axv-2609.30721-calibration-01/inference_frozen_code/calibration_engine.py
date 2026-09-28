"""Matched-session-length calibration for the final variance diagnostic.

This module deliberately reuses the Gaussian latent paired-correctness DGP
from ``src/ophb_synthetic/simulation.py``.  The only structural extension is
ragged, observed session lengths.  The implementation exploits an exact
block-state representation of AR(1) window sums when the stride divides the
Figure-3 window length (64), so it has the same Gaussian law as generating
every raw sample but is substantially faster.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import sqrt
from typing import Any, Iterable

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import brentq
from scipy.signal import lfilter
from scipy.stats import norm


FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]

FIGURE3_WINDOW_SIZE = 64
FIGURE3_ACCURACY = 0.80
FIGURE3_RHO_PAIR = 0.50
FIGURE3_PHI = 0.60
Z_975 = float(norm.ppf(0.975))

CONDITION_A_SCALES = {
    "sigma_subject": sqrt(0.10),
    "sigma_session": sqrt(0.10),
    "sigma_window": sqrt(0.60),
    "sigma_model": sqrt(0.20),
}
CONDITION_B_SCALES = {
    "sigma_subject": 0.0,
    "sigma_session": 0.0,
    "sigma_window": sqrt(0.75),
    "sigma_model": sqrt(0.25),
}

METHOD_ORDER = (
    "global_iid_normal",
    "oracle_centered_bartlett_hac_kmain",
    "estimated_centered_bartlett_hac_kmain",
    "estimated_centered_lag0_sc0",
    "current_formal_hac_kmain",
    "current_formal_sc0",
    "current_formal_hac_k0",
    "current_formal_hac_2k0",
    "current_formal_hac_4k0",
)


@dataclass(frozen=True)
class CalibrationTemplate:
    """One frozen real-data session-length template."""

    dataset: str
    window_seconds: int
    overlap_percent: int
    subject_labels: tuple[str, ...]
    session_subject_index: tuple[int, ...]
    session_lengths: tuple[int, ...]
    k0: int
    k_nw: int
    k_main: int
    monte_carlo_repetitions: int
    master_seed: int

    @property
    def setting_id(self) -> str:
        token = self.dataset.lower().replace(" ", "_")
        return (
            f"{token}_{self.window_seconds}s_"
            f"overlap_{self.overlap_percent:02d}"
        )


def derived_seed(master_seed: int, *parts: str) -> int:
    """Stable uint128 seed, matching the frozen calibration convention."""

    payload = "\x1f".join((str(master_seed), *parts)).encode("utf-8")
    return int.from_bytes(sha256(payload).digest()[:16], "big")


def paired_standard_normal(
    shape: tuple[int, ...],
    rho: float,
    rng: np.random.Generator,
) -> tuple[FloatArray, FloatArray]:
    """Two standard-normal arrays with elementwise correlation ``rho``."""

    common = rng.standard_normal(shape)
    private_a = rng.standard_normal(shape)
    private_b = rng.standard_normal(shape)
    shared_scale = sqrt(rho)
    private_scale = sqrt(1.0 - rho)
    return (
        shared_scale * common + private_scale * private_a,
        shared_scale * common + private_scale * private_b,
    )


def ar1_window_sum_variance(window_size: int, phi: float) -> float:
    """Variance of a length-``window_size`` sum from unit-variance AR(1)."""

    lags = np.arange(1, window_size, dtype=np.float64)
    return float(
        window_size
        + 2.0
        * np.sum((window_size - lags) * np.power(phi, lags))
    )


def block_state_parameters(
    stride: int,
    phi: float,
) -> tuple[float, float, FloatArray]:
    """Return the exact AR(1) block-sum state parameters.

    For a block beginning at state ``x`` and containing ``stride`` raw
    observations,

    ``block_sum = block_loading * x + eta``

    and

    ``next_x = state_loading * x + zeta``.

    ``(eta, zeta)`` is Gaussian with the returned 2x2 covariance.
    """

    if stride < 1:
        raise ValueError("stride must be positive")
    if not -1.0 < phi < 1.0:
        raise ValueError("phi must lie strictly between -1 and 1")
    powers = np.power(phi, np.arange(stride, dtype=np.float64))
    block_loading = float(powers.sum())
    state_loading = float(phi**stride)
    innovation_scale = sqrt(1.0 - phi**2)
    eta_coefficients = np.zeros(stride, dtype=np.float64)
    for index in range(stride - 1):
        remaining = stride - index - 1
        eta_coefficients[index] = (
            innovation_scale
            * (1.0 - phi**remaining)
            / (1.0 - phi)
        )
    zeta_coefficients = innovation_scale * np.power(
        phi,
        np.arange(stride - 1, -1, -1, dtype=np.float64),
    )
    covariance = np.array(
        [
            [
                float(np.dot(eta_coefficients, eta_coefficients)),
                float(np.dot(eta_coefficients, zeta_coefficients)),
            ],
            [
                float(np.dot(eta_coefficients, zeta_coefficients)),
                float(np.dot(zeta_coefficients, zeta_coefficients)),
            ],
        ],
        dtype=np.float64,
    )
    return block_loading, state_loading, covariance


def _paired_correlated_noise(
    shape: tuple[int, ...],
    covariance: FloatArray,
    rho: float,
    rng: np.random.Generator,
) -> tuple[FloatArray, FloatArray]:
    """Paired Gaussian vectors with within-model covariance ``covariance``."""

    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    transform = eigenvectors @ np.diag(
        np.sqrt(np.maximum(eigenvalues, 0.0))
    )
    common = rng.standard_normal((*shape, 2)) @ transform.T
    private_a = rng.standard_normal((*shape, 2)) @ transform.T
    private_b = rng.standard_normal((*shape, 2)) @ transform.T
    shared_scale = sqrt(rho)
    private_scale = sqrt(1.0 - rho)
    return (
        shared_scale * common + private_scale * private_a,
        shared_scale * common + private_scale * private_b,
    )


def _length_buckets(lengths: IntArray, maximum_buckets: int = 16) -> list[IntArray]:
    """Group similarly sized sessions to limit exact padding overhead."""

    order = np.argsort(lengths, kind="mergesort")
    count = min(maximum_buckets, len(order))
    return [
        np.asarray(part, dtype=np.int64)
        for part in np.array_split(order, count)
        if len(part)
    ]


def paired_ar1_window_aggregates(
    lengths: IntArray,
    overlap_percent: int,
    phi: float,
    rho: float,
    rng: np.random.Generator,
) -> tuple[FloatArray, FloatArray]:
    """Generate exact paired standardized AR(1) sliding-window sums.

    The Figure-3 window length is 64 and the frozen overlap grid is
    0/50/75 percent, so each stride divides 64 exactly.  Nonoverlapping
    ``stride``-sample block sums are generated from an exact Gaussian
    state-space representation, then summed into overlapping windows.
    """

    overlap = overlap_percent / 100.0
    stride = int(round(FIGURE3_WINDOW_SIZE * (1.0 - overlap)))
    if stride < 1 or FIGURE3_WINDOW_SIZE % stride:
        raise ValueError("the frozen overlap must yield a stride dividing 64")
    blocks_per_window = FIGURE3_WINDOW_SIZE // stride
    block_loading, state_loading, covariance = block_state_parameters(
        stride, phi
    )
    standardizer = sqrt(
        ar1_window_sum_variance(FIGURE3_WINDOW_SIZE, phi)
    )
    offsets = np.concatenate(
        (np.array([0], dtype=np.int64), np.cumsum(lengths, dtype=np.int64))
    )
    total = int(offsets[-1])
    flat_a = np.empty(total, dtype=np.float64)
    flat_b = np.empty(total, dtype=np.float64)

    for indices in _length_buckets(lengths):
        bucket_lengths = lengths[indices]
        maximum_length = int(bucket_lengths.max())
        block_count = maximum_length + blocks_per_window - 1
        initial_a, initial_b = paired_standard_normal(
            (len(indices),), rho, rng
        )
        noise_a, noise_b = _paired_correlated_noise(
            (len(indices), block_count), covariance, rho, rng
        )

        def block_sums(
            initial: FloatArray, noise: FloatArray
        ) -> FloatArray:
            eta = noise[..., 0]
            zeta = noise[..., 1]
            if block_count == 1:
                states = initial[:, None]
            else:
                future, _ = lfilter(
                    (1.0,),
                    (1.0, -state_loading),
                    zeta[:, : block_count - 1],
                    axis=-1,
                    zi=(state_loading * initial)[:, None],
                )
                states = np.concatenate((initial[:, None], future), axis=1)
            return block_loading * states + eta

        blocks_a = block_sums(initial_a, noise_a)
        blocks_b = block_sums(initial_b, noise_b)

        def rolling_windows(blocks: FloatArray) -> FloatArray:
            cumulative = np.concatenate(
                (
                    np.zeros((len(indices), 1), dtype=np.float64),
                    np.cumsum(blocks, axis=1),
                ),
                axis=1,
            )
            values = (
                cumulative[
                    :, blocks_per_window : blocks_per_window + maximum_length
                ]
                - cumulative[:, :maximum_length]
            )
            return values / standardizer

        windows_a = rolling_windows(blocks_a)
        windows_b = rolling_windows(blocks_b)
        positions = offsets[indices, None] + np.arange(
            maximum_length, dtype=np.int64
        )[None, :]
        valid = np.arange(maximum_length)[None, :] < bucket_lengths[:, None]
        flat_a[positions[valid]] = windows_a[valid]
        flat_b[positions[valid]] = windows_b[valid]

    return flat_a, flat_b


def solve_exact_record_null(
    session_constant_a: FloatArray,
    session_constant_b: FloatArray,
    session_lengths: IntArray,
    residual_sd: float,
    base_mu: float,
) -> tuple[float, FloatArray]:
    """Enforce an exact zero weighted record-conditional paired difference.

    A symmetric latent intercept ``(+delta, -delta)`` is solved from the
    known DGP effects and frozen session lengths.  No observed binary outcome
    enters this construction.
    """

    weights = session_lengths.astype(np.float64)

    def weighted_difference(delta: float) -> float:
        p_a = norm.cdf(
            (base_mu + delta + session_constant_a) / residual_sd
        )
        p_b = norm.cdf(
            (base_mu - delta + session_constant_b) / residual_sd
        )
        return float(np.dot(weights, p_a - p_b) / weights.sum())

    delta = float(
        brentq(weighted_difference, -12.0, 12.0, xtol=1e-13, rtol=1e-14)
    )
    p_a = norm.cdf(
        (base_mu + delta + session_constant_a) / residual_sd
    )
    p_b = norm.cdf(
        (base_mu - delta + session_constant_b) / residual_sd
    )
    session_means = np.asarray(p_a - p_b, dtype=np.float64)
    error = float(np.dot(weights, session_means) / weights.sum())
    if abs(error) > 5e-13:
        raise RuntimeError(f"exact record null solve failed: {error}")
    return delta, session_means


def _invalid_cross_session_indices(
    lengths: IntArray,
    maximum_lag: int,
) -> tuple[IntArray, ...]:
    session_index = np.repeat(
        np.arange(len(lengths), dtype=np.int64), lengths
    )
    result: list[IntArray] = [np.empty(0, dtype=np.int64)]
    for lag in range(1, maximum_lag + 1):
        result.append(
            np.flatnonzero(
                session_index[:-lag] != session_index[lag:]
            ).astype(np.int64, copy=False)
        )
    return tuple(result)


def lag_product_sums(
    residuals: FloatArray,
    invalid_indices: tuple[IntArray, ...],
    maximum_lag: int,
) -> FloatArray:
    """Pool legal within-session lag products without crossing boundaries."""

    result = np.empty(maximum_lag + 1, dtype=np.float64)
    result[0] = float(np.dot(residuals, residuals))
    for lag in range(1, maximum_lag + 1):
        value = float(np.dot(residuals[:-lag], residuals[lag:]))
        invalid = invalid_indices[lag]
        if len(invalid):
            value -= float(
                np.dot(residuals[invalid], residuals[invalid + lag])
            )
        result[lag] = value
    return result


def bartlett_variance(
    lag_sums: FloatArray,
    bandwidth: int,
    n_windows: int,
    correction: float,
) -> float:
    """Direct-sum Bartlett variance with the formal scaling convention."""

    effective = min(int(bandwidth), len(lag_sums) - 1)
    total = float(lag_sums[0])
    if effective:
        lags = np.arange(1, effective + 1, dtype=np.float64)
        weights = 1.0 - lags / (effective + 1.0)
        total += 2.0 * float(
            np.dot(weights, lag_sums[1 : effective + 1])
        )
    return float(correction * total / n_windows**2)


def _interval_row(
    *,
    method: str,
    bandwidth: int,
    correction: float,
    point: float,
    variance: float,
    base: dict[str, Any],
) -> dict[str, Any]:
    valid = bool(np.isfinite(variance) and variance >= 0.0)
    if valid:
        standard_error = sqrt(variance)
        lower = point - Z_975 * standard_error
        upper = point + Z_975 * standard_error
        width = upper - lower
        reject = int(lower > 0.0 or upper < 0.0)
        covered = int(lower <= 0.0 <= upper)
    else:
        standard_error = np.nan
        lower = np.nan
        upper = np.nan
        width = np.nan
        reject = np.nan
        covered = np.nan
    return {
        **base,
        "method": method,
        "bandwidth": int(bandwidth),
        "finite_sample_correction": float(correction),
        "point": float(point),
        "true_difference": 0.0,
        "variance_estimate": float(variance),
        "standard_error": float(standard_error),
        "ci_lower": float(lower),
        "ci_upper": float(upper),
        "ci_width": float(width),
        "reject_null": reject,
        "covered": covered,
        "variance_valid": int(valid),
    }


def _simulate_one(
    template: CalibrationTemplate,
    condition: str,
    replication: int,
    invalid_indices: tuple[IntArray, ...],
    offsets: IntArray,
    lengths: IntArray,
    subject_index: IntArray,
) -> list[dict[str, Any]]:
    rng = np.random.default_rng(
        derived_seed(
            template.master_seed,
            template.setting_id,
            condition,
            f"rep_{replication:04d}",
            "data",
        )
    )
    n_sessions = len(lengths)
    n_windows = int(lengths.sum())
    n_subjects = len(template.subject_labels)
    base_mu = float(norm.ppf(FIGURE3_ACCURACY))

    if condition == "A_session_iid_heterogeneous":
        scales = CONDITION_A_SCALES
        subject_a, subject_b = paired_standard_normal(
            (n_subjects,), FIGURE3_RHO_PAIR, rng
        )
        session_a, session_b = paired_standard_normal(
            (n_sessions,), FIGURE3_RHO_PAIR, rng
        )
        constant_a = (
            scales["sigma_subject"] * subject_a[subject_index]
            + scales["sigma_session"] * session_a
        )
        constant_b = (
            scales["sigma_subject"] * subject_b[subject_index]
            + scales["sigma_session"] * session_b
        )
        residual_sd = sqrt(
            scales["sigma_window"] ** 2 + scales["sigma_model"] ** 2
        )
        delta, oracle_session_means = solve_exact_record_null(
            constant_a,
            constant_b,
            lengths,
            residual_sd,
            base_mu,
        )
        window_a, window_b = paired_standard_normal(
            (n_windows,), FIGURE3_RHO_PAIR, rng
        )
        dgp_overlap_percent = 0
        phi = 0.0
    elif condition == "B_extended_ar1":
        scales = CONDITION_B_SCALES
        constant_a = np.zeros(n_sessions, dtype=np.float64)
        constant_b = np.zeros(n_sessions, dtype=np.float64)
        delta = 0.0
        oracle_session_means = np.zeros(n_sessions, dtype=np.float64)
        window_a, window_b = paired_ar1_window_aggregates(
            lengths,
            template.overlap_percent,
            FIGURE3_PHI,
            FIGURE3_RHO_PAIR,
            rng,
        )
        dgp_overlap_percent = template.overlap_percent
        phi = FIGURE3_PHI
    else:
        raise ValueError(f"unknown condition: {condition}")

    model_a, model_b = paired_standard_normal(
        (n_windows,), FIGURE3_RHO_PAIR, rng
    )
    repeated_constant_a = np.repeat(constant_a, lengths)
    repeated_constant_b = np.repeat(constant_b, lengths)
    score_a = (
        base_mu
        + delta
        + repeated_constant_a
        + scales["sigma_window"] * window_a
        + scales["sigma_model"] * model_a
    )
    score_b = (
        base_mu
        - delta
        + repeated_constant_b
        + scales["sigma_window"] * window_b
        + scales["sigma_model"] * model_b
    )
    difference = (
        (score_a > 0.0).astype(np.float64)
        - (score_b > 0.0).astype(np.float64)
    )
    point = float(difference.mean())
    session_sums = np.add.reduceat(difference, offsets[:-1])
    estimated_session_means = session_sums / lengths
    estimated_residuals = difference - np.repeat(
        estimated_session_means, lengths
    )
    oracle_residuals = difference - np.repeat(
        oracle_session_means, lengths
    )

    maximum_bandwidth = max(
        template.k_main,
        template.k0,
        2 * template.k0,
        4 * template.k0,
    )
    estimated_lag_sums = lag_product_sums(
        estimated_residuals, invalid_indices, maximum_bandwidth
    )
    oracle_lag_sums = lag_product_sums(
        oracle_residuals, invalid_indices, template.k_main
    )
    formal_correction = n_windows / (n_windows - n_sessions)
    iid_variance = float(difference.var(ddof=1) / n_windows)

    requested_ratios = template.k_main / lengths.astype(np.float64)
    base = {
        "dataset": template.dataset,
        "window_seconds": template.window_seconds,
        "overlap_percent": template.overlap_percent,
        "setting_id": template.setting_id,
        "condition": condition,
        "condition_dgp_overlap_percent": dgp_overlap_percent,
        "raw_ar_phi": phi,
        "replication": replication,
        "monte_carlo_target": template.monte_carlo_repetitions,
        "n_windows": n_windows,
        "n_sessions": n_sessions,
        "n_subjects": n_subjects,
        "k0": template.k0,
        "k_nw": template.k_nw,
        "k_main": template.k_main,
        "k_main_over_t_median": float(np.median(requested_ratios)),
        "k_main_over_t_q75": float(np.quantile(requested_ratios, 0.75)),
        "k_main_over_t_q90": float(np.quantile(requested_ratios, 0.90)),
        "null_intercept_delta": float(delta),
        "oracle_session_mean_sd": float(
            np.std(oracle_session_means, ddof=1)
            if n_sessions > 1
            else 0.0
        ),
        "oracle_weighted_null_error": float(
            np.dot(lengths, oracle_session_means) / n_windows
        ),
    }
    rows = [
        _interval_row(
            method="global_iid_normal",
            bandwidth=0,
            correction=1.0,
            point=point,
            variance=iid_variance,
            base=base,
        ),
        _interval_row(
            method="oracle_centered_bartlett_hac_kmain",
            bandwidth=template.k_main,
            correction=1.0,
            point=point,
            variance=bartlett_variance(
                oracle_lag_sums, template.k_main, n_windows, 1.0
            ),
            base=base,
        ),
        _interval_row(
            method="estimated_centered_bartlett_hac_kmain",
            bandwidth=template.k_main,
            correction=1.0,
            point=point,
            variance=bartlett_variance(
                estimated_lag_sums, template.k_main, n_windows, 1.0
            ),
            base=base,
        ),
        _interval_row(
            method="estimated_centered_lag0_sc0",
            bandwidth=0,
            correction=1.0,
            point=point,
            variance=bartlett_variance(
                estimated_lag_sums, 0, n_windows, 1.0
            ),
            base=base,
        ),
        _interval_row(
            method="current_formal_hac_kmain",
            bandwidth=template.k_main,
            correction=formal_correction,
            point=point,
            variance=bartlett_variance(
                estimated_lag_sums,
                template.k_main,
                n_windows,
                formal_correction,
            ),
            base=base,
        ),
        _interval_row(
            method="current_formal_sc0",
            bandwidth=0,
            correction=formal_correction,
            point=point,
            variance=bartlett_variance(
                estimated_lag_sums, 0, n_windows, formal_correction
            ),
            base=base,
        ),
    ]
    for label, bandwidth in (
        ("current_formal_hac_k0", template.k0),
        ("current_formal_hac_2k0", 2 * template.k0),
        ("current_formal_hac_4k0", 4 * template.k0),
    ):
        rows.append(
            _interval_row(
                method=label,
                bandwidth=bandwidth,
                correction=formal_correction,
                point=point,
                variance=bartlett_variance(
                    estimated_lag_sums,
                    bandwidth,
                    n_windows,
                    formal_correction,
                ),
                base=base,
            )
        )
    return rows


def run_template_condition(
    template: CalibrationTemplate,
    condition: str,
) -> list[dict[str, Any]]:
    """Run all frozen Monte Carlo replications for one setting/condition."""

    lengths = np.asarray(template.session_lengths, dtype=np.int64)
    subject_index = np.asarray(
        template.session_subject_index, dtype=np.int64
    )
    if len(lengths) != len(subject_index):
        raise ValueError("session lengths and subject mapping differ")
    if (lengths < 1).any():
        raise ValueError("all real session lengths must be positive")
    offsets = np.concatenate(
        (np.array([0], dtype=np.int64), np.cumsum(lengths, dtype=np.int64))
    )
    maximum_bandwidth = max(
        template.k_main,
        template.k0,
        2 * template.k0,
        4 * template.k0,
    )
    invalid_indices = _invalid_cross_session_indices(
        lengths, maximum_bandwidth
    )
    rows: list[dict[str, Any]] = []
    for replication in range(template.monte_carlo_repetitions):
        rows.extend(
            _simulate_one(
                template,
                condition,
                replication,
                invalid_indices,
                offsets,
                lengths,
                subject_index,
            )
        )
    return rows


def wilson_interval(successes: int, total: int) -> tuple[float, float]:
    """95% Wilson interval for a Monte Carlo proportion."""

    if total <= 0:
        return np.nan, np.nan
    proportion = successes / total
    z = Z_975
    denominator = 1.0 + z**2 / total
    center = (proportion + z**2 / (2.0 * total)) / denominator
    half = (
        z
        / denominator
        * sqrt(
            proportion * (1.0 - proportion) / total
            + z**2 / (4.0 * total**2)
        )
    )
    return float(center - half), float(center + half)


def summarize_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize raw rows without depending on pandas in worker processes."""

    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    keys = (
        "dataset",
        "window_seconds",
        "overlap_percent",
        "setting_id",
        "condition",
        "method",
        "bandwidth",
        "k0",
        "k_nw",
        "k_main",
    )
    for row in rows:
        grouped.setdefault(tuple(row[key] for key in keys), []).append(row)

    summaries: list[dict[str, Any]] = []
    for group_key, group in grouped.items():
        first = group[0]
        valid = [item for item in group if item["variance_valid"] == 1]
        total = len(group)
        valid_count = len(valid)
        rejects = int(sum(int(item["reject_null"]) for item in valid))
        covered = int(sum(int(item["covered"]) for item in valid))
        type_i = rejects / valid_count if valid_count else np.nan
        coverage = covered / valid_count if valid_count else np.nan
        type_low, type_high = wilson_interval(rejects, valid_count)
        cover_low, cover_high = wilson_interval(covered, valid_count)
        widths = np.asarray(
            [item["ci_width"] for item in valid], dtype=np.float64
        )
        variances = np.asarray(
            [item["variance_estimate"] for item in valid],
            dtype=np.float64,
        )
        summary = {
            **dict(zip(keys, group_key, strict=True)),
            "condition_dgp_overlap_percent": first[
                "condition_dgp_overlap_percent"
            ],
            "raw_ar_phi": first["raw_ar_phi"],
            "n_windows": first["n_windows"],
            "n_sessions": first["n_sessions"],
            "n_subjects": first["n_subjects"],
            "k_main_over_t_median": first["k_main_over_t_median"],
            "k_main_over_t_q75": first["k_main_over_t_q75"],
            "k_main_over_t_q90": first["k_main_over_t_q90"],
            "monte_carlo_runs": total,
            "valid_variance_runs": valid_count,
            "invalid_variance_runs": total - valid_count,
            "invalid_variance_rate": (total - valid_count) / total,
            "type_i_error": type_i,
            "type_i_mc_ci_low": type_low,
            "type_i_mc_ci_high": type_high,
            "coverage": coverage,
            "coverage_mc_ci_low": cover_low,
            "coverage_mc_ci_high": cover_high,
            "mean_ci_width": float(widths.mean()) if len(widths) else np.nan,
            "mean_variance_estimate": (
                float(variances.mean()) if len(variances) else np.nan
            ),
            "mean_point": float(
                np.mean([item["point"] for item in group])
            ),
            "point_sd": float(
                np.std([item["point"] for item in group], ddof=1)
            ),
            "mean_oracle_session_mean_sd": float(
                np.mean(
                    [item["oracle_session_mean_sd"] for item in group]
                )
            ),
            "max_abs_oracle_weighted_null_error": float(
                np.max(
                    np.abs(
                        [
                            item["oracle_weighted_null_error"]
                            for item in group
                        ]
                    )
                )
            ),
        }
        summaries.append(summary)

    lookup = {
        (
            item["setting_id"],
            item["condition"],
            item["method"],
        ): item
        for item in summaries
    }
    for item in summaries:
        oracle = lookup.get(
            (
                item["setting_id"],
                item["condition"],
                "oracle_centered_bartlett_hac_kmain",
            )
        )
        estimated = lookup.get(
            (
                item["setting_id"],
                item["condition"],
                "estimated_centered_bartlett_hac_kmain",
            )
        )
        if oracle is not None and estimated is not None:
            item["oracle_vs_estimated_type_i_difference"] = (
                estimated["type_i_error"] - oracle["type_i_error"]
            )
            item["oracle_vs_estimated_coverage_difference"] = (
                estimated["coverage"] - oracle["coverage"]
            )
            item["oracle_vs_estimated_mean_ci_width_difference"] = (
                estimated["mean_ci_width"] - oracle["mean_ci_width"]
            )
            item["oracle_vs_estimated_mean_variance_difference"] = (
                estimated["mean_variance_estimate"]
                - oracle["mean_variance_estimate"]
            )
        else:
            item["oracle_vs_estimated_type_i_difference"] = np.nan
            item["oracle_vs_estimated_coverage_difference"] = np.nan
            item["oracle_vs_estimated_mean_ci_width_difference"] = np.nan
            item["oracle_vs_estimated_mean_variance_difference"] = np.nan
    return summaries

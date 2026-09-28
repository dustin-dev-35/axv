"""Dependence-aware inference for WISDM Real Data Phase 2.

This module is deliberately separate from :mod:`real_data_audit`.  Phase 1
used global centering, a rectangular lag window, and retained a clipped
negative-variance diagnostic.  Phase 2 has a different, frozen specification:

* fixed-record inference uses *within-session* centering and a Bartlett kernel;
* the Newey--West rule is the default fixed-record bandwidth;
* negative or non-finite variance estimates are fatal errors;
* new-session inference treats sessions equally but clusters scores by subject;
* new-subject inference first constructs one metric per subject and then gives
  every subject equal weight; and
* pooled Macro-F1 uncertainty is estimated with its observation-level delta
  method influence function.  In particular, the paired Macro-F1 variance is
  estimated from ``IF_RF - IF_MiniROCKET`` and never by adding two marginal
  variances.

All lag products are accumulated separately inside observed sessions.  No
padding, concatenation across session boundaries, or equal-length assumption
is used anywhere in the module.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, floor, sqrt
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray
import pandas as pd
from scipy.stats import norm, t as student_t


FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]

DEFAULT_KEY_COLUMNS = (
    "fold_id",
    "subject_id",
    "session_id",
    "window_start_time",
    "window_end_time",
)


class PredictionPairingError(ValueError):
    """Raised when model predictions do not describe the same ordered windows."""


class HACVarianceError(FloatingPointError):
    """Raised instead of silently clipping an invalid HAC variance."""


@dataclass(frozen=True)
class IntervalResult:
    point: float
    variance: float
    standard_error: float
    lower: float
    upper: float
    p_value: float
    reject_null: bool | None
    null_value: float | None
    distribution: str
    degrees_of_freedom: int | None
    estimand: str


@dataclass(frozen=True)
class BartlettHACResult:
    point: float
    n_windows: int
    n_sessions: int
    requested_bandwidth: int
    effective_bandwidth: int
    lag_product_sums: FloatArray
    lag_pair_counts: IntArray
    bartlett_weights: FloatArray
    variance_contributions: FloatArray
    degrees_of_freedom_correction: float
    variance: float
    standard_error: float
    kernel: str
    centering: str
    session_contributions: pd.DataFrame


@dataclass(frozen=True)
class MacroF1Influence:
    point: float
    influence: FloatArray
    labels: tuple[Any, ...]
    class_statistics: pd.DataFrame


@dataclass(frozen=True)
class Phase2InferenceOutputs:
    canonical_predictions: pd.DataFrame
    audit_summary: pd.DataFrame
    bandwidth_diagnostics: pd.DataFrame
    estimand_comparison: pd.DataFrame
    session_statistics: pd.DataFrame
    subject_statistics: pd.DataFrame
    heterogeneity_decomposition: pd.DataFrame


def _require_columns(frame: pd.DataFrame, columns: Iterable[str], name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def _effective_key_columns(
    frame: pd.DataFrame,
    key_columns: Sequence[str],
) -> tuple[str, ...]:
    keys = list(key_columns)
    for column in ("source_start_index", "source_end_index"):
        if column in frame.columns and column not in keys:
            keys.append(column)
    return tuple(keys)


def _validate_unique_keys(
    frame: pd.DataFrame,
    key_columns: Sequence[str],
    name: str,
) -> None:
    _require_columns(frame, key_columns, name)
    if frame[list(key_columns)].isna().any().any():
        raise PredictionPairingError(f"{name} contains missing window-key values")
    duplicate = frame.duplicated(list(key_columns), keep=False)
    if duplicate.any():
        example = frame.loc[duplicate, list(key_columns)].iloc[0].to_dict()
        raise PredictionPairingError(
            f"{name} contains duplicate window keys; example={example}"
        )


def align_model_prediction_tables(
    windows: pd.DataFrame,
    predictions_rf: pd.DataFrame,
    predictions_minirocket: pd.DataFrame,
    *,
    key_columns: Sequence[str] = DEFAULT_KEY_COLUMNS,
    truth_column: str = "y_true",
    rf_input_column: str = "prediction",
    minirocket_input_column: str = "prediction",
) -> pd.DataFrame:
    """Attach two predictions only after exact ordered-key validation.

    A set-based merge is intentionally insufficient here: a model export whose
    predictions were silently permuted must fail rather than be automatically
    reordered.  Source indices are added to the immutable key whenever they
    are present in all three tables.
    """

    common_extra = all(
        {"source_start_index", "source_end_index"}.issubset(candidate.columns)
        for candidate in (windows, predictions_rf, predictions_minirocket)
    )
    keys = tuple(key_columns)
    if common_extra:
        keys = tuple(dict.fromkeys((*keys, "source_start_index", "source_end_index")))
    for name, candidate in (
        ("windows", windows),
        ("predictions_rf", predictions_rf),
        ("predictions_minirocket", predictions_minirocket),
    ):
        _validate_unique_keys(candidate, keys, name)
    _require_columns(windows, (truth_column,), "windows")
    _require_columns(predictions_rf, (rf_input_column,), "predictions_rf")
    _require_columns(
        predictions_minirocket,
        (minirocket_input_column,),
        "predictions_minirocket",
    )
    expected = windows[list(keys)].reset_index(drop=True)
    for name, candidate in (
        ("predictions_rf", predictions_rf),
        ("predictions_minirocket", predictions_minirocket),
    ):
        observed = candidate[list(keys)].reset_index(drop=True)
        if not expected.equals(observed):
            if len(expected) != len(observed):
                detail = f"row counts differ ({len(expected)} != {len(observed)})"
            else:
                equal = (expected == observed).all(axis=1).to_numpy()
                location = int(np.flatnonzero(~equal)[0]) if (~equal).any() else 0
                detail = (
                    f"first mismatch at row {location}: expected "
                    f"{expected.iloc[location].to_dict()}, observed "
                    f"{observed.iloc[location].to_dict()}"
                )
            raise PredictionPairingError(f"{name} is not strictly paired; {detail}")
    result = windows.copy().reset_index(drop=True)
    result["pred_rf"] = predictions_rf[rf_input_column].to_numpy(copy=True)
    result["pred_minirocket"] = predictions_minirocket[
        minirocket_input_column
    ].to_numpy(copy=True)
    return validate_phase2_prediction_frame(result, key_columns=keys)


def validate_phase2_prediction_frame(
    frame: pd.DataFrame,
    *,
    key_columns: Sequence[str] = DEFAULT_KEY_COLUMNS,
    truth_column: str = "y_true",
    rf_column: str = "pred_rf",
    minirocket_column: str = "pred_minirocket",
    expected_stride_samples: int | None = None,
    target_sample_rate_hz: float = 20.0,
) -> pd.DataFrame:
    """Validate one OOF long prediction table and derive paired correctness."""

    keys = _effective_key_columns(frame, key_columns)
    required = (*keys, "activity", truth_column, rf_column, minirocket_column)
    _require_columns(frame, required, "Phase 2 prediction frame")
    _validate_unique_keys(frame, keys, "Phase 2 prediction frame")
    if frame[list(required)].isna().any().any():
        raise ValueError("Phase 2 prediction frame contains missing required values")
    starts = pd.to_numeric(frame["window_start_time"], errors="coerce")
    ends = pd.to_numeric(frame["window_end_time"], errors="coerce")
    if not np.isfinite(starts.to_numpy(dtype=np.float64)).all() or not np.isfinite(
        ends.to_numpy(dtype=np.float64)
    ).all():
        raise ValueError("window times must be finite numeric values")
    if (ends <= starts).any():
        raise ValueError("every window_end_time must exceed window_start_time")

    canonical = frame.copy()
    canonical["window_start_time"] = starts
    canonical["window_end_time"] = ends
    order_column = (
        "resampled_start_index"
        if "resampled_start_index" in canonical
        else "window_start_time"
    )
    sort_columns = [
        "fold_id",
        "subject_id",
        "session_id",
        order_column,
    ]
    canonical = canonical.sort_values(sort_columns, kind="mergesort").reset_index(
        drop=True
    )
    subject_folds = canonical.groupby("subject_id", dropna=False)["fold_id"].nunique()
    if (subject_folds != 1).any():
        offenders = subject_folds[subject_folds != 1].index.tolist()[:5]
        raise PredictionPairingError(
            f"subjects occur in more than one OOF test fold: {offenders}"
        )
    for key, session in canonical.groupby(
        ["subject_id", "session_id"], sort=False, dropna=False
    ):
        order = pd.to_numeric(session[order_column], errors="coerce").to_numpy(
            dtype=np.float64
        )
        if not np.isfinite(order).all() or (np.diff(order) <= 0).any():
            raise ValueError(f"session {key!r} has non-increasing window order")
        if expected_stride_samples is not None and len(order) > 1:
            if target_sample_rate_hz <= 0.0:
                raise ValueError("target_sample_rate_hz must be positive")
            if order_column == "resampled_start_index":
                expected_increment = float(expected_stride_samples)
            else:
                # WISDM device timestamps are integer nanoseconds.  Synthetic
                # and unit-test frames may use seconds.  The scale distinction
                # is unambiguous for a positive window-to-window increment.
                observed_increment = float(np.min(np.diff(order)))
                expected_seconds = expected_stride_samples / target_sample_rate_hz
                expected_increment = (
                    expected_seconds * 1e9
                    if observed_increment > 1e6
                    else expected_seconds
                )
            if not np.allclose(
                np.diff(order), expected_increment, atol=0.0, rtol=0.0
            ):
                raise ValueError(
                    f"session {key!r} contains an interior window gap; "
                    "lag adjacency may not bridge excluded windows"
                )

    correct_rf = (canonical[rf_column] == canonical[truth_column]).astype(np.float64)
    correct_minirocket = (
        canonical[minirocket_column] == canonical[truth_column]
    ).astype(np.float64)
    paired = correct_rf - correct_minirocket
    for column, expected in (
        ("correct_rf", correct_rf),
        ("correct_minirocket", correct_minirocket),
        ("paired_accuracy_difference", paired),
    ):
        if column in canonical.columns:
            observed = pd.to_numeric(canonical[column], errors="coerce").to_numpy()
            if not np.array_equal(observed, expected.to_numpy()):
                raise PredictionPairingError(
                    f"existing {column} is inconsistent with paired predictions"
                )
        canonical[column] = expected
    return canonical


def _truth_supported_labels(y_true: Sequence[Any]) -> tuple[Any, ...]:
    labels = tuple(pd.unique(pd.Series(y_true, copy=False)))
    if not labels:
        raise ValueError("at least one true label is required")
    return labels


def macro_f1_with_influence(
    y_true: Sequence[Any],
    y_pred: Sequence[Any],
    *,
    labels: Sequence[Any] | None = None,
) -> MacroF1Influence:
    """Return Macro-F1 and its observation-level delta-method influence.

    The default label universe contains exactly the classes with positive true
    support in the evaluation unit.  This avoids making a perfect one-activity
    session have Macro-F1 ``1/C`` merely because unrelated dataset classes are
    absent from that session.
    """

    truth = np.asarray(y_true, dtype=object)
    prediction = np.asarray(y_pred, dtype=object)
    if truth.ndim != 1 or prediction.ndim != 1 or len(truth) != len(prediction):
        raise ValueError("y_true and y_pred must be equal-length one-dimensional arrays")
    if len(truth) < 1:
        raise ValueError("Macro-F1 requires at least one observation")
    if pd.isna(truth).any() or pd.isna(prediction).any():
        raise ValueError("Macro-F1 inputs must not contain missing labels")
    label_values = tuple(labels) if labels is not None else _truth_supported_labels(truth)
    if len(set(label_values)) != len(label_values) or not label_values:
        raise ValueError("labels must be a nonempty sequence of unique values")
    n = len(truth)
    influence = np.zeros(n, dtype=np.float64)
    rows: list[dict[str, Any]] = []
    macro = 0.0
    class_weight = 1.0 / len(label_values)
    for label in label_values:
        true_class = truth == label
        predicted_class = prediction == label
        tp_i = (true_class & predicted_class).astype(np.float64)
        fp_i = ((~true_class) & predicted_class).astype(np.float64)
        fn_i = (true_class & (~predicted_class)).astype(np.float64)
        tp = float(tp_i.mean())
        fp = float(fp_i.mean())
        fn = float(fn_i.mean())
        denominator = 2.0 * tp + fp + fn
        if denominator <= 0.0 or not np.isfinite(denominator):
            raise ValueError(
                f"Macro-F1 influence is undefined for unsupported label {label!r}"
            )
        f1 = 2.0 * tp / denominator
        gradient_tp = 2.0 * (fp + fn) / denominator**2
        gradient_fp = -2.0 * tp / denominator**2
        gradient_fn = gradient_fp
        influence += class_weight * (
            gradient_tp * (tp_i - tp)
            + gradient_fp * (fp_i - fp)
            + gradient_fn * (fn_i - fn)
        )
        macro += class_weight * f1
        rows.append(
            {
                "label": label,
                "tp_proportion": tp,
                "fp_proportion": fp,
                "fn_proportion": fn,
                "f1": f1,
                "gradient_tp": gradient_tp,
                "gradient_fp": gradient_fp,
                "gradient_fn": gradient_fn,
            }
        )
    if not np.isfinite(influence).all() or not np.isfinite(macro):
        raise FloatingPointError("Macro-F1 influence calculation is non-finite")
    # The influence identity has exactly zero expectation up to roundoff.
    if abs(float(influence.mean())) > 1e-10:
        raise FloatingPointError("Macro-F1 influence does not have sample mean zero")
    return MacroF1Influence(
        point=float(macro),
        influence=influence,
        labels=label_values,
        class_statistics=pd.DataFrame(rows),
    )


def _ordered_sessions(
    frame: pd.DataFrame,
    value_column: str,
    *,
    subject_column: str,
    session_column: str,
    time_column: str,
) -> tuple[pd.DataFrame, list[tuple[tuple[Any, Any], FloatArray]]]:
    _require_columns(
        frame,
        (subject_column, session_column, time_column, value_column),
        "long inference frame",
    )
    selected = frame[
        [subject_column, session_column, time_column, value_column]
    ].copy()
    if selected.isna().any().any():
        raise ValueError("inference grouping, time, and values must not be missing")
    selected[time_column] = pd.to_numeric(selected[time_column], errors="coerce")
    selected[value_column] = pd.to_numeric(selected[value_column], errors="coerce")
    if not np.isfinite(selected[[time_column, value_column]].to_numpy()).all():
        raise ValueError("inference time and values must be finite")
    selected = selected.sort_values(
        [subject_column, session_column, time_column], kind="mergesort"
    ).reset_index(drop=True)
    sessions: list[tuple[tuple[Any, Any], FloatArray]] = []
    for key, group in selected.groupby(
        [subject_column, session_column], sort=False, dropna=False
    ):
        times = group[time_column].to_numpy(dtype=np.float64)
        if len(times) > 1 and (np.diff(times) <= 0).any():
            raise ValueError(f"session {key!r} has duplicate/non-increasing times")
        sessions.append((key, group[value_column].to_numpy(dtype=np.float64)))
    if not sessions:
        raise ValueError("at least one observed session is required")
    return selected, sessions


def _checked_variance(value: float, context: str) -> float:
    if not np.isfinite(value):
        raise HACVarianceError(f"{context} variance is non-finite: {value}")
    if value < 0.0:
        raise HACVarianceError(f"{context} variance is negative: {value}")
    return float(value)


def session_centered_bartlett_hac(
    frame: pd.DataFrame,
    value_column: str,
    bandwidth: int,
    *,
    point: float | None = None,
    subject_column: str = "subject_id",
    session_column: str = "session_id",
    time_column: str = "window_start_time",
    finite_sample_correction: bool = True,
) -> BartlettHACResult:
    r"""Estimate fixed-record ``Var(point)`` by direct session-local sums.

    For :math:`u_{rt}=z_{rt}-\bar z_r`, this computes

    .. math::

       \frac{c}{N^2}\left[\sum_{r,t}u_{rt}^2+
       2\sum_{h=1}^{K} \left(1-\frac{h}{K+1}\right)
       \sum_{r,t}u_{rt}u_{r,t+h}\right],

    where ``c=N/(N-R)`` accounts for the ``R`` estimated session means.  The
    correction can be disabled for a sensitivity check.  Legal pairs are
    accumulated directly, so unequal session lengths need no padding or
    additional ``1-h/T`` factor.
    """

    if not isinstance(bandwidth, (int, np.integer)) or bandwidth < 0:
        raise ValueError("bandwidth must be a nonnegative integer")
    selected, sessions = _ordered_sessions(
        frame,
        value_column,
        subject_column=subject_column,
        session_column=session_column,
        time_column=time_column,
    )
    n_windows = len(selected)
    n_sessions = len(sessions)
    if n_windows <= n_sessions:
        raise ValueError("session-centered HAC requires N greater than R")
    maximum = max(len(values) for _, values in sessions) - 1
    effective = min(int(bandwidth), maximum)
    lag_sums = np.zeros(effective + 1, dtype=np.float64)
    lag_counts = np.zeros(effective + 1, dtype=np.int64)
    rows: list[dict[str, Any]] = []
    for (subject, session), values in sessions:
        centered = values - float(values.mean())
        for lag in range(effective + 1):
            legal = len(centered) - lag
            if legal <= 0:
                continue
            product = (
                float(np.dot(centered, centered))
                if lag == 0
                else float(np.dot(centered[:-lag], centered[lag:]))
            )
            lag_sums[lag] += product
            lag_counts[lag] += legal
            rows.append(
                {
                    subject_column: subject,
                    session_column: session,
                    "lag": lag,
                    "pair_count": legal,
                    "product_sum": product,
                }
            )
    weights = np.ones(effective + 1, dtype=np.float64)
    if effective:
        lags = np.arange(1, effective + 1, dtype=np.float64)
        weights[1:] = 1.0 - lags / (effective + 1.0)
    correction = (
        n_windows / (n_windows - n_sessions) if finite_sample_correction else 1.0
    )
    contributions = correction * lag_sums / n_windows**2
    if effective:
        contributions[1:] *= 2.0 * weights[1:]
    variance = _checked_variance(
        float(contributions.sum()),
        f"session-centered Bartlett HAC({value_column}, K={effective})",
    )
    observed_point = (
        float(selected[value_column].mean()) if point is None else float(point)
    )
    if not np.isfinite(observed_point):
        raise ValueError("point estimate must be finite")
    return BartlettHACResult(
        point=observed_point,
        n_windows=n_windows,
        n_sessions=n_sessions,
        requested_bandwidth=int(bandwidth),
        effective_bandwidth=effective,
        lag_product_sums=lag_sums,
        lag_pair_counts=lag_counts,
        bartlett_weights=weights,
        variance_contributions=contributions,
        degrees_of_freedom_correction=float(correction),
        variance=variance,
        standard_error=sqrt(variance),
        kernel="bartlett",
        centering="session_mean",
        session_contributions=pd.DataFrame(rows),
    )


def interval_from_variance(
    point: float,
    variance: float,
    *,
    estimand: str,
    distribution: str = "z",
    degrees_of_freedom: int | None = None,
    null_value: float | None = None,
    alpha: float = 0.05,
) -> IntervalResult:
    """Construct an untruncated interval and an optional two-sided test."""

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    checked = _checked_variance(float(variance), estimand)
    standard_error = sqrt(checked)
    if distribution == "z":
        critical = float(norm.ppf(1.0 - alpha / 2.0))
        reference_df = None
    elif distribution == "t":
        if degrees_of_freedom is None or degrees_of_freedom < 1:
            raise ValueError("t inference requires positive degrees_of_freedom")
        reference_df = int(degrees_of_freedom)
        critical = float(student_t.ppf(1.0 - alpha / 2.0, reference_df))
    else:
        raise ValueError("distribution must be 'z' or 't'")
    lower = float(point - critical * standard_error)
    upper = float(point + critical * standard_error)
    if null_value is None:
        p_value = np.nan
        reject: bool | None = None
    elif standard_error == 0.0:
        p_value = 1.0 if float(point) == float(null_value) else 0.0
        reject = bool(p_value <= alpha)
    else:
        statistic = abs((float(point) - float(null_value)) / standard_error)
        p_value = float(
            2.0
            * (
                norm.sf(statistic)
                if distribution == "z"
                else student_t.sf(statistic, reference_df)
            )
        )
        reject = bool(p_value <= alpha)
    return IntervalResult(
        point=float(point),
        variance=checked,
        standard_error=standard_error,
        lower=lower,
        upper=upper,
        p_value=float(p_value),
        reject_null=reject,
        null_value=None if null_value is None else float(null_value),
        distribution=distribution,
        degrees_of_freedom=reference_df,
        estimand=estimand,
    )


def iid_normal_inference(
    analysis_values: Sequence[float],
    *,
    point: float | None = None,
    estimand: str = "fixed_record_pooled_window",
    null_value: float | None = None,
) -> IntervalResult:
    """Ordinary IID baseline; for Macro-F1 pass its influence values and point."""

    values = np.asarray(analysis_values, dtype=np.float64)
    if values.ndim != 1 or len(values) < 2 or not np.isfinite(values).all():
        raise ValueError("IID inference requires at least two finite values")
    observed_point = float(values.mean()) if point is None else float(point)
    variance = _checked_variance(float(values.var(ddof=1) / len(values)), "IID")
    return interval_from_variance(
        observed_point,
        variance,
        estimand=estimand,
        distribution="z",
        null_value=null_value,
    )


def newey_west_rule_bandwidth(
    session_lengths: Sequence[int],
    minimum: int,
) -> int:
    """Newey--West rule based on mean observed session length, lower-bounded by K0."""

    lengths = np.asarray(session_lengths, dtype=np.int64)
    if lengths.ndim != 1 or not len(lengths) or (lengths < 1).any():
        raise ValueError("session_lengths must be nonempty positive integers")
    if not isinstance(minimum, (int, np.integer)) or minimum < 0:
        raise ValueError("minimum must be a nonnegative integer")
    maximum = int(lengths.max() - 1)
    if maximum == 0:
        return 0
    reference = float(lengths.mean())
    rule = floor(4.0 * (reference / 100.0) ** (2.0 / 9.0))
    return min(maximum, max(int(minimum), int(rule)))


def acf_diagnostics(
    frame: pd.DataFrame,
    value_column: str,
    *,
    k0: int,
    max_lag: int = 50,
    subject_column: str = "subject_id",
    session_column: str = "session_id",
    time_column: str = "window_start_time",
) -> pd.DataFrame:
    """Compute global- and session-centered ACFs on a fixed lag grid.

    Products always remain within sessions.  Unavailable lags are represented
    by ``pair_count=0`` and NaN covariance/correlation rather than by a false
    zero.
    """

    if k0 < 0 or max_lag < 1:
        raise ValueError("k0 must be nonnegative and max_lag must be positive")
    selected, sessions = _ordered_sessions(
        frame,
        value_column,
        subject_column=subject_column,
        session_column=session_column,
        time_column=time_column,
    )
    global_mean = float(selected[value_column].mean())
    rows: list[dict[str, Any]] = []
    for centering in ("global_mean", "session_mean"):
        centered_sessions = [
            (
                key,
                values
                - (global_mean if centering == "global_mean" else float(values.mean())),
            )
            for key, values in sessions
        ]
        gamma0_sum = float(sum(np.dot(values, values) for _, values in centered_sessions))
        gamma0_count = int(sum(len(values) for _, values in centered_sessions))
        gamma0 = gamma0_sum / gamma0_count if gamma0_count else np.nan
        for lag in range(0, max_lag + 1):
            product_sum = 0.0
            pair_count = 0
            for _, values in centered_sessions:
                legal = len(values) - lag
                if legal <= 0:
                    continue
                product_sum += (
                    float(np.dot(values, values))
                    if lag == 0
                    else float(np.dot(values[:-lag], values[lag:]))
                )
                pair_count += legal
            covariance = product_sum / pair_count if pair_count else np.nan
            correlation = (
                covariance / gamma0
                if pair_count and np.isfinite(gamma0) and gamma0 > 0.0
                else np.nan
            )
            threshold = 1.96 / sqrt(pair_count) if pair_count else np.nan
            rows.append(
                {
                    "centering": centering,
                    "lag": lag,
                    "pair_count": pair_count,
                    "available": int(pair_count > 0),
                    "lag_product_sum": product_sum if pair_count else np.nan,
                    "autocovariance": covariance,
                    "autocorrelation": correlation,
                    "white_noise_threshold": threshold,
                    "beyond_k0": int(lag > k0),
                }
            )
    result = pd.DataFrame(rows)
    global_rows = result[result["centering"] == "global_mean"][
        ["lag", "autocorrelation"]
    ].rename(columns={"autocorrelation": "global_autocorrelation"})
    session_rows = result[result["centering"] == "session_mean"][
        ["lag", "autocorrelation"]
    ].rename(columns={"autocorrelation": "session_autocorrelation"})
    comparison = global_rows.merge(session_rows, on="lag", validate="one_to_one")
    comparison["global_minus_session_acf"] = (
        comparison["global_autocorrelation"]
        - comparison["session_autocorrelation"]
    )
    result = result.merge(comparison, on="lag", how="left", validate="many_to_one")
    return result


def acf_threshold_bandwidth(
    diagnostics: pd.DataFrame,
    *,
    minimum: int,
    max_lag: int = 50,
) -> int:
    """Largest session-centered lag exceeding a frozen white-noise threshold."""

    _require_columns(
        diagnostics,
        ("centering", "lag", "pair_count", "autocorrelation"),
        "ACF diagnostics",
    )
    selected = diagnostics[
        (diagnostics["centering"] == "session_mean")
        & (diagnostics["lag"] >= 1)
        & (diagnostics["lag"] <= max_lag)
        & (diagnostics["pair_count"] > 0)
        & diagnostics["autocorrelation"].notna()
    ].copy()
    if selected.empty:
        return int(minimum)
    selected["threshold"] = 1.96 / np.sqrt(selected["pair_count"])
    significant = selected[
        selected["autocorrelation"].abs() > selected["threshold"]
    ]
    data_maximum = int(selected["lag"].max())
    selected_lag = int(significant["lag"].max()) if len(significant) else int(minimum)
    return min(data_maximum, max(int(minimum), selected_lag))


def _unit_macro_f1(truth: pd.Series, prediction: pd.Series) -> float:
    return macro_f1_with_influence(truth.to_numpy(), prediction.to_numpy()).point


def session_metric_statistics(frame: pd.DataFrame) -> pd.DataFrame:
    """Construct one Accuracy and Macro-F1 value per observed session."""

    canonical = validate_phase2_prediction_frame(frame)
    rows: list[dict[str, Any]] = []
    for (subject, session), group in canonical.groupby(
        ["subject_id", "session_id"], sort=True, dropna=False
    ):
        activities = pd.unique(group["activity"])
        if len(activities) != 1:
            raise ValueError(
                f"session {(subject, session)!r} contains multiple activities"
            )
        accuracy_rf = float(group["correct_rf"].mean())
        accuracy_minirocket = float(group["correct_minirocket"].mean())
        macro_rf = _unit_macro_f1(group["y_true"], group["pred_rf"])
        macro_minirocket = _unit_macro_f1(
            group["y_true"], group["pred_minirocket"]
        )
        rows.append(
            {
                "subject_id": subject,
                "session_id": session,
                "activity": activities[0],
                "n_windows": len(group),
                "accuracy_rf": accuracy_rf,
                "accuracy_minirocket": accuracy_minirocket,
                "paired_accuracy_difference": accuracy_rf - accuracy_minirocket,
                "macro_f1_rf": macro_rf,
                "macro_f1_minirocket": macro_minirocket,
                "paired_macro_f1_difference": macro_rf - macro_minirocket,
            }
        )
    return pd.DataFrame(rows)


def subject_metric_statistics(frame: pd.DataFrame) -> pd.DataFrame:
    """Construct one metric per subject; no subject is weighted by its window count."""

    canonical = validate_phase2_prediction_frame(frame)
    rows: list[dict[str, Any]] = []
    for subject, group in canonical.groupby("subject_id", sort=True, dropna=False):
        accuracy_rf = float(group["correct_rf"].mean())
        accuracy_minirocket = float(group["correct_minirocket"].mean())
        macro_rf = _unit_macro_f1(group["y_true"], group["pred_rf"])
        macro_minirocket = _unit_macro_f1(
            group["y_true"], group["pred_minirocket"]
        )
        rows.append(
            {
                "subject_id": subject,
                "fold_id": group["fold_id"].iloc[0],
                "n_windows": len(group),
                "n_sessions": group["session_id"].nunique(),
                "accuracy_rf": accuracy_rf,
                "accuracy_minirocket": accuracy_minirocket,
                "paired_accuracy_difference": accuracy_rf - accuracy_minirocket,
                "macro_f1_rf": macro_rf,
                "macro_f1_minirocket": macro_minirocket,
                "paired_macro_f1_difference": macro_rf - macro_minirocket,
            }
        )
    return pd.DataFrame(rows)


def subject_clustered_session_inference(
    session_statistics: pd.DataFrame,
    value_column: str,
    *,
    null_value: float | None = None,
    subject_column: str = "subject_id",
) -> IntervalResult:
    r"""Equal-session mean with an intercept-only subject-cluster sandwich.

    If ``m_r`` is a session metric and ``G`` is the subject count, the CR1
    variance is

    ``G/(G-1) * sum_g (sum_{r in g}(m_r-mbar))^2 / R^2``.

    Subjects are assumed independent; dependence among all sessions from the
    same subject is unrestricted.  The reference t distribution uses ``G-1``
    degrees of freedom.
    """

    _require_columns(
        session_statistics,
        (subject_column, value_column),
        "session statistics",
    )
    values = pd.to_numeric(session_statistics[value_column], errors="coerce")
    if not np.isfinite(values.to_numpy(dtype=np.float64)).all():
        raise ValueError("session metric values must be finite")
    n_sessions = len(values)
    n_subjects = session_statistics[subject_column].nunique(dropna=False)
    if n_subjects < 2 or n_sessions < 2:
        raise ValueError("clustered session inference requires at least two subjects")
    point = float(values.mean())
    scores = (
        pd.DataFrame({subject_column: session_statistics[subject_column], "u": values - point})
        .groupby(subject_column, dropna=False)["u"]
        .sum()
        .to_numpy(dtype=np.float64)
    )
    variance = _checked_variance(
        float(n_subjects / (n_subjects - 1.0) * np.dot(scores, scores) / n_sessions**2),
        "new-session subject-cluster sandwich",
    )
    return interval_from_variance(
        point,
        variance,
        estimand="new_session_equal_session",
        distribution="t",
        degrees_of_freedom=int(n_subjects - 1),
        null_value=null_value,
    )


def equal_subject_t_inference(
    subject_statistics: pd.DataFrame,
    value_column: str,
    *,
    null_value: float | None = None,
) -> IntervalResult:
    """Equal-subject paired t inference with exactly ``n_subjects-1`` df."""

    _require_columns(subject_statistics, ("subject_id", value_column), "subject statistics")
    if subject_statistics["subject_id"].duplicated().any():
        raise ValueError("subject statistics must contain exactly one row per subject")
    values = pd.to_numeric(subject_statistics[value_column], errors="coerce").to_numpy(
        dtype=np.float64
    )
    if len(values) < 2 or not np.isfinite(values).all():
        raise ValueError("subject inference requires at least two finite subject values")
    point = float(values.mean())
    variance = _checked_variance(
        float(values.var(ddof=1) / len(values)), "new-subject paired t"
    )
    return interval_from_variance(
        point,
        variance,
        estimand="new_subject_equal_subject",
        distribution="t",
        degrees_of_freedom=len(values) - 1,
        null_value=null_value,
    )


def heterogeneity_decomposition(
    frame: pd.DataFrame,
    value_column: str = "paired_accuracy_difference",
) -> pd.DataFrame:
    """Exact weighted nested sum-of-squares decomposition.

    This separates within-session variation, between-session variation within
    subjects, and between-subject variation.  It is descriptive and prevents a
    global-centered ACF tail from being labelled as pure temporal dependence.
    """

    _require_columns(frame, ("subject_id", "session_id", value_column), "metric frame")
    values = pd.to_numeric(frame[value_column], errors="coerce")
    if not np.isfinite(values.to_numpy(dtype=np.float64)).all():
        raise ValueError("heterogeneity values must be finite")
    work = frame[["subject_id", "session_id"]].copy()
    work["value"] = values.to_numpy()
    global_mean = float(work["value"].mean())
    subject_mean = work.groupby("subject_id", dropna=False)["value"].transform("mean")
    session_mean = work.groupby(
        ["subject_id", "session_id"], dropna=False
    )["value"].transform("mean")
    within = float(np.square(work["value"] - session_mean).sum())
    between_session = float(np.square(session_mean - subject_mean).sum())
    between_subject = float(np.square(subject_mean - global_mean).sum())
    total = float(np.square(work["value"] - global_mean).sum())
    if not np.isclose(
        within + between_session + between_subject,
        total,
        atol=1e-9 * max(1.0, total),
        rtol=1e-10,
    ):
        raise FloatingPointError("nested heterogeneity decomposition is not exact")
    return pd.DataFrame(
        [
            {
                "value_column": value_column,
                "n_windows": len(work),
                "n_sessions": work[["subject_id", "session_id"]].drop_duplicates().shape[0],
                "n_subjects": work["subject_id"].nunique(dropna=False),
                "global_mean": global_mean,
                "total_ss": total,
                "within_session_ss": within,
                "between_session_within_subject_ss": between_session,
                "between_subject_ss": between_subject,
                "within_session_fraction": within / total if total > 0 else np.nan,
                "between_session_fraction": between_session / total if total > 0 else np.nan,
                "between_subject_fraction": between_subject / total if total > 0 else np.nan,
            }
        ]
    )


def _analysis_targets(
    canonical: pd.DataFrame,
) -> Mapping[tuple[str, str], tuple[FloatArray, float]]:
    truth = canonical["y_true"].to_numpy(dtype=object)
    labels = _truth_supported_labels(truth)
    rf_macro = macro_f1_with_influence(
        truth, canonical["pred_rf"].to_numpy(dtype=object), labels=labels
    )
    mini_macro = macro_f1_with_influence(
        truth,
        canonical["pred_minirocket"].to_numpy(dtype=object),
        labels=labels,
    )
    return {
        ("accuracy", "rf"): (
            canonical["correct_rf"].to_numpy(dtype=np.float64),
            float(canonical["correct_rf"].mean()),
        ),
        ("accuracy", "minirocket"): (
            canonical["correct_minirocket"].to_numpy(dtype=np.float64),
            float(canonical["correct_minirocket"].mean()),
        ),
        ("accuracy", "rf_minus_minirocket"): (
            canonical["paired_accuracy_difference"].to_numpy(dtype=np.float64),
            float(canonical["paired_accuracy_difference"].mean()),
        ),
        ("macro_f1", "rf"): (rf_macro.influence, rf_macro.point),
        ("macro_f1", "minirocket"): (
            mini_macro.influence,
            mini_macro.point,
        ),
        ("macro_f1", "rf_minus_minirocket"): (
            rf_macro.influence - mini_macro.influence,
            rf_macro.point - mini_macro.point,
        ),
    }


def _audit_row(
    *,
    overlap_percent: int,
    stride: int,
    metric: str,
    contrast: str,
    estimand: str,
    method: str,
    inference: IntervalResult,
    n_windows: int,
    n_sessions: int,
    n_subjects: int,
    k0: int,
    bandwidth_name: str | None,
    requested_bandwidth: int | None,
    effective_bandwidth: int | None,
    is_primary: bool,
    is_sensitivity: bool,
) -> dict[str, Any]:
    return {
        "overlap_percent": overlap_percent,
        "stride": stride,
        "metric": metric,
        "contrast": contrast,
        "estimand": estimand,
        "method": method,
        "inference": f"{inference.distribution}_interval",
        "point": inference.point,
        "variance_estimate": inference.variance,
        "standard_error": inference.standard_error,
        "ci_lower": inference.lower,
        "ci_upper": inference.upper,
        "ci_width": inference.upper - inference.lower,
        "p_value_h0_difference_zero": (
            inference.p_value if contrast == "rf_minus_minirocket" else np.nan
        ),
        "reject_h0_difference_zero": (
            inference.reject_null if contrast == "rf_minus_minirocket" else np.nan
        ),
        "degrees_of_freedom": (
            inference.degrees_of_freedom
            if inference.degrees_of_freedom is not None
            else np.nan
        ),
        "nominal_window_count": n_windows,
        "n_sessions": n_sessions,
        "n_subjects": n_subjects,
        "k0": k0,
        "bandwidth_name": bandwidth_name,
        "requested_bandwidth": requested_bandwidth,
        "effective_bandwidth": effective_bandwidth,
        "is_primary": int(is_primary),
        "is_sensitivity_analysis": int(is_sensitivity),
    }


def evaluate_phase2_inference(
    frame: pd.DataFrame,
    *,
    overlap_percent: int,
    stride_samples: int,
    window_size_samples: int = 200,
    maximum_acf_lag: int = 50,
) -> Phase2InferenceOutputs:
    """Run all Phase 2 inference targets for one overlap-specific OOF table."""

    if stride_samples <= 0 or window_size_samples <= 0:
        raise ValueError("window size and stride must be positive")
    canonical = validate_phase2_prediction_frame(
        frame, expected_stride_samples=stride_samples
    )
    n_windows = len(canonical)
    n_sessions = canonical[["subject_id", "session_id"]].drop_duplicates().shape[0]
    n_subjects = canonical["subject_id"].nunique()
    k0 = ceil(window_size_samples / stride_samples) - 1
    session_lengths = canonical.groupby(
        ["subject_id", "session_id"], sort=False
    ).size().to_numpy(dtype=np.int64)
    # Raw source bracketing indices are intentionally irregular after
    # timestamp interpolation and therefore are not a window-lag axis.
    time_column = (
        "resampled_start_index"
        if "resampled_start_index" in canonical
        else "window_start_time"
    )
    targets = _analysis_targets(canonical)
    audit_rows: list[dict[str, Any]] = []
    diagnostic_parts: list[pd.DataFrame] = []

    for (metric, contrast), (values, point) in targets.items():
        work = canonical[
            ["subject_id", "session_id", time_column]
        ].copy()
        work["analysis_value"] = values
        diagnostics = acf_diagnostics(
            work,
            "analysis_value",
            k0=k0,
            max_lag=maximum_acf_lag,
            time_column=time_column,
        )
        diagnostic_k = acf_threshold_bandwidth(
            diagnostics, minimum=k0, max_lag=maximum_acf_lag
        )
        bandwidths = {
            "k0": k0,
            "2k0": 2 * k0,
            "4k0": 4 * k0,
            "newey_west_rule": newey_west_rule_bandwidth(session_lengths, k0),
            "acf_threshold_diagnostic": diagnostic_k,
        }
        diagnostics.insert(0, "contrast", contrast)
        diagnostics.insert(0, "metric", metric)
        diagnostics.insert(0, "stride", stride_samples)
        diagnostics.insert(0, "overlap_percent", overlap_percent)
        for name, bandwidth in bandwidths.items():
            diagnostics[f"included_{name}"] = (
                diagnostics["lag"] <= bandwidth
            ).astype(int)
            diagnostics[f"bandwidth_{name}"] = bandwidth
        diagnostic_parts.append(diagnostics)

        null = 0.0 if contrast == "rf_minus_minirocket" else None
        iid = iid_normal_inference(values, point=point, null_value=null)
        audit_rows.append(
            _audit_row(
                overlap_percent=overlap_percent,
                stride=stride_samples,
                metric=metric,
                contrast=contrast,
                estimand="fixed_record_pooled_window",
                method="iid_normal",
                inference=iid,
                n_windows=n_windows,
                n_sessions=n_sessions,
                n_subjects=n_subjects,
                k0=k0,
                bandwidth_name=None,
                requested_bandwidth=0,
                effective_bandwidth=0,
                is_primary=False,
                is_sensitivity=False,
            )
        )
        for bandwidth_name, bandwidth in bandwidths.items():
            hac = session_centered_bartlett_hac(
                work,
                "analysis_value",
                bandwidth,
                point=point,
                time_column=time_column,
            )
            for distribution in ("z", "t"):
                inference = interval_from_variance(
                    point,
                    hac.variance,
                    estimand="fixed_record_pooled_window",
                    distribution=distribution,
                    degrees_of_freedom=(n_sessions - 1 if distribution == "t" else None),
                    null_value=null,
                )
                audit_rows.append(
                    _audit_row(
                        overlap_percent=overlap_percent,
                        stride=stride_samples,
                        metric=metric,
                        contrast=contrast,
                        estimand="fixed_record_pooled_window",
                        method=f"bartlett_hac_{bandwidth_name}",
                        inference=inference,
                        n_windows=n_windows,
                        n_sessions=n_sessions,
                        n_subjects=n_subjects,
                        k0=k0,
                        bandwidth_name=bandwidth_name,
                        requested_bandwidth=bandwidth,
                        effective_bandwidth=hac.effective_bandwidth,
                        is_primary=(
                            bandwidth_name == "newey_west_rule"
                            and distribution == "z"
                        ),
                        is_sensitivity=(
                            distribution == "t"
                            or bandwidth_name != "newey_west_rule"
                        ),
                    )
                )

    sessions = session_metric_statistics(canonical)
    subjects = subject_metric_statistics(canonical)
    metric_columns = {
        ("accuracy", "rf"): "accuracy_rf",
        ("accuracy", "minirocket"): "accuracy_minirocket",
        ("accuracy", "rf_minus_minirocket"): "paired_accuracy_difference",
        ("macro_f1", "rf"): "macro_f1_rf",
        ("macro_f1", "minirocket"): "macro_f1_minirocket",
        ("macro_f1", "rf_minus_minirocket"): "paired_macro_f1_difference",
    }
    comparison_rows: list[dict[str, Any]] = []
    fixed_audit = pd.DataFrame(audit_rows)
    for (metric, contrast), column in metric_columns.items():
        null = 0.0 if contrast == "rf_minus_minirocket" else None
        session_inference = subject_clustered_session_inference(
            sessions, column, null_value=null
        )
        subject_inference = equal_subject_t_inference(
            subjects, column, null_value=null
        )
        audit_rows.append(
            _audit_row(
                overlap_percent=overlap_percent,
                stride=stride_samples,
                metric=metric,
                contrast=contrast,
                estimand="new_session_equal_session",
                method="subject_clustered_session_sandwich",
                inference=session_inference,
                n_windows=n_windows,
                n_sessions=n_sessions,
                n_subjects=n_subjects,
                k0=k0,
                bandwidth_name=None,
                requested_bandwidth=None,
                effective_bandwidth=None,
                is_primary=False,
                is_sensitivity=False,
            )
        )
        audit_rows.append(
            _audit_row(
                overlap_percent=overlap_percent,
                stride=stride_samples,
                metric=metric,
                contrast=contrast,
                estimand="new_subject_equal_subject",
                method=(
                    "subject_level_paired_t"
                    if contrast == "rf_minus_minirocket"
                    else "subject_level_t"
                ),
                inference=subject_inference,
                n_windows=n_windows,
                n_sessions=n_sessions,
                n_subjects=n_subjects,
                k0=k0,
                bandwidth_name=None,
                requested_bandwidth=None,
                effective_bandwidth=None,
                is_primary=(contrast == "rf_minus_minirocket"),
                is_sensitivity=False,
            )
        )
        if contrast == "rf_minus_minirocket":
            fixed = fixed_audit[
                (fixed_audit["metric"] == metric)
                & (fixed_audit["contrast"] == contrast)
                & (fixed_audit["method"] == "bartlett_hac_newey_west_rule")
                & (fixed_audit["inference"] == "z_interval")
            ].iloc[0]
            rf_fixed = targets[(metric, "rf")][1]
            mini_fixed = targets[(metric, "minirocket")][1]
            for estimand, method, rf_point, mini_point, inference in (
                (
                    "fixed_record_pooled_window",
                    "bartlett_hac_newey_west_rule_z",
                    rf_fixed,
                    mini_fixed,
                    fixed,
                ),
                (
                    "new_session_equal_session",
                    "subject_clustered_session_sandwich",
                    float(sessions[metric_columns[(metric, "rf")]].mean()),
                    float(sessions[metric_columns[(metric, "minirocket")]].mean()),
                    session_inference,
                ),
                (
                    "new_subject_equal_subject",
                    "subject_level_paired_t",
                    float(subjects[metric_columns[(metric, "rf")]].mean()),
                    float(subjects[metric_columns[(metric, "minirocket")]].mean()),
                    subject_inference,
                ),
            ):
                if isinstance(inference, pd.Series):
                    get = inference.__getitem__
                    point_value = float(get("point"))
                    lower = float(get("ci_lower"))
                    upper = float(get("ci_upper"))
                    p_value = float(get("p_value_h0_difference_zero"))
                    reject = bool(get("reject_h0_difference_zero"))
                    df = get("degrees_of_freedom")
                else:
                    point_value = inference.point
                    lower = inference.lower
                    upper = inference.upper
                    p_value = inference.p_value
                    reject = bool(inference.reject_null)
                    df = inference.degrees_of_freedom
                comparison_rows.append(
                    {
                        "overlap_percent": overlap_percent,
                        "stride": stride_samples,
                        "metric": metric,
                        "estimand": estimand,
                        "method": method,
                        "rf_point": rf_point,
                        "minirocket_point": mini_point,
                        "paired_difference": point_value,
                        "ci_lower": lower,
                        "ci_upper": upper,
                        "p_value_h0_difference_zero": p_value,
                        "reject_h0_difference_zero": int(reject),
                        "degrees_of_freedom": df,
                        "n_windows": n_windows,
                        "n_sessions": n_sessions,
                        "n_subjects": n_subjects,
                    }
                )

    audit = pd.DataFrame(audit_rows)
    iid_widths = (
        audit[audit["method"] == "iid_normal"]
        .set_index(["metric", "contrast"])["ci_width"]
        .to_dict()
    )
    audit["iid_ci_width"] = [
        iid_widths.get((metric, contrast), np.nan)
        for metric, contrast in zip(audit["metric"], audit["contrast"], strict=True)
    ]
    audit["ci_inflation_factor"] = np.where(
        audit["iid_ci_width"] > 0,
        audit["ci_width"] / audit["iid_ci_width"],
        np.nan,
    )
    diagnostics = pd.concat(diagnostic_parts, ignore_index=True)
    heterogeneity = heterogeneity_decomposition(canonical)
    return Phase2InferenceOutputs(
        canonical_predictions=canonical,
        audit_summary=audit,
        bandwidth_diagnostics=diagnostics,
        estimand_comparison=pd.DataFrame(comparison_rows),
        session_statistics=sessions,
        subject_statistics=subjects,
        heterogeneity_decomposition=heterogeneity,
    )


__all__ = [
    "BartlettHACResult",
    "DEFAULT_KEY_COLUMNS",
    "HACVarianceError",
    "IntervalResult",
    "MacroF1Influence",
    "Phase2InferenceOutputs",
    "PredictionPairingError",
    "acf_diagnostics",
    "acf_threshold_bandwidth",
    "align_model_prediction_tables",
    "equal_subject_t_inference",
    "evaluate_phase2_inference",
    "heterogeneity_decomposition",
    "iid_normal_inference",
    "interval_from_variance",
    "macro_f1_with_influence",
    "newey_west_rule_bandwidth",
    "session_centered_bartlett_hac",
    "session_metric_statistics",
    "subject_clustered_session_inference",
    "subject_metric_statistics",
    "validate_phase2_prediction_frame",
]

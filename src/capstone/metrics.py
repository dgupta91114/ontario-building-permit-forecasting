from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error

EPS = 1e-12


def mae(y_true, y_pred) -> float:
    return float(mean_absolute_error(y_true, y_pred))


def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def smape(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denominator = np.abs(y_true) + np.abs(y_pred)
    return float(100.0 * np.mean(2.0 * np.abs(y_pred - y_true) / np.maximum(denominator, EPS)))


def wape(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(100.0 * np.sum(np.abs(y_true - y_pred)) / max(np.sum(np.abs(y_true)), EPS))


def seasonal_scales(
    train: pd.DataFrame,
    target_col: str = "permit_value_t_plus_1",
    group_col: str = "cma",
    date_col: str = "target_date",
    seasonality: int = 12,
) -> dict[str, float]:
    scales: dict[str, float] = {}
    for group, part in train.sort_values(date_col).groupby(group_col):
        values = part[target_col].to_numpy(dtype=float)
        if len(values) <= seasonality:
            scales[str(group)] = np.nan
            continue
        denominator = np.mean(np.abs(values[seasonality:] - values[:-seasonality]))
        scales[str(group)] = float(denominator) if denominator > EPS else np.nan
    return scales


def pooled_mase(y_true, y_pred, groups, scales: dict[str, float]) -> float:
    frame = pd.DataFrame({"y": y_true, "pred": y_pred, "group": groups})
    frame["scale"] = frame["group"].astype(str).map(scales)
    valid = frame["scale"].notna() & (frame["scale"] > EPS)
    if not valid.any():
        return float("nan")
    return float((np.abs(frame.loc[valid, "y"] - frame.loc[valid, "pred"]) / frame.loc[valid, "scale"]).mean())


def metric_row(
    y_true,
    y_pred,
    groups,
    scales: dict[str, float],
    model: str,
    interval_lower=None,
    interval_upper=None,
) -> dict[str, float | str]:
    row: dict[str, float | str] = {
        "model": model,
        "n": int(len(y_true)),
        "mae": mae(y_true, y_pred),
        "rmse": rmse(y_true, y_pred),
        "mase": pooled_mase(y_true, y_pred, groups, scales),
        "smape_pct": smape(y_true, y_pred),
        "wape_pct": wape(y_true, y_pred),
    }
    if interval_lower is not None and interval_upper is not None:
        y = np.asarray(y_true, dtype=float)
        lo = np.asarray(interval_lower, dtype=float)
        hi = np.asarray(interval_upper, dtype=float)
        row["interval_coverage"] = float(np.mean((y >= lo) & (y <= hi)))
        row["mean_interval_width"] = float(np.mean(hi - lo))
    return row


def paired_error_tests(y_true, pred_a, pred_b, max_lag: int = 3) -> dict[str, float]:
    """Compare absolute errors of model A versus model B.

    Positive improvement means model A has lower MAE than model B.
    The DM-style statistic uses a Newey-West long-run variance estimate.
    """
    y = np.asarray(y_true, dtype=float)
    a = np.asarray(pred_a, dtype=float)
    b = np.asarray(pred_b, dtype=float)
    err_a = np.abs(y - a)
    err_b = np.abs(y - b)
    diff = err_b - err_a
    t_result = stats.ttest_rel(err_b, err_a, nan_policy="omit")
    try:
        w_result = stats.wilcoxon(err_b, err_a, alternative="two-sided", zero_method="wilcox")
        wilcoxon_stat = float(w_result.statistic)
        wilcoxon_p = float(w_result.pvalue)
    except ValueError:
        wilcoxon_stat = float("nan")
        wilcoxon_p = float("nan")

    n = len(diff)
    centered = diff - np.mean(diff)
    gamma0 = float(np.dot(centered, centered) / n)
    long_run_var = gamma0
    for lag in range(1, min(max_lag, n - 1) + 1):
        gamma = float(np.dot(centered[lag:], centered[:-lag]) / n)
        weight = 1.0 - lag / (max_lag + 1.0)
        long_run_var += 2.0 * weight * gamma
    dm_stat = float(np.mean(diff) / np.sqrt(max(long_run_var / n, EPS)))
    dm_p = float(2.0 * (1.0 - stats.norm.cdf(abs(dm_stat))))

    return {
        "n": int(n),
        "mae_a": float(np.mean(err_a)),
        "mae_b": float(np.mean(err_b)),
        "improvement_pct_a_vs_b": float(100.0 * (np.mean(err_b) - np.mean(err_a)) / max(np.mean(err_b), EPS)),
        "paired_t_statistic": float(t_result.statistic),
        "paired_t_p_value": float(t_result.pvalue),
        "wilcoxon_statistic": wilcoxon_stat,
        "wilcoxon_p_value": wilcoxon_p,
        "dm_style_statistic": dm_stat,
        "dm_style_p_value": dm_p,
    }

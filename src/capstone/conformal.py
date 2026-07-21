from __future__ import annotations

from sklearn.base import clone
import numpy as np
import pandas as pd


def split_conformal_interval(
    model,
    X_train,
    y_train,
    train_dates,
    X_test,
    alpha: float = 0.10,
    calibration_months: int = 12,
):
    dates = pd.to_datetime(pd.Series(train_dates)).reset_index(drop=True)
    unique = np.array(sorted(dates.unique()))
    if len(unique) <= calibration_months + 12:
        raise ValueError("Insufficient training history for split-conformal calibration.")
    calibration_dates = set(unique[-calibration_months:])
    proper_mask = ~dates.isin(calibration_dates).to_numpy()
    calibration_mask = dates.isin(calibration_dates).to_numpy()

    fitted = clone(model)
    fitted.fit(X_train.iloc[proper_mask], np.asarray(y_train)[proper_mask])
    calibration_pred = np.maximum(fitted.predict(X_train.iloc[calibration_mask]), 0.0)
    residuals = np.abs(np.asarray(y_train)[calibration_mask] - calibration_pred)
    n = len(residuals)
    quantile_level = min(1.0, np.ceil((n + 1) * (1 - alpha)) / n)
    radius = float(np.quantile(residuals, quantile_level, method="higher"))

    point = np.maximum(fitted.predict(X_test), 0.0)
    lower = np.maximum(point - radius, 0.0)
    upper = point + radius
    return fitted, point, lower, upper, radius

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import project_root
from .utils import write_json


def build_features(
    permits: pd.DataFrame,
    unemployment: pd.DataFrame,
    overnight: pd.DataFrame,
    cfg: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    permits = permits.copy()
    permits["ref_date"] = pd.to_datetime(permits["ref_date"])
    unemployment = unemployment.copy()
    unemployment["ref_date"] = pd.to_datetime(unemployment["ref_date"])
    overnight = overnight.copy()
    overnight["ref_date"] = pd.to_datetime(overnight["ref_date"])

    panel = permits.merge(unemployment, on="ref_date", how="left", validate="many_to_one")
    panel = panel.merge(overnight, on="ref_date", how="left", validate="many_to_one")
    panel = panel.sort_values(["cma", "ref_date"]).reset_index(drop=True)

    # Macroeconomic lags are computed on the unique monthly series before replication across CMAs.
    macro = (
        panel[["ref_date", "overnight_rate", "ontario_unemployment_rate"]]
        .drop_duplicates("ref_date")
        .sort_values("ref_date")
    )
    macro["overnight_rate_lag_1"] = macro["overnight_rate"].shift(1)
    macro["unemployment_lag_1"] = macro["ontario_unemployment_rate"].shift(1)
    panel = panel.drop(columns=["overnight_rate", "ontario_unemployment_rate"]).merge(
        macro, on="ref_date", how="left", validate="many_to_one"
    )
    panel = panel.sort_values(["cma", "ref_date"]).reset_index(drop=True)

    grouped = panel.groupby("cma", group_keys=False, sort=False)
    horizon = int(cfg["features"]["forecast_horizon_months"])
    panel["target_date"] = panel["ref_date"] + pd.offsets.MonthBegin(horizon)
    panel["permit_value_t_plus_1"] = grouped["permit_value_t"].shift(-horizon)
    panel["log_target"] = np.log1p(panel["permit_value_t_plus_1"].clip(lower=0))

    for lag in cfg["features"]["lags"]:
        panel[f"lag_{lag}"] = grouped["permit_value_t"].shift(int(lag))

    for window in cfg["features"]["rolling_windows"]:
        # Includes the observed value at origin t and excludes the future target t+1.
        panel[f"rolling_mean_{window}"] = grouped["permit_value_t"].transform(
            lambda s: s.rolling(int(window), min_periods=int(window)).mean()
        )
        panel[f"rolling_sd_{window}"] = grouped["permit_value_t"].transform(
            lambda s: s.rolling(int(window), min_periods=int(window)).std(ddof=1)
        )

    # For target y_(t+1), the same month one year earlier is y_(t-11).
    seasonal_source_shift = 12 - horizon
    panel["seasonal_naive_pred"] = grouped["permit_value_t"].shift(seasonal_source_shift)

    target_month = panel["target_date"].dt.month
    panel["month_sin"] = np.sin(2 * np.pi * target_month / 12.0)
    panel["month_cos"] = np.cos(2 * np.pi * target_month / 12.0)
    start = panel["ref_date"].min()
    panel["time_index"] = (
        (panel["ref_date"].dt.year - start.year) * 12
        + (panel["ref_date"].dt.month - start.month)
    ).astype(int)

    pandemic_start = pd.Timestamp(cfg["features"]["pandemic_start"])
    pandemic_end = pd.Timestamp(cfg["features"]["pandemic_end"])
    panel["pandemic_indicator"] = panel["target_date"].between(pandemic_start, pandemic_end).astype(int)

    required = [
        "permit_value_t_plus_1",
        "seasonal_naive_pred",
        *cfg["features"]["primary_numeric_features"],
        *cfg["features"]["macro_features"],
        *cfg["features"]["categorical_features"],
    ]
    before = len(panel)
    modeling = panel.dropna(subset=required).copy()
    modeling = modeling.sort_values(["target_date", "cma"]).reset_index(drop=True)

    if modeling.duplicated(["cma", "target_date"]).any():
        raise ValueError("Feature engineering produced duplicate CMA-target-month rows.")
    if not (modeling["ref_date"] < modeling["target_date"]).all():
        raise AssertionError("Forecast origin must precede target date for every row.")

    audit = {
        "rows_before_complete_case_filter": int(before),
        "rows_after_complete_case_filter": int(len(modeling)),
        "rows_dropped": int(before - len(modeling)),
        "target_date_min": modeling["target_date"].min(),
        "target_date_max": modeling["target_date"].max(),
        "rows_by_cma": modeling.groupby("cma").size().to_dict(),
        "forecast_horizon_months": horizon,
        "seasonal_naive_source_shift_from_origin": seasonal_source_shift,
        "required_columns": required,
    }
    return modeling, audit


def build_dataset_from_interim(cfg: dict[str, Any], root: Path | None = None) -> Path:
    base = root or project_root()
    interim = base / "data" / "interim"
    permits = pd.read_csv(interim / "building_permits_clean.csv", parse_dates=["ref_date"])
    unemployment = pd.read_csv(interim / "ontario_unemployment_clean.csv", parse_dates=["ref_date"])
    overnight = pd.read_csv(interim / "overnight_rate_clean.csv", parse_dates=["ref_date"])
    modeling, audit = build_features(permits, unemployment, overnight, cfg)
    output = base / "data" / "processed" / "modeling_dataset.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    modeling.to_csv(output, index=False)
    write_json(audit, base / "data" / "processed" / "feature_audit.json")
    return output

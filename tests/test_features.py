import numpy as np
import pandas as pd

from capstone.features import build_features


def _cfg():
    return {
        "features": {
            "forecast_horizon_months": 1,
            "lags": [1, 3, 6, 12],
            "rolling_windows": [3],
            "pandemic_start": "2020-03-01",
            "pandemic_end": "2021-06-01",
            "primary_numeric_features": [
                "permit_value_t", "lag_1", "lag_3", "lag_6", "lag_12",
                "rolling_mean_3", "rolling_sd_3", "month_sin", "month_cos",
                "time_index", "pandemic_indicator"
            ],
            "macro_features": ["overnight_rate_lag_1", "unemployment_lag_1"],
            "categorical_features": ["cma"],
        }
    }


def test_target_and_seasonal_naive_alignment():
    dates = pd.date_range("2018-01-01", periods=30, freq="MS")
    permits = pd.DataFrame({
        "ref_date": dates,
        "cma": "Toronto",
        "dguid": "D1",
        "permit_value_t": np.arange(1, 31, dtype=float),
        "source_status": "",
    })
    macro = pd.DataFrame({
        "ref_date": dates,
        "ontario_unemployment_rate": np.linspace(6, 7, 30),
        "overnight_rate": np.linspace(1, 2, 30),
    })
    result, audit = build_features(
        permits,
        macro[["ref_date", "ontario_unemployment_rate"]],
        macro[["ref_date", "overnight_rate"]],
        _cfg(),
    )
    row = result.iloc[0]
    origin_position = permits.index[permits["ref_date"] == row["ref_date"]][0]
    assert row["permit_value_t_plus_1"] == permits.loc[origin_position + 1, "permit_value_t"]
    # Same target month one year earlier = origin position - 11.
    assert row["seasonal_naive_pred"] == permits.loc[origin_position - 11, "permit_value_t"]
    assert row["ref_date"] < row["target_date"]
    assert audit["seasonal_naive_source_shift_from_origin"] == 11


def test_features_do_not_cross_cma_boundaries():
    dates = pd.date_range("2018-01-01", periods=20, freq="MS")
    permits = pd.concat([
        pd.DataFrame({"ref_date": dates, "cma": "Toronto", "dguid": "D1", "permit_value_t": 100 + np.arange(20), "source_status": ""}),
        pd.DataFrame({"ref_date": dates, "cma": "Hamilton", "dguid": "D2", "permit_value_t": 1000 + np.arange(20), "source_status": ""}),
    ], ignore_index=True)
    macro = pd.DataFrame({"ref_date": dates, "ontario_unemployment_rate": 6.0, "overnight_rate": 1.0})
    result, _ = build_features(
        permits,
        macro[["ref_date", "ontario_unemployment_rate"]],
        macro[["ref_date", "overnight_rate"]],
        _cfg(),
    )
    assert result.groupby("cma")["lag_1"].min().to_dict()["Hamilton"] > 900
    assert result.groupby("cma")["lag_1"].max().to_dict()["Toronto"] < 200

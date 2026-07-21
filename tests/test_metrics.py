import numpy as np
import pandas as pd

from capstone.metrics import paired_error_tests, pooled_mase, seasonal_scales


def test_mase_is_one_for_matching_seasonal_error_scale():
    train = pd.DataFrame({
        "target_date": pd.date_range("2018-01-01", periods=24, freq="MS"),
        "cma": "A",
        "permit_value_t_plus_1": np.arange(24, dtype=float),
    })
    scales = seasonal_scales(train, seasonality=12)
    value = pooled_mase([100, 112], [88, 100], ["A", "A"], scales)
    assert np.isclose(value, 1.0)


def test_paired_error_improvement_direction():
    y = np.array([10, 20, 30, 40], dtype=float)
    better = np.array([11, 19, 31, 39], dtype=float)
    worse = np.array([15, 15, 35, 35], dtype=float)
    result = paired_error_tests(y, better, worse, max_lag=1)
    assert result["improvement_pct_a_vs_b"] > 0

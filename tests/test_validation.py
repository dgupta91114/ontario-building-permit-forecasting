import pandas as pd

from capstone.validation import assert_month_integrity, expanding_month_splits, temporal_holdout_indices


def test_temporal_holdout_keeps_months_together():
    dates = pd.Series(list(pd.date_range("2020-01-01", periods=24, freq="MS").repeat(5)))
    train_idx, test_idx = temporal_holdout_indices(dates, 6)
    train_dates = set(dates.iloc[train_idx])
    test_dates = set(dates.iloc[test_idx])
    assert not train_dates & test_dates
    assert len(test_dates) == 6
    assert max(train_dates) < min(test_dates)


def test_expanding_splits_keep_months_together():
    dates = pd.Series(list(pd.date_range("2020-01-01", periods=36, freq="MS").repeat(5)))
    splits = expanding_month_splits(dates, initial_train_months=18, test_months=6, step_months=6)
    assert len(splits) == 3
    assert_month_integrity(dates, splits)

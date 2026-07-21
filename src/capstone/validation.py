from __future__ import annotations

from collections.abc import Iterator

import numpy as np
import pandas as pd


def temporal_holdout_indices(dates, holdout_months: int) -> tuple[np.ndarray, np.ndarray]:
    dates = pd.to_datetime(pd.Series(dates)).reset_index(drop=True)
    unique = np.array(sorted(dates.dropna().unique()))
    if len(unique) <= holdout_months:
        raise ValueError("Not enough unique months for requested temporal holdout.")
    test_dates = set(unique[-holdout_months:])
    train_idx = np.flatnonzero(~dates.isin(test_dates).to_numpy())
    test_idx = np.flatnonzero(dates.isin(test_dates).to_numpy())
    return train_idx, test_idx


def expanding_month_splits(
    dates,
    initial_train_months: int,
    test_months: int,
    step_months: int,
) -> list[tuple[np.ndarray, np.ndarray]]:
    dates = pd.to_datetime(pd.Series(dates)).reset_index(drop=True)
    unique = np.array(sorted(dates.dropna().unique()))
    splits: list[tuple[np.ndarray, np.ndarray]] = []
    train_end = initial_train_months
    while train_end + test_months <= len(unique):
        train_dates = set(unique[:train_end])
        test_dates = set(unique[train_end : train_end + test_months])
        train_idx = np.flatnonzero(dates.isin(train_dates).to_numpy())
        test_idx = np.flatnonzero(dates.isin(test_dates).to_numpy())
        if len(train_idx) and len(test_idx):
            splits.append((train_idx, test_idx))
        train_end += step_months
    if not splits:
        raise ValueError(
            "No rolling-origin splits were created. Reduce initial_train_months/test_months "
            "or provide a longer history."
        )
    return splits


def assert_month_integrity(dates, splits: list[tuple[np.ndarray, np.ndarray]]) -> None:
    dates = pd.to_datetime(pd.Series(dates)).reset_index(drop=True)
    for train_idx, test_idx in splits:
        train_dates = set(dates.iloc[train_idx])
        test_dates = set(dates.iloc[test_idx])
        if train_dates & test_dates:
            raise AssertionError("A calendar month appears in both train and test within a split.")
        if max(train_dates) >= min(test_dates):
            raise AssertionError("Rolling-origin training dates must precede test dates.")

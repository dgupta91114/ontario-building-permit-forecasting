from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
from scipy.optimize import brentq
from scipy.stats import f, ncf, norm
from statsmodels.stats.power import FTestAnovaPower, TTestPower

from .config import project_root


def correlation_sample_size(r: float, alpha: float, power: float) -> int:
    n = ((norm.ppf(1 - alpha / 2) + norm.ppf(power)) / math.atanh(r)) ** 2 + 3
    return math.ceil(n)


def multiple_regression_sample_size(
    f_squared: float, tested_predictors: int, alpha: float, power: float
) -> int:
    def achieved(n: float) -> float:
        denominator_df = n - tested_predictors - 1
        if denominator_df <= 0:
            return 0.0
        critical = f.ppf(1 - alpha, tested_predictors, denominator_df)
        noncentrality = f_squared * n
        return float(1 - ncf.cdf(critical, tested_predictors, denominator_df, noncentrality))

    root = brentq(lambda n: achieved(n) - power, tested_predictors + 3, 10000)
    return math.ceil(root)


def calculate_sample_sizes() -> pd.DataFrame:
    alpha = 0.05
    power = 0.80
    rows = [
        {
            "research_question": "RQ1",
            "method": "Correlation / Fisher z",
            "key_parameters": "alpha=.05; power=.80; r=.30; two-sided",
            "minimum_n": correlation_sample_size(0.30, alpha, power),
        },
        {
            "research_question": "RQ2",
            "method": "Multiple regression F test",
            "key_parameters": "alpha=.05; power=.80; f-squared=.15; tested predictors=10",
            "minimum_n": multiple_regression_sample_size(0.15, 10, alpha, power),
        },
        {
            "research_question": "RQ3",
            "method": "Paired forecast-error t test",
            "key_parameters": "alpha=.05; power=.80; paired d=.35; two-sided",
            "minimum_n": math.ceil(
                TTestPower().solve_power(effect_size=0.35, alpha=alpha, power=power, alternative="two-sided")
            ),
        },
        {
            "research_question": "RQ4",
            "method": "One-way ANOVA",
            "key_parameters": "alpha=.05; power=.80; Cohen f=.25; groups=5",
            "minimum_n": math.ceil(
                FTestAnovaPower().solve_power(effect_size=0.25, alpha=alpha, power=power, k_groups=5)
            ),
        },
    ]
    return pd.DataFrame(rows)


def save_sample_sizes(root: Path | None = None) -> Path:
    base = root or project_root()
    output = base / "outputs" / "tables" / "sample_size_calculations.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    calculate_sample_sizes().to_csv(output, index=False)
    return output

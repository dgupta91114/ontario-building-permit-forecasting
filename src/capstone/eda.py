from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.tsa.stattools import acf

from .config import project_root
from .utils import write_json


def run_rq1_eda(data: pd.DataFrame, cfg: dict[str, Any], root: Path | None = None) -> dict[str, Path]:
    base = root or project_root()
    figures = base / "outputs" / "figures"
    tables = base / "outputs" / "tables"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)

    frame = data.copy()
    frame["ref_date"] = pd.to_datetime(frame["ref_date"])
    summary = frame.groupby("cma")["permit_value_t"].agg(
        n="count", mean="mean", median="median", std="std", minimum="min", maximum="max"
    )
    summary["coefficient_of_variation"] = summary["std"] / summary["mean"]
    summary_path = tables / "rq1_summary_by_cma.csv"
    summary.reset_index().to_csv(summary_path, index=False)

    persistence_rows = []
    for cma, part in frame.sort_values("ref_date").groupby("cma"):
        values = part["permit_value_t"].to_numpy(dtype=float)
        coeffs = acf(values, nlags=min(12, len(values) - 1), fft=False, missing="drop")
        persistence_rows.append(
            {
                "cma": cma,
                "acf_lag_1": float(coeffs[1]) if len(coeffs) > 1 else np.nan,
                "acf_lag_12": float(coeffs[12]) if len(coeffs) > 12 else np.nan,
            }
        )
    persistence = pd.DataFrame(persistence_rows)
    persistence_path = tables / "rq1_persistence.csv"
    persistence.to_csv(persistence_path, index=False)

    # HAC regression addresses autocorrelation/heteroskedasticity in the pooled descriptive test.
    regression = frame.dropna(subset=["permit_value_t_plus_1", "permit_value_t", "month_sin", "month_cos"]).copy()
    design = pd.get_dummies(
        regression[["permit_value_t", "month_sin", "month_cos", "time_index", "cma"]],
        columns=["cma"],
        drop_first=True,
        dtype=float,
    )
    design = sm.add_constant(design, has_constant="add")
    model = sm.OLS(regression["permit_value_t_plus_1"], design).fit(
        cov_type="HAC", cov_kwds={"maxlags": 3}
    )
    coef = pd.DataFrame(
        {
            "term": model.params.index,
            "coefficient": model.params.values,
            "standard_error_hac": model.bse.values,
            "t_statistic": model.tvalues.values,
            "p_value": model.pvalues.values,
        }
    )
    coef_path = tables / "rq1_hac_regression.csv"
    coef.to_csv(coef_path, index=False)

    # Trend figure
    fig, ax = plt.subplots(figsize=(10, 6))
    for cma, part in frame.groupby("cma"):
        part = part.sort_values("ref_date")
        ax.plot(part["ref_date"], part["permit_value_t"], label=cma, linewidth=1.3)
    ax.set_title("Monthly Residential Building-Permit Values by Ontario CMA")
    ax.set_xlabel("Reference month")
    ax.set_ylabel("Permit value ($000s)")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    trend_path = figures / "rq1_trend_by_cma.png"
    fig.savefig(trend_path, dpi=200)
    plt.close(fig)

    # Seasonal profile figure
    seasonal = frame.assign(month=frame["ref_date"].dt.month).groupby(["cma", "month"])["permit_value_t"].median().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    for cma, part in seasonal.groupby("cma"):
        ax.plot(part["month"], part["permit_value_t"], marker="o", label=cma)
    ax.set_title("Median Seasonal Profile by CMA")
    ax.set_xlabel("Calendar month")
    ax.set_ylabel("Median permit value ($000s)")
    ax.set_xticks(range(1, 13))
    ax.legend(fontsize=8, ncol=2)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    seasonal_path = figures / "rq1_seasonal_profile.png"
    fig.savefig(seasonal_path, dpi=200)
    plt.close(fig)

    write_json(
        {
            "hac_r_squared": float(model.rsquared),
            "hac_adjusted_r_squared": float(model.rsquared_adj),
            "n": int(model.nobs),
            "trend_figure": str(trend_path.relative_to(base)),
            "seasonal_figure": str(seasonal_path.relative_to(base)),
        },
        tables / "rq1_model_summary.json",
    )
    return {
        "summary": summary_path,
        "persistence": persistence_path,
        "regression": coef_path,
        "trend_figure": trend_path,
        "seasonal_figure": seasonal_path,
    }

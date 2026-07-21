from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import project_root


def generate_synthetic_modeling_dataset(cfg: dict[str, Any], root: Path | None = None) -> Path:
    """Create synthetic software-test data. Never use this for substantive capstone results."""
    base = root or project_root()
    rng = np.random.default_rng(int(cfg["project"]["random_seed"]))
    dates = pd.date_range("2018-01-01", "2026-05-01", freq="MS")
    cmas = list(cfg["project"]["selected_cmas"])
    rows = []
    for i, cma in enumerate(cmas):
        level = 120000 + i * 25000
        series = []
        for t, date in enumerate(dates):
            seasonal = 20000 * np.sin(2 * np.pi * date.month / 12)
            trend = 900 * t
            shock = rng.normal(0, 12000 + i * 1500)
            if pd.Timestamp("2020-03-01") <= date <= pd.Timestamp("2021-06-01"):
                shock -= 18000
            value = max(level + seasonal + trend + shock, 1000)
            series.append(value)
        for date, value in zip(dates, series):
            rows.append({
                "ref_date": date,
                "cma": cma,
                "dguid": f"DEMO-{i}",
                "permit_value_t": value,
                "source_status": "DEMO",
            })
    permits = pd.DataFrame(rows)
    macro_dates = pd.DataFrame({"ref_date": dates})
    macro_dates["ontario_unemployment_rate"] = 6.0 + 0.5 * np.sin(np.arange(len(dates)) / 8) + rng.normal(0, 0.2, len(dates))
    macro_dates["overnight_rate"] = np.clip(1.5 + 0.8 * np.sin(np.arange(len(dates)) / 15), 0.25, 5.0)

    from .features import build_features
    modeling, _ = build_features(
        permits,
        macro_dates[["ref_date", "ontario_unemployment_rate"]],
        macro_dates[["ref_date", "overnight_rate"]],
        cfg,
    )
    output = base / "data" / "demo" / "synthetic_modeling_dataset.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    modeling.to_csv(output, index=False)
    return output

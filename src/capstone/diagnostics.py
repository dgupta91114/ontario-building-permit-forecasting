from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import project_root
from .utils import sha256_file, write_json


def generate_holdout_diagnostics(root: Path | None = None) -> dict[str, Path]:
    base = root or project_root()
    tables = base / "outputs" / "tables"
    figures = base / "outputs" / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    selection = json.loads((tables / "model_selection.json").read_text(encoding="utf-8"))
    selected = selection["selected_model"]
    predictions = pd.read_csv(tables / "holdout_predictions.csv", parse_dates=["target_date"])
    chosen = predictions[predictions["model"] == selected].copy()
    chosen["residual"] = chosen["actual"] - chosen["prediction"]
    chosen["absolute_error"] = chosen["residual"].abs()

    cmas = sorted(chosen["cma"].unique())
    fig, axes = plt.subplots(len(cmas), 1, figsize=(10, 13), sharex=True)
    for ax, cma in zip(axes, cmas):
        part = chosen[chosen["cma"] == cma].sort_values("target_date")
        ax.plot(part["target_date"], part["actual"], marker="o", label="Actual")
        ax.plot(part["target_date"], part["prediction"], marker="s", label="Forecast")
        ax.set_title(cma)
        ax.set_ylabel("$000s")
        ax.grid(alpha=0.25)
    axes[0].legend(ncol=2)
    axes[-1].set_xlabel("Target month")
    fig.suptitle(f"Official Holdout Actual and Forecast Values — {selected}", y=0.995)
    fig.tight_layout()
    actual_path = figures / "selected_model_actual_vs_predicted.png"
    fig.savefig(actual_path, dpi=220, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    for cma, part in chosen.groupby("cma"):
        part = part.sort_values("target_date")
        ax.plot(part["target_date"], part["absolute_error"], marker="o", label=cma)
    ax.set_title(f"Official Holdout Absolute Error Over Time — {selected}")
    ax.set_xlabel("Target month")
    ax.set_ylabel("Absolute error ($000s)")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    error_path = figures / "selected_model_absolute_error.png"
    fig.savefig(error_path, dpi=220)
    plt.close(fig)

    interval = pd.read_csv(tables / "selected_model_intervals.csv", parse_dates=["target_date"])
    interval["interval_width"] = interval["upper_90"] - interval["lower_90"]
    coverage = interval.groupby("cma").agg(
        n=("covered", "size"),
        coverage=("covered", "mean"),
        mean_interval_width=("interval_width", "mean"),
        median_interval_width=("interval_width", "median"),
    ).reset_index()
    coverage_path = tables / "rq4_interval_coverage_by_cma.csv"
    coverage.to_csv(coverage_path, index=False)

    extremes = chosen.nlargest(10, "actual")[
        ["target_date", "cma", "actual", "prediction", "residual", "absolute_error"]
    ]
    extremes_path = tables / "holdout_largest_actual_values.csv"
    extremes.to_csv(extremes_path, index=False)
    return {
        "actual_vs_predicted": actual_path,
        "absolute_error": error_path,
        "coverage": coverage_path,
        "extremes": extremes_path,
    }


def write_official_run_manifest(root: Path | None = None) -> Path:
    base = root or project_root()
    raw_manifest = json.loads((base / "data" / "raw" / "download_manifest.json").read_text(encoding="utf-8"))
    tracked = [
        base / "config" / "config.yaml",
        base / "data" / "processed" / "modeling_dataset.csv",
        base / "data" / "processed" / "feature_audit.json",
        base / "data" / "interim" / "cleaning_audit.json",
        base / "outputs" / "tables" / "rq3_model_metrics.csv",
        base / "outputs" / "tables" / "model_selection.json",
    ]
    manifest: dict[str, Any] = {
        "evidence_type": "official empirical analysis",
        "synthetic_data_used": False,
        "analysis_window": {"start": "2018-01-01", "end": "2026-05-01"},
        "raw_sources": raw_manifest,
        "sha256": {str(p.relative_to(base)): sha256_file(p) for p in tracked},
    }
    output = base / "outputs" / "official_run_manifest.json"
    write_json(manifest, output)
    return output

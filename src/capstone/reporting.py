from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .config import project_root


def _markdown_table(df: pd.DataFrame, digits: int = 3) -> str:
    display = df.copy()
    for col in display.select_dtypes(include="number").columns:
        display[col] = display[col].map(lambda x: f"{x:.{digits}f}" if pd.notna(x) else "")
    headers = list(display.columns)
    rows = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for _, row in display.iterrows():
        rows.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    return "\n".join(rows)


def generate_results_summary(cfg: dict[str, Any], root: Path | None = None) -> Path:
    base = root or project_root()
    tables = base / "outputs" / "tables"
    selection = json.loads((tables / "model_selection.json").read_text(encoding="utf-8"))
    metrics = pd.read_csv(tables / "rq3_model_metrics.csv")
    rq2 = pd.read_csv(tables / "rq2_incremental_value.csv")
    regional = pd.read_csv(tables / "rq4_regional_metrics.csv")
    sample = pd.read_csv(tables / "sample_size_calculations.csv")
    audit_path = base / "data" / "processed" / "feature_audit.json"
    if audit_path.exists():
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
    else:
        dataset_candidates = [
            base / "data" / "processed" / "modeling_dataset.csv",
            base / "data" / "demo" / "synthetic_modeling_dataset.csv",
        ]
        dataset_path = next((p for p in dataset_candidates if p.exists()), None)
        if dataset_path is None:
            raise FileNotFoundError("No feature audit or modeling dataset is available for the results summary.")
        dataset = pd.read_csv(dataset_path, parse_dates=["target_date"])
        audit = {
            "rows_after_complete_case_filter": len(dataset),
            "target_date_min": dataset["target_date"].min().isoformat(),
            "target_date_max": dataset["target_date"].max().isoformat(),
            "rows_by_cma": dataset.groupby("cma").size().to_dict(),
        }

    lines = [
        "# Generated Results Summary",
        "",
        "> This file is generated from the analysis outputs. Confirm all interpretations against the tables and figures before copying text into the final paper.",
        "",
        "## Dataset",
        "",
        f"- Analytic observations: **{audit['rows_after_complete_case_filter']} CMA-months**",
        f"- Target period: **{audit['target_date_min']} to {audit['target_date_max']}**",
        f"- Selected CMAs: **{', '.join(audit['rows_by_cma'].keys())}**",
        "",
        "## Sample-size calculations",
        "",
        _markdown_table(sample),
        "",
        "## RQ2 — Incremental predictive value of macroeconomic variables",
        "",
        _markdown_table(rq2),
        "",
        "## RQ3 — Holdout model comparison",
        "",
        _markdown_table(metrics),
        "",
        "## Prespecified model-selection outcome",
        "",
        f"- Selected model: **{selection['selected_model']}**",
        f"- Rule outcome: {selection['rule_outcome']}",
        f"- Holdout interval coverage: {selection['holdout_interval_coverage']:.3f}",
        "",
        "## RQ4 — Regional reliability",
        "",
        _markdown_table(regional),
        "",
        "## Interpretation checklist",
        "",
        "- Report out-of-sample results, not training fit, as the primary evidence.",
        "- Describe associations and predictive value; do not claim causal effects.",
        "- State that building permits measure construction intentions rather than completed construction.",
        "- Discuss unusually large projects as potential genuine events, not automatic data errors.",
        "- Report negative or mixed results when the prespecified rule retains the benchmark.",
    ]
    output = base / "outputs" / "results_summary.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output

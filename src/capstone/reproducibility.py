from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from .config import project_root
from .utils import sha256_file, write_json


def run_reproducibility_check(root: Path | None = None) -> dict:
    base = root or project_root()
    required = [
        base / "README.md",
        base / "config" / "config.yaml",
        base / "docs" / "data_dictionary.csv",
        base / "docs" / "source_manifest.csv",
        base / "data" / "processed" / "modeling_dataset.csv",
        base / "outputs" / "tables" / "sample_size_calculations.csv",
        base / "outputs" / "tables" / "rq3_model_metrics.csv",
        base / "outputs" / "tables" / "model_selection.json",
    ]
    missing = [str(p.relative_to(base)) for p in required if not p.exists()]
    hashes = {str(p.relative_to(base)): sha256_file(p) for p in required if p.exists()}
    dataset_checks = {}
    dataset = base / "data" / "processed" / "modeling_dataset.csv"
    if dataset.exists():
        frame = pd.read_csv(dataset)
        dataset_checks = {
            "rows": len(frame),
            "columns": len(frame.columns),
            "duplicate_cma_target_rows": int(frame.duplicated(["cma", "target_date"]).sum()),
            "missing_target": int(frame["permit_value_t_plus_1"].isna().sum()),
        }
    test = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=base,
        capture_output=True,
        text=True,
        check=False,
    )
    report = {
        "passed": not missing and test.returncode == 0 and dataset_checks.get("duplicate_cma_target_rows", 1) == 0,
        "missing_required_files": missing,
        "sha256": hashes,
        "dataset_checks": dataset_checks,
        "pytest_return_code": test.returncode,
        "pytest_stdout": test.stdout,
        "pytest_stderr": test.stderr,
    }
    output = base / "outputs" / "reproducibility_report.json"
    write_json(report, output)
    return report

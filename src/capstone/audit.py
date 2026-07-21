from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .cleaning import _load_manifest, _manifest_csv, _read_statcan_csv
from .config import project_root
from .utils import normalize_text


def inspect_statcan_table(df: pd.DataFrame, output_dir: Path, prefix: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"column": df.columns}).to_csv(output_dir / f"{prefix}_columns.csv", index=False)
    likely_dimensions = [
        c for c in df.columns
        if c.upper() not in {"REF_DATE", "VALUE", "STATUS", "SYMBOL", "TERMINATED", "DECIMALS", "SCALAR_ID", "UOM_ID"}
        and df[c].nunique(dropna=True) <= 500
    ]
    for col in likely_dimensions:
        values = pd.DataFrame({col: sorted(df[col].dropna().astype(str).unique())})
        safe = normalize_text(col).replace(" ", "_")[:60]
        values.to_csv(output_dir / f"{prefix}_{safe}_values.csv", index=False)


def inspect_sources(cfg: dict[str, Any], root: Path | None = None) -> Path:
    base = root or project_root()
    manifest = _load_manifest(base)
    output = base / "outputs" / "tables" / "source_audit"
    for key in ["statcan_building_permits", "statcan_unemployment"]:
        product_id = cfg["sources"][key]["product_id"]
        path = _manifest_csv(manifest, "product_id", product_id, base)
        frame = _read_statcan_csv(path)
        inspect_statcan_table(frame, output, product_id)
    return output

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


def inspect_statcan_path(path: Path, output_dir: Path, prefix: str) -> None:
    """Audit a full-table CSV in chunks, capping high-cardinality dimensions."""
    output_dir.mkdir(parents=True, exist_ok=True)
    columns = list(pd.read_csv(path, nrows=0).columns)
    pd.DataFrame({"column": columns}).to_csv(output_dir / f"{prefix}_columns.csv", index=False)
    excluded = {
        "REF_DATE", "VALUE", "STATUS", "SYMBOL", "TERMINATED", "DECIMALS",
        "SCALAR_ID", "UOM_ID", "VECTOR", "COORDINATE", "DGUID",
    }
    dimensions = [c for c in columns if c.upper() not in excluded]
    values: dict[str, set[str]] = {c: set() for c in dimensions}
    high_cardinality: set[str] = set()
    for chunk in pd.read_csv(path, usecols=dimensions, chunksize=250_000, low_memory=False):
        for column in dimensions:
            if column in high_cardinality:
                continue
            values[column].update(chunk[column].dropna().astype(str).unique())
            if len(values[column]) > 500:
                high_cardinality.add(column)
                values[column].clear()
    for column, observed in values.items():
        if column in high_cardinality:
            continue
        safe = normalize_text(column).replace(" ", "_")[:60]
        pd.DataFrame({column: sorted(observed)}).to_csv(
            output_dir / f"{prefix}_{safe}_values.csv", index=False
        )
    pd.DataFrame({"high_cardinality_dimension": sorted(high_cardinality)}).to_csv(
        output_dir / f"{prefix}_high_cardinality.csv", index=False
    )


def inspect_sources(cfg: dict[str, Any], root: Path | None = None) -> Path:
    base = root or project_root()
    manifest = _load_manifest(base)
    output = base / "outputs" / "tables" / "source_audit"
    for key in ["statcan_building_permits", "statcan_unemployment"]:
        product_id = cfg["sources"][key]["product_id"]
        path = _manifest_csv(manifest, "product_id", product_id, base)
        inspect_statcan_path(path, output, product_id)
    return output

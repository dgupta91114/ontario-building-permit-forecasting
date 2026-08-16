from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import project_root
from .utils import choose_dimension_label, find_column, normalize_text, write_json


def _load_manifest(root: Path) -> list[dict[str, Any]]:
    path = root / "data" / "raw" / "download_manifest.json"
    if not path.exists():
        raise FileNotFoundError("Download manifest not found. Run scripts/01_download_data.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest_csv(manifest: list[dict[str, Any]], key: str, value: str, root: Path) -> Path:
    for item in manifest:
        if str(item.get(key)) == str(value):
            return root / item["csv_path"]
    raise KeyError(f"No manifest entry with {key}={value}")


def _read_statcan_csv(path: Path) -> pd.DataFrame:
    # low_memory=False avoids mixed-type inference warnings in status/symbol columns.
    return pd.read_csv(path, low_memory=False)


def _statcan_chunks(path: Path, usecols: list[str], chunksize: int = 250_000):
    """Read a large Statistics Canada CSV with bounded memory."""
    yield from pd.read_csv(path, usecols=usecols, chunksize=chunksize, low_memory=False)


def _canonical_cma(geo: str, selected: dict[str, Any]) -> str | None:
    norm = normalize_text(geo)
    if "ontario" not in norm:
        return None
    for canonical, rule in selected.items():
        patterns = [normalize_text(p) for p in rule.get("patterns", [])]
        if patterns and all(pattern in norm for pattern in patterns):
            return canonical
    return None


def clean_building_permits(
    cfg: dict[str, Any], root: Path | None = None, df: pd.DataFrame | None = None,
    value_basis: str = "current",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    base = root or project_root()
    source_rows: int | None = None
    if df is None:
        manifest = _load_manifest(base)
        product_id = cfg["sources"]["statcan_building_permits"]["product_id"]
        path = _manifest_csv(manifest, "product_id", product_id, base)
        columns = list(pd.read_csv(path, nrows=0).columns)
        combined_col = "Seasonal adjustment, value type"
        if combined_col not in columns:
            df = _read_statcan_csv(path)
        else:
            building_col = "Type of building"
            usecols = [
                "REF_DATE", "GEO", "DGUID", building_col, "Type of work",
                "Variables", combined_col, "UOM", "SCALAR_FACTOR", "VALUE", "STATUS",
            ]
            fcfg = cfg["filters"]["building_permits"]
            basis_cfg = fcfg["seasonal_adjustment_value_type"][value_basis]
            chosen_combined = basis_cfg["exact_candidates"][0]
            chosen_building = fcfg["type_of_structure"]["exact_candidates"][0]
            chosen_work = fcfg["type_of_work"]["exact_candidates"][0]
            chosen_variable = fcfg["variable"]["exact_candidates"][0]
            selected_parts: list[pd.DataFrame] = []
            observed = {combined_col: set(), building_col: set(), "Type of work": set(), "Variables": set()}
            source_rows = 0
            start = cfg["project"]["start_date"][:7]
            end = cfg["project"]["end_date"][:7]
            geo_lookup = {
                f"{canonical}, Ontario": canonical
                for canonical in cfg["project"]["selected_cmas"]
            }
            for chunk in _statcan_chunks(path, usecols):
                source_rows += len(chunk)
                dates = chunk["REF_DATE"].astype(str)
                relevant = chunk[
                    chunk["GEO"].isin(geo_lookup) & dates.between(start, end)
                ].copy()
                relevant["cma"] = relevant["GEO"].map(geo_lookup)
                for column in observed:
                    observed[column].update(relevant[column].dropna().astype(str).unique())
                mask = (
                    (relevant[combined_col].astype(str) == chosen_combined)
                    & (relevant[building_col].astype(str) == chosen_building)
                    & (relevant["Type of work"].astype(str) == chosen_work)
                    & (relevant["Variables"].astype(str) == chosen_variable)
                    & (relevant["UOM"].astype(str) == "Dollars")
                    & (relevant["SCALAR_FACTOR"].astype(str) == "thousands")
                )
                selected_parts.append(relevant.loc[mask])
            df = pd.concat(selected_parts, ignore_index=True) if selected_parts else pd.DataFrame()
            if df.empty:
                available = {k: sorted(v) for k, v in observed.items()}
                raise ValueError(f"Official building-permit filters returned zero rows. Observed labels: {available}")

    date_col = find_column(df, ["REF_DATE", "Reference period"], ["ref", "date"])
    geo_col = find_column(df, ["GEO", "Geography"], ["geo"])
    dguid_col = find_column(df, ["DGUID"], ["dguid"])
    value_col = find_column(df, ["VALUE", "Value"], ["value"])
    status_col = find_column(df, ["STATUS", "Status"], ["status"])
    combined_schema = "Seasonal adjustment, value type" in df.columns
    if combined_schema:
        seasonal_col = "Seasonal adjustment, value type"
        value_type_col = seasonal_col
        structure_col = find_column(df, ["Type of building"], ["type", "building"])
        variable_col = find_column(df, ["Variables"], ["variable"])
    else:
        seasonal_col = find_column(df, ["Seasonal adjustment"], ["seasonal", "adjustment"])
        value_type_col = find_column(df, ["Value type"], ["value", "type"])
        structure_col = find_column(df, ["Type of structure"], ["type", "structure"])
        variable_col = None
    work_col = find_column(df, ["Type of work"], ["type", "work"])

    fcfg = cfg["filters"]["building_permits"]
    if combined_schema:
        basis_cfg = fcfg["seasonal_adjustment_value_type"][value_basis]
        combined = choose_dimension_label(df[seasonal_col], **basis_cfg)
        seasonal_label = combined
        value_type_label = combined
    else:
        seasonal_label = choose_dimension_label(df[seasonal_col], **fcfg["seasonal_adjustment"])
        value_type_label = choose_dimension_label(df[value_type_col], **fcfg["value_type"])
    chosen = {
        "seasonal_adjustment": seasonal_label,
        "value_type": value_type_label,
        "type_of_structure": choose_dimension_label(df[structure_col], **fcfg["type_of_structure"]),
        "type_of_work": choose_dimension_label(df[work_col], **fcfg["type_of_work"]),
    }
    if variable_col:
        chosen["variable"] = choose_dimension_label(df[variable_col], **fcfg["variable"])

    working = df.copy()
    working["ref_date"] = pd.to_datetime(working[date_col], errors="coerce")
    working["cma"] = working[geo_col].map(
        lambda x: _canonical_cma(str(x), cfg["project"]["selected_cmas"])
    )
    mask = (
        working["cma"].notna()
        & (working[seasonal_col].astype(str) == chosen["seasonal_adjustment"])
        & (working[value_type_col].astype(str) == chosen["value_type"])
        & (working[structure_col].astype(str) == chosen["type_of_structure"])
        & (working[work_col].astype(str) == chosen["type_of_work"])
        & working["ref_date"].between(
            pd.Timestamp(cfg["project"]["start_date"]),
            pd.Timestamp(cfg["project"]["end_date"]),
        )
    )
    if variable_col:
        mask &= working[variable_col].astype(str) == chosen["variable"]
    working = working.loc[mask].copy()
    working["permit_value_t"] = pd.to_numeric(working[value_col], errors="coerce")
    working = working.rename(columns={dguid_col: "dguid", status_col: "source_status"})
    keep = [
        "ref_date",
        "cma",
        "dguid",
        "permit_value_t",
        "source_status",
    ]
    working = working[keep].sort_values(["cma", "ref_date"])

    duplicated = working.duplicated(["cma", "ref_date"], keep=False)
    if duplicated.any():
        examples = working.loc[duplicated, ["cma", "ref_date"]].head(20).to_dict("records")
        raise ValueError(
            "Building-permit filters produced duplicate CMA-month rows. "
            f"Examples: {examples}. Inspect source labels and tighten config filters."
        )

    selected_cmas = set(cfg["project"]["selected_cmas"])
    found_cmas = set(working["cma"].dropna())
    missing = sorted(selected_cmas - found_cmas)
    if missing:
        raise ValueError(f"No building-permit data found for configured CMAs: {missing}")
    if working["permit_value_t"].notna().sum() == 0:
        raise ValueError("All selected building-permit values are missing.")

    report = {
        "source_rows": int(source_rows if source_rows is not None else len(df)),
        "selected_rows": int(len(working)),
        "date_min": working["ref_date"].min(),
        "date_max": working["ref_date"].max(),
        "rows_by_cma": working.groupby("cma").size().to_dict(),
        "missing_values": int(working["permit_value_t"].isna().sum()),
        "chosen_labels": chosen,
        "value_basis": value_basis,
        "source_schema": "combined seasonal adjustment/value type" if combined_schema else "separate dimensions",
        "source_columns": {
            "date": date_col,
            "geography": geo_col,
            "dguid": dguid_col,
            "value": value_col,
            "status": status_col,
            "seasonal_adjustment": seasonal_col,
            "value_type": value_type_col,
            "type_of_structure": structure_col,
            "type_of_work": work_col,
        },
    }
    return working, report


def _choose_exact_or_tokens(series: pd.Series, exact: list[str], tokens: list[str]) -> str:
    return choose_dimension_label(series, exact, tokens, [])


def clean_unemployment(
    cfg: dict[str, Any], root: Path | None = None, df: pd.DataFrame | None = None
) -> tuple[pd.DataFrame, dict[str, Any]]:
    base = root or project_root()
    source_rows: int | None = None
    if df is None:
        manifest = _load_manifest(base)
        product_id = cfg["sources"]["statcan_unemployment"]["product_id"]
        path = _manifest_csv(manifest, "product_id", product_id, base)
        usecols = ["REF_DATE", "GEO", "Labour force characteristics", "Gender", "Age group", "Statistics", "Data type", "VALUE"]
        parts = []
        source_rows = 0
        start = cfg["project"]["start_date"][:7]
        end = cfg["project"]["end_date"][:7]
        for chunk in _statcan_chunks(path, usecols):
            source_rows += len(chunk)
            dates = chunk["REF_DATE"].astype(str)
            parts.append(chunk[(chunk["GEO"].astype(str) == "Ontario") & dates.between(start, end)])
        df = pd.concat(parts, ignore_index=True)

    date_col = find_column(df, ["REF_DATE"], ["ref", "date"])
    geo_col = find_column(df, ["GEO", "Geography"], ["geo"])
    value_col = find_column(df, ["VALUE", "Value"], ["value"])
    characteristic_col = find_column(
        df, ["Labour force characteristics"], ["labour", "force", "character"]
    )
    data_type_col = find_column(df, ["Data type"], ["data", "type"])
    gender_col = find_column(df, ["Gender", "Sex"], ["gender"])
    age_col = find_column(df, ["Age group"], ["age", "group"])
    statistics_col = find_column(df, ["Statistics"], ["statistic"]) if "Statistics" in df.columns else None

    fcfg = cfg["filters"]["unemployment"]
    labels = {
        "geography": _choose_exact_or_tokens(df[geo_col], fcfg["geography_exact_candidates"], ["ontario"]),
        "characteristic": _choose_exact_or_tokens(
            df[characteristic_col],
            fcfg["labour_force_characteristic_exact_candidates"],
            ["unemployment", "rate"],
        ),
        "data_type": _choose_exact_or_tokens(
            df[data_type_col], fcfg["data_type_exact_candidates"], ["seasonally", "adjusted"]
        ),
        "gender": _choose_exact_or_tokens(
            df[gender_col], fcfg["gender_exact_candidates"], ["total"]
        ),
        "age_group": _choose_exact_or_tokens(
            df[age_col], fcfg["age_group_exact_candidates"], ["15", "over"]
        ),
    }
    if statistics_col:
        labels["statistics"] = _choose_exact_or_tokens(
            df[statistics_col], fcfg.get("statistics_exact_candidates", ["Estimate"]), ["estimate"]
        )

    working = df.copy()
    working["ref_date"] = pd.to_datetime(working[date_col], errors="coerce")
    mask = (
        (working[geo_col].astype(str) == labels["geography"])
        & (working[characteristic_col].astype(str) == labels["characteristic"])
        & (working[data_type_col].astype(str) == labels["data_type"])
        & (working[gender_col].astype(str) == labels["gender"])
        & (working[age_col].astype(str) == labels["age_group"])
        & working["ref_date"].between(
            pd.Timestamp(cfg["project"]["start_date"]),
            pd.Timestamp(cfg["project"]["end_date"]),
        )
    )
    if statistics_col:
        mask &= working[statistics_col].astype(str) == labels["statistics"]
    working = working.loc[mask, ["ref_date", value_col]].copy()
    working["ontario_unemployment_rate"] = pd.to_numeric(working[value_col], errors="coerce")
    working = working[["ref_date", "ontario_unemployment_rate"]].drop_duplicates("ref_date")
    working = working.sort_values("ref_date")
    if working.empty:
        raise ValueError("Unemployment filters returned zero rows. Run source inspection and update config.")
    report = {
        "source_rows": int(source_rows if source_rows is not None else len(df)),
        "selected_rows": int(len(working)),
        "date_min": working["ref_date"].min(),
        "date_max": working["ref_date"].max(),
        "missing_values": int(working["ontario_unemployment_rate"].isna().sum()),
        "chosen_labels": labels,
    }
    return working, report


def clean_overnight_rate(
    cfg: dict[str, Any], root: Path | None = None, df: pd.DataFrame | None = None
) -> tuple[pd.DataFrame, dict[str, Any]]:
    base = root or project_root()
    series = cfg["sources"]["bank_of_canada"]["series"]
    if df is None:
        manifest = _load_manifest(base)
        path = _manifest_csv(manifest, "series", series, base)
        df = pd.read_csv(path)
    date_col = find_column(df, ["date", "Date"], ["date"])
    value_col = find_column(df, [series], [normalize_text(series)])
    working = df[[date_col, value_col]].copy()
    working["date"] = pd.to_datetime(working[date_col], errors="coerce")
    working["overnight_rate"] = pd.to_numeric(working[value_col], errors="coerce")
    working = working.dropna(subset=["date"]).sort_values("date")
    # Use the last observation in each calendar month, which reflects the end-of-month policy target.
    working["ref_date"] = working["date"].dt.to_period("M").dt.to_timestamp()
    monthly = working.groupby("ref_date", as_index=False).tail(1)
    monthly = monthly[["ref_date", "overnight_rate"]].sort_values("ref_date")
    report = {
        "source_rows": int(len(df)),
        "selected_months": int(len(monthly)),
        "date_min": monthly["ref_date"].min(),
        "date_max": monthly["ref_date"].max(),
        "aggregation": "last daily observation in each calendar month",
        "missing_values": int(monthly["overnight_rate"].isna().sum()),
    }
    return monthly, report


def clean_all(cfg: dict[str, Any], root: Path | None = None) -> dict[str, Path]:
    base = root or project_root()
    interim = base / "data" / "interim"
    interim.mkdir(parents=True, exist_ok=True)

    permits, permit_report = clean_building_permits(cfg, base)
    unemployment, unemployment_report = clean_unemployment(cfg, base)
    overnight, overnight_report = clean_overnight_rate(cfg, base)

    permit_path = interim / "building_permits_clean.csv"
    unemployment_path = interim / "ontario_unemployment_clean.csv"
    overnight_path = interim / "overnight_rate_clean.csv"
    permits.to_csv(permit_path, index=False)
    unemployment.to_csv(unemployment_path, index=False)
    overnight.to_csv(overnight_path, index=False)

    write_json(
        {
            "building_permits": permit_report,
            "unemployment": unemployment_report,
            "overnight_rate": overnight_report,
        },
        interim / "cleaning_audit.json",
    )
    return {
        "building_permits": permit_path,
        "unemployment": unemployment_path,
        "overnight_rate": overnight_path,
    }

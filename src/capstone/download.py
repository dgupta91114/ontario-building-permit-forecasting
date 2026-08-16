from __future__ import annotations

import csv
import io
import json
import shutil
import time
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import ensure_project_directories, project_root
from .utils import sha256_file, write_json

USER_AGENT = "QM640-Capstone/0.1 (academic reproducibility project)"


def _session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def download_file(url: str, destination: Path, timeout: int = 120) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_suffix(destination.suffix + ".part")
    with _session().get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with tmp.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
    tmp.replace(destination)
    return destination


def get_statcan_download_url(product_id: str, endpoint_template: str) -> str:
    endpoint = endpoint_template.format(product_id=product_id)
    response = _session().get(endpoint, timeout=60)
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") != "SUCCESS" or not payload.get("object"):
        raise RuntimeError(f"Statistics Canada WDS returned an unexpected response: {payload}")
    return str(payload["object"])


def extract_primary_csv(zip_path: Path, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        csv_members = [m for m in archive.infolist() if m.filename.lower().endswith(".csv")]
        if not csv_members:
            raise RuntimeError(f"No CSV file found in {zip_path}")
        # Full-table ZIPs include data and metadata. The data file is normally the largest CSV.
        primary = max(csv_members, key=lambda m: m.file_size)
        output = destination_dir / Path(primary.filename).name
        with archive.open(primary) as source, output.open("wb") as target:
            # Full Statistics Canada tables can expand to many gigabytes. Stream the
            # member rather than materializing the entire CSV in memory.
            shutil.copyfileobj(source, target, length=1024 * 1024)
    return output


def download_statcan_table(source_cfg: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    base = root or project_root()
    ensure_project_directories(base)
    product_id = str(source_cfg["product_id"])
    raw_dir = base / "data" / "raw" / product_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    zip_path = raw_dir / f"{product_id}-eng.zip"
    url = get_statcan_download_url(product_id, source_cfg["wds_endpoint"])
    download_file(url, zip_path)
    csv_path = extract_primary_csv(zip_path, raw_dir)
    return {
        "agency": "Statistics Canada",
        "product_id": product_id,
        "table_number": source_cfg.get("table_number"),
        "landing_page": source_cfg.get("landing_page"),
        "download_url": url,
        "zip_path": str(zip_path.relative_to(base)),
        "csv_path": str(csv_path.relative_to(base)),
        "sha256": sha256_file(zip_path),
        "downloaded_at_utc": pd.Timestamp.utcnow().isoformat(),
    }


def download_bank_of_canada_series(
    source_cfg: dict[str, Any], start_date: str, end_date: str, root: Path | None = None
) -> dict[str, Any]:
    base = root or project_root()
    ensure_project_directories(base)
    series = source_cfg["series"]
    endpoint = source_cfg["endpoint"].format(series=series)
    # The project configuration stores monthly dates as the first day of a month.
    # Expand the final month to its calendar end so the monthly end-of-period value is available.
    request_end_date = (pd.Timestamp(end_date) + pd.offsets.MonthEnd(0)).date().isoformat()
    response = _session().get(
        endpoint,
        params={"start_date": start_date, "end_date": request_end_date},
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    raw_dir = base / "data" / "raw" / "bank_of_canada"
    raw_dir.mkdir(parents=True, exist_ok=True)
    json_path = raw_dir / f"{series}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    records = []
    for observation in payload.get("observations", []):
        item = observation.get(series, {})
        records.append({"date": observation.get("d"), series: item.get("v")})
    frame = pd.DataFrame(records)
    if frame.empty:
        raise RuntimeError(f"No Bank of Canada observations returned for {series}")
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    frame[series] = pd.to_numeric(frame[series], errors="coerce")
    csv_path = raw_dir / f"{series}.csv"
    frame.to_csv(csv_path, index=False)
    return {
        "agency": "Bank of Canada",
        "series": series,
        "label": source_cfg.get("label"),
        "request_url": response.url,
        "json_path": str(json_path.relative_to(base)),
        "csv_path": str(csv_path.relative_to(base)),
        "sha256": sha256_file(json_path),
        "downloaded_at_utc": pd.Timestamp.utcnow().isoformat(),
    }


def download_all(cfg: dict[str, Any], root: Path | None = None) -> list[dict[str, Any]]:
    base = root or project_root()
    manifests = [
        download_statcan_table(cfg["sources"]["statcan_building_permits"], base),
        download_statcan_table(cfg["sources"]["statcan_unemployment"], base),
        download_bank_of_canada_series(
            cfg["sources"]["bank_of_canada"],
            cfg["project"]["start_date"],
            cfg["project"]["end_date"],
            base,
        ),
    ]
    output_path = base / "data" / "raw" / "download_manifest.json"
    write_json(manifests, output_path)
    return manifests

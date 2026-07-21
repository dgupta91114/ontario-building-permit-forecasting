from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


def normalize_text(value: Any) -> str:
    """Normalize labels for resilient matching without changing source files."""
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def find_column(df: pd.DataFrame, candidates: Iterable[str], required_tokens: Iterable[str] = ()) -> str:
    normalized = {normalize_text(c): c for c in df.columns}
    for candidate in candidates:
        key = normalize_text(candidate)
        if key in normalized:
            return normalized[key]
    tokens = [normalize_text(t) for t in required_tokens]
    matches = [
        original
        for norm, original in normalized.items()
        if all(token in norm for token in tokens)
    ]
    if len(matches) == 1:
        return matches[0]
    raise KeyError(
        f"Could not uniquely identify column. Candidates={list(candidates)}, "
        f"required_tokens={list(required_tokens)}, matches={matches}, "
        f"available={list(df.columns)}"
    )


def choose_dimension_label(
    series: pd.Series,
    exact_candidates: Iterable[str],
    required_tokens: Iterable[str] = (),
    forbidden_tokens: Iterable[str] = (),
) -> str:
    values = sorted({str(v).strip() for v in series.dropna().unique()})
    norm_to_original = {normalize_text(v): v for v in values}
    for candidate in exact_candidates:
        key = normalize_text(candidate)
        if key in norm_to_original:
            return norm_to_original[key]

    required = [normalize_text(t) for t in required_tokens]
    forbidden = [normalize_text(t) for t in forbidden_tokens]
    matches = []
    for value in values:
        norm = normalize_text(value)
        if all(token in norm for token in required) and not any(token in norm for token in forbidden):
            matches.append(value)

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        # Prefer the shortest total-level label. Fail if ambiguity remains.
        matches = sorted(matches, key=lambda x: (len(normalize_text(x).split()), len(x), x))
        first_score = (len(normalize_text(matches[0]).split()), len(matches[0]))
        tied = [m for m in matches if (len(normalize_text(m).split()), len(m)) == first_score]
        if len(tied) == 1:
            return matches[0]

    raise ValueError(
        "Could not choose one dimension label. "
        f"exact_candidates={list(exact_candidates)}, required={required}, "
        f"forbidden={forbidden}, matches={matches}. "
        "Run scripts/00_inspect_sources.py and update config/config.yaml."
    )


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(data: Any, path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, default=_json_default)


def _json_default(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value)!r} is not JSON serializable")

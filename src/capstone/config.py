from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path) if path else project_root() / "config" / "config.yaml"
    with config_path.open("r", encoding="utf-8") as handle:
        cfg = yaml.safe_load(handle)
    cfg["_config_path"] = str(config_path.resolve())
    return cfg


def ensure_project_directories(root: Path | None = None) -> None:
    base = root or project_root()
    for rel in [
        "data/raw",
        "data/interim",
        "data/processed",
        "data/demo",
        "outputs/figures",
        "outputs/tables",
        "outputs/models",
    ]:
        (base / rel).mkdir(parents=True, exist_ok=True)

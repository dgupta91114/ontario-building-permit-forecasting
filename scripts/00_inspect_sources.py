from pathlib import Path

from capstone.audit import inspect_sources
from capstone.config import load_config, project_root
from capstone.download import download_all


def main() -> None:
    root = project_root()
    cfg = load_config()
    if not (root / "data" / "raw" / "download_manifest.json").exists():
        print("Raw-data manifest not found; downloading official source tables first.")
        download_all(cfg, root)
    output = inspect_sources(cfg, root)
    print(f"Source label audit written to {output}")


if __name__ == "__main__":
    main()

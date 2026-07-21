from __future__ import annotations

import pandas as pd

from capstone.cleaning import clean_all
from capstone.config import ensure_project_directories, load_config, project_root
from capstone.download import download_all
from capstone.eda import run_rq1_eda
from capstone.explain import explain_selected_model
from capstone.features import build_dataset_from_interim
from capstone.reporting import generate_results_summary
from capstone.sample_size import save_sample_sizes
from capstone.training import train_and_evaluate


def main() -> None:
    root = project_root()
    cfg = load_config()
    ensure_project_directories(root)
    download_all(cfg, root)
    clean_all(cfg, root)
    dataset_path = build_dataset_from_interim(cfg, root)
    data = pd.read_csv(dataset_path, parse_dates=["ref_date", "target_date"])
    save_sample_sizes(root)
    run_rq1_eda(data, cfg, root)
    train_and_evaluate(data, cfg, root)
    explain_selected_model(data, cfg, root)
    summary = generate_results_summary(cfg, root)
    print(f"Pipeline completed. Review {summary}")


if __name__ == "__main__":
    main()

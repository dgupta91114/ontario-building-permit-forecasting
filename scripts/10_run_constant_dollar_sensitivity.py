from pathlib import Path

import pandas as pd

from capstone.cleaning import clean_building_permits
from capstone.config import load_config, project_root
from capstone.eda import run_rq1_eda
from capstone.explain import explain_selected_model
from capstone.features import build_features
from capstone.reporting import generate_results_summary
from capstone.sample_size import save_sample_sizes
from capstone.training import train_and_evaluate
from capstone.utils import write_json


def main() -> None:
    root = project_root()
    cfg = load_config()
    run_root = root / "outputs" / "sensitivity" / "constant_dollars"
    permits, permit_audit = clean_building_permits(cfg, root, value_basis="constant")
    unemployment = pd.read_csv(root / "data" / "interim" / "ontario_unemployment_clean.csv", parse_dates=["ref_date"])
    overnight = pd.read_csv(root / "data" / "interim" / "overnight_rate_clean.csv", parse_dates=["ref_date"])
    data, feature_audit = build_features(permits, unemployment, overnight, cfg)
    processed = run_root / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    data.to_csv(processed / "modeling_dataset.csv", index=False)
    write_json(feature_audit, processed / "feature_audit.json")
    write_json({"building_permits": permit_audit}, run_root / "data" / "cleaning_audit.json")
    save_sample_sizes(run_root)
    run_rq1_eda(data, cfg, run_root)
    train_and_evaluate(data, cfg, run_root)
    explain_selected_model(data, cfg, run_root)
    summary = generate_results_summary(cfg, run_root)
    print(f"Constant-dollar sensitivity completed: {summary}")


if __name__ == "__main__":
    main()

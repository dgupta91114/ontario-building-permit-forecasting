import pandas as pd

from capstone.config import load_config, project_root
from capstone.eda import run_rq1_eda


def main() -> None:
    root = project_root()
    cfg = load_config()
    path = root / "data" / "processed" / "modeling_dataset.csv"
    data = pd.read_csv(path, parse_dates=["ref_date", "target_date"])
    outputs = run_rq1_eda(data, cfg, root)
    for name, output in outputs.items():
        print(f"{name}: {output}")


if __name__ == "__main__":
    main()

import pandas as pd

from capstone.config import load_config, project_root
from capstone.training import train_and_evaluate


def main() -> None:
    root = project_root()
    cfg = load_config()
    data = pd.read_csv(
        root / "data" / "processed" / "modeling_dataset.csv",
        parse_dates=["ref_date", "target_date"],
    )
    result = train_and_evaluate(data, cfg, root)
    print(result["metrics"].to_string(index=False))
    print("Selection:", result["selection"])


if __name__ == "__main__":
    main()

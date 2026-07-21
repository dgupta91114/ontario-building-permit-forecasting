import pandas as pd

from capstone.config import load_config, project_root
from capstone.explain import explain_selected_model


def main() -> None:
    root = project_root()
    cfg = load_config()
    data = pd.read_csv(
        root / "data" / "processed" / "modeling_dataset.csv",
        parse_dates=["ref_date", "target_date"],
    )
    result = explain_selected_model(data, cfg, root)
    print(result)


if __name__ == "__main__":
    main()

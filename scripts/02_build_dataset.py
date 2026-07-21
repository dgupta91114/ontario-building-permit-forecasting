from capstone.cleaning import clean_all
from capstone.config import load_config, project_root
from capstone.features import build_dataset_from_interim


def main() -> None:
    root = project_root()
    cfg = load_config()
    clean_all(cfg, root)
    output = build_dataset_from_interim(cfg, root)
    print(f"Modeling dataset written to {output}")


if __name__ == "__main__":
    main()

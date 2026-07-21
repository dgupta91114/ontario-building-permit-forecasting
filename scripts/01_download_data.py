from capstone.config import load_config, project_root
from capstone.download import download_all


def main() -> None:
    cfg = load_config()
    manifests = download_all(cfg, project_root())
    for item in manifests:
        print(item)


if __name__ == "__main__":
    main()

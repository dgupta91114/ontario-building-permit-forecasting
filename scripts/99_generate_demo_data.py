from capstone.config import load_config
from capstone.demo import generate_synthetic_modeling_dataset


def main() -> None:
    output = generate_synthetic_modeling_dataset(load_config())
    print(f"Synthetic software-test dataset written to {output}")
    print("Do not use synthetic data for substantive capstone results.")


if __name__ == "__main__":
    main()

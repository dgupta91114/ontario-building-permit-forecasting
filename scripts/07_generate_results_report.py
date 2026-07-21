from capstone.config import load_config
from capstone.reporting import generate_results_summary


def main() -> None:
    output = generate_results_summary(load_config())
    print(f"Generated {output}")


if __name__ == "__main__":
    main()

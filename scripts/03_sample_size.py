from capstone.sample_size import calculate_sample_sizes, save_sample_sizes


def main() -> None:
    output = save_sample_sizes()
    print(calculate_sample_sizes().to_string(index=False))
    print(f"Saved to {output}")


if __name__ == "__main__":
    main()

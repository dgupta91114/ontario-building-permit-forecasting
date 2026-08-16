from capstone.diagnostics import generate_holdout_diagnostics, write_official_run_manifest


def main() -> None:
    for name, path in generate_holdout_diagnostics().items():
        print(f"{name}: {path}")
    print(f"manifest: {write_official_run_manifest()}")


if __name__ == "__main__":
    main()

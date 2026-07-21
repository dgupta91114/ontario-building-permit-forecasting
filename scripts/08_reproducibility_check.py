import json

from capstone.reproducibility import run_reproducibility_check


def main() -> None:
    report = run_reproducibility_check()
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

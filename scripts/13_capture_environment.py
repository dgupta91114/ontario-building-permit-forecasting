from importlib import metadata

from capstone.config import project_root


def main() -> None:
    packages = sorted(
        {f"{dist.metadata['Name']}=={dist.version}" for dist in metadata.distributions()},
        key=str.lower,
    )
    output = project_root() / "environment-lock.txt"
    output.write_text("\n".join(packages) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()

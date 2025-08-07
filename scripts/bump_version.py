# scripts/bump_version.py
import toml
import sys


def bump(version, level):
    major, minor, patch = map(int, version.split("."))
    if level == "major":
        return f"{major+1}.0.0"
    elif level == "minor":
        return f"{major}.{minor+1}.0"
    elif level == "patch":
        return f"{major}.{minor}.{patch+1}"
    else:
        return version


def main():
    level = sys.argv[1] if len(sys.argv) > 1 else "patch"
    data = toml.load("pyproject.toml")
    current_version = data["project"]["version"]
    new_version = bump(current_version, level)
    data["project"]["version"] = new_version
    with open("pyproject.toml", "w") as f:
        toml.dump(data, f)
    print(f"Bumped to {new_version}")


if __name__ == "__main__":
    main()
# This script bumps the version in pyproject.toml based on the provided level (major, minor, patch).
# Usage: python scripts/bump_version.py [level]
# If no level is provided, it defaults to "patch".
# Ensure you have the `toml` package installed to run this script.
# You can install it using pip:
# pip install toml

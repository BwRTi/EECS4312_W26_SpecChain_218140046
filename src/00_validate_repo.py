"""Validate that the repository contains the required folders and files."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]

REQUIRED_DIRECTORIES = [
    "data",
    "metrics",
    "personas",
    "prompts",
    "reflection",
    "spec",
    "src",
    "tests",
]

REQUIRED_FILES = [
    "README.md",
    "data/reviews_raw.jsonl",
    "data/reviews_clean.jsonl",
    "data/dataset_metadata.json",
    "data/review_groups_manual.json",
    "data/review_groups_auto.json",
    "data/review_groups_hybrid.json",
    "personas/personas_manual.json",
    "personas/personas_auto.json",
    "personas/personas_hybrid.json",
    "spec/spec_manual.md",
    "spec/spec_auto.md",
    "spec/spec_hybrid.md",
    "tests/tests_manual.json",
    "tests/tests_manual.feature",
    "tests/tests_auto.json",
    "tests/tests_hybrid.json",
    "metrics/metrics_manual.json",
    "metrics/metrics_auto.json",
    "metrics/metrics_hybrid.json",
    "metrics/metrics_summary.json",
    "src/run_all.py",
    "src/00_validate_repo.py",
]


def main() -> int:
    errors: list[str] = []

    print("Checking repository structure...")

    for relative_path in REQUIRED_DIRECTORIES:
        path = ROOT_DIR / relative_path
        if path.is_dir():
            print(f"{relative_path} found")
        else:
            errors.append(f"Missing required directory: {relative_path}")

    for relative_path in REQUIRED_FILES:
        path = ROOT_DIR / relative_path
        if path.is_file():
            print(f"{relative_path} found")
        else:
            errors.append(f"Missing required file: {relative_path}")

    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository validation complete")
    print(f"Repository root: {ROOT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

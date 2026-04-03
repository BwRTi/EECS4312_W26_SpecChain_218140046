"""Run the automated pipeline from raw data to metrics."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
DATA_DIR = ROOT_DIR / "data"
METRICS_DIR = ROOT_DIR / "metrics"

VALIDATE_SCRIPT = SRC_DIR / "00_validate_repo.py"
COLLECT_SCRIPT = SRC_DIR / "01_collect_or_import.py"
CLEAN_SCRIPT = SRC_DIR / "02_clean.py"
AUTO_PERSONAS_SCRIPT = SRC_DIR / "05_personas_auto.py"
AUTO_SPEC_SCRIPT = SRC_DIR / "06_spec_generate.py"
AUTO_TESTS_SCRIPT = SRC_DIR / "07_tests_generate.py"
METRICS_SCRIPT = SRC_DIR / "08_metrics.py"

RAW_DATASET = DATA_DIR / "reviews_raw.jsonl"
CLEAN_DATASET = DATA_DIR / "reviews_clean.jsonl"
METRICS_SUMMARY = METRICS_DIR / "metrics_summary.json"


def run_script(script_path: Path, *args: str) -> None:
    command = [sys.executable, str(script_path), *args]
    subprocess.run(command, check=True, cwd=str(ROOT_DIR))


def count_jsonl_rows(path: Path) -> int:
    if not path.is_file():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_metrics_summary() -> dict[str, Any]:
    summary: dict[str, Any] = {
        "raw_reviews": count_jsonl_rows(RAW_DATASET),
        "clean_reviews": count_jsonl_rows(CLEAN_DATASET),
    }

    for pipeline_name in ["manual", "hybrid", "auto"]:
        metrics_path = METRICS_DIR / f"metrics_{pipeline_name}.json"
        metrics = load_json_if_exists(metrics_path)
        if metrics is not None:
            summary[pipeline_name] = metrics

    with METRICS_SUMMARY.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the repository pipeline. By default, existing raw reviews are reused."
    )
    parser.add_argument(
        "--collect",
        action="store_true",
        help="Fetch raw reviews even if data/reviews_raw.jsonl already exists.",
    )
    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="Skip the cleaning step even if raw data exists.",
    )
    parser.add_argument(
        "--skip-auto",
        action="store_true",
        help="Skip the automated review grouping, persona, spec, test, and metrics generation steps.",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip repository validation before and after the run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.skip_validate:
        print("Running initial repository validation...")
        run_script(VALIDATE_SCRIPT)

    # Step 1: Create or reuse the raw dataset in data/reviews_raw.jsonl.
    should_collect = args.collect or not RAW_DATASET.is_file() or count_jsonl_rows(RAW_DATASET) == 0
    if should_collect:
        print("Collecting raw reviews...")
        run_script(COLLECT_SCRIPT)
    else:
        print("Skipping review collection because an existing raw dataset was found.")
        print("Use --collect if you want to fetch reviews again.")

    # Step 2: Clean the raw reviews and produce data/reviews_clean.jsonl.
    if args.skip_clean:
        print("Skipping cleaning step by request.")
    else:
        if not RAW_DATASET.is_file() or count_jsonl_rows(RAW_DATASET) == 0:
            print("Skipping cleaning because no raw dataset is available.")
        else:
            print("Cleaning raw reviews...")
            run_script(CLEAN_SCRIPT)

    # Step 3: Generate the automated review groups and personas from the clean dataset.
    # Output files:
    # - data/review_groups_auto.json
    # - personas/personas_auto.json
    # - prompts/prompt_auto.json
    #
    # Step 4: Generate the automated specification.
    # Output file:
    # - spec/spec_auto.md
    #
    # Step 5: Generate validation tests for the automated specification.
    # Output file:
    # - tests/tests_auto.json
    #
    # Step 6: Compute automated metrics.
    # Output file:
    # - metrics/metrics_auto.json
    if args.skip_auto:
        print("Skipping automated generation steps by request.")
    else:
        if not CLEAN_DATASET.is_file() or count_jsonl_rows(CLEAN_DATASET) == 0:
            print("Skipping automated generation because no cleaned dataset is available.")
        else:
            print("Generating automated review groups and personas...")
            run_script(AUTO_PERSONAS_SCRIPT)
            print("Generating automated specification...")
            run_script(AUTO_SPEC_SCRIPT)
            print("Generating automated validation tests...")
            run_script(AUTO_TESTS_SCRIPT)
            print("Computing automated metrics...")
            run_script(METRICS_SCRIPT, "--pipeline", "automated")

    # Step 7: Build or refresh the cross-pipeline summary for comparison.
    # Output file:
    # - metrics/metrics_summary.json
    summary = build_metrics_summary()
    print(f"Updated metrics summary: {METRICS_SUMMARY}")
    print(
        f"Current dataset sizes -> raw: {summary.get('raw_reviews', 0)}, "
        f"clean: {summary.get('clean_reviews', 0)}"
    )

    if not args.skip_validate:
        print("Running final repository validation...")
        run_script(VALIDATE_SCRIPT)

    print("Pipeline run completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

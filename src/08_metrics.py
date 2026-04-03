"""Compute metrics for manual, automated, or hybrid pipeline artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
REVIEWS_PATH = ROOT_DIR / "data" / "reviews_clean.jsonl"

AMBIGUOUS_TERMS = {
    "affordable",
    "clear",
    "contextual",
    "fast",
    "flexible",
    "guidance",
    "easy",
    "better",
    "user-friendly",
    "user friendly",
    "intuitive",
    "good",
    "human-like",
    "human like",
    "natural",
    "appropriate",
    "helpful",
    "reasonable",
    "seamless",
    "smooth",
    "support",
    "quick",
    "visible",
}

PIPELINE_PATHS = {
    "manual": {
        "groups": ROOT_DIR / "data" / "review_groups_manual.json",
        "personas": ROOT_DIR / "personas" / "personas_manual.json",
        "spec": ROOT_DIR / "spec" / "spec_manual.md",
        "tests": ROOT_DIR / "tests" / "tests_manual.json",
        "output": ROOT_DIR / "metrics" / "metrics_manual.json",
        "requirement_pattern": r"FR\d+",
    },
    "automated": {
        "groups": ROOT_DIR / "data" / "review_groups_auto.json",
        "personas": ROOT_DIR / "personas" / "personas_auto.json",
        "spec": ROOT_DIR / "spec" / "spec_auto.md",
        "tests": ROOT_DIR / "tests" / "tests_auto.json",
        "output": ROOT_DIR / "metrics" / "metrics_auto.json",
        "requirement_pattern": r"FR_auto_\d+",
    },
    "hybrid": {
        "groups": ROOT_DIR / "data" / "review_groups_hybrid.json",
        "personas": ROOT_DIR / "personas" / "personas_hybrid.json",
        "spec": ROOT_DIR / "spec" / "spec_hybrid.md",
        "tests": ROOT_DIR / "tests" / "tests_hybrid.json",
        "output": ROOT_DIR / "metrics" / "metrics_hybrid.json",
        "requirement_pattern": r"FR_hybrid_\d+",
    },
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_requirements(spec_text: str, requirement_pattern: str) -> list[dict[str, str]]:
    pattern = re.compile(
        rf"# Requirement ID: (?P<requirement_id>{requirement_pattern})\n+"
        r"- Description: (?P<description>.+?)\n"
        r"- Source Persona: (?P<source_persona>.+?)\n"
        r"- Traceability: (?P<traceability>.+?)\n"
        r"- Acceptance Criteria: (?P<acceptance_criteria>.+?)"
        r"(?:\n- Notes: (?P<notes>.+?))?(?=\n# Requirement ID: |\Z)",
        flags=re.DOTALL,
    )
    requirements: list[dict[str, str]] = []
    for match in pattern.finditer(spec_text):
        requirements.append(
            {
                key: value.strip() if isinstance(value, str) else ""
                for key, value in match.groupdict().items()
            }
        )
    return requirements


def ambiguity_ratio(requirements: list[dict[str, str]]) -> float:
    ambiguous_count = 0
    for requirement in requirements:
        text = f"{requirement['description']} {requirement['acceptance_criteria']}".lower()
        if any(term in text for term in AMBIGUOUS_TERMS):
            ambiguous_count += 1
    return round(ambiguous_count / len(requirements), 4) if requirements else 0.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute repository metrics for one pipeline.")
    parser.add_argument(
        "--pipeline",
        choices=sorted(PIPELINE_PATHS.keys()),
        default="automated",
        help="Pipeline whose artifacts should be measured.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = PIPELINE_PATHS[args.pipeline]

    reviews = load_jsonl(REVIEWS_PATH)
    groups = load_json(paths["groups"])["groups"]
    personas = load_json(paths["personas"])["personas"]
    spec_text = paths["spec"].read_text(encoding="utf-8")
    requirements = parse_requirements(spec_text, paths["requirement_pattern"])
    tests = load_json(paths["tests"])["tests"]

    covered_review_ids = {review_id for group in groups for review_id in group["review_ids"]}
    requirement_ids = {requirement["requirement_id"] for requirement in requirements}
    tested_requirement_ids = {test["requirement_id"] for test in tests}

    persona_group_links = len(personas)
    requirement_persona_links = sum(1 for requirement in requirements if requirement["source_persona"].strip())
    requirement_trace_links = sum(1 for requirement in requirements if "review group" in requirement["traceability"].lower())
    test_requirement_links = len(tests)
    group_review_links = sum(len(group["review_ids"]) for group in groups)

    metrics = {
        "pipeline": args.pipeline,
        "dataset_size": len(reviews),
        "persona_count": len(personas),
        "requirements_count": len(requirements),
        "tests_count": len(tests),
        "traceability_links": group_review_links + persona_group_links + requirement_persona_links + requirement_trace_links + test_requirement_links,
        "review_coverage_ratio": round(len(covered_review_ids) / len(reviews), 4) if reviews else 0.0,
        "traceability_ratio": round(requirement_trace_links / len(requirements), 4) if requirements else 0.0,
        "testability_rate": round(len(requirement_ids & tested_requirement_ids) / len(requirement_ids), 4) if requirement_ids else 0.0,
        "ambiguity_ratio": ambiguity_ratio(requirements),
    }

    output_path = paths["output"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2, ensure_ascii=False)

    print(f"Wrote {args.pipeline} pipeline metrics to '{output_path}'.")


if __name__ == "__main__":
    main()

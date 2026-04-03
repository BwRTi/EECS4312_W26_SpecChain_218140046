"""Generate validation tests from automated specifications."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT_DIR / "spec" / "spec_auto.md"
TESTS_OUTPUT_PATH = ROOT_DIR / "tests" / "tests_auto.json"


def parse_requirements(spec_text: str) -> list[dict[str, str]]:
    pattern = re.compile(
        r"# Requirement ID: (?P<requirement_id>FR_auto_\d+)\n+"
        r"- Description: (?P<description>.+?)\n"
        r"- Source Persona: (?P<source_persona>.+?)\n"
        r"- Traceability: (?P<traceability>.+?)\n"
        r"- Acceptance Criteria: (?P<acceptance_criteria>.+?)(?=\n# Requirement ID: |\Z)",
        flags=re.DOTALL,
    )
    requirements: list[dict[str, str]] = []
    for match in pattern.finditer(spec_text):
        requirements.append({key: value.strip() for key, value in match.groupdict().items()})
    return requirements


def build_test_variants(requirement: dict[str, str], index: int) -> list[dict[str, Any]]:
    description = requirement["description"]
    acceptance = requirement["acceptance_criteria"]
    scenario = description.replace("The system shall ", "").rstrip(".")
    base_scenario = scenario[:1].upper() + scenario[1:]

    positive_steps = [
        "Open the relevant screen or feature for this requirement",
        "Perform the primary user action described by the requirement",
        "Observe the system response and compare it against the acceptance criteria",
    ]
    boundary_steps = [
        "Open the same feature in a realistic follow-up or repeat-use situation",
        "Perform the requirement-related action again while preserving the same flow",
        "Verify that the system still satisfies the stated acceptance criteria",
    ]

    return [
        {
            "test_id": f"T_auto_{index}_a",
            "requirement_id": requirement["requirement_id"],
            "scenario": f"{base_scenario} in the primary flow",
            "steps": positive_steps,
            "expected_result": acceptance,
        },
        {
            "test_id": f"T_auto_{index}_b",
            "requirement_id": requirement["requirement_id"],
            "scenario": f"{base_scenario} in a repeat or follow-up flow",
            "steps": boundary_steps,
            "expected_result": acceptance,
        },
    ]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def main() -> None:
    spec_text = SPEC_PATH.read_text(encoding="utf-8")
    requirements = parse_requirements(spec_text)
    tests: list[dict[str, Any]] = []
    for index, requirement in enumerate(requirements, start=1):
        tests.extend(build_test_variants(requirement, index))
    write_json(TESTS_OUTPUT_PATH, {"tests": tests})
    print(f"Wrote {len(tests)} automated validation tests to '{TESTS_OUTPUT_PATH}'.")


if __name__ == "__main__":
    main()

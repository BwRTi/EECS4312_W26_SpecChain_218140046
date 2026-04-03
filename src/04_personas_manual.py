"""Create manual persona draft scaffolds from manual review groups.

This script supports the manual pipeline by turning grouped reviews into a
persona draft template. The output is intentionally incomplete and is meant to
be refined by a human reviewer rather than treated as a final persona file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
GROUPS_PATH = ROOT_DIR / "data" / "review_groups_manual.json"
OUTPUT_PATH = ROOT_DIR / "personas" / "personas_manual_draft.json"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_persona_draft(group: dict[str, Any], index: int) -> dict[str, Any]:
    evidence = group.get("review_ids", [])[:3]
    theme = group.get("theme", f"Manual group {index}")
    return {
        "id": f"PM_DRAFT_{index}",
        "name": f"Draft persona for {theme}",
        "description": "",
        "derived_from_group": group.get("group_id", f"M{index}"),
        "goals": [],
        "pain_points": [],
        "context": [],
        "constraints": [],
        "evidence_reviews": evidence,
        "editor_notes": "Fill this draft manually based on the full review group.",
    }


def main() -> None:
    groups_payload = load_json(GROUPS_PATH)
    groups = groups_payload.get("groups", [])
    drafts = [build_persona_draft(group, index) for index, group in enumerate(groups, start=1)]
    payload = {
        "purpose": "Manual persona drafting scaffold generated from manual review groups.",
        "personas": drafts,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote manual persona draft template to '{OUTPUT_PATH}'.")


if __name__ == "__main__":
    main()

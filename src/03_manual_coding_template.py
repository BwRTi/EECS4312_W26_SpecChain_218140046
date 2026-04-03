"""Create a lightweight manual coding template from the cleaned review dataset.

This helper script is intended for the manual pipeline. It does not replace
manual judgment; instead, it prepares a small structured template that can be
filled in while reading reviews and identifying feedback themes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT_DIR / "data" / "reviews_clean.jsonl"
OUTPUT_PATH = ROOT_DIR / "data" / "manual_coding_template.json"

DEFAULT_TEMPLATE_ROWS = 30


def load_reviews(path: Path) -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                reviews.append(json.loads(line))
    return reviews


def build_template_rows(reviews: list[dict[str, Any]], row_count: int = DEFAULT_TEMPLATE_ROWS) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for review in reviews[:row_count]:
        rows.append(
            {
                "review_id": review["id"],
                "review_text": review["content"],
                "proposed_group": "",
                "theme_notes": "",
                "persona_notes": "",
            }
        )
    return rows


def main() -> None:
    reviews = load_reviews(INPUT_PATH)
    payload = {
        "purpose": "Manual coding support template for grouping reviews before persona construction.",
        "instructions": [
            "Read each review and assign it to a candidate manual group.",
            "Write short theme notes that justify the grouping decision.",
            "Add persona notes only when the review suggests a recurring user need or context.",
        ],
        "rows": build_template_rows(reviews),
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote manual coding template to '{OUTPUT_PATH}'.")


if __name__ == "__main__":
    main()

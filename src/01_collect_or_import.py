"""Collect raw Google Play reviews and write them to JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_APP_ID = "bot.touchkin"
DEFAULT_REVIEW_COUNT = 1500
DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "reviews_raw.jsonl"


class GooglePlayReviewCollector:
    """Fetch reviews from Google Play and persist them as JSONL."""

    def __init__(self, app_id: str, output_path: Path, review_count: int = DEFAULT_REVIEW_COUNT) -> None:
        self.app_id = app_id
        self.output_path = output_path
        self.review_count = review_count

    def fetch_reviews(self) -> list[dict[str, Any]]:
        try:
            from google_play_scraper import Sort, reviews
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency 'google-play-scraper'. "
                "Create a Python 3.10 virtual environment and install it with "
                "`python -m pip install google-play-scraper`."
            ) from exc

        collected: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        continuation_token: str | None = None

        while len(collected) < self.review_count:
            batch_size = min(200, self.review_count - len(collected))
            batch, continuation_token = reviews(
                self.app_id,
                lang="en",
                country="ca",
                sort=Sort.NEWEST,
                count=batch_size,
                continuation_token=continuation_token,
            )

            if not batch:
                break

            for review in batch:
                review_id = str(review.get("reviewId", "")).strip()
                if not review_id or review_id in seen_ids:
                    continue

                collected.append(
                    {
                        "id": review_id,
                        "content": str(review.get("content", "")),
                        "score": int(review.get("score", 0)),
                    }
                )
                seen_ids.add(review_id)

                if len(collected) >= self.review_count:
                    break

            if continuation_token is None:
                break

        return collected

    def fetch_app_details(self) -> dict[str, Any]:
        try:
            from google_play_scraper import app
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency 'google-play-scraper'. "
                "Create a Python 3.10 virtual environment and install it with "
                "`python -m pip install google-play-scraper`."
            ) from exc

        try:
            details = app(self.app_id, lang="en", country="ca")
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch Google Play app details for '{self.app_id}'.") from exc

        if not details:
            raise RuntimeError(f"No app details returned for '{self.app_id}'.")

        return details

    def write_reviews(self, reviews_data: list[dict[str, Any]]) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8") as handle:
            for review in reviews_data:
                handle.write(json.dumps(review, ensure_ascii=False) + "\n")

    def run(self) -> list[dict[str, Any]]:
        app_details = self.fetch_app_details()
        print(
            "Confirmed target app: "
            f"{app_details.get('title', 'Unknown Title')} "
            f"by {app_details.get('developer', 'Unknown Developer')} "
            f"(app id: {self.app_id})"
        )
        reviews_data = self.fetch_reviews()
        self.write_reviews(reviews_data)
        return reviews_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect Google Play reviews into JSONL.")
    parser.add_argument("--app-id", default=DEFAULT_APP_ID, help="Google Play app id to fetch.")
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_REVIEW_COUNT,
        help="Number of reviews to fetch.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to the output JSONL file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collector = GooglePlayReviewCollector(
        app_id=args.app_id,
        output_path=args.output,
        review_count=args.count,
    )
    reviews_data = collector.run()
    print(
        f"Wrote {len(reviews_data)} reviews for '{args.app_id}' "
        f"to '{args.output}'."
    )


if __name__ == "__main__":
    main()

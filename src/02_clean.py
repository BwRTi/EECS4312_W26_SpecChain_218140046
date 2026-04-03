"""Clean raw review data and write a normalized JSONL dataset."""

from __future__ import annotations

import argparse
import json
import re
import string
import unicodedata
from pathlib import Path
from typing import Any


DEFAULT_INPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "reviews_raw.jsonl"
DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "reviews_clean.jsonl"
DEFAULT_MIN_WORD_COUNT = 3

DEFAULT_STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "as", "at", "be", "because", "been", "before", "being", "below",
    "between", "both", "but", "by", "can", "could", "did", "do", "does", "doing",
    "down", "during", "each", "few", "for", "from", "further", "had", "has", "have",
    "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how",
    "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more",
    "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once",
    "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s",
    "same", "she", "should", "so", "some", "such", "t", "than", "that", "the",
    "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "we",
    "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will",
    "with", "you", "your", "yours", "yourself", "yourselves",
}


def number_to_words(value: int) -> str:
    """Convert a non-negative integer to English words."""
    if value < 0:
        return f"minus {number_to_words(abs(value))}"
    if value == 0:
        return "zero"

    ones = [
        "", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
        "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
        "seventeen", "eighteen", "nineteen",
    ]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

    def under_thousand(num: int) -> str:
        parts: list[str] = []
        hundreds, remainder = divmod(num, 100)
        if hundreds:
            parts.extend([ones[hundreds], "hundred"])
        if remainder >= 20:
            ten_value, one_value = divmod(remainder, 10)
            parts.append(tens[ten_value])
            if one_value:
                parts.append(ones[one_value])
        elif remainder:
            parts.append(ones[remainder])
        return " ".join(part for part in parts if part)

    chunks: list[str] = []
    scales = ["", "thousand", "million", "billion"]
    scale_index = 0
    current = value

    while current > 0:
        current, remainder = divmod(current, 1000)
        if remainder:
            words = under_thousand(remainder)
            scale = scales[scale_index]
            chunks.append(f"{words} {scale}".strip())
        scale_index += 1

    return " ".join(reversed(chunks)).strip()


class ReviewCleaner:
    """Normalize raw reviews into a cleaned JSONL dataset."""

    def __init__(self, input_path: Path, output_path: Path, min_word_count: int = DEFAULT_MIN_WORD_COUNT) -> None:
        self.input_path = input_path
        self.output_path = output_path
        self.min_word_count = min_word_count
        self._lemmatizer = self._build_lemmatizer()

    def _build_lemmatizer(self) -> Any:
        try:
            import nltk
            from nltk.stem import WordNetLemmatizer
            from nltk.corpus import wordnet
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency 'nltk'. Install it in the Python 3.10 virtual environment with "
                "`python -m pip install nltk`."
            ) from exc

        resources = [
            ("corpora/wordnet", "wordnet"),
            ("corpora/omw-1.4", "omw-1.4"),
        ]
        for resource_path, resource_name in resources:
            try:
                nltk.data.find(resource_path)
            except LookupError:
                nltk.download(resource_name, quiet=True)

        # Accessing the corpus here ensures download failures surface early.
        _ = wordnet.synsets("review")
        return WordNetLemmatizer()

    def load_reviews(self) -> list[dict[str, Any]]:
        reviews: list[dict[str, Any]] = []
        with self.input_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                reviews.append(json.loads(line))
        return reviews

    def _convert_numbers(self, text: str) -> str:
        def repl(match: re.Match[str]) -> str:
            return f" {number_to_words(int(match.group()))} "

        return re.sub(r"\d+", repl, text)

    def _strip_symbols_and_emojis(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        without_marks = "".join(char for char in normalized if not unicodedata.combining(char))
        filtered = []
        for char in without_marks:
            category = unicodedata.category(char)
            if category.startswith(("S", "C")):
                filtered.append(" ")
            else:
                filtered.append(char)
        return "".join(filtered)

    def _remove_punctuation(self, text: str) -> str:
        translation_table = str.maketrans({punct: " " for punct in string.punctuation})
        return text.translate(translation_table)

    def _lemmatize_tokens(self, tokens: list[str]) -> list[str]:
        return [self._lemmatizer.lemmatize(token) for token in tokens]

    def clean_text(self, text: str) -> str:
        text = text.strip()
        if not text:
            return ""

        text = self._convert_numbers(text)
        text = self._strip_symbols_and_emojis(text)
        text = self._remove_punctuation(text)
        text = text.lower()
        text = re.sub(r"[^a-z\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return ""

        tokens = [token for token in text.split() if token not in DEFAULT_STOP_WORDS]
        tokens = self._lemmatize_tokens(tokens)
        tokens = [token for token in tokens if token]
        return " ".join(tokens).strip()

    def clean_reviews(self, raw_reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen_ids: set[str] = set()
        seen_contents: set[str] = set()
        cleaned_reviews: list[dict[str, Any]] = []

        for review in raw_reviews:
            review_id = str(review.get("id", "")).strip()
            content = str(review.get("content", "")).strip()
            score = int(review.get("score", 0))

            if not review_id or review_id in seen_ids:
                continue
            if not content:
                continue

            cleaned_content = self.clean_text(content)
            if not cleaned_content:
                continue
            if len(cleaned_content.split()) < self.min_word_count:
                continue
            if cleaned_content in seen_contents:
                continue

            cleaned_reviews.append(
                {
                    "id": review_id,
                    "content": cleaned_content,
                    "score": score,
                }
            )
            seen_ids.add(review_id)
            seen_contents.add(cleaned_content)

        return cleaned_reviews

    def write_reviews(self, cleaned_reviews: list[dict[str, Any]]) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8") as handle:
            for review in cleaned_reviews:
                handle.write(json.dumps(review, ensure_ascii=False) + "\n")

    def run(self) -> list[dict[str, Any]]:
        raw_reviews = self.load_reviews()
        cleaned_reviews = self.clean_reviews(raw_reviews)
        self.write_reviews(cleaned_reviews)
        return cleaned_reviews


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean Google Play reviews into JSONL.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH, help="Path to the raw JSONL file.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Path to the cleaned JSONL file.")
    parser.add_argument(
        "--min-word-count",
        type=int,
        default=DEFAULT_MIN_WORD_COUNT,
        help="Minimum number of cleaned tokens required to keep a review.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cleaner = ReviewCleaner(
        input_path=args.input,
        output_path=args.output,
        min_word_count=args.min_word_count,
    )
    cleaned_reviews = cleaner.run()
    print(f"Wrote {len(cleaned_reviews)} cleaned reviews to '{args.output}'.")


if __name__ == "__main__":
    main()

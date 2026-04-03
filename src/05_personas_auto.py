"""Automated review grouping and persona generation pipeline."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


GROQ_API_KEY = ""
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT_DIR / "data" / "reviews_clean.jsonl"
GROUPS_OUTPUT_PATH = ROOT_DIR / "data" / "review_groups_auto.json"
PERSONAS_OUTPUT_PATH = ROOT_DIR / "personas" / "personas_auto.json"
PROMPT_OUTPUT_PATH = ROOT_DIR / "prompts" / "prompt_auto.json"


AUTO_GROUP_CONFIG = [
    {
        "group_id": "A1",
        "theme": "Users seeking emotional support and a safe space to talk through stress, anxiety, or loneliness",
        "keywords": {"support", "talk", "someone", "listen", "companion", "understood", "advice", "emotion"},
        "example_reviews": [
            "helpful app talk support",
            "need companion help deal emotion daily highly recommend app",
        ],
    },
    {
        "group_id": "A2",
        "theme": "Users relying on self-help exercises such as CBT prompts, breathing, journaling, and mindfulness tools",
        "keywords": {"exercise", "meditation", "breathing", "tool", "grounding", "technique", "mindfulness", "journal"},
        "example_reviews": [
            "love utilizes cbt technique help break negative thought cycle",
            "good really liked mindful breathing relaxation tool helped helpful",
        ],
    },
    {
        "group_id": "A3",
        "theme": "Users frustrated by robotic, repetitive, or low-context AI conversations",
        "keywords": {"robot", "chat", "bot", "repeating", "generic", "loop", "scripted", "understand"},
        "example_reviews": [
            "ai chat doesnt give useful insight keep repeating thing",
            "feel like chatting customer support bot designed five year ago",
        ],
    },
    {
        "group_id": "A4",
        "theme": "Users sensitive to pricing, subscription friction, and free-tier limitations",
        "keywords": {"free", "pay", "paid", "subscription", "premium", "cost", "expensive", "paywall"},
        "example_reviews": [
            "install app searching something free paid",
            "subscription expensive end day paid therapist ai pet something",
        ],
    },
    {
        "group_id": "A5",
        "theme": "Users affected by slow performance, errors, lost chat history, or unstable flows",
        "keywords": {"slow", "load", "glitch", "stuck", "forgot", "erasing", "working", "wrong", "polish", "unoptimized"},
        "example_reviews": [
            "kept glitching saying check erasing long conversation",
            "take long load message",
        ],
    },
]


def load_reviews(path: Path) -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                reviews.append(json.loads(line))
    return reviews


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def get_groq_api_key() -> str:
    return GROQ_API_KEY.strip() or os.getenv("GROQ_API_KEY", "").strip()


def call_groq(messages: list[dict[str, str]]) -> str:
    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError("Groq API key is not configured.")

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.3,
    }
    request = urllib.request.Request(
        url="https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "EECS4312-SpecChain/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Groq API request failed: {exc.code} {details}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Groq API request failed: {exc.reason}") from exc

    return body["choices"][0]["message"]["content"]


def score_review(content: str, keywords: set[str]) -> int:
    tokens = set(content.split())
    return sum(1 for keyword in keywords if keyword in tokens)


def build_groups(reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    assigned_ids: set[str] = set()
    groups: list[dict[str, Any]] = []

    for config in AUTO_GROUP_CONFIG:
        scored_reviews: list[tuple[int, dict[str, Any]]] = []
        for review in reviews:
            if review["id"] in assigned_ids:
                continue
            score = score_review(review["content"], config["keywords"])
            if score > 0:
                scored_reviews.append((score, review))

        scored_reviews.sort(key=lambda item: (-item[0], item[1]["score"], item[1]["id"]))
        selected = [review for _, review in scored_reviews[:12]]

        for review in selected:
            assigned_ids.add(review["id"])

        groups.append(
            {
                "group_id": config["group_id"],
                "theme": config["theme"],
                "review_ids": [review["id"] for review in selected],
                "example_reviews": [review["content"] for review in selected[:2]] or config["example_reviews"],
            }
        )

    return groups


def build_prompt_payload(groups: list[dict[str, Any]], reviews_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    grouped_reviews = []
    for group in groups:
        grouped_reviews.append(
            {
                "group_id": group["group_id"],
                "theme": group["theme"],
                "reviews": [
                    {"id": review_id, "content": reviews_by_id[review_id]["content"], "score": reviews_by_id[review_id]["score"]}
                    for review_id in group["review_ids"][:8]
                ],
            }
        )

    system_prompt = (
        "You are generating structured software-engineering personas from clustered app reviews. "
        "Return valid JSON only."
    )
    user_prompt = (
        "Using the grouped reviews below, generate one persona per group. "
        "For each persona include: id, name, description, derived_from_group, goals, pain_points, "
        "context, constraints, and evidence_reviews. Keep the result grounded in the supplied reviews.\n\n"
        f"{json.dumps({'groups': grouped_reviews}, ensure_ascii=False, indent=2)}"
    )
    return {
        "provider": "Groq",
        "model": GROQ_MODEL,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "group_count": len(groups),
    }


def heuristic_personas(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    persona_templates = {
        "A1": {
            "id": "PA1",
            "name": "Always-On Emotional Support Seeker",
            "description": "A user who needs a safe, available, and non-judgmental place to talk through difficult emotions.",
            "goals": ["Talk through stress in the moment", "Feel listened to without judgment"],
            "pain_points": ["Does not always have a trusted person available", "Needs emotional validation during vulnerable moments"],
            "context": ["Uses the app during stress or loneliness", "Often opens the app outside normal therapy hours"],
            "constraints": ["Support responses must feel emotionally safe", "The entry point to support should be immediate"],
        },
        "A2": {
            "id": "PA2",
            "name": "Structured Self-Help Routine Builder",
            "description": "A user who values practical exercises like breathing, journaling, and reframing over open-ended chat alone.",
            "goals": ["Access coping exercises quickly", "Build repeatable daily self-help habits"],
            "pain_points": ["Gets frustrated when useful tools are hidden", "Needs specific actions instead of vague encouragement"],
            "context": ["Uses the app for daily regulation", "Returns for guided exercises and tool-based support"],
            "constraints": ["Exercises should be easy to start", "Instructions should be concrete and actionable"],
        },
        "A3": {
            "id": "PA3",
            "name": "Conversation Quality Evaluator",
            "description": "A user who expects the AI to understand context and avoid robotic, repetitive, or generic replies.",
            "goals": ["Receive relevant responses", "Maintain a coherent conversation across turns"],
            "pain_points": ["Responses feel scripted or repetitive", "The AI misses important details from prior messages"],
            "context": ["Uses the app as a conversational support tool", "Compares the experience to modern chat systems"],
            "constraints": ["Replies must stay context-aware", "The chat should not reset unnecessarily"],
        },
        "A4": {
            "id": "PA4",
            "name": "Budget-Conscious Support User",
            "description": "A user who needs clarity about what is free, what is paid, and whether the product is worth the subscription cost.",
            "goals": ["Understand pricing before committing", "Use meaningful free-tier support if possible"],
            "pain_points": ["Feels misled by paywalls or upgrade prompts", "Sees subscriptions as expensive relative to value"],
            "context": ["Often compares multiple support apps", "May already be under financial pressure"],
            "constraints": ["Pricing must be transparent", "Upgrade prompts should not interrupt core free-tier use"],
        },
        "A5": {
            "id": "PA5",
            "name": "Reliability-Dependent Distressed User",
            "description": "A user who needs the app to load quickly, preserve context, and remain stable during emotionally difficult moments.",
            "goals": ["Use the app without technical friction", "Trust the app to preserve conversation state"],
            "pain_points": ["Sees slow loading or glitches as additional stress", "Loses trust when chats or drafts disappear"],
            "context": ["Often opens the app while already upset", "May be on a slower device or unstable connection"],
            "constraints": ["Core screens must stay responsive", "Conversation state should survive interruptions"],
        },
    }

    personas: list[dict[str, Any]] = []
    for group in groups:
        template = persona_templates[group["group_id"]]
        personas.append(
            {
                **template,
                "derived_from_group": group["group_id"],
                "evidence_reviews": group["review_ids"][:3],
            }
        )
    return personas


def generate_personas_with_groq(prompt_payload: dict[str, Any]) -> list[dict[str, Any]]:
    messages = [
        {"role": "system", "content": prompt_payload["system_prompt"]},
        {"role": "user", "content": prompt_payload["user_prompt"]},
    ]
    response_text = call_groq(messages)
    payload = parse_json_response(response_text)
    if isinstance(payload, list):
        return payload
    return payload["personas"]


def parse_json_response(response_text: str) -> dict[str, Any]:
    response_text = response_text.strip()
    if not response_text:
        raise ValueError("Groq returned an empty response.")

    fenced_match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, flags=re.DOTALL)
    if fenced_match:
        response_text = fenced_match.group(1).strip()

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\])", response_text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def main() -> None:
    reviews = load_reviews(INPUT_PATH)
    reviews_by_id = {review["id"]: review for review in reviews}

    groups = build_groups(reviews)
    write_json(GROUPS_OUTPUT_PATH, {"groups": groups})

    prompt_payload = build_prompt_payload(groups, reviews_by_id)
    write_json(PROMPT_OUTPUT_PATH, prompt_payload)

    if get_groq_api_key():
        try:
            personas = generate_personas_with_groq(prompt_payload)
            generation_mode = "groq"
        except Exception as exc:
            print(f"Groq persona generation failed, falling back to heuristic mode: {exc}")
            personas = heuristic_personas(groups)
            generation_mode = "heuristic-fallback"
    else:
        personas = heuristic_personas(groups)
        generation_mode = "heuristic"

    write_json(PERSONAS_OUTPUT_PATH, {"generation_mode": generation_mode, "personas": personas})
    print(f"Wrote {len(groups)} automated review groups to '{GROUPS_OUTPUT_PATH}'.")
    print(f"Wrote {len(personas)} automated personas to '{PERSONAS_OUTPUT_PATH}'.")
    print(f"Saved automation prompt to '{PROMPT_OUTPUT_PATH}'.")


if __name__ == "__main__":
    main()

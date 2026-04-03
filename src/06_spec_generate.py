"""Generate structured specifications from automated personas."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


GROQ_API_KEY = ""
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

ROOT_DIR = Path(__file__).resolve().parents[1]
PERSONAS_PATH = ROOT_DIR / "personas" / "personas_auto.json"
GROUPS_PATH = ROOT_DIR / "data" / "review_groups_auto.json"
SPEC_OUTPUT_PATH = ROOT_DIR / "spec" / "spec_auto.md"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_groq_api_key() -> str:
    return GROQ_API_KEY.strip() or os.getenv("GROQ_API_KEY", "").strip()


def call_groq(messages: list[dict[str, str]]) -> str:
    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError("Groq API key is not configured.")

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.2,
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


def heuristic_requirements(personas: list[dict[str, Any]]) -> list[dict[str, str]]:
    requirements: list[dict[str, str]] = []
    templates = {
        "PA1": [
            (
                "FR_auto_1",
                "The system shall provide a primary home-screen action that opens a support chat in no more than one tap.",
                "Given the user is on the home screen, when the user selects the primary support action, then an active chat input opens within 3 seconds.",
            ),
            (
                "FR_auto_2",
                "The system shall acknowledge emotional disclosures using supportive and non-judgmental language.",
                "Given the user sends a message describing stress, anxiety, or loneliness, when the system responds, then the first reply acknowledges the emotional state without blaming or dismissive wording.",
            ),
        ],
        "PA2": [
            (
                "FR_auto_3",
                "The system shall organize self-help tools into clearly labeled exercise categories including breathing, journaling, and thought reframing.",
                "Given the user opens the tools area, when the screen loads, then breathing, journaling, and thought reframing appear as separate categories.",
            ),
            (
                "FR_auto_4",
                "The system shall allow a user to start a listed self-help exercise within 2 taps from the tools area.",
                "Given the user is in the tools area, when the user selects a listed exercise, then the first instruction is displayed within 3 seconds and no more than 2 taps are required.",
            ),
        ],
        "PA3": [
            (
                "FR_auto_5",
                "The system shall generate responses that reference at least one topic or feeling from the user's most recent message.",
                "Given the user sends a message with a specific concern, when the system replies, then the reply includes at least one matching topic, feeling, or situation from that message.",
            ),
            (
                "FR_auto_6",
                "The system shall preserve active session context across at least 20 turns of conversation.",
                "Given the user has exchanged 20 or fewer turns in an active session, when the user asks a follow-up question, then the response reflects information from earlier turns instead of restarting the conversation.",
            ),
        ],
        "PA4": [
            (
                "FR_auto_7",
                "The system shall present free features and paid features in separate labeled sections before purchase confirmation.",
                "Given the user opens the pricing or upgrade screen, when the screen is displayed, then it shows separate labeled sections for free features and paid features before any checkout step.",
            ),
            (
                "FR_auto_8",
                "The system shall allow the user to dismiss upgrade prompts and continue any current free-tier flow without losing progress.",
                "Given the user is using a free-tier feature, when an upgrade prompt appears and the user dismisses it, then the user returns to the same flow with previously entered progress preserved.",
            ),
        ],
        "PA5": [
            (
                "FR_auto_9",
                "The system shall load the home screen and active chat screen within 3 seconds under normal network conditions.",
                "Given the app is launched or an existing chat is opened on a supported device with normal network connectivity, when the requested screen loads, then it becomes interactive within 3 seconds.",
            ),
            (
                "FR_auto_10",
                "The system shall restore unsent draft text and same-day chat history after an interruption or app restart.",
                "Given the user has typed a draft or completed a chat exchange, when the app is interrupted and reopened on the same day, then the draft text and previous chat messages are restored.",
            ),
        ],
    }

    for persona in personas:
        for requirement_id, description, acceptance in templates.get(persona["id"], []):
            requirements.append(
                {
                    "requirement_id": requirement_id,
                    "description": description,
                    "source_persona": f"{persona['id']} - {persona['name']}",
                    "traceability": f"Derived from review group {persona['derived_from_group']}",
                    "acceptance_criteria": acceptance,
                }
            )
    return requirements


def render_spec(requirements: list[dict[str, str]]) -> str:
    parts: list[str] = []
    for requirement in requirements:
        parts.append(f"# Requirement ID: {requirement['requirement_id']}")
        parts.append("")
        parts.append(f"- Description: {requirement['description']}")
        parts.append(f"- Source Persona: {requirement['source_persona']}")
        parts.append(f"- Traceability: {requirement['traceability']}")
        parts.append(f"- Acceptance Criteria: {requirement['acceptance_criteria']}")
        parts.append("")
    return "\n".join(parts).strip() + "\n"


def main() -> None:
    personas_payload = load_json(PERSONAS_PATH)
    personas = personas_payload["personas"]

    if get_groq_api_key():
        try:
            groups_payload = load_json(GROUPS_PATH)
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a senior requirements engineer for a software engineering course project. "
                        "Your job is to transform personas into clear, testable, traceable functional requirements. "
                        "Write concise markdown only. Do not add explanations before or after the requirements."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Create exactly 10 requirements, with two requirements per persona, following this exact format:\n"
                        "# Requirement ID: FR_auto_n\n"
                        "- Description: ...\n"
                        "- Source Persona: ...\n"
                        "- Traceability: Derived from review group ...\n"
                        "- Acceptance Criteria: ...\n\n"
                        "Requirements must satisfy all of these rules:\n"
                        "1. Every requirement must describe observable system behavior, not vague product goals.\n"
                        "2. Avoid ambiguous words such as good, better, seamless, user-friendly, helpful, intuitive, fast, easy, appropriate.\n"
                        "3. Acceptance criteria must be concrete and verifiable, ideally with measurable conditions, explicit triggers, or observable results.\n"
                        "4. Keep traceability aligned to the persona's derived review group.\n"
                        "5. Prefer behaviors around conversation quality, support entry, tools, pricing transparency, reliability, and history preservation only if grounded in the personas.\n"
                        "6. Return markdown only, with no code fences.\n\n"
                        "Here is a style example for one requirement:\n"
                        "# Requirement ID: FR_auto_example\n"
                        "- Description: The system shall display separate labeled sections for free features and paid features on the pricing screen before checkout.\n"
                        "- Source Persona: Example Persona\n"
                        "- Traceability: Derived from review group A4\n"
                        "- Acceptance Criteria: Given the user opens the pricing screen, when the screen finishes loading, then the interface shows one labeled section for free features and one labeled section for paid features before any purchase confirmation step.\n\n"
                        f"Personas:\n{json.dumps(personas, ensure_ascii=False, indent=2)}\n\n"
                        f"Groups:\n{json.dumps(groups_payload, ensure_ascii=False, indent=2)}"
                    ),
                },
            ]
            spec_text = call_groq(messages)
        except Exception as exc:
            print(f"Groq spec generation failed, falling back to heuristic mode: {exc}")
            spec_text = render_spec(heuristic_requirements(personas))
    else:
        spec_text = render_spec(heuristic_requirements(personas))

    SPEC_OUTPUT_PATH.write_text(spec_text, encoding="utf-8")
    print(f"Wrote automated specification to '{SPEC_OUTPUT_PATH}'.")


if __name__ == "__main__":
    main()

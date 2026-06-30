"""
Module 01 · structured_output.py — getting reliable JSON back from an LLM.

Run from the project root:
    python modules/01-prompt-engineering/structured_output.py

Why this matters: to USE an LLM inside a program, you usually need structured
data (JSON), not prose. The reliable recipe has two halves:
  1. ASK clearly — a system prompt that says "return ONLY JSON, these keys".
  2. PARSE defensively — strip any stray ```json fences, then json.loads().

(The bulletproof way to force structure is 'tool use', which we learn in
module 03. This module shows the simpler approach you'll use most of the time.)
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.llm import claude, SetupError


def parse_json(text: str) -> dict:
    """
    Turn the model's reply into a dict.

    Models sometimes wrap JSON in a markdown code fence like ```json ... ```.
    We strip that if present, then parse. This little bit of defensiveness is
    the difference between code that works 99% of the time and code that crashes.
    """
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Drop the first line (``` or ```json) and any trailing ``` fence.
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        cleaned = cleaned.rsplit("```", 1)[0]
    return json.loads(cleaned.strip())


def extract_contact(text: str) -> dict:
    """Ask Claude to pull structured fields out of messy text and return a dict."""
    system = (
        "You extract contact info. Respond with ONLY a JSON object and nothing "
        "else — no prose, no explanation, no markdown code fences. Use exactly "
        'these keys: "name" (string), "email" (string or null), '
        '"company" (string or null).'
    )
    reply = claude(text, system=system, temperature=0, max_tokens=300)
    return parse_json(reply)


def main() -> None:
    messy_inputs = [
        "Hey, this is Priya Nair from Acme Robotics — reach me at priya@acme.io anytime.",
        "Call me! - Tom (no email, I work at a tiny startup called Beanstalk)",
        "Dr. Lena Ortiz, lena.ortiz@uni.edu",
    ]

    print("Extracting structured contacts from messy text:\n")
    for text in messy_inputs:
        data = extract_contact(text)
        # Prove it's real, usable data by accessing fields like a normal dict.
        print(f"  input : {text}")
        print(f"  parsed: name={data['name']!r}  email={data['email']!r}  "
              f"company={data['company']!r}")
        assert isinstance(data, dict) and "name" in data  # would raise if malformed
        print()

    print("✅ Done. Every reply parsed as valid JSON we can use in code.")
    print("   Try this: add a phone-number field to the system prompt and re-run.")


if __name__ == "__main__":
    try:
        main()
    except SetupError as e:
        print("\n⚠️  Setup problem:\n")
        print(str(e))
        sys.exit(2)

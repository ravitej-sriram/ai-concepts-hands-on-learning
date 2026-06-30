"""
Module 02 · thinking_vs_fast.py — see 'test-time compute' actually pay off.

Run from the project root:
    python modules/02-reasoning-and-test-time-compute/thinking_vs_fast.py

Idea: a model can spend MORE compute at answer-time ("test-time compute") by
reasoning before it replies. On easy questions that's wasted money; on hard
ones it can flip a wrong answer into a right one. This script shows both.
"""

import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.llm import claude, claude_think, SetupError

# See modules/01-prompt-engineering/prompting_techniques.py for why this
# exists: tools/llm_judge.py sets this env var to ask for a structured JSON
# dump of prompt/output pairs, checked against this module's rubric.yaml.
# Normal runs (the learner just running the script) are unaffected.
_JUDGE_OUTPUT_PATH = os.environ.get("JUDGE_OUTPUT_PATH")
_exercises: list[dict] = []


def section(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def trim(text: str, max_chars: int = 1000) -> str:
    """Cleanly cut long output at a sentence/line boundary for display."""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    boundary = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"), cut.rfind("\n"))
    if boundary > max_chars * 0.4:
        cut = cut[: boundary + 1]
    return cut.rstrip() + "\n   [...trimmed for the lesson — the model would keep going]"


def main() -> None:
    # A puzzle with a deliberate TWIST (the day-5 wind setback) instead of the
    # famous "snail climbs out of a well" puzzle's standard form. The plain
    # version has a well-known shortcut formula; a model can recall that
    # formula and sound confident while being wrong, because it skips the
    # twist. That's exactly the gap test-time compute is supposed to close —
    # a generic, instantly-recalled puzzle wouldn't show it (we verified this
    # live: the unmodified water-jug/well puzzles got solved correctly even
    # without extended thinking, because the model has just memorized them).
    puzzle = (
        "A snail is at the bottom of a 30-foot well. Each day it climbs 4 "
        "feet, then each night it slides back 3 feet. However, on day 5 "
        "specifically, right after climbing (before that night's slide), a "
        "gust of wind blows it back an extra 2 feet. On which day does the "
        "snail first reach the top of the well (height 30 feet or more, "
        "measured right after a day's climb, before any slide-back)?"
    )
    fast_prompt = (
        puzzle + " Don't calculate step by step — give your immediate "
        "gut-instinct answer as just a day number."
    )
    thinking_prompt = puzzle + " End your reply with: FINAL: <day number>."

    section("A · FAST mode (no extended thinking)")
    print(f"Prompt: {fast_prompt}\n")
    fast = claude(fast_prompt, temperature=0, max_tokens=50)
    print("Output:", fast.strip())

    section("B · THINKING mode (extended thinking / more test-time compute)")
    print(f"Prompt: {thinking_prompt}\n")
    result = claude_think(thinking_prompt, thinking_budget=2000, max_tokens=3000)
    peek = result["thinking"].strip().replace("\n", " ")
    print(f"(peek at the model's private reasoning: {peek[:240]}...)\n")
    print("Final answer:\n" + trim(result["answer"]))

    section("C · The trade-off")
    print(
        "The correct answer is day 29 (the day-5 wind setback delays things by\n"
        "2 days past the 'normal' well puzzle's day 27). A gut-instinct answer\n"
        "often misses that twist and lands on some OTHER number — the model is\n"
        "pattern-matching the famous version of this puzzle instead of\n"
        "simulating this one's day 5. Extended thinking has room to simulate\n"
        "day-by-day and catch it. If FAST also said 29 this run, that's fine —\n"
        "the point isn't 'fast is always wrong', it's that thinking mode spent\n"
        "many more tokens (= more time + money) to verify instead of\n"
        "pattern-match, which is what you're paying for.\n"
        "On 'What is the capital of France?' that same spend would be pure\n"
        "waste — the skill is knowing WHICH problems deserve it."
    )
    print("\n✅ Done. See the README for when to reach for reasoning models.")

    _exercises.append({
        "id": "test_time_compute",
        "without_prompt": fast_prompt,
        "without_output": fast,
        "with_prompt": thinking_prompt,
        "with_output": result["answer"],
    })
    if _JUDGE_OUTPUT_PATH:
        Path(_JUDGE_OUTPUT_PATH).write_text(json.dumps(_exercises, indent=2))


if __name__ == "__main__":
    try:
        main()
    except SetupError as e:
        print("\n⚠️  Setup problem:\n")
        print(str(e))
        sys.exit(2)

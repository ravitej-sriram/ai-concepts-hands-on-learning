"""
Module 01 · prompting_techniques.py — the four prompting moves you'll use forever.

Run from the project root:
    python modules/01-prompt-engineering/prompting_techniques.py

Demonstrates, side by side:
  1. A vague prompt vs. a specific one.
  2. A SYSTEM PROMPT to set role + rules + output format.
  3. FEW-SHOT: teaching by examples instead of instructions.
  4. CHAIN-OF-THOUGHT: asking the model to reason step by step.
"""

import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.llm import claude, SetupError

# tools/llm_judge.py sets this env var to ask this script to also dump its
# prompt/output pairs as JSON (in addition to the normal printed output), so
# the judge can check each exercise against modules/01.../rubric.yaml without
# scraping printed text. Plain runs (the learner just running the script) are
# unaffected — nothing is written unless this is set.
_JUDGE_OUTPUT_PATH = os.environ.get("JUDGE_OUTPUT_PATH")
_exercises: list[dict] = []


def section(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def trim(text: str, max_chars: int = 1000) -> str:
    """Cleanly cut long output at a sentence/line boundary for display.

    max_tokens caps the API call, but the model can still get cut off
    mid-word — that looks like a bug, not a lesson. We trim ourselves at a
    clean boundary instead and say so, so any cutoff you see is intentional.
    """
    text = text.strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    boundary = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"), cut.rfind("\n"))
    if boundary > max_chars * 0.4:  # only use the boundary if it's not too early
        cut = cut[: boundary + 1]
    return cut.rstrip() + "\n   [...trimmed for the lesson — the model would keep going]"


def compare(exercise_id: str, without_label: str, without_prompt: str, without_output: str,
            with_label: str, with_prompt: str, with_output: str) -> None:
    """Print a prompt/output pair WITHOUT the technique, then WITH it —
    same shape every time so the contrast is the thing you look at.

    exercise_id must match an id in this module's rubric.yaml so
    tools/llm_judge.py can match this exercise to its pass/fail criteria.
    """
    print(f"\nWITHOUT {without_label} — prompt sent:\n  {without_prompt}")
    print(f"WITHOUT {without_label} — output:\n{trim(without_output)}")
    print(f"\nWITH {with_label} — prompt sent:\n  {with_prompt}")
    print(f"WITH {with_label} — output:\n{trim(with_output)}")
    _exercises.append({
        "id": exercise_id,
        "without_prompt": without_prompt,
        "without_output": without_output,
        "with_prompt": with_prompt,
        "with_output": with_output,
    })


def main() -> None:
    # 1) VAGUE vs SPECIFIC -----------------------------------------------------
    section("1 · Specific instructions (audience, length, format)")
    vague_prompt = "Write about dogs."
    specific_prompt = (
        "Write exactly 2 sentences for a 6-year-old about why dogs wag their "
        "tails. Use simple words."
    )
    vague = claude(vague_prompt, temperature=0, max_tokens=250)
    specific = claude(specific_prompt, temperature=0, max_tokens=120)
    compare(
        "specific_instructions",
        "specific instructions", vague_prompt, vague,
        "specific instructions", specific_prompt, specific,
    )

    # 2) SYSTEM PROMPT ---------------------------------------------------------
    # The system prompt sets HOW the model should behave: persona, rules, format.
    # We run the SAME user message with and without it, so you see the system
    # prompt's effect directly instead of taking it on faith.
    section("2 · System prompt (set role, rules, and format once)")
    review_request = (
        "Review this: a function named 'doStuff' that reads a file, parses JSON, "
        "and returns it, with no error handling."
    )
    system = (
        "You are a terse senior Python reviewer. "
        "Reply in at most 3 bullet points. Never write code, only feedback."
    )
    no_system = claude(review_request, temperature=0, max_tokens=350)
    with_system = claude(review_request, system=system, temperature=0, max_tokens=200)
    print(f"(Same user message both times: '{review_request}')")
    print(f"(System prompt added in the WITH run: '{system}')")
    compare(
        "system_prompt",
        "system prompt", review_request, no_system,
        "system prompt", review_request, with_system,
    )

    # 3) FEW-SHOT --------------------------------------------------------------
    # Few-shot's real value isn't teaching the model sentiment (it already
    # knows that) — it's teaching an arbitrary CONVENTION you can't fully spell
    # out in words. Here the convention is "use +1/-1/0", not "POSITIVE" etc.
    # Zero-shot has no way to guess that scheme, so it invents its own.
    section("3 · Few-shot (teach a convention by showing examples)")
    target_review = "Best purchase I have made all year."
    zero_shot_prompt = f"Classify the sentiment of this review: '{target_review}'"
    few_shot_prompt = (
        "Review: 'Absolutely loved it!' -> +1\n"
        "Review: 'It broke after one day.' -> -1\n"
        "Review: 'It arrived on Tuesday.' -> 0\n"
        f"Review: '{target_review}' ->"
    )
    zero_shot = claude(zero_shot_prompt, temperature=0, max_tokens=200)
    few_shot = claude(few_shot_prompt, temperature=0, max_tokens=10)
    compare(
        "few_shot_convention",
        "few-shot examples", zero_shot_prompt, zero_shot,
        "few-shot examples", few_shot_prompt, few_shot,
    )
    print(
        "\nBoth runs agree the review is positive — that part the model "
        "already knows. What changes is the OUTPUT CONVENTION: with no "
        "examples, the model has to invent its own label scheme (so it picks "
        "something reasonable like 'Positive', maybe with a whole writeup). "
        "With 3 examples using '+1/-1/0', it copies that exact scheme instead "
        "— because '+1/-1/0 for sentiment' isn't a standard convention it can "
        "infer from the word 'classify' alone. That's what few-shot is really "
        "for: teaching a convention that's faster to SHOW than to DESCRIBE."
    )

    # 4) CHAIN-OF-THOUGHT ------------------------------------------------------
    # For reasoning tasks, asking the model to think step by step often fixes
    # wrong answers — it spends more tokens 'working it out' before answering.
    # NOTE: we deliberately do NOT use the famous "$1.10 bat and ball" puzzle —
    # it's the canonical Cognitive Reflection Test question, so memorized in
    # training data that modern models often get it right even when rushed,
    # which defeats the demo. These numbers are off the well-known version so
    # the model has to actually compute, not recall.
    section("4 · Chain-of-thought (ask it to reason step by step)")
    puzzle = (
        "A racket and a shuttlecock cost $6.30 in total. The racket costs $5.00 "
        "more than the shuttlecock. How much does the shuttlecock cost?"
    )
    blunt_prompt = puzzle + " Answer with just the amount."
    reasoned_prompt = puzzle + " Think step by step, then give the final amount on its own line."
    blunt = claude(blunt_prompt, temperature=0, max_tokens=20)
    reasoned = claude(reasoned_prompt, temperature=0, max_tokens=300)
    compare(
        "chain_of_thought",
        "chain-of-thought (blunt)", blunt_prompt, blunt,
        "chain-of-thought (step-by-step)", reasoned_prompt, reasoned,
    )
    print(
        "\n(The intuitive trap is $1.30 [just '6.30 - 5.00']; the correct answer "
        "is $0.65 [shuttlecock=x, racket=x+5, 2x+5=6.30 -> x=0.65]. If the "
        "model's blunt answer is ALSO $0.65, that's fine — it means it didn't "
        "fall for the trap this time. The point isn't 'blunt is always wrong', "
        "it's that blunt answers skip verification and step-by-step answers "
        "show their work so YOU can catch it when they slip.)"
    )

    print("\n✅ Done. Open the README and try editing these prompts yourself.")

    if _JUDGE_OUTPUT_PATH:
        Path(_JUDGE_OUTPUT_PATH).write_text(json.dumps(_exercises, indent=2))


if __name__ == "__main__":
    try:
        main()
    except SetupError as e:
        print("\n⚠️  Setup problem:\n")
        print(str(e))
        sys.exit(2)

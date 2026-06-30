"""
Module 00 · hello_llm.py — your very first call to an LLM.

Run it from the project root:
    python modules/00-setup-and-mental-model/hello_llm.py

What it does:
  1. Checks your setup is ready (API key present, package installed).
  2. Sends one prompt to Claude and prints the reply.
  3. Sends the SAME prompt twice at different 'temperatures' so you can SEE
     how temperature changes the model's behavior.

If anything's not set up yet, it prints a friendly message telling you the fix.
"""

# --- Boilerplate so this script can find the 'shared' package ---------------
# (Every module script starts with these 3 lines. They add the project root to
#  Python's import path so `from shared.llm import ...` works no matter where
#  you run the script from. You can ignore the details for now.)
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
# ---------------------------------------------------------------------------

from shared.llm import claude, check_claude_ready, SetupError

# See modules/01-prompt-engineering/prompting_techniques.py for why this
# exists: tools/llm_judge.py sets this env var to ask for a structured JSON
# dump of prompt/output pairs, checked against this module's rubric.yaml.
# Normal runs (the learner just running the script) are unaffected.
_JUDGE_OUTPUT_PATH = os.environ.get("JUDGE_OUTPUT_PATH")
_exercises: list[dict] = []


def main() -> None:
    print("=" * 70)
    print("Module 00 · Your first LLM call")
    print("=" * 70)

    # Step 1: Make sure everything is wired up before we try anything fancy.
    print("\n[1/3] Checking your setup...")
    ok, message = check_claude_ready()
    print("   " + message.replace("\n", "\n   "))
    if not ok:
        print("\nFix the above, then run this script again. (See SETUP.md.)")
        sys.exit(2)  # exit 2 = "setup needed / skip" (see tools/smoke_test.py)

    # Step 2: Ask Claude something simple.
    print("\n[2/3] Asking Claude a question...")
    question = "In one sentence, explain what a large language model is to a curious 12-year-old."
    answer = claude(question, temperature=0)
    print(f"   Q: {question}")
    print(f"   A: {answer.strip()}")

    # Step 3: See temperature in action. Same prompt, three calls.
    # temperature=0 → always picks the single most-likely word → same every run.
    # temperature=1 → samples from the distribution → varies every run.
    # We call temp=1 TWICE so you can see the variance in a single run
    # without needing to re-run the script.
    print("\n[3/3] Temperature demo — same prompt, three calls:")
    creative_prompt = "Write one sentence describing what it feels like to touch a cloud."
    print(f"   Prompt: {creative_prompt}\n")
    cold  = claude(creative_prompt, temperature=0).strip()
    hot1  = claude(creative_prompt, temperature=1.0).strip()
    hot2  = claude(creative_prompt, temperature=1.0).strip()

    print(f"   temp=0  (run 1) →  {cold}")
    print(f"   temp=0  (run 2) →  {cold}  ← same")
    print()
    print(f"   temp=1  (call 1) →  {hot1}")
    print(f"   temp=1  (call 2) →  {hot2}")
    print()
    print("   temp=0 locks onto one answer. temp=1 samples a different one each time.")

    print("\n✅ Done! You just used an LLM from your own code.")
    print("   Next: open this module's README and read the 'Mental model' section.")

    _exercises.append({
        "id": "temperature",
        "without_prompt": creative_prompt,
        "without_output": hot1,  # temp=1: uncontrolled, varies across calls
        "with_prompt": creative_prompt,
        "with_output": cold,     # temp=0: focused, same every run
    })
    if _JUDGE_OUTPUT_PATH:
        Path(_JUDGE_OUTPUT_PATH).write_text(json.dumps(_exercises, indent=2))


if __name__ == "__main__":
    try:
        main()
    except SetupError as e:
        # Friendly, actionable error instead of a scary stack trace.
        print("\n⚠️  Setup problem:\n")
        print(str(e))
        sys.exit(2)  # exit 2 = "setup needed / skip" (see tools/smoke_test.py)

"""
Module 07 · context_and_memory.py — why "memory" is an illusion you build.

Run from the project root (Claude only — no Ollama needed):
    python modules/07-context-engineering-and-memory/context_and_memory.py

Key truth from module 00: the model has NO memory between calls. "Memory" in
chat apps is just the previous conversation being re-sent every time. This script
makes that concrete, then shows how to manage a growing conversation with a
running summary so you don't blow the context window (or your budget).
"""

import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.llm import get_client, claude, DEFAULT_CLAUDE_MODEL, SetupError

_JUDGE_OUTPUT_PATH = os.environ.get("JUDGE_OUTPUT_PATH")
_exercises: list[dict] = []


def chat(messages: list[dict], *, max_tokens: int = 300) -> str:
    """Send a FULL conversation (list of turns) and return the model's reply."""
    client = get_client()
    resp = client.messages.create(
        model=DEFAULT_CLAUDE_MODEL, max_tokens=max_tokens,
        temperature=0, messages=messages,
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def section(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main() -> None:
    # 1) NO MEMORY: two separate calls. The second can't know the first.
    #    Print BOTH responses so the contrast is visible: call 1 received the name,
    #    call 2 has no access to it.
    section("1 · The model has no memory between calls")
    first_reply = claude("My name is Sam and my favorite color is teal.", max_tokens=50)
    print("Call 1 — prompt: 'My name is Sam and my favorite color is teal.'")
    print("   " + first_reply.strip().replace("\n", "\n   "))
    forgot = claude("What is my name and favorite color?", max_tokens=60)
    print("\nCall 2 — NEW call (no history): 'What is my name and favorite color?'")
    print("   " + forgot.strip().replace("\n", "\n   "))
    print("   (It can't know — call 2 has no access to call 1's messages.)")
    _exercises.append({"id": "no_memory", "first_reply": first_reply, "forgot_reply": forgot})

    # 2) MEMORY = re-sending the conversation. We keep a 'messages' list.
    section("2 · 'Memory' is just re-sending the whole conversation")
    conversation = [
        {"role": "user", "content": "My name is Sam and my favorite color is teal."},
    ]
    conversation.append({"role": "assistant", "content": chat(conversation)})
    # Now ask again — but this time the earlier turn is INCLUDED in the list.
    conversation.append({"role": "user", "content": "What is my name and favorite color?"})
    remembered = chat(conversation)
    conversation.append({"role": "assistant", "content": remembered})
    print("Same question, but the history was included this time:")
    print("   " + remembered.strip().replace("\n", "\n   "))
    print("   (It 'remembers' only because we re-sent the earlier turn.)")
    _exercises.append({"id": "memory_via_history", "remembered_reply": remembered})

    # 3) The problem: conversations grow. Re-sending everything costs tokens and
    #    eventually overflows the context window. Fix: SUMMARIZE old turns.
    section("3 · Context engineering: summarize old turns to stay small")
    # Pretend we've had a long chat. Compress it into a compact 'memory'.
    long_history = (
        "User said their name is Sam, favorite color teal, they live in Denver, "
        "they're planning a 2-week trip to Japan in October, budget $4000, "
        "vegetarian, and they want hiking and food recommendations."
    )
    memory = claude(
        "Summarize the key facts to remember about this user in 1-2 sentences, "
        "as durable notes:\n\n" + long_history,
        temperature=0, max_tokens=120,
    )
    print("Compressed memory of a long chat:")
    print("   " + memory.strip().replace("\n", "\n   "))

    # Continue the chat using ONLY the short summary instead of the full history.
    compact_conversation = [
        {"role": "user", "content": f"(Notes about me: {memory.strip()})\n\n"
                                    "Given that, suggest one restaurant type and one "
                                    "activity for my trip. One line each."},
    ]
    print("\nReply using only the compact memory (not the full transcript):")
    print("   " + chat(compact_conversation).strip().replace("\n", "\n   "))

    print("\n" + "=" * 70)
    print("✅ Takeaways: you OWN the context window. What you put in it (and leave")
    print("   out) is 'context engineering' — the core skill behind agents & RAG.")

    if _JUDGE_OUTPUT_PATH:
        Path(_JUDGE_OUTPUT_PATH).write_text(json.dumps(_exercises, indent=2))


if __name__ == "__main__":
    try:
        main()
    except SetupError as e:
        print("\n⚠️  Setup problem:\n")
        print(str(e))
        sys.exit(2)

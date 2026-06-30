"""
shared/llm.py — tiny, friendly wrappers around the models we use in this course.

You import from this file in almost every module so the lessons stay short and
readable. There are two "brains" available:

  • claude(...)      → calls Anthropic's Claude over the internet (needs an API key).
  • local_llm(...)   → calls a model running locally on your Mac via Ollama (free).
  • embed_local(...) → turns text into a vector (a list of numbers) using Ollama.

Everything here is heavily commented on purpose — read it once and you'll
understand what's happening every time a lesson calls these functions.
"""

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Load your secrets from the .env file (so we never hard-code an API key).
# ---------------------------------------------------------------------------
# python-dotenv reads the .env file in the project root and puts the values
# into "environment variables" that os.environ can see.
from dotenv import load_dotenv

# Find the project root (the folder that contains this 'shared' folder) and
# load the .env that lives there, no matter which folder you run a script from.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# Sensible defaults. You can override these in your .env file (see .env.example).
DEFAULT_CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
DEFAULT_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
DEFAULT_OLLAMA_EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")

OLLAMA_URL = "http://localhost:11434"  # where Ollama listens by default


# ---------------------------------------------------------------------------
# 2. A small, clear error type so beginners get *helpful* messages, not stack
#    traces full of library internals.
# ---------------------------------------------------------------------------
class SetupError(Exception):
    """Raised when something about your setup isn't ready (key missing, etc.)."""


# ---------------------------------------------------------------------------
# 3. Talking to Claude (the cloud model).
# ---------------------------------------------------------------------------
def get_client():
    """
    Return a ready-to-use Anthropic client, or raise a friendly SetupError.

    Most lessons just call claude(...) below. But a few advanced modules
    (structured output via 'prefill', extended thinking, tool use) want the
    real, full API — they call get_client() and use it directly so you see
    exactly what's happening. This keeps the key-handling in one place.
    """
    try:
        import anthropic
    except ImportError as e:
        raise SetupError(
            "The 'anthropic' package isn't installed.\n"
            "Fix: activate your venv and run  pip install -r requirements.txt"
        ) from e

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key or api_key.startswith("sk-ant-xxxx"):
        raise SetupError(
            "No real ANTHROPIC_API_KEY found.\n"
            "Fix: copy .env.example to .env and paste your key from\n"
            "     https://console.anthropic.com (Settings → API Keys).\n"
            "See SETUP.md for step-by-step help."
        )
    return anthropic.Anthropic(api_key=api_key)


def claude(
    prompt: str,
    *,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 1.0,
) -> str:
    """
    Send one message to Claude and return its text reply as a string.

    Args:
        prompt:      What you want to ask/tell the model (the "user" message).
        system:      Optional "system prompt" — instructions about *how* to behave
                     (persona, rules, output format). More on this in module 01.
        model:       Which Claude model to use. Defaults to DEFAULT_CLAUDE_MODEL.
        max_tokens:  Roughly the maximum length of the reply (1 token ≈ ¾ of a word).
        temperature: 0.0 = focused/deterministic, 1.0 = more creative/varied.

    Returns:
        The model's reply, as plain text.
    """
    import anthropic  # for the error type below; get_client() handles install/key checks

    client = get_client()

    # The Messages API takes a list of messages. Here we send a single user turn.
    kwargs = {
        "model": model or DEFAULT_CLAUDE_MODEL,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system is not None:
        kwargs["system"] = system  # system prompt is a top-level field, not a message

    try:
        response = client.messages.create(**kwargs)
    except anthropic.APIStatusError as e:
        # Turn cryptic HTTP errors into something a learner can act on.
        raise SetupError(
            f"Claude API returned an error ({e.status_code}).\n"
            "Common causes: out of credits, wrong/expired key, or an invalid model name.\n"
            f"Details: {e.message}"
        ) from e

    # A reply can contain multiple 'content blocks'; we join the text ones.
    return "".join(block.text for block in response.content if block.type == "text")


def claude_think(
    prompt: str,
    *,
    thinking_budget: int = 2000,
    max_tokens: int = 3000,
    model: str | None = None,
) -> dict:
    """
    Call Claude with 'extended thinking' turned on (module 02).

    The model is given a scratchpad to reason before answering. We get back BOTH
    its private reasoning and its final answer, so you can see the difference
    spending extra 'thinking' tokens makes.

    Returns a dict: {"thinking": <reasoning text>, "answer": <final text>}.

    Notes:
      • thinking_budget must be < max_tokens (it's part of the same budget).
      • When thinking is enabled the API requires temperature=1, so we set it.
    """
    client = get_client()
    response = client.messages.create(
        model=model or DEFAULT_CLAUDE_MODEL,
        max_tokens=max_tokens,
        temperature=1,  # required when extended thinking is enabled
        thinking={"type": "enabled", "budget_tokens": thinking_budget},
        messages=[{"role": "user", "content": prompt}],
    )

    thinking_text, answer_text = "", ""
    for block in response.content:
        if block.type == "thinking":
            thinking_text += block.thinking
        elif block.type == "text":
            answer_text += block.text
    return {"thinking": thinking_text, "answer": answer_text}


# ---------------------------------------------------------------------------
# 4. Talking to a local model via Ollama (free, runs on your machine).
# ---------------------------------------------------------------------------
def local_llm(prompt: str, *, model: str | None = None) -> str:
    """
    Send a prompt to a local model running in Ollama and return its text reply.

    Requires Ollama to be installed and running, and the model pulled, e.g.:
        ollama pull llama3.2
    See SETUP.md.
    """
    import requests  # imported here so cloud-only scripts don't need it loaded early

    model = model or DEFAULT_OLLAMA_MODEL
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise SetupError(
            "Couldn't reach Ollama at http://localhost:11434.\n"
            "Fix: install it from https://ollama.com, then make sure it's running\n"
            "     (open the Ollama app, or run 'ollama serve')."
        ) from e
    except requests.exceptions.HTTPError as e:
        raise SetupError(
            f"Ollama responded with an error for model '{model}'.\n"
            f"Have you pulled it?  Try:  ollama pull {model}\n"
            f"Details: {e}"
        ) from e

    return resp.json().get("response", "")


def embed_local(text: str, *, model: str | None = None) -> list[float]:
    """
    Turn a piece of text into an 'embedding' — a list of numbers that captures
    its meaning, so we can compare texts by similarity. Used in the RAG modules.
    Runs locally and free via Ollama.
    """
    import requests

    model = model or DEFAULT_OLLAMA_EMBED_MODEL
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=120,
        )
        resp.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise SetupError(
            "Couldn't reach Ollama at http://localhost:11434.\n"
            "Fix: install from https://ollama.com and make sure it's running, then:\n"
            f"     ollama pull {model}"
        ) from e
    except requests.exceptions.HTTPError as e:
        raise SetupError(
            f"Ollama couldn't create an embedding with model '{model}'.\n"
            f"Fix: ollama pull {model}\nDetails: {e}"
        ) from e

    return resp.json().get("embedding", [])


# ---------------------------------------------------------------------------
# 5. A convenience used by module 00 and the smoke test to check your setup.
# ---------------------------------------------------------------------------
def check_claude_ready() -> tuple[bool, str]:
    """Return (ok, message). Doesn't raise — safe to call for a friendly check."""
    try:
        reply = claude("Reply with exactly the word: ready", max_tokens=10, temperature=0)
        return True, f"Claude is reachable. It replied: {reply.strip()!r}"
    except SetupError as e:
        return False, str(e)

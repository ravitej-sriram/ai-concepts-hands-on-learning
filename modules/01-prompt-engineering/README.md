# Module 01 · Prompt Engineering & Structured Outputs

⏱️ **~50 minutes**

> Goal: reliably steer the model with **system prompts, examples, and reasoning**,
> and get **machine-readable JSON** back so you can use the output in real code.

---

## What you'll learn

- The four prompting moves you'll reach for constantly: **be specific**,
  **system prompts**, **few-shot examples**, **chain-of-thought**.
- How to get **reliable JSON** out of an LLM — *ask clearly, then parse
  defensively* — the bridge from "chatbot" to "component inside my program".

## Why it matters

Prompting is the cheapest, fastest way to change an LLM's behavior — no training,
no infrastructure. And turning free-form replies into **structured data** is what
lets you wire an LLM into actual software (the rest of this course depends on it).

---

## Mental model: the prompt is the entire program

The model has no memory and no goals of its own (module 00). For one call, the
prompt you send **is the whole program** — instructions, data, and examples all
in text. So "programming" an LLM means writing clearer text, in roughly this
order of power:

1. **Be specific** — say the audience, length, format, and constraints.
2. **System prompt** — set persona + rules + output format *once*, separate from
   the user's actual request.
3. **Few-shot** — when rules are hard to describe, *show* 2–3 examples instead.
4. **Chain-of-thought** — for reasoning, tell it to "think step by step" so it
   works the problem out before answering (a preview of module 02).

**Structured output:** to use a reply in code you need JSON, not prose. The
everyday recipe is two halves: **ask clearly** (a system prompt that says "return
ONLY JSON with these keys") and **parse defensively** (strip any stray ```` ```json ````
fence, then `json.loads`). The *bulletproof* way to force structure is **tool
use** (module 03), but ask-and-parse is what you'll use most of the time.

---

## Hands-on

> Setup done? You need your API key in `.env` (see [SETUP.md](../../SETUP.md)).

### Step 1 — The four prompting techniques

```bash
python modules/01-prompt-engineering/prompting_techniques.py
```

**Expected (wording varies; the *behavior* is the point):**

All four sections follow the same shape: the same underlying request, run
**WITHOUT** the technique and then **WITH** it, so you see the prompt *and*
both outputs side by side instead of trusting a claim about what would happen.

```
1 · Specific instructions
WITHOUT → a long, generic essay about dogs
WITH    → exactly 2 simple sentences for a 6-year-old

2 · System prompt (same user message both times)
WITHOUT → a long markdown report with headers, tables, even a fake code block
WITH    → exactly 3 terse bullets, no code (the system prompt forbade it)

3 · Few-shot (teach a CONVENTION, not the sentiment itself)
WITHOUT → model invents its own label scheme, e.g. "Sentiment: Positive 😊"
WITH    → model copies the exact scheme from the examples: "+1"

4 · Chain-of-thought
WITHOUT (blunt)       → $0.65 (or sometimes the $1.30 trap)
WITH (step-by-step)   → shows the algebra, then $0.65 ← correct
```

**On #3 (few-shot):** the point isn't that the model doesn't know "Best
purchase I have made all year" is positive — it already knows that. The point
is the *label scheme*. The example prompt asks for `+1`/`-1`/`0`, a convention
the model has no way to guess from the word "classify" alone. Zero-shot has to
invent something reasonable (`"Positive"`, often with a writeup). Few-shot, by
*showing* 3 examples that already use `+1`/`-1`/`0`, gets the model to copy
that exact scheme. That's few-shot's real job: teaching an arbitrary
convention that's faster to show than to describe — not teaching facts the
model already has.

**On #4 (chain-of-thought):** this uses a non-famous variant of the classic
bat-and-ball puzzle (not the literal "$1.10" version), because that exact
puzzle is so widely known the model may have it memorized — these numbers
force it to actually compute. If the model's blunt answer is right too, that's
fine: the lesson isn't "blunt is always wrong," it's that showing the work
lets *you* verify it instead of trusting a one-line answer.

### Step 2 — Reliable JSON for real programs

```bash
python modules/01-prompt-engineering/structured_output.py
```

**Expected:**

```
  input : Hey, this is Priya Nair from Acme Robotics — reach me at priya@acme.io anytime.
  parsed: name='Priya Nair'  email='priya@acme.io'  company='Acme Robotics'
  ...
✅ Done. Every reply parsed as valid JSON we can use in code.
```

Open [`structured_output.py`](structured_output.py) and read `parse_json()` —
that tiny "strip the code fence if present, then `json.loads`" helper is what
makes this robust instead of crash-prone.

---

## Try this

1. **Tighten a prompt.** Make `prompting_techniques.py`'s vague prompt produce a
   haiku. What constraints did you have to add?
2. **Change the convention.** In section 3, change the few-shot examples' scale
   from `+1/-1/0` to something else arbitrary, like `HAPPY`/`SAD`/`MEH` or
   `5/3/1`. Re-run — the model should pick up *your* new convention, because
   that's literally what the examples are teaching it.
3. **Extend the schema.** In `structured_output.py`, add a `"phone"` field to the
   system prompt and a messy input with a phone number. Re-run.
4. **See why defensive parsing matters.** In the system prompt, *remove* the
   "no markdown code fences" instruction and re-run. The model may now wrap its
   JSON in ```` ```json ```` — and `parse_json()` still handles it. Then try
   deleting the fence-stripping lines from `parse_json()` to watch it break.

---

## Recap

- The prompt is the program: be specific → system prompt → few-shot → chain-of-thought.
- Structured output (JSON via the **prefill** trick) turns an LLM into a callable
  component, which everything later relies on.

## Go deeper (one link)

- **[Anthropic's prompt engineering guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)** —
  the authoritative, Claude-specific reference (system prompts, examples, prefill, and more).

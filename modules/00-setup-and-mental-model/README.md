# Module 00 · Setup & Your First LLM Call

⏱️ **~45 minutes** (most of it one-time setup you never repeat)

> Goal: get your machine ready, make your first call to an LLM from code, and
> build a correct **mental model** of what an LLM actually is.

---

## What you'll learn

- How to set up the course once (Python environment, API key, optional local models).
- How to send a prompt to Claude from Python and get a reply.
- What an LLM *is* (and isn't) — the single most important idea in this whole course.
- What **tokens**, **context window**, and **temperature** mean.

## Why it matters

Almost everything later (RAG, agents, fine-tuning) is built on this one action:
*send text in, get text out*. If your mental model here is wrong, everything
downstream feels confusing. Ten minutes of mental-model now saves hours later.

---

## Mental model: an LLM is a *next-word predictor*, not a database

Imagine the world's most well-read autocomplete. You give it some text, and it
predicts the most plausible next chunk of text — over and over — based on
patterns it learned from a huge amount of writing.

That's it. A few consequences fall out of this, and they explain *most* "weird"
LLM behavior:

- **It doesn't "look things up."** It generates what *sounds* right. That's why
  it can be confidently wrong ("hallucinate"). Fixing this is literally what the
  RAG track (modules 04–07) is about.
- **It has no memory between calls.** Each call is fresh. Any "memory" you've
  seen in chat apps is just the previous conversation being re-sent every time.
  (We make this concrete in module 07.)
- **It's a predictor, so it's a bit random.** Run the same creative prompt twice
  and you may get different answers. The **temperature** dial controls how much.

Three words you'll hear constantly:

| Term | Plain meaning |
|------|---------------|
| **Token** | A piece of a word. The model reads and writes in tokens. ~1 token ≈ ¾ of a word. You pay per token, so tokens = cost. |
| **Context window** | The maximum amount of text (in tokens) the model can "see" at once — your prompt + its reply. Big but not infinite. |
| **Temperature** | Creativity dial. `0` = focused and repeatable. `1` = more varied and creative. |

---

## Hands-on

### Step 0 — One-time setup
Follow **[SETUP.md](../../SETUP.md)** in the project root first (create the
virtual environment, install packages, add your API key). Come back here when
`python -c "import anthropic"` runs without error.

### Step 1 — Run your first LLM call
From the **project root**, run:

```bash
python modules/00-setup-and-mental-model/hello_llm.py
```

**Expected output** (your wording will vary — that's the whole point):

```
======================================================================
Module 00 · Your first LLM call
======================================================================

[1/3] Checking your setup...
   Claude is reachable. It replied: 'ready'

[2/3] Asking Claude a question...
   Q: In one sentence, explain what a large language model is to a curious 12-year-old.
   A: A large language model is a computer program that has read an enormous
      amount of text and uses those patterns to predict and write words...

[3/3] Temperature demo — same prompt, three calls:
   Prompt: Write one sentence describing what it feels like to touch a cloud.

   temp=0  (run 1) →  Touching a cloud would feel like cool, damp mist —
                       so soft you can barely sense it against your skin.
   temp=0  (run 2) →  Touching a cloud would feel like cool, damp mist —
                       so soft you can barely sense it against your skin.  ← same

   temp=1  (call 1) →  Touching a cloud might feel like brushing cool silk
                       that melts the instant you reach for it.
   temp=1  (call 2) →  Touching a cloud would feel like sinking your hand
                       into chilled smoke — there, then gone.

   temp=0 locks onto one answer. temp=1 samples a different one each time.

✅ Done! You just used an LLM from your own code.
```

If you instead see a "Setup problem" message, read it — it tells you exactly
what to fix (usually the API key in `.env`).

### Step 2 — Read the code
Open [`hello_llm.py`](hello_llm.py). It's short and fully commented. Notice that
the actual LLM call is just **one line**: `claude(question, temperature=0)`.
Everything else is friendliness around it.

---

## Try this

1. **Feel the temperature.** Run the script 3 times. Notice `temperature=0`
   produces the *same* sentence every run, while `temperature=1.0` rewrites it
   differently each time. Why? At `0` the model always picks the single
   most-likely next token; at `1` it samples, so choices compound.
2. **Change the question.** Edit `question` in the script to something you're
   curious about and re-run.
3. **Break it on purpose.** Temporarily rename your `.env` to `.env.bak` and run
   the script. See how the error message guides you. Rename it back afterward.

---

## Recap

- An LLM is a **next-word predictor** trained on lots of text — not a database.
- That's why it can hallucinate, has no built-in memory, and is a little random.
- You send **tokens** in (within the **context window**) and **temperature**
  controls randomness.
- Calling it from code is one function call.

## Go deeper (one link)

- **[Anthropic Academy](https://www.anthropic.com/learn)** — free, official, and
  uses the exact same Claude API you just called. Start with their intro/prompting
  course.

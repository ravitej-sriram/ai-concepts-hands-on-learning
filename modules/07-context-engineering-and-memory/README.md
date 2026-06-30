# Module 07 · Context Engineering & Memory

⏱️ **~45 minutes** · 🖥️ **Claude only** (no Ollama needed)

> Goal: understand that an LLM's "memory" is something *you* construct by managing
> the context window — and learn the core moves of **context engineering**.

---

## What you'll learn

- Why the model has no memory, and how chat apps fake it by re-sending history.
- How a multi-turn conversation is just a growing `messages` list.
- **Context engineering**: deciding what to keep, summarize, or drop so you stay
  within the window (and budget) without losing the thread.

## Why it matters

Everything you build — chatbots, agents, RAG — runs through one bottleneck: the
**context window** (module 00). It's finite, and you pay per token in it. Knowing
what to put in it, and what to leave out, is arguably *the* skill of applied AI.
"Context engineering" has largely replaced "prompt engineering" as the thing pros
spend their time on.

---

## Mental model: a whiteboard you rewrite before every call

Each API call starts with a blank model. The only thing it knows is what's on the
**whiteboard** you hand it — the messages you send this time. So:

- **There is no hidden memory.** If you want the model to "remember" the user's
  name, that text must be on the whiteboard for *this* call.
- **A conversation is a list you keep appending to** (`user`, `assistant`,
  `user`, …) and re-send each turn. That's all "chat memory" is.
- **The whiteboard is finite.** Long conversations overflow it and cost more
  every turn. So you curate: keep recent turns verbatim, **summarize** older ones
  into compact notes, and drop irrelevant stuff.

Context engineering = managing that whiteboard well. RAG (Tracks 1) is one
instance: retrieve the few relevant chunks and put *those* on the whiteboard
instead of everything.

---

## Hands-on

> Claude key in `.env` is all you need.

```bash
python modules/07-context-engineering-and-memory/context_and_memory.py
```

**Expected shape:**

```
1 · The model has no memory between calls
   → asked "what is my name?" in a separate call, it says it doesn't know.

2 · 'Memory' is just re-sending the whole conversation
   → same question, but with the earlier turn included → "Your name is Sam, color teal."

3 · Context engineering: summarize old turns to stay small
   Compressed memory: "Sam, from Denver; vegetarian; planning a 2-week Japan trip
   in October, ~$4000; wants hiking + food tips."
   → continues helpfully using only that short summary, not the full transcript.
```

Section 1 vs 2 is the lightbulb: the *only* difference is whether the earlier
turn was included in the list you sent.

---

## Try this

1. **Watch the list grow.** Add a `print(len(conversation))` after each append in
   section 2. Every turn adds two entries (your message + the reply) — and all of
   it gets re-sent next time.
2. **Summarize vs. truncate.** In section 3, instead of summarizing, try just
   keeping the last sentence of `long_history`. Notice how summarization preserves
   key facts that naive truncation would throw away.
3. **Budget it.** Ask the model to keep the memory under 25 words. How much detail
   survives? This is the real trade-off: smaller context = cheaper but lossy.

---

## Recap

- No hidden memory: "chat memory" = re-sending a growing `messages` list.
- The context window is finite and metered, so you **curate** it.
- **Context engineering** — keep / summarize / drop — is the central skill, and
  RAG is one application of it.

## Go deeper (one link)

- **[Anthropic — Context engineering / managing context](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)** —
  how to think about what belongs in the window, especially for agents.

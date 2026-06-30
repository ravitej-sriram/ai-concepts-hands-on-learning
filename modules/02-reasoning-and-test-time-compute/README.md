# Module 02 · Reasoning Models, Extended Thinking & Test-Time Compute

⏱️ **~40 minutes**

> Goal: understand the second big way to make a model "smarter" — not training a
> bigger model, but letting it **spend more compute thinking at answer-time** —
> and learn when that's worth the cost.

---

## What you'll learn

- What "test-time compute" (a.k.a. inference-time / test-time scaling) means.
- The difference between a **fast** answer and an **extended-thinking** answer.
- When reasoning is worth the extra latency and money — and when it's waste.

## Why it matters

For years, "smarter" meant "train a bigger model." Since 2024–25 there's a second
dial: let the model **reason longer before answering**. Smaller models with more
thinking time can beat bigger models that answer instantly — on the right
problems. Knowing which dial to turn is a core cost/quality decision in real apps.

---

## Mental model: thinking time is a dial, not a default

Two ways to get a better answer:

| Dial | What you change | Cost |
|---|---|---|
| **Train-time compute** | A bigger/better-trained model | Paid by the model maker; you just pick the model |
| **Test-time compute** | Let *this* call reason longer before replying | You pay per call (more tokens, more latency) |

Chain-of-thought from module 01 ("think step by step") was a manual taste of
this. **Extended thinking** is the built-in version: the model gets a private
scratchpad, reasons, then answers — and you can see both.

The judgment call: **hard, multi-step problems** (math, planning, tricky logic,
careful code) often justify the extra compute. **Simple lookups and short
rewrites** do not — there you're just paying more for the same answer. Many
production systems *route*: cheap/fast model by default, escalate to a reasoning
model only when needed (we build exactly this in module 18).

---

## Hands-on

> Needs your API key in `.env`. Uses `claude_think(...)` from `shared/llm.py`,
> which turns on extended thinking and returns both the reasoning and the answer.

```bash
python modules/02-reasoning-and-test-time-compute/thinking_vs_fast.py
```

**Expected shape (exact text varies):**

```
A · FAST mode (no extended thinking)
   Prompt: ...snail in a 30-foot well... gut-instinct answer as just a day number.
   Output: 27   (or 28 — some number that ISN'T 29)

B · THINKING mode (extended thinking / more test-time compute)
   (peek at the model's private reasoning: Let me track the snail's position...)
   Final answer: a day-by-day table that accounts for the day-5 wind, ending FINAL: 29

C · The trade-off
   ...explanation of when the extra compute is worth it...
```

This is a snail-in-a-well puzzle with a deliberate **twist**: a one-time wind
setback on day 5. The plain version of this puzzle is famous enough that a
model can recall its shortcut formula and answer correctly without any real
reasoning — which would make this demo show nothing. The twist forces actual
day-by-day simulation. A gut-instinct FAST answer tends to apply the familiar
formula and miss the twist (landing on some wrong number); THINKING mode has
room to simulate day-by-day and catch it, reliably landing on the correct
answer, **29**. If FAST also lands on 29, that's fine — the lesson isn't
"fast is always wrong," it's that thinking mode verifies instead of
pattern-matching, which is what the extra tokens are paying for.

---

## Try this

1. **Waste it on purpose.** Change `puzzle` to `"What is the capital of France?"`
   and re-run. Notice thinking mode spends tokens reasoning about a trivial
   question — that's the "when NOT to use it" lesson, made concrete.
2. **Tune the budget.** Lower `thinking_budget` to `1024` and raise it to `4000`.
   Does more budget change the answer on the puzzle? (It must stay below
   `max_tokens`.)
3. **Find your own hard problem.** Give it a logic puzzle you know the answer to
   and compare fast vs. thinking.

---

## Recap

- "Smarter" has two dials: a better model (**train-time**) or more reasoning per
  call (**test-time compute**).
- Extended thinking gives the model a scratchpad; it shines on hard, multi-step
  problems and wastes money on easy ones.
- Real systems route between fast and thinking models (module 18).

## Go deeper (one link)

- **[Anthropic — Extended thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)** —
  how it works, the `thinking` parameter, budgets, and best practices.

# Module 03 · Tool Use / Function Calling

⏱️ **~50 minutes**

> Goal: let the model use **your** Python functions to do things it can't do on
> its own (math, look things up, call APIs). This is the foundation of every
> agent in Track 2.

---

## What you'll learn

- What "tool use" (a.k.a. function calling) really is — and what it *isn't*.
- The four-step tool-use loop, implemented by hand so nothing is magic.
- How to expose your own functions to the model safely.

## Why it matters

An LLM alone can't reliably do arithmetic, look up today's data, or act on the
world — it just predicts text (module 00). Tool use fixes this: you give the
model a menu of functions, it decides which to call and with what arguments, and
**your code** runs them. Reason → act → observe → repeat **is** an agent
(module 08); this module is that loop in its simplest form.

---

## Mental model: the model orders, the kitchen cooks

The model is a customer reading a menu. It can't cook — it can only **place an
order**: "call `get_price` with `product='gizmo'`." Your program is the kitchen:
it runs the real function and brings back the dish (the result). The model never
runs your code; it only asks. You stay in control of what actually executes.

The loop, every time:

1. **You** send the question + a list of tool descriptions (name, purpose, inputs).
2. **Model** replies either with a final answer, or `stop_reason="tool_use"` plus
   which tool(s) to call and the arguments.
3. **You** run the real Python function and send back a `tool_result`.
4. **Model** uses the result to answer — or asks for another tool. Repeat until
   it's done.

Two things to internalize:
- **The model only sees your *descriptions***, not your code. Clear names and
  descriptions = correct tool calls.
- **You execute the tools**, so you decide what's allowed. (Note our calculator
  uses a tiny *safe* evaluator, not Python's dangerous `eval`.)

---

## Hands-on

> Needs your API key in `.env`.

```bash
python modules/03-tool-use/tool_use.py
```

**Expected shape (numbers exact, phrasing varies):**

```
WITHOUT tools
   Prompt: How much do 3 gizmos and 2 widgets cost in total?
   Output: I don't have any pricing information for gizmos or widgets...
           Could you share the cost of each item?

WITH tools (the reason→act→observe loop in action)
   Prompt: How much do 3 gizmos and 2 widgets cost in total?
   🔧 model called get_price({'product': 'gizmo'}) → $7.25
   🔧 model called get_price({'product': 'widget'}) → $4.50
   🔧 model called calculator({'expression': '3 * 7.25 + 2 * 4.50'}) → 30.75
   A: Total: $30.75

A second example — chained tool calls
   Prompt: What's 15% of the price of a gadget?
   🔧 model called get_price({'product': 'gadget'}) → $12.00
   🔧 model called calculator({'expression': '12.00 * 0.15'}) → 1.7999...
   A: $1.80
```

Without tools the model is genuinely stuck — it can't look up your private
catalog, so it asks you for the prices instead. With tools, it plans the
steps itself: look up prices first, then compute. You didn't tell it the
order; it figured that out from the tool descriptions alone.

Open [`tool_use.py`](tool_use.py) and read `ask_with_tools()` — the `while` loop
*is* the four steps above.

---

## Try this

1. **Add a tool.** Write an `apply_discount(price, percent)` function, add its
   description to `TOOLS` and the function to `TOOL_IMPLEMENTATIONS`, then ask a
   question that needs it.
2. **Break the description.** Rename `get_price`'s description to something vague
   ("does stuff with products"). Does the model still call it correctly? This
   shows how much the *description* matters.
3. **Watch it chain.** Ask: "If I buy one of everything and there's 8% tax, what's
   the total?" Count how many tool calls it makes.

---

## Recap

- Tool use = the model *requests* function calls; **your** code runs them and
  returns results.
- The model sees only your tool **descriptions**, so write them clearly.
- The reason→act→observe loop here is the seed of agents (module 08).

## Go deeper (one link)

- **[Anthropic — Tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview)** —
  the full reference: schemas, parallel tool calls, forcing a tool, and streaming.

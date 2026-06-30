# Module 05 · RAG from Scratch

⏱️ **~55 minutes** · 🖥️ **needs Ollama** (embeddings) **+ Claude** (answers)

> Goal: build the full **Retrieval-Augmented Generation** pipeline by hand and
> watch it turn a model that *guesses* into one that *answers correctly from your
> documents*.

---

## What you'll learn

- The four stages of RAG: **chunk → embed/store → retrieve → generate**.
- How to **ground** a model's answer in retrieved text (and tell it to say "I
  don't know" when the answer isn't there).
- Why RAG is the standard fix for hallucination and for private/up-to-date data.

## Why it matters

This is probably the single most useful pattern in applied AI. Most "chat with
your docs / your codebase / your company wiki" products are RAG underneath. It
also directly attacks the module 00 problem: an LLM makes things up because it's
predicting plausible text. RAG hands it the *real* facts to predict from.

---

## Mental model: open-book exam

A raw LLM answering from memory is a student taking a **closed-book** exam — it
recalls what it can and bluffs the rest (hallucination). RAG turns it into an
**open-book** exam:

1. **Chunk** your documents into bite-sized pieces (module 04's reason: you feed
   the model only the relevant bits, not the whole book).
2. **Embed & store** every chunk as a vector (module 04).
3. **Retrieve**: embed the question, pull the few most similar chunks.
4. **Generate**: paste those chunks into the prompt and ask the model to answer
   *using only them*.

The model's job shifts from "remember the answer" to "read these notes and
respond" — which it's extremely good at.

---

## Hands-on

> Needs Ollama running with `nomic-embed-text` pulled (see module 04 setup) and
> your Claude key in `.env`.

The knowledge base is [`knowledge.md`](knowledge.md) — facts about a **fictional**
"Lumina X1" e-bike. Because it's invented, the model *cannot* know it from
training, so the with/without-RAG contrast is crystal clear.

```bash
python modules/05-rag-from-scratch/rag_from_scratch.py
```

**Expected shape:**

```
Indexing 5 chunks from knowledge.md...

Q: What is the range of the Lumina X1 in Eco mode?
[WITHOUT RAG] (model's memory only):
   I don't have specific information about the "Lumina X1"... (it can't know)
[WITH RAG] (grounded in retrieved chunks):
   In Eco mode, the Lumina X1 has a tested range of 95 kilometers per charge.

Q: How much does the Lumina X1 cost and what warranty does it include?
[WITHOUT RAG]:
   I'm not able to find reliable details on that model...
[WITH RAG]:
   It retails for $2,480, with a 3-year frame warranty and 2-year battery/
   electronics warranty (registered owners get +12 months battery coverage).
```

The "without" answers admit ignorance or hedge; the "with" answers are specific
and correct — pulled from your file, not the model's memory.

---

## Try this

1. **Edit the facts.** Change the price in `knowledge.md` to `$1,999` and re-run.
   The RAG answer updates instantly — no retraining. That's the superpower.
2. **Ask something not in the doc** ("Does the Lumina X1 have a phone holder?").
   A good RAG prompt makes the model say it doesn't know instead of inventing.
3. **Break retrieval on purpose.** Set `k=1` in `answer_with_rag` and ask the
   cost+warranty question (the answer spans two chunks). Watch quality drop — a
   preview of why module 06's smarter retrieval matters.
4. **Bring your own doc.** Replace `knowledge.md` with a markdown file of your own
   and ask questions about it.

---

## Recap

- RAG = **chunk → embed/store → retrieve → generate**.
- Grounding the model in retrieved text fixes hallucination and gives it private,
  current knowledge — with no retraining.
- Retrieval quality is everything; module 06 upgrades it.

## Go deeper (one link)

- **[Chroma — RAG / getting started](https://docs.trychroma.com/)** — when you
  outgrow our NumPy store, Chroma is a popular real vector DB with the same
  add/query model you just built by hand.

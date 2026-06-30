# Module 06 · Advanced RAG ⏱️

⏱️ **~75 minutes** (the first "longer than an hour" module) · 🖥️ **needs Ollama + Claude**

> Goal: upgrade the *retrieval* step from module 05 with **hybrid search** and
> **re-ranking**, and — most importantly — learn to **measure** whether retrieval
> is actually working.

---

## What you'll learn

- Why pure vector search misses things, and how **hybrid search** (meaning +
  keywords) fixes it.
- **Re-ranking**: using a smart model to reorder candidates so the best chunks
  land on top.
- How to **evaluate retrieval** with a simple, honest metric instead of vibes.

## Why it matters

In a RAG app, **generation can't be better than retrieval** — if the right chunk
never makes it into the prompt, the model can't answer (or it hallucinates).
Most "our RAG bot gives bad answers" problems are actually *retrieval* problems.
So the highest-leverage skill is measuring and improving retrieval.

---

## Mental model: a funnel, and a scoreboard

Good retrieval is a **funnel**: cast a wide net, then narrow to the best few.

1. **Hybrid search** casts the net. Vectors capture *meaning* but can fumble
   exact tokens (product codes, version numbers like `3.4.1`, names, emails).
   Keyword search nails exact tokens but misses paraphrases. Blend both and you
   get the strengths of each. (We normalize each score to 0–1 and combine with a
   weight `alpha`.)
2. **Re-ranking** narrows the net. Take the top handful of candidates and ask a
   capable model "which of these actually answer the question?" It reorders them;
   you keep the best 2–3 for the final prompt.
3. **Evaluation** is the **scoreboard**. For a set of questions where you know
   the answer, check: did retrieval surface the chunk containing it? Count the
   hits. Now "did my change help?" has a number, not an opinion.

---

## Hands-on

> Uses module 05's [`knowledge.md`](../05-rag-from-scratch/knowledge.md). Needs
> Ollama running (`nomic-embed-text`) and your Claude key.

```bash
python modules/06-advanced-rag/advanced_rag.py
```

**Expected shape (exact hits can vary by a point):**

```
Indexing 7 chunks...

Q: What is the current firmware version?
   naive vector   : ✗ missed (needed '3.4.1')
   hybrid+rerank  : ✓ found
Q: How often should I lubricate the chain?
   naive vector   : ✓ found (needed '250')
   hybrid+rerank  : ✓ found
...
======================================================================
Retrieval score — naive: 2/4   hybrid+rerank: 4/4
======================================================================
```

The exact-token questions (firmware `3.4.1`, the support email) are where pure
vector search tends to slip and hybrid+rerank pulls ahead. The number at the
bottom is the point of the whole module: you can now *prove* an improvement.

---

## Try this

1. **Slide the dial.** In `hybrid_search`, try `alpha=1.0` (pure vector) and
   `alpha=0.0` (pure keyword) and re-run the eval. Which questions does each get
   right? Neither extreme wins them all — that's why we blend.
2. **Remove the re-ranker.** Compare hybrid-only (skip `llm_rerank`) vs
   hybrid+rerank. Does reranking change the score on this small set?
3. **Grow the scoreboard.** Add two more `(question, needle)` pairs to
   `eval_set`. A bigger eval set makes the comparison more trustworthy.
4. **Stress it.** Add several unrelated paragraphs to `knowledge.md` (noise) and
   see whether naive retrieval degrades faster than hybrid+rerank.

---

## Recap

- **Hybrid search** = meaning (vectors) + exact tokens (keywords); better than
  either alone.
- **Re-ranking** reorders the top candidates so the best chunks make the prompt.
- **Evaluate retrieval** with a hit-rate metric — generation can't fix what
  retrieval missed.

## Go deeper (one link)

- **[DeepLearning.AI — Advanced Retrieval for AI with Chroma](https://www.deeplearning.ai/short-courses/advanced-retrieval-for-ai/)** —
  a free short course on query expansion, re-ranking, and evaluating retrieval.

# Module 04 · Embeddings & Semantic Search

⏱️ **~45 minutes** · 🖥️ **needs Ollama** (free, local — see setup below)

> Goal: understand **embeddings** — turning text into vectors that capture
> meaning — and use them to search by *meaning* instead of keywords. This is the
> engine under RAG (module 05).

---

## What you'll learn

- What an embedding is (a vector of numbers representing meaning).
- How **cosine similarity** measures "do these two texts mean similar things?"
- How to build **semantic search** that finds relevant text with zero keyword overlap.

## Why it matters

LLMs don't know your private documents. To feed them the *right* snippet at the
right time (RAG), you first need to **find** that snippet by meaning. Embeddings
are how. Search-by-meaning also powers recommendations, deduplication, clustering,
and the "second brain" capstone (module 20).

---

## One-time setup: install Ollama (free, runs locally)

Embeddings here run on your Mac for free via Ollama — no API cost.

```bash
# 1. Install Ollama (pick one):
brew install ollama          # if you use Homebrew
#   ...or download the app from https://ollama.com

# 2. Make sure it's running (open the app, or in a terminal):
ollama serve                 # leave this running, or just open the Ollama app

# 3. Pull the small embedding model this module uses:
ollama pull nomic-embed-text
```

If Ollama isn't running, the script prints a friendly message telling you so.

---

## Mental model: meaning becomes a location in space

An embedding model reads text and outputs a long list of numbers — a **vector**.
Think of each vector as a *location* in a huge multi-dimensional space where
**things that mean similar stuff sit close together**. "a happy dog" and "a
joyful puppy" land near each other; "the stock market fell" lands far away —
even though "happy dog" and "joyful puppy" share no words.

To compare two vectors we use **cosine similarity**: do they point the same
direction?

- `1.0` → same meaning · `~0.0` → unrelated · `-1.0` → opposite.

**Semantic search** is then simple: embed your query, embed your documents, and
return the documents whose vectors are closest to the query's. No keyword
matching — it finds meaning.

---

## Hands-on

```bash
python modules/04-embeddings-and-semantic-search/embeddings_and_search.py
```

**Expected shape (exact numbers vary by model version):**

```
1 · What an embedding looks like
'a happy dog' → a vector of 768 numbers.
First 8 of them: [0.021, -0.044, ...] ...

2 · Meaning, not keywords
   0.78   'a happy dog'  vs  'a joyful puppy'          ← high (same idea)
   0.31   'a happy dog'  vs  'the stock market fell'   ← low (unrelated)
   0.74   'how do I reset my password' vs 'I forgot my login credentials'

3 · Semantic search
Query: 'What should I eat to stay healthy?'
   0.66   A balanced diet includes fruits, vegetables, and whole grains.
   0.55   Regular exercise improves cardiovascular health.
   0.21   The capital of Japan is Tokyo.
   ...
```

The lesson lives in section 3: the diet/health facts rank top despite sharing
almost no words with the question. That's meaning-based retrieval.

---

## Try this

1. **Probe the space.** Add your own pairs to section 2 — e.g. `"cat"` vs
   `"feline"`, `"car"` vs `"automobile"`, `"car"` vs `"banana"`. Do the scores
   match your intuition?
2. **Trick keyword search, not meaning.** Add the document
   `"Avoid junk food and sugary drinks."` and re-run. It should rank high for the
   health query despite zero shared words with "eat / healthy".
3. **Change the query** to `"Where are famous landmarks?"` and watch the ranking
   reshuffle toward the Eiffel Tower / Tokyo facts.

---

## Recap

- An **embedding** turns text into a vector that encodes meaning.
- **Cosine similarity** scores how aligned two meanings are.
- **Semantic search** = embed query + docs, return the closest docs. This is the
  retrieval half of RAG.

## Go deeper (one link)

- **[Hugging Face — Sentence Embeddings / Sentence Transformers](https://huggingface.co/blog/getting-started-with-embeddings)** —
  a clear, hands-on intro to embeddings and similarity.

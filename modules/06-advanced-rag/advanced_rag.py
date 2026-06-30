"""
Module 06 · advanced_rag.py — make the *retrieval* step much smarter.

Run from the project root (needs Ollama + Claude):
    python modules/06-advanced-rag/advanced_rag.py

Module 05 retrieved with pure vector search. Real systems do better:
  • HYBRID search  — combine meaning (vectors) with exact keywords.
  • RE-RANKING     — ask a smart model to reorder the top candidates.
  • EVALUATION     — actually MEASURE whether retrieval found the answer.

We build all three on the same fictional e-bike knowledge base from module 05.
"""

import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.llm import claude, SetupError
from shared.rag import TinyVectorStore, chunk_text, cosine_similarity
import numpy as np

_JUDGE_OUTPUT_PATH = os.environ.get("JUDGE_OUTPUT_PATH")
_exercises: list[dict] = []

# Reuse module 05's knowledge base instead of duplicating it.
KNOWLEDGE_FILE = Path(__file__).resolve().parents[1] / "05-rag-from-scratch" / "knowledge.md"

_STOPWORDS = {"the", "a", "an", "is", "of", "in", "to", "and", "for", "what",
              "how", "do", "i", "my", "does", "it", "on", "with", "are"}


def keyword_score(query: str, text: str) -> float:
    """Simple keyword overlap: fraction of the query's meaningful words present."""
    q_words = {w.strip("?.,").lower() for w in query.split()} - _STOPWORDS
    if not q_words:
        return 0.0
    t_words = {w.strip("?.,").lower() for w in text.split()}
    return len(q_words & t_words) / len(q_words)


def _normalize(scores: list[float]) -> list[float]:
    """Scale a list of scores to 0..1 so we can fairly combine different methods."""
    lo, hi = min(scores), max(scores)
    if hi == lo:
        return [0.0 for _ in scores]
    return [(s - lo) / (hi - lo) for s in scores]


class HybridStore(TinyVectorStore):
    """A vector store that ALSO supports hybrid (vector + keyword) search."""

    def hybrid_search(self, query: str, *, k: int = 3, alpha: float = 0.5) -> list[dict]:
        """alpha=1.0 → pure vector, 0.0 → pure keyword, 0.5 → equal blend."""
        q_vec = np.array(self.embed_fn(query), dtype=float)
        vec_scores = [cosine_similarity(q_vec, v) for v in self._vectors]
        kw_scores = [keyword_score(query, t) for t in self._texts]
        vn, kn = _normalize(vec_scores), _normalize(kw_scores)
        combined = [
            {"text": t, "score": alpha * v + (1 - alpha) * k_}
            for t, v, k_ in zip(self._texts, vn, kn)
        ]
        combined.sort(key=lambda r: r["score"], reverse=True)
        return combined[:k]


def llm_rerank(query: str, candidates: list[str], *, k: int = 2) -> list[str]:
    """
    Ask Claude to reorder candidate chunks by true relevance and keep the best k.
    A small, fast model is great at this 'which of these actually answers it?' job.
    """
    listing = "\n".join(f"[{i}] {c}" for i, c in enumerate(candidates))
    prompt = (
        f"Question: {query}\n\nCandidate passages:\n{listing}\n\n"
        f"Reply with ONLY the numbers of the {k} most relevant passages, best "
        "first, comma-separated (e.g. '2,0'). No other text."
    )
    reply = claude(prompt, temperature=0, max_tokens=30)
    order = []
    for tok in reply.replace(" ", "").split(","):
        if tok.isdigit() and int(tok) < len(candidates):
            order.append(int(tok))
    # Fall back to original order if the model said something unexpected.
    order = order or list(range(len(candidates)))
    return [candidates[i] for i in order[:k]]


def context_has(chunks: list[str], needle: str) -> bool:
    """Did retrieval surface the chunk containing the expected answer?"""
    return any(needle.lower() in c.lower() for c in chunks)


def main() -> None:
    text = KNOWLEDGE_FILE.read_text()
    chunks = chunk_text(text, words_per_chunk=45, overlap=10)
    store = HybridStore()
    print(f"Indexing {len(chunks)} chunks...\n")
    store.add_many(chunks)

    # An evaluation set: question → a string that MUST appear in the retrieved
    # context for retrieval to count as a success. This is how you measure RAG.
    eval_set = [
        ("What is the current firmware version?", "3.4.1"),
        ("How often should I lubricate the chain?", "250"),
        ("What's the Eco mode range?", "95"),
        ("How do I contact customer support?", "support@luminacycles.example"),
    ]

    naive_hits = smart_hits = 0
    for question, needle in eval_set:
        # Strategy A: naive pure-vector top-2 (what module 05 did).
        naive = [h["text"] for h in store.search(question, k=2)]
        # Strategy B: hybrid top-4, then LLM-rerank down to the best 2.
        wide = [h["text"] for h in store.hybrid_search(question, k=4, alpha=0.5)]
        smart = llm_rerank(question, wide, k=2)

        a_ok, b_ok = context_has(naive, needle), context_has(smart, needle)
        naive_hits += a_ok
        smart_hits += b_ok
        print(f"Q: {question}")
        print(f"   naive vector   : {'✓ found' if a_ok else '✗ missed'} (needed {needle!r})")
        print(f"     top chunk: {naive[0][:90]!r}")
        print(f"   hybrid+rerank  : {'✓ found' if b_ok else '✗ missed'}")
        print(f"     top chunk: {smart[0][:90]!r}")

    n = len(eval_set)
    final_score = f"naive: {naive_hits}/{n}   hybrid+rerank: {smart_hits}/{n}"
    print("\n" + "=" * 70)
    print(f"Retrieval score — {final_score}")
    print("=" * 70)
    print("This is the real lesson: don't guess if retrieval is good — MEASURE it,")
    print("then improve the retriever. (Generation quality can't beat bad retrieval.)")

    _exercises.append({"id": "hybrid_vs_naive", "final_score": final_score})
    if _JUDGE_OUTPUT_PATH:
        Path(_JUDGE_OUTPUT_PATH).write_text(json.dumps(_exercises, indent=2))


if __name__ == "__main__":
    try:
        main()
    except SetupError as e:
        print("\n⚠️  Setup problem:\n")
        print(str(e))
        sys.exit(2)

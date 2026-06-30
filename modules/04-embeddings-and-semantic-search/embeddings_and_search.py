"""
Module 04 · embeddings_and_search.py — turn meaning into numbers, search by meaning.

Run from the project root (needs Ollama — see the README):
    python modules/04-embeddings-and-semantic-search/embeddings_and_search.py

An "embedding" is a list of numbers (a vector) that captures the MEANING of a
piece of text. Texts with similar meaning get similar vectors — even if they
share no words. This script proves that, then contrasts keyword search (which
FAILS on meaning-only queries) with semantic search (which SUCCEEDS).
"""

import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.llm import embed_local, SetupError
from shared.rag import cosine_similarity
import numpy as np

_JUDGE_OUTPUT_PATH = os.environ.get("JUDGE_OUTPUT_PATH")
_exercises: list[dict] = []

_STOPWORDS = {"what", "should", "i", "to", "the", "a", "an", "is", "of", "in",
              "and", "for", "do", "me", "be", "stay", "how", "does", "it"}


def keyword_score(query: str, text: str) -> float:
    """Fraction of query's non-stopword tokens that appear verbatim in the text."""
    q_words = {w.strip("?.,!").lower() for w in query.split()} - _STOPWORDS
    if not q_words:
        return 0.0
    t_words = {w.strip("?.,!").lower() for w in text.split()}
    return len(q_words & t_words) / len(q_words)


def main() -> None:
    # 1) An embedding is just a vector of numbers. Let's look at one.
    print("=" * 70)
    print("1 · What an embedding looks like")
    print("=" * 70)
    vec = embed_local("a happy dog")
    print(f"'a happy dog' → a vector of {len(vec)} numbers.")
    print(f"First 8 of them: {[round(x, 3) for x in vec[:8]]} ...")

    # 2) Similar MEANING → similar vectors, even with different words.
    print("\n" + "=" * 70)
    print("2 · Meaning, not keywords (cosine similarity: 1.0 = identical meaning)")
    print("=" * 70)
    pairs = [
        ("a happy dog", "a joyful puppy"),       # same idea, different words → HIGH
        ("a happy dog", "the stock market fell"), # unrelated → LOW
        ("how do I reset my password", "I forgot my login credentials"),  # HIGH
    ]
    for a, b in pairs:
        sim = cosine_similarity(np.array(embed_local(a)), np.array(embed_local(b)))
        print(f"   {sim:.3f}   {a!r}  vs  {b!r}")

    # 3) Keyword vs. semantic search — same query, same documents.
    #    The query shares NO meaningful words with the correct answer, so keyword
    #    search MUST return zero everywhere and semantic search MUST find the right
    #    docs. The contrast is structural, not coincidental.
    print("\n" + "=" * 70)
    print("3 · Keyword search vs. semantic search — same query, same documents")
    print("=" * 70)
    documents = [
        "The Eiffel Tower is located in Paris, France.",
        "Photosynthesis lets plants convert sunlight into energy.",
        "A balanced diet includes fruits, vegetables, and whole grains.",
        "The capital of Japan is Tokyo.",
        "Regular exercise improves cardiovascular health.",
    ]
    query = "What should I eat to stay healthy?"
    print(f"Query: {query!r}\n")

    # Keyword match: score each doc by how many query words it contains verbatim.
    kw_ranked = sorted(
        ({"doc": d, "score": keyword_score(query, d)} for d in documents),
        key=lambda r: r["score"], reverse=True,
    )
    print("  [KEYWORD MATCH] — word overlap between query and document:")
    kw_lines = []
    for r in kw_ranked:
        line = f"   {r['score']:.3f}   {r['doc']}"
        print(line)
        kw_lines.append(line)
    print("  ↑ All zeros — 'eat', 'stay', 'healthy' don't appear verbatim in any document.")

    # Semantic search: embed both query and docs, rank by cosine similarity.
    print()
    doc_vecs = [np.array(embed_local(d)) for d in documents]
    q_vec = np.array(embed_local(query))
    sem_ranked = sorted(
        ({"doc": d, "score": cosine_similarity(q_vec, v)} for d, v in zip(documents, doc_vecs)),
        key=lambda r: r["score"], reverse=True,
    )
    print("  [SEMANTIC SEARCH] — ranked by meaning, not words:")
    for r in sem_ranked:
        print(f"   {r['score']:.3f}   {r['doc']}")
    print("  ↑ Diet and exercise rise to the top — no shared words required.")
    print("    This is what makes RAG powerful: retrieve by meaning, not keyword.")

    print("\n✅ Done. Next: module 05 uses this to answer questions from your own docs.")

    _exercises.append({
        "id": "semantic_vs_keyword",
        "keyword_results": "\n".join(kw_lines),
        "semantic_top": sem_ranked[0]["doc"],
    })
    if _JUDGE_OUTPUT_PATH:
        Path(_JUDGE_OUTPUT_PATH).write_text(json.dumps(_exercises, indent=2))


if __name__ == "__main__":
    try:
        main()
    except SetupError as e:
        print("\n⚠️  Setup problem:\n")
        print(str(e))
        sys.exit(2)

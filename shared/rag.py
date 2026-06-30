"""
shared/rag.py — a tiny, readable vector store you can actually understand.

Real apps use a vector database (Chroma, pgvector, Pinecone, ...). But those
hide the mechanics behind a library. Here we implement the whole idea in ~40
lines of NumPy so you can SEE what a vector store does:

    • store some texts, each turned into a vector (an "embedding")
    • given a query, find the stored texts whose vectors point the same way

Used by the RAG modules (05, 06) and the second-brain capstone (20).
"""

from __future__ import annotations

import numpy as np

from shared.llm import embed_local


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    How aligned are two vectors? 1.0 = same direction (very similar meaning),
    0.0 = unrelated, -1.0 = opposite. This is THE core operation of search-by-meaning.
    """
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1.0  # avoid divide-by-zero
    return float(np.dot(a, b) / denom)


def chunk_text(text: str, *, words_per_chunk: int = 120, overlap: int = 20) -> list[str]:
    """
    Split a long document into smaller overlapping pieces ("chunks").

    Why chunk? You retrieve and feed the model only the relevant pieces, not a
    whole book. Overlap keeps sentences from being awkwardly cut between chunks.
    We split by words here for simplicity; real systems often split by sentences
    or paragraphs.
    """
    words = text.split()
    if not words:
        return []
    step = max(1, words_per_chunk - overlap)
    chunks = []
    for start in range(0, len(words), step):
        chunk = words[start:start + words_per_chunk]
        chunks.append(" ".join(chunk))
        if start + words_per_chunk >= len(words):
            break
    return chunks


class TinyVectorStore:
    """An in-memory store of (text, embedding) pairs with similarity search."""

    def __init__(self, embed_fn=embed_local):
        # embed_fn turns a string into a vector. Defaults to the free local
        # Ollama embedder, but you could pass any function with the same shape.
        self.embed_fn = embed_fn
        self._texts: list[str] = []
        self._vectors: list[np.ndarray] = []

    def add(self, text: str) -> None:
        """Embed one piece of text and remember it."""
        self._texts.append(text)
        self._vectors.append(np.array(self.embed_fn(text), dtype=float))

    def add_many(self, texts: list[str]) -> None:
        for t in texts:
            self.add(t)

    def __len__(self) -> int:
        return len(self._texts)

    def search(self, query: str, *, k: int = 3) -> list[dict]:
        """
        Return the k stored texts most similar in meaning to `query`,
        as a list of {"text", "score"} dicts, best first.
        """
        if not self._texts:
            return []
        q = np.array(self.embed_fn(query), dtype=float)
        scored = [
            {"text": text, "score": cosine_similarity(q, vec)}
            for text, vec in zip(self._texts, self._vectors)
        ]
        scored.sort(key=lambda r: r["score"], reverse=True)
        return scored[:k]

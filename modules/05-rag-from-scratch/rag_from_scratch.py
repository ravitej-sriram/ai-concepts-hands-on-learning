"""
Module 05 · rag_from_scratch.py — answer questions from YOUR documents.

Run from the project root (needs Ollama for embeddings + Claude for answers):
    python modules/05-rag-from-scratch/rag_from_scratch.py

RAG = Retrieval-Augmented Generation. The whole pipeline, by hand:
    chunk  →  embed & store  →  retrieve relevant chunks  →  generate an answer
              (module 04)        (search by meaning)         (Claude, grounded)

The demo asks about a FICTIONAL e-bike. First we ask Claude with NO context
(watch it admit it doesn't know / guess), then WITH retrieved context (watch it
answer correctly). Same model — the difference is entirely the retrieval.
"""

import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.llm import claude, SetupError
from shared.rag import TinyVectorStore, chunk_text

KNOWLEDGE_FILE = Path(__file__).parent / "knowledge.md"

_JUDGE_OUTPUT_PATH = os.environ.get("JUDGE_OUTPUT_PATH")
_exercises: list[dict] = []


def build_store() -> TinyVectorStore:
    """Load the document, split it into chunks, and embed them into a store."""
    text = KNOWLEDGE_FILE.read_text()
    chunks = chunk_text(text, words_per_chunk=60, overlap=15)
    store = TinyVectorStore()
    print(f"Indexing {len(chunks)} chunks from {KNOWLEDGE_FILE.name}...")
    store.add_many(chunks)
    return store


def answer_without_rag(question: str) -> str:
    """Ask Claude with no extra context — it can only use its training."""
    return claude(question, temperature=0, max_tokens=200)


def answer_with_rag(question: str, store: TinyVectorStore) -> tuple[str, str]:
    """Retrieve the most relevant chunks, then ask Claude grounded in them.
    Returns (context_used, answer) so the caller can print what was retrieved."""
    hits = store.search(question, k=3)
    chunks = [h["text"] for h in hits]
    context = "\n\n".join(f"- {c}" for c in chunks)

    # The key move: put the retrieved context in the prompt and instruct the
    # model to answer ONLY from it (and to admit when it's not there).
    prompt = (
        "Use ONLY the context below to answer the question. "
        "If the answer isn't in the context, say you don't know.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )
    return context, claude(prompt, temperature=0, max_tokens=200)


def main() -> None:
    store = build_store()

    questions = [
        "What is the range of the Lumina X1 in Eco mode?",
        "How much does the Lumina X1 cost and what warranty does it include?",
    ]

    for qi, q in enumerate(questions):
        print("\n" + "=" * 70)
        print("Q:", q)
        print("=" * 70)

        without = answer_without_rag(q)
        print("\n[WITHOUT RAG] — prompt: the bare question. Output:")
        print("   " + without.strip().replace("\n", "\n   "))

        context, with_rag = answer_with_rag(q, store)
        print("\n[RETRIEVED CONTEXT] — these chunks were injected into the WITH-RAG prompt:")
        for chunk_line in context.split("\n\n"):
            print("   " + chunk_line.strip())

        print("\n[WITH RAG] — prompt: context + question. Output:")
        print("   " + with_rag.strip().replace("\n", "\n   "))

        _exercises.append({
            "id": f"rag_contrast_{qi + 1}",
            "without_output": without,
            "with_output": with_rag,
        })

    print("\n" + "=" * 70)
    print("✅ Same model, same questions. Retrieval is what made the answers correct.")
    print("   That's RAG. Module 06 makes the *retrieval* step much smarter.")

    if _JUDGE_OUTPUT_PATH:
        Path(_JUDGE_OUTPUT_PATH).write_text(json.dumps(_exercises, indent=2))


if __name__ == "__main__":
    try:
        main()
    except SetupError as e:
        print("\n⚠️  Setup problem:\n")
        print(str(e))
        sys.exit(2)

# AI Concepts — Hands-On Learning

A self-paced, **build-it-yourself** course for the core concepts behind modern AI
applications: prompting, RAG, agents, MCP, fine-tuning, evals, multimodal, and
personal-AI systems like the Karpathy "second brain" and self-improvement loop.

The goal isn't to use AI to write ordinary code — it's to **build applications
that leverage what AI uniquely enables**. Every module is a short Markdown
explainer plus small Python scripts you actually run.

> **Who this is for:** people comfortable enough to follow code but who want the
> AI concepts explained from the ground up. Each module fits in **~1 hour** (often
> less); a few longer/optional ones are marked ⏱️/✚.

---

## How to use this course

1. Do the one-time **[SETUP.md](SETUP.md)** (Python env, API key, optional Ollama).
2. Work through the modules **in order** — each builds on the last.
3. For each module: read the `README.md`, run the scripts, do the "Try this" bits.
4. Stuck? Every script prints a friendly message telling you what to fix.

**Models used:** [Claude](https://www.anthropic.com) via API (primary) + free
**local models via [Ollama](https://ollama.com)** where it makes sense. The
helpers in [`shared/llm.py`](shared/llm.py) wrap both so lessons stay short.

---

## The path (23 modules · 6 tracks)

⏱️ = longer than an hour · ✚ = optional/advanced (skip on a first pass)

### Track 0 — Foundations
- **00 · [Setup & your first LLM call](modules/00-setup-and-mental-model/)** — mental model: tokens, context window, temperature
- **01 · [Prompt engineering & structured outputs](modules/01-prompt-engineering/)** — system prompts, few-shot, chain-of-thought, reliable JSON
- **02 · [Reasoning, extended thinking & test-time compute](modules/02-reasoning-and-test-time-compute/)**
- **03 · [Tool use / function calling](modules/03-tool-use/)** — the foundation of agents

### Track 1 — Giving the model knowledge (RAG)
- **04 · [Embeddings & semantic search](modules/04-embeddings-and-semantic-search/)**
- **05 · [RAG from scratch](modules/05-rag-from-scratch/)**
- **06 · [Advanced RAG](modules/06-advanced-rag/)** ⏱️ — hybrid search, re-ranking, measuring retrieval
- **07 · [Context engineering & memory](modules/07-context-engineering-and-memory/)**

### Track 2 — Agents
- **08 · Workflows vs. agents + the agent loop (ReAct)**
- **09 · MCP (Model Context Protocol)**
- **10 · Multi-agent & reflection** ⏱️
- **11 · Computer use / browser automation** ✚

### Track 3 — Customizing models & data
- **12 · Fine-tuning concepts** (PEFT, LoRA, QLoRA, RLHF/DPO overview)
- **13 · Hands-on LoRA fine-tune** ⏱️
- **14 · Synthetic data generation**

### Track 4 — Beyond text
- **15 · Multimodal AI: vision & audio**

### Track 5 — Quality, safety & cost
- **16 · Evals** (test sets, LLM-as-judge)
- **17 · Guardrails & safety** (incl. prompt-injection defense)
- **18 · Model selection & routing** (build vs. buy, cost/latency)
- **19 · Observability, cost & latency**

### Track 6 — Personal AI systems (capstones)
- **20 · Second brain / LLM wiki** (the Karpathy method)
- **21 · The Karpathy self-improvement loop**
- **22 · Capstone: RAG + agent + evals in one app** ⏱️

See **[PROGRESS.md](PROGRESS.md)** for which modules are built so far.

---

## Anchor map — where to go deeper

We don't reinvent pedagogy. Each module points to a best-in-class existing
resource for the deep dive; our value-add is the *hands-on glue you run yourself*.

| Topic | Canonical resource |
|---|---|
| Prompting, MCP, agents (Claude-native) | [Anthropic Academy](https://www.anthropic.com/learn) |
| RAG, agents, evals (short courses) | [DeepLearning.AI](https://www.deeplearning.ai/) |
| Fine-tuning, LoRA/QLoRA, embeddings | [mlabonne/llm-course](https://github.com/mlabonne/llm-course) |
| Broad fundamentals | [Microsoft GenAI for Beginners](https://github.com/microsoft/generative-ai-for-beginners) |
| Reference app implementations | [awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) |

---

## Quality: how we keep modules trustworthy

Every module passes a five-layer, near-zero-cost review gate before it's "done":

1. **Deterministic smoke test** — `python tools/smoke_test.py` runs every script
   and checks it works (ground truth, not an opinion).
2. **Rubric judge** — `python tools/llm_judge.py` runs each module's demo
   script and checks the actual prompt/output of each exercise against a
   `rubric.yaml` next to it (e.g. "did the few-shot run actually use the
   convention it was taught?"). Mostly plain regex; the rare fuzzy check asks
   a free local Ollama model (or `--haiku` for a few cents when regex truly
   can't capture it). Catches "the demo doesn't actually show the contrast it
   claims to" — the exact class of bug found and fixed in module 01.
3. **Anchor fact-check** — concept claims verified against the cited source.
4. **Local-model review** — a free, different-family model (via Ollama) reviews
   for accuracy/clarity (independence without a second paid API).
5. **Fresh "beginner" review** — a from-scratch pass that follows only the README
   and reports the first place it breaks.

---

## Publishing to GitHub (your copy → shareable course)

This folder is a ready-to-publish repo. When you want to share it:

```bash
git init
git add .
git commit -m "AI Concepts hands-on course"
gh repo create ai-concepts-hands-on-learning --public --source=. --push
```

Your `.env` (with your key) is git-ignored, so it stays private. Others just copy
`.env.example`, add their own key, and follow `SETUP.md`.

# Progress tracker

Where we are, so any session (or contributor) can pick up instantly.

**Legend:** ✅ done · 🚧 in progress · ⏸️ blocked on local setup · ⬜ not started
**Per-module checks:** _Authored_ (README + scripts written) · _Smoke_ (runs via
`tools/smoke_test.py`) · _Rubric QA_ (demo script has a `rubric.yaml` and
`python tools/llm_judge.py <NN>` passes — checks each exercise actually
demonstrates the contrast it claims to, not just "didn't crash") · _Reviewed_
(passed the full QA gate from the README's "Quality" section).

⚠️ **From module 08 onward, a module cannot be marked Authored ✅ until it also
has a passing Rubric QA** — this gate exists because module 01 needed 4 manual
QA rounds to catch issues `llm_judge.py` now catches automatically (see
[[demo-script-design-lessons]]). Modules 00–07 predate the gate and are being
retrofitted incrementally (see notes below).

| # | Module | Authored | Smoke | Rubric QA | Reviewed |
|---|--------|:--------:|:-----:|:---------:|:--------:|
| 00 | Setup & mental model | ✅ | ✅ | ✅ | 🚧 |
| 01 | Prompt engineering & structured outputs | ✅ | ✅ | ✅ | 🚧 |
| 02 | Reasoning & test-time compute | ✅ | ✅ | ✅ | 🚧 |
| 03 | Tool use / function calling | ✅ | ✅ | ✅ | 🚧 |
| 04 | Embeddings & semantic search | ✅ | ✅ | ✅ | 🚧 |
| 05 | RAG from scratch | ✅ | ✅ | ✅ | 🚧 |
| 06 | Advanced RAG ⏱️ | ✅ | ✅ | ✅ | 🚧 |
| 07 | Context engineering & memory | ✅ | ✅ | ✅ | 🚧 |
| 08 | Workflows vs. agents + agent loop | ⬜ | ⬜ | ⬜ | ⬜ |
| 09 | MCP | ⬜ | ⬜ | ⬜ | ⬜ |
| 10 | Multi-agent & reflection ⏱️ | ⬜ | ⬜ | ⬜ | ⬜ |
| 11 | Computer use / browser ✚ | ⬜ | ⬜ | ⬜ | ⬜ |
| 12 | Fine-tuning concepts | ⬜ | ⬜ | ⬜ | ⬜ |
| 13 | Hands-on LoRA fine-tune ⏱️ | ⬜ | ⬜ | ⬜ | ⬜ |
| 14 | Synthetic data generation | ⬜ | ⬜ | ⬜ | ⬜ |
| 15 | Multimodal: vision & audio | ⬜ | ⬜ | ⬜ | ⬜ |
| 16 | Evals | ⬜ | ⬜ | ⬜ | ⬜ |
| 17 | Guardrails & safety | ⬜ | ⬜ | ⬜ | ⬜ |
| 18 | Model selection & routing | ⬜ | ⬜ | ⬜ | ⬜ |
| 19 | Observability, cost & latency | ⬜ | ⬜ | ⬜ | ⬜ |
| 20 | Second brain / LLM wiki | ⬜ | ⬜ | ⬜ | ⬜ |
| 21 | Karpathy self-improvement loop | ⬜ | ⬜ | ⬜ | ⬜ |
| 22 | Capstone ⏱️ | ⬜ | ⬜ | ⬜ | ⬜ |

**Rubric QA retrofit status:** 00–07 done (all of Track 0 + Track 1 complete
— 26/26 checks pass). Modules 04–07 were retrofitted and aligned with design
principles (keyword-vs-semantic contrast added to 04, retrieved context printed
in 05, top chunks shown per question in 06, first call response printed in 07).

**Track 0 verified live:** all 5 scripts PASS `python tools/smoke_test.py` with
real Claude calls. Outputs were inspected and match each README's "Expected"
block. The QA gate already caught + fixed one real bug (the default model rejects
assistant-prefill, so module 01's structured-output lesson now uses
"instruct + parse defensively" instead).

🚧 **Reviewed = partial.** Done: deterministic smoke test + maintainer output
inspection. Not yet done: the free local-model review and fresh beginner-subagent
pass (both need Ollama installed). Tick to ✅ after those.

✅ **Track 1 (04–07) fully verified.** All 4 scripts pass smoke test live
(Ollama + Claude). All 11 rubric checks pass (`python tools/llm_judge.py 04 05 06 07`).
Scripts are aligned with design principles: contrast is structurally forced,
retrieved context is printed inline, and stdout is self-contained evidence.

## Learner position (where to resume)
- Completed **Module 00** (ran `hello_llm.py`, mental model understood).
- **Resume at Module 01** → `python modules/01-prompt-engineering/prompting_techniques.py`,
  then `structured_output.py`, then read its README.

## Next up
- **You:** install Ollama (`brew install ollama`, then `ollama pull nomic-embed-text`),
  then `python tools/smoke_test.py 04 05 06` to flip ⏸️ → ✅ and see RAG live.
- **Work through:** Track 0 (00–03, running) and Track 1 (04–07).
- **Build next:** Track 2 (Agents) — modules 08–11 (workflows vs agents + agent
  loop, MCP, multi-agent, computer use). Mostly Claude; no new heavy deps.

# Changelog

A dated, plain-English log of every meaningful change to the course. The newest
entry goes on top. (Part of the session wrap-up protocol — see the plan/README.)

## 2026-06-27 (session 3 — Track 1 design-principle alignment)

- **Module 04 — keyword vs. semantic contrast added.** Previously only showed
  semantic search succeeding; contrast was described in prose. Now runs keyword
  match first (all 0.000 — "eat/stay/healthy" appear in no document verbatim),
  then semantic search finding the right docs. Contrast is structurally forced.
- **Module 05 — retrieved context now printed inline.** Previously the WITH-RAG
  answer appeared without showing what was retrieved. Now prints the 3 retrieved
  chunks between the WITHOUT and WITH outputs so the mechanism is visible.
- **Module 06 — top retrieved chunk shown per question.** Previously showed
  ✓/✗ but not what was retrieved. Now prints the top chunk for both naive and
  hybrid+rerank per question, making it clear why naive misses and hybrid finds.
- **Module 07 — first call response now printed.** Previously discarded call 1's
  reply, so the "model heard it then forgot it" contrast wasn't visible. Now
  prints both replies side-by-side.
- **Rubric QA complete for Track 1 (04–07).** Added `rubric.yaml` + `JUDGE_OUTPUT_PATH`
  wiring to all four modules. All 11 new checks pass. Full suite: 26/26 pass.
- **Smoke test:** all 9 scripts PASS live (Ollama installed; Track 1 no longer ⏸️).

## 2026-06-27 (session 2, continued — wrap-up)

- **Module 00 temperature demo — show temp=0 output twice with `← same`
  label.** Previously said "(identical every time — try it)" for the second
  temp=0 call, which hid the value and prompted "why doesn't it show the full
  text?" Now prints the actual sentence twice so the repeatability lesson is
  self-evident without re-running.
- **Removed `excerpt()` trimming from module 00.** The "..." prefix on long
  sentences also read as broken output. Full sentences now shown — the two
  temp=1 outputs differ enough to be obviously distinct without trimming.
- **`demo-script-design-lessons.md` — consolidated rules 1, 2, 6, 7, 8 into
  one principle:** "A single run's stdout must be self-contained evidence for
  the lesson." Checklist is now 6 rules instead of 10.

## 2026-06-27 (session 2, continued)

- **Module 00 `hello_llm.py` — improved temperature demo and added
  `JUDGE_OUTPUT_PATH` opt-in.** The previous `creative_prompt` ("fun two-word
  name for a pet robot") converged to the same answer at both `temperature=0`
  and `temperature=1.0` in a single run, making the lesson invisible. Replaced
  with "Write one sentence describing what it feels like to touch a cloud" —
  verified live that `temperature=0` produces the *identical* sentence across
  5 consecutive runs, while `temperature=1.0` rephrases it differently each
  time. Also added the prompt display (previously missing from step 3) and a
  "(Run this script a few more times…)" hint reinforcing the repeatability lesson.
  Wired in `JUDGE_OUTPUT_PATH` opt-in identical to modules 01–03.
- **Module 00 — added `rubric.yaml`.** Four checks (2 per temperature branch):
  each output must fit on ≤ 2 lines and mention cloud/mist/damp/soft/weightless/cool.
  All 4 pass.
- **Module 00 `README.md` — updated Expected block and Try-this #1** to match
  the new cloud-sentence prompt and clarify the temp=0 repeatability lesson.
- **Rubric QA retrofit now covers all of Track 0 (modules 00–03):** 15/15
  checks pass across all four rubric files.

## 2026-06-27 (session 2)

- **Module 03 `tool_use.py` — added WITHOUT/WITH contrast and `JUDGE_OUTPUT_PATH`
  opt-in.** Previously the script only showed the WITH-tools path. Now it first
  asks the same question with no tools available (model is stuck: "I don't have
  any pricing information…") then with tools (model plans → calls get_price twice
  + calculator → returns exact $30.75). The contrast makes the lesson concrete:
  tools extend what the model can *do*, not just what it can *say*. Added
  `JUDGE_OUTPUT_PATH` opt-in identical to modules 01 and 02.
- **Module 03 — added `rubric.yaml`.** Two regex checks: WITHOUT output must
  signal inability (matches "don't have / can't / no information"); WITH output
  must contain the correct total `30.75`. All 2 checks pass.
- **Module 03 `README.md` — updated Expected shape block** to show the
  WITHOUT/WITH output structure instead of the previous Q/A-only format.
- **Module 01 `rubric.yaml` — removed unreliable Ollama judge check** on
  `chain_of_thought`. The check asked Ollama (llama3.2) whether the output shows
  step-by-step algebra; it consistently answered NO even when the regex check
  (which directly matches the algebra) passed. Same root cause as the module 02
  judge check removed last session: llama3.2 is unreliable on this, and the
  judge adds zero signal beyond the already-passing regex. Removed per the
  "prefer mechanical checks" design principle.
- **Rubric QA retrofit complete for Track 0 (modules 01–03).** `python
  tools/llm_judge.py 01 02 03` → 11 passed, 0 failed, 0 skipped. Full smoke
  test `python tools/smoke_test.py 00 01 02 03` → 5/5 passed.

## 2026-06-27

- **Added `tools/llm_judge.py` — new QA layer 2, "does each exercise actually
  teach what it claims?"** This formalizes the manual live-checking done
  across module 01's 4 QA rounds into a repeatable, automated tool. Each
  module can define a `rubric.yaml` next to its demo script listing, per
  exercise, pass/fail checks: `regex` (does the output match/not-match a
  pattern), `max_lines` (terseness), or `judge` (ask an LLM a yes/no question
  for anything regex can't capture — defaults to free local Ollama, or
  `--haiku`/`model: haiku` in the rubric for a few cents when a check is
  genuinely subjective). A demo script opts in by writing its prompt/output
  pairs as JSON to `$JUDGE_OUTPUT_PATH` when that env var is set (no effect on
  a normal run — `prompting_techniques.py` updated to do this). Added
  `modules/01-prompt-engineering/rubric.yaml` covering all 4 of its exercises;
  `python tools/llm_judge.py 01` passes 7/7 regex checks (the 1 `judge` check
  skips cleanly since Ollama isn't installed yet). Added `pyyaml` to
  `requirements.txt`. README's "Quality" section updated from 4 to 5 layers.
- **Module 01 `prompting_techniques.py` — loosened display trimming (4th QA
  pass).** The 350-char display cap from the previous fix was too aggressive —
  it cut the verbose WITHOUT outputs (headers, tables, structure) right when
  they were supposed to demonstrate rambling. Raised the `trim()` cap to 1000
  chars; most responses now print in full with no cutoff at all, and the rare
  ones that still exceed it get cut at a clean boundary as before.
- **Module 01 `prompting_techniques.py` — fixed ragged truncation (3rd QA pass).**
  Long outputs were getting cut mid-word by `max_tokens`, which looked like a
  bug rather than a deliberate cutoff. Added a `trim()` helper that cuts
  display text at a clean sentence/line boundary and says
  `[...trimmed for the lesson]` explicitly, and raised `max_tokens` on the
  longer-output calls (vague essay, unconstrained code review, zero-shot
  classification) so the model has room to reach a sentence boundary before
  either the API or `trim()` cuts it off.
- **Module 01 `prompting_techniques.py` rewritten for a consistent WITHOUT/WITH
  format and a clearer few-shot demo — second round of learner QA.** All four
  sections now share one `compare()` helper that prints: prompt without the
  technique → its output → prompt with the technique → its output, every
  time. The few-shot section (#3) was redesigned after the first fix's
  explanation proved confusing: instead of comparing zero-shot vs. few-shot
  sentiment labels (which always agree — the model already knows sentiment),
  it now teaches an arbitrary **convention** the model can't infer from words
  alone (`+1/-1/0` instead of `POSITIVE/NEGATIVE/NEUTRAL`). Zero-shot invents
  its own scheme; few-shot copies the exact one shown — an unambiguous,
  easy-to-explain contrast. Chain-of-thought puzzle (still the de-famous-ified
  "$6.30 racket and shuttlecock" variant from the prior fix) kept as-is.
  README's "Expected" block and "Try this" #2 updated to match.

## 2026-06-24

- **Track 1 (RAG) authored — modules 04–07.** 04 Embeddings & semantic search,
  05 RAG from scratch (with/without-RAG contrast on a fictional product),
  06 Advanced RAG ⏱️ (hybrid search + LLM re-rank + a real retrieval eval),
  07 Context engineering & memory. Added reusable `shared/rag.py`
  (`TinyVectorStore`, `HybridStore` via subclass in module 06, `chunk_text`,
  `cosine_similarity`).
- **Design change (logged per wrap-up protocol):** dropped the planned `chromadb`
  dependency in favor of a pure-NumPy `TinyVectorStore`. Reasons: more educational
  ("from scratch"), and avoids heavy deps that may lack Python 3.14 wheels. Chroma
  is now referenced as the "real DB" upgrade in module 05's deep-dive link.
- **Verification:** Module 07 (Claude-only) live-verified PASS. Modules 04–06 need
  Ollama for embeddings (not installed) so they SKIP in the smoke test; their full
  logic was verified separately via a deterministic fake embedder + the live
  Claude re-ranker. Suite stays green (0 failures).
- **Track 0 verified live.** Ran all scripts against the real Claude API: 5/5
  PASS in `tools/smoke_test.py`, outputs match the READMEs.
- **Bug caught + fixed by the QA gate:** the default model (`claude-sonnet-4-6`)
  rejects assistant-message *prefill*, which module 01's `structured_output.py`
  relied on. Rewrote that lesson to "instruct + parse defensively" (system prompt
  demands raw JSON; `parse_json()` strips stray code fences) and updated its
  README. This is also the more broadly applicable pattern for beginners.
- **Track 0 complete (modules 00–03 authored).** 01 Prompt engineering &
  structured outputs (4 techniques + JSON via prefill), 02 Reasoning &
  test-time compute (extended thinking vs. fast), 03 Tool use / function calling
  (full hand-built tool-use loop). All scripts verified syntactically and via the
  smoke runner (report SKIP until an API key is set — expected).
- Added `get_client()` and `claude_think()` helpers to `shared/llm.py` so advanced
  lessons can show the real Claude API (prefill, extended thinking, tool use)
  while reusing one place for key handling.
- **Initial scaffolding created.** Project structure, shared model helpers
  (`shared/llm.py` — wraps Claude + local Ollama), one-venv `requirements.txt`,
  `.env.example`, `.gitignore`, and the smoke-test runner (`tools/smoke_test.py`).
- **Course design finalized:** 23 modules across 6 tracks (Foundations → RAG →
  Agents → Customizing models → Multimodal → Quality/Cost → Personal AI systems).
- **Module 00 (Setup & mental model) authored** with `hello_llm.py` — first LLM
  call, plus tokens/context-window/temperature mental model. Verified: core deps
  install on Python 3.14; friendly setup-error path and smoke runner both work.
- **Decisions:** Python · Claude API (default model `claude-sonnet-4-6`,
  overridable) + free local Ollama · Markdown explainer + runnable `.py` per
  module · `chromadb`/`torch` deferred to the modules that need them so the base
  install stays small and robust on very new Python versions.

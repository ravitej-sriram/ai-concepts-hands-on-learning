# Setup (do this once)

This takes about 15–20 minutes the first time. After this, every module just
works. Commands assume **macOS** with a terminal open in the project folder.

> Tip: the project folder has a space in its name. When `cd`-ing into it, wrap
> the path in quotes: `cd "AI Concepts Hands On Learning"`.

---

## 1. Check Python

You need Python 3.10 or newer.

```bash
python3 --version
```

If that prints `Python 3.10.x` or higher, you're good. If `python3` isn't found,
install it from [python.org](https://www.python.org/downloads/).

## 2. Create a virtual environment (a sandbox for this course's packages)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

After activating, your prompt shows `(.venv)`. **Run every course command with
the venv active.** To reactivate later (e.g. a new terminal):
`source .venv/bin/activate`. To leave it: `deactivate`.

## 3. Install the packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Add your Claude API key

1. Go to [console.anthropic.com](https://console.anthropic.com) → **Settings → API Keys** → create a key.
2. Copy the example env file and paste your key into it:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` in any editor and replace the placeholder with your real key:
   ```
   ANTHROPIC_API_KEY=sk-ant-...your-real-key...
   ```

> 💡 `.env` is git-ignored, so your key is never committed or published.
> 💰 The API is pay-per-use but very cheap for learning — the whole course
> typically costs well under a few dollars. Set a low spend limit in the console
> for peace of mind.

## 5. Verify it all works

```bash
python modules/00-setup-and-mental-model/hello_llm.py
```

You should see Claude reply. If you see a "Setup problem" message, it tells you
exactly what to fix.

---

## 6. Optional now, needed later: local models with Ollama (free)

Some modules (embeddings, RAG, and anything marked "local/free") run a model on
your own Mac via **Ollama** — no API cost. You can set this up now or when you
reach those modules.

1. Install from [ollama.com](https://ollama.com) (download the macOS app and open it).
2. Pull the two small models the course uses:
   ```bash
   ollama pull llama3.2
   ollama pull nomic-embed-text
   ```
3. Make sure the Ollama app is running (it serves at `http://localhost:11434`).

---

## Running the smoke test (optional but nice)

To check that everything still runs after changes:

```bash
python tools/smoke_test.py        # runs every module's scripts
python tools/smoke_test.py 00     # just module 00
```

A **SKIP** simply means that script needs a key or local model you haven't set
up — it's not a failure.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `No real ANTHROPIC_API_KEY found` | You haven't created `.env` or didn't paste a real key. Redo step 4. |
| `command not found: python3` | Install Python from python.org. |
| `ModuleNotFoundError: anthropic` | Your venv isn't active, or step 3 didn't run. `source .venv/bin/activate` then reinstall. |
| `Couldn't reach Ollama` | Install/open Ollama (step 6) and make sure the app is running. |
| Claude API error about credits | Add a little credit / raise the spend limit in the Anthropic console. |

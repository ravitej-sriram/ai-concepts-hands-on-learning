"""
tools/smoke_test.py — the deterministic "does it actually work?" check.

This is QA layer 1 from the course plan: it RUNS every module's scripts and
reports whether they succeed. Running the code is model-independent ground
truth — far more trustworthy than asking an AI "does this look right?".

Exit-code convention used by every module script:
    0  → success (the exercise ran end-to-end)
    2  → setup needed / skipped (e.g. no API key, or Ollama not running)
    other → real failure (a bug we must fix)

Usage (from the project root, with your venv active):
    python tools/smoke_test.py            # run every script in every module
    python tools/smoke_test.py 00 01      # only modules whose folder starts 00/01

A "skip" is not a failure — it just means that script needs a key or a local
model you haven't configured. The runner is GREEN as long as nothing truly fails.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = PROJECT_ROOT / "modules"

# ANSI colors (fall back to plain text if the terminal doesn't like them)
GREEN, YELLOW, RED, DIM, RESET = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"


def find_scripts(prefixes: list[str]) -> list[Path]:
    """Return every .py file inside modules/, optionally filtered by folder prefix."""
    scripts: list[Path] = []
    for module_dir in sorted(MODULES_DIR.iterdir()):
        if not module_dir.is_dir():
            continue
        if prefixes and not any(module_dir.name.startswith(p) for p in prefixes):
            continue
        scripts.extend(sorted(module_dir.glob("*.py")))
    return scripts


def run_one(script: Path) -> tuple[str, str]:
    """Run a single script. Returns (status, detail) where status is pass/skip/fail."""
    rel = script.relative_to(PROJECT_ROOT)
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,  # 5 min ceiling so a hung script can't stall the suite
        )
    except subprocess.TimeoutExpired:
        return "fail", "timed out after 300s"

    if result.returncode == 0:
        return "pass", ""
    if result.returncode == 2:
        # Friendly "needs setup" — pull the first meaningful line for context.
        first_line = next(
            (ln for ln in result.stdout.splitlines() if ln.strip() and "===" not in ln),
            "needs setup",
        )
        return "skip", first_line.strip()
    # Anything else is a genuine failure; surface the tail of stderr to debug.
    tail = (result.stderr or result.stdout).strip().splitlines()[-3:]
    return "fail", " | ".join(tail) if tail else f"exit code {result.returncode}"


def main() -> None:
    prefixes = sys.argv[1:]  # e.g. ["00", "01"]
    scripts = find_scripts(prefixes)

    if not scripts:
        print("No module scripts found to run.")
        return

    print(f"Running {len(scripts)} script(s)...\n")
    passed = skipped = failed = 0

    for script in scripts:
        status, detail = run_one(script)
        rel = script.relative_to(PROJECT_ROOT)
        if status == "pass":
            passed += 1
            print(f"  {GREEN}✓ PASS{RESET}  {rel}")
        elif status == "skip":
            skipped += 1
            print(f"  {YELLOW}~ SKIP{RESET}  {rel}  {DIM}({detail}){RESET}")
        else:
            failed += 1
            print(f"  {RED}✗ FAIL{RESET}  {rel}  {DIM}{detail}{RESET}")

    print("\n" + "-" * 60)
    print(f"  {passed} passed · {skipped} skipped · {failed} failed")
    print("-" * 60)

    # The suite is only RED if something actually failed. Skips are fine.
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

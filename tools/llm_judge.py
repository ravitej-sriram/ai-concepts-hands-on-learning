"""
tools/llm_judge.py — QA layer: does each exercise actually teach what it claims?

smoke_test.py only checks "did it crash?" (ground truth, but cheap). This goes
one level deeper: it runs a module's demo script, and checks the actual
prompt/output pairs from THIS run against that module's rubric.yaml — e.g.
"did the few-shot run actually use the +1/-1/0 convention?" Most rubric checks
are plain regex (free, deterministic, no model needed). A rubric can also ask
an LLM a yes/no question for anything regex can't capture — by default the
free local Ollama model; pass --haiku to use Claude Haiku for that exercise's
judge checks instead (small real cost, only worth it for genuinely fuzzy
judgment calls — see modules/*/rubric.yaml's `model:` field).

Usage (from the project root, venv active):
    python tools/llm_judge.py            # judge every module with a rubric.yaml
    python tools/llm_judge.py 01         # judge only modules whose folder starts "01"
    python tools/llm_judge.py 01 --haiku # use Haiku instead of Ollama for judge checks
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.llm import claude, local_llm, SetupError  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = PROJECT_ROOT / "modules"

GREEN, YELLOW, RED, DIM, RESET = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"


def find_rubrics(prefixes: list[str]) -> list[Path]:
    rubrics = []
    for module_dir in sorted(MODULES_DIR.iterdir()):
        if not module_dir.is_dir():
            continue
        if prefixes and not any(module_dir.name.startswith(p) for p in prefixes):
            continue
        rubric = module_dir / "rubric.yaml"
        if rubric.exists():
            rubrics.append(rubric)
    return rubrics


def run_for_exercises(script: Path) -> list[dict]:
    """Run a module's demo script with JUDGE_OUTPUT_PATH set; return its
    reported prompt/output records (see prompting_techniques.py's _exercises)."""
    fd, out_path_str = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    out_path = Path(out_path_str)
    try:
        env = {**os.environ, "JUDGE_OUTPUT_PATH": str(out_path)}
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 2:
            raise SetupError(result.stdout.strip().splitlines()[-1] if result.stdout else "needs setup")
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout).strip().splitlines()[-1])
        raw = out_path.read_text().strip()
        if not raw:
            return []  # script doesn't opt into JUDGE_OUTPUT_PATH — nothing to judge
        return json.loads(raw)
    finally:
        out_path.unlink(missing_ok=True)


def run_check(check: dict, exercise: dict, default_model: str) -> tuple[bool | None, str]:
    target_text = exercise.get(check["target"], "").strip()
    ctype = check["type"]

    if ctype == "regex":
        matched = re.search(check["pattern"], target_text) is not None
        ok = matched == check.get("must_match", True)
        return ok, f"regex {check['pattern']!r} {'matched' if matched else 'did not match'}"

    if ctype == "max_lines":
        n_lines = len([ln for ln in target_text.splitlines() if ln.strip()])
        ok = n_lines <= check["max"]
        return ok, f"{n_lines} non-empty line(s), max {check['max']}"

    if ctype == "judge":
        model = check.get("model", default_model)
        prompt = f"{check['question']}\n\nOutput to judge:\n{target_text}"
        try:
            reply = (
                claude(prompt, model="claude-haiku-4-5", temperature=0, max_tokens=10)
                if model == "haiku"
                else local_llm(prompt)
            )
        except SetupError as e:
            return None, f"judge ({model}) unavailable: {e}"
        ok = reply.strip().upper().startswith("YES")
        return ok, f"{model} judge said: {reply.strip()[:80]!r}"

    raise ValueError(f"Unknown check type: {ctype}")


def judge_rubric(rubric_path: Path, default_model: str) -> tuple[int, int, int]:
    module_dir = rubric_path.parent
    rubric = yaml.safe_load(rubric_path.read_text())

    # A module's rubric ids can come from any of its scripts. Most modules
    # have only one script that opts into JUDGE_OUTPUT_PATH; running all of
    # them and merging by exercise id keeps this simple without needing the
    # rubric to also name which script each exercise lives in.
    scripts = sorted(module_dir.glob("*.py"))
    exercises_by_id: dict[str, dict] = {}
    for script in scripts:
        try:
            for ex in run_for_exercises(script):
                exercises_by_id[ex["id"]] = ex
        except SetupError as e:
            print(f"  {YELLOW}~ SKIP{RESET}  {script.relative_to(PROJECT_ROOT)}  {DIM}({e}){RESET}")
        except Exception as e:
            print(f"  {RED}✗ ERROR{RESET}  {script.relative_to(PROJECT_ROOT)}  {DIM}{e}{RESET}")

    passed = failed = skipped = 0
    for exercise_spec in rubric.get("exercises", []):
        ex_id = exercise_spec["id"]
        exercise = exercises_by_id.get(ex_id)
        if exercise is None:
            print(f"  {YELLOW}~ SKIP{RESET}  {ex_id}  {DIM}(no run produced this exercise){RESET}")
            skipped += 1
            continue
        for check in exercise_spec.get("checks", []):
            ok, detail = run_check(check, exercise, default_model)
            label = f"{ex_id} · {check['type']}({check['target']})"
            if ok is True:
                passed += 1
                print(f"  {GREEN}✓ PASS{RESET}  {label}  {DIM}{detail}{RESET}")
            elif ok is False:
                failed += 1
                print(f"  {RED}✗ FAIL{RESET}  {label}  {DIM}{detail}{RESET}")
            else:
                skipped += 1
                print(f"  {YELLOW}~ SKIP{RESET}  {label}  {DIM}{detail}{RESET}")
    return passed, failed, skipped


def main() -> None:
    args = sys.argv[1:]
    default_model = "haiku" if "--haiku" in args else "ollama"
    prefixes = [a for a in args if a != "--haiku"]

    rubrics = find_rubrics(prefixes)
    if not rubrics:
        print("No rubric.yaml found for the given module(s).")
        return

    total_passed = total_failed = total_skipped = 0
    for rubric_path in rubrics:
        rel = rubric_path.relative_to(PROJECT_ROOT)
        print(f"\n{rel}")
        print("-" * 70)
        p, f, s = judge_rubric(rubric_path, default_model)
        total_passed += p
        total_failed += f
        total_skipped += s

    print("\n" + "=" * 70)
    print(f"  {total_passed} passed · {total_skipped} skipped · {total_failed} failed")
    print("=" * 70)
    sys.exit(1 if total_failed else 0)


if __name__ == "__main__":
    main()

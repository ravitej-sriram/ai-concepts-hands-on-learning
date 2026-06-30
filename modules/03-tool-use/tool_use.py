"""
Module 03 · tool_use.py — let the model call YOUR Python functions.

Run from the project root:
    python modules/03-tool-use/tool_use.py

This is the single most important mechanism behind "agents": the model doesn't
run your code, it *asks* to. The loop is:

    1. You describe your tools (name + what they do + inputs).
    2. The model replies "please call tool X with these arguments."
    3. YOUR code runs the real function and sends the result back.
    4. The model uses that result to answer (or asks for another tool).

We implement that whole loop by hand here so you can see every step.
"""

import ast
import json
import operator
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.llm import claude, get_client, DEFAULT_CLAUDE_MODEL, SetupError

# See modules/01-prompt-engineering/prompting_techniques.py for why this
# exists: tools/llm_judge.py sets this env var to ask for a structured JSON
# dump of prompt/output pairs, checked against this module's rubric.yaml.
# Normal runs (the learner just running the script) are unaffected.
_JUDGE_OUTPUT_PATH = os.environ.get("JUDGE_OUTPUT_PATH")
_exercises: list[dict] = []


# ---------------------------------------------------------------------------
# 1. The actual Python functions ("tools") the model is allowed to use.
# ---------------------------------------------------------------------------
_OPS = {  # a tiny, SAFE arithmetic evaluator (no eval() of arbitrary code!)
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant):           # a number literal
        return node.value
    if isinstance(node, ast.BinOp):              # a + b, a * b, ...
        return _OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):            # -a
        return _OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("unsupported expression")


def calculator(expression: str) -> str:
    """Evaluate a basic math expression like '(1.10 - 1.00) / 2'."""
    try:
        return str(_safe_eval(ast.parse(expression, mode="eval").body))
    except Exception as e:
        return f"error: {e}"


# A fake "database" so we don't need real infrastructure to learn the pattern.
_PRICES = {"widget": 4.50, "gadget": 12.0, "gizmo": 7.25}


def get_price(product: str) -> str:
    """Look up the unit price of a product in our catalog."""
    price = _PRICES.get(product.lower().strip())
    return f"${price:.2f}" if price is not None else f"unknown product: {product!r}"


# Map tool NAME → the real Python function. The model never sees this code; it
# only knows the descriptions below.
TOOL_IMPLEMENTATIONS = {"calculator": calculator, "get_price": get_price}


# ---------------------------------------------------------------------------
# 2. The tool DESCRIPTIONS we send to the model (this is all it sees).
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression (+ - * / parentheses).",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string",
                                          "description": "e.g. '3 * (4.50 + 7.25)'"}},
            "required": ["expression"],
        },
    },
    {
        "name": "get_price",
        "description": "Look up the unit price of a product in the catalog.",
        "input_schema": {
            "type": "object",
            "properties": {"product": {"type": "string",
                                       "description": "Product name, e.g. 'widget'"}},
            "required": ["product"],
        },
    },
]


def ask_with_tools(question: str) -> str:
    """Run the full tool-use loop and return the model's final text answer."""
    client = get_client()
    messages = [{"role": "user", "content": question}]

    # Keep going as long as the model wants to call a tool.
    while True:
        response = client.messages.create(
            model=DEFAULT_CLAUDE_MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            # No tool requested → this is the final answer.
            return "".join(b.text for b in response.content if b.type == "text")

        # Record the model's turn (which includes its tool requests).
        messages.append({"role": "assistant", "content": response.content})

        # Run every tool the model asked for, and collect the results.
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                func = TOOL_IMPLEMENTATIONS[block.name]
                output = func(**block.input)
                print(f"   🔧 model called {block.name}({block.input}) → {output}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })

        # Send the tool results back as the next user turn, then loop.
        messages.append({"role": "user", "content": tool_results})


def main() -> None:
    question = "How much do 3 gizmos and 2 widgets cost in total?"

    # ------------------------------------------------------------------
    # WITHOUT tools — the model doesn't know our private catalog prices.
    # It can only admit it's stuck; it cannot look anything up or compute.
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("WITHOUT tools")
    print("=" * 70)
    print(f"Prompt: {question}\n")
    without_answer = claude(question, temperature=0, max_tokens=200)
    print("Output:", without_answer.strip())

    # ------------------------------------------------------------------
    # WITH tools — same question, but the model now has get_price and
    # calculator available. Watch it plan → call → observe → answer.
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("WITH tools (the reason→act→observe loop in action)")
    print("=" * 70)
    print(f"Prompt: {question}\n")
    with_answer = ask_with_tools(question)
    print("A:", with_answer.strip())

    print("\n" + "=" * 70)
    print("A second example — chained tool calls")
    print("=" * 70)
    q2 = "What's 15% of the price of a gadget?"
    print(f"Prompt: {q2}\n")
    answer2 = ask_with_tools(q2)
    print("A:", answer2.strip())

    print("\n✅ Done. The model planned, called your real functions, and answered.")
    print("   That loop — reason, act, observe — is exactly what an agent is (module 08).")

    _exercises.append({
        "id": "tool_use_contrast",
        "without_prompt": question,
        "without_output": without_answer,
        "with_prompt": question,
        "with_output": with_answer,
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

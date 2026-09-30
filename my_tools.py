import ast
import operator
from pathlib import Path
from urllib.parse import urlparse

import requests


# -----------------------------
# Safe Calculator
# -----------------------------

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_calculator(expression: str) -> str:
    """Safely evaluate basic arithmetic without using eval()."""

    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree.body)
        return str(result)
    except Exception as exc:
        return f"Calculator error: {exc}"


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        operand = _eval_node(node.operand)
        return _ALLOWED_OPERATORS[type(node.op)](operand)

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _ALLOWED_OPERATORS[type(node.op)](left, right)

    raise ValueError("Only basic arithmetic expressions are allowed.")


# -----------------------------
# Web Page Reader
# -----------------------------

def read_webpage(url: str, max_chars: int = 2000) -> str:
    """Read local HTML/text files or HTTP/HTTPS pages."""

    try:
        parsed = urlparse(url)

        if parsed.scheme in ("", "file"):
            path = Path(parsed.path if parsed.scheme == "file" else url)

            if not path.exists():
                return f"File not found: {path}"

            text = path.read_text(encoding="utf-8", errors="ignore")

        elif parsed.scheme in ("http", "https"):
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            text = response.text

        else:
            return f"Unsupported URL scheme: {parsed.scheme}"

        # Remove simple script/style blocks.
        import re

        text = re.sub(
            r"<script.*?>.*?</script>",
            "",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        text = re.sub(
            r"<style.*?>.*?</style>",
            "",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Remove HTML tags.
        text = re.sub(r"<[^>]+>", " ", text)

        # Normalize whitespace.
        text = re.sub(r"\s+", " ", text).strip()

        return text[:max_chars]

    except Exception as exc:
        return f"Web reader error: {exc}"


# -----------------------------
# Tool Registry
# -----------------------------

TOOL_FUNCTIONS = {
    "safe_calculator": safe_calculator,
    "read_webpage": read_webpage,
}


# -----------------------------
# OpenAI Tool Schemas
# -----------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "safe_calculator",
            "description": "Safely calculate a basic arithmetic expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Arithmetic expression such as (12000 + 18000) * 0.9",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_webpage",
            "description": "Read text from a local HTML/text file or HTTP/HTTPS webpage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Local file path or webpage URL.",
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Maximum number of characters to return.",
                    },
                },
                "required": ["url"],
            },
        },
    },
]
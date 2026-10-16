"""Code pruner and simplification transforms."""

from __future__ import annotations

import re


def prune_whitespace_and_blank_lines(source: str, max_consecutive_blanks: int = 2) -> str:
    """Normalize excessive blank lines and trailing whitespace."""
    lines = source.splitlines()
    cleaned = []
    blank_run = 0

    for line in lines:
        stripped_right = line.rstrip()
        if not stripped_right:
            blank_run += 1
            if blank_run <= max_consecutive_blanks:
                cleaned.append("")
        else:
            blank_run = 0
            cleaned.append(stripped_right)

    return "\n".join(cleaned) + ("\n" if source.endswith("\n") else "")


def strip_inline_comments(source: str) -> str:
    """Remove purely cosmetic comment lines while preserving docstrings and headers."""
    lines = source.splitlines()
    kept = []
    for line in lines:
        stripped = line.strip()
        # Keep shebang, encoding, noqa, type hints, and todo comments
        if stripped.startswith("#"):
            lower = stripped.lower()
            if any(k in lower for k in ("!/bin", "coding:", "type: ignore", "noqa", "todo", "fixme")):
                kept.append(line)
            else:
                continue
        else:
            kept.append(line)
    return "\n".join(kept) + ("\n" if source.endswith("\n") else "")


def simplify_code(source: str) -> str:
    """Run non-destructive simplification passes over Python source code."""
    res = strip_inline_comments(source)
    res = prune_whitespace_and_blank_lines(res, max_consecutive_blanks=1)
    return res

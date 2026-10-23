#!/usr/bin/env python3
"""PostToolUse (Write|Edit|MultiEdit): lint agent and skill definition files."""

from __future__ import annotations

import sys

from mas_lint.definitions import definition_kind, lint_definition, short_path
from mas_lint.hookio import WRITE_TOOLS, post_block, post_context, run, target_path
from mas_lint.model import Severity


def handle(event: dict) -> dict | None:
    if event.get("tool_name") not in WRITE_TOOLS:
        return None
    path = target_path(event)
    kind = definition_kind(str(path)) if path else None
    if kind is None or not path.is_file():
        return None
    findings = lint_definition(path.read_text(encoding="utf-8"), kind, str(path))
    serious = [f for f in findings if f.severity is not Severity.INFO]
    if not serious:
        return None
    lines = "\n".join(f"- {f.rule_id} {f.severity.value}: {f.message}" for f in serious)
    headline = f"mas-architect check of {kind} {short_path(str(path))}:"
    if any(f.severity is Severity.ERROR for f in serious):
        return post_block(f"{headline}\n{lines}")
    return post_context(f"{headline}\n{lines}")


if __name__ == "__main__":
    sys.exit(run(handle))

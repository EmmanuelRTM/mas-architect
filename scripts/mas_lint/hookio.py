"""Claude Code hook I/O: read the event from stdin, write a decision to stdout.

Hooks fail open: an internal error is reported on stderr and the tool call
proceeds, so a broken check never blocks a session.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

WRITE_TOOLS = frozenset({"Write", "Edit", "MultiEdit", "NotebookEdit"})


def read_event() -> dict[str, Any] | None:
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def tool_input(event: dict) -> dict:
    value = event.get("tool_input")
    return value if isinstance(value, dict) else {}


def target_path(event: dict) -> Path | None:
    raw = tool_input(event).get("file_path") or tool_input(event).get("notebook_path")
    if not isinstance(raw, str) or not raw:
        return None
    path = Path(raw)
    return path if path.is_absolute() else Path(event.get("cwd") or os.getcwd()) / path


def written_texts(event: dict) -> list[str]:
    """Every piece of text the tool call would write."""
    data = tool_input(event)
    texts = [data.get(k) for k in ("content", "new_string", "new_source")]
    for edit in data.get("edits") or []:
        if isinstance(edit, dict):
            texts.append(edit.get("new_string"))
    return [t for t in texts if isinstance(t, str) and t]


def emit(payload: dict | None) -> None:
    if payload:
        sys.stdout.write(json.dumps(payload))


def deny(reason: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}


def pre_context(text: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": text}}


def post_block(reason: str) -> dict:
    return {"decision": "block", "reason": reason}


def post_context(text: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}


def run(handler: Callable[[dict], dict | None]) -> int:
    event = read_event()
    if event is None:
        return 0
    try:
        emit(handler(event))
    except Exception as exc:  # fail open, but say why
        print(f"mas-architect hook error: {type(exc).__name__}: {exc}", file=sys.stderr)
    return 0

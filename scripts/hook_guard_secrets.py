#!/usr/bin/env python3
"""PreToolUse (Write|Edit|MultiEdit|NotebookEdit): deny writes that contain secrets."""

from __future__ import annotations

import sys

from mas_lint.hookio import WRITE_TOOLS, deny, run, written_texts
from mas_lint.secrets import describe, find_secrets


def handle(event: dict) -> dict | None:
    if event.get("tool_name") not in WRITE_TOOLS:
        return None
    matches = [m for text in written_texts(event) for m in find_secrets(text)]
    if not matches:
        return None
    return deny(
        "mas-architect blocked this write: it contains what looks like a hardcoded secret — "
        f"{describe(matches)}. Read it from an environment variable or a secret store instead."
    )


if __name__ == "__main__":
    sys.exit(run(handle))

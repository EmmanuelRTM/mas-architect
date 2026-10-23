"""Skill references: how agents name the skills they preload.

Claude Code resolves an agent's `skills:` entry by exact name, then as
`<agent's plugin>:<name>`, then as any `<plugin>:<name>`. Subagents do not
inherit the parent's skills, and each preloaded skill injects its whole
SKILL.md into the agent's context at startup.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

MAX_PRELOADED_SKILLS = 4

_PART = r"[a-z0-9]+(?:-[a-z0-9]+)*"
_REF = re.compile(rf"^(?:{_PART}:)?{_PART}$")


def parse_skill_list(value: object) -> list[str]:
    """Accept a YAML list, `[a, b]` or `a, b` and return the names in order."""
    if value is None:
        return []
    if isinstance(value, list):
        items: Iterable[object] = value
    else:
        text = str(value).strip()
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1]
        items = text.split(",")
    names = [str(item).strip().strip("'\"") for item in items]
    return [name for name in names if name]


def is_valid_skill_ref(name: str) -> bool:
    return bool(_REF.match(name)) and len(bare_name(name)) <= 64


def bare_name(name: str) -> str:
    return name.rsplit(":", 1)[-1]


def discover_skills(agent_path: Path) -> set[str]:
    """Skill folders next to the agent's `agents/` directory (plugin or `.claude/`)."""
    root = Path(agent_path).parent.parent
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return set()
    return {entry.name for entry in skills_dir.iterdir() if (entry / "SKILL.md").is_file()}


def unknown_refs(refs: Iterable[str], known: Iterable[str]) -> list[str]:
    known_set = set(known)
    return [ref for ref in refs if bare_name(ref) not in known_set and ref not in known_set]

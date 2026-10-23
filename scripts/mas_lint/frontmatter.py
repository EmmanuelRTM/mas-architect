"""Minimal, deterministic YAML-frontmatter reader for agent and skill files.

Supports the subset Claude Code definitions use: `key: value`, quoted
values, `>`/`|` block scalars and `- item` lists. No dependency on PyYAML,
so results are identical everywhere the hook runs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_BLOCK = re.compile(r"\A---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)(.*)\Z", re.DOTALL)
_KEY = re.compile(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$")


@dataclass
class Document:
    has_frontmatter: bool
    fields: dict[str, object] = field(default_factory=dict)
    body: str = ""


def parse(text: str) -> Document:
    match = _BLOCK.match(text)
    if not match:
        return Document(has_frontmatter=False, body=text)
    return Document(True, _parse_fields(match.group(1).splitlines()), match.group(2))


def _parse_fields(lines: list[str]) -> dict[str, object]:
    fields: dict[str, object] = {}
    index = 0
    while index < len(lines):
        match = _KEY.match(lines[index])
        index += 1
        if not match:
            continue
        key, raw = match.group(1), match.group(2).strip()
        nested, index = _collect_indented(lines, index)
        if raw in (">", "|", ">-", "|-"):
            joiner = " " if raw.startswith(">") else "\n"
            fields[key] = joiner.join(line.strip() for line in nested).strip()
        elif raw == "" and nested and all(line.strip().startswith("- ") for line in nested if line.strip()):
            fields[key] = [line.strip()[2:].strip().strip("'\"") for line in nested if line.strip()]
        else:
            fields[key] = _unquote(raw)
    return fields


def _collect_indented(lines: list[str], index: int) -> tuple[list[str], int]:
    nested = []
    while index < len(lines) and (lines[index].startswith((" ", "\t")) or not lines[index].strip()):
        nested.append(lines[index])
        index += 1
    return [line for line in nested if line.strip()], index


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value

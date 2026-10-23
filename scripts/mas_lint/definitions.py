"""Regex lint for Claude Code agent (`agents/*.md`) and skill (`SKILL.md`) files."""

from __future__ import annotations

import re
from pathlib import PurePosixPath

from . import frontmatter
from .catalog import EFFORT_LEVELS, resolve_model
from .model import Finding, Severity
from .reasoning import asks_for_visible_reasoning
from .secrets import find_secrets

_AGENT_PATH = re.compile(r"(?:^|/)agents/[^/]+\.md$")
_SKILL_PATH = re.compile(r"(?:^|/)skills/([^/]+)/SKILL\.md$")
_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_MODEL_ALIASES = {"sonnet", "opus", "haiku", "fable", "inherit"}
MAX_DESCRIPTION = 1024
MAX_SKILL_LINES = 500


def definition_kind(path: str) -> str | None:
    normalized = str(path).replace("\\", "/")
    if _SKILL_PATH.search(normalized):
        return "skill"
    if _AGENT_PATH.search(normalized) and not normalized.endswith("/README.md"):
        return "agent"
    return None


def _finding(rule_id: str, severity: Severity, message: str, path: str) -> Finding:
    return Finding(rule_id=rule_id, severity=severity, message=message, practice="DEF", path=path)


def lint_definition(text: str, kind: str, path: str) -> list[Finding]:
    doc = frontmatter.parse(text)
    out: list[Finding] = []
    err = lambda rid, msg: out.append(_finding(rid, Severity.ERROR, msg, path))  # noqa: E731
    warn = lambda rid, msg: out.append(_finding(rid, Severity.WARNING, msg, path))  # noqa: E731
    info = lambda rid, msg: out.append(_finding(rid, Severity.INFO, msg, path))  # noqa: E731

    if not doc.has_frontmatter:
        err("DEF001", "Missing YAML frontmatter block (--- name/description ---).")
        return out
    name, description = doc.fields.get("name"), doc.fields.get("description")
    if not isinstance(name, str) or not _NAME.match(name) or len(name) > 64:
        err("DEF002", f"`name` must be kebab-case, at most 64 chars (got {name!r}).")
    if not isinstance(description, str) or not description.strip():
        err("DEF003", "`description` is required: it is how Claude decides when to use this.")
    elif len(description) > MAX_DESCRIPTION:
        warn("DEF003", f"`description` is {len(description)} chars; keep it under {MAX_DESCRIPTION}.")
    if not doc.body.strip():
        err("DEF006", "The body is empty; it is the agent's system prompt or the skill's instructions.")
    for match in find_secrets(text):
        err("DEF007", f"Possible {match.kind} on line {match.line}; reference secrets by environment variable.")
    if kind == "agent":
        _lint_agent(doc, err, warn, info)
    elif kind == "skill":
        _lint_skill(doc, path, name, warn)
    return out


def _lint_agent(doc, err, warn, info) -> None:
    model = doc.fields.get("model")
    if not doc.fields.get("tools"):
        warn("DEF004", "No `tools` list: the agent inherits every tool. Grant the least it needs.")
    if model is not None and model not in _MODEL_ALIASES and resolve_model(model) is None and not str(model).startswith("claude-"):
        warn("DEF005", f"Unknown model {model!r}; use sonnet, opus, haiku, fable, inherit or a full claude-* id.")
    effort = doc.fields.get("effort")
    if effort is None:
        info("DEF010", "No `effort`: the model's default applies. Choose it per role (see mas-model-selection).")
    elif str(effort) not in EFFORT_LEVELS and not str(effort).isdigit():
        err("DEF010", f"`effort` {effort!r} is not one of {', '.join(EFFORT_LEVELS)}.")
    if asks_for_visible_reasoning(doc.body):
        resolved = resolve_model(model)
        message = "The prompt asks for reasoning in the reply; ask for a short explanation or a summary of actions instead."
        if resolved is not None and not resolved.reasoning_extraction_refusals:
            warn("DEF011", message)
        else:
            err("DEF011", message + " Fable 5.1, Opus 5.5 and Sonnet 5.5 may refuse it (reasoning_extraction).")


def _lint_skill(doc, path, name, warn) -> None:
    folder = _SKILL_PATH.search(str(path).replace("\\", "/"))
    if folder and isinstance(name, str) and name != folder.group(1):
        warn("DEF009", f"Skill name {name!r} differs from its folder {folder.group(1)!r}.")
    if doc.body.count("\n") > MAX_SKILL_LINES:
        warn("DEF008", f"SKILL.md body exceeds {MAX_SKILL_LINES} lines; move detail into references/.")
    if asks_for_visible_reasoning(doc.body):
        warn("DEF011", "The skill asks for reasoning in the reply; newer models may refuse it (reasoning_extraction).")


def short_path(path: str) -> str:
    parts = PurePosixPath(str(path).replace("\\", "/")).parts
    return "/".join(parts[-3:])

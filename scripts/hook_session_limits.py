#!/usr/bin/env python3
"""SessionStart: remind Claude of the Claude Code limits and the mas-architect commands.

The paragraph is the documented platform contract every design must fit
(the same numbers MAS016 checks); the command list tells Claude what the
plugin can do without reading its README.
"""

from __future__ import annotations

import sys

from mas_lint.hookio import run
from mas_lint.rules.platform import (
    SUBAGENT_CONCURRENCY,
    SUBAGENT_NESTING,
    WORKFLOW_ADVISORY,
    WORKFLOW_AGENTS_PER_RUN,
    WORKFLOW_CONCURRENCY_DEFAULT,
    WORKFLOW_CONCURRENCY_MAX,
    WORKFLOW_MAX_ITEMS,
)

_NESTING_WORDS = {3: "three"}

COMMANDS = (
    ("new", "design a multi-agent system from a task description (writes a .mas.json spec)"),
    ("lint", "check a spec against the research-backed rules"),
    ("models", "recommend a model and effort level per agent role"),
    ("audit", "review an existing multi-agent setup (agents, skills, hooks) against the rules"),
    ("baseline", "plan the single-agent baseline at matched budget before building a team"),
    ("generate", "turn a spec into Claude Code orchestration (subagents or workflows)"),
    ("review", "blind critique of a spec by a critic that did not design it"),
    ("verify", "design selection, verification and monitoring: selector, judge rubric, belief probes, closure test"),
)


def limits_paragraph() -> str:
    nesting = _NESTING_WORDS.get(SUBAGENT_NESTING, str(SUBAGENT_NESTING))
    return (
        f"Claude Code limits for multi-agent designs: spawning fails past {SUBAGENT_CONCURRENCY} concurrent subagents "
        f"per session by default (raise CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS to change it); subagents nest up to {nesting} "
        "levels below the main conversation and each starts with a fresh context, returning only its final summary. "
        f"Dynamic workflows run {WORKFLOW_CONCURRENCY_DEFAULT} concurrent agents by default, configurable from 1 to "
        f"{WORKFLOW_CONCURRENCY_MAX}, with {WORKFLOW_AGENTS_PER_RUN:,} agents per run, up to {WORKFLOW_MAX_ITEMS:,} items "
        f"in a single parallel() or pipeline() call, and an advisory warning above {WORKFLOW_ADVISORY} agents or 1.5 million "
        "projected tokens. Agents with matching configurations share a prompt cache; when several start at once the "
        "rest wait up to 5,000 ms to read the first one's cached prefix, so keep their prefixes identical."
    )


def commands_paragraph() -> str:
    rows = "\n".join(f"- /mas-architect:{name}: {what}" for name, what in COMMANDS)
    return f"mas-architect commands:\n{rows}\n- /mas-panel: open the control panel with the last lint report."


def handle(_event: dict) -> dict:
    text = limits_paragraph() + "\n\n" + commands_paragraph()
    return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}


if __name__ == "__main__":
    sys.exit(run(handle))

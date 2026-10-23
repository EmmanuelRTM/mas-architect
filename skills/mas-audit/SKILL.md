---
name: mas-audit
description: Audit an existing multi-agent system (code, workflow scripts, agent files, prompts or a .mas.json spec) against the ten evidence-based practices and known failure modes - correlated agents, voting over big pools, summarizing orchestrators, stateful managers, self-grading, missing owners and monitors, spurious parallelism, unbounded context, critique on graded objectives, herding, collusion and hidden belief infection. Use when reviewing, debugging or hardening an agent team, or when it costs more than one agent without beating it.
---

# Audit a multi-agent system

The checklist and the failure-mode table are in `references/checklist.md`, so a reviewer that must not write files (the `mas-critic` agent) can read only that file. The steps below are for an auditor that may write.

## Steps

1. **Inventory.** Find the agents, their prompts and models, how they are spawned and how results merge. Search for agent files (`.claude/agents/`, `agents/`), workflow scripts, orchestration code, and any `*.mas.json`.
2. **Reconstruct the spec.** If no spec exists, write one as `audit.mas.json` describing the system as it *is*, not as it should be. Mark unknown values with a `"TODO"` string rather than guessing. Format in `mas-design/references/spec-format.md`.
3. **Lint deterministically.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" lint audit.mas.json`. The hook also writes `.mas/last-report.json` for the panel.
4. **Check what a linter cannot see.** Walk `references/checklist.md` and cite file and line for each item's evidence.
5. **Independent review.** Give the spec path (not your notes) to the `mas-critic` agent; merge its findings with yours, keeping both sources.
6. **Report.** Lead with the three changes that most likely raise the team's final answer per token. For each finding: practice, evidence in the code, fix, and the paper or guide behind it (evidence summaries in `mas-selection-verification/references/evidence.md` and `mas-patterns/references/patterns.md`). Put the full list after the top three.

---
name: mas-design
description: Design a multi-agent system end to end (team shape, roles, model and effort per role, communication, selection, verification, monitoring) as a lintable .mas.json spec, then turn it into Claude Code agents or a workflow. Use when someone wants to build, scale or restructure a team of agents, subagents, a swarm, an orchestrator-worker setup or a deep-research pipeline.
---

# Design a multi-agent system

The 2026 evidence is blunt: adding agents raises the chance that *someone* finds the answer far more than it raises the team's final answer. Selection, context growth and verification are the binding constraints. Design for those first and treat agent count as the last knob.

## Workflow

Track these steps in a checklist and finish each before the next.

1. **Frame the task.** Get the goal, the success metric, the budget (tokens, wall-clock, money) and how a result is checked. If any is unknown, make a stated assumption and move on.
2. **Baseline first (P1).** Ask for, or plan, the strongest single-agent run at the same budget. Record it in `baseline.single_agent_score`. If the single agent is already near the ceiling, recommend *not* building a team and stop.
3. **Classify the task shape.** Pick exactly one `task.shape` from `references/task-shape-matrix.md` and read only that row's architecture. The shape decides the architecture; the team never decides the shape.
4. **Pick the pattern.** Load the `mas-patterns` skill for the pattern that row names. Copy the closest example from `${CLAUDE_PLUGIN_ROOT}/templates/examples/` as the starting spec.
5. **Assign roles, models and effort.** Use the `mas-model-selection` skill (or the `mas-model-planner` agent) to set `model` and `effort` on every agent. Then run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" recommend <spec>` to compare against the role table. Then give every agent its `skills` list following `references/skill-assignment.md`: preload only what the role runs every time (at most 4), and give judges rubrics, not the generators' playbook.
6. **Wire state, communication and ownership.** State lives in the harness (files, a ledger), never in a coordinator's chat. Every task gets `owner`, `start_condition` and `done_criterion`. Exploration stays private; share claims, not full solutions.
7. **Choose selection and verification.** Load `mas-selection-verification`. Spend on an evidence-grounded or bias-controlled selector and a judge that did not do the work, not on more voters.
8. **Write the spec.** Save it as `<name>.mas.json` (format in `references/spec-format.md`). The plugin's hook lints it on every write: errors block, warnings come back as context. Fix every error; justify or fix each warning.
9. **Independent review.** Hand only the spec file path to the `mas-critic` agent. Do not pass your rationale; a reviewer that sees it anchors on it.
10. **Generate the artifacts.** For each agent, write a Claude Code agent file (`.claude/agents/<id>.md`) with `model`, `effort`, `skills` (from the spec; subagents do not inherit the parent's skills), a minimal `tools` list and a prompt built by the `mas-prompt-writer` agent for that model. For fan-out work, write a workflow or orchestration prompt that respects the limits in `references/limits-and-budget.md`.
11. **Run and watch.** Run `/mas-panel` to open the control panel (live agents, concurrency vs limit, spec health, model plan). Evaluate over at least three repeated runs before claiming a gain.

## Non-negotiables

- No team without a measured single-agent baseline at matched budget.
- No majority vote over a large pool as the final selector.
- No summary handoff into the merge step; pass raw snippets with sources.
- No judge that generated the candidates it grades.
- No coordinator that accumulates context across epochs.
- No secrets in specs or agent files; reference environment variables.

## Output

Deliver: the `.mas.json` spec (lint-clean), a one-paragraph design note covering shape, pattern, why this team beats the baseline and the main risk, the agent files, and what to measure on the first runs. Keep the design note short; the spec carries the detail.

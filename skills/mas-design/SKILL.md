---
name: mas-design
description: Design a multi-agent system end to end (closure criteria, baseline, team shape, roles, model and effort per role, communication, selection, verification, monitoring, budget) as a lintable .mas.json spec, then turn it into Claude Code agents or a workflow. Use when someone wants to build, scale or restructure a team of agents, subagents, a swarm, an orchestrator-worker setup or a deep-research pipeline.
---

# Design a multi-agent system

The 2026 evidence is blunt: adding agents raises the chance that *someone* finds the answer far more than it raises the team's final answer. Selection, context growth, verification and closure are the binding constraints. Design for those first and treat agent count as the last knob.

## Workflow

Track these steps in a checklist and finish each before the next.

1. **Frame the task.** Get the goal, the success metric and its ceiling, the budget (tokens, wall-clock, money) and how a result is checked. If any is unknown, make a stated assumption and move on.
2. **Write the closure criteria.** Agents handle local, checkable sub-steps and fail at closing the loop: full research closure in 32.7% of attempts and in all three runs on only 18.0% of tasks (2610.21767); control testing at 11.45–15.78% (2609.05079); about 86% of the best model's deficit was failed delivery (2610.24087). Record in `task.closure_criteria` what "closed" means: controls, validation, delivery/feasibility, and success on repeated runs. Every `done_criterion` and the evaluation step refer back to these. Procedure in the `mas-evaluation` skill.
3. **Baseline first (P1).** Run, or plan, the strongest single-agent configuration at the same budget, at least three times (`baseline.runs ≥ 3`), on the same metric, and record `baseline.single_agent_score` with `baseline.max_score` (the metric's ceiling). If the single agent is near the ceiling as defined in `references/task-shape-matrix.md` ("When a team is the wrong answer"), recommend *not* building a team and stop.
4. **Pilot ρ and budget arithmetic.** From the baseline runs (or a short replica pilot), estimate the error correlation ρ as the share of failures that replicas share, and write it to `budget.expected_error_correlation`. Compute N_eff and the expected cost (baseline tokens × 1.41–3.31× subagent overhead × N) with the formulas in `references/limits-and-budget.md`; record `budget.expected_tokens_per_instance`. If N_eff is close to 1, more replicas buy nothing: spend on selection instead.
5. **Classify the task shape.** Pick exactly one `task.shape` from `references/task-shape-matrix.md` and read only that row. Set `task.parallelism` to `replica` (several complete solution paths), `structural` (concurrent parts of one path) or `both`; the two are complementary, pay most at intermediate difficulty and cost tokens (TIPEX 2608.05791). The shape decides the architecture; the team never decides the shape.
6. **Pick the pattern.** Load the `mas-patterns` skill for the pattern that row names. Copy the closest example from `${CLAUDE_PLUGIN_ROOT}/templates/examples/` as the starting spec.
7. **Assign roles, models and effort.** Use the `mas-model-selection` skill (or the `mas-model-planner` agent) to set `model` and `effort` on every agent, then run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" recommend <spec>`. Give every agent its `skills` list following `references/skill-assignment.md` (preload only what the role runs every time, at most 4; judges get rubrics, not the generators' playbook) and a pruned `tools` list.
8. **Wire state, communication and ownership.** State lives in the harness (files, a ledger), never in a coordinator's chat. Every task gets `owner`, `start_condition`, `done_criterion` and `monitor`: the delegator that watches progress and recovers the task when it stalls (Responsibility-Centered Coordination: 63.0 vs 44.3 for AgentVerse; 72.8 → 46.7 when the protocol is removed, 2610.21243). Exploration stays private; share claims, not full solutions. Set `context_policy` so stale tool output is dropped, not summarized (`references/limits-and-budget.md`).
9. **Choose selection and verification.** Load `mas-selection-verification`. Spend on an evidence-grounded or bias-controlled selector and a judge that did not do the work, not on more voters. The `mas-verification-designer` agent writes the selector procedure and the judge rubric.
10. **Design monitoring.** Heartbeats with progress inferred from tool-call evidence, peers and the supervisor overriding self-reports (`monitoring.heartbeat: true`, `monitoring.progress_check: peer_override`); private belief probes whenever agents talk (`monitoring.belief_probes: true`); a commitment log whenever agents share resources or talk (`monitoring.commitment_log: true`); cost tracked per agent (`monitoring.track_cost: true`); `monitoring.repeated_runs ≥ 3`; progress measured in critical-path steps (`monitoring.critical_path_steps: true`). Protocols in the `mas-evaluation` skill.
11. **Write the spec.** Save it as `<name>.mas.json` (format in `references/spec-format.md`). The plugin's hook lints it on every write: errors block, warnings come back as context. Fix every error; justify or fix each warning.
12. **Independent review.** Hand only the spec file path to the `mas-critic` agent. Do not pass your rationale; a reviewer that sees it anchors on it.
13. **Generate the artifacts.** For each agent, the `mas-prompt-writer` agent writes a Claude Code agent file (`.claude/agents/<id>.md`) with `model`, `effort`, `skills` (subagents do not inherit the parent's skills), a minimal `tools` list and a prompt for that model. The `mas-orchestration-writer` agent writes the lead-agent prompt or the workflow script using the `mas-orchestration` skill. The `mas-verification-designer` agent writes the selector procedure, the judge rubric skill and the monitoring protocol using `mas-evaluation`.
14. **Run, watch and evaluate.** Run `/mas-panel` to open the control panel (live agents, concurrency vs limit, spec health, model plan). Compare against the baseline at matched budget across at least three repeated runs, scoring closure criteria, not only the metric, before claiming a gain.

## Non-negotiables

- No team without a measured single-agent baseline at matched budget (≥3 runs).
- No team funded by splitting one agent's budget across its members.
- No majority vote over a large pool as the final selector.
- No summary handoff into the merge step: pass raw snippets with sources. Compact summaries are allowed only when the merger has `merge.recall_tool: true` so it can pull the full transcript behind any summary (DAGent).
- No critique or review rounds on graded optimization objectives (`references/task-shape-matrix.md`).
- No judge that generated the candidates it grades.
- No coordinator that accumulates context across epochs.
- No task without an owner and a monitor.
- No secrets in specs or agent files; reference environment variables.

## Output

Deliver: the `.mas.json` spec (lint-clean), a one-paragraph design note covering shape, pattern, why this team beats the baseline, the budget arithmetic and the main risk, the agent files, and what to measure on the first runs. Keep the design note short; the spec carries the detail.

---
name: mas-orchestration
description: Turn a lint-clean .mas.json spec into Claude Code orchestration - choose subagents vs a workflow from platform.runtime, write the lead-agent prompt (every delegation with owner, start condition and done criterion; evidence written to files; model-specific mid-turn message and time-signal rules), respect Claude Code concurrency and workflow limits, share prompt caches, schedule fork-and-flush or session splits, prune tools and set the context policy, and fill the budget table. Use when writing the orchestration prompt, workflow script or delegation templates for an agent team.
---

# From spec to Claude Code orchestration

The spec says what the team is; this skill says how Claude Code runs it. Delegation rules and the prompt template are in `references/lead-prompt.md`; platform limits, cache sharing and the budget table are in `references/workflow-limits.md`. Model-specific prompt text stays in `mas-model-selection/references/prompting-rules.md`.

## Procedure

1. **Pick the runtime from `platform.runtime`.**
   - `claude-code-subagents`: the lead is an interactive or headless Claude Code session; each spec agent becomes `.claude/agents/<id>.md`; the lead delegates with the Agent tool. Use when the team fits the subagent concurrency and nesting limits in `references/workflow-limits.md` and when a human may watch.
   - `claude-code-workflow`: a workflow script runs the fan-out (`parallel()`, `pipeline()`), with `maxConcurrency` set explicitly when `platform.max_concurrency` exceeds the default 16. Use for large replica pools, batch evaluation and fixed pipelines.
   - `custom`: write the harness loop yourself; the same delegation rules apply.
2. **Write the lead-agent prompt** from `references/lead-prompt.md`: role, the task list with owner / start condition / done criterion / monitor copied from `tasks[]`, the delegation template, the merge rule (`merge.input`, `merge.recall_tool`), the monitoring duties (`monitoring.*`), and the model-specific block for the lead's model.
3. **Write the per-agent files** (or confirm the `mas-prompt-writer` output): `model`, `effort`, `skills`, a pruned `tools` list matching `context_policy.prune_unused_tools`.
4. **Set the schedule** from `state.reset_policy`: fork-and-flush checkpoints, session splits at the inflection point, or the prune schedule (`references/workflow-limits.md`, "Schedules").
5. **Set the context policy** per agent from `context_policy`: retained tool responses, drop (never summarize) stale output, tools pruned.
6. **Fill the budget table** in `references/workflow-limits.md` and compare the projected total against the single-agent baseline and the platform advisories.
7. **Hand off to evaluation**: the run plan names the metric, closure criteria and run count from the `mas-evaluation` protocol file.

## Rules the lead prompt must encode

- Every delegation names an owner, a start condition and a done criterion; the `spawn-contract` hook flags any delegation without one.
- Subagents write evidence to files and return the path plus a 3-line summary; the lead never merges from summaries without a recall tool.
- The lead keeps working while subagents run (Fable 5.1) and does not treat a text-only end of turn as completion (Opus 5.5).
- Peer messages, heartbeats and time signals go to subagents as a text block after the last `tool_result` in the user turn, never inside a `tool_result`; no per-step countdowns on Sonnet 5.5 or Fable; the elapsed-time budget line is for Opus 5.5 leads only.
- The lead monitors by tool-call evidence (`monitoring.progress_check: peer_override`) and recovers stalled tasks itself; it is the `monitor` of every task it delegated unless the spec names another.

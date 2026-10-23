# Claude Code limits, cache sharing, schedules and the budget table

This file is the only home of the platform numbers; other skills point here. Formulas (N_eff, cost, session arithmetic) are in `mas-design/references/limits-and-budget.md`.

## Claude Code limits (documented, Oct 2026)

| Runtime | Limit |
|---|---|
| Subagents (`claude-code-subagents`) | 20 concurrent per session by default, configurable through `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`; subagents nest up to 3 levels below the main conversation; no cap on the total spawned over a session; each starts with a fresh, isolated context and returns only its final summary |
| Dynamic workflows (`claude-code-workflow`) | 16 concurrent agents by default, configurable 1–256 (`maxConcurrency`); 1,000 agents per run; up to 4,096 items in a single `parallel()` or `pipeline()` call; advisory warning above 25 agents or 1.5M projected tokens; agents with matching configurations share a prompt cache, and when several start at once all but the first wait up to 5,000 ms by default to read the first one's cached prefix |

The linter mirrors these: `platform.max_items` above 4,096 is an error; `max_concurrency` above 16 on a workflow without an explicit `maxConcurrency`, or more than 20 subagent instances with no `max_concurrency`, draws a finding; a budget above 1.5M tokens on a workflow gets the advisory note.

Codex documents a per-session cap on concurrent threads without a numeric default; Kimi Code states no numeric limits; Kimi's consumer Agent Swarm page claims up to 300 simultaneous subagents (a screenshot caption says 100). Most research tested 2–30 reasoning agents, so these ceilings sit far above the evidence: scale in steps.

## Prompt-cache sharing

- Agents with identical configuration (system prompt, tools, model, effort) share one prompt cache in workflows; the 5,000 ms stagger is the price of the shared prefix. Make replica configs byte-identical and put per-instance differences (instance number, evidence path) in the first user message, not the system prompt.
- Keep the fixed prefix stable: no mid-session edits to `system` or `tools`, no rewriting of earlier turns, nudges appended as turn-scoped system messages. Changing top-level `effort` between requests invalidates the cache; use per-message effort changes.
- Stale tool output is dropped, not summarized (`context_policy.stale_output: "drop"`); summarizing rewrites the prefix. Keep the latest `context_policy.retained_tool_responses` (12 in AKV) tool responses.
- Tool pruning: give each agent only the tools it calls (`context_policy.prune_unused_tools: true`); unused tool descriptions are billed every turn.

## Schedules

Encode `state.reset_policy` in the harness; definitions and evidence in `mas-design/references/limits-and-budget.md` and `mas-patterns/references/patterns.md` §3.

- `fork_and_flush`: at each checkpoint (fraction of budget), snapshot the workspace, start `branches` fresh sessions on it with empty chat and about 6% of budget each, score, continue the best. In a workflow this is a `parallel()` of `branches` items per checkpoint followed by a selection step; with subagents, the lead spawns `branches` workers on copies of the workspace.
- `session_split`: `sessions = ⌈budget ÷ inflection_tokens⌉`; each session starts with the files and the harness ledger, never the previous chat.
- `prune_schedule`: run `schedule[0]` sessions, keep the best `schedule[1]`, continue, until 1; each stage gets an equal slice of the budget unless the spec says otherwise.
- `stateless_epochs`: the advisor runs once per epoch in a new session on a harness-built summary; workers are fresh per assignment.

## Budget table template

Fill one row per agent in the spec and a total; compare the total against the single-agent baseline at the same budget before running.

| Agent | N | ρ (pilot) | N_eff | Tokens per instance (baseline × 1.41–3.31×) | Sessions / resets | Projected tokens | Projected wall-clock |
|---|---|---|---|---|---|---|---|
| section-researcher | 6 | 0.4 | 2.0 | 120,000 | 1 | 720,000 | 25 min (parallel) |
| global-editor | 1 | – | – | 90,000 | 1 | 90,000 | 10 min |
| citation-verifier | 1 | – | – | 40,000 | 1 | 40,000 | 5 min |
| **Total** | 8 | | | | | **850,000** | ~40 min critical path |

Checks on the total: below `budget.max_tokens`; below 1.5M projected tokens on a workflow or justified against the advisory; concurrent instances within the runtime's limit; the single-agent baseline run at the same 850,000 tokens (one run, or best-of-k) is the comparison in the evaluation protocol. Time is estimated on the critical path, not the sum of agent times.

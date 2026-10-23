---
name: mas-model-selection
description: Choose the Claude model (Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5) and the effort/reasoning level for every agent in a multi-agent system, plus the per-model prompt rules each agent's instructions must follow (grounding, mid-turn messages, time signals, max_tokens). Use when assigning models or effort to agents, subagents or workflow steps, when a team costs too much or runs too slowly, or when writing agent frontmatter.
---

# Model and effort per role

Effort is the main control for quality, latency and cost on every current Claude model, and level names do not transfer between models. Decide model and effort per role, write both into the spec and the agent files, then sweep effort on your own evals.

## Procedure

1. List each agent's role, instance count, and whether it searches, codes, judges or routes.
2. Start from the role table below (also encoded in `scripts/mas_lint/model_advisor.py`; run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" recommend <spec>`).
3. Adjust for the constraints in `references/model-effort-guide.md`: fan-out multiplies cost, low effort weakens search and verification, some thinking modes are rejected at some efforts, and mixing tiers is safe only in independent replica pools.
4. Write `model`, `effort` and, when it matters, `thinking` and `max_tokens` on each agent in the spec. In Claude Code agent files use `model: opus|sonnet|haiku|fable` and `effort: low|medium|high|xhigh|max`.
5. Write each agent's prompt with the rules in `references/prompting-rules.md` for its model, or delegate that to the `mas-prompt-writer` agent.
6. Keep `xhigh`/`max` only where an eval shows a gain, and record it in `effort_justification`.

## Starting table

| Role | Model @ effort | Why |
|---|---|---|
| Orchestrator / advisor (thin, stateless) | Opus 5.5 @ medium | Coordinator tokens are <1% of the team's when stateless, so strong reasoning is cheap there |
| Orchestrator for ambiguous science or multi-day autonomy | Fable 5.1 @ high | Strongest long-horizon autonomy and parallel-subagent management; on MIRA Bench, which tests judgment about when to delegate to subagents, Claude Fable 5 scored 72.9 vs 64.1 for Kimi K3 (K3 report; Fable 5.1 unreported) |
| Planner (ensemble) | Opus 5.5 @ high | The plan fixes what every worker builds on |
| Worker, large-repo coding (`codebase_long`) | Opus 5.5 @ medium | Strongest multistep repo work, fewer steps |
| Worker, optimization loops | Sonnet 5.5 @ high | Parallel workers multiply cost; high suits long, hard tasks |
| Worker, well-specified tasks | Sonnet 5.5 @ medium | Balanced; raise to high for longer tasks |
| Solver replicas (`short_verifiable`) | Haiku 5.5 @ medium, mixed with other families | Diversity beats depth in an independent pool; spend on the selector |
| Researcher (search-heavy) | Sonnet 5.5 @ high | Low effort makes models search less and answer from memory |
| Editor / merger | Opus 5.5 @ medium | The merge step is where citations break; Opus 5.5 is much less likely to cite the wrong source |
| Judge / verifier / critic | Opus 5.5 @ high, memoryless, off the generators' model | Code review with more bugs caught and fewer false alarms |
| Selector | Haiku 5.5 @ medium | Evidence-grounded selection is cheap; spend on signal, not size |
| Router over top-K | Haiku 5.5 @ low | High-volume, short decisions |

Defaults if you set nothing: Fable 5.1 `high`, Opus 5.5 `medium`, Sonnet 5.5 `high` (API), Haiku 5.5 `medium`. Fable 5.1 at `low` is often competitive on cost per task with Opus and Sonnet while scoring higher, so include it when a smaller model would otherwise run at higher effort.

## Hard rules the linter enforces (MOD)

- MAS022: every Claude agent declares a valid `effort`.
- MAS023: `xhigh`/`max` on a role with ≥3 instances, a router or a selector needs `effort_justification` (warning); any other agent at `xhigh`/`max` without one gets an info.
- MAS024: low effort on researchers or long-running generators with Haiku, Fable or Sonnet is flagged.
- MAS025: documented rejections are errors (Opus 5.5 cannot disable thinking; Sonnet 5.5 `between_tools` above `high`; Haiku 5.5 `disabled` above `high`); undocumented combinations get a warning ("not documented in the model's guide").
- MAS026: agent instructions must not request visible chain-of-thought in the reply (`reasoning_extraction` refusal on Fable 5.1, Opus 5.5, Sonnet 5.5; leakage on Haiku 5.5).
- MAS027: set `max_tokens` to 128,000 for long agentic turns (the guides' recommendation; thinking counts toward it) and treat `stop_reason: max_tokens` as failure; the linter's minimum threshold is a plugin heuristic.

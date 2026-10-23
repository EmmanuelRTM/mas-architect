# Platform limits and budget arithmetic

## Claude Code limits (documented, Oct 2026)

| Runtime | Limit |
|---|---|
| Subagents | 20 concurrent per session by default (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`); nest up to 3 levels; no cap on total spawned; each starts with a fresh, isolated context and returns only its final summary |
| Dynamic workflows | 16 concurrent by default, configurable 1–256; 1,000 agents per run; up to 4,096 items per `parallel()`/`pipeline()`; advisory warning above 25 agents or 1.5M projected tokens; agents with matching configs share a prompt cache (later starters wait up to 5,000 ms for the first one's prefix) |

Most research tested teams of 2–30 reasoning agents (one sweep to 200, one to 1,024). Product ceilings sit far above what has been measured, so scale in steps and measure each step.

## Effective team size

`N_eff = N / (1 + (N − 1)·ρ)`, which tends to `1/ρ`. At ρ = 0.9, thirty agents act like 1.1. Estimate ρ from a pilot (how often two replicas fail on the same items) and size the replica pool to about `2·⌈1/ρ⌉` at most. `python3 scripts/mas_lint_cli.py neff 30 0.9` computes it.

## Where the money goes

- Re-reading context, not reasoning, dominates: KV-cache reads were 82.4% of API cost in one analysis (2610.28577). Keep prompts' fixed prefix stable so it caches; drop stale tool output; keep the latest ~12 tool responses.
- 16 of 23 tool descriptions billed every turn were never called; 17% of tasks failed yet consumed 32% of spend (TokenEconomizer). Prune tools per agent and halt failure loops.
- Subagents add 1.41–3.31× token overhead (2610.10263). Delegate only genuinely independent, sizeable work.
- A stateful manager reading ~99K tokens per call costs 8–11% of team tokens; a fresh-session advisor reading ~8K costs <0.6% (2610.07625).

## Session splitting

Long single sessions fall into "idea basins". Splitting 100M tokens into three sessions beat one long session by +264 Elo (2609.15309); fork-and-flush forks four branches with the workspace files but an empty chat at 0%, 33% and 66% of budget (2610.07447). Measure the inflection point where gains per token drop, then split there.

## Time budgets for Opus 5.5 teams

Opus 5.5 paces work to an elapsed-time budget shown after each harness message (e.g. `elapsed 340s / 1200s`), which keeps more agents working in parallel. Set the budget somewhat above the time you want and keep a hard timeout of your own.

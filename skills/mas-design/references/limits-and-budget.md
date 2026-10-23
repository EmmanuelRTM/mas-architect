# Budget arithmetic, context cost, sessions and latency

Platform ceilings (concurrent subagents, workflow limits, prompt-cache sharing) live in `mas-orchestration/references/workflow-limits.md`. Most research tested teams of 2–30 reasoning agents (one simulated-world sweep to 200, one to 1,024), far below product ceilings, so scale in steps and measure each step.

## Effective team size

`N_eff = N / (1 + (N − 1)·ρ)`, which tends to `1/ρ`. At ρ = 0.9, thirty agents act like 1.1 (2609.31563). Estimate ρ from the pilot: the share of failures that two replicas share (procedure in the `mas-evaluation` skill); write it to `budget.expected_error_correlation`. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" neff 30 0.9` computes N_eff.

- Replica pool size: at most about `2·⌈1/ρ⌉` (plugin heuristic; the research gives the formula, not the cap).
- Do not average estimates across replicas on compensatory tasks: shared item-level bias made up about 87% of squared error, so averaging cut error only about 6%, moving order-of-magnitude accuracy from 31.6% at N = 1 to 33.4% at N = 30 even though some agent was within range on 57.3% of items (2609.31563). Select one answer with evidence instead.

## Cost of a team

`expected cost ≈ baseline tokens per run × 1.41–3.31× subagent overhead × N instances`, plus the coordinator. The 1.41–3.31× token overhead of sub-agents was measured in 2610.10263. Record the per-instance figure in `budget.expected_tokens_per_instance` and compare the total against the single-agent baseline at the *same* total budget (the baseline may also run N times and take the best). Delegate only genuinely independent, sizeable work.

## Where the money goes

- Re-reading context, not reasoning, dominates: KV-cache reads were 82.4% of total API cost in one analysis (AKV, 2610.28577). Keep each prompt's fixed prefix stable so it caches.
- **Lever 1, drop stale tool output.** AKV's rolling policy keeps **all** reasoning plus the latest 12 tool responses and drops older tool responses from the cache. It raised the average score 1.7 points while cutting cost 27.7% against threshold-triggered summarization; on SWE-bench Verified with GPT-OSS-120B cost fell 20.0¢ → 9.7¢ while the score rose 40.0 → 43.2 (2610.28577). Drop rather than summarize: summarizing rewrites the prefix and invalidates the cache. Spec: `context_policy.retained_tool_responses: 12`, `context_policy.stale_output: "drop"`.
- **Lever 2, prune tools.** 16 of the 23 tool descriptions billed every turn were never called; 17% of tasks failed yet consumed 32% of spend (TokenEconomizer, 2610.22732). Give each agent only the tools it calls (`context_policy.prune_unused_tools: true`) and halt failure loops.
- **Lever 3, inject learned project facts.** Once a repository has five or more prior tasks, 30% of tool calls repeat an earlier task's action. An outside controller that injects learned project facts, hides unused tools and halts failure loops cut cost 18.4–30.9% on 277 SWE-Bench tasks at comparable Pass@1 (TokenEconomizer). Keep a per-project facts file the harness prepends to worker prompts.
- A stateful manager reading ~99K tokens per call costs 8.39–10.70% of team tokens; a fresh-session advisor reading ~8K costs 0.24–0.51% (SLA, 2610.07625).

## Session splitting and reset schedules

Long single sessions fall into "idea basins" and gain less per token than independent sampling, which gains 400 Elo per tenfold budget (2609.15309). Three documented schedules, encoded in `state.reset_policy.type`:

- **`session_split`.** Measure the inflection point where gains per token drop, then `sessions ≈ budget ÷ inflection_tokens`. On Polyomino Packing, Kimi K2.7's inflection came at 38M tokens, so 100M tokens called for three sessions; splitting three ways beat one long session by +264 Elo (90% interval [+135, +412]) and beat ten 10M-token sessions by +355 (2609.15309). Do not over-split: on MoE load balancing the splits were statistically indistinguishable. Fields: `sessions`, `inflection_tokens`.
- **`prune_schedule`.** Start many, then prune: an adaptive 12 → 5 → 2 → 1 schedule won across harnesses, none of which was reliably superior (2607.18235). Field: `schedule` (strictly decreasing, ends in 1).
- **`fork_and_flush`.** Keep the files, empty the chat, fork at fixed checkpoints. Schedule and ablation in `mas-patterns/references/patterns.md` §3 only. Fields: `branches`, `checkpoints`.

## Latency

- Workers cut wall-clock, not only tokens: going from 1 to 15 Workers cut elapsed time 6.6× on the kernel task and 7.3× on average on FrontierSWE; one Worker needed 98.1 hours at 1B tokens against 39.0 for three (SLA, 2610.07625).
- Measure progress in critical-path steps, not total steps: end-to-end time is set by the critical execution path (LAMaS, 2607.13359, >50% lower latency; Kimi K2.5's PARL counts critical steps). Spec: `monitoring.critical_path_steps: true`.
- Speculative tool execution: a small drafter guesses the next actions and runs them early in copy-on-write sandboxes, keeping them only if checks pass: 1.31× on SWE-bench Verified, 1.35× on Terminal-Bench 2.0, 1.27× on SWE-Marathon at an unchanged resolve rate, costing about 2.1 s of extra compute per wall-clock second saved (TomasuLLM, 2609.38201). Worth it when wall-clock is the constraint, not when tokens are.
- Decentralised dispatch: per-agent routing on backlog and expertise reached 4.7×–22.7× a central dispatcher's throughput, measured only with 3–7 agents (DEALS, 2609.33768).
- Prompt-cache sharing: workflow agents with matching configurations share a prompt cache, and later starters wait up to 5,000 ms for the first one's prefix (`mas-orchestration/references/workflow-limits.md`). Identical configs trade a one-time stagger for cheaper reads across the fan-out.
- Time budgets as a pacing signal are documented for Opus 5.5 only: see `mas-model-selection/references/model-effort-guide.md`.

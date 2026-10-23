---
name: mas-evaluation
description: Measure whether a multi-agent team beats its single-agent baseline and keeps working - baseline at matched budget over repeated runs, error-correlation pilot and effective team size, closure criteria, repeated-run and held-out evaluation, belief probes, heartbeat and peer-override progress checks, commitment logs, critical-path progress and cost per agent. Use when designing the evaluation, monitoring protocol or verification plan for an agent team, or when deciding whether a team's gain is real.
---

# Evaluate and monitor a multi-agent system

Most "the team wins" claims fail one of four checks: the baseline was not run at the same budget, the gain was measured on one run, sub-steps were graded instead of closure, or the transcript was trusted over the agents' private state. This skill gives the protocols that close those gaps. Each protocol is in `references/protocols.md`; formulas live in `mas-design/references/limits-and-budget.md` and the evidence in `mas-selection-verification/references/evidence.md`.

## Procedure

1. **Define closure** (`task.closure_criteria`): controls, validation, delivery/feasibility, repeat-run success. Write these before any run.
2. **Baseline at matched budget** (`baseline.single_agent_score`, `baseline.metric`, `baseline.runs ≥ 3`, `baseline.max_score`). If score / max_score ≥ 0.85 (plugin heuristic), stop: recommend the single agent.
3. **Pilot ρ and N_eff** (`budget.expected_error_correlation`, `budget.expected_tokens_per_instance`). Size the team from N_eff and the cost formula, not from the ceiling.
4. **Repeated-run evaluation** (`monitoring.repeated_runs ≥ 3`): compare the team against the baseline at the same total budget, score closure on every run, report all-runs closure as well as best-run.
5. **Held-out audits** (`verification.held_out_audit_every`) for any loop that optimizes against a proxy.
6. **Live monitoring protocol**: heartbeats with peer override (`monitoring.heartbeat`, `monitoring.progress_check: peer_override`), belief probes when agents talk (`monitoring.belief_probes`), a commitment log when agents share resources or talk (`monitoring.commitment_log`), critical-path progress (`monitoring.critical_path_steps`), cost per agent (`monitoring.track_cost`).
7. **Write the protocol** as a short Markdown file next to the spec (`<name>.eval.md`) listing: metric and ceiling, budget per run, run count, closure criteria, probe schedule, stall rule, cost ledger columns, and the decision rule for "ship the team" vs "keep the single agent".

## Decision rule

Ship the team only when, over ≥3 runs at the same total budget, its mean closure rate and metric both exceed the single agent's, its all-runs closure is not worse, and the cost per closed run is within the budget the design note promised. A gain on one run, or on the metric alone with closure flat, is not a gain.

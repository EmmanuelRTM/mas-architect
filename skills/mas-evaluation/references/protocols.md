# Evaluation and monitoring protocols

Step-by-step procedures. Formulas: `mas-design/references/limits-and-budget.md`. Evidence and caveats per paper: `mas-selection-verification/references/evidence.md`.

## 1. Closure criteria

Write `task.closure_criteria` before the first run, one line each, in four groups. Each line must be checkable by a script or a reviewer who did not do the work.

- **Controls:** the comparison that would falsify the result (an ablation, a null baseline, the harness swapped out). Agents reached control testing on only 11.45–15.78% of TruthInsightBench items.
- **Validation:** the required and risk-linked checks (re-derive every number from source data, run the project's tests, verify every citation resolves). Required validation was met 59.6% of the time and risk-linked 47.8% on PhysClosureBench.
- **Delivery / feasibility:** the artifact exists in the form asked for and is feasible (builds, runs within constraints, passes the client's hard limits). About 86% of the best model's deficit on OR-License was failed delivery, and feasibility varied 43.23 points across models while conditional quality varied 4.09.
- **Repeat-run success:** closure reached on all runs of the evaluation, not the best one (32.7% of attempts vs 18.0% of tasks in all three runs).

Every `tasks[].done_criterion` must point at one of these lines or at an artifact a line consumes.

## 2. Single-agent baseline at matched budget

1. Pick the strongest single agent you would ship (model, effort, tools, skills), not a weak strawman.
2. Fix the total budget B (tokens, wall-clock, money) the team will get. The single agent gets the same B: either one run of B, or `k` runs of B/k with best-of-k selection by the same selector the team will use. Report both when they differ.
3. Run it at least three times (`baseline.runs`). Record mean, minimum and all-runs closure.
4. Record `baseline.single_agent_score`, `baseline.metric` and `baseline.max_score` (the ceiling of the metric: 100 for a percentage, the oracle score for a pool, the expert's score for a deployment-adjusted metric).
5. Near-ceiling check: if `single_agent_score / max_score ≥ 0.85` (plugin heuristic; the Nature MI threshold is task-specific and predicted the coordination effect in 94% of validation configurations), recommend the single agent and stop.

## 3. Error-correlation pilot and effective team size

1. From the baseline runs, or a pilot of 2–4 replicas on the same items, list the items each replica failed.
2. ρ ≈ (items failed by both replicas) ÷ (items failed by at least one), averaged over replica pairs. This is a plugin approximation of the error correlation in the N_eff model; the paper fits ρ to accuracy curves.
3. Write ρ to `budget.expected_error_correlation`; compute `N_eff = N / (1 + (N − 1)·ρ)` with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" neff N ρ`.
4. If N_eff < 2 at the planned N, replicas buy nothing: cut N and spend on the selector, or decorrelate (different families, different retrieval, different starting files).
5. Expected cost = baseline tokens per run × 1.41–3.31× (subagent overhead) × N, plus the coordinator; write the per-instance figure to `budget.expected_tokens_per_instance`. Do not fund the team by splitting B across members.

## 4. Repeated-run evaluation

1. Run the team and the baseline at the same total budget, ≥3 times each (`monitoring.repeated_runs`), on the same items, with the same grader.
2. Score every run against the closure criteria, not only the metric. Report: metric mean and min, closure rate per run, all-runs closure, cost per closed run, wall-clock.
3. Use a grader that did not do the work (`mas-selection-verification/SKILL.md`); if it is an LLM judge, calibrate it on a human-labelled sample before trusting it (expert agreement with PhysClosureBench's grader was 81.8% on atomic criteria and 75.9% on closure).
4. Compare on the hardest subset separately; gains concentrate at intermediate difficulty and selectors behave differently there.
5. Keep a held-out item set that no agent, proxy or prompt was tuned on; in-loop gains overstated held-out gains 2.0–2.6×.

## 5. Held-out audits for proxy-driven loops

Every `verification.held_out_audit_every` iterations (10 in DAPS), evaluate the current best candidate on real, held-out validation. If it is worse than the last audited checkpoint, revert to that checkpoint (DAPS reverted about 2.7 ± 0.9 times per run). Admit no candidate to the archive on a proxy score alone (`verification.real_validation_before_promotion: true`). Note the limit: the audit shapes the trajectory through the gate, so keep a second, never-gated set for the final number.

## 6. Belief-probe protocol

Use whenever agents read each other's messages (`communication.mode` other than `none`).

1. After every round, send each agent a private probe outside the shared channel: "Independently of the discussion, what is your current answer to X and how confident are you?" The probe is not visible to peers and is not written to shared memory.
2. Log private answers next to public messages per round.
3. Decide by round 4: about 80% of eventual infection is in place by then. If any agent's private answer flipped toward a claim it has not verified with evidence, stop the discussion, quarantine the claim as `contested` in the ledger, and re-run the affected sub-task with fresh contexts.
4. Pilot with one planted attacker before trusting the protocol: one attacker in a ten-agent group raised private false-belief adoption from 0.6% to 44.8%. If the probes do not detect that pilot, the protocol is not working.
5. Do not rely on transcripts: with three attackers, agents privately held the false answer in 51.6% of exposed turns but endorsed it publicly in 19.7%.

## 7. Heartbeats, stalls and peer override

1. Each long-running agent emits a heartbeat every `heartbeat_seconds` (`monitoring.heartbeat: true`).
2. The harness records, per heartbeat interval, the tool calls made and artifacts changed. Progress is inferred from that evidence, not from the agent's status text.
3. Stall rule: an interval with zero tool calls and no artifact change is "alive but not progressing" (98% of one CORAL run's last 1,500 sessions made no tool calls). Two consecutive stalled intervals trigger the task's `monitor`.
4. `monitoring.progress_check: peer_override`: the monitor (or a peer with evidence) can mark a task stalled or failed regardless of the owner's self-report; the owner cannot un-mark it without new tool-call evidence.
5. The monitor recovers: restart the task with a fresh context, reassign it, or cut it, and records which (RCM: the delegator stays responsible for monitoring and recovery).

## 8. Commitment log

Use when `platform.shared_resources` is true or agents talk (`monitoring.commitment_log: true`).

- Every promise between agents (resource reservations, "I'll handle X", trades, exclusions) is written to an append-only log with: from, to, what, when, and whether the principal sanctioned it.
- The monitor audits the log each epoch and voids commitments nobody sanctioned.
- No shared memory across runs for agents that share a machine: removing cross-subrun memory dropped coalition formation from 27 to 0 (SCARCE).

## 9. Critical-path progress

Track progress as the number of steps on the critical path completed, not the total steps across agents (`monitoring.critical_path_steps: true`). A team that does more total steps than one agent but no more critical-path steps is spurious parallelism; a team whose critical path equals one agent's full path is serial collapse. Report wall-clock against the baseline too: 1 → 15 workers cut elapsed time 6.6× on SLA's kernel task.

## 10. Cost per agent

Keep a ledger with one row per agent instance per run: input tokens, cache-read tokens, output tokens, tool calls, wall-clock, and whether its task closed. Cache reads were 82.4% of API cost in AKV's analysis, so report them separately. Compare the coordinator's share against the stateless-advisor reference (0.24–0.51% of tokens) and the stateful-manager reference (8.39–10.70%); a coordinator above a few percent is accumulating context. Failed tasks that consume a large share of spend (17% of tasks took 32% of spend in TokenEconomizer's profile) are the first candidates for a halt rule.

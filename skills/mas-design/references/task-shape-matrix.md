# Task shape → architecture

Synthesis of ~75 papers (Jul–Oct 2026). Pick one row. `task.shape` values are the spec's enum. This file holds the architecture and the evidence per shape; the one-line pattern rule is in `mas-patterns/SKILL.md` and the structure, spec fields and failure modes in `mas-patterns/references/patterns.md`.

| `task.shape` | Architecture the evidence favors | Key evidence |
|---|---|---|
| `short_verifiable` (math, QA, multiple choice) | Independent diverse samples, then an evidence-grounded or bias-controlled selector; one or two peers for revision | 1 vs 29 revision peers: 26.5 vs 26.6 pts (2609.31563); TRACE at K=8 ≈ majority vote at K=64 (2609.39912) |
| `optimization` (kernels, heuristics, executable score) | Stateless parallel workers under a thin advisor, or fork-and-flush on a fixed schedule; no full-solution broadcast; no critique rounds; protected evaluator | SLA: 84–93% fewer tokens to match baselines (2610.07625); fork-and-flush +66% vs single run (2610.07447) |
| `codebase_long` (questions/changes cutting across a large repo) | About four agents, joint exploration first, negotiated partition, non-blocking passive awareness, explicit owners and monitors | 32.3% → 62.1% (AgentRadio, 2607.28430); RCM 63.0 vs 44.3 (2610.21243) |
| `cited_report` (long-form research with citations) | Planner ensemble → fixed spec → one researcher per section writing its own citations → global editor; raw snippets to any merge. For deep search with open-ended sub-questions, a batch-grown task graph with a recall tool (DAGent) | DRB-II 33.13 → 48.68 from the harness alone (2609.36071); orchestrator introduced 84.7% of errors (2608.24306); DAGent 61.3 vs 56.0 on BrowseComp-Plus (2609.39154) |
| `routing` (hundreds–thousands of agents or tools) | Retrieval pre-selection with a hard top-K before the LLM router | Full catalog fails at 5,000 cards; pre-selection cuts tokens 98.8% (2610.21113) |
| `expensive_eval` (slow or costly evaluation) | Co-evolved proxy evaluators recalibrated online; real validation before promotion; periodic held-out audits | 59.1% fewer real evaluations (2608.08189); in-loop gains overstated 2.0–2.6× (2609.00077) |
| `judgment_science` (hypotheses, novelty, write-ups) | Co-scientist with a memoryless or blinded reviewer and human taste-setting | Idea-level weaknesses resolved 11.1% vs execution 85.3% (2609.14738); 1.2% novel solutions (2608.13417) |

## When a team is the wrong answer

- **The single agent is near the ceiling.** Coordination's benefit shrinks as baseline capability rises: across 260 configurations, single-agent baseline performance was the most robust predictor of whether coordination helps, and a capability-saturation threshold predicted the coordination effect in 94% of validation configurations (Nature MI 2026, outside the window); the Collaboration Tax shrank with capability and turned negative for the strongest models on constraint puzzles (2608.22152). Plugin heuristic for "near the ceiling": `baseline.single_agent_score / baseline.max_score ≥ 0.85` (the linter warns at this ratio). Record `baseline.max_score` so the check can run.
- **The objective is graded and the plan has critique rounds.** In the Interaction Tax, no multi-agent configuration beat every single-agent baseline in aggregate, and the first critique round made 17 of 30 optimization runs (57%) worse, while pushing none of 30 constraint-task runs into infeasibility (2608.23541). Do not add critique, review or debate rounds on graded optimization objectives; use them only where feasibility, not score, is at stake.
- **The team would be funded by splitting one agent's budget.** Test-Time Communication saw communication collapse when five agents split one agent's budget, and gains only when each agent kept its full budget with an objective score (2609.21032). Never fund a team by dividing the single agent's budget across members; size the budget per instance (`budget.expected_tokens_per_instance`).
- **The task is a bounded fix.** Parallel subagents cut SWE-bench Verified 83.0% → 59.0% while raising long LoopsBench tasks 7.1% → 21.4% (2610.10263).
- **The work cannot be split without cutting across the partition.** Naive division lost architecture questions (15 → 13) in AgentRadio (2607.28430); negotiate the partition after joint exploration or keep one agent.

## Ten practices (what the linter's P1–P10 check)

1. Measure the strong single-agent baseline first, at matched budget, over repeated runs.
2. Generate independently across diverse model families; restrict peer reads during exploration.
3. Spend on selection, not more voters.
4. Keep state in the harness; make agents disposable (fresh context, reset chat, keep files).
5. Cap every read: top-K catalogs, prune unused tools, drop stale tool output.
6. Non-blocking communication and explicit ownership (owner, start, done, monitor, heartbeats, conflict-preserving memory).
7. Hand raw evidence, not summaries, to whatever merges.
8. Separate the judge from the generator.
9. Monitor private beliefs, commitments and repeated runs, not only transcripts and best runs.
10. Train with team-level credit while keeping agents decorrelated.

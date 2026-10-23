# Task shape → architecture

Synthesis of ~75 papers (Jul–Oct 2026). Pick one row. `task.shape` values are the spec's enum.

| `task.shape` | Architecture the evidence favors | Key evidence |
|---|---|---|
| `short_verifiable` (math, QA, multiple choice) | Independent diverse samples, then an evidence-grounded or bias-controlled selector; one or two peers for revision | 1 vs 29 revision peers: 26.5 vs 26.6 pts (2609.31563); TRACE at K=8 ≈ majority vote at K=64 (2609.39912) |
| `optimization` (kernels, heuristics, executable score) | Stateless parallel workers under a thin advisor, or fork-and-flush on a fixed schedule; no full-solution broadcast; protected evaluator | SLA: 84–93% fewer tokens to match baselines (2610.07625); fork-and-flush +66% vs single run (2610.07447) |
| `codebase_long` (questions/changes cutting across a large repo) | About four agents, joint exploration first, negotiated partition, non-blocking passive awareness, explicit owners | 32.3% → 62.1% (AgentRadio, 2607.28430); RCM ablations (2610.21243) |
| `cited_report` (long-form research with citations) | Planner ensemble → fixed spec → one researcher per section writing its own citations → global editor; raw snippets to any merge | DRB-II 33.13 → 48.68 from the harness alone (2609.36071); orchestrator introduced 84.7% of errors (2608.24306) |
| `routing` (hundreds–thousands of agents or tools) | Retrieval pre-selection with a hard top-K before the LLM router | Full catalog fails at 5,000 cards; pre-selection cuts tokens 98.8% (2610.21113) |
| `expensive_eval` (slow or costly evaluation) | Co-evolved proxy evaluators recalibrated online; real validation before promotion; periodic held-out audits | 59.1% fewer real evaluations (2608.08189); in-loop gains overstated 2.0–2.6× (2609.00077) |
| `judgment_science` (hypotheses, novelty, write-ups) | Co-scientist with a memoryless or blinded reviewer and human taste-setting | Idea-level weaknesses resolved 11.1% vs execution 85.3% (2609.14738); 1.2% novel solutions (2608.13417) |

## When a team is the wrong answer

- The single agent already scores near the ceiling: coordination's benefit shrinks as baseline capability rises (Nature MI 2026; Collaboration Tax 2608.22152).
- The task is a bounded fix: parallel subagents cut SWE-bench Verified 83.0% → 59.0% while helping long LoopsBench tasks (2610.10263).
- The work cannot be split without cutting across the partition: naive division lost architecture questions (AgentRadio).

## Ten practices (what the linter's P1–P10 check)

1. Measure the strong single-agent baseline first.
2. Generate independently across diverse model families; restrict peer reads during exploration.
3. Spend on selection, not more voters.
4. Keep state in the harness; make agents disposable (fresh context, reset chat, keep files).
5. Cap every read: top-K catalogs, prune unused tools, drop stale tool output.
6. Non-blocking communication and explicit ownership (owner, start, done, heartbeats, conflict-preserving memory).
7. Hand raw evidence, not summaries, to whatever merges.
8. Separate the judge from the generator.
9. Monitor private beliefs and repeated runs, not only transcripts and best runs.
10. Train with team-level credit while keeping agents decorrelated.

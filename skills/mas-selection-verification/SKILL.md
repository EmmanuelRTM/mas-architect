---
name: mas-selection-verification
description: Choose how a multi-agent team picks its final answer and who checks it - evidence-grounded selectors, bias-controlled judges, cheap trained selectors, memoryless reviewers, cross-fitted verifiers, held-out audits, belief probes, peer-override progress checks and commitment logs. Use when designing the aggregation, judging, verification or monitoring part of an agent team, or when a team finds right answers but returns wrong ones.
---

# Selection and verification

The gap between "someone on the team was right" and "the team answered right" is where extra agents are won or lost. Close it with selection and an independent verifier before adding agents. Numbers and caveats per paper are in `references/evidence.md`; the step-by-step measurement protocols are in the `mas-evaluation` skill.

## Choose a selector

| Situation | Selector | Why |
|---|---|---|
| Rollouts retrieve documents (search, RAG, deep research) | **Evidence-grounded (RGV):** score each rollout by how much of its answer appears in a document it actually retrieved; no logprobs, no extra LLM calls | 84.4% correct picks vs 49.2% for confidence voting when only 1–2 of 8 are right; ~0.3 ms per rollout (2608.24024) |
| Many rollouts, budget for a small trained model | **Trained evidence selector (TRACE):** link the evidence each rollout retrieved into one graph and pick an existing answer | 78.6 vs 75.5 majority at K=16; ~1/258 of AggAgent's GPU-hours (2609.39912) |
| Reasoning answers without retrieval | **Bias-controlled judge** (procedure below) | +3.2–6.2 pts over majority; keeps 98.4% of what majority got right (2610.21290) |
| Executable metric | **Best-of-N by metric** with a protected evaluator | The metric is the selector; protect its code from workers |

**Caveats that change the choice.** Evidence selectors need diverse retrieval: TRACE's gains over voting nearly vanish on RL-trained pools whose rollouts retrieve overlapping evidence (+0.7 and +0.3 points), and RGV's gain shrinks to 0.7 points on reasoning-heavy HLE; on 4.2% of items a wrong rollout with on-topic evidence outscored a correct one. So when the pool reasons rather than retrieves, use bias control; when the pool was trained to retrieve the same way, decorrelate retrieval (different search tools, query rewrites, model families) before trusting an evidence selector.

Avoid: plurality or majority over large pools; confidence-weighted voting for search agents (copied text inflates confidence); LLM aggregators that read every rollout in full (about 122–258× the cost of a trained selector).

## Bias-control procedure (lives only here)

1. Keep one trace per distinct final answer.
2. Rewrite each trace into identical plain prose so style and length cannot sway the judge.
3. Let three judges choose.
4. Inject an adverse bias: show the strongest competitor twice, or reverse the order.
5. Accept only answers that survive the injection; on the hardest items require a hold plus majority support (49.1% vs 18.1% for majority support alone).
Spec: `selection.strategy: bias_controlled`. Evidence base: 220 olympiad problems, open models of 8B–14B.

## Revision

One or two peers capture the revision gain (26.5 vs 26.6 points with 1 vs 29 peers; 2609.31563). More peers cost context and erase diversity. Never run revision or critique rounds on a graded optimization objective (`mas-design/references/task-shape-matrix.md`).

## Verification: a judge that did not do the work

- **Memoryless reviewer:** a fresh context each round so it cannot anchor on earlier drafts.
- **Blinded critic:** pairwise preferences without knowing which agent wrote what.
- **Cross-fitted verifier:** score each item with a solver that never saw its source documents; cut false agreement from 6.1–8.8% to 3.0–3.7% (2609.39102).
- **Decompose-then-verify:** rewrite each claim into explicit premises and check each premise cheaply against the source (PremiseCheck matched a holistic judge at 51.2% of the cost, 2610.21046).
- **Held-out audit:** every ~10 iterations, gate on held-out data and revert to the last faithful checkpoint.
- **Different model:** the judge should not run the only model the generators use.
- **Closure, not atomic criteria:** 36.2% of attempts scoring ≥8/10 on atomic criteria still missed closure (2610.21767); grade against `task.closure_criteria`.

## Monitoring rules

- **Repeated runs:** judge closure across ≥3 runs (`monitoring.repeated_runs: 3`); closure in one run (32.7% of attempts) was far more common than in all three (18.0% of tasks).
- **Belief probes whenever agents talk** (`monitoring.belief_probes: true`): privately ask each honest agent its current belief after every round. With no attackers private false-belief adoption averaged 0.6%; one attacker in a ten-agent discussion raised it to 44.8% (range 19–74%), three to 60.5%. With three attackers, honest agents privately held the false answer in 51.6% of exposed turns but publicly endorsed it in only 19.7%, so transcripts hide most of the damage. About 80% of eventual infection is in place by round 4: probe each round and decide (stop, quarantine, reset) by round 4 (2610.22138).
- **Progress by evidence, not self-report** (`monitoring.progress_check: peer_override`): infer liveness from heartbeats and progress from tool-call evidence; let peers and the supervisor override an agent's self-report (Agent Status Protocol, 2610.21538, abstract only, no evaluation). A session with zero tool calls is stalled: 98% of one CORAL run's final 1,500 sessions made no tool calls while it kept spending (2610.07625).
- **Commitment log** (`monitoring.commitment_log: true`) and **no shared memory across runs** for agents that share resources: five coding agents on one machine formed coalitions and made unsanctioned commitments in up to 79% of rounds with Opus 5; removing cross-subrun memory from GLM-5.3 dropped coalition formation from 27 to 0 (SCARCE, 2610.21029). Set `platform.shared_resources: true` so the linter requires the log.
- **No popularity ranking** (`communication.ranking: none`): popularity drifted about 9× further from quality than in humans under weak social influence and 4× under strong, tracked early movers rather than quality, and LLM populations did not self-correct (2610.30769).

## Spec fields

`selection.strategy`, `selection.candidates`, `selection.revision_peers`, `verification.judge_agents`, judges' `memoryless: true`, `verification.held_out_audit_every`, `task.closure_criteria`, `monitoring.repeated_runs`, `monitoring.belief_probes`, `monitoring.progress_check`, `monitoring.commitment_log`, `communication.ranking`, `platform.shared_resources`.

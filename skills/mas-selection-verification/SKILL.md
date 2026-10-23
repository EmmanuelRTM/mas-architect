---
name: mas-selection-verification
description: Choose how a multi-agent team picks its final answer and who checks it - evidence-grounded selectors, bias-controlled judges, cheap trained selectors, memoryless reviewers, cross-fitted verifiers, held-out audits and belief probes. Use when designing the aggregation, judging, verification or monitoring part of an agent team, or when a team finds right answers but returns wrong ones.
---

# Selection and verification

The gap between "someone on the team was right" and "the team answered right" is where extra agents are won or lost. Close it with selection and an independent verifier before adding agents.

## Choose a selector

| Situation | Selector | Why |
|---|---|---|
| Rollouts retrieve documents (search, RAG, deep research) | **Evidence-grounded:** score each rollout by how much of its answer appears in a document it actually retrieved; no logprobs, no extra LLM calls | RGV: 84.4% correct picks vs 49.2% for confidence voting when only 1–2 of 8 are right; ~0.3 ms per rollout (2608.24024) |
| Many rollouts, budget for a small model | **Trained evidence selector:** link the evidence each rollout retrieved into one graph and pick an existing answer | TRACE: 78.6 vs 75.5 majority at K=16, ~1/258 of AggAgent's GPU-hours (2609.39912) |
| Reasoning answers without retrieval | **Bias-controlled judge:** keep one trace per distinct answer, rewrite each into identical plain prose, three judges choose, then inject an adverse bias (show the strongest competitor twice, reverse order) and keep only answers that survive | +3.2–6.2 pts over majority; keeps 98.4% of what majority got right (2610.21290) |
| Executable metric | **Best-of-N by metric** with a protected evaluator | The metric is the selector; protect its code from workers |

Avoid: plurality or majority over large pools; confidence-weighted voting for search agents (copied text inflates confidence); LLM aggregators that read every rollout in full (122–258× the cost of a trained selector).

## Revision

One or two peers capture the revision gain (26.5 vs 26.6 points with 1 vs 29 peers). More peers cost context and erase diversity.

## Verification: a judge that did not do the work

- **Memoryless reviewer:** a fresh context each round so it cannot anchor on earlier drafts.
- **Blinded critic:** pairwise preferences without knowing which agent wrote what.
- **Cross-fitted verifier:** score each item with a solver that never saw its source documents; cut false agreement from 6.1–8.8% to 3.0–3.7% (2609.39102).
- **Decompose-then-verify:** rewrite each claim into explicit premises, check each premise cheaply against the source (PremiseCheck matched a holistic judge at 51% of the cost).
- **Held-out audit:** every ~10 iterations, gate on held-out data and revert to the last faithful checkpoint.
- **Different model:** the judge should not run the only model the generators use.

## Monitoring

- **Repeated runs:** judge closure across ≥3 runs; all-three-runs success is far rarer than single-run success.
- **Belief probes:** when agents discuss, privately ask each honest agent its current belief each round. One adversarial peer raised private false-belief adoption from 0.6% to 44.8% while only 19.7% of exposed turns showed it publicly (2610.22138). About 80% of infection is in place by round 4, so probe early.
- **Herding:** popularity tracks early movers, not quality, in LLM populations (2610.30769). Do not rank shared messages by citation or vote count alone.
- **Collusion:** agents sharing resources invent coalitions and unsanctioned commitments (SCARCE). Log commitments between agents and audit them.

## Spec fields

`selection.strategy`, `selection.candidates`, `selection.revision_peers`, `verification.judge_agents`, judges' `memoryless: true`, `verification.held_out_audit_every`, `monitoring.repeated_runs`, `monitoring.belief_probes`.

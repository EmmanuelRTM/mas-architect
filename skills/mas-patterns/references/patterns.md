# Pattern catalog

## 1. Diverse pool + selector (`short_verifiable`)

**Wins when** answers are short and checkable and one correct member suffices.
**Structure:** N independent solvers across model families, no communication; an evidence-grounded selector (scores each answer by how much of it appears in documents that rollout retrieved) or a bias-controlled judge (one trace per distinct answer, rewrite to identical plain prose, three judges, then inject an adverse bias such as order swap and keep only answers that survive). Optional revision against one or two peers.
**Spec:** `communication.mode: none`, `selection.strategy: evidence_grounded|bias_controlled`, `selection.revision_peers ≤ 2`, `budget.expected_error_correlation`.
**Failure modes:** copy inflation fools confidence voting (copied web text is ~0.5 nats more confident); correlated replicas cap N_eff near 1/ρ.
**Evidence:** coverage 34.3% → 54.4% at N=30 while plurality captured little (2609.31563); RGV 72.6 → 78.9 vs oracle 92.6 (2608.24024); bias control +3.2–6.2 pts over majority (2610.21290).

## 2. Stateless advisor + isolated workers (`optimization`)

**Wins when** an executable score exists and work runs for hours.
**Structure:** the harness keeps the ledger of candidates and scores. Each epoch a fresh-session advisor reads a harness-built evidence summary and assigns concrete, non-overlapping experiments. Workers run in isolated sandboxes seeing only their assignment and local feedback. A protected evaluator scores.
**Spec:** advisor `stateful: false`; workers `context: isolated`; `state.location: harness`; `verification.evaluator_protected: true`.
**Failure modes:** without assignments, workers duplicate each other (three built the same XML decoder); without isolation progress fell 42.8%; short budgets can reverse rankings (SLA trailed at 175M tokens, won at 700M).
**Evidence:** SLA matched baselines with 84–93% fewer tokens; advisor used 0.24–0.51% of tokens (2610.07625).

## 3. Fork-and-flush (`optimization`)

**Wins when** single runs plateau in different "idea basins".
**Structure:** at 0%, 33% and 66% of budget fork four branches that keep workspace files but start with an empty chat; each explores with ~6% of budget; the best continues.
**Spec:** `state.reset_policy: {type: fork_and_flush, checkpoints: [0, 0.33, 0.66], branches: 4}`.
**Failure modes:** both halves are needed (fork alone 0.57, flush alone 0.55, together 0.71 vs 0.45 single); fixed schedule, not adaptive.
**Evidence:** +66% vs single runs, +44.4% vs best-of-N over 13 tasks (2610.07447).

## 4. Negotiated partition + passive awareness (`codebase_long`)

**Wins when** questions or changes cut across a large codebase.
**Structure:** ~4 agents explore jointly, negotiate a partition with one named owner per sub-question, then work with non-blocking sends and a background listener (wait-for-mention as a background process, so listening costs no LLM calls). A memoryless reviewer traces each claim to file and line.
**Spec:** `planning.joint_exploration: true`, `communication.mode: passive`, task owners, `monitoring.heartbeat: true`.
**Failure modes:** division without negotiation loses cross-cutting questions (15 → 13); ~6.6× single-agent cost.
**Evidence:** 32.3% → 62.1% on SWE-Atlas QnA; passive beat blocking 15–2 (2607.28430).

## 5. Section-parallel research (`cited_report`)

**Wins when** the deliverable is a long, cited report.
**Structure:** three planners propose outlines; a judge consolidates; a critic hunts gaps; the spec is then frozen. One researcher per section runs in its own context and writes its own cited section ("no summary handoff"). A global editor directs local edits only inside owning sections. A citation verifier checks each claim's premises against its snippet.
**Spec:** `planning.fixed_spec: true`, `merge.input: raw_evidence|snippets`, an `editor` agent, verifier in `judge_agents`.
**Failure modes:** the orchestrator introduced 84.7% of final-report errors in NVIDIA AI-Q; snippets instead of notes lifted citation precision 87.6 → 94.1 (2608.24306).
**Evidence:** harness alone lifted DRB-II 33.13 → 48.68 (2609.36071).

## 6. Retrieval router (`routing`)

**Wins when** an orchestrator chooses among hundreds to thousands of agents or tools.
**Structure:** BM25 or an inverted index pre-selects the top K (10–30) agent cards; the LLM router reads only those; an auditor samples routes.
**Spec:** `routing.catalog_size`, `routing.top_k`, `routing.preselection`.
**Evidence:** full catalog failed at 5,000 cards; pre-selection cut tokens 98.8% and cost per query 80× at 1,000 agents; any pre-selection was as good as the fancy one (2610.21113).

## 7. Proxy evaluator loop (`expensive_eval`)

**Wins when** real evaluation is slow or costly.
**Structure:** the model writes and evolves proxy evaluators alongside candidates, fits them to the archive of real outcomes, and only real evaluation admits a candidate. Every ~10 iterations a held-out audit gates progress and reverts to the last faithful checkpoint.
**Spec:** `verification.real_validation_before_promotion: true`, `verification.held_out_audit_every`.
**Failure modes:** a fixed surrogate pushed proxy score up while real fluorescence fell; in-loop gains overstated held-out gains 2.0–2.6×; idea clusters collapse 50–70%.
**Evidence:** 59.1% fewer real evaluations at 99% of the gain (2608.08189); DAPS audits (2609.00077).

## 8. Co-scientist (`judgment_science`)

**Wins when** value is judged rather than measured (hypotheses, novelty, papers).
**Structure:** a scientist agent with memory of drafts; a reviewer that starts fresh each round or a blinded critic giving pairwise preferences; a human sets taste and accepts ideas.
**Spec:** `human_in_the_loop: true`, judge `memoryless: true`.
**Failure modes:** execution weaknesses were fixed 85.3% of the time, idea-level ones 11.1%; one reviewer both guiding and scoring inflates gains.
**Evidence:** 2609.14738, 2610.23839; Dr. Claw is explicitly human-in-the-loop.

## Cross-cutting: shared memory that keeps disagreement

Tag every shared claim `proposed | confirmed | contested | superseded` (LatticeMind: 0.97 vs 0.45 for debate on ConflictBank). Post findings to a bulletin board but keep selected searches isolated so they retain their priors (ArcticSwarm: 82.6% vs 74.5% without isolation and review).

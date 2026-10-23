# Pattern catalog

Structure, spec fields, failure modes and evidence per pattern. Selector and judge procedures (including bias control) are described only in the `mas-selection-verification` skill; budget formulas only in `mas-design/references/limits-and-budget.md`.

## 1. Diverse pool + selector (`short_verifiable`)

**Wins when** answers are short and checkable and one correct member suffices.
**Structure:** N independent solvers across model families, no communication, each with its full budget; then one selector, evidence-grounded when rollouts retrieve documents, bias-controlled when they only reason (procedures and caveats in `mas-selection-verification/SKILL.md`). Optional revision against one or two peers.
**Spec:** `task.parallelism: replica`, `communication.mode: none`, `selection.strategy: evidence_grounded|bias_controlled`, `selection.revision_peers ≤ 2`, `budget.expected_error_correlation`.
**Failure modes:** copy inflation fools confidence voting (copied web text is about 0.50 nats more confident); correlated replicas cap N_eff near 1/ρ; averaging across replicas does not remove shared bias.
**Evidence:** coverage 34.3% → 54.4% at N=30 while plurality captured little (2609.31563); RGV 72.6 → 78.9 vs oracle 92.6 (2608.24024); bias control +3.2–6.2 pts over majority (2610.21290).

## 2. Stateless advisor + isolated workers (`optimization`)

**Wins when** an executable score exists and work runs for hours.
**Structure:** the harness keeps the ledger of candidates and scores. Each epoch a fresh-session advisor reads a harness-built evidence summary and assigns concrete, non-overlapping experiments. Three workers by default run them in parallel, each in a Landlock-isolated sandbox that shows only its assignment and local feedback. An independent evaluator with protected code scores the results.
**Spec:** advisor `stateful: false`, `memoryless: true`; workers `context: isolated`, `count: 3`; `state.location: harness`; `state.reset_policy.type: stateless_epochs`; `verification.evaluator_protected: true`; an `evaluator` agent; `communication.mode: none`.
**Failure modes:** without assignments, workers duplicate each other (three built the same XML decoder); without isolation, kernel progress fell 42.8% in relative terms; short budgets can reverse rankings (SLA trailed on all four FrontierSWE tasks at 175M tokens and won only at 700M); the backbone dominates the loop (in Janus, Gemini 3.1 Pro added 38.7 points of AUBC and Gemini 2.5 Flash subtracted 12.9, 2608.08189). A stalled baseline is a warning: one CORAL run made its last improvement at 231M tokens and spent on to 1B while 98% of its final 1,500 sessions made no tool calls.
**Evidence:** SLA matched SwarmResearch with 93.1% fewer tokens and CORAL with 84.4% fewer; advisor used 0.24–0.51% of tokens vs 8.39–10.70% for a stateful Shepherd; 1 → 15 workers cut elapsed time 6.6× (2610.07625).

## 3. Fork-and-flush (`optimization`)

**Wins when** single runs plateau in different "idea basins".
**Structure (the schedule lives only here):** at 0%, 33% and 66% of budget fork four branches that keep the workspace files but start with an empty chat; each explores with about 6% of the budget; the best branch continues.
**Spec:** `state.reset_policy: {type: fork_and_flush, branches: 4, checkpoints: [0, 0.33, 0.66]}`, `task.parallelism: replica`.
**Failure modes:** both halves are needed (fork alone 0.57, flush alone 0.55, together 0.71 vs 0.45 single); the schedule is fixed, not adaptive (for an adaptive alternative use `prune_schedule`, `mas-design/references/limits-and-budget.md`); LWE-rec regressed.
**Evidence:** +66.0% vs single runs, +44.4% vs best-of-N over 13 tasks; normalized mean 0.78 vs 0.47 single and 0.54 best-of-4 (2610.07447).

## 4. Negotiated partition + passive awareness (`codebase_long`)

**Wins when** questions or changes cut across a large codebase.
**Structure:** about four agents explore jointly, negotiate a partition with one named owner per sub-question, then work with three messaging primitives: *create a thread*, *send a non-blocking message*, and *wait for an @-mention* run as a background OS process, so listening costs no LLM calls (the blocking variant runs the same wait in the foreground). A memoryless reviewer traces each claim to file and line. Each owner's delegator monitors and recovers (RCM).
**Spec:** `task.parallelism: structural`, `planning.joint_exploration: true`, `planning.negotiated_partition: true`, `communication.mode: passive`, tasks with `owner` and `monitor`, `monitoring.heartbeat: true`, `monitoring.progress_check: peer_override`.
**Ladder (SWE-Atlas QnA, Claude Opus 4.6, one run per task, LLM grader):**

| Configuration | Accuracy | Cost per task |
|---|---|---|
| One agent | 32.3% | $2.96 |
| Best of six independent runs | 37.9% | $17.76 |
| Four agents, division only | 39.5% | $5.38 |
| Four agents + negotiation with blocking receive | 51.6% | $15.59 |
| Four agents + passive awareness | 62.1% | $19.45 |

**Failure modes:** division without negotiation loses cross-cutting architecture questions (15 → 13); passive awareness gained 47 rubrics while losing 23; about 6.6× single-agent cost; the ladder is one run per task on one benchmark.
**Evidence:** passive beat blocking on 15 tasks against 2 (p = 0.0023); DeepSeek V4 Pro climbed 29.0% → 50.8% (AgentRadio, 2607.28430); RCM 63.0 vs 44.3, 72.8 → 46.7 without its protocol (2610.21243).

## 5. Section-parallel research (`cited_report`)

**Wins when** the deliverable is a long, cited report.
**Structure:** three Planning Writers propose structures, a Judge consolidates them, a Critic hunts for gaps and a Reviser folds the feedback in; the resulting spec is frozen. One Researcher per section runs concurrently in its own context and writes its own citation-bearing section ("no summary handoff"). A Global Editor reads the full draft and directs Local Editors that revise only their own sections. LongCat has no citation verifier; add one using decompose-then-verify (PremiseCheck, 2610.21046: rewrite each claim into explicit premises and check each against its snippet; see `mas-selection-verification/SKILL.md`).
**Spec:** `task.parallelism: structural`, `planning.fixed_spec: true`, `planning.planner_ensemble: 3`, `merge.input: raw_evidence|snippets`, an `editor` agent, a `reviewer` (Reviser) agent, verifier in `verification.judge_agents`.
**Budget template (LongCat's per-task caps):** 600 model calls, 1,048,576 completion tokens, 500 searches, 500 page reads; realized cost unreported.
**Failure modes:** the orchestrator introduced 84.7% of final-report errors in NVIDIA AI-Q; giving it source snippets instead of researcher notes lifted citation recall 64.5 → 69.7 and precision 87.6 → 94.1, and a citation instruction alone cut the orchestrator's error share 84.7% → 77.0% (2608.24306). One whole-report researcher instead of per-section researchers dropped LongCat's development average 63.91 → 62.07, and a single planner dropped it to 59.56.
**Evidence:** the harness alone lifted DRB-II 33.13 → 48.68 with the previous model; the new model added 2.67 more (2609.36071).

## 5b. Batch-grown task graph (`cited_report`, deep search)

**Wins when** the sub-questions are not known up front (BrowseComp-style deep search, GAIA-style multi-hop tasks).
**Structure:** instead of planning the whole task up front, grow the task graph in batches. Each finished node is labelled `Success`, `Uncertain` or `Not Found`; uncertain nodes are retried up to three attempts; independent nodes run in parallel as ReAct executors. Nodes pass forward only a compact "QueryDoc" summary, and a recall tool lets any dependent node pull snippets from a dependency's full transcript, so compactness does not cost evidence.
**Spec:** `task.parallelism: structural`, `merge.input: snippets`, `merge.recall_tool: true`, per-node tasks with `done_criterion` naming the label and `monitor` set to the graph owner.
**Failure modes:** a compact handoff without the recall tool is the summarizing-orchestrator anti-pattern; retries without a cap loop on `Uncertain`.
**Evidence:** with Qwen3-235B-A22B, 61.3 vs 56.0 on BrowseComp-Plus, 63.1 vs 57.3 on GAIA, 72.0 vs 70.0 on xbench-DeepSearch (DAGent, 2609.39154; GPT-5 numbers and efficiency figures were not in the extracted text).

## 6. Retrieval router (`routing`)

**Wins when** an orchestrator chooses among hundreds to thousands of agents or tools.
**Structure:** BM25 or an inverted index pre-selects the top K agent cards; the LLM router reads only those; an auditor samples routes. K ≈ 20 (chosen on test queries in SSR; tune K on held-out queries). SSR and BM25 were statistically indistinguishable (Holm-adjusted p = 1.000), so any pre-selection step gives most of the gain.
**Spec:** `routing.catalog_size`, `routing.top_k` (≈20), `routing.preselection: bm25|index|embedding` (never `none` above a few dozen cards).
**Evidence:** the full catalog failed at 5,000 cards (about 447,761 tokens, 0% API success); at 1,000 agents pre-selection cut input tokens 98.8%, latency 2.647 s → 0.769 s and cost per query $0.009551 → $0.000119, holding 0.885 accuracy at 5,000 cards (2610.21113).

## 7. Proxy evaluator loop (`expensive_eval`)

**Wins when** real evaluation is slow or costly.
**Structure:** the model writes and evolves proxy evaluators alongside candidates, fits them to the archive of real outcomes, and only real evaluation admits a candidate. DAPS adds three guards: deduplicate each proposal against a memory of the last 200 accepted edits, reweight proposals toward under-covered categories, and every 10 iterations gate progress against a held-out audit, reverting to the last faithful checkpoint (about 2.7 ± 0.9 reverts per run).
**Spec:** `verification.real_validation_before_promotion: true`, `verification.held_out_audit_every: 10`, an `evaluator` agent with `evaluator_protected: true`.
**Failure modes:** a fixed surrogate pushed the proxy score to about 5.6 while measured fluorescence fell to about 2.9; in-loop gains overstated held-out gains 2.0–2.6× by iteration 300; semantic idea clusters collapse 50–70% while surface edit diversity stays flat; the audit still shapes the trajectory through the gate, so it is not fully held out.
**Evidence:** 59.1% fewer real evaluations at 99% of the gain (Janus, 2608.08189); DAPS cut cluster decay 69.1% and improved relative faithfulness 83.7% blind (2609.00077).

## 8. Co-scientist (`judgment_science`)

**Wins when** value is judged rather than measured (hypotheses, novelty, papers).
**Structure:** a scientist agent with memory of drafts; a reviewer that starts fresh each round or a blinded critic giving pairwise preferences; a human sets taste and accepts ideas.
**Spec:** `human_in_the_loop: true`, judge `memoryless: true`.
**Failure modes:** execution weaknesses were fixed 85.3% of the time, idea-level ones 11.1%; one reviewer both guiding and scoring inflates gains.
**Evidence:** 2609.14738, 2610.23839; Dr. Claw is explicitly human-in-the-loop (2609.00365).

## Cross-cutting: shared memory that keeps disagreement

- **Claim ledger.** Tag every shared claim `proposed | confirmed | contested | superseded`: LatticeMind scored 0.97 on ConflictBank against 0.63 for a single agent and 0.45 for debate, though planning results were mixed (0.80 vs 0.97 single on TravelPlanner) and samples small at 10–75 (2608.08236). Spec: `communication.memory.type: claim_ledger` with all four `claim_states`; the linter requires `contested`.
- **Bulletin board with gated isolation.** Post findings to a board but keep selected search tasks isolated so they retain their own priors: ArcticSwarm reached 82.6% on BrowseComp-Plus, 78.8% without gated isolation and 74.5% without isolation and review (2609.01870, abstract-level read). Spec: `communication.memory.type: bulletin_board`, `communication.gated_isolation: true`.
- **No popularity ranking.** Rank shared messages by evidence, never by vote or citation count (`communication.ranking: none`); the herding evidence is in `mas-selection-verification/SKILL.md`.
- **Commitment log.** Whenever agents share resources or talk, log every inter-agent commitment (`monitoring.commitment_log: true`); the SCARCE evidence is in `mas-selection-verification/SKILL.md`.

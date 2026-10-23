# Audit checklist and failure modes

Read-only material for reviewers. Each item names the practice it checks (P1–P10, `mas-design/references/task-shape-matrix.md`) and the spec field that would encode the fix. Cite file and line for every finding.

## Checklist: what a linter cannot see

Baseline and closure
- Is there a measured single-agent baseline at matched budget, over ≥3 runs, with the metric's ceiling recorded (`baseline.runs`, `baseline.max_score`)? Is the single agent already near that ceiling? (P1)
- Are closure criteria written down (controls, validation, delivery/feasibility, repeat-run success → `task.closure_criteria`), and do the done criteria refer to them? Or does the team grade atomic sub-steps only?
- Was the team funded by splitting one agent's budget across members?

Decomposition and ownership
- Is the parallelism real? Spurious parallelism: agents spawned without a decomposition (replicas with no task, workers that all redo the same step). Serial collapse: the orchestrator does the work itself and the "workers" idle (Kimi K2.5 PARL names both). Is progress measured in critical-path steps?
- Does every task have an owner, a start condition and a checkable done criterion? Does each task have a **monitor**: the delegator that watches progress and recovers it when it stalls (RCM; `tasks[].monitor`)? (P6)
- Do delegation prompts state a done criterion and a return format (the `spawn-contract` hook's phrases are listed in `mas-orchestration/references/lead-prompt.md`)?

Communication and diversity
- Do peers read each other's full solutions before selection? (P2)
- Are there critique, review or debate rounds on a graded optimization objective? (Interaction Tax: 57% of runs made worse)
- Is there a claim ledger with a `contested` state, or a bulletin board with gated isolation, wherever agents talk (`communication.memory.type`, `communication.gated_isolation`)? Are shared messages ranked by popularity or citation count (`communication.ranking`)?
- Is there a commitment log when agents share resources or talk (`monitoring.commitment_log`, `platform.shared_resources`)? Do agents keep memory across runs while sharing a machine?

Context and cost
- Does a coordinator's context grow across epochs? (P4)
- Context policy: how many tool responses are retained, is stale output dropped or summarized, are unused tools pruned per agent (`context_policy`)? Do tool lists contain tools an agent never calls? (P5)
- Are model and effort chosen per role, or inherited everywhere? Is a strong model paired with a much weaker one on a task where they split information?
- Does each agent preload the skills its role needs (subagents do not inherit them), at most four, and do judges avoid the generators' playbook?

Merge and judging
- Does any merge, editor or orchestrator step read summaries instead of sources? If summaries are passed, does the merger have a recall tool (`merge.recall_tool`)? (P7)
- Does any judge share the generators' context, prompt or model? (P8)
- Is the final answer chosen by majority, plurality or confidence voting over a large pool? (P3)

Monitoring and prompts
- Are heartbeats in place, with progress inferred from tool-call evidence and peers or a supervisor able to override self-reports (`monitoring.progress_check: peer_override`)?
- Are private beliefs probed each round when agents discuss (`monitoring.belief_probes`)?
- Is success judged on repeated runs or on the best run (`monitoring.repeated_runs`)? (P9)
- Do prompts ask models to write out their reasoning, place harness text inside `tool_result` blocks, or add per-step countdowns on Sonnet 5.5 or Fable?

## Failure modes to name

| Symptom | Likely cause | Fix |
|---|---|---|
| Pool often contains the right answer, final answer wrong | Voting or confidence selection | Evidence-grounded or bias-controlled selector |
| Agents converge on the same idea quickly | Full-solution broadcast; same model everywhere | Private exploration; mix families in independent pools |
| Graded score drops after review rounds | Critique on an optimization objective | Remove critique rounds; keep review for feasibility only |
| Cost grows superlinearly with run length | Stateful coordinator; stale tool output summarized into context | Fresh-session advisor; drop old tool output, keep the latest ~12 |
| Wrong citations in the final report | Orchestrator merges notes | Pass raw snippets to the merge step, or summaries plus a recall tool |
| Agents duplicate work | No assignments or owners | Advisor assigns non-overlapping tasks with owners |
| Many agents, one agent's worth of progress | Spurious parallelism or serial collapse | Real decomposition into tasks; measure critical-path steps |
| Tasks stall and nobody recovers them | No monitor per task | Name the delegator as `monitor`; heartbeats with peer override |
| Sub-steps pass, deliverable fails | No closure criteria | Write `task.closure_criteria`; grade closure across repeated runs |
| Team silently adopts a false claim | Persuasion or herding | Private belief probes; claim ledger with contested state; no popularity ranking |
| Agents cut deals, exclude peers, promise things nobody sanctioned | Shared resources plus cross-run memory | Commitment log; no shared memory across runs |
| Long runs stall without errors | No heartbeat; self-reported progress | Heartbeats; zero tool calls = stalled; peer override |
| One great run, poor repeatability | Judging best runs | ≥3 repeated runs per configuration |
| Model ignores or questions harness messages | Text inside `tool_result` or countdowns after every step (Sonnet 5.5, Haiku 5.5) | Text block after the last `tool_result`; no per-step countdowns |

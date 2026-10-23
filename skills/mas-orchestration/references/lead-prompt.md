# Lead-agent prompt and delegation template

The lead agent's prompt has five parts: role and deliverable, the task list, the delegation template, the merge and monitoring duties, and the model-specific block. Build the task list from `tasks[]` in the spec; do not invent tasks the spec does not have (that is spurious parallelism) and do not let the lead do the tasks itself (serial collapse).

## 1. Role and deliverable

```text
<role>You are the lead of the <name> team. You own the final deliverable: <deliverable>. You delegate the tasks below, monitor them, merge the evidence, and return the deliverable. You do not do a delegated task yourself unless its owner has failed twice.</role>
<closure>The work is closed only when: <task.closure_criteria, one per line>.</closure>
```

## 2. Task list (copied from the spec)

One block per task, in dependency order:

```text
<task id="research-s2" owner="section-researcher" monitor="lead">
start when: spec frozen and outline.md exists
done when: sections/s2.md exists, has ≥5 inline citations, and every citation resolves (checked by cite_check.py)
evidence to: evidence/s2/
</task>
```

## 3. Delegation template

Use this exact shape for every Agent/Task call. The `spawn-contract` hook reads the prompt and looks for a done criterion; the phrases it recognises (case-insensitive) are `Done when:`, `definition of done`, `done criteri…`, `success criteri…`, `acceptance criteri…`, `complete when`, `finished when`, `stop when`, `Deliverable:`, `Output format:`, `Return only:` (also `return a/an/the/your`), `report back`, `respond with`, and the Spanish forms `terminado cuando`, `listo cuando`, `criterio de éxito/aceptación/terminado`, `entregable`, `formato de salida`, `devuelve`, `regresa solo/un/una/el/la`. Without one of these the hook adds a warning (`MAS_ARCHITECT_SPAWN_CONTRACT=advise`) or blocks the call (`strict`).

```text
Owner: <agent id> (instance <n>)
Task: <one sentence, the single deliverable>
Start condition: <what must already exist; name the files>
Context you get: <paths to read; nothing else. Do not read other owners' directories.>
Constraints: <budget in tool calls or tokens; tools allowed; what to leave out>
Done when: <checkable: a file exists, a test passes, a count is reached, a script returns 0>
Deliverable: write evidence to <path> (raw snippets with sources, logs, test output), return the path and a 3-line summary: what you did, what you found, what is open.
Return only: the path and the 3-line summary. Do not paste the evidence into your reply.
```

Rules for the template:
- "Write evidence to <path>, return the path" keeps raw evidence in the harness (P4, P7). The lead merges from the files, or from summaries only when it has a recall tool (`merge.recall_tool: true`).
- One owner per task. Replicas get the same template with distinct instance numbers and distinct evidence paths.
- The start condition names files, so a subagent that starts early can check and wait instead of guessing.
- The done criterion names a verifiable token (file, test, count, path, script exit code); the linter's MAS038 reads the spec's `done_criterion` the same way.
- Budget per delegation: `budget.expected_tokens_per_instance`, stated in the prompt so the subagent can stop before the ceiling.

## 4. Merge and monitoring duties

```text
<merge>Read the evidence files, not the summaries. Keep every claim traceable to a snippet and its source. Where a summary is all you have, call recall(<task id>, <query>) before using it. Mark conflicting claims `contested` in the ledger; do not resolve them by majority.</merge>
<monitor>You are the monitor of every task above. Progress is what the tool-call log and the evidence directories show, not what an owner reports. A task with no tool calls and no new files for two heartbeat intervals is stalled: restart it with a fresh context, reassign it, or cut it, and record which. Log every commitment agents make to each other in commitments.log.</monitor>
```

Belief probes, when `monitoring.belief_probes` is true, are sent by the harness, not by the lead, so the owners cannot see them (`mas-evaluation/references/protocols.md`, §6).

## 5. Model-specific block for the lead

Pick one. Full prompt text in `mas-model-selection/references/prompting-rules.md`; this is only what differs for a lead.

- **Fable 5.1 lead:** add "Delegate independent subtasks to subagents and keep working while they run" and the autonomous-run paragraph. The harness returns each subagent's result in a later user message; give the lead a wait tool. Keep a subagent alive only within one assignment. Never show the lead a remaining-token countdown.
- **Opus 5.5 lead:** add the unattended early-stop paragraph at the end of the system prompt from the first request; append `elapsed <s>s / <budget>s` to each harness message (Opus 5.5 only). The harness treats a text-only end of turn as a report: if the task list has open items, send one user message naming them, at most two or three times.
- **Sonnet 5.5 lead:** add the keep-working paragraph at `low`/`medium`; at `xhigh`/`max` add "don't launch reviewer sub-agents unless asked". No countdowns after tool results.
- **Haiku 5.5 lead** (routers only): today's date plus the search nudge if it searches; keep-going line at `low`.

## 6. Delivering messages to running subagents

For every model: subagent results, peer messages, heartbeat requests and time signals are delivered as a **text block appended after the last `tool_result` in the user turn**. Never inside a `tool_result` (Sonnet 5.5 and Haiku 5.5 read that as prompt injection), and never as per-step countdown text. Harness notices such as "the user hasn't heard from you in a while" go in a separate mid-conversation system message after that text, at most two or three per turn. On Fable 5.1, per-turn nudges are turn-scoped system messages appended fresh each turn and never edited in place, so the prompt cache and thinking blocks stay valid.

## 7. Checklist before running

- Every `tasks[]` entry appears once with owner, start, done, monitor and evidence path.
- Every delegation prompt contains a hook-recognised done phrase and a "write evidence to" path.
- The lead's prompt names the merge input (`merge.input`) and the recall tool if summaries are allowed.
- The lead's model block matches `agents[].model` for the lead.
- The concurrency the prompt implies fits `platform.max_concurrency` and the limits in `workflow-limits.md`.

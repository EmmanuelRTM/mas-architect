# Changelog

## 0.3.1 — 2026-10-23

- Everything the plugin ships is now in English: README, architecture notes, rule catalog (practice titles, DEF rule descriptions, hook table) and the `rules --markdown` output. The delegation-contract hook still recognises Spanish done-criterion phrases in prompts.

## 0.3.0 — 2026-10-23

Audit of the whole plugin against the research synthesis (≈75 papers, Jul–Oct 2026) and the model prompting guides. Gaps closed:

- **New agents:** `mas-verification-designer` (selector procedure, judge rubric skill, belief-probe and heartbeat protocol, closure test; Opus 5.5 @ high) and `mas-orchestration-writer` (lead-agent prompt with owner/start/done per task, workflow script, tool lists, budget table; Opus 5.5 @ medium). `mas-critic` now runs at `high` (a judge gets more effort than the generators) and checks decomposition (spurious parallelism, serial collapse, partitions that cut across questions). `mas-prompt-writer` locates the user's `model-prompt-writer` guides by path and adds the per-model blocks (early stops, keep-working, date and search nudges, batching). `mas-system-auditor` treats hook blocks as findings and preloads only `mas-audit`.
- **New commands:** `/mas-architect:baseline`, `verify`, `generate`, `review`; `/new` delegates to the `mas-architect` agent.
- **New skills:** `mas-evaluation` (baseline at matched budget, ρ pilot and N_eff, closure criteria, repeated-run and held-out evaluation, belief probes, stall detection with peer override, commitment log, critical-path progress, cost per agent) and `mas-orchestration` (subagents vs workflows, delegation template the spawn-contract hook recognises, Claude Code limits and cache sharing, schedules, budget table).
- **Skills corrected and extended:** closure criteria, ρ/budget and monitoring steps in `mas-design`; the batch-grown task graph pattern (DAGent) and the AgentRadio ladder; LongCat planner ensemble numbers; SLA, DAPS and SSR details; AKV cache rule fixed (keep all reasoning plus the latest 12 tool responses, drop rather than summarize); session-split arithmetic and the 12→5→2→1 prune schedule; latency section; TIPEX replica vs structural parallelism; Collaboration Tax rule on mixing tiers; mid-turn message placement for Sonnet 5.5 and Haiku 5.5; Opus 5.5 time budget marked model-specific; belief-probe numbers corrected; selector caveats; Agent Status Protocol peer override; SCARCE commitment logging; herding; plugin heuristics labelled as such; duplicated facts now live in one file each; `mas-audit` checklist moved to `references/checklist.md`.
- **Spec fields:** `task.closure_criteria`, `task.parallelism`, `baseline.max_score`, `tasks[].monitor`, `state.reset_policy` (`prune_schedule`, `branches`, `sessions`, `inflection_tokens`, `schedule`), `communication.memory.type` enum, `gated_isolation`, `ranking`, `context_policy`, `merge.recall_tool`, `routing.preselection` enum, `platform.shared_resources`, `platform.max_items`, `monitoring.commitment_log`, `progress_check`, `critical_path_steps`, `budget.expected_tokens_per_instance`, `selection.dedup`, `selection.strategy: confidence_vote`.
- **New rules MAS033–MAS039:** real decomposition (no spurious parallelism, no serial collapse), no critique rounds on graded objectives, shared memory that keeps disagreement, bounded context (tool pruning, no summarizing of stale output), commitment log and no popularity ranking, checkable done criteria with a monitoring delegator, complete reset policy.
- **Rules tightened:** MAS000 validates roles and counts; MAS001 warns near the ceiling and below 3 baseline runs; MAS004 falls back to generator instances; MAS008 K≈20, pre-selection required; MAS011 heartbeats by budget too; MAS012 flags full transcripts; MAS013 judge sharing a generator model; MAS016 workflow items, 16-agent default, 1.5M advisory, runtime declared; MAS018 planner ensemble and negotiated partition; MAS023 any xhigh/max without justification; MAS025 only documented thinking rejections are errors; MAS027 cites the guides' 128,000.
- **Hooks:** new `SessionStart` reminder of the platform limits and the commands; the spec linter emits its decision even when the report cannot be saved; the definitions linter ignores `docs/` paths.
- **Panel:** agents alive but not progressing (stale after `staleAfterSeconds`), nesting depth vs `maxNestingDepth`, tokens and cache-read share per agent, consecutive tool-error badge, cumulative tokens vs the 1.5M advisory, N_eff labelled as the spec estimate with ρ and 1/ρ, P9 monitoring row, env-var precedence for the report dir and the subagent limit, refresh only while the pane is open.
- **Templates:** two new lint-clean examples (`proxy-eval-loop`, `co-scientist`), one per task shape now; all examples updated to the new fields. CLI `rules --markdown` regenerates `docs/RULES.md`.

## 0.2.0 — 2026-10-23

- Skills per agent: every plugin agent preloads only the skills its role needs through `skills:` (the blind critic gets the audit checklist, not the architect's playbook).
- Spec: top-level `skills` catalog and per-agent `skills` list, in the JSON Schema and all five examples.
- New spec rules MAS029-MAS032: skills declared, present in the catalog, at most 4 preloaded, judges not sharing the generators' playbook.
- New definition rules DEF012-DEF014: valid and existing skill names (the hook discovers sibling skills), no `Skill` in `tools`, declared and bounded preloads.
- Report and control panel show each agent's preloaded skill count.
- New reference `skills/mas-design/references/skill-assignment.md`.

## 0.1.0 — 2026-10-23

- Skills: `mas-design`, `mas-patterns`, `mas-selection-verification`, `mas-model-selection`, `mas-audit`.
- Agents with explicit model and effort: `mas-architect`, `mas-critic`, `mas-model-planner`, `mas-prompt-writer`, `mas-system-auditor`.
- Commands: `new`, `lint`, `models`, `audit`, plus `/mas-panel` from the mod.
- Deterministic linter `mas_lint` (stdlib only): 29 spec rules across the ten research practices, model/effort (MOD) and operations (OPS); 11 definition rules for agents and skills.
- Hooks: secret guard, spec linter, definition linter, delegation done-criterion contract.
- Control panel mod: live subagents vs concurrency limit, session cost/context, spec health, model plan, top findings.
- JSON Schema and five lint-clean example specs.

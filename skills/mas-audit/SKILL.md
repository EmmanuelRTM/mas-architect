---
name: mas-audit
description: Audit an existing multi-agent system (code, workflow scripts, agent files, prompts or a .mas.json spec) against the ten evidence-based practices and known failure modes - correlated agents, voting over big pools, summarizing orchestrators, stateful managers, self-grading, missing owners, unbounded reads, herding and hidden belief infection. Use when reviewing, debugging or hardening an agent team, or when it costs more than one agent without beating it.
---

# Audit a multi-agent system

## Steps

1. **Inventory.** Find the agents, their prompts and models, how they are spawned and how results merge. Search for agent files (`.claude/agents/`, `agents/`), workflow scripts, orchestration code, and any `*.mas.json`.
2. **Reconstruct the spec.** If no spec exists, write one as `audit.mas.json` describing the system as it *is*, not as it should be. Mark unknown values with a `"TODO"` string rather than guessing.
3. **Lint deterministically.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" lint audit.mas.json`. The hook also writes `.mas/last-report.json` for the panel.
4. **Check what a linter cannot see.** For each item below, cite file and line for the evidence:
   - Does any merge, editor or orchestrator step read summaries instead of sources?
   - Do peers read each other's full solutions before selection?
   - Does a coordinator's context grow across epochs?
   - Does any judge share the generators' context or prompt?
   - Do delegation prompts state a done criterion?
   - Is there a measured single-agent baseline at matched budget?
   - Do tool lists per agent contain tools it never calls?
   - Are model and effort chosen per role, or inherited everywhere?
   - Does each agent preload the skills its role needs (subagents do not inherit them), at most four, and do judges avoid the generators' playbook?
   - Do prompts ask models to write out their reasoning?
5. **Independent review.** Give the spec path (not your notes) to the `mas-critic` agent; merge its findings with yours, keeping both sources.
6. **Report.** Lead with the three changes that most likely raise the team's final answer per token. For each finding: practice, evidence in the code, fix, and the paper or guide behind it. Put the full list after the top three.

## Failure modes to name

| Symptom | Likely cause | Fix |
|---|---|---|
| Pool often contains the right answer, final answer wrong | Voting or confidence selection | Evidence-grounded or bias-controlled selector |
| Agents converge on the same idea quickly | Full-solution broadcast; same model everywhere | Private exploration; mix models and families |
| Cost grows superlinearly with run length | Stateful coordinator; stale tool output in context | Fresh-session advisor; drop old tool output |
| Wrong citations in the final report | Orchestrator merges notes | Pass raw snippets to the merge step |
| Agents duplicate work | No assignments or owners | Advisor assigns non-overlapping tasks with owners |
| Team silently adopts a false claim | Persuasion or herding | Private belief probes; claim ledger with contested state |
| Long runs stall without errors | No heartbeat | Heartbeats; alive-but-not-progressing detection |
| One great run, poor repeatability | Judging best runs | ≥3 repeated runs per configuration |

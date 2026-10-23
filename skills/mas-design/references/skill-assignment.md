# Assigning skills to agents

A Claude Code agent preloads skills through its `skills:` frontmatter. Each listed skill's full `SKILL.md` is injected into the agent's context at startup. Subagents do **not** inherit the parent session's skills, so an agent that needs a playbook must name it.

In the spec, list the team's skills once in the top-level `skills` catalog and give each agent its own `skills` list. The linter checks both (MAS029-MAS032, DEF012-DEF014).

## Rules

1. **Preload what the role runs every time.** A skill belongs in `skills:` when the agent applies it on every task (a rubric, a citation format, a repo map protocol). Material it needs only sometimes stays on demand: it can still read a skill's `references/` files by path.
2. **Keep it small (at most 4).** Every preload costs context before the first tool call, and context growth is a binding constraint (P5). If a role needs more, it is probably two roles.
3. **Judges get rubrics, not the generators' playbook (P8).** A judge primed with the same heuristics shares the generators' blind spots. Give it a verification or rubric skill written for checking.
4. **Diverse generators may share a playbook.** Sharing the task format is fine; diversity comes from model family and independent context (P2). Do not share solutions through skills.
5. **Routers and selectors stay lean.** A router over top-K reads short cards; a cheap selector reads candidates and evidence. Preload one rubric at most, or `[]`.
6. **State "none" explicitly.** `skills: []` records the decision; a missing field reads as an oversight (MAS029, DEF014).
7. **Never put `Skill` in `tools`.** That form is deprecated; use the `skills` field (DEF013).
8. **Do not paste a skill into the prompt.** Refer to it by name; the preload already places it in context.

## Naming and resolution

Claude Code resolves each entry by exact name, then as `<agent's plugin>:<name>`, then as any `<plugin>:<name>`. Inside a plugin, the bare name (`mas-design`) finds the sibling skill. To pin another plugin's skill, write `plugin:skill`. An unresolved name is skipped with only a warning, so the agent silently runs without it: the definition hook flags names it cannot find next to the agent.

## Role starting points

| Role | Typical preload |
|---|---|
| Planner | The spec or plan template the team uses |
| Worker / researcher / solver | The task playbook and output format (shared across replicas) |
| Editor / merger | The output format and house style |
| Judge / verifier / critic / reviewer | A rubric or verification skill, never the generators' playbook |
| Selector | One selection rubric, or none |
| Router | None, or a short catalog-reading rule |
| Stateless advisor / orchestrator | The coordination protocol (ownership, done criteria) |

For runtimes other than Claude Code, treat `skills` as the instruction packs the harness injects into that agent.

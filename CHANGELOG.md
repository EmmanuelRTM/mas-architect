# Changelog

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

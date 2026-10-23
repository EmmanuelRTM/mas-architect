# Architecture

```
mas-architect/
├── .claude-plugin/        plugin.json (userConfig, mod types) and marketplace.json
├── skills/                7 skills Claude loads on demand (progressive disclosure)
├── agents/                7 subagents with model + effort + skills chosen per role
├── commands/              /mas-architect:new | baseline | lint | models | verify | generate | review | audit
├── hooks/
│   ├── hooks.json         classic hooks (python) + the panel module
│   ├── register.tsx       mod entry point: events and the /mas-panel command
│   └── panel/             model.ts (pure) · sources.ts (state + $) · view.tsx (drawing) · pure helper modules
├── scripts/
│   ├── mas_lint/          linter (stdlib only): rules, model catalog, advisor, hook I/O
│   └── hook_*.py          hook entry points (secrets, spec, definitions, delegation, limits)
├── templates/             JSON Schema and 7 lint-clean example specs (one per task shape)
├── types/index.d.ts       panel state contract
├── docs/                  ARCHITECTURE.md and RULES.md (generated with `mas_lint_cli.py rules --markdown`)
├── tests/                 python/ (pytest, with fixtures/) and mod/ (claude plugin test)
├── CHANGELOG.md · LICENSE · pyproject.toml
```

## Design principles

- **Deterministic first.** Everything that a regex or a rule over the spec can verify lives in `scripts/mas_lint` and runs as a hook. The model steps in only where judgment is needed (skills and agents).
- **Open/closed.** Each rule is a class with `@register`; adding one never touches the engine. Per-shape requirements (`rules/fit.py`) and the model catalog (`catalog.py`) are data.
- **Single responsibility.** `loader` loads, `accessors` queries, `rules/*` judge, `engine` orchestrates, `formatting` presents, `skill_refs` resolves the skills each agent preloads, `hookio` talks to Claude Code. In the panel, `model.ts` never sees `$`, `sources.ts` owns the state and `view.tsx` only draws.
- **Fail open.** An internal hook error is reported on stderr and never blocks the session. Blocks are explicit decisions (linter errors, secrets).
- **No secrets.** The detector reports the kind and the line, never the value. Test fixtures build fake keys at runtime.

## Workflow (agents and commands)

```
/baseline ─► mas-evaluation (single-agent baseline over ≥3 runs, rho, N_eff)
/new ──────► mas-architect (mas-design) ─► spec.mas.json ─► lint hook ─► /review (mas-critic, blind)
/verify ───► mas-verification-designer (selector, judge rubric, belief probes, closure)
/generate ─► mas-model-planner ─► mas-prompt-writer ×N ─► mas-orchestration-writer (lead prompt / workflow / budget)
/audit ────► mas-system-auditor (audit.mas.json) ─► mas-critic
```

## Panel data flow

1. `hook_lint_spec.py` (PostToolUse) writes `.mas/last-report.json` every time a `*.mas.json` changes; the report carries `metrics`, `practices`, `agents`, `monitoring` and `platform`.
2. The `register.tsx` module observes `agent.spawn`, `turn.start`, `turn.complete` and `tool.call` (liveness, usage per agent, consecutive errors), re-reads the report when a spec is written and, while the pane is open, refreshes every `refreshSeconds`: `$.agent.list()`, `$.fs.read(reportPath)` and `$.session.usage()`.
3. `sources.ts` writes to `$.state` only when a value changed, so the panel redraws exactly when something is new.
4. `view.tsx` uses only `Box` and `Text`, which exist on all four surfaces.

## Extending

- **New rule:** create a class in `scripts/mas_lint/rules/<topic>.py` with `id`, `practice`, `evidence` and `check()`, import it in `rules/__init__.py`, add tests and regenerate the tables in `docs/RULES.md` with `python3 scripts/mas_lint_cli.py rules --markdown`.
- **An agent's skills:** declare `skills:` in the frontmatter (and `skills` in the spec). Subagents do not inherit the session's skills; the guide is `skills/mas-design/references/skill-assignment.md`.
- **New model:** add a `ClaudeModel` to `catalog.py` and adjust the table in `model_advisor.py`.
- **New task shape:** add the entry to `accessors.SHAPES`, its requirements to `rules/fit.py`, the row in `skills/mas-design/references/task-shape-matrix.md`, the pattern in `skills/mas-patterns/references/patterns.md` and an example in `templates/examples/`.
- **New spec field:** add it to `templates/spec.schema.json`, document it in `skills/mas-design/references/spec-format.md` and give it at least one rule that reads it.

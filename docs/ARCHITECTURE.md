# Arquitectura

```
mas-architect/
├── .claude-plugin/        plugin.json (userConfig, tipos del mod) y marketplace.json
├── skills/                7 skills que Claude carga bajo demanda (progressive disclosure)
├── agents/                7 subagentes con model + effort + skills elegidos por rol
├── commands/              /mas-architect:new | baseline | lint | models | verify | generate | review | audit
├── hooks/
│   ├── hooks.json         hooks clásicos (python) + módulo del panel
│   ├── register.tsx       entrada del mod: eventos y comando /mas-panel
│   └── panel/             model.ts (puro) · sources.ts (estado + $) · view.tsx (dibujo) · módulos puros auxiliares
├── scripts/
│   ├── mas_lint/          linter (stdlib): reglas, catálogo de modelos, asesor, hooks I/O
│   └── hook_*.py          puntos de entrada de los hooks (secretos, spec, definiciones, delegación, límites)
├── templates/             schema JSON y 7 specs de ejemplo limpios (uno por forma de tarea)
├── types/index.d.ts       contrato de estado del panel
├── docs/                  ARCHITECTURE.md y RULES.md (generado con `mas_lint_cli.py rules --markdown`)
├── tests/                 python/ (pytest, con fixtures/) y mod/ (claude plugin test)
├── CHANGELOG.md · LICENSE · pyproject.toml
```

## Principios de diseño

- **Determinista primero.** Todo lo que se puede verificar con regex o reglas sobre el spec vive en `scripts/mas_lint` y corre como hook. El modelo sólo interviene donde hace falta juicio (skills y agentes).
- **Abierto/cerrado.** Cada regla es una clase con `@register`; agregar una no toca el motor. Los requisitos por forma de tarea (`rules/fit.py`) y el catálogo de modelos (`catalog.py`) son datos.
- **Responsabilidad única.** `loader` carga, `accessors` consulta, `rules/*` juzgan, `engine` orquesta, `formatting` presenta, `skill_refs` resuelve las skills que precarga cada agente, `hookio` habla con Claude Code. En el panel, `model.ts` no conoce `$`, `sources.ts` es dueño del estado y `view.tsx` sólo dibuja.
- **Falla abierta.** Un error interno de un hook se reporta en stderr y no bloquea la sesión. Los bloqueos son decisiones explícitas (errores del linter, secretos).
- **Sin secretos.** El detector reporta tipo y línea, nunca el valor. Los fixtures de test construyen llaves falsas en tiempo de ejecución.

## Flujo de trabajo (agentes y comandos)

```
/baseline ─► mas-evaluation (línea base ≥3 corridas, ρ, N_eff)
/new ──────► mas-architect (mas-design) ─► spec.mas.json ─► hook lint ─► /review (mas-critic, ciego)
/verify ───► mas-verification-designer (selector, rúbrica del juez, sondas, cierre)
/generate ─► mas-model-planner ─► mas-prompt-writer ×N ─► mas-orchestration-writer (líder / workflow / presupuesto)
/audit ────► mas-system-auditor (audit.mas.json) ─► mas-critic
```

## Flujo de datos del panel

1. `hook_lint_spec.py` (PostToolUse) escribe `.mas/last-report.json` cada vez que cambia un `*.mas.json`; el reporte incluye `metrics`, `practices`, `agents`, `monitoring` y `platform`.
2. El módulo `register.tsx` observa `agent.spawn`, `turn.start`, `turn.complete` y `tool.call` (para liveness, uso por agente y errores consecutivos), relee el reporte cuando se escribe un spec y, con el panel abierto, refresca cada `refreshSeconds`: `$.agent.list()`, `$.fs.read(reportPath)` y `$.session.usage()`.
3. `sources.ts` escribe en `$.state` sólo si el valor cambió; el panel se redibuja exactamente cuando hay algo nuevo.
4. `view.tsx` usa sólo `Box` y `Text`, presentes en las cuatro superficies.

## Extender

- **Nueva regla:** crea una clase en `scripts/mas_lint/rules/<tema>.py` con `id`, `practice`, `evidence` y `check()`, impórtala en `rules/__init__.py`, agrega tests y regenera las tablas de `docs/RULES.md` con `python3 scripts/mas_lint_cli.py rules --markdown`.
- **Skills de un agente:** declara `skills:` en el frontmatter (y `skills` en el spec). Los subagentes no heredan las skills de la sesión; la guía está en `skills/mas-design/references/skill-assignment.md`.
- **Nuevo modelo:** agrega un `ClaudeModel` en `catalog.py` y ajusta la tabla de `model_advisor.py`.
- **Nueva forma de tarea:** agrega la entrada en `accessors.SHAPES`, sus requisitos en `rules/fit.py`, la fila en `skills/mas-design/references/task-shape-matrix.md`, el patrón en `skills/mas-patterns/references/patterns.md` y un ejemplo en `templates/examples/`.
- **Nuevo campo del spec:** agrégalo a `templates/spec.schema.json`, documéntalo en `skills/mas-design/references/spec-format.md` y dale al menos una regla que lo lea.

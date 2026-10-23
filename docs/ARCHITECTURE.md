# Arquitectura

```
mas-architect/
├── .claude-plugin/        plugin.json (userConfig, tipos del mod) y marketplace.json
├── skills/                conocimiento que Claude carga bajo demanda (progressive disclosure)
├── agents/                subagentes con model + effort + skills elegidos por rol
├── commands/              /mas-architect:new | lint | models | audit
├── hooks/
│   ├── hooks.json         hooks clásicos (python) + módulo del panel
│   ├── register.tsx       entrada del mod: eventos y comando /mas-panel
│   └── panel/             model.ts (puro) · sources.ts (estado + $) · view.tsx (dibujo)
├── scripts/
│   ├── mas_lint/          linter (stdlib): reglas, catálogo de modelos, asesor, hooks I/O
│   └── hook_*.py          puntos de entrada de los hooks
├── templates/             schema JSON y 5 specs de ejemplo limpios
├── types/index.d.ts       contrato de estado del panel
└── tests/                 python/ (pytest) y mod/ (claude plugin test)
```

## Principios de diseño

- **Determinista primero.** Todo lo que se puede verificar con regex o reglas sobre el spec vive en `scripts/mas_lint` y corre como hook. El modelo sólo interviene donde hace falta juicio (skills y agentes).
- **Abierto/cerrado.** Cada regla es una clase con `@register`; agregar una no toca el motor. Los requisitos por forma de tarea (`rules/fit.py`) y el catálogo de modelos (`catalog.py`) son datos.
- **Responsabilidad única.** `loader` carga, `accessors` consulta, `rules/*` juzgan, `engine` orquesta, `formatting` presenta, `skill_refs` resuelve las skills que precarga cada agente, `hookio` habla con Claude Code. En el panel, `model.ts` no conoce `$`, `sources.ts` es dueño del estado y `view.tsx` sólo dibuja.
- **Falla abierta.** Un error interno de un hook se reporta en stderr y no bloquea la sesión. Los bloqueos son decisiones explícitas (errores del linter, secretos).
- **Sin secretos.** El detector reporta tipo y línea, nunca el valor. Los fixtures de test construyen llaves falsas en tiempo de ejecución.

## Flujo de datos del panel

1. `hook_lint_spec.py` (PostToolUse) escribe `.mas/last-report.json` cada vez que cambia un `*.mas.json`.
2. El módulo `register.tsx` refresca cada 3 s y justo después de cada llamada a `Agent`: `$.agent.list()`, `$.fs.read(reportPath)` y `$.session.usage()`.
3. `sources.ts` escribe en `$.state` sólo si el valor cambió; el panel se redibuja exactamente cuando hay algo nuevo.
4. `view.tsx` usa sólo `Box` y `Text`, presentes en las cuatro superficies.

## Extender

- **Nueva regla:** crea una clase en `scripts/mas_lint/rules/<tema>.py` con `id`, `practice`, `evidence` y `check()`, impórtala en `rules/__init__.py`, agrega tests y regenera `docs/RULES.md`.
- **Skills de un agente:** declara `skills:` en el frontmatter (y `skills` en el spec). Los subagentes no heredan las skills de la sesión; la guía está en `skills/mas-design/references/skill-assignment.md`.
- **Nuevo modelo:** agrega un `ClaudeModel` en `catalog.py` y ajusta la tabla de `model_advisor.py`.
- **Nueva forma de tarea:** agrega la entrada en `accessors.SHAPES`, sus requisitos en `rules/fit.py`, la fila en `skills/mas-design/references/task-shape-matrix.md` y un ejemplo en `templates/examples/`.

# mas-architect

Plugin de Claude Code para **diseñar, verificar y monitorear sistemas multiagente** con base en la evidencia de 2026 (≈75 papers, jul–oct 2026) y en las guías oficiales de prompting de Claude Fable 5.1, Opus 5.5, Sonnet 5.5 y Haiku 5.5.

La idea central de la investigación: agregar agentes sube la probabilidad de que *alguien* encuentre la respuesta, pero no la respuesta final del equipo. Lo que limita es la **selección**, el **contexto acumulado** y la **verificación**. El plugin empuja cada diseño hacia equipos pequeños, decorrelacionados y desechables, con un buen selector y un verificador independiente, y con el modelo y el nivel de razonamiento correctos por rol.

## Qué incluye

| Componente | Contenido |
|---|---|
| **Skills** | `mas-design` (flujo completo), `mas-patterns` (8 patrones con evidencia), `mas-selection-verification`, `mas-model-selection` (modelo + esfuerzo por rol), `mas-audit` |
| **Agentes** | `mas-architect` (opus/high), `mas-critic` revisor ciego sin memoria (fable/medium), `mas-model-planner` (sonnet/medium), `mas-prompt-writer` (opus/medium), `mas-system-auditor` (opus/medium) |
| **Comandos** | `/mas-architect:new`, `/mas-architect:lint`, `/mas-architect:models`, `/mas-architect:audit`, `/mas-panel` |
| **Hooks deterministas** | Bloqueo de secretos por regex, linter de specs `*.mas.json` (29 reglas), linter de agentes/skills (11 reglas DEF), contrato de delegación (criterio de terminado) |
| **Mod / panel** | Panel lateral en vivo: subagentes activos vs límite de concurrencia, costo y contexto de la sesión, salud del spec por práctica, plan de modelo/esfuerzo y hallazgos principales |
| **Plantillas** | `templates/spec.schema.json` y 5 ejemplos limpios (`deep-research`, `optimization-swarm`, `codebase-team`, `qa-selector`, `agent-router`) |

## Instalación

Requisitos: Claude Code reciente y `python3` (3.10+) en el `PATH`. Sin dependencias externas; PyYAML es opcional para specs `.mas.yaml`.

```text
/plugin install mas-architect --marketplace <owner>/<repo>
```

Durante el desarrollo, desde la carpeta del repo:

```bash
claude --plugin-dir ./mas-architect
```

## Uso rápido

1. `/mas-architect:new "equipo para responder preguntas de arquitectura sobre nuestro monorepo"`
2. Claude sigue `mas-design`: línea base de un solo agente → forma de la tarea → patrón → modelos y esfuerzo → spec `.mas.json`.
3. Cada vez que se escribe el spec, el hook lo lintea: los **errores bloquean** y Claude los corrige; las advertencias regresan como contexto.
4. `mas-critic` revisa el spec sin ver el razonamiento del autor.
5. `/mas-panel` abre el panel de control.

CLI directo (sin Claude):

```bash
python3 scripts/mas_lint_cli.py lint templates/examples/deep-research.mas.json
python3 scripts/mas_lint_cli.py recommend templates/examples/deep-research.mas.json
python3 scripts/mas_lint_cli.py neff 30 0.9      # tamaño efectivo del equipo
python3 scripts/mas_lint_cli.py rules
```

## Modelo y nivel de razonamiento por rol

| Rol | Modelo @ esfuerzo inicial |
|---|---|
| Orquestador / advisor sin estado | Opus 5.5 @ medium (Fable 5.1 @ high para ciencia ambigua o autonomía de días) |
| Planner | Opus 5.5 @ high |
| Worker en repos grandes | Opus 5.5 @ medium |
| Worker en optimización | Sonnet 5.5 @ high |
| Researcher (mucha búsqueda) | Sonnet 5.5 @ high |
| Editor / merge | Opus 5.5 @ medium |
| Juez / verificador / crítico | Opus 5.5 @ high, sin memoria, distinto modelo que los generadores |
| Selector | Haiku 5.5 @ medium |
| Router sobre top-K | Haiku 5.5 @ low |

Es un punto de partida: barre los niveles de esfuerzo con tus propios evals. Detalle en `skills/mas-model-selection/`.

## Configuración

| Opción (`userConfig`) | Default | Uso |
|---|---|---|
| `maxConcurrentSubagents` | 20 | Límite que muestra el panel (igual a `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`) |
| `reportPath` | `.mas/last-report.json` | Reporte que lee el panel |

| Variable de entorno | Efecto |
|---|---|
| `MAS_ARCHITECT_SPAWN_CONTRACT` | `advise` (default), `strict` (niega delegaciones sin criterio de terminado) u `off` |
| `MAS_ARCHITECT_REPORT_DIR` | Carpeta alternativa para los reportes del linter |

Agrega `.mas/` a tu `.gitignore`: contiene reportes generados.

## Desarrollo

```bash
pytest                    # 150+ tests del linter, hooks y contenido del plugin
claude plugin test .      # tests del panel en terminal, desktop, vscode y mobile
claude plugin validate .
```

Documentación: [arquitectura](docs/ARCHITECTURE.md) · [catálogo de reglas](docs/RULES.md) · [formato del spec](skills/mas-design/references/spec-format.md) · [cambios](CHANGELOG.md).

## Licencia

MIT. Ver [LICENSE](LICENSE).

# mas-architect

Plugin de Claude Code para **diseñar, verificar y monitorear sistemas multiagente** con base en la evidencia de 2026 (≈75 papers, jul–oct 2026) y en las guías oficiales de prompting de Claude Fable 5.1, Opus 5.5, Sonnet 5.5 y Haiku 5.5.

La idea central de la investigación: agregar agentes sube la probabilidad de que *alguien* encuentre la respuesta, pero no la respuesta final del equipo. Lo que limita es la **selección**, el **contexto acumulado** y la **verificación**. El plugin empuja cada diseño hacia equipos pequeños, decorrelacionados y desechables, con un buen selector y un verificador independiente, y con el modelo y el nivel de razonamiento correctos por rol.

## Qué incluye

| Componente | Contenido |
|---|---|
| **Skills** | `mas-design` (flujo completo), `mas-patterns` (8 patrones con evidencia), `mas-selection-verification`, `mas-model-selection` (modelo + esfuerzo por rol), `mas-audit` |
| **Agentes** | `mas-architect` (opus/high), `mas-critic` revisor ciego sin memoria (fable/medium), `mas-model-planner` (sonnet/medium), `mas-prompt-writer` (opus/medium), `mas-system-auditor` (opus/medium). Cada uno precarga sólo sus skills (ver abajo) |
| **Comandos** | `/mas-architect:new`, `/mas-architect:lint`, `/mas-architect:models`, `/mas-architect:audit`, `/mas-panel` |
| **Hooks deterministas** | Bloqueo de secretos por regex, linter de specs `*.mas.json` (33 reglas), linter de agentes/skills (14 reglas DEF, incluidas las skills por agente), contrato de delegación (criterio de terminado) |
| **Mod / panel** | Panel lateral en vivo: subagentes activos vs límite de concurrencia, costo y contexto de la sesión, salud del spec por práctica, plan de modelo/esfuerzo/skills y hallazgos principales |
| **Plantillas** | `templates/spec.schema.json` y 5 ejemplos limpios (`deep-research`, `optimization-swarm`, `codebase-team`, `qa-selector`, `agent-router`) |

## Instalación

Requisitos: Claude Code reciente y `python3` (3.10+) en el `PATH`. Sin dependencias externas; PyYAML es opcional para specs `.mas.yaml`.

```text
/plugin install mas-architect --marketplace EmmanuelRTM/mas-architect
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

## Skills por agente

Los subagentes no heredan las skills de la sesión, así que cada agente declara en `skills:` las que precarga. Cada una inyecta su `SKILL.md` completo al arrancar, por eso se limitan a lo que el rol usa siempre.

| Agente | Skills precargadas | Por qué |
|---|---|---|
| `mas-architect` | `mas-design`, `mas-patterns`, `mas-selection-verification`, `mas-model-selection` | Diseña de punta a punta |
| `mas-critic` | `mas-audit`, `mas-selection-verification` | Revisa con la lista de fallas, sin el playbook del autor (independencia del juez) |
| `mas-model-planner` | `mas-model-selection` | Sólo decide modelo y esfuerzo |
| `mas-prompt-writer` | `mas-model-selection` | Reglas de prompting por modelo |
| `mas-system-auditor` | `mas-audit`, `mas-design` | Audita y escribe el spec del sistema existente |

Para los sistemas que diseñes, el spec lleva un catálogo `skills` y una lista `skills` por agente. Las reglas MAS029–MAS032 y DEF012–DEF014 revisan que esté declarada, que exista, que no pase de 4 y que los jueces no compartan el playbook de los generadores. Guía completa: [skill-assignment.md](skills/mas-design/references/skill-assignment.md).

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
pytest                    # 175+ tests del linter, hooks y contenido del plugin
claude plugin test .      # tests del panel en terminal, desktop, vscode y mobile
claude plugin validate .
```

Documentación: [arquitectura](docs/ARCHITECTURE.md) · [catálogo de reglas](docs/RULES.md) · [formato del spec](skills/mas-design/references/spec-format.md) · [cambios](CHANGELOG.md).

## Licencia

MIT. Ver [LICENSE](LICENSE).

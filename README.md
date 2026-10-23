# mas-architect

Plugin de Claude Code para **diseñar, verificar, orquestar y monitorear sistemas multiagente** con base en la evidencia de 2026 (≈75 papers, jul–oct 2026) y en las guías oficiales de prompting de Claude Fable 5.1, Opus 5.5, Sonnet 5.5 y Haiku 5.5.

La idea central de la investigación: agregar agentes sube la probabilidad de que *alguien* encuentre la respuesta, pero no la respuesta final del equipo. Lo que limita es la **selección**, el **contexto acumulado**, la **verificación** y el **cierre** (controles, validación, entrega). El plugin empuja cada diseño hacia equipos pequeños, decorrelacionados y desechables, con un buen selector, un verificador independiente, dueños y monitores explícitos por tarea, y el modelo y el nivel de razonamiento correctos por rol.

## Qué incluye

| Componente | Contenido |
|---|---|
| **Skills** | `mas-design` (flujo de 14 pasos), `mas-patterns` (9 patrones con evidencia), `mas-selection-verification`, `mas-model-selection` (modelo + esfuerzo por rol), `mas-evaluation` (línea base, ρ, cierre, corridas repetidas, sondas de creencia), `mas-orchestration` (prompt del líder, límites, caché, presupuesto), `mas-audit` |
| **Agentes** | `mas-architect` (opus/high), `mas-critic` revisor ciego sin memoria (fable/high), `mas-model-planner` (sonnet/medium), `mas-prompt-writer` (opus/medium), `mas-verification-designer` (opus/high), `mas-orchestration-writer` (opus/medium), `mas-system-auditor` (opus/medium). Cada uno precarga sólo sus skills (ver abajo) |
| **Comandos** | `/mas-architect:new`, `baseline`, `lint`, `models`, `verify`, `generate`, `review`, `audit` y `/mas-panel` |
| **Hooks deterministas** | Bloqueo de secretos por regex, linter de specs `*.mas.json` (40 reglas), linter de agentes/skills (14 reglas DEF), contrato de delegación (criterio de terminado), recordatorio de límites de la plataforma al iniciar la sesión |
| **Mod / panel** | Panel lateral en vivo: subagentes activos vs límite de concurrencia, profundidad de anidado, agentes vivos sin progreso, tokens y lectura de caché por agente, bucles de error, costo de la sesión, salud del spec por práctica, N_eff, monitoreo (P9) y hallazgos principales |
| **Plantillas** | `templates/spec.schema.json` y 7 ejemplos limpios (`deep-research`, `optimization-swarm`, `codebase-team`, `qa-selector`, `agent-router`, `proxy-eval-loop`, `co-scientist`) |

## Instalación

Requisitos: Claude Code reciente y `python3` (3.10+) en el `PATH`. Sin dependencias externas; PyYAML es opcional para specs `.mas.yaml`.

```text
/plugin install mas-architect --marketplace EmmanuelRTM/mas-architect
```

Durante el desarrollo, desde la carpeta del repo:

```bash
claude --plugin-dir .
```

## Uso rápido

1. `/mas-architect:baseline "equipo para responder preguntas de arquitectura sobre nuestro monorepo"` mide (o planea) el mejor agente individual con el mismo presupuesto, al menos 3 corridas, y estima la correlación de errores ρ.
2. `/mas-architect:new "..."` delega el diseño al agente `mas-architect`, que sigue `mas-design`: criterios de cierre → línea base → ρ y presupuesto → forma de la tarea → patrón → modelos y esfuerzo → dueños y monitores → selección y verificación → monitoreo → spec `.mas.json`.
3. Cada vez que se escribe el spec, el hook lo lintea: los **errores bloquean** y Claude los corrige; las advertencias regresan como contexto.
4. `/mas-architect:review` entrega sólo la ruta del spec a `mas-critic`, que lo revisa sin ver el razonamiento del autor.
5. `/mas-architect:verify` hace que `mas-verification-designer` escriba el procedimiento del selector, la skill de rúbrica del juez y el protocolo de sondas, latidos y cierre.
6. `/mas-architect:generate` produce los artefactos: archivos de agente por modelo (`mas-prompt-writer`), prompt del líder o script de workflow y tabla de presupuesto (`mas-orchestration-writer`).
7. `/mas-panel` abre el panel de control mientras el equipo corre.

CLI directo (sin Claude):

```bash
python3 scripts/mas_lint_cli.py lint templates/examples/deep-research.mas.json
python3 scripts/mas_lint_cli.py recommend templates/examples/deep-research.mas.json
python3 scripts/mas_lint_cli.py neff 30 0.9      # tamaño efectivo del equipo
python3 scripts/mas_lint_cli.py rules            # lista de reglas (--markdown para docs/RULES.md)
```

## Las diez prácticas y lo que el linter revisa

| Práctica | Reglas |
|---|---|
| P1 Medir primero la línea base de un solo agente (≥3 corridas, techo del métrico) | MAS001 |
| P2 Generar de forma independiente con modelos diversos; sin difundir soluciones; sin crítica sobre objetivos calificados | MAS002, MAS003, MAS017, MAS034 |
| P3 Invertir en selección, no en más votantes | MAS004, MAS005 |
| P4 Estado en el harness; agentes desechables; política de reinicio completa | MAS006, MAS007, MAS039 |
| P5 Acotar cada lectura: top-K, podar herramientas, descartar salida vieja sin resumirla | MAS008, MAS029, MAS031, MAS036 |
| P6 Comunicación no bloqueante, dueños y monitores por tarea, descomposición real, memoria que conserva el desacuerdo | MAS009, MAS010, MAS011, MAS033, MAS035, MAS038 |
| P7 Evidencia cruda, no resúmenes, al que fusiona | MAS012 |
| P8 Separar al juez del generador | MAS013, MAS032 |
| P9 Monitorear creencias, compromisos y corridas repetidas | MAS014, MAS015, MAS037 |
| P10 Entrenar con crédito de equipo | MAS021 |
| MOD Modelo y esfuerzo por rol | MAS022–MAS028 |
| OPS Límites de la plataforma, esquema, higiene | MAS000, MAS016, MAS018, MAS019, MAS020, MAS030 |

Catálogo completo con la evidencia de cada regla: [docs/RULES.md](docs/RULES.md).

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

Es un punto de partida: barre los niveles de esfuerzo con tus propios evals. Mezcla familias sólo en pools de réplicas independientes; nunca emparejes un modelo fuerte con uno mucho más débil en una tarea donde se reparten la información. Detalle en `skills/mas-model-selection/`.

## Skills por agente

Los subagentes no heredan las skills de la sesión, así que cada agente declara en `skills:` las que precarga. Cada una inyecta su `SKILL.md` completo al arrancar, por eso se limitan a lo que el rol usa siempre.

| Agente | Skills precargadas | Por qué |
|---|---|---|
| `mas-architect` | `mas-design`, `mas-patterns`, `mas-selection-verification`, `mas-model-selection` | Diseña de punta a punta |
| `mas-critic` | `mas-audit`, `mas-selection-verification` | Revisa con la lista de fallas, sin el playbook del autor (independencia del juez) |
| `mas-model-planner` | `mas-model-selection` | Sólo decide modelo y esfuerzo |
| `mas-prompt-writer` | `mas-model-selection` | Reglas de prompting por modelo |
| `mas-verification-designer` | `mas-selection-verification`, `mas-evaluation` | Selector, rúbrica del juez, sondas, cierre |
| `mas-orchestration-writer` | `mas-orchestration`, `mas-patterns` | Prompt del líder, workflow, límites y presupuesto |
| `mas-system-auditor` | `mas-audit` | Reconstruye el spec de un sistema existente |

Para los sistemas que diseñes, el spec lleva un catálogo `skills` y una lista `skills` por agente. Las reglas MAS029–MAS032 y DEF012–DEF014 revisan que esté declarada, que exista, que no pase de 4 y que los jueces no compartan el playbook de los generadores. Guía completa: [skill-assignment.md](skills/mas-design/references/skill-assignment.md).

## Configuración

| Opción (`userConfig`) | Default | Uso |
|---|---|---|
| `maxConcurrentSubagents` | 20 | Límite que muestra el panel (igual a `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`; la variable de entorno se lee primero) |
| `reportPath` | `.mas/last-report.json` | Reporte que lee el panel (si `MAS_ARCHITECT_REPORT_DIR` está definida, se usa `<dir>/last-report.json`) |
| `staleAfterSeconds` | 120 | Segundos sin turno ni tool call tras los que un agente `running` se marca `stalled?` (vivo pero sin progreso, Agent Status Protocol) |
| `maxNestingDepth` | 3 | Profundidad máxima de anidamiento de subagentes (Claude Code permite 3); la fila `nesting` se pinta en rojo al alcanzarla |
| `maxConcurrentWorkflowAgents` | 16 | Límite de la segunda barra: agentes lanzados por un script Workflow (`maxConcurrency` por defecto 16) |
| `refreshSeconds` | 3 | Intervalo de refresco del panel abierto; los eventos (spawn, turnos, tool calls, edición de `*.mas.json`) lo refrescan antes |

| Variable de entorno | Efecto |
|---|---|
| `MAS_ARCHITECT_SPAWN_CONTRACT` | `advise` (default), `strict` (niega delegaciones sin criterio de terminado) u `off` |
| `MAS_ARCHITECT_REPORT_DIR` | Carpeta alternativa para los reportes del linter (el panel la respeta) |
| `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` | Límite real de subagentes concurrentes de Claude Code; el panel lo usa como referencia |

Agrega `.mas/` a tu `.gitignore`: contiene reportes generados.

## Desarrollo

```bash
pytest                    # ~240 tests del linter, hooks y contenido del plugin
claude plugin test .      # tests del panel en terminal, desktop, vscode y mobile
claude plugin validate .
```

Documentación: [arquitectura](docs/ARCHITECTURE.md) · [catálogo de reglas](docs/RULES.md) · [formato del spec](skills/mas-design/references/spec-format.md) · [cambios](CHANGELOG.md).

## Licencia

MIT. Ver [LICENSE](LICENSE).

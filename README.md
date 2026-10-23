# mas-architect

A Claude Code plugin to **design, verify, orchestrate and monitor multi-agent systems**, grounded in the 2026 evidence (about 75 papers, Jul–Oct 2026) and in the official prompting guides for Claude Fable 5.1, Opus 5.5, Sonnet 5.5 and Haiku 5.5.

The research's central finding: adding agents raises the chance that *someone* finds the answer, not the team's final answer. The binding constraints are **selection**, **accumulated context**, **verification** and **closure** (controls, validation, delivery). The plugin pushes every design toward small, decorrelated, disposable teams with a good selector, an independent verifier, explicit owners and monitors per task, and the right model and reasoning level per role.

## What is included

| Component | Contents |
|---|---|
| **Skills** | `mas-design` (14-step workflow), `mas-patterns` (9 evidence-backed patterns), `mas-selection-verification`, `mas-model-selection` (model + effort per role), `mas-evaluation` (baseline, rho, closure, repeated runs, belief probes), `mas-orchestration` (lead prompt, limits, cache, budget), `mas-audit` |
| **Agents** | `mas-architect` (opus/high), `mas-critic` blind memoryless reviewer (fable/high), `mas-model-planner` (sonnet/medium), `mas-prompt-writer` (opus/medium), `mas-verification-designer` (opus/high), `mas-orchestration-writer` (opus/medium), `mas-system-auditor` (opus/medium). Each preloads only its own skills (see below) |
| **Commands** | `/mas-architect:new`, `baseline`, `lint`, `models`, `verify`, `generate`, `review`, `audit` and `/mas-panel` |
| **Deterministic hooks** | Regex secret guard, `*.mas.json` spec linter (40 rules), agent/skill definition linter (14 DEF rules), delegation contract (done criterion), platform-limits reminder at session start |
| **Mod / panel** | Live side panel: active subagents vs the concurrency limit, nesting depth, agents alive but not progressing, tokens and cache-read share per agent, failure loops, session cost, spec health per practice, N_eff, monitoring (P9) and top findings |
| **Templates** | `templates/spec.schema.json` and 7 lint-clean examples (`deep-research`, `optimization-swarm`, `codebase-team`, `qa-selector`, `agent-router`, `proxy-eval-loop`, `co-scientist`) |

## Installation

Requirements: a recent Claude Code and `python3` (3.10+) on the `PATH`. No external dependencies; PyYAML is optional for `.mas.yaml` specs.

```text
/plugin install mas-architect --marketplace EmmanuelRTM/mas-architect
```

During development, from the repository folder:

```bash
claude --plugin-dir .
```

## Quick start

1. `/mas-architect:baseline "a team that answers architecture questions about our monorepo"` measures (or plans) the strongest single agent at the same budget, at least 3 runs, and estimates the error correlation rho.
2. `/mas-architect:new "..."` delegates the design to the `mas-architect` agent, which follows `mas-design`: closure criteria → baseline → rho and budget → task shape → pattern → models and effort → owners and monitors → selection and verification → monitoring → `.mas.json` spec.
3. Every time the spec is written, the hook lints it: **errors block** and Claude fixes them; warnings come back as context.
4. `/mas-architect:review` hands only the spec path to `mas-critic`, which reviews it without seeing the author's rationale.
5. `/mas-architect:verify` has `mas-verification-designer` write the selector procedure, the judge's rubric skill and the probe, heartbeat and closure protocol.
6. `/mas-architect:generate` produces the artifacts: per-model agent files (`mas-prompt-writer`), the lead prompt or workflow script and the budget table (`mas-orchestration-writer`).
7. `/mas-panel` opens the control panel while the team runs.

Direct CLI (without Claude):

```bash
python3 scripts/mas_lint_cli.py lint templates/examples/deep-research.mas.json
python3 scripts/mas_lint_cli.py recommend templates/examples/deep-research.mas.json
python3 scripts/mas_lint_cli.py neff 30 0.9      # effective team size
python3 scripts/mas_lint_cli.py rules            # rule list (--markdown for docs/RULES.md)
```

## The ten practices and what the linter checks

| Practice | Rules |
|---|---|
| P1 Measure the single-agent baseline first (≥3 runs, metric ceiling) | MAS001 |
| P2 Generate independently with diverse models; no solution broadcast; no critique on graded objectives | MAS002, MAS003, MAS017, MAS034 |
| P3 Spend on selection, not on more voters | MAS004, MAS005 |
| P4 State in the harness; disposable agents; complete reset policy | MAS006, MAS007, MAS039 |
| P5 Cap every read: top-K, prune tools, drop stale output without summarizing it | MAS008, MAS029, MAS031, MAS036 |
| P6 Non-blocking communication, owners and monitors per task, real decomposition, memory that keeps disagreement | MAS009, MAS010, MAS011, MAS033, MAS035, MAS038 |
| P7 Raw evidence, not summaries, to the merger | MAS012 |
| P8 Separate the judge from the generator | MAS013, MAS032 |
| P9 Monitor beliefs, commitments and repeated runs | MAS014, MAS015, MAS037 |
| P10 Train with team-level credit | MAS021 |
| MOD Model and effort per role | MAS022–MAS028 |
| OPS Platform limits, schema, hygiene | MAS000, MAS016, MAS018, MAS019, MAS020, MAS030 |

Full catalog with the evidence behind each rule: [docs/RULES.md](docs/RULES.md).

## Model and reasoning level per role

| Role | Model @ starting effort |
|---|---|
| Stateless orchestrator / advisor | Opus 5.5 @ medium (Fable 5.1 @ high for ambiguous science or multi-day autonomy) |
| Planner | Opus 5.5 @ high |
| Worker on large repositories | Opus 5.5 @ medium |
| Worker in optimization loops | Sonnet 5.5 @ high |
| Researcher (search-heavy) | Sonnet 5.5 @ high |
| Editor / merge | Opus 5.5 @ medium |
| Judge / verifier / critic | Opus 5.5 @ high, memoryless, a different model from the generators |
| Selector | Haiku 5.5 @ medium |
| Router over top-K | Haiku 5.5 @ low |

This is a starting point: sweep effort levels on your own evals. Mix families only in independent replica pools; never pair a strong model with a much weaker one on a task where they split the information. Details in `skills/mas-model-selection/`.

## Skills per agent

Subagents do not inherit the session's skills, so each agent declares the ones it preloads in `skills:`. Each one injects its full `SKILL.md` at startup, which is why they are limited to what the role always uses.

| Agent | Preloaded skills | Why |
|---|---|---|
| `mas-architect` | `mas-design`, `mas-patterns`, `mas-selection-verification`, `mas-model-selection` | Designs end to end |
| `mas-critic` | `mas-audit`, `mas-selection-verification` | Reviews with the failure checklist, without the author's playbook (judge independence) |
| `mas-model-planner` | `mas-model-selection` | Only decides model and effort |
| `mas-prompt-writer` | `mas-model-selection` | Per-model prompting rules |
| `mas-verification-designer` | `mas-selection-verification`, `mas-evaluation` | Selector, judge rubric, probes, closure |
| `mas-orchestration-writer` | `mas-orchestration`, `mas-patterns` | Lead prompt, workflow, limits and budget |
| `mas-system-auditor` | `mas-audit` | Reconstructs the spec of an existing system |

For the systems you design, the spec carries a `skills` catalog and a `skills` list per agent. Rules MAS029–MAS032 and DEF012–DEF014 check that it is declared, that it exists, that it stays at 4 or fewer, and that judges do not share the generators' playbook. Full guide: [skill-assignment.md](skills/mas-design/references/skill-assignment.md).

## Configuration

| Option (`userConfig`) | Default | Use |
|---|---|---|
| `maxConcurrentSubagents` | 20 | Concurrent-subagent limit shown by the panel; when unset, `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` is read |
| `reportPath` | `.mas/last-report.json` | Report the panel reads; when unset and `MAS_ARCHITECT_REPORT_DIR` exists, `<dir>/last-report.json` is used |
| `staleAfterSeconds` | 120 | Seconds without a turn or tool call after which a `running` agent is marked `stalled?` (alive but not progressing, Agent Status Protocol) |
| `maxNestingDepth` | 3 | Maximum subagent nesting depth (Claude Code allows 3); the `nesting` row turns red when reached |
| `maxConcurrentWorkflowAgents` | 16 | Limit of the second bar: agents started by a Workflow script (`maxConcurrency` defaults to 16) |
| `refreshSeconds` | 3 | Refresh interval of the open panel; events (spawn, turns, tool calls, `*.mas.json` edits) refresh it sooner |

| Environment variable | Effect |
|---|---|
| `MAS_ARCHITECT_SPAWN_CONTRACT` | `advise` (default), `strict` (denies delegations without a done criterion) or `off` |
| `MAS_ARCHITECT_REPORT_DIR` | Alternative folder for the linter reports (the panel honours it) |
| `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` | Claude Code's real concurrent-subagent limit; the panel uses it as the reference |

Add `.mas/` to your `.gitignore`: it holds generated reports.

## Development

```bash
pytest                    # ~240 tests for the linter, hooks and plugin content
claude plugin test .      # panel tests on terminal, desktop, vscode and mobile
claude plugin validate .
```

Documentation: [architecture](docs/ARCHITECTURE.md) · [rule catalog](docs/RULES.md) · [spec format](skills/mas-design/references/spec-format.md) · [changes](CHANGELOG.md).

## License

MIT. See [LICENSE](LICENSE).

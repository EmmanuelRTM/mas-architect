# Rule catalog

Generated from `scripts/mas_lint/rules/` (`python3 scripts/mas_lint_cli.py rules --markdown` prints the two rule tables). A test checks that this file lists every rule.

Severities: **error** blocks (the hook returns `decision: block`), **warning** comes back as context, **info** only informs.

## Practices

| Id | Practice |
|---|---|
| P1 | Measure the strong single-agent baseline first |
| P2 | Generate independently across diverse model families |
| P3 | Spend on selection, not on more voters |
| P4 | Keep state in the harness; agents are disposable |
| P5 | Cap every read (top-K, prune tools, drop stale output) |
| P6 | Non-blocking communication and explicit ownership |
| P7 | Hand raw evidence, not summaries, to the merger |
| P8 | Separate the judge from the generator |
| P9 | Monitor beliefs and repeated runs, not only transcripts |
| P10 | Train with team-level credit and decorrelated agents |
| MOD | Assign model and effort per role deliberately |
| OPS | Respect platform limits, schema and hygiene |

## Spec rules (`*.mas.json`)

| Rule | Practice | What it checks | Evidence |
|---|---|---|---|
| MAS000 | OPS | Spec structure |  |
| MAS001 | P1 | Single-agent baseline measured | Coordination's benefit shrinks as the single agent strengthens: a capability-saturation threshold predicted the coordination effect in 94% of validation configurations (Nature MI 2026) and the Collaboration Tax's penalty shrinks for stronger models (arXiv 2608.22152). |
| MAS002 | P2 | Decorrelated generators | Cross-family pairing lowers error overlap from kappa 0.53 to 0.38 (Co-RL); same-model teams score zero on some tasks (2608.23541). |
| MAS003 | P2 | No full-solution broadcast | Solution distance fell 0.315 -> 0.229 after interaction; synthesizers copied the best proposer >=80% of the time (2608.23541). |
| MAS004 | P3 | Evidence-grounded or bias-controlled selection | Oracle 92.6 vs majority 72.6 on BrowseComp; RGV lifts to 78.9 at ~0.3 ms/rollout (2608.24024); TRACE 1/258 of AggAgent cost (2609.39912). |
| MAS005 | P3 | Revision saturates after one or two peers | Revising against 1 peer gained 26.5 points, against 29 peers 26.6 (2609.31563). |
| MAS006 | P4 | Stateless coordinator, state in the harness | Stateless advisor used 0.24-0.51% of tokens vs 8.4-10.7% for a stateful manager; 84-93% fewer tokens overall (2610.07625). |
| MAS007 | P4 | Isolated generator contexts | Removing worker isolation cut kernel progress 42.8% (2610.07625); gated isolation worth 3.8 pts (ArcticSwarm). |
| MAS008 | P5 | Hard top-K on what a router reads | Full catalog fails at 5,000 cards; any pre-selection cuts tokens 98.8% at 1,000 agents, SSR and BM25 statistically indistinguishable, K = 20 chosen on the test queries (2610.21113). |
| MAS009 | P6 | Every delegation has an owner, a start and a done criterion | Responsibility-centered coordination: 63.0 vs 44.3 (AgentVerse); 72.8 -> 46.7 without the protocol (2610.21243). |
| MAS010 | P6 | Non-blocking communication | Passive awareness 62.1% vs blocking receive 51.6%, 15 wins to 2 (AgentRadio, 2607.28430). |
| MAS011 | P6 | Heartbeats for long-running agents | Missing active monitoring was a top failure (25 cases, 2610.10263); Agent Status Protocol flags alive-but-stuck agents. |
| MAS012 | P7 | Raw evidence, not summaries, to the merger | Orchestrator introduced 84.7% of report errors; snippets instead of notes lifted citation precision 87.6 -> 94.1 (2608.24306); DAGent passes compact summaries plus a recall tool over full transcripts (2609.39154). |
| MAS013 | P8 | A judge that did not do the work | Fresh reviewers avoid anchoring (2609.14738); cross-fitted verifiers cut false agreement 6-9% -> 3-4% (2609.39102). |
| MAS014 | P9 | Judge repeated runs, not the best run | Full closure in all three runs on 18.0% of tasks vs 32.7% of single attempts (PhysClosureBench). |
| MAS015 | P9 | Probe private beliefs in debates | One adversarial peer lifted private false-belief adoption 0.6% -> 44.8%; only 19.7% showed it publicly (2610.22138). |
| MAS016 | OPS | Fits the runtime's limits | Claude Code docs: 20 concurrent subagents, 3 nesting levels; workflows 16 default, 1-256, 1,000 agents/run, 4,096 items per parallel()/pipeline(), advisory above 25 agents or 1.5 million projected tokens. |
| MAS017 | P2 | Replica count vs error correlation | N_eff = N/(1+(N-1)rho) tends to 1/rho; rho 0.9 leaves ~1.1 effective agents out of 30 (2609.31563). |
| MAS018 | OPS | Architecture fits the task shape | Task shape -> architecture table of the research synthesis (Oct 2026). |
| MAS019 | OPS | No hardcoded secrets | Secrets belong in the environment or a secret store, referenced by name. |
| MAS020 | OPS | References point at real agents |  |
| MAS021 | P10 | Team-level credit and decorrelated training | Set-level credit (SRPO) beats per-response GRPO by 3.5-7.6 pts on search; cross-family peer rewards (Co-RL). |
| MAS022 | MOD | Model and effort declared per Claude agent | Effort is the primary intelligence/latency/cost control; level names do not transfer across models (model guides). |
| MAS023 | MOD | xhigh/max only where measured | Guides: reserve xhigh and max for work where you have measured a quality gain; thinking and replies get much longer. |
| MAS024 | MOD | Low effort on search-heavy or long agentic roles | Haiku 5.5, Fable 5.1 and Sonnet 5.5 guides on behavior at low effort. |
| MAS025 | MOD | Thinking mode accepted by the model at that effort | Documented rejections: Opus 5.5 cannot disable thinking; Sonnet 5.5 between_tools and Haiku 5.5 disabled only at high or below (API 400 otherwise). Other combinations are not documented in the guides. |
| MAS026 | MOD | Do not ask for reasoning in the reply | Fable 5.1/Opus 5.5/Sonnet 5.5 may refuse with reasoning_extraction; Haiku 5.5 leaks reasoning-like text. |
| MAS027 | MOD | max_tokens leaves room for thinking | Thinking counts toward max_tokens; the Opus 5.5 and Sonnet 5.5 guides recommend 128,000 (the maximum) for long agentic turns. The 32,000 threshold is this plugin's heuristic. |
| MAS028 | MOD | Role-model fit (advisory) | Recommendation table in model_advisor.py (research roles x model guides). |
| MAS029 | P5 | Every agent states which skills it preloads | Subagents do not inherit the parent's skills; an undeclared playbook is either missing or loaded ad hoc. |
| MAS030 | OPS | Agent skills exist in the spec's skill catalog | Claude Code skips an unresolved skill with only a warning, so the agent silently runs without it. |
| MAS031 | P5 | At most 4 preloaded skills per agent | Each preloaded skill injects its whole SKILL.md at startup; context growth is a binding constraint. |
| MAS032 | P8 | Judges do not preload the generators' playbook | A judge primed with the same heuristics as the generators shares their blind spots (correlated errors, self-preference). |
| MAS033 | P6 | Real decomposition: no spurious parallelism, no serial collapse | PARL rewards counter serial collapse (orchestrator does everything) and spurious parallelism (spawning without decomposition); progress measured in critical steps (Kimi K2.5); 16 missing-owner failures (2610.10263). |
| MAS034 | P2 | No critique rounds on graded objectives | First critique round made 17 of 30 optimization runs (57%) worse; debate gain -0.078 for diverse teams (2608.23541). |
| MAS035 | P6 | Shared memory keeps disagreement | LatticeMind claim states 0.97 vs 0.45 for debate on ConflictBank (2608.08236); ArcticSwarm 82.6 -> 78.8 without gated isolation (2609.01870). |
| MAS036 | P5 | Bounded context: prune tools, drop stale tool output | KV-cache reads 82.4% of API cost; keeping all reasoning plus the latest 12 tool responses cut cost 27.7% and raised score 1.7 pts, while summarizing invalidates the cache (2610.28577); 16 of 23 tool descriptions billed every turn were never called (TokenEconomizer). |
| MAS037 | P9 | Log commitments; do not rank by popularity | Agents sharing a machine formed coalitions in up to 79% of rounds and made unsanctioned commitments (SCARCE 2610.21029); popularity drifted 9x further from quality than in humans (2610.30769). |
| MAS038 | P6 | Checkable done criteria and a monitoring delegator | Closure reached in 32.7% of attempts and in all three runs on 18.0% of tasks (PhysClosureBench); 86% of the best model's deficit was failed delivery (OR-License); the delegator stays responsible for monitoring and recovery (RCM 2610.21243). |
| MAS039 | P4 | Reset policy is complete | Fork alone 0.57, flush alone 0.55, both 0.71 vs 0.45 (2610.07447); 100M tokens split three ways at the measured inflection beat one session by +264 Elo (2609.15309); start-many-then-prune 12 -> 5 -> 2 -> 1 (2607.18235). |

## Definition rules (`agents/*.md`, `skills/*/SKILL.md`)

| Rule | Severity | What it checks |
|---|---|---|
| DEF001 | error | YAML frontmatter block present |
| DEF002 | error | `name` in kebab-case, at most 64 characters |
| DEF003 | error / warning | `description` present (at most 1024 characters) |
| DEF004 | warning | The agent declares `tools` (least privilege) |
| DEF005 | warning | `model` is a valid Claude alias or id |
| DEF006 | error | The body (system prompt / instructions) is not empty |
| DEF007 | error | No secrets in the file |
| DEF008 | warning | `SKILL.md` at most 500 lines |
| DEF009 | warning | The skill name matches its folder |
| DEF010 | info / error | `effort` declared and valid |
| DEF011 | error / warning | Does not ask for visible reasoning in the reply (`reasoning_extraction`) |
| DEF012 | warning | Every entry in `skills:` is kebab-case (or `plugin:skill`) and exists next to the agent |
| DEF013 | warning | `Skill` does not belong in `tools`; use the `skills:` field |
| DEF014 | info / warning | The agent declares `skills` (subagents do not inherit the parent's) and preloads at most 4 |

## Hooks

| Hook | Event | Behaviour |
|---|---|---|
| `hook_session_limits.py` | SessionStart | Injects the Claude Code limits as context (20 concurrent subagents, 3 nesting levels, workflows 16 by default / 1–256 / 1,000 per run / 4,096 items / advisory above 25 agents or 1.5M tokens, shared prompt cache) plus the list of `/mas-architect:*` commands and `/mas-panel` |
| `hook_guard_secrets.py` | PreToolUse `Write\|Edit\|MultiEdit\|NotebookEdit` | Denies writes that contain keys or tokens (regex); never shows the value |
| `hook_spawn_contract.py` | PreToolUse `Agent\|Task` | Warns when a delegation has no done criterion (English or Spanish phrasing); `MAS_ARCHITECT_SPAWN_CONTRACT=strict` denies it, `=off` disables the check |
| `hook_lint_spec.py` | PostToolUse `Write\|Edit\|MultiEdit` | Lints `*.mas.json`; errors block; writes `.mas/last-report.json` (if the report cannot be saved it says so on stderr and still emits the decision) |
| `hook_validate_definitions.py` | PostToolUse `Write\|Edit\|MultiEdit` | Lints agent and skill files with the DEF rules |

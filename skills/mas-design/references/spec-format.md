# `.mas.json` spec format

JSON (YAML `.mas.yaml` works when PyYAML is installed). The JSON Schema is `templates/spec.schema.json`; the examples in `templates/examples/` are lint-clean references. Fields marked `// v0.3` are new in v0.3.0; the linter checks them (rules MAS033–MAS039 plus updated existing rules). Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" rules` for the full rule list.

```jsonc
{
  "name": "deep-research-report",                 // required
  "task": {
    "shape": "cited_report",                      // one row of task-shape-matrix.md
    "description": "...",
    "closure_criteria": [                         // v0.3: what "closed" means; done criteria refer to these
      "controls: ablation with the harness swapped out",
      "validation: every number re-derived from the source table",
      "delivery: report builds and every citation resolves",
      "repeat: closure reached in 3 of 3 runs"
    ],
    "parallelism": "replica | structural | both"  // v0.3: several full paths vs concurrent parts of one path (TIPEX)
  },
  "platform": {
    "runtime": "claude-code-subagents | claude-code-workflow | custom",
    "max_concurrency": 8, "nesting_depth": 1, "concurrency_override": false,
    "shared_resources": false,                    // v0.3: true when agents share a machine, repo or account (SCARCE)
    "max_items": 4096                             // v0.3: items per parallel()/pipeline(); cap in mas-orchestration/references/workflow-limits.md
  },
  "baseline": {
    "single_agent_score": 48.7, "metric": "DRB-II",
    "runs": 3,                                    // ≥3 repeated single-agent runs at matched budget (P1)
    "max_score": 100                              // v0.3: metric ceiling; score/max_score ≥ 0.85 = near the ceiling (plugin heuristic)
  },
  "planning": { "fixed_spec": true, "planner_ensemble": 3, "joint_exploration": false, "negotiated_partition": false },
  "skills": [{ "name": "citation-format", "description": "...", "source": "plugin|project|user|harness" }],  // catalog; agents preload only these
  "agents": [{
    "id": "section-researcher",                   // unique
    "role": "planner|worker|researcher|solver|orchestrator|advisor|manager|judge|verifier|critic|selector|reviewer|editor|router|evaluator",
    "count": 6,                                   // identical instances, ≥1
    "model": "claude-sonnet-5-5",                 // or alias opus/sonnet/haiku/fable, or a non-Claude id
    "model_family": "claude",
    "effort": "low|medium|high|xhigh|max",        // MOD rules
    "effort_justification": "eval: +4 pts at xhigh",   // needed for xhigh/max on fan-out roles
    "thinking": "adaptive|disabled|between_tools",
    "max_tokens": 128000,
    "context": "isolated|shared", "stateful": false, "memoryless": true,
    "heartbeat_seconds": 60,
    "tools": ["Read", "Grep", "WebSearch"],       // pruned per agent; >12 draws an info (plugin heuristic)
    "skills": ["source-search", "citation-format"],   // preloaded at startup; [] for none (see skill-assignment.md)
    "instructions": "short role prompt (never ask for visible reasoning)"
  }],
  "tasks": [{
    "id": "research", "owner": "section-researcher",
    "start_condition": "spec frozen",
    "done_criterion": "section file written with ≥5 inline citations that resolve",   // checkable: names a file, test, count, path...
    "monitor": "global-editor"                    // v0.3: agent id or "harness"; the delegator that watches and recovers (RCM)
  }],                                             // P6
  "communication": {
    "mode": "none|passive|non_blocking|blocking|broadcast|debate",
    "share_full_solutions": false, "debate": false,
    "memory": {
      "type": "claim_ledger | bulletin_board | shared_workspace | none",   // v0.3 enum
      "claim_states": ["proposed", "confirmed", "contested", "superseded"] // claim_ledger must keep "contested"
    },
    "gated_isolation": true,                      // v0.3: selected searches stay isolated from the board (ArcticSwarm)
    "ranking": "none | popularity | citation"     // v0.3: how shared messages are ranked; none avoids herding
  },
  "context_policy": {                             // v0.3 (P5): bounded context per agent
    "retained_tool_responses": 12,                // keep all reasoning plus the latest N tool responses (AKV)
    "prune_unused_tools": true,
    "stale_output": "drop | keep | summarize"     // summarize rewrites the prefix and invalidates the cache: drop instead
  },
  "selection": {
    "strategy": "evidence_grounded|bias_controlled|trained_selector|best_of_n_metric|confidence_vote|majority_vote|plurality|llm_aggregator",
    "candidates": 8, "revision_peers": 1,         // P3; candidates falls back to generator instances when absent
    "dedup": true                                 // drop near-duplicate candidates before selection (DAPS)
  },
  "merge": {
    "input": "raw_evidence|snippets|summaries|full_transcripts",   // P7
    "agent": "global-editor",
    "recall_tool": true                           // v0.3: merger can pull snippets from a dependency's full transcript (DAGent)
  },
  "verification": { "judge_agents": ["citation-verifier"], "evaluator_protected": true,
                    "real_validation_before_promotion": true, "held_out_audit_every": 10 },         // P8
  "state": {
    "location": "harness|orchestrator_context",   // P4
    "reset_policy": {
      "type": "fork_and_flush | session_split | stateless_epochs | prune_schedule | none",   // v0.3 enum
      "branches": 4, "checkpoints": [0, 0.33, 0.66],   // fork_and_flush: branches ≥2 and non-empty checkpoints
      "sessions": 3, "inflection_tokens": 38000000,    // session_split: sessions ≥2 and the measured inflection point
      "schedule": [12, 5, 2, 1]                        // prune_schedule: strictly decreasing, ends in 1
    }
  },
  "routing": { "catalog_size": 5000, "top_k": 20, "preselection": "bm25 | index | embedding | none" },  // P5; top_k ≥ 1
  "monitoring": {
    "repeated_runs": 3, "belief_probes": true, "heartbeat": true, "track_cost": true,   // P9
    "commitment_log": true,                       // v0.3: log every inter-agent commitment (SCARCE)
    "progress_check": "self_report | peer_override",   // v0.3: peers and supervisor can override an agent's self-report (ASP)
    "critical_path_steps": true                   // v0.3: measure progress in critical-path steps, not total steps
  },
  "training": { "credit_assignment": "team|active_set|set_level|per_response", "peer_families": 2 },     // P10, optional
  "human_in_the_loop": false,
  "budget": {
    "max_tokens": 1000000,
    "expected_error_correlation": 0.5,            // ρ from the pilot (share of shared failures)
    "expected_tokens_per_instance": 120000        // v0.3: baseline tokens × 1.41–3.31× subagent overhead
  }
}
```

Field-by-field rationale lives next to the pattern that uses it (`mas-patterns/references/patterns.md`), the budget formulas in `limits-and-budget.md`, and the monitoring protocols in the `mas-evaluation` skill.

# `.mas.json` spec format

JSON (YAML `.mas.yaml` works when PyYAML is installed). The JSON Schema is `templates/spec.schema.json`; the examples in `templates/examples/` are lint-clean references.

```jsonc
{
  "name": "deep-research-report",                 // required
  "task": { "shape": "cited_report", "description": "..." },   // shape: see task-shape-matrix.md
  "platform": { "runtime": "claude-code-subagents | claude-code-workflow | custom",
                "max_concurrency": 8, "nesting_depth": 1, "concurrency_override": false },
  "baseline": { "single_agent_score": 48.7, "metric": "DRB-II", "runs": 3 },        // P1
  "planning": { "fixed_spec": true, "planner_ensemble": 3, "joint_exploration": false, "negotiated_partition": false },
  "agents": [{
    "id": "section-researcher",                   // unique
    "role": "planner|worker|researcher|solver|orchestrator|advisor|manager|judge|verifier|critic|selector|reviewer|editor|router",
    "count": 6,                                   // identical instances
    "model": "claude-sonnet-5-5",                 // or alias opus/sonnet/haiku/fable, or a non-Claude id
    "model_family": "claude",
    "effort": "low|medium|high|xhigh|max",        // MOD rules
    "effort_justification": "eval: +4 pts at xhigh",   // needed for xhigh/max on fan-out roles
    "thinking": "adaptive|disabled|between_tools",
    "max_tokens": 128000,
    "context": "isolated|shared", "stateful": false, "memoryless": true,
    "heartbeat_seconds": 60,
    "instructions": "short role prompt (never ask for visible reasoning)"
  }],
  "tasks": [{ "id": "research", "owner": "section-researcher",
              "start_condition": "spec frozen", "done_criterion": "section with inline citations" }],   // P6
  "communication": { "mode": "none|passive|non_blocking|blocking|broadcast|debate",
                     "share_full_solutions": false, "debate": false,
                     "memory": { "type": "claim_ledger", "claim_states": ["proposed","confirmed","contested","superseded"] } },
  "selection": { "strategy": "evidence_grounded|bias_controlled|trained_selector|best_of_n_metric|majority_vote|plurality|llm_aggregator",
                 "candidates": 8, "revision_peers": 1 },                    // P3
  "merge": { "input": "raw_evidence|snippets|summaries|full_transcripts", "agent": "global-editor" },   // P7
  "verification": { "judge_agents": ["citation-verifier"], "evaluator_protected": true,
                    "real_validation_before_promotion": true, "held_out_audit_every": 10 },         // P8
  "state": { "location": "harness|orchestrator_context",
             "reset_policy": { "type": "fork_and_flush|session_split|stateless_epochs|none", "checkpoints": [0, 0.33, 0.66] } },  // P4
  "routing": { "catalog_size": 5000, "top_k": 20, "preselection": "bm25" },  // P5
  "monitoring": { "repeated_runs": 3, "belief_probes": false, "heartbeat": true, "track_cost": true },  // P9
  "training": { "credit_assignment": "team|active_set|set_level|per_response", "peer_families": 2 },     // P10, optional
  "human_in_the_loop": false,
  "budget": { "max_tokens": 1000000, "expected_error_correlation": 0.5 }
}
```

Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" rules` for the full rule list.

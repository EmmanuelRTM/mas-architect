"""State in the harness (P4), bounded reads (P5) and coordination (P6)."""


def test_mas006_stateful_coordinator(make_spec, rule_ids):
    spec = make_spec()
    spec["agents"].append({"id": "boss", "role": "orchestrator", "stateful": True, "model_family": "claude"})
    assert "MAS006" in rule_ids(spec)


def test_mas006_state_held_in_orchestrator_context(make_spec, rule_ids):
    spec = make_spec(state={"location": "orchestrator_context"})
    assert "MAS006" in rule_ids(spec)


def test_mas007_generators_must_not_share_context(make_spec, rule_ids):
    spec = make_spec()
    spec["agents"][0]["context"] = "shared"
    assert "MAS007" in rule_ids(spec)


def test_mas008_large_catalog_without_top_k_is_error(make_spec):
    from mas_lint import lint

    spec = make_spec(routing={"catalog_size": 1000})
    severities = {f.severity.value for f in lint(spec).findings if f.rule_id == "MAS008"}
    assert severities == {"error"}


def test_mas008_top_k_too_large_is_warning(make_spec, rule_ids):
    spec = make_spec(routing={"catalog_size": 1000, "top_k": 400})
    assert "MAS008" in rule_ids(spec, severities=("warning",))


def test_mas010_blocking_communication(make_spec, rule_ids):
    spec = make_spec(communication={"mode": "blocking"})
    assert "MAS010" in rule_ids(spec)


def test_mas011_long_running_shape_needs_heartbeat(make_spec, rule_ids):
    spec = make_spec(task={"shape": "codebase_long"}, monitoring={"heartbeat": False})
    assert "MAS011" in rule_ids(spec)


def test_mas011_short_tasks_do_not_need_heartbeat(make_spec, rule_ids):
    spec = make_spec(monitoring={"heartbeat": False})
    assert "MAS011" not in rule_ids(spec)


def test_mas008_top_k_above_30_is_warning(make_spec):
    from mas_lint import lint

    spec = make_spec(routing={"catalog_size": 1000, "top_k": 40, "preselection": "bm25"})
    hits = [f for f in lint(spec).findings if f.rule_id == "MAS008"]
    assert [f.severity.value for f in hits] == ["warning"]
    assert "K≈20" in hits[0].message


def test_mas008_top_k_below_5_is_info(make_spec, rule_ids):
    spec = make_spec(routing={"catalog_size": 1000, "top_k": 3, "preselection": "bm25"})
    assert "MAS008" not in rule_ids(spec)
    assert "MAS008" in rule_ids(spec, severities=("info",))


def test_mas008_no_preselection_is_warning(make_spec, rule_ids):
    spec = make_spec(routing={"catalog_size": 1000, "top_k": 20, "preselection": "none"})
    assert "MAS008" in rule_ids(spec, severities=("warning",))


def test_mas011_ten_million_token_budget_needs_heartbeat(make_spec, rule_ids):
    spec = make_spec(budget={"max_tokens": 10_000_000}, monitoring={"heartbeat": False})
    assert "MAS011" in rule_ids(spec)


def test_mas011_heartbeat_without_interval_is_info(make_spec, rule_ids):
    spec = make_spec(monitoring={"heartbeat": True})
    assert "MAS011" in rule_ids(spec, severities=("info",))
    assert "MAS011" not in rule_ids(spec)


def test_mas033_no_tasks_is_warning(make_spec, rule_ids):
    spec = make_spec()
    del spec["tasks"]
    assert "MAS033" in rule_ids(spec)


def test_mas033_replicated_agent_without_a_task(make_spec, rule_ids):
    spec = make_spec()
    spec["tasks"] = [t for t in spec["tasks"] if t["owner"] != "solver-qwen"]
    assert "MAS033" in rule_ids(spec)


def test_mas033_serial_collapse(make_spec, rule_ids):
    spec = make_spec()
    spec["agents"].append({"id": "boss", "role": "orchestrator", "model": "claude-opus-5-5", "model_family": "claude", "effort": "medium", "skills": []})
    for task in spec["tasks"]:
        task["owner"] = "boss"
    assert "MAS033" in rule_ids(spec)


def test_mas035_channel_without_claim_ledger(make_spec, rule_ids):
    spec = make_spec(communication={"mode": "passive"}, monitoring={"commitment_log": True})
    assert "MAS035" in rule_ids(spec)


def test_mas035_bulletin_board_with_gated_isolation_is_info(make_spec, rule_ids):
    spec = make_spec(
        communication={"mode": "passive", "gated_isolation": True, "memory": {"type": "bulletin_board"}},
        monitoring={"commitment_log": True},
    )
    assert "MAS035" not in rule_ids(spec)
    assert "MAS035" in rule_ids(spec, severities=("info",))


def test_mas035_claim_ledger_needs_contested_state(make_spec, rule_ids):
    memory = {"type": "claim_ledger", "claim_states": ["proposed", "confirmed"]}
    spec = make_spec(communication={"mode": "non_blocking", "memory": memory}, monitoring={"commitment_log": True})
    assert "MAS035" in rule_ids(spec)
    spec["communication"]["memory"]["claim_states"].append("contested")
    assert "MAS035" not in rule_ids(spec, severities=("error", "warning", "info"))


def test_mas035_ignores_mode_none(make_spec, rule_ids):
    assert "MAS035" not in rule_ids(make_spec(communication={"mode": "none"}), severities=("error", "warning", "info"))


def test_mas038_vague_done_criterion_is_info(make_spec):
    from mas_lint import lint

    spec = make_spec()
    spec["tasks"][0]["done_criterion"] = "it works well enough"
    hits = [f for f in lint(spec).findings if f.rule_id == "MAS038" and "solve" in f.path]
    assert [f.severity.value for f in hits] == ["info"]


def test_mas038_long_running_task_without_monitor_is_info(make_spec, rule_ids):
    spec = make_spec(task={"shape": "codebase_long"})
    assert "MAS038" not in rule_ids(spec, severities=("info",))
    for task in spec["tasks"]:
        del task["monitor"]
    assert "MAS038" in rule_ids(spec, severities=("info",))


def test_mas038_unknown_monitor_is_error(make_spec):
    from mas_lint import lint

    spec = make_spec()
    spec["tasks"][0]["monitor"] = "nobody"
    spec["tasks"][1]["monitor"] = "harness"
    hits = [f for f in lint(spec).findings if f.rule_id == "MAS038" and f.severity.value == "error"]
    assert len(hits) == 1 and "nobody" in hits[0].message


def test_mas039_fork_and_flush_needs_branches_and_checkpoints(make_spec, rule_ids):
    spec = make_spec(state={"reset_policy": {"type": "fork_and_flush", "branches": 1}})
    assert "MAS039" in rule_ids(spec)
    spec["state"]["reset_policy"] = {"type": "fork_and_flush", "branches": 4, "checkpoints": [0, 0.33, 0.66]}
    assert "MAS039" not in rule_ids(spec)


def test_mas039_session_split_needs_sessions_and_inflection(make_spec, rule_ids):
    spec = make_spec(state={"reset_policy": {"type": "session_split", "sessions": 3}})
    assert "MAS039" in rule_ids(spec)
    spec["state"]["reset_policy"]["inflection_tokens"] = 38_000_000
    assert "MAS039" not in rule_ids(spec)


def test_mas039_prune_schedule_must_decrease_to_one(make_spec, rule_ids):
    spec = make_spec(state={"reset_policy": {"type": "prune_schedule", "schedule": [12, 5, 5, 2]}})
    assert "MAS039" in rule_ids(spec)
    spec["state"]["reset_policy"]["schedule"] = [12, 5, 2, 1]
    assert "MAS039" not in rule_ids(spec)

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

"""Platform limits (OPS) and task-shape fit (FIT)."""

from mas_lint import lint


def _findings(spec, rule_id):
    return [f for f in lint(spec).findings if f.rule_id == rule_id]


def test_mas016_subagent_concurrency_over_20(make_spec):
    spec = make_spec(platform={"runtime": "claude-code-subagents", "max_concurrency": 21})
    assert {f.severity.value for f in _findings(spec, "MAS016")} == {"error"}


def test_mas016_override_downgrades_to_warning(make_spec):
    spec = make_spec(platform={"runtime": "claude-code-subagents", "max_concurrency": 30, "concurrency_override": True})
    assert {f.severity.value for f in _findings(spec, "MAS016")} == {"warning"}


def test_mas016_nesting_deeper_than_three(make_spec):
    spec = make_spec(platform={"runtime": "claude-code-subagents", "nesting_depth": 4})
    assert _findings(spec, "MAS016")


def test_mas016_workflow_advisory_above_25(make_spec):
    spec = make_spec(platform={"runtime": "claude-code-workflow", "max_concurrency": 64})
    assert {f.severity.value for f in _findings(spec, "MAS016")} == {"info"}


def test_mas016_workflow_hard_cap_256(make_spec):
    spec = make_spec(platform={"runtime": "claude-code-workflow", "max_concurrency": 300})
    assert "error" in {f.severity.value for f in _findings(spec, "MAS016")}


def test_mas016_workflow_total_agents_cap(make_spec):
    spec = make_spec(platform={"runtime": "claude-code-workflow"})
    spec["agents"][0]["count"] = 1200
    assert "error" in {f.severity.value for f in _findings(spec, "MAS016")}


def test_mas018_cited_report_needs_fixed_spec_and_editor(make_spec):
    spec = make_spec(task={"shape": "cited_report"})
    messages = " ".join(f.message for f in _findings(spec, "MAS018"))
    assert "planning.fixed_spec" in messages
    assert "editor" in messages


def test_mas018_optimization_needs_reset_policy(make_spec):
    spec = make_spec(task={"shape": "optimization"})
    messages = " ".join(f.message for f in _findings(spec, "MAS018"))
    assert "state.reset_policy.type" in messages


def test_mas018_judgment_science_needs_human(make_spec):
    spec = make_spec(task={"shape": "judgment_science"})
    assert any("human_in_the_loop" in f.message for f in _findings(spec, "MAS018"))

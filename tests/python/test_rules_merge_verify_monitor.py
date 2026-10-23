"""Merge (P7), judge separation (P8), monitoring (P9) and training (P10)."""

from mas_lint import lint


def _severity(spec, rule_id):
    return {f.severity.value for f in lint(spec).findings if f.rule_id == rule_id}


def test_mas012_summaries_to_merger_is_warning(make_spec):
    spec = make_spec(merge={"input": "summaries"})
    assert _severity(spec, "MAS012") == {"warning"}


def test_mas012_summaries_in_cited_report_is_error(make_spec):
    spec = make_spec(task={"shape": "cited_report"}, merge={"input": "summaries"})
    assert "error" in _severity(spec, "MAS012")


def test_mas013_requires_a_judge(make_spec, rule_ids):
    spec = make_spec()
    del spec["verification"]
    assert "MAS013" in rule_ids(spec)


def test_mas013_judge_cannot_be_a_generator(make_spec, rule_ids):
    spec = make_spec(verification={"judge_agents": ["solver-claude"]})
    assert "MAS013" in rule_ids(spec)


def test_mas013_judge_should_be_memoryless(make_spec):
    spec = make_spec()
    spec["agents"][-1]["memoryless"] = False
    assert _severity(spec, "MAS013") == {"warning"}


def test_mas014_needs_three_repeated_runs(make_spec, rule_ids):
    spec = make_spec(monitoring={"repeated_runs": 1})
    assert "MAS014" in rule_ids(spec)


def test_mas015_debate_without_belief_probes(make_spec, rule_ids):
    spec = make_spec(communication={"debate": True})
    assert "MAS015" in rule_ids(spec)


def test_mas015_debate_with_probes_passes(make_spec, rule_ids):
    spec = make_spec(communication={"debate": True}, monitoring={"belief_probes": True})
    assert "MAS015" not in rule_ids(spec)


def test_mas021_training_needs_team_level_credit(make_spec, rule_ids):
    spec = make_spec(training={"credit_assignment": "per_response"})
    assert "MAS021" in rule_ids(spec)


def test_mas021_team_credit_passes(make_spec, rule_ids):
    spec = make_spec(training={"credit_assignment": "active_set", "peer_families": 2})
    assert "MAS021" not in rule_ids(spec, severities=("error", "warning", "info"))

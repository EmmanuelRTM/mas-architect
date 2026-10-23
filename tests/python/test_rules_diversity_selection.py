"""Diversity (P2) and selection (P3) rules."""


def _same_family(spec, same_model):
    for agent in spec["agents"]:
        if agent["role"] == "worker":
            agent["model_family"] = "claude"
            agent["model"] = "claude-sonnet-5-5" if same_model else agent["model"]
    return spec


def test_mas002_one_identical_model_for_every_generator_warns(make_spec, rule_ids):
    spec = _same_family(make_spec(), same_model=True)
    assert "MAS002" in rule_ids(spec)


def test_mas002_one_family_with_mixed_models_is_info(make_spec, rule_ids):
    spec = _same_family(make_spec(), same_model=False)
    assert "MAS002" not in rule_ids(spec)
    assert "MAS002" in rule_ids(spec, severities=("info",))


def test_mas002_skips_tiny_teams(make_spec, rule_ids):
    spec = make_spec()
    spec["agents"] = [a for a in spec["agents"] if a["id"] in ("solver-claude", "selector")]
    spec["agents"][0]["count"] = 2
    spec["tasks"] = [t for t in spec["tasks"] if t["owner"] in ("solver-claude", "selector")]
    assert "MAS002" not in rule_ids(spec)


def test_mas003_full_solution_broadcast(make_spec, rule_ids):
    spec = make_spec(communication={"share_full_solutions": True})
    assert "MAS003" in rule_ids(spec)


def test_mas004_majority_vote_over_many_candidates(make_spec, rule_ids):
    spec = make_spec(selection={"strategy": "majority_vote"})
    assert "MAS004" in rule_ids(spec)


def test_mas004_llm_aggregator_is_only_info(make_spec, rule_ids):
    spec = make_spec(selection={"strategy": "llm_aggregator"})
    assert "MAS004" not in rule_ids(spec)
    assert "MAS004" in rule_ids(spec, severities=("info",))


def test_mas005_revision_saturates_after_two_peers(make_spec, rule_ids):
    spec = make_spec(selection={"revision_peers": 5})
    assert "MAS005" in rule_ids(spec, severities=("info",))


def test_mas017_over_provisioned_replicas_for_correlation(make_spec, rule_ids):
    spec = make_spec(selection={"candidates": 30}, budget={"expected_error_correlation": 0.9})
    assert "MAS017" in rule_ids(spec)


def test_mas017_reports_effective_size_as_info(make_spec, rule_ids):
    assert "MAS017" in rule_ids(make_spec(), severities=("info",))


def test_mas004_voting_falls_back_to_generator_instances(make_spec, rule_ids):
    spec = make_spec(selection={"strategy": "majority_vote"})
    del spec["selection"]["candidates"]
    assert "MAS004" in rule_ids(spec)


def test_mas034_debate_on_optimization_warns(make_spec, rule_ids):
    spec = make_spec(task={"shape": "optimization"}, communication={"mode": "debate"})
    assert "MAS034" in rule_ids(spec)


def test_mas034_revision_peers_on_optimization_warns(make_spec, rule_ids):
    spec = make_spec(task={"shape": "optimization"}, selection={"revision_peers": 1})
    assert "MAS034" in rule_ids(spec)


def test_mas034_critic_owning_a_task_on_optimization_warns(make_spec, rule_ids):
    spec = make_spec(task={"shape": "optimization"}, selection={"revision_peers": 0})
    spec["agents"].append({"id": "nitpicker", "role": "critic", "model": "gpt-5.5", "memoryless": True, "skills": []})
    spec["tasks"].append({"id": "critique", "owner": "nitpicker", "start_condition": "candidate ready", "done_criterion": "list of issues written to file"})
    assert "MAS034" in rule_ids(spec)


def test_mas034_ignores_other_shapes(make_spec, rule_ids):
    spec = make_spec(communication={"mode": "debate"}, monitoring={"belief_probes": True})
    assert "MAS034" not in rule_ids(spec)

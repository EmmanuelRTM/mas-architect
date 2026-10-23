"""Schema, baseline, ownership and reference rules."""


def test_clean_base_has_no_findings(base_spec, rule_ids):
    assert rule_ids(base_spec) == set()


def test_mas000_missing_name_and_unknown_shape(make_spec, rule_ids):
    spec = make_spec(name="", task={"shape": "vibes"})
    assert "MAS000" in rule_ids(spec)


def test_mas000_duplicate_agent_ids(make_spec, rule_ids):
    spec = make_spec()
    spec["agents"].append(dict(spec["agents"][0]))
    assert "MAS000" in rule_ids(spec)


def test_mas000_agents_required(make_spec, rule_ids):
    spec = make_spec(agents=[])
    assert "MAS000" in rule_ids(spec)


def test_mas001_requires_single_agent_baseline(make_spec, rule_ids):
    spec = make_spec()
    del spec["baseline"]
    assert "MAS001" in rule_ids(spec)


def test_mas001_baseline_must_be_numeric(make_spec, rule_ids):
    spec = make_spec(baseline={"single_agent_score": "high"})
    assert "MAS001" in rule_ids(spec)


def test_mas009_each_task_needs_owner_start_and_done(make_spec, rule_ids):
    spec = make_spec()
    spec["tasks"].append({"id": "orphan"})
    assert "MAS009" in rule_ids(spec)


def test_mas020_owner_must_reference_an_agent(make_spec, rule_ids):
    spec = make_spec()
    spec["tasks"][0]["owner"] = "ghost"
    assert "MAS020" in rule_ids(spec)


def test_mas020_judge_and_merge_agent_must_exist(make_spec, rule_ids):
    spec = make_spec(merge={"agent": "nobody"}, verification={"judge_agents": ["nobody"]})
    assert "MAS020" in rule_ids(spec)


def test_mas019_flags_hardcoded_secret_without_echoing_it(make_spec):
    from mas_lint import lint

    fake = "sk-ant-api03-" + "A1b2C3d4" * 6
    spec = make_spec(platform={"api_key": fake})
    report = lint(spec)
    hits = [f for f in report.findings if f.rule_id == "MAS019"]
    assert hits and hits[0].severity.value == "error"
    assert fake not in hits[0].message

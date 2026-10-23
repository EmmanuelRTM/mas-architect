"""Bounded context (P5): tool pruning and stale tool output."""

from mas_lint import lint


def _severity(spec, rule_id):
    return {f.severity.value for f in lint(spec).findings if f.rule_id == rule_id}


def test_mas036_more_than_twelve_tools_is_info(make_spec):
    spec = make_spec()
    spec["agents"][0]["tools"] = [f"tool_{i}" for i in range(13)]
    assert _severity(spec, "MAS036") == {"info"}


def test_mas036_long_running_without_context_policy_is_info(make_spec):
    spec = make_spec(task={"shape": "optimization"})
    assert _severity(spec, "MAS036") == {"info"}


def test_mas036_summarizing_stale_output_is_warning(make_spec):
    spec = make_spec(context_policy={"stale_output": "summarize"})
    assert _severity(spec, "MAS036") == {"warning"}


def test_mas036_dropping_stale_output_passes(make_spec):
    spec = make_spec(task={"shape": "optimization"}, context_policy={"retained_tool_responses": 12, "prune_unused_tools": True, "stale_output": "drop"})
    assert _severity(spec, "MAS036") == set()

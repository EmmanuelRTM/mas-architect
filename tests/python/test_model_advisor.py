"""Model catalog, per-role model/effort recommendations and the MOD rules."""

import pytest

from mas_lint import lint
from mas_lint.catalog import CATALOG, resolve_model
from mas_lint.model_advisor import recommend


def _findings(spec, rule_id):
    return [f for f in lint(spec).findings if f.rule_id == rule_id]


def _severities(spec, rule_id):
    return {f.severity.value for f in _findings(spec, rule_id)}


# --- catalog -------------------------------------------------------------


def test_catalog_has_current_claude_models_with_defaults():
    defaults = {m.id: m.default_effort for m in CATALOG.values()}
    assert defaults == {
        "claude-fable-5-1": "high",
        "claude-opus-5-5": "medium",
        "claude-sonnet-5-5": "high",
        "claude-haiku-5-5": "medium",
    }


@pytest.mark.parametrize(
    "name, expected",
    [
        ("opus", "claude-opus-5-5"),
        ("claude-sonnet-5-5", "claude-sonnet-5-5"),
        ("haiku", "claude-haiku-5-5"),
        ("fable", "claude-fable-5-1"),
        ("gpt-5.5", None),
        ("inherit", None),
    ],
)
def test_resolve_model_aliases(name, expected):
    model = resolve_model(name)
    assert (model.id if model else None) == expected


# --- recommendations ------------------------------------------------------


@pytest.mark.parametrize(
    "role, shape, model, effort",
    [
        ("router", "routing", "claude-haiku-5-5", "low"),
        ("researcher", "cited_report", "claude-sonnet-5-5", "high"),
        ("judge", "short_verifiable", "claude-opus-5-5", "high"),
        ("advisor", "optimization", "claude-opus-5-5", "medium"),
        ("worker", "codebase_long", "claude-opus-5-5", "medium"),
        ("worker", "optimization", "claude-sonnet-5-5", "high"),
        ("worker", "short_verifiable", "claude-sonnet-5-5", "medium"),
        ("selector", "short_verifiable", "claude-haiku-5-5", "medium"),
        ("orchestrator", "judgment_science", "claude-fable-5-1", "high"),
    ],
)
def test_recommendation_table(role, shape, model, effort):
    rec = recommend(role, shape)
    assert (rec.model, rec.effort) == (model, effort)
    assert rec.reasons


def test_unknown_role_falls_back_to_a_safe_default():
    rec = recommend("mystery", "routing")
    assert rec.model == "claude-sonnet-5-5"


# --- MOD rules --------------------------------------------------------------


def test_mas022_claude_agent_without_effort(make_spec):
    spec = make_spec()
    del spec["agents"][0]["effort"]
    assert _severities(spec, "MAS022") == {"warning"}


def test_mas022_invalid_effort_is_error(make_spec):
    spec = make_spec()
    spec["agents"][0]["effort"] = "turbo"
    assert "error" in _severities(spec, "MAS022")


def test_mas022_non_claude_models_need_no_effort(base_spec):
    assert not any(f.rule_id == "MAS022" and "solver-openai" in f.path for f in lint(base_spec).findings)


def test_mas023_xhigh_on_fan_out_role(make_spec):
    spec = make_spec()
    spec["agents"][0]["effort"] = "xhigh"
    assert _severities(spec, "MAS023") == {"warning"}


def test_mas023_justified_xhigh_passes(make_spec):
    spec = make_spec()
    spec["agents"][0].update(effort="xhigh", effort_justification="evals: +4 pts at xhigh vs high")
    assert _findings(spec, "MAS023") == []


def test_mas024_low_effort_on_search_heavy_role(make_spec):
    spec = make_spec(task={"shape": "cited_report"})
    spec["agents"][0].update(role="researcher", model="claude-haiku-5-5", effort="low")
    assert "warning" in _severities(spec, "MAS024")


def test_mas025_opus_cannot_disable_thinking(make_spec):
    spec = make_spec()
    spec["agents"][0].update(model="claude-opus-5-5", thinking="disabled")
    assert "error" in _severities(spec, "MAS025")


def test_mas025_sonnet_between_tools_needs_high_or_lower(make_spec):
    spec = make_spec()
    spec["agents"][0].update(thinking="between_tools", effort="xhigh", effort_justification="measured")
    assert "error" in _severities(spec, "MAS025")


def test_mas025_haiku_disabled_thinking_at_low_is_fine(make_spec):
    spec = make_spec()
    spec["agents"][-1].update(thinking="disabled", effort="low")
    assert _findings(spec, "MAS025") == []


def test_mas026_visible_reasoning_instruction_on_opus_is_error(make_spec):
    spec = make_spec()
    spec["agents"][0].update(model="claude-opus-5-5", instructions="Think step by step and show your reasoning in the answer.")
    assert "error" in _severities(spec, "MAS026")


def test_mas026_on_haiku_is_warning(make_spec):
    spec = make_spec()
    spec["agents"][-1]["instructions"] = "Explica tu razonamiento paso a paso en la respuesta."
    assert _severities(spec, "MAS026") == {"warning"}


def test_mas027_max_tokens_too_small_for_thinking(make_spec):
    spec = make_spec()
    spec["agents"][0].update(effort="high", max_tokens=8000)
    assert _severities(spec, "MAS027") == {"warning"}


def test_mas028_off_table_choice_is_info_only(make_spec):
    spec = make_spec()
    spec["agents"][-1].update(model="claude-fable-5-1", effort="max", effort_justification="tested")
    assert "info" in _severities(spec, "MAS028")
    assert "warning" not in _severities(spec, "MAS028")


def test_report_lists_model_plan_per_agent(base_spec):
    agents = lint(base_spec).to_dict()["agents"]
    selector = next(a for a in agents if a["id"] == "selector")
    assert selector["model"] == "claude-haiku-5-5"
    assert selector["effort"] == "medium"
    assert selector["recommended"] == {"model": "claude-haiku-5-5", "effort": "medium"}


def test_mas023_single_agent_at_xhigh_is_info(make_spec):
    spec = make_spec()
    spec["agents"][0]["count"] = 1
    spec["agents"][0]["effort"] = "xhigh"
    assert _severities(spec, "MAS023") == {"info"}


def test_mas025_undocumented_combination_is_warning(make_spec):
    spec = make_spec()
    spec["agents"][0].update(model="claude-fable-5-1", thinking="between_tools")
    hits = _findings(spec, "MAS025")
    assert {f.severity.value for f in hits} == {"warning"}
    assert "not documented" in hits[0].message


def test_mas025_haiku_disabled_above_high_is_error(make_spec):
    spec = make_spec()
    spec["agents"][-1].update(thinking="disabled", effort="xhigh", effort_justification="measured")
    assert "error" in _severities(spec, "MAS025")


def test_judge_and_researcher_reasons_cite_their_guides():
    assert "Opus 5.5" in " ".join(recommend("judge", None).reasons)
    assert "Sonnet 5.5" in " ".join(recommend("researcher", "cited_report").reasons)

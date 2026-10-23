"""Skills per agent: reference parsing, definition lint (DEF012-014) and spec rules (MAS029-032)."""

import pytest

from mas_lint import lint
from mas_lint.definitions import lint_definition
from mas_lint.skill_refs import (
    MAX_PRELOADED_SKILLS,
    bare_name,
    discover_skills,
    is_valid_skill_ref,
    parse_skill_list,
)

AGENT = """---
name: reviewer
description: Reviews a design. Use after a spec is drafted.
tools: Read, Grep
model: opus
effort: medium
{skills}---

You review designs.
"""


def agent(skills: str = "") -> str:
    return AGENT.format(skills=skills)


def ids(findings, severities=("error", "warning")):
    return {f.rule_id for f in findings if f.severity.value in severities}


# --- reference helpers ---------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        (["a", "b"], ["a", "b"]),
        ("a, b", ["a", "b"]),
        ("[a, 'b']", ["a", "b"]),
        ("", []),
        (None, []),
    ],
)
def test_parse_skill_list_accepts_yaml_shapes(raw, expected):
    assert parse_skill_list(raw) == expected


def test_valid_refs_allow_plugin_namespace():
    assert is_valid_skill_ref("mas-design")
    assert is_valid_skill_ref("mas-architect:mas-design")
    assert not is_valid_skill_ref("Mas Design")
    assert not is_valid_skill_ref("a:b:c")
    assert bare_name("mas-architect:mas-design") == "mas-design"


def test_discover_skills_finds_siblings_of_agents_dir(tmp_path):
    (tmp_path / "skills" / "alpha").mkdir(parents=True)
    (tmp_path / "skills" / "alpha" / "SKILL.md").write_text("---\nname: alpha\n---\n")
    (tmp_path / "skills" / "no-manifest").mkdir()
    (tmp_path / "agents").mkdir()
    assert discover_skills(tmp_path / "agents" / "x.md") == {"alpha"}


def test_discover_skills_includes_project_claude_dir(tmp_path):
    (tmp_path / ".claude" / "skills" / "beta").mkdir(parents=True)
    (tmp_path / ".claude" / "skills" / "beta" / "SKILL.md").write_text("x")
    (tmp_path / ".claude" / "agents").mkdir()
    assert "beta" in discover_skills(tmp_path / ".claude" / "agents" / "x.md")


# --- agent definition lint -----------------------------------------------


def test_agent_with_known_skills_is_clean():
    text = agent("skills:\n  - mas-audit\n  - mas-architect:mas-design\n")
    assert ids(lint_definition(text, "agent", "agents/reviewer.md", {"mas-audit", "mas-design"})) == set()


def test_unknown_skill_is_flagged_only_when_skills_are_known():
    text = agent("skills: [mas-audti]\n")
    assert "DEF012" in ids(lint_definition(text, "agent", "agents/reviewer.md", {"mas-audit"}))
    assert "DEF012" not in ids(lint_definition(text, "agent", "agents/reviewer.md"))


def test_malformed_skill_name_is_flagged():
    assert "DEF012" in ids(lint_definition(agent("skills: [Bad Name]\n"), "agent", "agents/reviewer.md"))


def test_skill_in_tools_is_deprecated():
    text = agent("").replace("tools: Read, Grep", "tools: Read, Grep, Skill")
    assert "DEF013" in ids(lint_definition(text, "agent", "agents/reviewer.md"))


def test_missing_skills_is_info_and_too_many_is_warning():
    assert "DEF014" in ids(lint_definition(agent(""), "agent", "agents/reviewer.md"), ("info",))
    many = ", ".join(f"s{i}" for i in range(MAX_PRELOADED_SKILLS + 1))
    assert "DEF014" in ids(lint_definition(agent(f"skills: [{many}]\n"), "agent", "agents/reviewer.md"))


def test_explicit_empty_skills_is_a_decision_not_a_gap():
    assert "DEF014" not in ids(lint_definition(agent("skills: []\n"), "agent", "agents/reviewer.md"), ("info", "warning"))


# --- spec rules ------------------------------------------------------------


def _with_skills(base_spec, catalog=None, **per_agent):
    spec = dict(base_spec)
    spec["agents"] = [dict(a) for a in base_spec["agents"]]
    for a in spec["agents"]:
        if a["id"] in per_agent:
            a["skills"] = per_agent[a["id"]]
    if catalog is not None:
        spec["skills"] = catalog
    return spec


def test_clean_examples_declare_skills_for_every_agent(example_paths):
    import json

    for path in example_paths:
        spec = json.loads(path.read_text())
        assert all("skills" in a for a in spec["agents"]), path.name


def test_agent_without_skills_gets_info(base_spec, rule_ids):
    spec = _with_skills(base_spec)
    spec["agents"][0].pop("skills", None)
    assert "MAS029" in rule_ids(spec, ("info",))


def test_skill_missing_from_catalog_is_warning(base_spec, rule_ids):
    first = base_spec["agents"][0]["id"]
    spec = _with_skills(base_spec, catalog=[{"name": "qa-rubric"}], **{first: ["qa-rubrik"]})
    assert "MAS030" in rule_ids(spec)


def test_catalog_accepts_plain_strings_and_namespaced_refs(base_spec, rule_ids):
    first = base_spec["agents"][0]["id"]
    names = [entry["name"] for entry in base_spec["skills"]]
    spec = _with_skills(base_spec, catalog=names + ["qa-rubric"], **{first: ["my-plugin:qa-rubric"]})
    assert "MAS030" not in rule_ids(spec)


def test_too_many_preloaded_skills_is_warning(base_spec, rule_ids):
    first = base_spec["agents"][0]["id"]
    names = [f"s{i}" for i in range(MAX_PRELOADED_SKILLS + 1)]
    spec = _with_skills(base_spec, **{first: names})
    assert "MAS031" in rule_ids(spec)


def test_judge_sharing_generator_playbook_is_warning(base_spec, rule_ids):
    spec = _with_skills(base_spec)
    generator = next(a for a in spec["agents"] if a["role"] in {"worker", "solver", "researcher"})
    judge = next(a for a in spec["agents"] if a["role"] in {"judge", "verifier", "critic", "selector", "reviewer", "evaluator"})
    generator["skills"] = ["solve-playbook"]
    judge["skills"] = ["solve-playbook"]
    assert "MAS032" in rule_ids(spec)


def test_report_model_plan_lists_skills(base_spec):
    first = base_spec["agents"][0]["id"]
    report = lint(_with_skills(base_spec, **{first: ["qa-rubric"]})).to_dict()
    row = next(r for r in report["agents"] if r["id"] == first)
    assert row["skills"] == ["qa-rubric"]

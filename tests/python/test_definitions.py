"""Regex lint for agent and skill definition files."""

from mas_lint.definitions import definition_kind, lint_definition

GOOD_AGENT = """---
name: mas-critic
description: Blind reviewer for multi-agent designs. Use after a spec is drafted.
tools: Read, Grep, Glob
model: opus
---

You review designs without seeing the author's rationale.
"""


def ids(findings, severities=("error", "warning")):
    return {f.rule_id for f in findings if f.severity.value in severities}


def test_kind_detection():
    assert definition_kind("plugin/agents/mas-critic.md") == "agent"
    assert definition_kind(".claude/agents/x.md") == "agent"
    assert definition_kind("skills/mas-design/SKILL.md") == "skill"
    assert definition_kind("docs/agents.md") is None
    assert definition_kind("src/main.py") is None


def test_good_agent_passes():
    assert ids(lint_definition(GOOD_AGENT, "agent", "agents/mas-critic.md")) == set()


def test_missing_frontmatter():
    assert "DEF001" in ids(lint_definition("just text", "agent", "agents/x.md"))


def test_name_must_be_kebab_case():
    text = GOOD_AGENT.replace("name: mas-critic", "name: MAS Critic")
    assert "DEF002" in ids(lint_definition(text, "agent", "agents/x.md"))


def test_description_required():
    text = GOOD_AGENT.replace(
        "description: Blind reviewer for multi-agent designs. Use after a spec is drafted.\n", ""
    )
    assert "DEF003" in ids(lint_definition(text, "agent", "agents/mas-critic.md"))


def test_agent_without_tools_gets_least_privilege_warning():
    text = GOOD_AGENT.replace("tools: Read, Grep, Glob\n", "")
    assert "DEF004" in ids(lint_definition(text, "agent", "agents/mas-critic.md"))


def test_unknown_model_alias():
    text = GOOD_AGENT.replace("model: opus", "model: gpt-banana")
    assert "DEF005" in ids(lint_definition(text, "agent", "agents/mas-critic.md"))


def test_empty_body():
    text = GOOD_AGENT.split("\n---\n")[0] + "\n---\n"
    assert "DEF006" in ids(lint_definition(text, "agent", "agents/mas-critic.md"))


def test_skill_name_should_match_folder():
    skill = "---\nname: other\ndescription: Does things when asked.\n---\nBody\n"
    assert "DEF009" in ids(lint_definition(skill, "skill", "skills/mas-design/SKILL.md"))


def test_block_scalar_description_is_parsed():
    skill = "---\nname: mas-design\ndescription: >\n  Multi-line description\n  that continues.\n---\nBody\n"
    assert ids(lint_definition(skill, "skill", "skills/mas-design/SKILL.md")) == set()


def test_secret_inside_definition_is_error():
    text = GOOD_AGENT + "\nUse token ghp_" + "c" * 36 + "\n"
    assert "DEF007" in ids(lint_definition(text, "agent", "agents/mas-critic.md"))


def test_agent_without_effort_gets_warning():
    assert "DEF010" in ids(lint_definition(GOOD_AGENT, "agent", "agents/mas-critic.md"), severities=("info",))


def test_agent_with_invalid_effort():
    text = GOOD_AGENT.replace("model: opus\n", "model: opus\neffort: ultra\n")
    assert "DEF010" in ids(lint_definition(text, "agent", "agents/mas-critic.md"))


def test_agent_asking_for_visible_reasoning_is_flagged():
    text = GOOD_AGENT + "\nAlways show your reasoning step by step in the final answer.\n"
    assert "DEF011" in ids(lint_definition(text, "agent", "agents/mas-critic.md"))

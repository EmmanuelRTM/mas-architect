"""Dogfooding: the plugin's own agents, skills and manifests pass its checks."""

import json

import pytest

from conftest import ROOT
from mas_lint.definitions import definition_kind, lint_definition
from mas_lint.secrets import find_secrets

AGENTS = sorted((ROOT / "agents").glob("*.md"))
SKILLS = sorted((ROOT / "skills").glob("*/SKILL.md"))
EXPECTED_SKILLS = {"mas-design", "mas-patterns", "mas-selection-verification", "mas-model-selection", "mas-audit"}
EXPECTED_AGENTS = {"mas-architect", "mas-critic", "mas-model-planner", "mas-prompt-writer", "mas-system-auditor"}


def test_expected_skills_and_agents_exist():
    assert {p.parent.name for p in SKILLS} == EXPECTED_SKILLS
    assert {p.stem for p in AGENTS} == EXPECTED_AGENTS


@pytest.mark.parametrize("path", AGENTS + SKILLS, ids=lambda p: p.parent.name + "/" + p.name)
def test_definition_is_clean(path):
    kind = definition_kind(str(path))
    findings = lint_definition(path.read_text(encoding="utf-8"), kind, str(path))
    serious = [f"{f.rule_id}: {f.message}" for f in findings if f.severity.value != "info"]
    assert serious == []


@pytest.mark.parametrize("path", AGENTS, ids=lambda p: p.stem)
def test_every_agent_declares_model_and_effort(path):
    head = path.read_text(encoding="utf-8").split("---")[1]
    assert "\nmodel:" in head and "\neffort:" in head


def test_manifests_are_valid_and_not_authored_by_claude():
    for name in ("plugin.json", "marketplace.json"):
        data = json.loads((ROOT / ".claude-plugin" / name).read_text())
        assert "claude" not in json.dumps(data.get("author", data.get("owner", {}))).lower()


def test_hooks_config_points_at_existing_scripts():
    config = json.loads((ROOT / "hooks" / "hooks.json").read_text())
    scripts = [
        arg.replace("${CLAUDE_PLUGIN_ROOT}/", "")
        for groups in config["hooks"].values()
        for group in groups
        for hook in group["hooks"]
        for arg in hook.get("args", [])
    ]
    assert scripts and all((ROOT / s).is_file() for s in scripts)


def test_no_file_in_the_plugin_holds_a_secret():
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".json", ".py", ".ts", ".tsx"} and ".git" not in path.parts:
            assert find_secrets(path.read_text(encoding="utf-8", errors="ignore")) == [], path


def test_source_files_stay_under_500_lines():
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".ts", ".tsx"} and ".claude-plugin" not in path.parts:
            assert sum(1 for _ in path.open(encoding="utf-8")) < 500, path


def test_rules_doc_lists_every_rule():
    from mas_lint.rules import registered

    doc = (ROOT / "docs" / "RULES.md").read_text(encoding="utf-8")
    missing = [r.id for r in registered() if f"| {r.id} |" not in doc]
    assert missing == [], "regenerate docs/RULES.md"


@pytest.mark.parametrize("path", AGENTS, ids=lambda p: p.stem)
def test_every_agent_preloads_only_existing_plugin_skills(path):
    from mas_lint import frontmatter
    from mas_lint.skill_refs import MAX_PRELOADED_SKILLS, bare_name, parse_skill_list

    skills = parse_skill_list(frontmatter.parse(path.read_text(encoding="utf-8")).fields.get("skills"))
    assert 1 <= len(skills) <= MAX_PRELOADED_SKILLS
    assert {bare_name(s) for s in skills} <= EXPECTED_SKILLS


def test_blind_critic_does_not_share_the_architects_playbook():
    from mas_lint import frontmatter
    from mas_lint.skill_refs import parse_skill_list

    def skills_of(stem):
        text = (ROOT / "agents" / f"{stem}.md").read_text(encoding="utf-8")
        return set(parse_skill_list(frontmatter.parse(text).fields.get("skills")))

    assert "mas-design" not in skills_of("mas-critic")
    assert "mas-design" in skills_of("mas-architect")

"""End-to-end tests of the hook scripts through their stdin/stdout contract."""

import json
import shutil
import subprocess
import sys

from conftest import EXAMPLES, FIXTURES, SCRIPTS


def run_hook(script, payload, env=None):
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def test_guard_denies_write_with_secret(tmp_path):
    payload = {
        "hook_event_name": "PreToolUse",
        "cwd": str(tmp_path),
        "tool_name": "Write",
        "tool_input": {"file_path": str(tmp_path / "cfg.py"), "content": "KEY = '" + "sk-ant-api03-" + "q" * 40 + "'"},
    }
    out = run_hook("hook_guard_secrets.py", payload)
    decision = out["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "anthropic-api-key" in decision["permissionDecisionReason"]
    assert "q" * 40 not in decision["permissionDecisionReason"]


def test_guard_checks_edit_and_multiedit(tmp_path):
    edit = {
        "tool_name": "MultiEdit",
        "cwd": str(tmp_path),
        "tool_input": {"file_path": "x.py", "edits": [{"old_string": "a", "new_string": "AKIA" + "ABCDEFGHIJKLMNOP"}]},
    }
    assert run_hook("hook_guard_secrets.py", edit)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_guard_allows_clean_write(tmp_path):
    payload = {"tool_name": "Write", "cwd": str(tmp_path), "tool_input": {"file_path": "a.py", "content": "print(1)"}}
    assert run_hook("hook_guard_secrets.py", payload) is None


def test_lint_hook_ignores_other_files(tmp_path):
    payload = {"tool_name": "Write", "cwd": str(tmp_path), "tool_input": {"file_path": str(tmp_path / "a.json")}}
    assert run_hook("hook_lint_spec.py", payload) is None


def test_lint_hook_blocks_on_errors_and_writes_report(tmp_path):
    spec = tmp_path / "bad.mas.json"
    shutil.copy(FIXTURES / "antipatterns.mas.json", spec)
    payload = {"tool_name": "Write", "cwd": str(tmp_path), "tool_input": {"file_path": str(spec)}}
    out = run_hook("hook_lint_spec.py", payload)
    assert out["decision"] == "block"
    assert "MAS001" in out["reason"]
    report = json.loads((tmp_path / ".mas" / "last-report.json").read_text())
    assert report["spec"] == "everything-wrong"
    assert (tmp_path / ".mas" / "reports" / "everything-wrong.json").exists()


def test_lint_hook_adds_context_on_clean_spec(tmp_path):
    spec = tmp_path / "ok.mas.json"
    shutil.copy(EXAMPLES / "qa-selector.mas.json", spec)
    payload = {"tool_name": "Edit", "cwd": str(tmp_path), "tool_input": {"file_path": str(spec)}}
    out = run_hook("hook_lint_spec.py", payload)
    assert "decision" not in out
    assert "0 errors" in out["hookSpecificOutput"]["additionalContext"]


def test_lint_hook_reports_unparseable_spec(tmp_path):
    spec = tmp_path / "broken.mas.json"
    spec.write_text("{ not json")
    payload = {"tool_name": "Write", "cwd": str(tmp_path), "tool_input": {"file_path": str(spec)}}
    out = run_hook("hook_lint_spec.py", payload)
    assert out["decision"] == "block"


def test_definitions_hook_blocks_bad_agent(tmp_path):
    agent = tmp_path / "agents" / "bad.md"
    agent.parent.mkdir()
    agent.write_text("---\nname: Bad Name\n---\nbody\n")
    payload = {"tool_name": "Write", "cwd": str(tmp_path), "tool_input": {"file_path": str(agent)}}
    out = run_hook("hook_validate_definitions.py", payload)
    assert out["decision"] == "block"
    assert "DEF002" in out["reason"]


def test_spawn_contract_adds_context_without_done_criterion(tmp_path):
    payload = {"tool_name": "Agent", "cwd": str(tmp_path), "tool_input": {"description": "look", "prompt": "Look around the repo."}}
    out = run_hook("hook_spawn_contract.py", payload)
    assert "done criterion" in out["hookSpecificOutput"]["additionalContext"].lower()


def test_spawn_contract_passes_with_criterion(tmp_path):
    prompt = "Map the auth module. Done when: a list of files with one-line roles is returned."
    payload = {"tool_name": "Agent", "cwd": str(tmp_path), "tool_input": {"description": "map", "prompt": prompt}}
    assert run_hook("hook_spawn_contract.py", payload) is None


def test_spawn_contract_strict_mode_denies(tmp_path):
    import os

    env = dict(os.environ, MAS_ARCHITECT_SPAWN_CONTRACT="strict")
    payload = {"tool_name": "Agent", "cwd": str(tmp_path), "tool_input": {"description": "x", "prompt": "Do it."}}
    out = run_hook("hook_spawn_contract.py", payload, env=env)
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_hooks_survive_garbage_input():
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "hook_lint_spec.py")], input="not json", capture_output=True, text=True
    )
    assert proc.returncode == 0


def test_definitions_hook_flags_unknown_sibling_skill(tmp_path):
    (tmp_path / "skills" / "qa-rubric").mkdir(parents=True)
    (tmp_path / "skills" / "qa-rubric" / "SKILL.md").write_text("---\nname: qa-rubric\ndescription: d\n---\nBody\n")
    (tmp_path / "agents").mkdir()
    agent = tmp_path / "agents" / "judge.md"
    agent.write_text(
        "---\nname: judge\ndescription: Grades answers. Use after solving.\ntools: Read\n"
        "skills:\n  - qa-rubrik\nmodel: opus\neffort: high\n---\nGrade the answers.\n"
    )
    payload = {"tool_name": "Write", "cwd": str(tmp_path), "tool_input": {"file_path": str(agent)}}
    out = run_hook("hook_validate_definitions.py", payload)
    assert "DEF012" in out["hookSpecificOutput"]["additionalContext"]
    assert "qa-rubrik" in out["hookSpecificOutput"]["additionalContext"]


def test_lint_hook_emits_decision_when_report_dir_is_unwritable(tmp_path):
    import os

    spec = tmp_path / "bad.mas.json"
    shutil.copy(FIXTURES / "antipatterns.mas.json", spec)
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("x")
    env = dict(os.environ, MAS_ARCHITECT_REPORT_DIR=str(blocker))
    payload = {"tool_name": "Write", "cwd": str(tmp_path), "tool_input": {"file_path": str(spec)}}
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "hook_lint_spec.py")], input=json.dumps(payload), capture_output=True, text=True, env=env
    )
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["decision"] == "block"
    assert "report" in proc.stderr.lower()


def test_session_limits_hook_adds_context(tmp_path):
    payload = {"hook_event_name": "SessionStart", "cwd": str(tmp_path), "source": "startup"}
    out = run_hook("hook_session_limits.py", payload)
    block = out["hookSpecificOutput"]
    assert block["hookEventName"] == "SessionStart"
    text = block["additionalContext"]
    for needle in ("20 concurrent subagents", "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS", "three", "16", "256", "1,000", "4,096", "25 agents", "1.5 million", "prompt cache"):
        assert needle in text, needle
    for command in ("new", "lint", "models", "audit", "baseline", "generate", "review", "verify"):
        assert f"/mas-architect:{command}" in text, command
    assert "/mas-panel" in text

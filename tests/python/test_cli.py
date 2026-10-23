"""The command line: `rules --markdown` is what docs/RULES.md is generated from."""

import io
from contextlib import redirect_stdout

from mas_lint_cli import main


def _run(*argv):
    out = io.StringIO()
    with redirect_stdout(out):
        code = main(list(argv))
    return code, out.getvalue()


def test_rules_plain_lists_ids():
    code, text = _run("rules")
    assert code == 0 and "MAS001" in text and "|" not in text


def test_rules_markdown_prints_both_tables():
    from mas_lint.rules import registered

    code, text = _run("rules", "--markdown")
    assert code == 0
    assert "| Regla | Práctica | Qué verifica | Evidencia |" in text
    assert "| Regla | Severidad | Qué verifica |" in text
    for rule in registered():
        assert f"| {rule.id} | {rule.practice} | {rule.title} |" in text
    assert "| DEF001 | error |" in text

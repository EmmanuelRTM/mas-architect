#!/usr/bin/env python3
"""PostToolUse (Write|Edit|MultiEdit): lint `*.mas.json` specs after every change.

Errors block (Claude sees the reason and fixes the spec); warnings come back
as context. The JSON report lands in `<cwd>/.mas/` for the control panel.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from mas_lint import SpecLoadError, lint, load_spec
from mas_lint.formatting import format_findings_brief
from mas_lint.hookio import WRITE_TOOLS, post_block, post_context, run, target_path
from mas_lint.loader import is_spec_path


def report_dir(event: dict) -> Path:
    override = os.environ.get("MAS_ARCHITECT_REPORT_DIR")
    return Path(override) if override else Path(event.get("cwd") or os.getcwd()) / ".mas"


def save_report(directory: Path, data: dict) -> None:
    (directory / "reports").mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", data.get("spec") or "unnamed")
    text = json.dumps(data, indent=2, ensure_ascii=False)
    (directory / "reports" / f"{safe}.json").write_text(text, encoding="utf-8")
    (directory / "last-report.json").write_text(text, encoding="utf-8")


def handle(event: dict) -> dict | None:
    if event.get("tool_name") not in WRITE_TOOLS:
        return None
    path = target_path(event)
    if path is None or not is_spec_path(path):
        return None
    try:
        spec = load_spec(path)
    except SpecLoadError as exc:
        return post_block(f"mas-architect: {path.name} could not be parsed ({exc}). Fix the syntax.")
    report = lint(spec)
    data = report.to_dict()
    data["path"] = str(path)
    save_report(report_dir(event), data)
    summary = report.summary()
    headline = f"mas-architect lint of {path.name}: {summary['error']} errors, {summary['warning']} warnings."
    if report.has_errors:
        return post_block(f"{headline} Fix the errors:\n{format_findings_brief(report)}")
    detail = format_findings_brief(report)
    return post_context(headline + ("\n" + detail if detail else ""))


if __name__ == "__main__":
    sys.exit(run(handle))

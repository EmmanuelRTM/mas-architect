"""Human-readable rendering of a report (JSON comes from Report.to_dict)."""

from __future__ import annotations

from .model import Report, Severity
from .practices import PRACTICES

_ICON = {"pass": "✓", "warn": "!", "fail": "✗", "n/a": "·"}


def format_text(report: Report, include_info: bool = True) -> str:
    summary = report.summary()
    lines = [
        f"MAS lint: {report.spec_name} — {summary['error']} errors, {summary['warning']} warnings, {summary['info']} info",
        "",
    ]
    for finding in report.findings:
        if finding.severity is Severity.INFO and not include_info:
            continue
        where = f" [{finding.path}]" if finding.path else ""
        lines.append(f"{finding.severity.value.upper():7} {finding.rule_id} ({finding.practice}){where}: {finding.message}")
    lines += ["", "Practices:"]
    for practice in PRACTICES:
        status = report.practices.get(practice.id, "pass")
        lines.append(f"  {_ICON[status]} {practice.id:4} {practice.title}")
    n_eff = report.metrics.get("effective_team_size")
    if n_eff is not None:
        lines += ["", f"Effective team size: {n_eff} (saturation ~{report.metrics.get('saturation_size')})"]
    return "\n".join(lines)


def format_findings_brief(report: Report, limit: int = 12) -> str:
    """Compact list for hook feedback: errors and warnings only."""
    rows = [f for f in report.findings if f.severity is not Severity.INFO]
    out = [f"- {f.rule_id} {f.severity.value}: {f.message}" for f in rows[:limit]]
    if len(rows) > limit:
        out.append(f"- ... and {len(rows) - limit} more (see .mas/last-report.json)")
    return "\n".join(out)

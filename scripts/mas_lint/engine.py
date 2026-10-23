"""Run every registered rule over a spec and build a report."""

from __future__ import annotations

from typing import Iterable

from .accessors import agent_skills, agents, instances, shape
from .catalog import resolve_model
from .metrics import compute_metrics
from .model import Finding, Report, Severity
from .model_advisor import recommend
from .practices import PRACTICE_IDS
from .rules import Rule, registered


def lint(spec: dict, rules: Iterable[Rule] | None = None) -> Report:
    findings: list[Finding] = []
    for rule in rules if rules is not None else registered():
        findings.extend(rule.check(spec))
    findings.sort(key=lambda f: (f.severity.rank, f.rule_id, f.path))
    name = spec.get("name") if isinstance(spec.get("name"), str) else "unnamed"
    return Report(
        spec_name=name or "unnamed",
        findings=findings,
        metrics=compute_metrics(spec),
        practices=_practice_status(spec, findings),
        agents=_model_plan(spec),
        monitoring=_section(spec, "monitoring"),
        platform=_section(spec, "platform"),
    )


def _section(spec: dict, key: str) -> dict:
    value = spec.get(key)
    return dict(value) if isinstance(value, dict) else {}


def _practice_status(spec: dict, findings: list[Finding]) -> dict[str, str]:
    status = {pid: "pass" for pid in PRACTICE_IDS}
    if not isinstance(spec.get("training"), dict):
        status["P10"] = "n/a"
    for finding in findings:
        current = status.get(finding.practice, "pass")
        if finding.severity is Severity.ERROR:
            status[finding.practice] = "fail"
        elif finding.severity is Severity.WARNING and current != "fail":
            status[finding.practice] = "warn"
    return status


def _model_plan(spec: dict) -> list[dict]:
    plan = []
    for agent in agents(spec):
        model = resolve_model(agent.get("model"))
        plan.append(
            {
                "id": agent.get("id"),
                "role": agent.get("role"),
                "count": instances(agent),
                "model": model.id if model else agent.get("model"),
                "effort": agent.get("effort") or (model.default_effort if model else None),
                "effort_is_default": agent.get("effort") is None and model is not None,
                "skills": agent_skills(agent),
                "recommended": recommend(agent.get("role"), shape(spec)).to_dict(),
            }
        )
    return plan

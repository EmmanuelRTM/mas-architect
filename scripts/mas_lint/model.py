"""Value objects shared by every part of the linter."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

    @property
    def rank(self) -> int:
        return {"error": 0, "warning": 1, "info": 2}[self.value]


@dataclass(frozen=True)
class Finding:
    """One rule violation or observation. `path` points into the spec."""

    rule_id: str
    severity: Severity
    message: str
    practice: str
    path: str = ""
    evidence: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


@dataclass
class Report:
    spec_name: str
    findings: list[Finding] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    practices: dict[str, str] = field(default_factory=dict)
    agents: list[dict[str, Any]] = field(default_factory=list)
    monitoring: dict[str, Any] = field(default_factory=dict)
    platform: dict[str, Any] = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        return any(f.severity is Severity.ERROR for f in self.findings)

    def count(self, severity: Severity) -> int:
        return sum(1 for f in self.findings if f.severity is severity)

    def summary(self) -> dict[str, int]:
        return {s.value: self.count(s) for s in Severity}

    def to_dict(self) -> dict[str, Any]:
        return {
            "spec": self.spec_name,
            "summary": self.summary(),
            "practices": dict(self.practices),
            "metrics": dict(self.metrics),
            "agents": list(self.agents),
            "monitoring": dict(self.monitoring),
            "platform": dict(self.platform),
            "findings": [f.to_dict() for f in self.findings],
        }

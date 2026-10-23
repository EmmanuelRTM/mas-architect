"""Rule contract and registry.

A rule is a small class with an id, a practice and a `check` method. New
rules are added by writing a class with `@register` — the engine never
changes (open/closed principle).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Iterator

from ..model import Finding, Severity

_REGISTRY: list["Rule"] = []


class Rule(ABC):
    id: str = ""
    title: str = ""
    practice: str = ""
    evidence: str = ""

    @abstractmethod
    def check(self, spec: dict) -> Iterable[Finding]:
        """Yield findings for this spec; yield nothing when it passes."""

    def finding(self, severity: Severity, message: str, path: str = "") -> Finding:
        return Finding(
            rule_id=self.id,
            severity=severity,
            message=message,
            practice=self.practice,
            path=path,
            evidence=self.evidence,
        )

    def error(self, message: str, path: str = "") -> Finding:
        return self.finding(Severity.ERROR, message, path)

    def warning(self, message: str, path: str = "") -> Finding:
        return self.finding(Severity.WARNING, message, path)

    def info(self, message: str, path: str = "") -> Finding:
        return self.finding(Severity.INFO, message, path)


def register(cls: type[Rule]) -> type[Rule]:
    if not cls.id or not cls.practice:
        raise ValueError(f"{cls.__name__} needs an id and a practice")
    if any(r.id == cls.id for r in _REGISTRY):
        raise ValueError(f"duplicate rule id {cls.id}")
    _REGISTRY.append(cls())
    return cls


def registered() -> Iterator[Rule]:
    return iter(sorted(_REGISTRY, key=lambda r: r.id))

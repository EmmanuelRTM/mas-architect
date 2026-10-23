"""Deterministic, regex-based secret detection.

Matches report the kind and the line only, never the matched value, so a
finding can be shown to a person or a model without leaking the secret.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("anthropic-api-key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("openai-api-key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}\b")),
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b")),
    ("slack-token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    (
        "generic-secret-assignment",
        re.compile(
            r"""(?ix)
            \b(?:api[_-]?key|secret|token|passw(?:or)?d|client[_-]?secret|access[_-]?key)\b
            \s*[:=]\s*
            (['"])(?P<value>[^'"\s]{12,})\1
            """
        ),
    ),
)

# Values that are clearly placeholders or references, not secrets.
_PLACEHOLDER = re.compile(
    r"""(?ix)
    ^\$\{.*\}$ | ^\$[A-Z_][A-Z0-9_]*$ | ^<.*>$ | ^\{\{.*\}\}$ |
    your[-_ ] | example | changeme | placeholder | dummy | redacted | xxxx | \*\*\*\*
    """
)


@dataclass(frozen=True)
class SecretMatch:
    kind: str
    line: int

    def __repr__(self) -> str:  # never include the value
        return f"SecretMatch(kind={self.kind!r}, line={self.line})"


def find_secrets(text: str) -> list[SecretMatch]:
    matches: list[SecretMatch] = []
    for kind, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            value = match.groupdict().get("value")
            if value is not None and _PLACEHOLDER.search(value):
                continue  # only free-form assignments can be placeholders
            matches.append(SecretMatch(kind=kind, line=text.count("\n", 0, match.start()) + 1))
    return sorted(matches, key=lambda m: (m.line, m.kind))


def describe(matches: list[SecretMatch]) -> str:
    return ", ".join(f"{m.kind} (line {m.line})" for m in matches)

"""OPS: never hardcode secrets in a spec."""

from __future__ import annotations

from ..accessors import walk_strings
from ..secrets import find_secrets
from .base import Rule, register


@register
class NoSecretsRule(Rule):
    id = "MAS019"
    title = "No hardcoded secrets"
    practice = "OPS"
    evidence = "Secrets belong in the environment or a secret store, referenced by name."

    def check(self, spec):
        for path, value in walk_strings(spec):
            for match in find_secrets(value):
                yield self.error(
                    f"Possible {match.kind} in `{path}`. Reference it by environment variable (e.g. ${{MY_API_KEY}}) instead.",
                    path,
                )

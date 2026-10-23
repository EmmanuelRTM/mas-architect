"""P1: measure the strong single-agent baseline before building a team."""

from __future__ import annotations

from ..accessors import get, is_number
from .base import Rule, register


@register
class BaselineRule(Rule):
    id = "MAS001"
    title = "Single-agent baseline measured"
    practice = "P1"
    evidence = "Coordination's benefit shrinks as the single agent strengthens (Nature MI 2026; arXiv 2608.22152)."

    def check(self, spec):
        score = get(spec, "baseline.single_agent_score")
        if not is_number(score):
            yield self.error(
                "Record `baseline.single_agent_score` (a number) for the strongest single agent at matched "
                "budget before adding agents; without it you cannot tell whether the team helps.",
                "baseline.single_agent_score",
            )

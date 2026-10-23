"""P1: measure the strong single-agent baseline before building a team."""

from __future__ import annotations

from ..accessors import get, is_number
from .base import Rule, register

MIN_BASELINE_RUNS = 3
CEILING_RATIO = 0.85


@register
class BaselineRule(Rule):
    id = "MAS001"
    title = "Single-agent baseline measured"
    practice = "P1"
    evidence = (
        "Coordination's benefit shrinks as the single agent strengthens: a capability-saturation threshold predicted "
        "the coordination effect in 94% of validation configurations (Nature MI 2026) and the Collaboration Tax's "
        "penalty shrinks for stronger models (arXiv 2608.22152)."
    )

    def check(self, spec):
        score = get(spec, "baseline.single_agent_score")
        if not is_number(score):
            yield self.error(
                "Record `baseline.single_agent_score` (a number) for the strongest single agent at matched "
                "budget before adding agents; without it you cannot tell whether the team helps.",
                "baseline.single_agent_score",
            )
            return
        ceiling = get(spec, "baseline.max_score")
        if is_number(ceiling) and ceiling > 0 and score / ceiling >= CEILING_RATIO:
            yield self.warning(
                f"The single agent scores {score} of {ceiling} ({score / ceiling:.0%}): near ceiling the "
                "coordination tax likely exceeds the gain. Measure the team against this baseline before building it.",
                "baseline.single_agent_score",
            )
        runs = get(spec, "baseline.runs")
        if not is_number(runs) or runs < MIN_BASELINE_RUNS:
            yield self.warning(
                f"Set `baseline.runs` to at least {MIN_BASELINE_RUNS}: one run of the single agent is not a baseline, "
                "the same metric over repeated runs is.",
                "baseline.runs",
            )

"""P9 monitor beliefs and repeated runs; P10 team-level credit in training."""

from __future__ import annotations

from ..accessors import get, is_number
from .base import Rule, register

MIN_RUNS = 3
TEAM_CREDIT = frozenset({"team", "active_set", "set_level"})


@register
class RepeatedRunsRule(Rule):
    id = "MAS014"
    title = "Judge repeated runs, not the best run"
    practice = "P9"
    evidence = "Full closure in all three runs on 18.0% of tasks vs 32.7% of single attempts (PhysClosureBench)."

    def check(self, spec):
        runs = get(spec, "monitoring.repeated_runs")
        if not is_number(runs) or runs < MIN_RUNS:
            yield self.warning(
                f"Set `monitoring.repeated_runs` to at least {MIN_RUNS}; single best runs overstate reliability.",
                "monitoring.repeated_runs",
            )


@register
class BeliefProbeRule(Rule):
    id = "MAS015"
    title = "Probe private beliefs in debates"
    practice = "P9"
    evidence = "One adversarial peer lifted private false-belief adoption 0.6% -> 44.8%; only 19.7% showed it publicly (2610.22138)."

    def check(self, spec):
        debating = get(spec, "communication.debate") is True or get(spec, "communication.mode") in ("broadcast", "debate")
        if debating and get(spec, "monitoring.belief_probes") is not True:
            yield self.warning(
                "Agents that discuss with each other need private belief probes (`monitoring.belief_probes: true`); "
                "transcripts hide most infection.",
                "monitoring.belief_probes",
            )


@register
class TeamCreditRule(Rule):
    id = "MAS021"
    title = "Team-level credit and decorrelated training"
    practice = "P10"
    evidence = "Set-level credit (SRPO) beats per-response GRPO by 3.5-7.6 pts on search; cross-family peer rewards (Co-RL)."

    def check(self, spec):
        training = spec.get("training")
        if not isinstance(training, dict):
            return
        if training.get("credit_assignment") not in TEAM_CREDIT:
            yield self.warning(
                "Assign credit to team decisions (`credit_assignment`: team, active_set or set_level), not single responses.",
                "training.credit_assignment",
            )
        families = training.get("peer_families")
        if not (isinstance(families, int) and families >= 2) and training.get("decorrelation") is not True:
            yield self.info("Train peers across >= 2 model families (or reward decorrelation) to keep errors independent.", "training")

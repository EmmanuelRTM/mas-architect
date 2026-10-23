"""P9 monitor beliefs and repeated runs; P10 team-level credit in training."""

from __future__ import annotations

from ..accessors import get, is_number
from .base import Rule, register

MIN_RUNS = 3
TEAM_CREDIT = frozenset({"team", "active_set", "set_level"})
PEER_CHANNELS = frozenset({"passive", "non_blocking", "broadcast", "debate"})
HERDING_RANKINGS = frozenset({"popularity", "citation"})


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


@register
class CommitmentLogRule(Rule):
    id = "MAS037"
    title = "Log commitments; do not rank by popularity"
    practice = "P9"
    evidence = (
        "Agents sharing a machine formed coalitions in up to 79% of rounds and made unsanctioned commitments "
        "(SCARCE 2610.21029); popularity drifted 9x further from quality than in humans (2610.30769)."
    )

    def check(self, spec):
        peers = get(spec, "platform.shared_resources") is True or get(spec, "communication.mode") in PEER_CHANNELS
        if peers and get(spec, "monitoring.commitment_log") is not True:
            yield self.warning(
                "Agents that share a channel or a machine make commitments to each other. Set "
                "`monitoring.commitment_log: true` so every promise is logged for the principal to sanction or revoke.",
                "monitoring.commitment_log",
            )
        ranking = get(spec, "communication.ranking")
        if ranking in HERDING_RANKINGS:
            yield self.info(
                f"Shared findings ranked by {ranking} herd agents toward early movers, not quality. Rank by evidence "
                "or show items in a fixed order.",
                "communication.ranking",
            )

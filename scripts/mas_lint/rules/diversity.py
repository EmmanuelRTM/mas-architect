"""P2: generate independently across diverse models; keep exploration private."""

from __future__ import annotations

import math

from ..accessors import generator_instances, generators, get, is_number
from ..metrics import effective_team_size, saturation_size
from .base import Rule, register


@register
class ModelDiversityRule(Rule):
    id = "MAS002"
    title = "Decorrelated generators"
    practice = "P2"
    evidence = "Cross-family pairing lowers error overlap from kappa 0.53 to 0.38 (Co-RL); same-model teams score zero on some tasks (2608.23541)."

    def check(self, spec):
        gens = generators(spec)
        if generator_instances(spec) < 3:
            return
        models = {a.get("model") for a in gens if a.get("model")}
        families = {a.get("model_family") for a in gens if a.get("model_family")}
        if len(models) <= 1:
            yield self.warning(
                "Every generator runs the same model, so their errors correlate and extra agents add little. "
                "Mix at least two models, ideally from different families.",
                "agents",
            )
        elif len(families) <= 1:
            yield self.info(
                "Generators use several models from one family; adding another family lowers error overlap further.",
                "agents",
            )


@register
class NoBroadcastRule(Rule):
    id = "MAS003"
    title = "No full-solution broadcast"
    practice = "P2"
    evidence = "Solution distance fell 0.315 -> 0.229 after interaction; synthesizers copied the best proposer >=80% of the time (2608.23541)."

    def check(self, spec):
        if get(spec, "communication.share_full_solutions") is True:
            yield self.warning(
                "Sharing full solutions collapses diversity within a round. Share findings or claims, "
                "keep candidate solutions private until selection.",
                "communication.share_full_solutions",
            )


@register
class EffectiveTeamSizeRule(Rule):
    id = "MAS017"
    title = "Replica count vs error correlation"
    practice = "P2"
    evidence = "N_eff = N/(1+(N-1)rho) tends to 1/rho; rho 0.9 leaves ~1.1 effective agents out of 30 (2609.31563)."

    def check(self, spec):
        rho = get(spec, "budget.expected_error_correlation")
        candidates = get(spec, "selection.candidates")
        replicas = candidates if isinstance(candidates, int) and candidates > 0 else generator_instances(spec)
        if replicas < 2:
            return
        if not is_number(rho) or not 0 <= rho <= 1:
            yield self.info(
                "Estimate `budget.expected_error_correlation` (0-1) from a pilot run to size the replica pool.",
                "budget.expected_error_correlation",
            )
            return
        n_eff = effective_team_size(replicas, rho)
        sat = saturation_size(rho)
        if not math.isinf(sat) and replicas > 2 and replicas > 2 * math.ceil(sat):
            yield self.warning(
                f"{replicas} replicas at rho={rho} behave like {n_eff:.1f} independent agents (ceiling ~{sat:.1f}). "
                "Cut the pool or decorrelate it (other families, isolated contexts) and spend the savings on selection.",
                "selection.candidates",
            )
        else:
            yield self.info(f"Effective team size: {n_eff:.2f} of {replicas} replicas at rho={rho}.", "selection.candidates")

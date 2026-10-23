"""P3: spend on selection rather than on more voters."""

from __future__ import annotations

from ..accessors import generator_instances, get
from .base import Rule, register

VOTING = frozenset({"majority_vote", "plurality", "confidence_vote"})


@register
class SelectorRule(Rule):
    id = "MAS004"
    title = "Evidence-grounded or bias-controlled selection"
    practice = "P3"
    evidence = "Oracle 92.6 vs majority 72.6 on BrowseComp; RGV lifts to 78.9 at ~0.3 ms/rollout (2608.24024); TRACE 1/258 of AggAgent cost (2609.39912)."

    def check(self, spec):
        strategy = get(spec, "selection.strategy")
        candidates = get(spec, "selection.candidates")
        pool = candidates if isinstance(candidates, int) else generator_instances(spec)
        if strategy in VOTING and pool >= 3:
            yield self.warning(
                f"`{strategy}` strands most of the pool's coverage. Use an evidence-grounded selector (score each "
                "answer by support in documents it retrieved) or a bias-controlled judge (dedupe, normalize style, "
                "swap order).",
                "selection.strategy",
            )
        elif strategy == "llm_aggregator":
            yield self.info(
                "LLM aggregators cost 122-258x a trained evidence selector after rollouts; check the cost is worth it.",
                "selection.strategy",
            )


@register
class RevisionPeersRule(Rule):
    id = "MAS005"
    title = "Revision saturates after one or two peers"
    practice = "P3"
    evidence = "Revising against 1 peer gained 26.5 points, against 29 peers 26.6 (2609.31563)."

    def check(self, spec):
        peers = get(spec, "selection.revision_peers")
        if isinstance(peers, int) and peers > 2:
            yield self.info(
                f"{peers} revision peers cost context without measured gain; one or two peers capture the effect.",
                "selection.revision_peers",
            )

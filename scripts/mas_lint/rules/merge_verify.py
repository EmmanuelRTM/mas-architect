"""P7 raw evidence to the merger, P8 judge separated from generator."""

from __future__ import annotations

from ..accessors import GENERATOR_ROLES, agent_by_id, generators, get, shape
from .base import Rule, register


@register
class RawEvidenceMergeRule(Rule):
    id = "MAS012"
    title = "Raw evidence, not summaries, to the merger"
    practice = "P7"
    evidence = "Orchestrator introduced 84.7% of report errors; snippets instead of notes lifted citation precision 87.6 -> 94.1 (2608.24306)."

    def check(self, spec):
        if get(spec, "merge.input") != "summaries":
            return
        message = (
            "The merge step receives summaries, which is where citations break. Pass raw snippets or evidence "
            "with their sources to whatever merges the work."
        )
        if shape(spec) == "cited_report":
            yield self.error(message, "merge.input")
        else:
            yield self.warning(message, "merge.input")


@register
class JudgeSeparationRule(Rule):
    id = "MAS013"
    title = "A judge that did not do the work"
    practice = "P8"
    evidence = "Fresh reviewers avoid anchoring (2609.14738); cross-fitted verifiers cut false agreement 6-9% -> 3-4% (2609.39102)."

    def check(self, spec):
        judges = get(spec, "verification.judge_agents") or []
        if not judges:
            yield self.error(
                "Declare `verification.judge_agents`: a verifier, critic or selector separate from the generators.",
                "verification.judge_agents",
            )
            return
        by_id = agent_by_id(spec)
        generator_models = {a.get("model") for a in generators(spec) if a.get("model")}
        for judge_id in judges:
            judge = by_id.get(judge_id)
            if judge is None:
                continue  # MAS020 reports it
            path = f"agents.{judge_id}"
            if judge.get("role") in GENERATOR_ROLES:
                yield self.error(f"judge {judge_id!r} is also a generator ({judge.get('role')}); it grades its own work.", path)
                continue
            if judge.get("memoryless") is not True:
                yield self.warning(f"judge {judge_id!r} should be memoryless (fresh context per review) to avoid anchoring.", path)
            if generator_models and generator_models == {judge.get("model")}:
                yield self.warning(
                    f"judge {judge_id!r} runs the only model the generators use, so it shares their blind spots.", path
                )

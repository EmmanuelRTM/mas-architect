"""P7 raw evidence to the merger, P8 judge separated from generator."""

from __future__ import annotations

from ..accessors import GENERATOR_ROLES, agent_by_id, generator_instances, generators, get, instances, shape
from .base import Rule, register

SHARED_MODEL_WARNING_SHARE = 0.5


@register
class RawEvidenceMergeRule(Rule):
    id = "MAS012"
    title = "Raw evidence, not summaries, to the merger"
    practice = "P7"
    evidence = (
        "Orchestrator introduced 84.7% of report errors; snippets instead of notes lifted citation precision "
        "87.6 -> 94.1 (2608.24306); DAGent passes compact summaries plus a recall tool over full transcripts (2609.39154)."
    )

    def check(self, spec):
        merge_input = get(spec, "merge.input")
        if merge_input == "full_transcripts":
            yield self.info(
                "The merge step reads full transcripts, which re-bills every token. Pass snippets with a recall tool "
                "(`merge.recall_tool: true`) that pulls from a transcript on demand, not whole transcripts.",
                "merge.input",
            )
        if merge_input != "summaries":
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
            yield from self._shared_model(spec, judge, path)

    def _shared_model(self, spec, judge, path):
        model = judge.get("model")
        total = generator_instances(spec)
        shared = sum(instances(a) for a in generators(spec) if model and a.get("model") == model)
        if not shared or not total:
            return
        share = shared / total
        message = f"judge {judge.get('id')!r} runs {model}, the model of {shared} of {total} generator instances ({share:.0%})"
        if share >= SHARED_MODEL_WARNING_SHARE:
            yield self.warning(message + "; it shares their blind spots. Put the judge on another model or family.", path)
        else:
            yield self.info(message + ". A judge from another family avoids correlated errors entirely.", path)

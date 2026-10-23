"""Deterministic model + effort recommendation per agent role and task shape.

The table is a synthesis of the multi-agent research (what each role must
do well) and the per-model prompting guides (what each model and effort
level is good at). It is a starting point to sweep against your own evals,
never a substitute for them.
"""

from __future__ import annotations

from dataclasses import dataclass

OPUS, SONNET, HAIKU, FABLE = "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5", "claude-fable-5-1"


@dataclass(frozen=True)
class Recommendation:
    model: str
    effort: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, str]:
        return {"model": self.model, "effort": self.effort}


_COORDINATOR = Recommendation(
    OPUS,
    "medium",
    (
        "A stateless advisor spends <1% of team tokens (SLA), so the strongest reasoning is cheap here.",
        "Opus 5.5 at its default medium matches Opus 5 at high on agentic work.",
    ),
)

# (role, shape) overrides first, then role defaults. `None` shape = any shape.
_TABLE: dict[tuple[str, str | None], Recommendation] = {
    ("orchestrator", "judgment_science"): Recommendation(
        FABLE, "high", ("Ambiguous, multithreaded science work: Fable 5.1 navigates ambiguity and sustains long autonomy.",)
    ),
    ("advisor", "judgment_science"): Recommendation(
        FABLE, "high", ("Ambiguous, multithreaded science work: Fable 5.1 navigates ambiguity and sustains long autonomy.",)
    ),
    ("orchestrator", None): _COORDINATOR,
    ("advisor", None): _COORDINATOR,
    ("manager", None): _COORDINATOR,
    ("planner", None): Recommendation(
        OPUS, "high", ("Plans fix the spec every worker builds on; planner ensembles beat a single planner (LongCat).",)
    ),
    ("worker", "codebase_long"): Recommendation(
        OPUS, "medium", ("Opus 5.5 is strongest on multistep work across a large repository, in fewer steps.",)
    ),
    ("worker", "optimization"): Recommendation(
        SONNET, "high", ("Parallel workers multiply cost; Sonnet 5.5 at high suits harder, longer tasks.",)
    ),
    ("worker", "short_verifiable"): Recommendation(
        SONNET, "medium", ("Replicas need diversity more than depth; keep each one cheap and mix families.",)
    ),
    ("worker", None): Recommendation(
        SONNET, "medium", ("Sonnet 5.5 at medium for well-specified agentic work; raise to high for longer tasks.",)
    ),
    ("solver", None): Recommendation(
        HAIKU, "medium", ("Many cheap, decorrelated solvers plus a good selector beat a few expensive voters.",)
    ),
    ("researcher", None): Recommendation(
        SONNET,
        "high",
        (
            "Sonnet 5.5 guide: for researched work tell it to gather current sources rather than write from "
            "training knowledge; at low effort it can skip verification, so keep it at high.",
            "Each researcher writes its own cited section, so it needs room to verify.",
        ),
    ),
    ("editor", None): Recommendation(
        OPUS,
        "medium",
        ("The merge step introduced 84.7% of report errors in one stack; Opus 5.5 rarely mis-cites sources.",),
    ),
    ("selector", None): Recommendation(
        HAIKU, "medium", ("Evidence-grounded selection is cheap (TRACE ~1/258 of AggAgent's cost); spend on signal, not size.",)
    ),
    ("judge", None): Recommendation(
        OPUS,
        "high",
        (
            "Opus 5.5 guide: stronger review with more bugs caught and fewer false alarms, and much less likely to "
            "cite the wrong source; keep it memoryless and off the generators' model.",
        ),
    ),
    ("verifier", None): Recommendation(
        OPUS,
        "high",
        (
            "Opus 5.5 guide: stronger review with more bugs caught and fewer false alarms, and much less likely to "
            "cite the wrong source; keep it memoryless and off the generators' model.",
        ),
    ),
    ("critic", None): Recommendation(
        OPUS, "high", ("A fresh-context critic outperforms self-critique; give it effort, not memory.",)
    ),
    ("reviewer", None): Recommendation(
        OPUS, "high", ("A fresh-context reviewer outperforms self-critique; give it effort, not memory.",)
    ),
    ("router", None): Recommendation(
        HAIKU, "low", ("High-volume, short decisions over a pre-selected top-K; Haiku 5.5 low is cheapest and fastest.",)
    ),
}

_FALLBACK = Recommendation(SONNET, "medium", ("No specific guidance for this role; Sonnet 5.5 at medium is a balanced start.",))


def recommend(role: str | None, shape: str | None) -> Recommendation:
    role = (role or "").lower()
    return _TABLE.get((role, shape)) or _TABLE.get((role, None)) or _FALLBACK

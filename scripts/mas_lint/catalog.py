"""Catalog of the current Claude models and their effort/thinking contracts.

Facts come from each model's official prompting guide (bundled with the
model-prompt-writer skill). Update this file, not the rules, when a model
ships or a default changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")
HIGH_EFFORTS = frozenset({"high", "xhigh", "max"})
EXTREME_EFFORTS = frozenset({"xhigh", "max"})
THINKING_MODES = ("adaptive", "disabled", "between_tools")


@dataclass(frozen=True)
class ClaudeModel:
    id: str
    alias: str
    tier: int  # relative capability tier, 1 = lightest
    default_effort: str
    # thinking mode -> effort levels at which the API accepts it
    thinking_allowed: dict[str, frozenset[str]] = field(default_factory=dict)
    strengths: tuple[str, ...] = ()
    cautions: tuple[str, ...] = ()
    guide: str = ""
    # does the model run the reasoning_extraction safety classifier?
    reasoning_extraction_refusals: bool = True


_ALL = frozenset(EFFORT_LEVELS)
_UP_TO_HIGH = frozenset({"low", "medium", "high"})

CATALOG: dict[str, ClaudeModel] = {
    m.id: m
    for m in (
        ClaudeModel(
            id="claude-fable-5-1",
            alias="fable",
            tier=4,
            default_effort="high",
            thinking_allowed={"adaptive": _ALL},
            strengths=(
                "longest-horizon autonomy and multi-day runs",
                "dispatching and sustaining parallel subagents",
                "navigating ambiguous, multithreaded requests",
                "at low effort often beats Opus/Sonnet on cost per task",
            ),
            cautions=(
                "calls search tools less at low effort",
                "at xhigh/max may draft long deliverables in thinking first",
                "writes fewer progress updates by default",
            ),
            guide="Prompting Claude Fable 5.1",
        ),
        ClaudeModel(
            id="claude-opus-5-5",
            alias="opus",
            tier=3,
            default_effort="medium",
            thinking_allowed={"adaptive": _ALL},
            strengths=(
                "agentic coding across large repositories",
                "code review with few false alarms",
                "knowledge work with accurate figures and citations",
                "uses elapsed-time budgets to parallelize agent teams",
            ),
            cautions=(
                "thinking cannot be disabled",
                "thinks more per level than Opus 5; reserve xhigh/max",
                "text-only turns can end unattended loops early",
            ),
            guide="Prompting Claude Opus 5.5",
        ),
        ClaudeModel(
            id="claude-sonnet-5-5",
            alias="sonnet",
            tier=2,
            default_effort="high",
            thinking_allowed={"adaptive": _ALL, "between_tools": _UP_TO_HIGH},
            strengths=(
                "well-specified agentic coding and tool use at medium effort",
                "balanced cost and quality for parallel workers",
            ),
            cautions=(
                "at low effort can skip verifying a change",
                "at low/medium may check in before long tasks finish",
                "at xhigh/max starts its own review rounds and subagents",
                "the hardest long-horizon work belongs on Opus",
            ),
            guide="Prompting Claude Sonnet 5.5",
        ),
        ClaudeModel(
            id="claude-haiku-5-5",
            alias="haiku",
            tier=1,
            default_effort="medium",
            thinking_allowed={"adaptive": _ALL, "disabled": _UP_TO_HIGH},
            strengths=(
                "cheapest and fastest; chat, routing and high-volume short tasks",
                "cheap selectors and classifiers",
            ),
            cautions=(
                "at low effort in long agent prompts may skip search, stop early or skip checks",
                "may leak reasoning-like text into replies at low effort",
                "no server-side refusal fallback",
            ),
            guide="Prompting Claude Haiku 5.5",
            reasoning_extraction_refusals=False,
        ),
    )
}

_ALIASES = {m.alias: m for m in CATALOG.values()}


def resolve_model(name: object) -> ClaudeModel | None:
    """Map an id or a Claude Code alias (`opus`, `sonnet`, ...) to the catalog."""
    if not isinstance(name, str):
        return None
    key = name.strip().lower()
    return CATALOG.get(key) or _ALIASES.get(key)


def looks_like_claude(name: object) -> bool:
    return isinstance(name, str) and (name.lower().startswith("claude") or name.lower() in _ALIASES)

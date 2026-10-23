"""MOD: assign a model and an effort level to each agent deliberately.

Grounded in the per-model prompting guides (Fable 5.1, Opus 5.5, Sonnet 5.5,
Haiku 5.5): effort is the main cost/quality control, defaults differ per
model, and some thinking/effort combinations are rejected by the API.
"""

from __future__ import annotations

from ..accessors import COORDINATOR_ROLES, GENERATOR_ROLES, LONG_RUNNING_SHAPES, agent_path, agents, instances, shape
from ..catalog import EFFORT_LEVELS, EXTREME_EFFORTS, HIGH_EFFORTS, THINKING_MODES, looks_like_claude, resolve_model
from ..model_advisor import recommend
from ..reasoning import asks_for_visible_reasoning
from .base import Rule, register

MIN_MAX_TOKENS_WITH_THINKING = 32_000
PROMPT_FIELDS = ("instructions", "prompt", "system_prompt")

_LOW_EFFORT_RISK = {
    "claude-haiku-5-5": "may skip searches, stop early or skip checks in long agent prompts",
    "claude-fable-5-1": "calls search and retrieval tools less often and answers from memory",
    "claude-sonnet-5-5": "can skip verifying changes and check in before long tasks finish",
}


def _claude_agents(spec):
    for agent in agents(spec):
        if looks_like_claude(agent.get("model")):
            yield agent, resolve_model(agent.get("model"))


def _effective_effort(agent, model):
    effort = agent.get("effort")
    return effort if effort in EFFORT_LEVELS else (model.default_effort if model else None)


@register
class EffortDeclaredRule(Rule):
    id = "MAS022"
    title = "Model and effort declared per Claude agent"
    practice = "MOD"
    evidence = "Effort is the primary intelligence/latency/cost control; level names do not transfer across models (model guides)."

    def check(self, spec):
        for agent, model in _claude_agents(spec):
            effort = agent.get("effort")
            if model is None:
                yield self.info(f"{agent.get('model')!r} is not in the catalog; check its own prompting guide.", agent_path(agent, "model"))
            if effort is None:
                default = f" (default would be {model.default_effort})" if model else ""
                yield self.warning(f"Set `effort` explicitly for {agent.get('id')!r}{default}; sweep levels on your evals.", agent_path(agent, "effort"))
            elif effort not in EFFORT_LEVELS and not isinstance(effort, int):
                yield self.error(f"effort {effort!r} is not one of {', '.join(EFFORT_LEVELS)}.", agent_path(agent, "effort"))


@register
class ExtremeEffortRule(Rule):
    id = "MAS023"
    title = "xhigh/max only where measured"
    practice = "MOD"
    evidence = "Guides: reserve xhigh and max for work where you have measured a quality gain; thinking and replies get much longer."

    def check(self, spec):
        for agent, _ in _claude_agents(spec):
            if agent.get("effort") not in EXTREME_EFFORTS or agent.get("effort_justification"):
                continue
            if instances(agent) >= 3 or agent.get("role") in ("router", "selector"):
                yield self.warning(
                    f"{agent.get('id')!r} runs at {agent['effort']} across {instances(agent)} instance(s). Add "
                    "`effort_justification` with the eval gain, or drop to high.",
                    agent_path(agent, "effort"),
                )


@register
class LowEffortRiskRule(Rule):
    id = "MAS024"
    title = "Low effort on search-heavy or long agentic roles"
    practice = "MOD"
    evidence = "Haiku 5.5, Fable 5.1 and Sonnet 5.5 guides on behavior at low effort."

    def check(self, spec):
        long_running = shape(spec) in LONG_RUNNING_SHAPES
        for agent, model in _claude_agents(spec):
            if model is None or _effective_effort(agent, model) != "low" or model.id not in _LOW_EFFORT_RISK:
                continue
            role = agent.get("role")
            if role == "researcher" or (long_running and role in GENERATOR_ROLES | COORDINATOR_ROLES):
                yield self.warning(
                    f"{agent.get('id')!r}: {model.alias} at low {_LOW_EFFORT_RISK[model.id]}. Use medium or add the "
                    "guide's search/verification nudge.",
                    agent_path(agent, "effort"),
                )


@register
class ThinkingCompatibilityRule(Rule):
    id = "MAS025"
    title = "Thinking mode accepted by the model at that effort"
    practice = "MOD"
    evidence = "Opus 5.5 cannot disable thinking; Sonnet between_tools and Haiku disabled only at high or below (API 400 otherwise)."

    def check(self, spec):
        for agent, model in _claude_agents(spec):
            mode = agent.get("thinking")
            if mode is None or model is None:
                continue
            path = agent_path(agent, "thinking")
            if mode not in THINKING_MODES:
                yield self.error(f"thinking {mode!r} is not one of {', '.join(THINKING_MODES)}.", path)
            elif mode not in model.thinking_allowed:
                yield self.error(f"{model.id} does not accept thinking={mode}.", path)
            elif _effective_effort(agent, model) not in model.thinking_allowed[mode]:
                yield self.error(f"{model.id} accepts thinking={mode} only at effort high or below.", path)


@register
class VisibleReasoningRule(Rule):
    id = "MAS026"
    title = "Do not ask for reasoning in the reply"
    practice = "MOD"
    evidence = "Fable 5.1/Opus 5.5/Sonnet 5.5 may refuse with reasoning_extraction; Haiku 5.5 leaks reasoning-like text."

    def check(self, spec):
        for agent, model in _claude_agents(spec):
            texts = [agent.get(f) for f in PROMPT_FIELDS if isinstance(agent.get(f), str)]
            if not any(asks_for_visible_reasoning(t) for t in texts):
                continue
            message = (
                f"{agent.get('id')!r} asks the model to write out its reasoning. Ask for a short explanation or a "
                "summary of actions instead, or read summarized thinking blocks."
            )
            if model is None or model.reasoning_extraction_refusals:
                yield self.error(message, agent_path(agent, "instructions"))
            else:
                yield self.warning(message + " On Haiku use adaptive thinking at medium effort.", agent_path(agent, "instructions"))


@register
class MaxTokensHeadroomRule(Rule):
    id = "MAS027"
    title = "max_tokens leaves room for thinking"
    practice = "MOD"
    evidence = "Thinking counts toward max_tokens; guides suggest up to 128,000 for agentic coding."

    def check(self, spec):
        for agent, model in _claude_agents(spec):
            limit = agent.get("max_tokens")
            if isinstance(limit, int) and limit < MIN_MAX_TOKENS_WITH_THINKING and _effective_effort(agent, model) in HIGH_EFFORTS:
                yield self.warning(
                    f"{agent.get('id')!r}: max_tokens={limit} at effort high or above can cut replies off; thinking counts toward it.",
                    agent_path(agent, "max_tokens"),
                )


@register
class RoleModelFitRule(Rule):
    id = "MAS028"
    title = "Role-model fit (advisory)"
    practice = "MOD"
    evidence = "Recommendation table in model_advisor.py (research roles x model guides)."

    def check(self, spec):
        for agent, model in _claude_agents(spec):
            rec = recommend(agent.get("role"), shape(spec))
            effort = _effective_effort(agent, model)
            current = (model.id if model else agent.get("model"), effort)
            if current != (rec.model, rec.effort):
                yield self.info(
                    f"{agent.get('id')!r} ({agent.get('role')}): {current[0]}@{current[1]}; table suggests "
                    f"{rec.model}@{rec.effort}. {rec.reasons[0]}",
                    agent_path(agent),
                )

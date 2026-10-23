"""P5: bound each agent's context: prune tools, drop stale tool output."""

from __future__ import annotations

from ..accessors import LONG_RUNNING_SHAPES, agent_path, agent_tools, agents, get, shape
from .base import Rule, register

MAX_TOOLS = 12


@register
class BoundedContextRule(Rule):
    id = "MAS036"
    title = "Bounded context: prune tools, drop stale tool output"
    practice = "P5"
    evidence = (
        "KV-cache reads 82.4% of API cost; keeping all reasoning plus the latest 12 tool responses cut cost 27.7% "
        "and raised score 1.7 pts, while summarizing invalidates the cache (2610.28577); 16 of 23 tool descriptions "
        "billed every turn were never called (TokenEconomizer)."
    )

    def check(self, spec):
        for agent in agents(spec):
            tools = agent_tools(agent)
            if len(tools) > MAX_TOOLS:
                yield self.info(
                    f"{agent.get('id')!r} declares {len(tools)} tools; every description is billed each turn. Grant "
                    "the few it calls and hide the rest (`context_policy.prune_unused_tools`).",
                    agent_path(agent, "tools"),
                )
        policy = spec.get("context_policy")
        if shape(spec) in LONG_RUNNING_SHAPES and not isinstance(policy, dict):
            yield self.info(
                "Long-running work with no `context_policy`: say how many tool responses stay in context "
                "(`retained_tool_responses`, 12 tested) and that stale output is dropped, not summarized.",
                "context_policy",
            )
        if get(spec, "context_policy.stale_output") == "summarize":
            yield self.warning(
                "Summarizing stale tool output rewrites the prefix and invalidates the KV cache, the largest cost "
                "line. Drop old tool responses instead (`stale_output: drop`).",
                "context_policy.stale_output",
            )

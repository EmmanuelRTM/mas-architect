"""OPS: documented Claude Code concurrency and nesting limits."""

from __future__ import annotations

from ..accessors import get, total_instances
from .base import Rule, register

SUBAGENT_CONCURRENCY = 20  # CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS default
SUBAGENT_NESTING = 3
WORKFLOW_CONCURRENCY_MAX = 256
WORKFLOW_ADVISORY = 25
WORKFLOW_AGENTS_PER_RUN = 1000


@register
class PlatformLimitsRule(Rule):
    id = "MAS016"
    title = "Fits the runtime's limits"
    practice = "OPS"
    evidence = "Claude Code docs: 20 concurrent subagents, 3 nesting levels; workflows 16 default, 1-256, 1,000 agents/run."

    def check(self, spec):
        runtime = get(spec, "platform.runtime")
        concurrency = get(spec, "platform.max_concurrency")
        depth = get(spec, "platform.nesting_depth")
        if runtime == "claude-code-subagents":
            yield from self._subagents(spec, concurrency, depth)
        elif runtime == "claude-code-workflow":
            yield from self._workflow(spec, concurrency)

    def _subagents(self, spec, concurrency, depth):
        if isinstance(concurrency, int) and concurrency > SUBAGENT_CONCURRENCY:
            message = (
                f"{concurrency} concurrent subagents exceeds the default of {SUBAGENT_CONCURRENCY}; spawning fails "
                "past it unless CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS is raised."
            )
            if get(spec, "platform.concurrency_override") is True:
                yield self.warning(message + " Override declared: confirm the env var is set.", "platform.max_concurrency")
            else:
                yield self.error(message, "platform.max_concurrency")
        if isinstance(depth, int) and depth > SUBAGENT_NESTING:
            yield self.error(f"Subagents nest at most {SUBAGENT_NESTING} levels (got {depth}).", "platform.nesting_depth")

    def _workflow(self, spec, concurrency):
        if isinstance(concurrency, int):
            if concurrency > WORKFLOW_CONCURRENCY_MAX:
                yield self.error(f"Workflows allow 1-{WORKFLOW_CONCURRENCY_MAX} concurrent agents (got {concurrency}).", "platform.max_concurrency")
            elif concurrency > WORKFLOW_ADVISORY:
                yield self.info(
                    f"Above {WORKFLOW_ADVISORY} concurrent agents the runtime warns; most research tested 2-30 agents.",
                    "platform.max_concurrency",
                )
        if total_instances(spec) > WORKFLOW_AGENTS_PER_RUN:
            yield self.error(f"A workflow run holds at most {WORKFLOW_AGENTS_PER_RUN} agents.", "agents")

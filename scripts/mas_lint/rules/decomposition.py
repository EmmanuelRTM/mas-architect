"""P6: real decomposition, neither serial collapse nor spurious parallelism."""

from __future__ import annotations

from ..accessors import COORDINATOR_ROLES, GENERATOR_ROLES, agent_path, agents, generators, instances, tasks
from .base import Rule, register


@register
class DecompositionRule(Rule):
    id = "MAS033"
    title = "Real decomposition: no spurious parallelism, no serial collapse"
    practice = "P6"
    evidence = (
        "PARL rewards counter serial collapse (orchestrator does everything) and spurious parallelism (spawning "
        "without decomposition); progress measured in critical steps (Kimi K2.5); 16 missing-owner failures (2610.10263)."
    )

    def check(self, spec):
        work = tasks(spec)
        if not work:
            yield self.warning(
                "No `tasks`: without a decomposition every extra agent is spurious parallelism. List what each "
                "agent owns, when it starts and when it is done.",
                "tasks",
            )
            return
        owners = {t.get("owner") for t in work if isinstance(t.get("owner"), str)}
        for agent in agents(spec):
            if agent.get("id") in owners:
                continue
            if instances(agent) >= 2 or agent.get("role") in GENERATOR_ROLES:
                yield self.warning(
                    f"{agent.get('id')!r} ({instances(agent)} x {agent.get('role')}) owns no task: spawning without "
                    "a decomposition adds tokens, not progress.",
                    agent_path(agent),
                )
        roles = {a.get("id"): a.get("role") for a in agents(spec)}
        if generators(spec) and owners and all(roles.get(o) in COORDINATOR_ROLES for o in owners):
            yield self.warning(
                "Every task is owned by a coordinator while generators exist: serial collapse, the orchestrator does "
                "the work itself. Hand the tasks to the generators.",
                "tasks",
            )

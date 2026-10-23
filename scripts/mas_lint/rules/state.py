"""P4: keep state in the harness and make agents disposable."""

from __future__ import annotations

from ..accessors import COORDINATOR_ROLES, agent_path, agents, generators, get
from .base import Rule, register


@register
class StatelessCoordinatorRule(Rule):
    id = "MAS006"
    title = "Stateless coordinator, state in the harness"
    practice = "P4"
    evidence = "Stateless advisor used 0.24-0.51% of tokens vs 8.4-10.7% for a stateful manager; 84-93% fewer tokens overall (2610.07625)."

    def check(self, spec):
        for agent in agents(spec):
            if agent.get("role") in COORDINATOR_ROLES and agent.get("stateful") is True:
                yield self.warning(
                    f"Coordinator {agent.get('id')!r} is stateful: every call re-reads a growing context. Run it in a "
                    "fresh session each epoch and feed it a harness-built evidence summary.",
                    agent_path(agent, "stateful"),
                )
        if get(spec, "state.location") == "orchestrator_context":
            yield self.warning(
                "Research state lives in the orchestrator's chat. Move it to the harness (files, a ledger of "
                "candidates and scores) so any agent can be thrown away.",
                "state.location",
            )


@register
class WorkerIsolationRule(Rule):
    id = "MAS007"
    title = "Isolated generator contexts"
    practice = "P4"
    evidence = "Removing worker isolation cut kernel progress 42.8% (2610.07625); gated isolation worth 3.8 pts (ArcticSwarm)."

    def check(self, spec):
        for agent in generators(spec):
            if agent.get("context") == "shared":
                yield self.warning(
                    f"Generator {agent.get('id')!r} shares context. Give each one a fresh, isolated context showing "
                    "only its assignment and local feedback.",
                    agent_path(agent, "context"),
                )

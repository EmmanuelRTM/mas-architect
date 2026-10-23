"""P4: keep state in the harness and make agents disposable."""

from __future__ import annotations

from ..accessors import COORDINATOR_ROLES, agent_path, agents, generators, get
from .base import Rule, register

MIN_BRANCHES = 2
MIN_SESSIONS = 2


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


@register
class ResetPolicyCompleteRule(Rule):
    id = "MAS039"
    title = "Reset policy is complete"
    practice = "P4"
    evidence = (
        "Fork alone 0.57, flush alone 0.55, both 0.71 vs 0.45 (2610.07447); 100M tokens split three ways at the "
        "measured inflection beat one session by +264 Elo (2609.15309); start-many-then-prune 12 -> 5 -> 2 -> 1 (2607.18235)."
    )

    def check(self, spec):
        policy = get(spec, "state.reset_policy")
        if not isinstance(policy, dict):
            return
        kind = policy.get("type")
        path = "state.reset_policy"
        if kind == "fork_and_flush":
            branches, checkpoints = policy.get("branches"), policy.get("checkpoints")
            if not (isinstance(branches, int) and branches >= MIN_BRANCHES) or not (isinstance(checkpoints, list) and checkpoints):
                yield self.warning(
                    f"fork_and_flush needs `branches` >= {MIN_BRANCHES} and non-empty `checkpoints` (e.g. [0, 0.33, 0.66]); "
                    "forking and flushing only work together.",
                    path,
                )
        elif kind == "session_split":
            sessions, inflection = policy.get("sessions"), policy.get("inflection_tokens")
            if not (isinstance(sessions, int) and sessions >= MIN_SESSIONS) or not (isinstance(inflection, int) and inflection > 0):
                yield self.warning(
                    f"session_split needs `sessions` >= {MIN_SESSIONS} and the measured `inflection_tokens` at which "
                    "the single session stops gaining.",
                    path,
                )
        elif kind == "prune_schedule":
            schedule = policy.get("schedule")
            if not self._prunes_to_one(schedule):
                yield self.warning(
                    "prune_schedule needs a strictly decreasing `schedule` of agent counts ending in 1 (e.g. [12, 5, 2, 1]).",
                    f"{path}.schedule",
                )

    @staticmethod
    def _prunes_to_one(schedule) -> bool:
        if not isinstance(schedule, list) or not schedule or not all(isinstance(n, int) and n >= 1 for n in schedule):
            return False
        return schedule[-1] == 1 and all(a > b for a, b in zip(schedule, schedule[1:]))

"""OPS: structural validity and reference integrity."""

from __future__ import annotations

from collections import Counter

from ..accessors import SHAPES, agent_ids, agents, get, tasks
from .base import Rule, register


@register
class SchemaRule(Rule):
    id = "MAS000"
    title = "Spec structure"
    practice = "OPS"

    def check(self, spec):
        if not isinstance(spec.get("name"), str) or not spec["name"].strip():
            yield self.error("`name` must be a non-empty string.", "name")
        shape = get(spec, "task.shape")
        if shape not in SHAPES:
            yield self.error(f"`task.shape` must be one of: {', '.join(SHAPES)} (got {shape!r}).", "task.shape")
        team = agents(spec)
        if not team:
            yield self.error("`agents` must list at least one agent.", "agents")
        for index, agent in enumerate(team):
            if not isinstance(agent.get("id"), str) or not agent.get("role"):
                yield self.error("every agent needs a string `id` and a `role`.", f"agents[{index}]")
        duplicates = [i for i, n in Counter(a.get("id") for a in team).items() if n > 1 and i]
        for dup in duplicates:
            yield self.error(f"agent id {dup!r} is defined more than once.", f"agents.{dup}")


@register
class ReferenceRule(Rule):
    id = "MAS020"
    title = "References point at real agents"
    practice = "OPS"

    def check(self, spec):
        known = agent_ids(spec)
        for task in tasks(spec):
            owner = task.get("owner")
            if owner and owner not in known:
                yield self.error(f"task {task.get('id')!r} is owned by unknown agent {owner!r}.", f"tasks.{task.get('id')}.owner")
        merger = get(spec, "merge.agent")
        if merger and merger not in known:
            yield self.error(f"`merge.agent` {merger!r} is not a defined agent.", "merge.agent")
        for judge in get(spec, "verification.judge_agents", []) or []:
            if judge not in known:
                yield self.error(f"judge {judge!r} is not a defined agent.", "verification.judge_agents")

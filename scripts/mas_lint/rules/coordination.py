"""P5 bounded reads and P6 non-blocking communication with explicit ownership."""

from __future__ import annotations

import re

from ..accessors import LONG_RUNNING_SHAPES, agent_ids, agents, get, shape, task_path, tasks
from .base import Rule, register

CATALOG_THRESHOLD = 50
TOP_K_CEILING = 30
TOP_K_FLOOR = 5
TASK_FIELDS = ("owner", "start_condition", "done_criterion")
HEARTBEAT_TOKEN_BUDGET = 10_000_000
MIN_DONE_WORDS = 4
VERIFIABLE_TOKEN = re.compile(r"file|test|score|list|count|written|returned|logged|cite|record|path|json|\d", re.IGNORECASE)
HARNESS_MONITOR = "harness"


@register
class BoundedReadsRule(Rule):
    id = "MAS008"
    title = "Hard top-K on what a router reads"
    practice = "P5"
    evidence = (
        "Full catalog fails at 5,000 cards; any pre-selection cuts tokens 98.8% at 1,000 agents, SSR and BM25 "
        "statistically indistinguishable, K = 20 chosen on the test queries (2610.21113)."
    )

    def check(self, spec):
        routing = spec.get("routing")
        if not isinstance(routing, dict):
            return
        size = routing.get("catalog_size")
        top_k = routing.get("top_k")
        large = isinstance(size, int) and size > CATALOG_THRESHOLD
        if not isinstance(top_k, int):
            if large:
                yield self.error(
                    f"A router over {size} agents/tools needs `routing.top_k`: pre-select with BM25 or an index and "
                    "show the router only the top K.",
                    "routing.top_k",
                )
        elif top_k > TOP_K_CEILING:
            yield self.warning(f"top_k={top_k} still floods the router; K≈20 tested, 10-30 is the tested range.", "routing.top_k")
        elif top_k < TOP_K_FLOOR:
            yield self.info(f"top_k={top_k} may drop the right card before the router sees it; K≈20 tested.", "routing.top_k")
        if routing.get("preselection") == "none":
            yield self.warning(
                "No pre-selection: most of the gain comes from having any pre-selection step (BM25 or an index), "
                "not from which one.",
                "routing.preselection",
            )


@register
class OwnershipRule(Rule):
    id = "MAS009"
    title = "Every delegation has an owner, a start and a done criterion"
    practice = "P6"
    evidence = "Responsibility-centered coordination: 63.0 vs 44.3 (AgentVerse); 72.8 -> 46.7 without the protocol (2610.21243)."

    def check(self, spec):
        for index, task in enumerate(tasks(spec)):
            missing = [f for f in TASK_FIELDS if not task.get(f)]
            if missing:
                name = task.get("id", f"#{index}")
                yield self.error(f"task {name!r} is missing {', '.join(missing)}.", f"tasks.{name}")


@register
class NonBlockingRule(Rule):
    id = "MAS010"
    title = "Non-blocking communication"
    practice = "P6"
    evidence = "Passive awareness 62.1% vs blocking receive 51.6%, 15 wins to 2 (AgentRadio, 2607.28430)."

    def check(self, spec):
        if get(spec, "communication.mode") == "blocking":
            yield self.warning(
                "Blocking receives stall agents on the slowest peer. Use non-blocking sends with a background "
                "listener (`passive` or `non_blocking`).",
                "communication.mode",
            )


@register
class LivenessRule(Rule):
    id = "MAS011"
    title = "Heartbeats for long-running agents"
    practice = "P6"
    evidence = "Missing active monitoring was a top failure (25 cases, 2610.10263); Agent Status Protocol flags alive-but-stuck agents."

    def check(self, spec):
        heartbeat = get(spec, "monitoring.heartbeat")
        budget = get(spec, "budget.max_tokens")
        big_budget = isinstance(budget, int) and budget >= HEARTBEAT_TOKEN_BUDGET
        if (shape(spec) in LONG_RUNNING_SHAPES or big_budget) and heartbeat is not True:
            yield self.warning(
                "Long-running work needs `monitoring.heartbeat: true` so the harness can flag agents that are "
                "alive but not progressing and let a supervisor override their self-report.",
                "monitoring.heartbeat",
            )
        elif heartbeat is True and not any(isinstance(a.get("heartbeat_seconds"), int) for a in agents(spec)):
            yield self.info(
                "`monitoring.heartbeat` is on but no agent sets `heartbeat_seconds`; the harness cannot tell a "
                "missed beat from a slow one.",
                "monitoring.heartbeat",
            )


@register
class SharedMemoryRule(Rule):
    id = "MAS035"
    title = "Shared memory keeps disagreement"
    practice = "P6"
    evidence = (
        "LatticeMind claim states 0.97 vs 0.45 for debate on ConflictBank (2608.08236); ArcticSwarm 82.6 -> 78.8 "
        "without gated isolation (2609.01870)."
    )

    def check(self, spec):
        mode = get(spec, "communication.mode")
        if not isinstance(mode, str) or mode == "none":
            return
        memory_type = get(spec, "communication.memory.type")
        if memory_type != "claim_ledger":
            message = (
                f"Agents talk (`communication.mode: {mode}`) but share no claim ledger. Tag every shared claim as "
                "proposed, confirmed, contested or superseded so disagreement survives instead of being averaged away."
            )
            if memory_type == "bulletin_board" and get(spec, "communication.gated_isolation") is True:
                yield self.info(message + " A bulletin board with gated isolation keeps priors; a ledger also keeps conflicts.", "communication.memory.type")
            else:
                yield self.warning(message, "communication.memory.type")
            return
        states = get(spec, "communication.memory.claim_states") or []
        if "contested" not in states:
            yield self.warning(
                "The claim ledger has no `contested` state, so conflicting claims cannot coexist; add it to `claim_states`.",
                "communication.memory.claim_states",
            )


@register
class DoneCriteriaRule(Rule):
    id = "MAS038"
    title = "Checkable done criteria and a monitoring delegator"
    practice = "P6"
    evidence = (
        "Closure reached in 32.7% of attempts and in all three runs on 18.0% of tasks (PhysClosureBench); 86% of "
        "the best model's deficit was failed delivery (OR-License); the delegator stays responsible for monitoring "
        "and recovery (RCM 2610.21243)."
    )

    def check(self, spec):
        known = agent_ids(spec)
        long_running = shape(spec) in LONG_RUNNING_SHAPES
        for task in tasks(spec):
            done = task.get("done_criterion")
            if isinstance(done, str) and done.strip() and not self._checkable(done):
                yield self.info(
                    f"task {task.get('id')!r}: done criterion {done!r} names nothing checkable; say which file, "
                    "list, score or record exists when it is done.",
                    task_path(task, "done_criterion"),
                )
            monitor = task.get("monitor")
            if monitor is None:
                if long_running:
                    yield self.info(
                        f"task {task.get('id')!r} has no `monitor`; name the delegator (agent id or \"harness\") "
                        "that watches progress and recovers it.",
                        task_path(task, "monitor"),
                    )
            elif monitor != HARNESS_MONITOR and monitor not in known:
                yield self.error(f"task {task.get('id')!r} is monitored by unknown agent {monitor!r}.", task_path(task, "monitor"))

    @staticmethod
    def _checkable(done: str) -> bool:
        return len(done.split()) >= MIN_DONE_WORDS and VERIFIABLE_TOKEN.search(done) is not None

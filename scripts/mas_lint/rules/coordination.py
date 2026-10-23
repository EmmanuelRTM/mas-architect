"""P5 bounded reads and P6 non-blocking communication with explicit ownership."""

from __future__ import annotations

from ..accessors import LONG_RUNNING_SHAPES, get, shape, tasks
from .base import Rule, register

CATALOG_THRESHOLD = 50
TOP_K_CEILING = 50
TASK_FIELDS = ("owner", "start_condition", "done_criterion")


@register
class BoundedReadsRule(Rule):
    id = "MAS008"
    title = "Hard top-K on what a router reads"
    practice = "P5"
    evidence = "Full catalog fails at 5,000 cards; any pre-selection cuts tokens 98.8% at 1,000 agents (2610.21113)."

    def check(self, spec):
        size = get(spec, "routing.catalog_size")
        top_k = get(spec, "routing.top_k")
        if not isinstance(size, int) or size <= CATALOG_THRESHOLD:
            return
        if not isinstance(top_k, int):
            yield self.error(
                f"A router over {size} agents/tools needs `routing.top_k`: pre-select with BM25 or an index and "
                "show the router only the top K.",
                "routing.top_k",
            )
        elif top_k > TOP_K_CEILING:
            yield self.warning(f"top_k={top_k} still floods the router; 10-30 is the tested range.", "routing.top_k")


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
        if shape(spec) in LONG_RUNNING_SHAPES and get(spec, "monitoring.heartbeat") is not True:
            yield self.warning(
                "Long-running work needs `monitoring.heartbeat: true` so the harness can flag agents that are "
                "alive but not progressing and let a supervisor override their self-report.",
                "monitoring.heartbeat",
            )

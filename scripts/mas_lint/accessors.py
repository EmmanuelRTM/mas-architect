"""Read-only helpers over a spec dict, so rules never repeat lookup logic."""

from __future__ import annotations

from typing import Any, Iterator

SHAPES = (
    "short_verifiable",
    "optimization",
    "codebase_long",
    "cited_report",
    "routing",
    "expensive_eval",
    "judgment_science",
)
LONG_RUNNING_SHAPES = frozenset({"optimization", "codebase_long", "cited_report", "expensive_eval", "judgment_science"})

GENERATOR_ROLES = frozenset({"worker", "researcher", "planner", "solver"})
COORDINATOR_ROLES = frozenset({"orchestrator", "advisor", "manager"})
JUDGE_ROLES = frozenset({"judge", "verifier", "critic", "selector", "reviewer", "evaluator"})


def get(spec: Any, dotted: str, default: Any = None) -> Any:
    """`get(spec, "selection.strategy")` without KeyErrors on missing levels."""
    node = spec
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


def agents(spec: dict) -> list[dict]:
    value = spec.get("agents")
    return [a for a in value if isinstance(a, dict)] if isinstance(value, list) else []


def agent_ids(spec: dict) -> set[str]:
    return {a["id"] for a in agents(spec) if isinstance(a.get("id"), str)}


def agent_by_id(spec: dict) -> dict[str, dict]:
    return {a["id"]: a for a in agents(spec) if isinstance(a.get("id"), str)}


def instances(agent: dict) -> int:
    count = agent.get("count", 1)
    return count if isinstance(count, int) and count > 0 else 1


def generators(spec: dict) -> list[dict]:
    return [a for a in agents(spec) if a.get("role") in GENERATOR_ROLES]


def generator_instances(spec: dict) -> int:
    return sum(instances(a) for a in generators(spec))


def total_instances(spec: dict) -> int:
    return sum(instances(a) for a in agents(spec))


def tasks(spec: dict) -> list[dict]:
    value = spec.get("tasks")
    return [t for t in value if isinstance(t, dict)] if isinstance(value, list) else []


def shape(spec: dict) -> str | None:
    value = get(spec, "task.shape")
    return value if isinstance(value, str) else None


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def agent_path(agent: dict, field: str = "") -> str:
    base = f"agents.{agent.get('id', '?')}"
    return f"{base}.{field}" if field else base


def walk_strings(node: Any, path: str = "") -> Iterator[tuple[str, str]]:
    """Yield (path, value) for every string anywhere in the spec."""
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from walk_strings(value, f"{path}.{key}" if path else str(key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk_strings(value, f"{path}[{index}]")

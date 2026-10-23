"""OPS: does the architecture match the task's shape?

The table encodes the research synthesis "task shape -> architecture the
evidence favors". Adding a shape or a requirement is a data change only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..accessors import agents, get, shape
from .base import Rule, register


@dataclass(frozen=True)
class Requirement:
    path: str
    accepts: Callable[[object], bool]
    expected: str


def _one_of(*values):
    return lambda v: v in values


def _true(v):
    return v is True


def _present(v):
    return v is not None


def _at_least(n):
    return lambda v: isinstance(v, int) and v >= n


def _has_role(role):
    return Requirement(f"agents[role={role}]", lambda spec: any(a.get("role") == role for a in agents(spec)), f"an agent with role '{role}'")


SHAPE_REQUIREMENTS: dict[str, tuple[Requirement, ...]] = {
    "short_verifiable": (
        Requirement("selection.strategy", _one_of("evidence_grounded", "bias_controlled", "trained_selector", "best_of_n_metric"),
                    "an evidence-grounded, bias-controlled or trained selector"),
    ),
    "optimization": (
        Requirement("state.location", _one_of("harness"), "'harness'"),
        Requirement("state.reset_policy.type", _one_of("fork_and_flush", "session_split", "stateless_epochs"),
                    "fork_and_flush, session_split or stateless_epochs"),
        Requirement("verification.evaluator_protected", _true, "true (workers cannot edit the evaluator)"),
    ),
    "codebase_long": (
        Requirement("planning.joint_exploration", _true, "true (explore jointly before partitioning)"),
        Requirement("planning.negotiated_partition", _true, "true (agents negotiate the partition after exploring)"),
        Requirement("communication.mode", _one_of("passive", "non_blocking"), "'passive' or 'non_blocking'"),
    ),
    "cited_report": (
        Requirement("planning.fixed_spec", _true, "true (a validated ResearchSpec that stays fixed)"),
        Requirement("planning.planner_ensemble", _at_least(2), ">= 2 (several candidate specs, one judged best; LongCat)"),
        Requirement("merge.input", _one_of("raw_evidence", "snippets"), "'raw_evidence' or 'snippets'"),
        _has_role("editor"),
    ),
    "routing": (Requirement("routing.top_k", _present, "a hard top-K"),),
    "expensive_eval": (
        Requirement("verification.real_validation_before_promotion", _true, "true"),
        Requirement("verification.held_out_audit_every", _present, "an audit interval"),
    ),
    "judgment_science": (Requirement("human_in_the_loop", _true, "true (co-scientist with human taste-setting)"),),
}


@register
class ArchitectureFitRule(Rule):
    id = "MAS018"
    title = "Architecture fits the task shape"
    practice = "OPS"
    evidence = "Task shape -> architecture table of the research synthesis (Oct 2026)."

    def check(self, spec):
        task_shape = shape(spec)
        for req in SHAPE_REQUIREMENTS.get(task_shape or "", ()):
            ok = req.accepts(spec) if req.path.startswith("agents[") else req.accepts(get(spec, req.path))
            if not ok:
                yield self.warning(f"For `{task_shape}` tasks, `{req.path}` should be {req.expected}.", req.path)

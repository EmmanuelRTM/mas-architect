#!/usr/bin/env python3
"""PreToolUse (Agent|Task): every delegation should state when it is done.

Responsibility-centered coordination (arXiv 2610.21243) ties each delegation
to an owner, a start condition and a completion criterion. The subagent is
the owner and the call is the start; this hook checks the prompt carries a
done criterion. Advisory by default; MAS_ARCHITECT_SPAWN_CONTRACT=strict
denies the call, =off disables the check.
"""

from __future__ import annotations

import os
import re
import sys

from mas_lint.hookio import deny, pre_context, run, tool_input

SPAWN_TOOLS = frozenset({"Agent", "Task"})
DONE_CRITERION = re.compile(
    r"""(?ix)
    done\ when | definition\ of\ done | done\ criteri | success\ criteri | acceptance\ criteri |
    complete\ when | finished\ when | stop\ when | deliverable | output\ format | return\ (only|a|an|the|your) |
    report\ back | respond\ with |
    terminad[oa]\ cuando | listo\ cuando | criterio\ de\ (éxito|exito|aceptación|aceptacion|terminado) |
    entregable | formato\ de\ salida | devuelve | regresa\ (solo|un|una|el|la)
    """
)


def handle(event: dict) -> dict | None:
    mode = os.environ.get("MAS_ARCHITECT_SPAWN_CONTRACT", "advise").lower()
    if mode == "off" or event.get("tool_name") not in SPAWN_TOOLS:
        return None
    prompt = tool_input(event).get("prompt")
    if not isinstance(prompt, str) or DONE_CRITERION.search(prompt):
        return None
    message = (
        "mas-architect: this delegation has no done criterion. State what the subagent must return and when "
        "it is finished (e.g. 'Done when: ...', 'Return only: ...') so ownership and completion are explicit."
    )
    return deny(message) if mode == "strict" else pre_context(message)


if __name__ == "__main__":
    sys.exit(run(handle))

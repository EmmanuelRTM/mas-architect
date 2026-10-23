---
description: Design the selection, verification and monitoring of a spec (selector, judge rubric, belief probes, closure test).
argument-hint: "<path/to/spec.mas.json>"
---

Delegate the spec at $ARGUMENTS to the mas-verification-designer agent. Report the files it wrote, the spec fields it changed and its note on why the selector fits the task shape. Then run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" lint $ARGUMENTS --no-info` and confirm that no P3, P8 or P9 finding remains.

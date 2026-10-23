---
description: Show and plan the Claude model and effort level for every agent of a spec.
argument-hint: "<path/to/spec.mas.json>"
allowed-tools: Bash(python3:*)
---

Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" recommend $ARGUMENTS`. Then use the mas-model-planner agent on the same spec if any agent lacks an explicit effort or differs from the recommendation without a reason, and report the final table.

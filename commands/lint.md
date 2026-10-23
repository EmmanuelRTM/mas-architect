---
description: Lint a .mas.json multi-agent spec against the 33 evidence-based rules.
argument-hint: "<path/to/spec.mas.json>"
allowed-tools: Bash(python3:*)
---

Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" lint $ARGUMENTS` and summarize the result: errors first with the concrete fix for each, then warnings, then the practices that are not passing. Keep it under 20 lines.

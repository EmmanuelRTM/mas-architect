---
description: Generate the runnable artifacts of a lint-clean spec - agent files, selector and rubric, lead prompt or workflow.
argument-hint: "<path/to/spec.mas.json>"
---

Generate the artifacts for the spec at: $ARGUMENTS

Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" lint $ARGUMENTS --no-info` first; stop and report if it has errors. Then, in order: the mas-model-planner agent if any agent lacks an explicit effort; the mas-verification-designer agent for the selector procedure, the judge rubric skill and the monitoring protocol; the mas-prompt-writer agent once per agent that needs a prompt (give each run the spec path and one agent id); the mas-orchestration-writer agent for the lead prompt, tool lists, workflow script and budget table. Finish by running the definition check on the generated `.claude/agents/*.md` files and listing every file written.

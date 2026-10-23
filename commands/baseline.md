---
description: Plan and record the strongest single-agent baseline at matched budget before designing a team (P1).
argument-hint: "<path/to/spec.mas.json or the goal of the team>"
---

Establish the single-agent baseline for: $ARGUMENTS

Follow the mas-evaluation skill. Run or plan the strongest single agent (Opus 5.5 at medium, or Fable 5.1 at high for ambiguous multi-day work) on the same task, metric and budget the team will get, for at least 3 runs. Write `baseline.md` next to the spec with: the score per run, the metric and its ceiling, the pilot error correlation (how often two runs fail the same items) and N_eff for the planned pool (`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mas_lint_cli.py" neff N RHO`), and the stop rule: if the score is within 15% of the ceiling, say that a team is unlikely to pay. If a spec exists, record `baseline.single_agent_score`, `baseline.metric`, `baseline.max_score`, `baseline.runs` and `budget.expected_error_correlation` in it.

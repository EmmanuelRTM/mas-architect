---
description: Start designing a multi-agent system (baseline, closure criteria, task shape, pattern, models and effort, spec, review).
argument-hint: "<goal of the agent team>"
---

Design a multi-agent system for: $ARGUMENTS

Clarify the goal, metric, budget and how results are checked with the user when they are missing; otherwise state assumptions. Then delegate the design to the mas-architect agent with the goal, the constraints and the assumptions, and the done criterion "a lint-clean `.mas.json` in the current project plus the design note". When the spec is back, hand only its path to the mas-critic agent for an independent review, fold its blockers in, and offer `/mas-architect:generate` for the runnable artifacts.

# Prompt rules for agent instructions, per model

Apply when writing an agent's system prompt or a delegation prompt. Structure prompts with XML tags for role, context, instructions and output format.

## Every model

- State the role, the single deliverable, the done criterion and the output format. The `spawn-contract` hook flags delegations without a done criterion.
- Ground claims in sources: allow "I don't know", quote first for long documents, cite claim by claim where accuracy matters.
- For structured output, give a template plus one concrete example, and prefer API structured outputs. Prefill is not supported on current models.
- Scope: say what to leave out (no unrequested refactors, tests or files); report extras as follow-ups.
- Never ask the model to write out its reasoning or thinking in the reply. Ask for a short explanation of the answer or a summary of actions, or read summarized thinking blocks.

## Fable 5.1

- Autonomous runs: tell it the user is not watching in real time, to proceed on reversible steps that follow from the request, and to do stated next steps instead of announcing them.
- Agent loops: nudge it to request every independent tool call in one response.
- Prefer targeted edits over whole-file rewrites.
- Compaction: tell it exactly what a summary must preserve (decisions, constraints, open items, exact details).

## Opus 5.5

- Unattended: name the early stops you do not want (summary that announces the next step, offers to wait, non-blocking decision lists) and the ones you do (blocked on the user, risky actions).
- Teams: append elapsed time against a budget to each harness message.
- Multi-app workflows: tell it to explore relevant sources before acting.
- Chat: drop "think carefully" lines; effort controls thinking.

## Sonnet 5.5

- Long agentic tasks at `low`/`medium`: tell it to keep working until everything asked is done and checked, and to stop and report after that with no extras.
- At `xhigh`/`max`: tell it not to start extra review rounds or reviewer subagents unless asked.
- Coding at `low`: require test or build output before reporting a change as done.

## Haiku 5.5

- Give today's date with any search tool, plus a nudge to search for recent facts.
- Long agent prompts at `low`: add a keep-going instruction or use `medium`.
- Chatbots: tell it to keep to its system prompt when users argue; use `high` when adherence matters most.

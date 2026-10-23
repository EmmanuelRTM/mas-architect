# Model and effort guide (multi-agent view)

Condensed from the official prompting guides for each model (bundled in the `model-prompt-writer` skill). Where this file and a newer guide differ, the guide wins.

## Claude Fable 5.1 (`fable`, `claude-fable-5-1`)

- Default effort `high`; sweep `low`, `medium`, `xhigh`, `max`. At `medium` it roughly matches Fable 5 at lower cost; at `low` it often beats Opus/Sonnet on cost per task.
- Best at long-horizon autonomy, ambiguous multithreaded requests, dispatching and sustaining parallel subagents.
- At `low` it calls search tools less and answers from memory: raise effort for search turns or tell it that recognizing a name is not knowing its current state.
- At `xhigh`/`max` it may draft a long deliverable in thinking and again in the reply. Run long deliverables at `high`, leave `max_tokens` room, and tell it not to compose the whole output twice.
- Writes fewer progress updates by default; ask for a one-line intent and a closing recap if humans watch.
- Lead agent: let it keep working while subagents run (spawn tool returns immediately; results arrive later; a separate wait tool).
- Keep conversation history append-only; edits to earlier turns invalidate thinking blocks and the prompt cache.

## Claude Opus 5.5 (`opus`, `claude-opus-5-5`)

- Default effort `medium`, which matches or beats Opus 5 at `high` on coding and knowledge work. Thinking is always on and cannot be disabled; for low latency start at `low`.
- Best at agentic coding across large repos, code review with few false alarms, accurate figures and citations, visual inputs.
- Thinks more per level than Opus 5: reserve `xhigh`/`max` for measured gains; `max_tokens` up to 128,000 for long agentic turns.
- Unattended loops: a text-only end of turn is a report, not completion. Keep a checklist; nudge open items; stop after 2–3 automatic continuations.
- Multi-agent teams finish sooner with a time signal (`elapsed 340s / 1200s` after each harness message). A budget keeps more agents working in parallel; lowering effort reduces the work itself.
- Mark pasted text with tagged blocks so it does not follow instructions inside them.

## Claude Sonnet 5.5 (`sonnet`, `claude-sonnet-5-5`)

- API default `high`. For agentic coding and tool use start at `medium` for well-specified tasks, `high` for harder or longer ones; `low`/`medium` for chat.
- At `low` it can skip verifying a change; at `low`/`medium` it may check in before long tasks finish. At `xhigh`/`max` it starts its own review rounds and reviewer subagents; tell it not to unless asked.
- `thinking: between_tools` is the lowest thinking setting and works only at `high` or below; per-message effort changes need adaptive thinking.
- For JSON answers that need working out, use adaptive thinking at `high`/`xhigh`; treat `stop_reason: max_tokens` as failure.
- The hardest long-horizon work belongs on Opus.

## Claude Haiku 5.5 (`haiku`, `claude-haiku-5-5`)

- Default `medium`. `low` for chat, routing and high-volume short tasks; `high` for knowledge work and strict instruction following; compare against Sonnet before using `xhigh`/`max`.
- Thinking is on by default and counts toward `max_tokens` (up to 128,000). `thinking: disabled` works only at `low`/`medium`/`high`.
- At `low` in long agent prompts it may skip a search, stop early or skip checks; give it today's date and a search nudge, or use `medium`.
- May leak reasoning-like text into replies at `low`; fix with adaptive thinking at `medium`.
- No server-side refusal fallback; handle `stop_reason: refusal` in the client.

## Cross-model rules for teams

- Effort is the cost lever; lowering it cuts thinking more reliably than prompt instructions do.
- Changing top-level effort between requests invalidates the prompt cache; use per-message effort changes.
- Diversity matters more than any single model's strength in replica pools: mix Claude tiers and, where possible, other families.
- Give judges a different model from the generators, more effort, and no memory.

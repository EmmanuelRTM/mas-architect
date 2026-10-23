# Model and effort guide (multi-agent view)

Condensed from the official prompting guides for each model (bundled in the `model-prompt-writer` skill). Where this file and a newer guide differ, the guide wins. Prompt text per model is in `prompting-rules.md`.

## Claude Fable 5.1 (`fable`, `claude-fable-5-1`)

- Default effort `high`; sweep `low`, `medium`, `xhigh`, `max`. At `medium` it roughly matches Fable 5 at lower cost; at `low` it is often competitive with Opus and Sonnet on cost per task while scoring higher.
- Best at long-horizon autonomy, ambiguous multithreaded requests, dispatching and sustaining parallel subagents (Fable 5 guide; Fable 5.1 inherits it).
- At `low` it calls search tools less and answers from memory: raise effort for search turns or add the verification nudge.
- At `xhigh`/`max` it may draft a long deliverable in thinking and again in the reply. Run long deliverables at `high`, leave `max_tokens` room, and add the "don't compose twice" note.
- Writes fewer progress updates by default; progress notes arrive as `thinking` blocks that are empty unless `display: "updates"` is set.
- Lead agent: let it keep working while subagents run (spawn tool returns immediately; results arrive in a later user message; a separate wait tool). It still often chooses to wait; savings come from the runs where it carries on.
- Subagent lifetime: the Fable 5 guide says long-lived subagents that keep context across subtasks save time and cost through cache reads and avoid bottlenecking on the slowest subagent. Reconcile with P4 (disposable agents): keep a subagent alive across the steps of *one* assignment, where its cached prefix is reused, and start a fresh one for the next assignment, so no worker's context grows across epochs.
- Keep conversation history append-only; edits to earlier turns invalidate thinking blocks and the prompt cache. Per-turn nudges go in as turn-scoped system messages appended fresh each turn, never edited in place.
- Avoid showing a remaining-token countdown (Fable 5 guide): it makes the model suggest a new session or trim its work.

## Claude Opus 5.5 (`opus`, `claude-opus-5-5`)

- Default effort `medium`, which matches or beats Opus 5 at `high` on coding and knowledge work. Thinking is always on and cannot be disabled; for low latency start at `low`.
- Best at agentic coding across large repos, code review with few false alarms, accurate figures and citations, visual inputs.
- Thinks more per level than Opus 5: reserve `xhigh`/`max` for measured gains; `max_tokens` of 128,000 has worked well for long agentic turns.
- Unattended loops: a text-only end of turn is a report, not completion. Keep a checklist; nudge open items; stop after two or three automatic continuations.
- **Time budgets (Opus 5.5 only).** Opus 5.5 pays close attention to elapsed time. Have the harness append a short line at the end of each message it sends back, e.g. `elapsed 340s / 1200s`; the model paces its work to finish inside the budget and usually finishes well before it, so set the budget somewhat above the time you want and tune it on your own tasks. If no budget can be estimated, show elapsed time alone plus one system-prompt sentence ("Time matters here: do not spend time that can be avoided, and the earlier a correct result is obtained, the better."). In Anthropic's evaluations of small research teams both signals made teams finish sooner than a single agent without them, at comparable answer quality. A budget keeps more agents working in parallel; lowering effort reduces the work itself. The budget is advisory, so keep a hard timeout of your own, and check that the model does not search and verify less under pressure. This signal is documented for Opus 5.5 only: do not add countdowns on Sonnet 5.5 (injection misread) or Fable (session-ending suggestions).
- Mark pasted text with tagged blocks so it does not follow instructions inside them.
- Server-side fallback can retry safeguard declines on another model, except `reasoning_extraction` declines, which it returns to you: the harness handles those by fixing the prompt, not by retrying.

## Claude Sonnet 5.5 (`sonnet`, `claude-sonnet-5-5`)

- API default `high`. For agentic coding and tool use start at `medium` for well-specified tasks, `high` for harder or longer ones; `low`/`medium` for chat.
- At `low` it can skip verifying a change; at `low`/`medium` it may check in before long tasks finish. At `xhigh`/`max` it starts its own review rounds and reviewer subagents; tell it not to unless asked (cut session cost by about a third at `max` with no quality change).
- `thinking: between_tools` is the lowest thinking setting and works only at `high` or below; per-message effort changes need adaptive thinking.
- For agentic coding set `max_tokens` to 128,000 and stream; treat `stop_reason: max_tokens` as failure. For JSON answers that need working out, use adaptive thinking at `high`/`xhigh`.
- Mid-turn text placed right after tool results, or inside a `tool_result`, can be read as prompt injection; placement rules in `prompting-rules.md`.
- Server-side fallback retries `cyber` and `frontier_llm` declines on Sonnet 5; it does not retry `bio`, `reasoning_extraction` or `general_harms`.
- The hardest long-horizon work belongs on Opus.

## Claude Haiku 5.5 (`haiku`, `claude-haiku-5-5`)

- Default `medium`. `low` for chat, routing and high-volume short tasks; `high` for knowledge work and strict instruction following; compare against Sonnet 5.5 before using `xhigh`/`max`.
- Thinking is on by default and counts toward `max_tokens` (up to 128,000). `thinking: disabled` works only at `low`/`medium`/`high`.
- At `low` in long agent prompts it may skip a search, stop early or skip checks; give it today's date and a search nudge, or use `medium` (moving `low` → `medium` roughly halved early stopping and more than doubled output tokens).
- May leak reasoning-like text into replies at `low` or with thinking off; fix with adaptive thinking at `medium`.
- Same mid-turn placement rules as Sonnet 5.5 (`prompting-rules.md`).
- No server-side fallback; handle `stop_reason: refusal` in the client (a retry usually refuses again).

## Cross-model rules for teams

- Effort is the cost lever; lowering it cuts thinking more reliably than prompt instructions do.
- Changing top-level effort between requests invalidates the prompt cache; use per-message effort changes.
- **Mix families and tiers only in independent replica pools.** Diversity pays where agents never read each other: pairing different model families lowered error overlap (Cohen's κ) from 0.53 to 0.38 (Co-RL, 2608.17253). But never pair a strong model with a much weaker one on a task where the two must split information: a gpt-5 + gpt-4.1-nano pair scored 0.706 against 0.932 for gpt-5 alone, and coordination failure, not missing information, explained 80–86% of the gap (Collaboration Tax, 2608.22152, pairs only). For partitioned work (`codebase_long`, `cited_report` sections) keep one tier per partition and spend the diversity budget on the selector or the judge.
- Give judges a different model from the generators, more effort, and no memory.
- `reasoning_extraction` declines are never retried by server-side fallback on any model; the harness fixes the prompt (MAS026) instead of resending.

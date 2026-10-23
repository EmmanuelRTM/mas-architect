---
name: mas-patterns
description: Catalog of evidence-backed multi-agent architecture patterns (selector pool, stateless advisor + workers, fork-and-flush, negotiated partition with passive awareness, section-parallel research, retrieval router, proxy-evaluator loop, co-scientist) with when to use each, structure, failure modes and the spec fields that encode it. Use when choosing or explaining a team topology.
---

# Multi-agent patterns

Pick the pattern from the task shape, not from taste. Each entry in `references/patterns.md` gives: when it wins, the structure, the spec fields that encode it, the failure modes it guards against, and the evidence.

| Pattern | Task shape | One-line rule |
|---|---|---|
| Diverse pool + selector | `short_verifiable` | Many cheap, decorrelated samples; one evidence-grounded pick |
| Stateless advisor + isolated workers | `optimization` | Memory in the harness; advisor in a fresh session each epoch |
| Fork-and-flush | `optimization` | At 0/33/66% of budget, fork 4 branches with files kept and chat emptied |
| Negotiated partition + passive awareness | `codebase_long` | Explore together, split with named owners, listen in the background |
| Section-parallel research | `cited_report` | Fixed spec, one researcher per section, no summary handoff |
| Retrieval router | `routing` | BM25/index top-K before any LLM reads the catalog |
| Proxy evaluator loop | `expensive_eval` | Cheap proxies propose, real evaluation promotes, held-out audits gate |
| Co-scientist | `judgment_science` | Human sets taste; memoryless or blinded reviewer |

## How to use

1. Read only the section of `references/patterns.md` for the chosen pattern.
2. Start from the matching example in `${CLAUDE_PLUGIN_ROOT}/templates/examples/` when one exists.
3. Check the pattern's failure modes against the plan before writing the spec.
4. Patterns compose: a section-parallel report can use a diverse pool + selector inside each section. Keep each composition explicit in `tasks` with owners.

## Anti-patterns to name when you see them

- **Full-solution broadcast:** peers read each other's solutions during exploration; diversity collapses within a round.
- **Summarizing orchestrator:** the merge step reads notes instead of evidence; citations break there.
- **Stateful manager:** one coordinator re-reads its whole history every call; it dominates token cost and locks in early ideas.
- **Vote over a big pool:** plurality captures little of the pool's coverage.
- **Spurious parallelism:** spawning agents without a real decomposition; **serial collapse:** the orchestrator does everything itself.
- **Self-grading:** the generator, or a copy sharing its context, judges its own output.

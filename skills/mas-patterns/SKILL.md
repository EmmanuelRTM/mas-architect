---
name: mas-patterns
description: Catalog of evidence-backed multi-agent architecture patterns (selector pool, stateless advisor + workers, fork-and-flush, negotiated partition with passive awareness, section-parallel research, batch-grown task graph, retrieval router, proxy-evaluator loop, co-scientist) with when to use each, structure, failure modes and the spec fields that encode it. Use when choosing or explaining a team topology.
---

# Multi-agent patterns

Pick the pattern from the task shape, not from taste. Each entry in `references/patterns.md` gives: when it wins, the structure, the spec fields that encode it, the failure modes it guards against, and the evidence. The architecture-per-shape table with its evidence is in `mas-design/references/task-shape-matrix.md`; this table is the only shape → pattern map.

| Pattern | Task shape | One-line rule |
|---|---|---|
| Diverse pool + selector | `short_verifiable` | Many cheap, decorrelated samples; one evidence-grounded pick |
| Stateless advisor + isolated workers | `optimization` | Memory in the harness; advisor in a fresh session each epoch |
| Fork-and-flush | `optimization` | Fork branches with files kept and chat emptied on a fixed schedule |
| Negotiated partition + passive awareness | `codebase_long` | Explore together, split with named owners, listen in the background |
| Section-parallel research | `cited_report` | Fixed spec, one researcher per section, no summary handoff |
| Batch-grown task graph | `cited_report` (deep search) | Grow the graph in batches, retry uncertain nodes, compact handoff plus a recall tool |
| Retrieval router | `routing` | BM25/index top-K before any LLM reads the catalog |
| Proxy evaluator loop | `expensive_eval` | Cheap proxies propose, real evaluation promotes, held-out audits gate |
| Co-scientist | `judgment_science` | Human sets taste; memoryless or blinded reviewer |

Two kinds of parallelism cut across the table and go in `task.parallelism`: *replica* parallelism runs several complete solution paths (the pool, forks, repeated sessions) and *structural* parallelism runs concurrent parts of one path (sections, partitions, graph nodes). TIPEX found them complementary, most useful at intermediate difficulty and costly in tokens (2608.05791), so declare which one a design buys and budget for it.

## How to use

1. Read only the section of `references/patterns.md` for the chosen pattern.
2. Start from the matching example in `${CLAUDE_PLUGIN_ROOT}/templates/examples/` when one exists.
3. Check the pattern's failure modes against the plan before writing the spec.
4. Patterns compose: a section-parallel report can use a diverse pool + selector inside each section. Keep each composition explicit in `tasks` with owners and monitors.
5. Apply the cross-cutting memory rules at the end of `references/patterns.md` whenever agents talk.

## Anti-patterns to name when you see them

- **Full-solution broadcast:** peers read each other's solutions during exploration; diversity collapses within a round.
- **Critique on a graded objective:** review rounds on an executable score make most runs worse.
- **Summarizing orchestrator:** the merge step reads notes instead of evidence; citations break there.
- **Stateful manager:** one coordinator re-reads its whole history every call; it dominates token cost and locks in early ideas.
- **Vote over a big pool:** plurality captures little of the pool's coverage.
- **Spurious parallelism:** spawning agents without a real decomposition; **serial collapse:** the orchestrator does everything itself.
- **Self-grading:** the generator, or a copy sharing its context, judges its own output.
- **Split budget:** a team paid for by dividing one agent's budget.

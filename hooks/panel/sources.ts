// Owns the panel's session state: reads live data through `$` and writes it
// only when it changed, so the pane redraws exactly when something is new.
import { atom, read, update } from 'claude-code'
import type { EngineInterface, ModelUsage } from 'claude-code'

import type { AgentRow, AgentUsageMap, LastSeen, ReportView, UsageView, WorkflowRunning } from '../../types'
import { markSeen, pruneSeen } from './liveness'
import { parseReport, sameValue, toAgentRows } from './model'
import { MAIN_LOOP, addTurnUsage, noteToolResult, pruneUsage } from './usage'

// Change a shape tag when its value's fields change: an old value outlives a
// reload and is then read as the initial value.
const agentsAtom = atom({ plugin: 'mas-architect', key: 'agents' } as const, [], { shape: 'agents-2' })
const reportAtom = atom({ plugin: 'mas-architect', key: 'report' } as const, null, { shape: 'report-2' })
const usageAtom = atom({ plugin: 'mas-architect', key: 'usage' } as const, null, { shape: 'usage-1' })
const lastSeenAtom = atom({ plugin: 'mas-architect', key: 'lastSeen' } as const, {}, { shape: 'lastSeen-1' })
const agentUsageAtom = atom({ plugin: 'mas-architect', key: 'agentUsage' } as const, {}, { shape: 'agentUsage-1' })
const workflowAtom = atom({ plugin: 'mas-architect', key: 'workflow' } as const, [], { shape: 'workflow-1' })
const clockAtom = atom({ plugin: 'mas-architect', key: 'clockMs' } as const, 0, { shape: 'clockMs-1' })

export type PanelState = {
  agents: AgentRow[]
  report: ReportView | null
  usage: UsageView | null
  lastSeen: LastSeen
  agentUsage: AgentUsageMap
  workflow: WorkflowRunning
  /** The last poll's time: read so a tick redraws the ages; `now` itself is fresh at draw time. */
  tick: number
}

export type RefreshSelector = { agents?: boolean; report?: boolean; usage?: boolean }

/** Read while drawing: subscribes the pane to every value. */
export async function readPanelState($: EngineInterface): Promise<PanelState> {
  const [agents, report, usage, lastSeen, agentUsage, workflow, tick] = await Promise.all([
    read($, agentsAtom),
    read($, reportAtom),
    read($, usageAtom),
    read($, lastSeenAtom),
    read($, agentUsageAtom),
    read($, workflowAtom),
    read($, clockAtom),
  ])
  return { agents, report, usage, lastSeen, agentUsage, workflow, tick }
}

// One slot per atom, each spelling `read`/`update` with its const atom so the
// engine's scan sees every state key the module touches.
type Slot<T> = { get: () => Promise<T>; patch: (fn: (before: T) => T) => Promise<unknown> }

function slots($: EngineInterface) {
  return {
    agents: { get: () => read($, agentsAtom), patch: (fn: (b: AgentRow[]) => AgentRow[]) => update($, agentsAtom, fn) },
    report: { get: () => read($, reportAtom), patch: (fn: (b: ReportView | null) => ReportView | null) => update($, reportAtom, fn) },
    usage: { get: () => read($, usageAtom), patch: (fn: (b: UsageView | null) => UsageView | null) => update($, usageAtom, fn) },
    lastSeen: { get: () => read($, lastSeenAtom), patch: (fn: (b: LastSeen) => LastSeen) => update($, lastSeenAtom, fn) },
    agentUsage: { get: () => read($, agentUsageAtom), patch: (fn: (b: AgentUsageMap) => AgentUsageMap) => update($, agentUsageAtom, fn) },
    workflow: { get: () => read($, workflowAtom), patch: (fn: (b: WorkflowRunning) => WorkflowRunning) => update($, workflowAtom, fn) },
    clock: { get: () => read($, clockAtom), patch: (fn: (b: number) => number) => update($, clockAtom, fn) },
  }
}

/** Apply `fn` and write only when the value differs, so readers redraw on real change.
 *  `update` re-reads and re-applies `fn` on a version miss, so concurrent writers never lose an update. */
async function patchAtom<T>(slot: Slot<T>, fn: (before: T) => T): Promise<void> {
  const before = await slot.get()
  if (sameValue(before, fn(before))) return
  await slot.patch(fn)
}

/** Replace with a fresh snapshot (last writer wins) when it differs. */
async function syncAtom<T>(slot: Slot<T>, value: T): Promise<void> {
  await patchAtom(slot, () => value)
}

async function readAgents($: EngineInterface): Promise<AgentRow[] | null> {
  return $.agent.list().then(toAgentRows).catch(() => null)
}

async function readReport($: EngineInterface, path: string): Promise<ReportView | null> {
  return $.fs
    .read(path)
    .then(text => (typeof text === 'string' ? parseReport(text) : null))
    .catch(() => null)
}

async function readUsage($: EngineInterface): Promise<UsageView | null> {
  return $.session
    .usage()
    .then(usage => ({ costUsd: usage.cost?.usd ?? null, contextPercent: usage.context.percent ?? null }))
    .catch(() => null)
}

const ALL: RefreshSelector = { agents: true, report: true, usage: true }

/** Pull the selected sources (all when none named) and store what changed. */
export async function refresh($: EngineInterface, reportPath: string, which: RefreshSelector = ALL): Promise<void> {
  const state = slots($)
  const [agents, report, usage] = await Promise.all([
    which.agents ? readAgents($) : null,
    which.report ? readReport($, reportPath) : undefined,
    which.usage ? readUsage($) : null,
  ])
  if (agents !== null) {
    await syncAtom(state.agents, agents)
    const ids = agents.map(row => row.id)
    await patchAtom(state.lastSeen, seen => pruneSeen(seen, ids))
    await patchAtom(state.agentUsage, map => pruneUsage(map, ids))
    await syncAtom(state.clock, await $.clock.now())
  }
  if (report !== undefined) await syncAtom(state.report, report)
  if (usage !== null) await syncAtom(state.usage, usage)
}

/** An agent's loop showed life now (a turn, a tool call, its spawn). */
export async function touchAgent($: EngineInterface, agentId: string | undefined): Promise<void> {
  if (agentId === undefined) return
  const now = await $.clock.now()
  await patchAtom(slots($).lastSeen, seen => markSeen(seen, agentId, now))
}

export async function recordTurnUsage($: EngineInterface, agentId: string | undefined, usage: ModelUsage | undefined): Promise<void> {
  if (usage === undefined) return
  await patchAtom(slots($).agentUsage, map => addTurnUsage(map, agentId ?? MAIN_LOOP, usage))
}

export async function recordToolResult($: EngineInterface, agentId: string | undefined, isError: boolean): Promise<void> {
  await patchAtom(slots($).agentUsage, map => noteToolResult(map, agentId ?? MAIN_LOOP, isError))
}

/** A workflow agent started (`e.workflow` on its spawn) or ended (its `turn.complete`). */
export async function trackWorkflowAgent($: EngineInterface, agentId: string, running: boolean): Promise<void> {
  await patchAtom(slots($).workflow, before =>
    running ? (before.includes(agentId) ? before : [...before, agentId]) : before.filter(id => id !== agentId),
  )
}

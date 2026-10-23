// Owns the panel's session state: reads live data through `$` and writes it
// only when it changed, so the pane redraws exactly when something is new.
import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { AgentRow, ReportView, UsageView } from '../../types'
import { parseReport, sameValue, toAgentRows } from './model'

// Change a shape tag when its value's fields change: an old value outlives a
// reload and is then read as the initial value.
const agentsAtom = atom({ plugin: 'mas-architect', key: 'agents' } as const, [], { shape: 'agents-1' })
const reportAtom = atom({ plugin: 'mas-architect', key: 'report' } as const, null, { shape: 'report-1' })
const usageAtom = atom({ plugin: 'mas-architect', key: 'usage' } as const, null, { shape: 'usage-1' })

export type PanelState = { agents: AgentRow[]; report: ReportView | null; usage: UsageView | null }

/** Read while drawing: subscribes the pane to all three values. */
export async function readPanelState($: EngineInterface): Promise<PanelState> {
  const [agents, report, usage] = await Promise.all([read($, agentsAtom), read($, reportAtom), read($, usageAtom)])
  return { agents, report, usage }
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

export async function refresh($: EngineInterface, reportPath: string): Promise<void> {
  const [agents, report, usage] = await Promise.all([readAgents($), readReport($, reportPath), readUsage($)])
  if (agents !== null && !sameValue(await read($, agentsAtom), agents)) {
    await update($, agentsAtom, () => agents)
  }
  if (!sameValue(await read($, reportAtom), report)) {
    await update($, reportAtom, () => report)
  }
  if (usage !== null && !sameValue(await read($, usageAtom), usage)) {
    await update($, usageAtom, () => usage)
  }
}

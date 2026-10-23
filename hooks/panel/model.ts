// Pure data shaping for the control panel: no `$`, so it is trivially testable.
import type { AgentInfo, AgentStatus } from 'claude-code'

import type { AgentRow, FindingRow, MonitoringView, PanelAgentStatus, PlanRow, ReportView } from '../../types'

// The contract mirrors the engine's union; a drift in either direction fails here.
type SameStatus<A, B> = [A] extends [B] ? ([B] extends [A] ? true : never) : never
const STATUS_UNIONS_AGREE: SameStatus<PanelAgentStatus, AgentStatus> = true
void STATUS_UNIONS_AGREE

export const PRACTICE_LABELS: Record<string, string> = {
  P1: 'Baseline',
  P2: 'Diversity',
  P3: 'Selection',
  P4: 'State in harness',
  P5: 'Bounded reads',
  P6: 'Ownership',
  P7: 'Raw-evidence merge',
  P8: 'Independent judge',
  P9: 'Monitoring',
  P10: 'Team credit',
  MOD: 'Model & effort',
  OPS: 'Limits & schema',
}

const ACTIVE = new Set<PanelAgentStatus>(['pending', 'running'])
const WAITING = new Set<PanelAgentStatus>(['waiting', 'idle'])
const FAILED = new Set<PanelAgentStatus>(['failed', 'killed'])
export const MAX_AGENT_ROWS = 50

export type AgentCounts = { active: number; waiting: number; done: number; failed: number }

/** Depth of each agent from its `parentId` chain: 1 for a child of the main loop. */
export function agentDepths(list: readonly Pick<AgentInfo, 'id' | 'parentId'>[]): Map<string, number> {
  const parents = new Map(list.map(agent => [agent.id, agent.parentId ?? null]))
  const depths = new Map<string, number>()
  const depthOf = (id: string, trail: Set<string>): number => {
    const known = depths.get(id)
    if (known !== undefined) return known
    const parent = parents.get(id) ?? null
    // A parent the list no longer names counts as one level; a cycle stops.
    const depth = parent === null ? 1 : trail.has(parent) ? 1 : parents.has(parent) ? depthOf(parent, new Set(trail).add(id)) + 1 : 2
    depths.set(id, depth)
    return depth
  }
  for (const agent of list) depthOf(agent.id, new Set())
  return depths
}

export function toAgentRows(list: readonly AgentInfo[]): AgentRow[] {
  const depths = agentDepths(list)
  const rows: AgentRow[] = list.map(agent => ({
    id: agent.id,
    description: agent.description,
    type: agent.type,
    status: agent.status,
    depth: depths.get(agent.id) ?? 1,
    parentId: agent.parentId ?? null,
  }))
  const rank = (row: AgentRow) => (ACTIVE.has(row.status) ? 0 : WAITING.has(row.status) ? 1 : 2)
  return rows.sort((a, b) => rank(a) - rank(b)).slice(0, MAX_AGENT_ROWS)
}

export function isActive(status: PanelAgentStatus): boolean {
  return ACTIVE.has(status)
}

export function countAgents(rows: readonly AgentRow[]): AgentCounts {
  const counts: AgentCounts = { active: 0, waiting: 0, done: 0, failed: 0 }
  for (const row of rows) {
    if (ACTIVE.has(row.status)) counts.active += 1
    else if (WAITING.has(row.status)) counts.waiting += 1
    else if (FAILED.has(row.status)) counts.failed += 1
    else counts.done += 1
  }
  return counts
}

/** Deepest nesting among rows still active; 0 with none. */
export function maxActiveDepth(rows: readonly AgentRow[]): number {
  return rows.reduce((deepest, row) => (ACTIVE.has(row.status) ? Math.max(deepest, row.depth) : deepest), 0)
}

export function concurrencyBar(active: number, limit: number, width = 16): string {
  const safeLimit = Math.max(1, limit)
  const filled = Math.min(width, Math.round((active / safeLimit) * width))
  return `${'█'.repeat(filled)}${'░'.repeat(width - filled)} ${active}/${safeLimit}`
}

export type Level = 'ok' | 'high' | 'over'

export function concurrencyLevel(active: number, limit: number): Level {
  if (active > limit) return 'over'
  return active >= limit * 0.8 ? 'high' : 'ok'
}

/** Depth is a hard platform limit: at the limit is already `over`. */
export function depthLevel(depth: number, limit: number): Level {
  if (depth >= limit) return 'over'
  return depth >= limit - 1 ? 'high' : 'ok'
}

export function statusGlyph(status: string): string {
  return { pass: '✓', warn: '!', fail: '✗', 'n/a': '·' }[status] ?? '?'
}

export function truncate(text: string, width: number): string {
  if (width <= 1) return ''
  return text.length <= width ? text : `${text.slice(0, width - 1)}…`
}

const asNumber = (value: unknown): number | null => (typeof value === 'number' && Number.isFinite(value) ? value : null)
const asString = (value: unknown, fallback = ''): string => (typeof value === 'string' ? value : fallback)
const asFlag = (value: unknown): boolean | null => (typeof value === 'boolean' ? value : null)
const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value)

function shortModel(model: string): string {
  return model.replace(/^claude-/, '')
}

function toPlanRow(raw: unknown): PlanRow | null {
  if (!isRecord(raw)) return null
  const rec = isRecord(raw.recommended) ? raw.recommended : {}
  const model = shortModel(asString(raw.model, '?'))
  const effort = asString(raw.effort, '-')
  const recommended = `${shortModel(asString(rec.model, '?'))}@${asString(rec.effort, '?')}`
  return {
    id: asString(raw.id, '?'),
    role: asString(raw.role, '?'),
    count: asNumber(raw.count) ?? 1,
    model,
    effort,
    recommended,
    matches: `${model}@${effort}` === recommended,
    skills: Array.isArray(raw.skills) ? raw.skills.length : null,
  }
}

/** `· 2 skills`, `· 1 skill`, or `· skills?` when undeclared. */
export function skillsLabel(skills: number | null): string {
  if (skills === null) return ' · skills?'
  return ` · ${skills} skill${skills === 1 ? '' : 's'}`
}

function toFindingRow(raw: unknown): FindingRow | null {
  if (!isRecord(raw)) return null
  return { ruleId: asString(raw.rule_id, '?'), severity: asString(raw.severity, 'info'), message: asString(raw.message) }
}

function toMonitoring(raw: unknown): MonitoringView | null {
  if (!isRecord(raw)) return null
  return {
    repeatedRuns: asFlag(raw.repeated_runs),
    beliefProbes: asFlag(raw.belief_probes),
    heartbeat: asFlag(raw.heartbeat),
    commitmentLog: asFlag(raw.commitment_log),
  }
}

/** Parse the JSON report the lint hook writes; anything malformed is `null`. */
export function parseReport(text: string): ReportView | null {
  let data: unknown
  try {
    data = JSON.parse(text)
  } catch {
    return null
  }
  if (!isRecord(data) || !isRecord(data.summary)) return null
  const practices = isRecord(data.practices) ? data.practices : {}
  const metrics = isRecord(data.metrics) ? data.metrics : {}
  const findings = Array.isArray(data.findings) ? data.findings : []
  const agents = Array.isArray(data.agents) ? data.agents : []
  return {
    spec: asString(data.spec, 'unnamed'),
    errors: asNumber(data.summary.error) ?? 0,
    warnings: asNumber(data.summary.warning) ?? 0,
    info: asNumber(data.summary.info) ?? 0,
    practices: Object.entries(practices).map(([id, status]) => ({ id, status: asString(status, '?') })),
    plan: agents.map(toPlanRow).filter((row): row is PlanRow => row !== null),
    findings: findings
      .map(toFindingRow)
      .filter((row): row is FindingRow => row !== null && row.severity !== 'info'),
    effectiveTeamSize: asNumber(metrics.effective_team_size),
    replicas: asNumber(metrics.candidates) ?? asNumber(metrics.generator_instances),
    errorCorrelation: asNumber(metrics.error_correlation),
    saturationSize: asNumber(metrics.saturation_size),
    monitoring: toMonitoring(data.monitoring),
  }
}

export function sameValue(a: unknown, b: unknown): boolean {
  return JSON.stringify(a) === JSON.stringify(b)
}

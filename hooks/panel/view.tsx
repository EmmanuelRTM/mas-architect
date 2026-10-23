// Draws the control panel from plain data. Every surface's element table has
// Box and Text, so one tree serves terminal, desktop, vscode and mobile.
import type { Elements, RenderSurface } from 'claude-code'

import type { AgentRow, MonitoringView, ReportView, UsageView } from '../../types'
import type { PanelConfig } from './config'
import { ageMs, formatAge, isStalled } from './liveness'
import {
  PRACTICE_LABELS,
  concurrencyBar,
  concurrencyLevel,
  countAgents,
  depthLevel,
  isActive,
  maxActiveDepth,
  skillsLabel,
  statusGlyph,
  truncate,
} from './model'
import type { Level } from './model'
import type { PanelState } from './sources'
import { WORKFLOW_ADVISORY_TOKENS, errorBadge, formatTokens, sessionTokens, usageLabel } from './usage'

type El = Pick<Elements[RenderSurface], 'Box' | 'Text'>

export type PanelData = PanelState & { config: PanelConfig; columns: number; rows: number; now: number }

const STATUS_COLOR: Record<string, string> = { pass: 'success', warn: 'warning', fail: 'error', 'n/a': 'inactive' }
const LEVEL_COLOR: Record<Level, string> = { ok: 'success', high: 'warning', over: 'error' }

/** Rows each section takes besides the agent list, so the list gets what is left. */
const ROWS = { agentsHeader: 5, usage: 1, report: 9, plan: 4, findings: 6 } as const
const ROWS_AROUND_AGENT_LIST = ROWS.agentsHeader + ROWS.usage + ROWS.report + ROWS.plan + ROWS.findings
const MIN_AGENT_LIST_ROWS = 1
const MAX_AGENT_LIST_ROWS = 12

export function agentListRoom(bodyRows: number): number {
  return Math.max(MIN_AGENT_LIST_ROWS, Math.min(MAX_AGENT_LIST_ROWS, bodyRows - ROWS_AROUND_AGENT_LIST))
}

function agentLine(agent: AgentRow, data: PanelData): { text: string; level: Level | null } {
  const active = isActive(agent.status)
  const age = active ? ageMs(data.lastSeen, agent.id, data.now) : null
  const stalled = active && isStalled(age, data.config.staleAfterSeconds)
  const usage = data.agentUsage[agent.id]
  const badge = errorBadge(usage)
  const indent = '  '.repeat(Math.max(0, agent.depth - 1))
  const glyph = stalled ? '?' : agent.status === 'running' ? '▶' : '·'
  const seen = age === null ? '' : ` · ${formatAge(age)}${stalled ? ' stalled?' : ''}`
  const text = `${indent}${glyph} ${agent.type}: ${agent.description}${seen}${usageLabel(usage)}${badge}`
  return { text, level: stalled || badge !== '' ? 'over' : null }
}

function AgentsSection({ Box, Text }: El, data: PanelData) {
  const counts = countAgents(data.agents)
  const depth = maxActiveDepth(data.agents)
  const workflows = data.workflow.length
  const { maxConcurrentSubagents: limit, maxNestingDepth, maxConcurrentWorkflowAgents } = data.config
  return (
    <Box flexDirection="column">
      <Text bold>Agents</Text>
      <Text color={LEVEL_COLOR[concurrencyLevel(counts.active, limit)]}>{concurrencyBar(counts.active, limit)}</Text>
      {workflows > 0 && (
        <Text color={LEVEL_COLOR[concurrencyLevel(workflows, maxConcurrentWorkflowAgents)]}>
          {`${concurrencyBar(workflows, maxConcurrentWorkflowAgents)} workflow`}
        </Text>
      )}
      <Text dimColor>
        {`active ${counts.active} · waiting ${counts.waiting} · done ${counts.done} · failed ${counts.failed}`}
      </Text>
      <Text color={depth === 0 ? undefined : LEVEL_COLOR[depthLevel(depth, maxNestingDepth)]} dimColor={depth === 0}>
        {`nesting ${depth}/${maxNestingDepth} · stale after ${data.config.staleAfterSeconds}s`}
      </Text>
      {data.agents.length === 0 && <Text dimColor>No subagents yet this session.</Text>}
      {data.agents.slice(0, agentListRoom(data.rows)).map(agent => {
        const line = agentLine(agent, data)
        return (
          <Text color={line.level === null ? undefined : LEVEL_COLOR[line.level]} dimColor={agent.status === 'completed'}>
            {truncate(line.text, data.columns)}
          </Text>
        )
      })}
    </Box>
  )
}

function UsageSection({ Text }: El, usage: UsageView | null, data: PanelData) {
  const spent = sessionTokens(data.agentUsage)
  const tokens = `spent ${formatTokens(spent)} of ${formatTokens(WORKFLOW_ADVISORY_TOKENS)} tok (advisory)`
  if (usage === null) return <Text dimColor>{truncate(`Session: ${tokens}`, data.columns)}</Text>
  const cost = usage.costUsd === null ? 'cost n/a' : `cost $${usage.costUsd.toFixed(2)}`
  const context = usage.contextPercent === null ? 'context n/a' : `context ${usage.contextPercent}%`
  return (
    <Text dimColor color={spent >= WORKFLOW_ADVISORY_TOKENS ? 'warning' : undefined}>
      {truncate(`Session: ${cost} · ${context} · ${tokens}`, data.columns)}
    </Text>
  )
}

function neffLine(report: ReportView): string {
  if (report.effectiveTeamSize === null) return ''
  const rho = report.errorCorrelation === null ? '' : ` · ρ ${report.errorCorrelation}`
  const saturation = report.saturationSize === null ? '' : ` · saturates at ${report.saturationSize}`
  return `N_eff ${report.effectiveTeamSize}/${report.replicas ?? '?'} (spec estimate${rho}${saturation})`
}

const flag = (value: boolean | null) => (value === null ? '·' : value ? '✓' : '✗')

function monitoringLine(monitoring: MonitoringView): string {
  return (
    `P9 ${flag(monitoring.repeatedRuns)} repeated runs · ${flag(monitoring.beliefProbes)} belief probes · ` +
    `${flag(monitoring.heartbeat)} heartbeat · ${flag(monitoring.commitmentLog)} commitment log`
  )
}

function ReportSection({ Box, Text }: El, report: ReportView | null, columns: number) {
  if (report === null) {
    return (
      <Box flexDirection="column" marginTop={1}>
        <Text bold>Spec health</Text>
        <Text dimColor>No lint report yet. Write or edit a *.mas.json spec to create one.</Text>
      </Box>
    )
  }
  const color = report.errors > 0 ? 'error' : report.warnings > 0 ? 'warning' : 'success'
  const neff = neffLine(report)
  return (
    <Box flexDirection="column" marginTop={1}>
      <Text bold>{truncate(`Spec health: ${report.spec}`, columns)}</Text>
      <Text color={color}>{`${report.errors} errors · ${report.warnings} warnings · ${report.info} info`}</Text>
      {neff !== '' && <Text dimColor>{truncate(neff, columns)}</Text>}
      {report.monitoring !== null && <Text dimColor>{truncate(monitoringLine(report.monitoring), columns)}</Text>}
      {report.practices.map(p => (
        <Text color={STATUS_COLOR[p.status]}>{`${statusGlyph(p.status)} ${p.id.padEnd(4)}${PRACTICE_LABELS[p.id] ?? ''}`}</Text>
      ))}
    </Box>
  )
}

function PlanSection({ Box, Text }: El, report: ReportView | null, columns: number) {
  if (report === null || report.plan.length === 0) return null
  return (
    <Box flexDirection="column" marginTop={1}>
      <Text bold>Model plan (model@effort · skills)</Text>
      {report.plan.map(row => (
        <Text color={row.matches ? undefined : 'warning'}>
          {truncate(
            `${row.matches ? '✓' : '≠'} ${row.id} (${row.role}×${row.count}) ${row.model}@${row.effort}${skillsLabel(row.skills)}` +
              (row.matches ? '' : ` → ${row.recommended}`),
            columns,
          )}
        </Text>
      ))}
    </Box>
  )
}

function FindingsSection({ Box, Text }: El, report: ReportView | null, columns: number) {
  if (report === null || report.findings.length === 0) return null
  return (
    <Box flexDirection="column" marginTop={1}>
      <Text bold>Top findings</Text>
      {report.findings.slice(0, 5).map(f => (
        <Text color={f.severity === 'error' ? 'error' : 'warning'}>{truncate(`${f.ruleId} ${f.message}`, columns)}</Text>
      ))}
    </Box>
  )
}

export function renderPanel(el: El, data: PanelData) {
  const { Box } = el
  return (
    <Box flexDirection="column">
      {AgentsSection(el, data)}
      {UsageSection(el, data.usage, data)}
      {ReportSection(el, data.report, data.columns)}
      {PlanSection(el, data.report, data.columns)}
      {FindingsSection(el, data.report, data.columns)}
    </Box>
  )
}

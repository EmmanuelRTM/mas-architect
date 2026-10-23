// Draws the control panel from plain data. Every surface's element table has
// Box and Text, so one tree serves terminal, desktop, vscode and mobile.
import type { Elements, RenderSurface } from 'claude-code'

import type { AgentRow, ReportView, UsageView } from '../../types'
import {
  PRACTICE_LABELS,
  concurrencyBar,
  concurrencyLevel,
  countAgents,
  skillsLabel,
  statusGlyph,
  truncate,
} from './model'

type El = Pick<Elements[RenderSurface], 'Box' | 'Text'>

export type PanelData = {
  agents: AgentRow[]
  report: ReportView | null
  usage: UsageView | null
  limit: number
  columns: number
  rows: number
}

const STATUS_COLOR: Record<string, string> = { pass: 'success', warn: 'warning', fail: 'error', 'n/a': 'inactive' }
const LEVEL_COLOR = { ok: 'success', high: 'warning', over: 'error' } as const

function AgentsSection({ Box, Text }: El, data: PanelData) {
  const counts = countAgents(data.agents)
  const room = Math.max(1, Math.min(8, data.rows - 22))
  return (
    <Box flexDirection="column">
      <Text bold>Agents</Text>
      <Text color={LEVEL_COLOR[concurrencyLevel(counts.active, data.limit)]}>
        {concurrencyBar(counts.active, data.limit)}
      </Text>
      <Text dimColor>
        {`active ${counts.active} · waiting ${counts.waiting} · done ${counts.done} · failed ${counts.failed}`}
      </Text>
      {data.agents.length === 0 && <Text dimColor>No subagents yet this session.</Text>}
      {data.agents.slice(0, room).map(agent => (
        <Text dimColor={agent.status === 'completed'}>
          {truncate(`${agent.status === 'running' ? '▶' : '·'} ${agent.type}: ${agent.description}`, data.columns)}
        </Text>
      ))}
    </Box>
  )
}

function UsageSection({ Text }: El, usage: UsageView | null) {
  if (usage === null) return null
  const cost = usage.costUsd === null ? 'cost n/a' : `cost $${usage.costUsd.toFixed(2)}`
  const context = usage.contextPercent === null ? 'context n/a' : `context ${usage.contextPercent}%`
  return <Text dimColor>{`Session: ${cost} · ${context}`}</Text>
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
  const neff = report.effectiveTeamSize === null ? '' : ` · N_eff ${report.effectiveTeamSize}/${report.replicas ?? '?'}`
  return (
    <Box flexDirection="column" marginTop={1}>
      <Text bold>{truncate(`Spec health: ${report.spec}`, columns)}</Text>
      <Text color={color}>{`${report.errors} errors · ${report.warnings} warnings · ${report.info} info${neff}`}</Text>
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
      {UsageSection(el, data.usage)}
      {ReportSection(el, data.report, data.columns)}
      {PlanSection(el, data.report, data.columns)}
      {FindingsSection(el, data.report, data.columns)}
    </Box>
  )
}

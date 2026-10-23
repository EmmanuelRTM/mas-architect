import { expect, test } from 'claude-code/testing'
import type { AgentInfo } from 'claude-code'

import { resolvePanelConfig } from '../../hooks/panel/config'
import {
  MAX_AGENT_ROWS,
  agentDepths,
  concurrencyBar,
  concurrencyLevel,
  countAgents,
  depthLevel,
  maxActiveDepth,
  parseReport,
  statusGlyph,
  toAgentRows,
  truncate,
} from '../../hooks/panel/model'

const info = (id: string, status: AgentInfo['status'], parentId?: string): AgentInfo => ({
  id,
  description: `task ${id}`,
  type: 'Explore',
  status,
  ...(parentId === undefined ? {} : { parentId }),
})

test('concurrency level is ok, high from 80% and over past the limit', () => {
  expect(concurrencyLevel(0, 20)).toBe('ok')
  expect(concurrencyLevel(15, 20)).toBe('ok')
  expect(concurrencyLevel(16, 20)).toBe('high')
  expect(concurrencyLevel(20, 20)).toBe('high')
  expect(concurrencyLevel(21, 20)).toBe('over')
  expect(concurrencyBar(5, 20, 4)).toBe('█░░░ 5/20')
  expect(concurrencyBar(3, 0, 4)).toBe('████ 3/1')
})

test('depth level is high one below the limit and over at it', () => {
  expect(depthLevel(1, 3)).toBe('ok')
  expect(depthLevel(2, 3)).toBe('high')
  expect(depthLevel(3, 3)).toBe('over')
  expect(depthLevel(4, 3)).toBe('over')
})

test('status glyphs and truncation', () => {
  expect(statusGlyph('pass')).toBe('✓')
  expect(statusGlyph('warn')).toBe('!')
  expect(statusGlyph('fail')).toBe('✗')
  expect(statusGlyph('n/a')).toBe('·')
  expect(statusGlyph('weird')).toBe('?')
  expect(truncate('abcdef', 4)).toBe('abc…')
  expect(truncate('abc', 3)).toBe('abc')
  expect(truncate('abc', 1)).toBe('')
})

test('agent rows come active first, then waiting, then the rest, capped at 50', () => {
  const many = Array.from({ length: 60 }, (_, i) => info(`done-${i}`, 'completed'))
  const rows = toAgentRows([...many, info('w', 'waiting'), info('p', 'pending'), info('r', 'running'), info('f', 'failed')])
  expect(rows.length).toBe(MAX_AGENT_ROWS)
  expect(rows.slice(0, 3).map(row => row.id).sort()).toEqual(['p', 'r', 'w'].sort())
  expect(rows[0]?.status === 'running' || rows[0]?.status === 'pending').toBe(true)
  expect(rows[2]?.id).toBe('w')
  expect(rows.every(row => row.depth === 1 && row.parentId === null)).toBe(true)
  expect(countAgents(rows)).toEqual({ active: 2, waiting: 1, done: 47, failed: 0 })
})

test('depth follows parentId chains, tolerates unknown parents and cycles', () => {
  const list = [info('a', 'running'), info('b', 'running', 'a'), info('c', 'running', 'b'), info('d', 'completed', 'ghost')]
  const depths = agentDepths(list)
  expect(depths.get('a')).toBe(1)
  expect(depths.get('b')).toBe(2)
  expect(depths.get('c')).toBe(3)
  expect(depths.get('d')).toBe(2)
  const rows = toAgentRows(list)
  expect(rows.find(row => row.id === 'c')?.depth).toBe(3)
  expect(rows.find(row => row.id === 'b')?.parentId).toBe('a')
  expect(maxActiveDepth(rows)).toBe(3)
  expect(maxActiveDepth([])).toBe(0)
  const loop = agentDepths([info('x', 'running', 'y'), info('y', 'running', 'x')])
  expect(loop.get('x')).toBeGreaterThan(0)
  expect(loop.get('y')).toBeGreaterThan(0)
})

test('parseReport reads N_eff, rho, saturation and the optional monitoring object', () => {
  const view = parseReport(
    JSON.stringify({
      spec: 's',
      summary: { error: 0, warning: 1, info: 0 },
      metrics: { effective_team_size: 2.0, candidates: 3, error_correlation: 0.3, saturation_size: 3.333 },
      monitoring: { repeated_runs: true, belief_probes: false, heartbeat: true },
    }),
  )
  expect(view?.errorCorrelation).toBe(0.3)
  expect(view?.saturationSize).toBe(3.333)
  expect(view?.monitoring).toEqual({ repeatedRuns: true, beliefProbes: false, heartbeat: true, commitmentLog: null })
  const older = parseReport(JSON.stringify({ spec: 's', summary: {} }))
  expect(older?.monitoring).toBe(null)
  expect(older?.saturationSize).toBe(null)
  expect(parseReport('not json')).toBe(null)
  expect(parseReport('{"spec": "x"}')).toBe(null)
})

test('config reads the environment first and lets a changed userConfig override it', () => {
  const unset = { reportDir: undefined, maxConcurrentSubagents: undefined }
  const defaults = resolvePanelConfig({}, unset)
  expect(defaults).toEqual({
    maxConcurrentSubagents: 20,
    reportPath: '.mas/last-report.json',
    staleAfterSeconds: 120,
    maxNestingDepth: 3,
    maxConcurrentWorkflowAgents: 16,
    refreshMs: 3000,
  })
  const fromEnv = resolvePanelConfig({ maxConcurrentSubagents: 20 }, { reportDir: '/tmp/reports/', maxConcurrentSubagents: '8' })
  expect(fromEnv.maxConcurrentSubagents).toBe(8)
  expect(fromEnv.reportPath).toBe('/tmp/reports/last-report.json')
  const overridden = resolvePanelConfig(
    { maxConcurrentSubagents: 12, reportPath: 'out/r.json', refreshSeconds: 5, staleAfterSeconds: 30, maxNestingDepth: 2 },
    { reportDir: '/tmp/reports', maxConcurrentSubagents: '8' },
  )
  expect(overridden.maxConcurrentSubagents).toBe(12)
  expect(overridden.reportPath).toBe('out/r.json')
  expect(overridden.refreshMs).toBe(5000)
  expect(overridden.staleAfterSeconds).toBe(30)
  expect(overridden.maxNestingDepth).toBe(2)
  expect(resolvePanelConfig({ refreshSeconds: -1 }, { reportDir: undefined, maxConcurrentSubagents: 'nope' }).refreshMs).toBe(3000)
})

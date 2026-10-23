import { expect, test } from 'claude-code/testing'

import { concurrencyBar, countAgents, parseReport, truncate } from '../../hooks/panel/model'

const PANE = {
  plugin: 'mas-architect',
  component: 'Pane',
  requestId: 'mas-panel',
  props: {
    title: 'MAS control panel',
    isFocused: false,
    bodyColumns: 70,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 40 },
    view: {},
  },
} as const

const SURFACES = ['terminal', 'desktop', 'vscode', 'mobile'] as const

// The shape hook_lint_spec.py writes to .mas/last-report.json.
const REPORT = {
  spec: 'deep-research-report',
  summary: { error: 1, warning: 2, info: 3 },
  practices: { P1: 'pass', P3: 'warn', OPS: 'fail' },
  metrics: { effective_team_size: 2.0, candidates: 3 },
  agents: [
    { id: 'planner', role: 'planner', count: 3, model: 'claude-opus-5-5', effort: 'high', recommended: { model: 'claude-opus-5-5', effort: 'high' } },
    { id: 'selector', role: 'selector', count: 1, model: 'claude-opus-5-5', effort: 'max', recommended: { model: 'claude-haiku-5-5', effort: 'medium' } },
  ],
  findings: [
    { rule_id: 'MAS016', severity: 'error', message: 'Too many subagents.' },
    { rule_id: 'MAS017', severity: 'info', message: 'Effective team size.' },
  ],
}

test('pure helpers shape the data', () => {
  expect(concurrencyBar(5, 20, 4)).toBe('█░░░ 5/20')
  expect(truncate('abcdef', 4)).toBe('abc…')
  const counts = countAgents([
    { id: 'a', description: '', type: 'Explore', status: 'running' },
    { id: 'b', description: '', type: 'Explore', status: 'completed' },
    { id: 'c', description: '', type: 'Explore', status: 'failed' },
  ])
  expect(counts).toEqual({ active: 1, waiting: 0, done: 1, failed: 1 })
  const view = parseReport(JSON.stringify(REPORT))
  expect(view?.errors).toBe(1)
  expect(view?.findings.length).toBe(1)
  expect(view?.plan[1]?.matches).toBe(false)
  expect(parseReport('not json')).toBe(null)
  expect(parseReport('{"spec": "x"}')).toBe(null)
})

test('an empty session shows the empty states on every surface', async $ => {
  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect(await ui.find({ type: 'Text', text: /No subagents yet/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /No lint report yet/ })).toBeDefined()
    await ui.unmount()
  }
})

test('live agents, usage and the lint report reach the pane', async ($, on) => {
  on('command.register', () => ({ value: { command: 'mas-panel' } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('agent.list', () => ({
    value: [
      { id: 'a1', description: 'map auth module', type: 'Explore', status: 'running' },
      { id: 'a2', description: 'write tests', type: 'general-purpose', status: 'completed' },
    ],
  }))
  on('fs.read', () => ({ value: JSON.stringify(REPORT) }))
  on('session.usage', () => ({
    value: { startedAt: 0, context: { window: 200000, percent: 42 }, rateLimits: [], cost: { usd: 1.5 } },
  }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect((await ui.find({ type: 'Text', text: /active 1/ }))?.text).toContain('done 1')
    expect(await ui.find({ type: 'Text', text: /Explore: map auth module/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /cost \$1\.50 · context 42%/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /1 errors · 2 warnings/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /selector .* → haiku-5-5@medium/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /MAS016 Too many subagents/ })).toBeDefined()
    await ui.unmount()
  }
})

test('a malformed report leaves the empty state instead of crashing', async ($, on) => {
  on('command.register', () => ({ value: { command: 'mas-panel' } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('agent.list', () => ({ value: [] }))
  on('fs.read', () => ({ value: '{broken' }))
  on('session.usage', () => ({ value: { startedAt: 0, context: { window: 1 }, rateLimits: [] } }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect(await ui.find({ type: 'Text', text: /No lint report yet/ })).toBeDefined()
  await ui.unmount()
})

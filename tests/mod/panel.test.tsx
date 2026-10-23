import { expect, mock, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { AgentInfo, On } from 'claude-code'

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
  metrics: { effective_team_size: 2.0, candidates: 3, error_correlation: 0.3, saturation_size: 3.333 },
  monitoring: { repeated_runs: true, belief_probes: false, heartbeat: true, commitment_log: false },
  agents: [
    { id: 'planner', role: 'planner', count: 3, model: 'claude-opus-5-5', effort: 'high', skills: ['report-spec-planning'], recommended: { model: 'claude-opus-5-5', effort: 'high' } },
    { id: 'selector', role: 'selector', count: 1, model: 'claude-opus-5-5', effort: 'max', recommended: { model: 'claude-haiku-5-5', effort: 'medium' } },
  ],
  findings: [
    { rule_id: 'MAS016', severity: 'error', message: 'Too many subagents.' },
    { rule_id: 'MAS017', severity: 'info', message: 'Effective team size.' },
  ],
}

const USAGE = { startedAt: 0, context: { window: 200000, percent: 42 }, rateLimits: [], cost: { usd: 1.5 } }
const TURN = { input_tokens: 100, output_tokens: 20, cache_read_input_tokens: 800, cache_creation_input_tokens: 100 }

type World = { agents: AgentInfo[]; report: string; listCalls: number; env?: Record<string, string>; reads?: string[] }

/** The engine beneath the plugin: every noun the panel reads, answered from `world`. */
function seed(on: On, world: World) {
  const clock = mock.clock(on, { now: 1_000_000 })
  mock.env(on, world.env ?? {})
  on('command.register', () => ({ value: { command: 'mas-panel' } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('session.end', (_, e) => ({ sessionId: e.sessionId }))
  on('agent.list', () => {
    world.listCalls += 1
    return { value: world.agents }
  })
  on('fs.read', (_, e) => {
    world.reads?.push(e.path)
    return { value: world.report }
  })
  on('session.usage', () => ({ value: USAGE }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('turn.start', (_, e) => ({ turnId: e.turnId }))
  on('turn.complete', () => ({ text: '' }))
  on('agent.spawn', () => ({ model: 'claude-sonnet-5-5', agentId: 'w1' }))
  on('tool.call', (_, e) => (String(e.tool) === 'Bash' && 'command' in e && e.command === 'false' ? { isError: true, result: 'exit 1', text: 'exit 1' } : { result: {} }))
  return clock
}

const running = (id: string, description: string, parentId?: string): AgentInfo => ({
  id,
  description,
  type: 'Explore',
  status: 'running',
  ...(parentId === undefined ? {} : { parentId }),
})

const start = ($: Engine) => $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

test('an empty session shows the empty states on every surface', async ($, on) => {
  seed(on, { agents: [], report: '', listCalls: 0 })
  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect(await ui.find({ type: 'Text', text: /No subagents yet/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /No lint report yet/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /nesting 0\/3 · stale after 120s/ })).toBeDefined()
    await ui.unmount()
  }
})

test('live agents, usage and the lint report reach the pane', async ($, on) => {
  const world: World = {
    agents: [running('a1', 'map auth module'), { id: 'a2', description: 'write tests', type: 'general-purpose', status: 'completed' }],
    report: JSON.stringify(REPORT),
    listCalls: 0,
  }
  seed(on, world)
  await start($)

  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect((await ui.find({ type: 'Text', text: /active 1/ }))?.text).toContain('done 1')
    expect(await ui.find({ type: 'Text', text: /Explore: map auth module/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /nesting 1\/3/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /cost \$1\.50 · context 42% · spent 0 of 1\.5M tok \(advisory\)/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /1 errors · 2 warnings/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /N_eff 2\/3 \(spec estimate · ρ 0\.3 · saturates at 3\.333\)/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /P9 ✓ repeated runs · ✗ belief probes · ✓ heartbeat · ✗ commitment log/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /selector .* → haiku-5-5@medium/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /planner .*opus-5-5@high · 1 skill\b/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /selector .*skills\?/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /MAS016 Too many subagents/ })).toBeDefined()
    await ui.unmount()
  }
})

test('a malformed report leaves the empty state instead of crashing', async ($, on) => {
  seed(on, { agents: [], report: '{broken', listCalls: 0 })
  await start($)
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect(await ui.find({ type: 'Text', text: /No lint report yet/ })).toBeDefined()
  await ui.unmount()
})

test('userConfig values set the limits the pane shows', { options: { maxConcurrentSubagents: 4, staleAfterSeconds: 30, maxNestingDepth: 2 } }, async ($, on) => {
  seed(on, { agents: [running('a1', 'one'), running('a2', 'two', 'a1')], report: '', listCalls: 0 })
  await start($)
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect(await ui.find({ type: 'Text', text: /2\/4$/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /nesting 2\/2 · stale after 30s/ })).toBeDefined()
  await ui.unmount()
})

test('the environment sets the limit and report path until userConfig overrides them', async ($, on) => {
  const paths: string[] = []
  seed(on, { agents: [running('a1', 'one')], report: '', listCalls: 0, reads: paths, env: { CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS: '8', MAS_ARCHITECT_REPORT_DIR: '/tmp/mas' } })
  await start($)
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect(await ui.find({ type: 'Text', text: /1\/8$/ })).toBeDefined()
  expect(paths).toContain('/tmp/mas/last-report.json')
  await ui.unmount()
})

test('/mas-panel opens the pane and the poll starts only once it is placed', async ($, on) => {
  const world: World = { agents: [running('a1', 'one')], report: '', listCalls: 0 }
  const clock = seed(on, world)
  await start($)
  const afterStart = world.listCalls
  await clock.advance(10_000)
  expect(world.listCalls).toBe(afterStart)

  const ran = await $.command.run({ command: 'mas-panel', args: '', origin: { kind: 'composer' }, presentation: { isFullscreen: true, columns: 160 } })
  expect(ran.text).toBe('Opened the MAS control panel.')
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const afterOpen = world.listCalls
  await clock.advance(3_000)
  expect(world.listCalls).toBe(afterOpen + 1)
  await clock.advance(6_000)
  expect(world.listCalls).toBe(afterOpen + 3)
  await ui.unmount()

  await $.session.end({ reason: 'prompt_input_exit', sessionId: 's1', resume: { id: 's1' } })
  const afterEnd = world.listCalls
  await clock.advance(9_000)
  expect(world.listCalls).toBe(afterEnd)
})

test('a running agent silent past staleAfterSeconds is flagged as stalled', async ($, on) => {
  const clock = seed(on, { agents: [running('a1', 'slow one'), running('a2', 'busy one')], report: '', listCalls: 0 })
  await start($)
  await $.turn.start({ text: 'go', turnId: 't1', agentId: 'a1' })
  await $.turn.start({ text: 'go', turnId: 't2', agentId: 'a2' })
  await clock.advance(130_000)
  await $.tool.call({ tool: 'Bash', command: 'ls', agentId: 'a2' })

  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect((await ui.find({ type: 'Text', text: /slow one/ }))?.text).toContain('2m stalled?')
    expect((await ui.find({ type: 'Text', text: /busy one/ }))?.text).toContain('0s')
    expect((await ui.find({ type: 'Text', text: /busy one/ }))?.text.includes('stalled')).toBe(false)
    await ui.unmount()
  }
})

test('turn usage shows tokens and cache share per agent and the session total', async ($, on) => {
  seed(on, { agents: [running('a1', 'reader')], report: '', listCalls: 0 })
  await start($)
  const turn = { answer: '', durationMs: 1, isAborted: false, reason: 'answer' as const }
  await $.turn.complete({ ...turn, turnId: 't1', agentId: 'a1', usage: { ...TURN, model: 'claude-sonnet-5-5' } })
  await $.turn.complete({ ...turn, turnId: 't2', agentId: 'a1', usage: { ...TURN, model: 'claude-sonnet-5-5' } })
  await $.turn.complete({ ...turn, turnId: 't3', usage: { ...TURN, model: 'claude-opus-5-5' } })

  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect((await ui.find({ type: 'Text', text: /reader/ }))?.text).toContain('2.0k tok · cache 80%')
  expect(await ui.find({ type: 'Text', text: /spent 3\.1k of 1\.5M tok/ })).toBeDefined()
  await ui.unmount()
})

test('three tool errors in a row raise the failure-loop badge until one succeeds', async ($, on) => {
  seed(on, { agents: [running('a1', 'looper')], report: '', listCalls: 0 })
  await start($)
  for (let i = 0; i < 3; i += 1) await $.tool.call({ tool: 'Bash', command: 'false', agentId: 'a1' })

  let ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect((await ui.find({ type: 'Text', text: /looper/ }))?.text).toContain('3 errors in a row')
  await ui.unmount()

  await $.tool.call({ tool: 'Bash', command: 'ls', agentId: 'a1' })
  ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect((await ui.find({ type: 'Text', text: /looper/ }))?.text.includes('errors in a row')).toBe(false)
  await ui.unmount()
})

test('workflow agents get their own bar from spawn to turn end', async ($, on) => {
  seed(on, { agents: [], report: '', listCalls: 0 })
  await start($)
  const spawn = {
    tool_use_id: 'tu1',
    prompt: 'do',
    description: 'wf agent',
    subagentType: 'general-purpose',
    provider: { plugin: 'engine', tier: 'core' as const },
    parentModel: 'claude-sonnet-5-5',
    background: true,
    fork: false,
  }
  await $.agent.spawn({ ...spawn, workflow: { runId: 'wf_1', agentIndex: 1 } })
  let ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect(await ui.find({ type: 'Text', text: /1\/16 workflow/ })).toBeDefined()
  await ui.unmount()

  await $.turn.complete({ answer: '', durationMs: 1, isAborted: false, reason: 'answer', turnId: 't1', agentId: 'w1' })
  ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect(await ui.find({ type: 'Text', text: /workflow/ })).toBeUndefined()
  await ui.unmount()
})

test('editing a .mas.json spec re-reads the report without waiting for a poll', async ($, on) => {
  const world: World = { agents: [], report: '', listCalls: 0 }
  seed(on, world)
  await start($)
  let ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect(await ui.find({ type: 'Text', text: /No lint report yet/ })).toBeDefined()
  await ui.unmount()

  world.report = JSON.stringify(REPORT)
  await $.tool.call({ tool: 'Edit', file_path: '/w/team.mas.json', old_string: 'a', new_string: 'b' })
  ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect(await ui.find({ type: 'Text', text: /Spec health: deep-research-report/ })).toBeDefined()
  await ui.unmount()
})

test('a narrow pane truncates every line instead of overflowing, on all surfaces', async ($, on) => {
  seed(on, { agents: [running('a1', 'a very long description that will not fit in a narrow pane at all')], report: JSON.stringify(REPORT), listCalls: 0 })
  await start($)
  const narrow = { ...PANE, props: { ...PANE.props, bodyColumns: 24, scroll: { offset: 0, bodyRows: 12 } } } as const
  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...narrow, surface })
    const line = await ui.find({ type: 'Text', text: /Explore: a very/ })
    expect(line?.text.length).toBe(24)
    expect(line?.text.endsWith('…')).toBe(true)
    expect(await ui.find({ type: 'Text', text: /MAS016/ })).toBeDefined()
    await ui.unmount()
  }
})

// mas-architect control panel: live subagents vs the concurrency limit,
// liveness per agent, nesting depth, tokens per agent, session cost and the
// latest .mas.json lint report with its model plan.
import type { EngineInterface, Register, Timer, ToolCallInput } from 'claude-code'

import { resolvePanelConfig } from './panel/config'
import type { PanelConfig } from './panel/config'
import { readPanelState, recordToolResult, recordTurnUsage, refresh, touchAgent, trackWorkflowAgent } from './panel/sources'
import { renderPanel } from './panel/view'

const PANE = 'mas-panel'
const TITLE = 'MAS control panel'
const SPEC_FILE = /\.mas\.(json|yaml|yml)$/
const SPEC_EDITORS = new Set(['Write', 'Edit', 'MultiEdit'])
/** Rows assumed when a surface reports no body height. */
const DEFAULT_BODY_ROWS = 30

/** The panel is an observer: its bookkeeping never fails the hook it rides. */
const quietly = (work: Promise<unknown>): Promise<void> => work.then(() => undefined, () => undefined)

/** The file path a Write/Edit/MultiEdit call targets, or null for any other call. */
function editedSpecPath(e: ToolCallInput): string | null {
  if (!SPEC_EDITORS.has(String(e.tool))) return null
  const path: unknown = 'file_path' in e ? e.file_path : undefined
  return typeof path === 'string' && SPEC_FILE.test(path) ? path : null
}

// Module state: starts over on a reload (the engine drops the old timer too).
let config: PanelConfig = resolvePanelConfig({}, { reportDir: undefined, maxConcurrentSubagents: undefined })
let poll: Timer | null = null

/** Poll only once the pane is drawn; the handle is cancelled on `session.end`. */
function startPolling($: EngineInterface): void {
  if (poll !== null) return
  poll = $.clock.every(config.refreshMs, () => void quietly(refresh($, config.reportPath, { agents: true, usage: true })))
}

function stopPolling(): void {
  poll?.cancel()
  poll = null
}

export const register: Register = (on, options) => {
  config = resolvePanelConfig(options, { reportDir: undefined, maxConcurrentSubagents: undefined })
  stopPolling()

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'mas-panel',
      description: 'Open the multi-agent control panel (agents, liveness, depth, tokens, spec health, model plan)',
    })
    const [reportDir, maxConcurrentSubagents] = await Promise.all([
      $.env.get('MAS_ARCHITECT_REPORT_DIR'),
      $.env.get('CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS'),
    ])
    config = resolvePanelConfig(options, { reportDir, maxConcurrentSubagents })
    await quietly(refresh($, config.reportPath))
    return next(e)
  })

  on('session.end', ($, e, next) => {
    stopPolling()
    return next(e)
  })

  on('command.run', { command: 'mas-panel' }, async $ => {
    await refresh($, config.reportPath).catch(() => undefined)
    const opened = await $.ui.open({ id: PANE, title: TITLE })
    if (opened.isPlaced) startPolling($)
    return { text: opened.isPlaced ? 'Opened the MAS control panel.' : `The MAS control panel is ready but undrawn: ${opened.reason}` }
  })

  // Observers: each lets the event through and records what the panel shows.
  on('agent.spawn', async ($, e, next) => {
    const ran = await next(e)
    if (ran.agentId !== undefined) {
      await quietly(touchAgent($, ran.agentId))
      if (e.workflow !== undefined) await quietly(trackWorkflowAgent($, ran.agentId, true))
    }
    await quietly(refresh($, config.reportPath, { agents: true }))
    return ran
  }).catch(($, e, next) => next(e))

  on('turn.start', async ($, e, next) => {
    await quietly(touchAgent($, e.agentId))
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    await quietly(touchAgent($, e.agentId))
    await quietly(recordTurnUsage($, e.agentId, e.usage))
    if (e.agentId !== undefined) await quietly(trackWorkflowAgent($, e.agentId, false))
    await quietly(refresh($, config.reportPath, { agents: true, usage: true }))
    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    await quietly(touchAgent($, e.agentId))
    const ran = await next(e)
    await quietly(recordToolResult($, e.agentId, ran.isError === true))
    if (editedSpecPath(e) !== null) await quietly(refresh($, config.reportPath, { report: true }))
    return ran
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    startPolling($)
    const el = $.ui.resolve(e)
    const [state, now] = await Promise.all([readPanelState($), $.clock.now()])
    return renderPanel(el, {
      ...state,
      now,
      config,
      columns: Math.max(20, e.props.bodyColumns ?? 60),
      rows: e.props.scroll.bodyRows ?? DEFAULT_BODY_ROWS,
    })
  })
}

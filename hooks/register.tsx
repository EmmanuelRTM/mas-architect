// mas-architect control panel: live subagents vs the concurrency limit,
// session cost, and the latest .mas.json lint report with its model plan.
import type { Register } from 'claude-code'

import { readPanelState, refresh } from './panel/sources'
import { renderPanel } from './panel/view'

const PANE = 'mas-panel'
const TITLE = 'MAS control panel'
const POLL_MS = 3000

export const register: Register = (on, options) => {
  const limit = typeof options.maxConcurrentSubagents === 'number' ? options.maxConcurrentSubagents : 20
  const reportPath = typeof options.reportPath === 'string' ? options.reportPath : '.mas/last-report.json'

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'mas-panel',
      description: 'Open the multi-agent control panel (agents, concurrency, spec health, model plan)',
    })
    await refresh($, reportPath).catch(() => undefined)
    $.clock.every(POLL_MS, () => {
      void refresh($, reportPath).catch(() => undefined)
    })
    return next(e)
  })

  on('command.run', { command: 'mas-panel' }, async $ => {
    await refresh($, reportPath).catch(() => undefined)
    const { isPlaced } = await $.ui.open({ id: PANE, title: TITLE })
    return { text: isPlaced ? 'Opened the MAS control panel.' : 'The MAS control panel is ready but this surface shows no panes.' }
  })

  // Refresh right after a delegation so the panel reacts without waiting for the poll.
  on('tool.call', { tool: 'Agent' }, async ($, e, next) => {
    const ran = await next(e)
    void refresh($, reportPath).catch(() => undefined)
    return ran
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const el = $.ui.resolve(e)
    return renderPanel(el, {
      ...(await readPanelState($)),
      limit,
      columns: Math.max(20, e.props.bodyColumns ?? 60),
      rows: e.viewport?.rows ?? 40,
    })
  })
}

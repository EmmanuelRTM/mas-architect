// Panel configuration: environment first, userConfig overrides when the
// person set it (a value equal to the manifest default is read as unset). Pure.
import type { PluginOptions } from 'claude-code'

import { DEFAULT_STALE_AFTER_SECONDS } from './liveness'

export const DEFAULTS = {
  maxConcurrentSubagents: 20,
  reportPath: '.mas/last-report.json',
  staleAfterSeconds: DEFAULT_STALE_AFTER_SECONDS,
  maxNestingDepth: 3,
  maxConcurrentWorkflowAgents: 16,
  refreshSeconds: 3,
} as const

export const REPORT_FILE = 'last-report.json'

export type PanelConfig = {
  maxConcurrentSubagents: number
  reportPath: string
  staleAfterSeconds: number
  maxNestingDepth: number
  maxConcurrentWorkflowAgents: number
  refreshMs: number
}

/** The two variables the panel reads; each `undefined` when unset. */
export type PanelEnv = { reportDir: string | undefined; maxConcurrentSubagents: string | undefined }

const positive = (value: unknown, fallback: number): number =>
  typeof value === 'number' && Number.isFinite(value) && value > 0 ? value : fallback

function optionNumber(options: PluginOptions, key: keyof typeof DEFAULTS, fromEnv: number | null): number {
  const fallback = DEFAULTS[key] as number
  const chosen = positive(options[key], fallback)
  if (chosen !== fallback) return chosen
  return fromEnv ?? fallback
}

function envNumber(raw: string | undefined): number | null {
  if (raw === undefined || raw.trim() === '') return null
  const parsed = Number(raw)
  return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : null
}

function reportPath(options: PluginOptions, reportDir: string | undefined): string {
  const chosen = typeof options.reportPath === 'string' && options.reportPath.trim() !== '' ? options.reportPath : DEFAULTS.reportPath
  if (chosen !== DEFAULTS.reportPath) return chosen
  if (reportDir !== undefined && reportDir.trim() !== '') return `${reportDir.replace(/\/+$/, '')}/${REPORT_FILE}`
  return DEFAULTS.reportPath
}

export function resolvePanelConfig(options: PluginOptions, env: PanelEnv): PanelConfig {
  return {
    maxConcurrentSubagents: optionNumber(options, 'maxConcurrentSubagents', envNumber(env.maxConcurrentSubagents)),
    reportPath: reportPath(options, env.reportDir),
    staleAfterSeconds: positive(options.staleAfterSeconds, DEFAULTS.staleAfterSeconds),
    maxNestingDepth: positive(options.maxNestingDepth, DEFAULTS.maxNestingDepth),
    maxConcurrentWorkflowAgents: positive(options.maxConcurrentWorkflowAgents, DEFAULTS.maxConcurrentWorkflowAgents),
    refreshMs: Math.max(1, positive(options.refreshSeconds, DEFAULTS.refreshSeconds)) * 1000,
  }
}

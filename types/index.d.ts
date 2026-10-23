export type AgentRow = {
  id: string
  description: string
  type: string
  status: string
}

export type PlanRow = {
  id: string
  role: string
  count: number
  model: string
  effort: string
  recommended: string
  matches: boolean
  /** Preloaded skills; null when the spec does not declare them. */
  skills: number | null
}

export type FindingRow = { ruleId: string; severity: string; message: string }

export type ReportView = {
  spec: string
  errors: number
  warnings: number
  info: number
  practices: { id: string; status: string }[]
  plan: PlanRow[]
  findings: FindingRow[]
  effectiveTeamSize: number | null
  replicas: number | null
}

export type UsageView = { costUsd: number | null; contextPercent: number | null }

declare module 'claude-code' {
  interface PluginState {
    'mas-architect': {
      agents: Shaped<AgentRow[]>
      report: Shaped<ReportView | null>
      usage: Shaped<UsageView | null>
    }
  }
}

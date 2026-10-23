// State contract of the mas-architect control panel. Self-contained: no
// import, so the engine checks every `$.state` key the module names here.

/** Mirrors the engine's AgentStatus union (checked at compile time in model.ts). */
export type PanelAgentStatus = 'pending' | 'running' | 'waiting' | 'idle' | 'completed' | 'failed' | 'killed'

export type AgentRow = {
  id: string
  description: string
  type: string
  status: PanelAgentStatus
  /** Nesting depth from the main loop: 1 for a direct subagent. */
  depth: number
  parentId: string | null
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

/** The report's top-level `monitoring` object (P9), absent in older reports. */
export type MonitoringView = {
  repeatedRuns: boolean | null
  beliefProbes: boolean | null
  heartbeat: boolean | null
  commitmentLog: boolean | null
}

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
  errorCorrelation: number | null
  saturationSize: number | null
  monitoring: MonitoringView | null
}

export type UsageView = { costUsd: number | null; contextPercent: number | null }

/** Token counts one agent (or `main`) accrued over its turns, plus its error streak. */
export type AgentUsage = {
  input: number
  output: number
  cacheRead: number
  cacheCreation: number
  turns: number
  /** Tool errors since the last successful tool call. */
  consecutiveErrors: number
}

/** Last time each agent showed a sign of life, in `$.clock.now()` milliseconds. */
export type LastSeen = Record<string, number>

export type AgentUsageMap = Record<string, AgentUsage>

/** Workflow agents started by `agent.spawn` with `e.workflow` and not yet ended. */
export type WorkflowRunning = string[]

declare module 'claude-code' {
  interface PluginState {
    'mas-architect': {
      agents: Shaped<AgentRow[]>
      report: Shaped<ReportView | null>
      usage: Shaped<UsageView | null>
      lastSeen: Shaped<LastSeen>
      agentUsage: Shaped<AgentUsageMap>
      workflow: Shaped<WorkflowRunning>
      clockMs: Shaped<number>
    }
  }
}

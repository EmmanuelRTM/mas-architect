// Usage per agent (P5): tokens, cache-read share and failure loops. Pure.
import type { ModelUsage } from 'claude-code'

import type { AgentUsage, AgentUsageMap } from '../../types'

/** Claude Code's advisory for one workflow run: a reference line, not a cap. */
export const WORKFLOW_ADVISORY_TOKENS = 1_500_000
/** Consecutive tool errors that read as a failure loop worth halting. */
export const ERROR_STREAK_BADGE = 3
/** Key for the main loop's own turns. */
export const MAIN_LOOP = 'main'

export const EMPTY_USAGE: AgentUsage = { input: 0, output: 0, cacheRead: 0, cacheCreation: 0, turns: 0, consecutiveErrors: 0 }

export function addTurnUsage(map: AgentUsageMap, agentId: string, usage: ModelUsage): AgentUsageMap {
  const before = map[agentId] ?? EMPTY_USAGE
  return {
    ...map,
    [agentId]: {
      ...before,
      input: before.input + usage.input_tokens,
      output: before.output + usage.output_tokens,
      cacheRead: before.cacheRead + usage.cache_read_input_tokens,
      cacheCreation: before.cacheCreation + usage.cache_creation_input_tokens,
      turns: before.turns + 1,
    },
  }
}

/** A failed tool call lengthens the streak; a successful one resets it. */
export function noteToolResult(map: AgentUsageMap, agentId: string, isError: boolean): AgentUsageMap {
  const before = map[agentId] ?? EMPTY_USAGE
  const consecutiveErrors = isError ? before.consecutiveErrors + 1 : 0
  if (consecutiveErrors === before.consecutiveErrors && map[agentId] !== undefined) return map
  return { ...map, [agentId]: { ...before, consecutiveErrors } }
}

export function totalTokens(usage: AgentUsage): number {
  return usage.input + usage.output + usage.cacheRead + usage.cacheCreation
}

/** Share of input served from the prompt cache, 0..1; null before any input. */
export function cacheShare(usage: AgentUsage): number | null {
  const inputs = usage.input + usage.cacheRead + usage.cacheCreation
  return inputs === 0 ? null : usage.cacheRead / inputs
}

/** Tokens spent so far across every loop, main included. */
export function sessionTokens(map: AgentUsageMap): number {
  return Object.values(map).reduce((sum, usage) => sum + totalTokens(usage), 0)
}

export function errorBadge(usage: AgentUsage | undefined): string {
  const streak = usage?.consecutiveErrors ?? 0
  return streak >= ERROR_STREAK_BADGE ? ` ⚠ ${streak} errors in a row` : ''
}

/** `12.3k`, `1.5M`, `842`. */
export function formatTokens(count: number): string {
  if (count >= 1_000_000) return `${(count / 1_000_000).toFixed(count >= 10_000_000 ? 0 : 1)}M`
  if (count >= 1_000) return `${(count / 1_000).toFixed(count >= 10_000 ? 0 : 1)}k`
  return String(count)
}

/** ` · 12.3k tok · cache 82%` for an agent that spent tokens; empty otherwise. */
export function usageLabel(usage: AgentUsage | undefined): string {
  if (usage === undefined || usage.turns === 0) return ''
  const share = cacheShare(usage)
  const cache = share === null ? '' : ` · cache ${Math.round(share * 100)}%`
  return ` · ${formatTokens(totalTokens(usage))} tok${cache}`
}

/** Drop entries of agents no longer listed, keeping the main loop's. */
export function pruneUsage(map: AgentUsageMap, liveIds: readonly string[]): AgentUsageMap {
  const keep = new Set([...liveIds, MAIN_LOOP])
  const entries = Object.entries(map).filter(([id]) => keep.has(id))
  return entries.length === Object.keys(map).length ? map : Object.fromEntries(entries)
}

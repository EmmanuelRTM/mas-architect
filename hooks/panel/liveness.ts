// Liveness (P9, Agent Status Protocol): an agent that is `running` but has
// shown no event for too long is "alive but not progressing". Pure.
import type { LastSeen } from '../../types'

export const DEFAULT_STALE_AFTER_SECONDS = 120

export function markSeen(seen: LastSeen, agentId: string, nowMs: number): LastSeen {
  return seen[agentId] === nowMs ? seen : { ...seen, [agentId]: nowMs }
}

/** Milliseconds since the agent's last sign of life; null when never seen. */
export function ageMs(seen: LastSeen, agentId: string, nowMs: number): number | null {
  const last = seen[agentId]
  return last === undefined ? null : Math.max(0, nowMs - last)
}

export function isStalled(age: number | null, staleAfterSeconds: number): boolean {
  return age !== null && age >= Math.max(1, staleAfterSeconds) * 1000
}

/** `12s`, `3m`, `2h`; empty when never seen. */
export function formatAge(age: number | null): string {
  if (age === null) return ''
  const seconds = Math.floor(age / 1000)
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`
  return `${Math.floor(seconds / 3600)}h`
}

/** Drop entries of agents no longer listed so the record cannot grow without bound. */
export function pruneSeen(seen: LastSeen, liveIds: readonly string[]): LastSeen {
  const keep = new Set(liveIds)
  const entries = Object.entries(seen).filter(([id]) => keep.has(id))
  return entries.length === Object.keys(seen).length ? seen : Object.fromEntries(entries)
}

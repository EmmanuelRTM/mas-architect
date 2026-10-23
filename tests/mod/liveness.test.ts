import { expect, test } from 'claude-code/testing'

import { ageMs, formatAge, isStalled, markSeen, pruneSeen } from '../../hooks/panel/liveness'

test('markSeen records the time and keeps the same object when nothing changed', () => {
  const first = markSeen({}, 'a1', 1000)
  expect(first).toEqual({ a1: 1000 })
  expect(markSeen(first, 'a1', 1000)).toBe(first)
  expect(markSeen(first, 'a2', 2000)).toEqual({ a1: 1000, a2: 2000 })
})

test('age is measured from the last sign of life and never negative', () => {
  expect(ageMs({ a1: 1000 }, 'a1', 4000)).toBe(3000)
  expect(ageMs({ a1: 5000 }, 'a1', 4000)).toBe(0)
  expect(ageMs({}, 'a1', 4000)).toBe(null)
})

test('an agent is stalled once silent for staleAfterSeconds', () => {
  expect(isStalled(119_999, 120)).toBe(false)
  expect(isStalled(120_000, 120)).toBe(true)
  expect(isStalled(null, 120)).toBe(false)
  expect(isStalled(1000, 0)).toBe(true)
})

test('ages read as seconds, minutes or hours', () => {
  expect(formatAge(null)).toBe('')
  expect(formatAge(12_400)).toBe('12s')
  expect(formatAge(185_000)).toBe('3m')
  expect(formatAge(7_200_000)).toBe('2h')
})

test('pruning drops agents no longer listed', () => {
  const seen = { a1: 1, a2: 2 }
  expect(pruneSeen(seen, ['a1', 'a2'])).toBe(seen)
  expect(pruneSeen(seen, ['a2'])).toEqual({ a2: 2 })
})

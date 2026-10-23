import { expect, test } from 'claude-code/testing'

import {
  EMPTY_USAGE,
  addTurnUsage,
  cacheShare,
  errorBadge,
  formatTokens,
  noteToolResult,
  pruneUsage,
  sessionTokens,
  totalTokens,
  usageLabel,
} from '../../hooks/panel/usage'

const turn = (input: number, cacheRead: number, cacheCreation = 0, output = 10) => ({
  input_tokens: input,
  output_tokens: output,
  cache_read_input_tokens: cacheRead,
  cache_creation_input_tokens: cacheCreation,
})

test('turn usage accumulates per agent and the cache share is read over all input', () => {
  let map = addTurnUsage({}, 'a1', turn(100, 800, 100))
  map = addTurnUsage(map, 'a1', turn(50, 850, 100))
  map = addTurnUsage(map, 'main', turn(10, 0))
  const a1 = map.a1
  expect(a1?.turns).toBe(2)
  expect(a1?.input).toBe(150)
  expect(a1?.cacheRead).toBe(1650)
  expect(a1 && totalTokens(a1)).toBe(150 + 20 + 1650 + 200)
  expect(a1 && cacheShare(a1)).toBe(1650 / 2000)
  expect(cacheShare(EMPTY_USAGE)).toBe(null)
  expect(sessionTokens(map)).toBe(2020 + 20)
})

test('consecutive tool errors count up and reset on success', () => {
  let map = noteToolResult({}, 'a1', true)
  map = noteToolResult(map, 'a1', true)
  expect(map.a1?.consecutiveErrors).toBe(2)
  expect(errorBadge(map.a1)).toBe('')
  map = noteToolResult(map, 'a1', true)
  expect(errorBadge(map.a1)).toBe(' ⚠ 3 errors in a row')
  const same = noteToolResult(map, 'a1', false)
  expect(same.a1?.consecutiveErrors).toBe(0)
  expect(noteToolResult(same, 'a1', false)).toBe(same)
  expect(errorBadge(undefined)).toBe('')
})

test('labels format tokens compactly', () => {
  expect(formatTokens(842)).toBe('842')
  expect(formatTokens(12_340)).toBe('12k')
  expect(formatTokens(1_234)).toBe('1.2k')
  expect(formatTokens(1_500_000)).toBe('1.5M')
  expect(usageLabel(undefined)).toBe('')
  expect(usageLabel(addTurnUsage({}, 'a', turn(100, 800, 100)).a)).toBe(' · 1.0k tok · cache 80%')
})

test('pruning keeps the main loop and the listed agents only', () => {
  const map = addTurnUsage(addTurnUsage({}, 'main', turn(1, 0)), 'gone', turn(1, 0))
  expect(Object.keys(pruneUsage(map, []))).toEqual(['main'])
  expect(pruneUsage(map, ['gone'])).toBe(map)
})

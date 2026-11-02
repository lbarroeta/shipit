import { expect, test } from 'claude-code/testing'
import { addTime, addUsage, duration, empty, merge, render, stageOf } from './metrics'

const u = (input: number, output: number, cacheRead = 0, cacheWrite = 0) => ({ input, output, cacheRead, cacheWrite })

test('maps shipit run agents to their skills', async () => {
  expect(stageOf('shipit:run-builder')).toBe('code-implement')
  expect(stageOf('run-delivery')).toBe('code-handoff')
  expect(stageOf('Explore')).toBe('other')
})

test('merges segments and renders the per-skill table', async () => {
  const a = empty()
  a.ms = 600_000
  addUsage(a, 'run', u(1000, 200))
  addUsage(a, 'code-implement', u(5000, 3000, 100_000, 2000))
  addTime(a, 'code-implement', 400_000)
  const b = empty()
  b.ms = 120_000
  addUsage(b, 'code-handoff', u(300, 100))
  addTime(b, 'code-handoff', 60_000)
  addUsage(b, 'run', u(10, 5))

  const t = merge(a, b)
  expect(t.ms).toBe(720_000)
  expect(t.stages.run?.usage.input).toBe(1010)

  const md = render(t)
  expect(md).toContain('Total: 12m 00s · 111,615 tokens')
  // Coordinator time is the total minus what its subagents spent.
  expect(md).toContain('| run | 4m 20s | 1,010 | 205 | 0 | 0 | 1,215 |')
  expect(md).toContain('| code-implement | 6m 40s | 5,000 | 3,000 | 100,000 | 2,000 | 110,000 |')
  expect(md.indexOf('| run |')).toBeLessThan(md.indexOf('| code-implement |'))
  expect(md.indexOf('| code-implement |')).toBeLessThan(md.indexOf('| code-handoff |'))
  expect(md).toContain('| **Total** | 12m 00s | 6,310 | 3,305 | 100,000 | 2,000 | 111,615 |')
})

test('formats durations', async () => {
  expect(duration(45_400)).toBe('45s')
  expect(duration(3_723_000)).toBe('1h 02m 03s')
})

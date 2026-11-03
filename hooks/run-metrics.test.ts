import { expect, mock, test } from 'claude-code/testing'

test('counts a run while its own checkout lock is held, background agents included, per repository and worktree', async ($, on) => {
  const clock = mock.clock(on)
  mock.store(on, {
    // Same branch name in another repository: must not leak into this one.
    'run:/other:feat/x': { ms: 999_000, stages: { run: { ms: 0, usage: { input: 9, output: 9, cacheRead: 9, cacheWrite: 9 } } } },
  })
  let locked = false
  let usage: { input_tokens: number; output_tokens: number } | null = null
  on('process.run', () => ({ value: { exitCode: 0, stdout: '/repo\n/repo/.git\nfeat/x\n', stderr: '' } }))
  const lock = (name: string) => ({ name, kind: 'file' as const, size: 1, mtimeMs: 0, isLink: false })
  // Another worktree of the same repository runs its own card the whole time: it must not count here.
  on('fs.list', () => ({
    value: [lock('checkout-other.json'), lock('checkout-half.json'), ...(locked ? [lock('checkout-abc.json')] : [])],
  }))
  on('fs.read', (_, e) => ({
    value: e.path.endsWith('checkout-abc.json') ? '{"owner": "o", "repo": "/repo"}'
      : e.path.endsWith('checkout-half.json') ? '{"own' // being written right now
      : '{"owner": "x", "repo": "/worktrees/repo/eng-413"}',
  }))
  on('agent.spawn', () => ({ model: 'm', agentId: 'b1' }))
  on('turn.step', async function* (_, e) {
    const u = usage && { ...usage, cache_read_input_tokens: 0, cache_creation_input_tokens: 0, model: 'm' }
    return { turnId: e.turnId, index: e.index, answer: '', toolUses: [], stopReason: 'end_turn', usage: u }
  })
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('tool.call', () => ({ result: {} }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('tool.register', () => ({ value: {} }))
  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })

  const step = async (input: number, output: number, agentId?: string) => {
    usage = { input_tokens: input, output_tokens: output }
    const s = $.turn.step({ turnId: 't', index: 0, model: 'm', messageCount: 1, agentId })
    for await (const _ of s);
    await s.result
  }
  const complete = (durationMs: number, agentId?: string) =>
    $.turn.complete({ answer: '', durationMs, isAborted: false, turnId: 't', agentId, reason: 'answer' })

  await step(7, 7) // before `begin`: not counted
  locked = true
  await step(100, 10) // the coordinator, after `begin`
  await clock.advance(1_000)
  await $.agent.spawn({ prompt: 'build', subagentType: 'shipit:run-builder' })
  await complete(1_000) // the coordinator's turn ends; the builder runs in the background
  await clock.advance(60_000)
  await step(5_000, 3_000, 'b1')
  await complete(60_000, 'b1')
  await clock.advance(1_000)
  locked = false // paused for QA
  await step(20, 2)
  await step(7, 7) // after the pause: not counted

  const r = await $.tool.call({ tool: 'mcp__shipit__run_metrics' })
  const md = String((r as { result: unknown }).result)
  expect(md).toContain('Total: 1m 02s · 8,132 tokens')
  expect(md).toContain('| run | 2s | 120 | 12 | 0 | 0 | 132 |')
  expect(md).toContain('| code-implement | 1m 00s | 5,000 | 3,000 | 0 | 0 | 8,000 |')
})

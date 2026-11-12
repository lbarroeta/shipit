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
  on('session.id', () => ({ value: 's1' }))
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

test('counts each card worktree this session locked on its own, and answers none rather than a hollow table', async ($, on) => {
  const clock = mock.clock(on)
  mock.store(on, {})
  // Another session's card; a second one of its cards starts in the same seconds as ours.
  const locks: Record<string, { repo: string; owner: string }> = { 'checkout-x.json': { repo: '/worktrees/repo/9', owner: 'b'.repeat(32) } }
  const branches: Record<string, string> = { '/repo': 'main', '/worktrees/repo/1': 'feat/1', '/worktrees/repo/12': 'feat/12' }
  on('process.run', (_, e) => {
    const dir = e.argv[1] === '-C' ? e.argv[2]! : '/repo'
    return { value: { exitCode: 0, stdout: `${dir}\n/repo/.git\n${branches[dir] ?? 'feat/9'}\n`, stderr: '' } }
  })
  on('fs.list', () => ({ value: Object.keys(locks).map(name => ({ name, kind: 'file' as const, size: 1, mtimeMs: 0, isLink: false })) }))
  on('fs.read', (_, e) => ({ value: JSON.stringify(locks[e.path.split('/').pop()!]) }))
  let n = 0
  on('agent.spawn', () => ({ model: 'm', agentId: `a${++n}` }))
  let usage = { input_tokens: 0, output_tokens: 0 }
  on('turn.step', async function* (_, e) {
    return { turnId: e.turnId, index: e.index, answer: '', toolUses: [], stopReason: 'end_turn',
      usage: { ...usage, cache_read_input_tokens: 0, cache_creation_input_tokens: 0, model: 'm' } }
  })
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('tool.call', (_, e) => {
    if (!('command' in e) || !e.command.includes('begin')) return { result: {} }
    // The coordinator's `begin` for both cards takes their locks and prints their owners.
    Object.assign(locks, {
      'checkout-1.json': { repo: '/worktrees/repo/1', owner: '1'.repeat(32) },
      'checkout-12.json': { repo: '/worktrees/repo/12', owner: '2'.repeat(32) },
      'checkout-y.json': { repo: '/worktrees/repo/10', owner: 'c'.repeat(32) },
    })
    return { result: { stdout: `{"owner": "${'1'.repeat(32)}"}\n{"owner": "${'2'.repeat(32)}"}`, stderr: '' } }
  })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('tool.register', () => ({ value: {} }))
  on('session.id', () => ({ value: 's1' }))
  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })

  const step = async (input: number, agentId?: string) => {
    usage = { input_tokens: input, output_tokens: 0 }
    const s = $.turn.step({ turnId: 't', index: 0, model: 'm', messageCount: 1, agentId })
    for await (const _ of s);
    await s.result
  }
  const metrics = async (agentId?: string, repo?: string) =>
    String(((await $.tool.call({ tool: 'mcp__shipit__run_metrics', agentId, ...(repo && { repo }) })) as { result: unknown }).result)

  await $.tool.call({ tool: 'Bash', command: 'python3 skills/run/scripts/run_state.py begin --repo /worktrees/repo/1' })
  await step(100) // the coordinator, shared by both cards
  const b1 = (await $.agent.spawn({ prompt: 'Build in /worktrees/repo/1', subagentType: 'shipit:run-builder' })).agentId!
  const b12 = (await $.agent.spawn({ prompt: 'Build in /worktrees/repo/12', subagentType: 'shipit:run-builder' })).agentId!
  await clock.advance(1_000)
  await step(1_000, b1)
  await step(4_000, b12)
  const d12 = (await $.agent.spawn({ prompt: 'Deliver /worktrees/repo/12', subagentType: 'shipit:run-delivery' })).agentId!

  const card12 = await metrics(d12)
  expect(card12).toContain('Total: 1s · 4,050 tokens')
  expect(card12).toContain('| code-implement |')
  expect(card12).not.toContain('1,000')
  expect(await metrics(b1)).toContain('Total: 1s · 1,050 tokens')
  // The session's own checkout ran nothing: no table, even with agents in flight.
  expect(await metrics()).toBe('No shipit run metrics recorded for this branch.')
  // retro, from the main loop, names the card it reads.
  expect(await metrics(undefined, '/worktrees/repo/1/')).toContain('Total: 1s · 1,050 tokens')
})

import type { EngineInterface, Register } from 'claude-code'
import { addTime, addUsage, empty, merge, render, stageOf, type Totals } from './metrics'

const TOOL = 'mcp__shipit__run_metrics'
const NONE = 'No shipit run metrics recorded for this branch.'

// The run being counted; its totals are saved to $.store on every change, so a
// reload or another session only loses the step in flight.
let run: { key: string; totals: Totals; at: number } | undefined
let locks: string | undefined
const agents = new Map<string, { stage: string; since?: number }>()

async function git($: EngineInterface) {
  const { exitCode, stdout } = await $.process.run([
    'git', 'rev-parse', '--path-format=absolute', '--show-toplevel', '--git-common-dir', '--abbrev-ref', 'HEAD',
  ])
  const [top = '', common = '', branch = ''] = stdout.trim().split('\n')
  return exitCode === 0 && top ? { common, key: branch && branch !== 'HEAD' ? `run:${top}:${branch}` : undefined } : undefined
}

// A run is working while run_state.py holds its checkout lock: from `begin`
// until it pauses (QA, a decision, a failure) or finishes.
// shortcut: any checkout lock of the repository counts, so a run in another
// worktree of the same repository would too; match the lock's digest if that happens.
async function isLocked($: EngineInterface) {
  locks ??= (await git($))?.common ?? ''
  if (!locks) return false
  try {
    return (await $.fs.list(`${locks}/shipit/locks`)).some(f => f.name.startsWith('checkout-'))
  } catch {
    return false
  }
}

async function stored($: EngineInterface, key: string | undefined) {
  return ((key && (await $.store.get(key))) as Totals | undefined) ?? empty()
}

// Moves the run's time up to now, applies `change` and saves; outside a run it does nothing.
async function track($: EngineInterface, change: (t: Totals) => void = () => {}) {
  const locked = await isLocked($)
  const now = await $.clock.now()
  if (!run && locked) {
    const key = (await git($))?.key
    if (!key) return
    run = { key, totals: await stored($, key), at: now }
  }
  if (!run) return
  const r = run
  r.totals.ms += Math.max(0, now - r.at) // the step that released the lock counts too
  r.at = Math.max(r.at, now)
  change(r.totals)
  if (!locked) run = undefined
  await $.store.set(r.key, r.totals)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const r = await next(e)
    await $.tool.register({
      name: 'run_metrics',
      description:
        'Total tokens and execution time of the current shipit:run task, with the breakdown per skill, as a markdown "Run metrics" section. Call it right before publishing the PR body.',
      isDeferred: false,
    })
    return r
  })

  on('agent.spawn', async ($, e, next) => {
    const r = await next(e)
    if (r.agentId) agents.set(r.agentId, { stage: stageOf(e.subagentType), since: await $.clock.now() })
    return r
  }).catch(($, e, next) => next(e)) // bookkeeping never blocks a spawn

  on('turn.start', async ($, e, next) => {
    const a = e.agentId ? agents.get(e.agentId) : undefined
    if (a) a.since = await $.clock.now()
    return next(e)
  })

  // Every model response, main loop and subagents alike, counted once here.
  on('turn.step', async function* ($, e, next) {
    const r = yield* next(e)
    const stage = e.agentId ? agents.get(e.agentId)?.stage : 'run'
    const u = r.usage
    await track($, t => {
      if (stage && u)
        addUsage(t, stage, {
          input: u.input_tokens,
          output: u.output_tokens,
          cacheRead: u.cache_read_input_tokens,
          cacheWrite: u.cache_creation_input_tokens,
        })
    })
    return r
  })

  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    const a = e.agentId ? agents.get(e.agentId) : undefined
    await track($, t => a && addTime(t, a.stage, e.durationMs))
    if (a) a.since = undefined
    return r
  })

  on('tool.call', { tool: TOOL }, async $ => {
    await track($)
    const t = merge(empty(), await stored($, (await git($))?.key))
    const now = await $.clock.now()
    // The delivery agent calling this is still running: count it up to now.
    for (const a of agents.values()) if (a.since !== undefined) addTime(t, a.stage, now - a.since)
    return { result: t.ms || Object.keys(t.stages).length ? render(t) : NONE }
  }).catch(() => ({ result: NONE }))
}

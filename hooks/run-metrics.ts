import type { EngineInterface, Register } from 'claude-code'
import { addTime, addUsage, empty, merge, render, stageOf, type Totals } from './metrics'

const TOOL = 'mcp__shipit__run_metrics'

// shortcut: the live segment sits in module variables, so a hot reload mid-run
// loses it; move to $.state if mods get reloaded during real runs.
let segmentStart: number | undefined
let seg = empty()
const agents = new Map<string, { stage: string; openSince?: number }>()

// Earlier segments (pauses, resumes, other sessions) live in $.store per task branch.
async function branchKey($: EngineInterface) {
  const { exitCode, stdout } = await $.process.run(['git', 'branch', '--show-current'])
  const branch = stdout.trim()
  return exitCode === 0 && branch && !['main', 'master'].includes(branch) ? `run:${branch}` : undefined
}

async function stored($: EngineInterface, key: string | undefined) {
  return ((key && (await $.store.get(key))) as Totals | undefined) ?? empty()
}

async function live($: EngineInterface): Promise<Totals> {
  if (segmentStart === undefined) return empty()
  const now = await $.clock.now()
  const t = merge(empty(), seg)
  t.ms = now - segmentStart
  for (const a of agents.values()) if (a.openSince !== undefined) addTime(t, a.stage, now - a.openSince)
  return t
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

  on('skill.prompt', async ($, e, next) => {
    if (e.skill === 'shipit:run' && segmentStart === undefined) {
      segmentStart = await $.clock.now()
      seg = empty()
      agents.clear()
    }
    return next(e)
  })

  on('agent.spawn', async ($, e, next) => {
    const r = await next(e)
    if (segmentStart !== undefined && r.agentId)
      agents.set(r.agentId, { stage: stageOf(e.subagentType), openSince: await $.clock.now() })
    return r
  }).catch(($, e, next) => next(e)) // bookkeeping never blocks a spawn

  on('turn.start', async ($, e, next) => {
    const a = e.agentId ? agents.get(e.agentId) : undefined
    if (a) a.openSince = await $.clock.now()
    return next(e)
  })

  // Every model response, main loop and subagents alike, counted once here.
  on('turn.step', async function* ($, e, next) {
    const r = yield* next(e)
    if (segmentStart === undefined || !r.usage) return r
    const stage = e.agentId ? agents.get(e.agentId)?.stage : 'run'
    if (stage)
      addUsage(seg, stage, {
        input: r.usage.input_tokens,
        output: r.usage.output_tokens,
        cacheRead: r.usage.cache_read_input_tokens,
        cacheWrite: r.usage.cache_creation_input_tokens,
      })
    return r
  })

  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    if (segmentStart === undefined) return r
    const a = e.agentId ? agents.get(e.agentId) : undefined
    if (a) {
      addTime(seg, a.stage, e.durationMs)
      a.openSince = undefined
    } else if (!e.agentId) {
      // The coordinator's turn ended: the run paused or finished; bank the segment.
      const finished = await live($)
      segmentStart = undefined
      const key = await branchKey($)
      if (key) await $.store.set(key, merge(await stored($, key), finished))
    }
    return r
  })

  on('tool.call', { tool: TOOL }, async $ => {
    const key = await branchKey($)
    const t = merge(await stored($, key), await live($))
    return { result: t.ms || Object.keys(t.stages).length ? render(t) : 'No shipit run metrics recorded for this branch.' }
  }).catch(() => ({ result: 'No shipit run metrics recorded for this branch.' }))
}

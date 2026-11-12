import type { EngineInterface, Register } from 'claude-code'
import { addTime, addUsage, empty, merge, render, stageOf, type Totals, type Usage } from './metrics'

const TOOL = 'mcp__shipit__run_metrics'
const NONE = 'No shipit run metrics recorded for this branch.'

// The runs being counted, one per locked checkout (the session's own, or a card's
// worktree); totals are saved to $.store on every change, so a reload or another
// session only loses the step in flight.
const runs = new Map<string, { key: string; totals: Totals; at: number }>()
let session: { top: string; common: string; key?: string } | undefined
// Owner tokens of the locks this session's coordinator took, saved per session so a
// reload keeps them; another session's card is never counted here.
let mine: Set<string> | undefined
// `repo` is the checkout a subagent works for; absent when the spawn named none.
const agents = new Map<string, { stage: string; since?: number; repo?: string }>()

async function git($: EngineInterface, dir?: string) {
  const { exitCode, stdout } = await $.process.run([
    'git', ...(dir ? ['-C', dir] : []), 'rev-parse', '--path-format=absolute', '--show-toplevel', '--git-common-dir', '--abbrev-ref', 'HEAD',
  ])
  const [top = '', common = '', branch = ''] = stdout.trim().split('\n')
  return exitCode === 0 && top ? { top, common, key: branch && branch !== 'HEAD' ? `run:${top}:${branch}` : undefined } : undefined
}

// A run is working while run_state.py holds its checkout lock: from `begin` until it
// pauses (QA, a decision, a failure) or finishes. Each lock records its checkout as
// `repo`, so the session's checkout and every card worktree are told apart.
async function allLocks($: EngineInterface) {
  session ??= await git($)
  if (!session) return []
  const dir = `${session.common}/shipit/locks`
  const files = await $.fs.list(dir).catch(() => [])
  const locks: { repo: string; owner?: string }[] = []
  for (const f of files) {
    if (!f.name.startsWith('checkout-')) continue
    // A lock being written or released mid-read is not a run yet; read the rest.
    const lock = await $.fs.read(`${dir}/${f.name}`).then(t => JSON.parse(t) as { repo?: string; owner?: string }).catch(() => undefined)
    if (lock?.repo) locks.push({ repo: lock.repo, owner: lock.owner })
  }
  return locks
}

const ownersKey = async ($: EngineInterface) => `owners:${await $.session.id()}`
async function owners($: EngineInterface) {
  return (mine ??= new Set(((await $.store.get(await ownersKey($))) as string[] | undefined) ?? []))
}

// This session's runs: its own checkout's, and every card worktree its coordinator locked.
async function lockedRepos($: EngineInterface) {
  const own = await owners($)
  return (await allLocks($)).filter(l => l.repo === session?.top || (l.owner && own.has(l.owner))).map(l => l.repo)
}

async function stored($: EngineInterface, key: string | undefined) {
  return ((key && (await $.store.get(key))) as Totals | undefined) ?? empty()
}

// The checkouts a step counts for: the agent's own, else every run held, sharing it evenly.
const targets = (repo: string | undefined) => (repo ? (runs.has(repo) ? [repo] : []) : [...runs.keys()])

// Moves every run's time up to now, applies `change` and saves; outside a run it does nothing.
async function track($: EngineInterface, change: (t: Totals, share: number) => void = () => {}, repo?: string) {
  const held = await lockedRepos($)
  const now = await $.clock.now()
  for (const r of held) {
    if (runs.has(r)) continue
    const key = (await git($, r))?.key
    if (key) runs.set(r, { key, totals: await stored($, key), at: now })
  }
  const counted = targets(repo)
  for (const [r, run] of runs) {
    run.totals.ms += Math.max(0, now - run.at) // the step that released the lock counts too
    run.at = Math.max(run.at, now)
    if (counted.includes(r)) change(run.totals, 1 / counted.length)
    if (!held.includes(r)) runs.delete(r)
    await $.store.set(run.key, run.totals)
  }
}

const scaled = (u: Usage, share: number): Usage => ({
  input: u.input * share, output: u.output * share, cacheRead: u.cacheRead * share, cacheWrite: u.cacheWrite * share,
})

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const r = await next(e)
    await $.tool.register({
      name: 'run_metrics',
      description:
        'Total tokens and execution time of the current shipit:run task, with the breakdown per skill, as a markdown "Run metrics" section. Call it right before publishing the PR body.',
      inputSchema: {
        type: 'object',
        properties: {
          repo: { type: 'string', description: "Absolute path of the run's checkout (its card worktree). Omit to use the caller's own run." },
        },
      },
      isDeferred: false,
    })
    return r
  })

  // A lock that appears while this session runs the helper, and whose owner token the
  // helper printed back to this session (`begin` always does), is this session's run.
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    if (!e.command.includes('run_state.py')) return next(e)
    const before = new Set((await allLocks($).catch(() => [])).map(l => l.owner))
    const r = await next(e)
    const printed = JSON.stringify([r.result, r.text])
    const own = await owners($)
    for (const l of await allLocks($).catch(() => []))
      if (l.owner && !before.has(l.owner) && printed.includes(l.owner)) own.add(l.owner)
    await $.store.set(await ownersKey($), [...own])
    return r
  }).catch(($, e, next) => next(e)) // replays a command that already ran; never runs it twice

  on('agent.spawn', async ($, e, next) => {
    const r = await next(e)
    if (!r.agentId) return r
    // The coordinator names the card's checkout in every delegation; the longest match
    // keeps worktree `…/42` from claiming `…/424`. One run held → it is that one's.
    const held = await lockedRepos($)
    const named = held.filter(x => e.prompt.includes(x)).sort((a, b) => b.length - a.length)[0]
    const repo = named ?? (held.length === 1 ? held[0] : undefined)
    agents.set(r.agentId, { stage: stageOf(e.subagentType), since: await $.clock.now(), repo })
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
    const a = e.agentId ? agents.get(e.agentId) : undefined
    const stage = e.agentId ? a?.stage : 'run'
    const u = r.usage
    await track($, (t, share) => {
      if (stage && u)
        addUsage(t, stage, scaled({
          input: u.input_tokens,
          output: u.output_tokens,
          cacheRead: u.cache_read_input_tokens,
          cacheWrite: u.cache_creation_input_tokens,
        }, share))
    }, a?.repo)
    return r
  })

  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    const a = e.agentId ? agents.get(e.agentId) : undefined
    await track($, (t, share) => a && addTime(t, a.stage, e.durationMs * share), a?.repo)
    if (a) a.since = undefined
    return r
  })

  // The caller is the card's delivery agent: its checkout picks the run; the main loop reads the session's.
  on('tool.call', { tool: TOOL }, async ($, e) => {
    await track($)
    const caller = e.agentId ? agents.get(e.agentId) : undefined
    const asked = typeof e.repo === 'string' && e.repo ? e.repo.replace(/\/+$/, '') : undefined
    const repo = asked ?? caller?.repo ?? (runs.size === 1 ? [...runs.keys()][0] : undefined)
    const key = repo ? (await git($, repo))?.key : (session ??= await git($))?.key
    const saved = await stored($, key)
    // Nothing recorded for this run: no table, so delivery reports `run metrics: n/a`.
    if (!saved.ms && !Object.keys(saved.stages).length) return { result: NONE }
    const t = merge(empty(), saved)
    const now = await $.clock.now()
    // The delivery agent calling this is still running: count it up to now.
    for (const a of agents.values())
      if (a.since !== undefined && a.repo === repo) addTime(t, a.stage, now - a.since)
    return { result: render(t) }
  }).catch(() => ({ result: NONE }))
}

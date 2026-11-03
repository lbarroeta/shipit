// Pure accounting for a shipit:run: what each skill spent, merged across
// resumed segments and rendered as the PR's "Run metrics" section.

export type Usage = { input: number; output: number; cacheRead: number; cacheWrite: number }
export type Stage = { usage: Usage; ms: number }
export type Totals = { ms: number; stages: Record<string, Stage> }

// shipit's run-* subagents, by the skill each one executes.
export const STAGE_BY_AGENT: Record<string, string> = {
  'run-sync': 'sync',
  'run-planner': 'code-plan',
  'run-builder': 'code-implement',
  'run-reviewer': 'code-review',
  'run-delivery': 'code-handoff',
}
const ORDER = ['run', 'sync', 'code-plan', 'code-implement', 'code-review', 'code-handoff']

export const empty = (): Totals => ({ ms: 0, stages: {} })

export const stageOf = (subagentType: string) =>
  STAGE_BY_AGENT[subagentType.replace(/^.*:/, '')] ?? 'other'

const stage = (t: Totals, name: string): Stage =>
  (t.stages[name] ??= { usage: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }, ms: 0 })

export const addUsage = (t: Totals, name: string, u: Usage) => {
  const s = stage(t, name).usage
  s.input += u.input
  s.output += u.output
  s.cacheRead += u.cacheRead
  s.cacheWrite += u.cacheWrite
}

export const addTime = (t: Totals, name: string, ms: number) => {
  stage(t, name).ms += ms
}

export const merge = (a: Totals, b: Totals): Totals => {
  const out = empty()
  for (const t of [a, b]) {
    out.ms += t.ms
    for (const [name, s] of Object.entries(t.stages)) {
      addUsage(out, name, s.usage)
      addTime(out, name, s.ms)
    }
  }
  return out
}

const sum = (u: Usage) => u.input + u.output + u.cacheRead + u.cacheWrite
const n = (x: number) => String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, ',')

export const duration = (ms: number) => {
  const s = Math.max(0, Math.round(ms / 1000))
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const pad = (x: number) => String(x).padStart(2, '0')
  if (h) return `${h}h ${pad(m)}m ${pad(s % 60)}s`
  if (m) return `${m}m ${pad(s % 60)}s`
  return `${s}s`
}

export const render = (t: Totals): string => {
  const names = Object.keys(t.stages).sort(
    (a, b) => (ORDER.indexOf(a) + 1 || 99) - (ORDER.indexOf(b) + 1 || 99),
  )
  // The coordinator's own time is what its subagents did not spend.
  const childMs = names.filter(x => x !== 'run').reduce((acc, x) => acc + (t.stages[x]?.ms ?? 0), 0)
  const row = (label: string, u: Usage, ms: number) =>
    `| ${label} | ${duration(ms)} | ${n(u.input)} | ${n(u.output)} | ${n(u.cacheRead)} | ${n(u.cacheWrite)} | ${n(sum(u))} |`
  const all = empty()
  for (const s of Object.values(t.stages)) addUsage(all, 'total', s.usage)
  const totalUsage = stage(all, 'total').usage
  return [
    '## Run metrics',
    '',
    `Total: ${duration(t.ms)} · ${n(sum(totalUsage))} tokens`,
    '',
    '| Skill | Time | Input | Output | Cache read | Cache write | Total tokens |',
    '|---|---|---|---|---|---|---|',
    ...names.map(x =>
      row(x, t.stages[x]!.usage, x === 'run' ? Math.max(0, t.ms - childMs) : t.stages[x]!.ms),
    ),
    row('**Total**', totalUsage, t.ms),
  ].join('\n')
}

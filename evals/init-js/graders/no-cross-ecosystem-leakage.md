---
type: llm
weight: 1
---

# Grader: no cross-ecosystem leakage

shipit's skills were extracted from a Rails codebase. This case checks that none of
that survived into the plugin's behaviour.

## Pass requires all of

1. **Not one Ruby artefact appears anywhere in the output.** No `rspec`, `rubocop`,
   `brakeman`, `bundle`, `Gemfile`, `bin/rails`, `spec/`, `_spec.rb`, `undercover`.
2. **`package_manager` is `pnpm`,** decided by `pnpm-lock.yaml` — not npm or yarn by
   default.
3. **`tests.location` is `colocated`** and `tests.naming` is the real `*.test.ts`
   pattern. Not `mirrored`, not a `spec/` convention.
4. **`typecheck` is populated** (`tsc --noEmit` via the script). A Rails-shaped
   contract would leave this null because Ruby has no typecheck step.
5. **`security` and `coverage_gate` are `null`** and listed in `unknown[]`. This repo
   has neither. Inventing one — `npm audit`, a coverage threshold — is a failure.
6. **`ci.config` is `null`** and the report says commands came from `package.json`
   scripts, which is the correct next authority when no CI exists.
7. **`docs.agent_docs` is empty** and nothing claims a `CLAUDE.md` was consulted.
8. **`layers[]` is derived from real directories** in this repo, or is empty. It is
   never populated with `models`/`services`/`controllers` by assumption.

## Fail on any of

- Any Ruby or Rails term in `config.json`, `stack.md`, `conventions.md`, or the report.
- `tests.location: mirrored` when the prompt states tests sit beside their sources.
- A layer list that reads like a Rails app rather than this repo's tree.
- `security` filled with an invented command.
- A convention asserted without a `path:line`.
- npm or yarn chosen when the lockfile says pnpm.

## Notes for the judge

The prompt deliberately omits CI and agent docs — the two richest evidence sources —
to see whether the run falls back correctly or fills the gap from priors.

The correct output here is **smaller** than the Ruby case's: fewer commands, more
`unknown` entries, an empty `agent_docs`. A fuller contract is a worse one.

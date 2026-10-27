# Senior Stance

Read by `code-plan`, `code-implement`, `code-review` and `pr-fix`. It sets how the work is
thought through and how its code is shaped — stack judgement, tests, operability,
SOLID and Clean Code — not what gets built: scope stays with the plan and
`lean-ladder.md`.

## Whose senior

The stack is what `init` recorded: `stack.languages`, `stack.frameworks` and
`tests.framework` in `.shipit/config.json`, with versions from `.shipit/stack.md`.
Think as a senior engineer who has shipped and maintained production code in exactly
that stack, at those versions. Never re-detect the stack here. Several languages or
frameworks → the stance of the one the touched files belong to. `stack` empty →
general senior judgement, and one line in the report saying the stack is unknown.

## Precedence

1. The repo contract: `.shipit/conventions.md`, `.shipit/rules/*`, cited analogues.
2. The framework's idiom at the installed version.
3. General engineering judgement.

A repo convention beats a framework idiom, even where you would write it
differently. The one exception is a convention that would introduce a security or
data-loss defect in this change: flag it — `Blockers` or `Assumptions` in the plan,
`Known Risks or Follow-ups` in the report — never follow it or deviate silently.

## What a senior in this stack does

- **Uses what the framework already provides** — validations, scopes, transactions,
  migration helpers, middleware, hooks, dependency injection, i18n — before writing
  their own. A hand-rolled framework feature is a defect, not a style.
- **Writes the language's idiom** as the repo already uses it: naming, error
  handling (exceptions or result values), nullability, immutability, async model,
  typing.
- **Knows the stack's failure modes and checks the ones the change touches.**
  Examples: N+1 queries and missing indexes behind an ORM; migrations that lock or
  backfill large tables, or add a non-null column without a default; background jobs
  that are not idempotent under retry; external side effects inside a transaction;
  read-modify-write races; cache invalidation; mass assignment; stale closures,
  effect dependencies and list keys in React; hydration mismatches; blocking the
  event loop; leaked goroutines; timezones; money as floats. Only those the change
  actually reaches — this is judgement, not a checklist to recite.
- **Is version-aware.** No API newer than the installed version; no deprecated API
  when the installed version ships its replacement. Unsure while writing code →
  `docs-lookup.md`.
- **Tests the way § Tests below says**, at the level the stack's practice and
  `.shipit/rules/tests/*` expect, with the repo's own factories and fixtures.

## Tests

The repo's test rules decide framework, kinds and layout; these decide quality.

- **Behaviour, not implementation.** Assert what a caller or user observes through
  the public surface. No assertions on private methods or internal calls unless
  that call is the contract (an email sent, a job enqueued).
- **One behaviour per test**, named for the behaviour and its condition.
- **Fails for the right reason.** The red seen before the fix is the expected
  assertion, not a setup error or a typo.
- **Deterministic.** No real clock, randomness, network or test-order dependence:
  freeze or inject time, seed randomness, stub external services at the boundary
  the repo already stubs. Never `sleep` or retry to make a test pass.
- **Isolated.** Each test builds its own data and leaves no shared state behind.
- **Fast.** The lowest level that proves the behaviour — unit before request,
  request before system or browser. The least data that proves it: in-memory over
  persisted records, no database when the logic needs none, no large fixture loads,
  no real external calls. Browser and system tests only for the critical flows the
  plan names. A slow test is a cost every run of CI pays.
- **Scoped runs only.** Run the test files this change writes and the ones covering
  the files it changes — never the full suite; CI owns it
  (`code-implement/references/validation-standards.md` § The full suite belongs to CI).
- **Edge cases covered.** Each `Failure paths` row in the plan is proved by a test
  or a QA scenario.
- **Never weakened.** No skipped tests, loosened assertions or deleted cases to get
  green.

## Operability

The code must survive production, not only the test run. Apply what the change
reaches:

- **Observability.** A new failure path leaves a trace with the repo's logging,
  error-tracking and metrics tools, with enough context to debug (ids, not
  payloads) and no personal data, secrets or tokens. Errors are never swallowed.
- **Performance.** No unbounded query, loop or list: paginate or batch what can
  grow; no query per item; indexes for new lookups; mind complexity on hot paths
  and large inputs; expensive work moves where the repo already puts it (jobs,
  caches) only when the plan says so.
- **Resilience.** Every external call has a timeout. Retries only with backoff and
  only on idempotent operations, or with an idempotency key. A partial failure
  leaves data consistent — transaction, compensation or a safe retry.

## Design principles

SOLID and Clean Code, applied to the code this change creates or modifies — never
as a reason to rework code it does not touch.

- **Single responsibility.** Each new class, module or function has one reason to
  change. New behaviour goes where its responsibility already lives; it is not
  piled onto an unrelated class because that class is nearby. A touched unit that
  would take on a second responsibility → place the new one beside it.
- **Open/closed.** Extend through the extension points the code already has —
  polymorphism, registries, callbacks, configuration the repo uses — rather than
  adding another branch to a growing conditional. No such point and only one or two
  cases → the plain conditional; build the extension point when a third case is real.
- **Liskov substitution.** A subclass or implementation honours its parent's
  contract: same inputs accepted, same guarantees, no surprise exceptions or
  no-op overrides.
- **Interface segregation.** Callers depend on the narrow surface they use. Do not
  widen a shared interface for one caller.
- **Dependency inversion.** Inject or pass collaborators that cross a boundary
  (I/O, external services, clock, randomness) the way the repo already does, so the
  unit is testable. An interface with a single implementation is still `yagni:`.
- **Clean Code.** Names that say intent in the domain's language; small functions
  at one level of abstraction; guard clauses over nested conditionals; no boolean
  flag arguments selecting behaviour; no magic numbers or strings the repo would
  name; commands and queries kept apart, with no hidden side effects; errors
  handled explicitly, never swallowed; duplication removed at the third occurrence,
  not the second. Leave each line you touch cleaner than you found it — only the
  lines you touch.

When a principle and the ladder disagree, the ladder wins: less code that is clear
beats a textbook structure. When a principle and a repo convention disagree, the
convention wins (see Precedence).

## Per skill

- **`code-plan`**: the stance drives discovery and decisions — which consumers to
  verify, which failure modes become a `Decisions` entry, an AC validation or a
  `Notes` risk; the test level each `Tests` row needs; the operability needs the
  change creates. The design principles decide where each responsibility lives in the
  `Files` table: which unit owns the new behaviour, which existing extension point
  it uses, which collaborator is injected. Any new class or module still passes the
  scope gate. Record the decision ("backfill in a separate migration", "eager-load
  `X` in `Y`", "new `RefundPolicy` instead of growing `OrdersController`"), not the
  code.
- **`code-implement`**: the stance and the design principles drive how each planned
  change is written — naming, function size, error handling, dependencies. A stack
  risk or design problem the plan missed is fixed only when it stays inside the
  plan's files and acceptance criteria and adds no new abstraction; otherwise it
  goes under `Known Risks or Follow-ups`.

## What it is not

- Not licence to refactor, upgrade, or add the pattern or abstraction "a senior
  would add" — SOLID included. The ladder still gates every addition.
- Not prose. No explaining idioms in the plan, the report or code comments.

# Validation Standards

Every command comes from `.sdd/config.json` `commands.*`. Never invent one, never
substitute a sibling you happen to know, never run a command the contract does not
carry.

## The chain

Run in order. Stop at the first failure, fix, then resume from that step — not from
the top.

| Step | Key | Skip when |
| --- | --- | --- |
| 1 | `test_one` on each test written | null, or has no `{path}` |
| 2 | `test_one` on the test files covering each changed file | same |
| 3 | `test_all` | **by default — see below** |
| 4 | `lint` | null |
| 5 | `typecheck` | null |
| 6 | `security` | null |
| 7 | `coverage_gate` | null |

A `null` key is skipped **silently** — the repo does not have that step, and saying
"skipped" for every absent key is noise. A key present in `unknown[]` is different:
report it once, because the contract could not determine it and coverage of that
dimension is genuinely missing.

## The full suite belongs to CI

Step 3 does not run by default. Steps 1 and 2 are the gate: the tests written this
run, plus the test files covering every file in the report's `Files Changed`. That
is the blast radius a local run can actually reason about. The whole suite is CI's
job, and re-running it here buys minutes of wall clock to re-prove code this change
never touched.

Run `test_all` only when one of these is true, and say which one:

- `test_one` is null or has no `{path}` — the scoped loop is unavailable, so the
  suite is the only way to run anything. Report the loop as degraded.
- The plan explicitly asks for it (a shared-fixture change, a global config or
  initializer edit, a rename that crosses the whole suite).
- Step 1 or 2 turned up a failure whose cause is plausibly repo-wide.

Not covered by any of those → the report line is
`test_all → not run (CI owns the full suite)`. That is a complete answer, not a gap,
and it never blocks `code-handoff`.

Two things this does not relax: `coverage_gate` still runs when it is configured,
even if the repo's gate command drives the suite itself — red coverage blocks the
merge, so it is worth the wall clock. And a failing scoped test is still a hard
stop; scoping down is about what gets *proved*, never about what gets *ignored*.

## Placeholders

Substitute at call time:

- `{path}` → the test file being run.
- `{base}` → `repo.default_branch`.

Never bake a branch name or a path into a stored command.

## Reporting

One line per command actually run:

```
<command as executed> → exit <code>
```

Rules:

- The command as executed, with placeholders already substituted. A reader must be
  able to paste it.
- Exit code, always. Not "passed".
- Non-zero → include the relevant failure output, not the whole log.
- A command you did not run does not get a line claiming it passed.

## Contract drift

A command that fails **because it does not exist** — binary not found, script
missing, task not defined — is not a code failure. It means `.sdd/config.json` has
drifted from the repo since `init` ran.

Say exactly that:

```
<command> → exit 127 (not found)
CONTRACT DRIFT: config.json names a command that no longer exists here.
Re-run /shipit:init to refresh the contract.
```

Do not improvise a replacement command. Do not mark the step green. Do not silently
skip it.

This distinction matters because the two failures need opposite responses: a real
failure means fix the code, drift means fix the contract.

## The three-attempt rule

Three attempts at the same failing check, with no new evidence between them, and
you stop. New evidence means a different error, a narrower reproduction, or a fact
you did not have — not a new guess.

On stopping, report: the command, the exact output, the three things tried, and
what evidence would unblock it.

Repeating a failing command hoping for a different result burns tokens and produces
nothing.

## Coverage gates

The most common cause of red CI on otherwise correct work. `tests.coverage_gates_merge`
true → treat `coverage_gate` as mandatory, not advisory.

- Uncovered changed lines are fixed with **tests for the changed behaviour**.
- Never with an exclusion, a threshold change, or a config edit.
- Never by deleting the uncovered code unless the plan says to.

## What "green" means

All of:

- Every non-null command in the chain ran, except `test_all` when it was correctly
  skipped per the rule above.
- Every one exited 0.
- No test was deleted, skipped, or weakened to get there.
- No exclusion was added to a lint, security, or coverage config.

Anything less is not green, and `code-handoff` is not invoked. Report and stop.

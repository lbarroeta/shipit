# Validation Standards

Every command comes from `.shipit/config.json` `commands.*`. Never invent one, never
substitute a sibling you happen to know, never run a command the contract does not
carry.

## The chain

Run in order after all planned code, test and doc edits. Stop at the first failure,
fix, then resume from the earliest check affected by the fix. Reuse earlier results
only when their inputs and dependencies are unchanged. This includes changes made
by formatters, lint fixes or later documentation edits. Before handoff, confirm
the results still apply to the final files; rerun affected checks after any drift.

| Step | Key | Skip when |
| --- | --- | --- |
| 1 | `test_one` on each test written | null, or has no `{path}` |
| 2 | `test_one` on the test files covering each changed file | same |
| 3 | `test_all` | **by default — see below** |
| 4 | `lint` | null |
| 5 | `typecheck` | null |
| 6 | `build` | null, or no relevant build impact — see below |
| 7 | `security` | null |
| 8 | `coverage_gate` | null |

A `null` key unrelated to required validation is skipped **silently**. A key
present in `unknown[]` is undetermined, not verified absent: report it once with
its effect on this change. A missing or unknown command needed to prove the plan
is a required validation gap, handled below; never treat it as an optional skip.

## Acceptance evidence

Use the plan's AC links, `Tests` and `Manual QA`, including already-met criteria,
affected consumers and regressions. Preserve their observable expected results.
The plan supplies validation intent; this skill selects and executes configured
commands. In the existing report sections, attach AC IDs to test evidence or
manual/external scenarios rather than duplicating the plan in another matrix.

- Required automated checks need actual execution. If no configured command can
  run them (including when both `test_one` and `test_all` are unavailable), stop
  with `Implementation Blocked` or `Implementation Incomplete` as applicable.
  Name the affected AC/check and the missing command or evidence. Request the
  needed clarification or `/shipit:sync`; never invent a command or
  replace planned tests with manual QA to get green.
- Human/external QA planned for review may remain pending through handoff. Keep
  its scenario, AC, executor, prerequisites and expected result in the report and
  PR; state whether it is ready to run or blocked. A check the plan requires before
  delivery must be completed before handoff. Missing timing that determines
  delivery readiness is a plan gap, returned to the planner for correction.
- No planned automated tests is valid when the plan's acceptance has another
  suitable verification path. Report what was actually checked and what remains
  pending; zero available commands alone is never evidence of acceptance.
  Coordinated runs must also satisfy their executed-command checkpoint; if no
  configured check can satisfy it, return the gap without fabricating evidence.

## Build

Run configured `build` when the change affects compiled output, bundling,
packaging, or their inputs/configuration, including UI changes on that build path,
or when the plan's validation intent requires it. Tests, lint and typechecking do
not establish build success. No relevant build impact → skip with a brief reason
when the command is configured. Required build verification with no usable command
is a validation gap under Acceptance evidence.

## The full suite belongs to CI

Step 3 does not run by default. Where automated coverage applies, steps 1 and 2
cover tests written this run and affected behavior, including the plan's consumers
and regressions. Use `Files Changed` to check the final scope. The whole suite is
CI's job unless one of the conditions below requires it locally.

Run `test_all` only when one of these is true, and say which one:

- Automated tests are required and `test_one` is null or has no `{path}` — the
  scoped loop is unavailable. Use configured `test_all` and report the loop as
  degraded; if it is unavailable too, report the validation gap.
- The plan's validation intent requires suite-wide regression coverage (a
  shared-fixture change, a global config or initializer edit, a rename that crosses
  the whole suite). The plan need not name the command.
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
- Distinguish expected TDD red and repaired failures from final results. Keep
  their actual exits; link the successful rerun instead of rewriting history.
- Preserve manual/external checks, including backend checks: AC, expected and
  observed result/evidence, or pending executor/prerequisite. Developer-only steps
  belong here; non-developer steps belong in QA. Missing required verification
  remains a blocker, not a follow-up hidden under risks.

## Contract drift

A command that fails **because it does not exist** — binary not found, script
missing, task not defined — is not a code failure. It means `.shipit/config.json` has
drifted from the repo since `init` ran.

Say exactly that:

```
<command> → exit 127 (not found)
CONTRACT DRIFT: config.json names a command that no longer exists here.
Run /shipit:sync to reconcile the contract.
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

- Every applicable non-null command in the chain ran, except `test_all` and
  `build` when correctly skipped under their rules above.
- Every required command's final execution exited 0 and still covers the final
  files; expected TDD red and repaired failures are not final failures.
- Each AC and planned regression retains its executed evidence or explicitly
  pending review QA. No required automated or pre-delivery verification is missing.
- Required manual pre-delivery checks passed, and no known acceptance or
  regression failure remains, including failures found during review QA.
- No test was deleted, skipped, or weakened to get there.
- No exclusion was added to a lint, security, or coverage config.

Anything less is not green, and `code-handoff` is not invoked. Report and stop.
Green permits handoff for review; it does not mean pending human/external QA passed.

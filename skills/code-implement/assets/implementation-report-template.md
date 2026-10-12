# Implementation Report — <ISSUE-ID> <title>

## QA Handoff

Worktree: `<path>` · Branch: `<branch>` · Base: `<base>`
Environment to test in: `<url or local instructions>`
Log in as: `<role, and how to get an account with it>`
Setup data needed: `<what must exist before testing, or "none">`

<If backend only: `Backend only. Manual UI QA not applicable.` plus one line on
what developer validation covered. Preserve any planned manual/external checks:
non-developer checks below, technical checks in Validation. Delete the next
section only when there are no non-developer checks.>

QA status: <pending, passed or failed, from actual evidence. Pending: executor,
and ready to run or blocked with the missing environment/account/data. Human QA
passes only on explicit human results. Omit when no manual/external QA applies.>

## QA Steps For Non-Developer

<The one section written in full, always, however terse the rest of the run is.>

No framework names. No class, file, or function names. No terminal commands. If a
step cannot be described without one of those, it belongs in Validation instead.

Preserve the plan's scenarios and AC IDs, including backend checks in external
services. Pending steps describe expected results, never results already observed.

1. <AC ID: action a person takes in the browser or external service>
   - Expected: <what they should see>
2. <action>
   - Expected: <what they should see>

Screenshots needed: <which screens, or "none">

If a step fails: <what to write down — the page, what appeared instead, any
message shown on screen>

## Plan

`<path to the plan file>`

## Summary

<2 sentences, 3 when the change is genuinely novel. What changed and why, for
someone reviewing the PR cold. Not a walk through the files — the table below and
the diff already carry those.>

## Files Changed

This table is the manifest `code-handoff` stages from. A path missing here does not get
committed; a path here that is not in the diff stops the handoff.
Generated plans stay in the `Plan` section, never in this table, regardless of
`sdd_tracking`. Coordinated run results separately retain their full ownership
manifest for validation.

| Path | Action | What |
| --- | --- | --- |
| `<path>` | Added \| Modified \| Deleted | <change> |

## Tests Added/Updated

| Test | Rule | Proves |
| --- | --- | --- |
| `<path>` | `.sdd/rules/tests/<kind>.md` | <AC IDs/regression and behaviour> |

## Validation Commands Run

Exact commands, placeholders substituted, with exit codes. Tie results to the
plan's ACs/regressions, including tests of already-met behavior. Distinguish TDD
red or repaired failures from final reruns; final evidence must cover final files.

```
<command> → exit 0
<command> → exit 0
```

<Record configured test_all/build skips with reasons. Omit unrelated null keys.>
<Unknown verification keys, when present: key, effect on this change, and next
action if required. Missing required validation blocks handoff.>

<For each developer-only manual/external check: AC, executor, prerequisites,
steps, expected result, and observed evidence or pending status. Preserve backend
checks. Pending review QA may follow handoff; required pre-delivery checks may not.
Non-developer scenarios live in QA above; reference them rather than repeat them.>

Design checks: <each `<paths.rules>/design.md` § Verify item — met, not met, or not
checked, and how it was seen. Delete for backend-only work or with no design
contract.>

## Security Notes

One line per item that applies. A line that would read "n/a" is dropped, not written.

- New entry points and what authorizes each: <…>
- Scoping enforced on new records or queries: <…>
- Input validated, and where the boundary is: <…>
- Deliberately left open: <…>

<`None — checked entry points, scoping, and input.` is a complete answer when true.
Valid after checking, not by default.>

## Handoff

<Appended verbatim by `code-handoff` after it runs. Leave empty until then. Never
summarize what handoff did; paste what it reported.>

## Known Risks or Follow-ups

One line each: the risk, and what would trigger acting on it. Nothing to report →
`None.` Do not pad this with restated risks from the plan.

- <risk, and what would trigger acting on it>

Debt markers written this run:

| File:line | Ceiling | Upgrade trigger |
| --- | --- | --- |
| `<path:line>` | <the limit accepted> | <what should prompt revisiting> |

<A marker with no upgrade trigger should not have been written. If one exists, fix
the comment now.>

## PR Preparation

<Title and body from `assets/pr-description-template.md`, including its section
drops and visible-summary/detail split. Full QA and validation above remain the
evidence; do not copy this report's structure into the body. Written here, checked
against final evidence by `sync`, then put on the PR by `code-handoff` — never
posted from this skill.>

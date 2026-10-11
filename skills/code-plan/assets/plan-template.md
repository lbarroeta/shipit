# <ISSUE-ID> <title>

Source: <tracker url | user request> · <YYYY-MM-DD>

## Worktree

Path: `<worktree path>` · Branch: `<branch>` · Base: `<base>`

<Delete this whole section when no worktree was used — the default. Keep it only
when `worktree.enabled` is true and one was created or reused.>

## Goal

<1-2 sentences. Current intended result and why it still matters; preserve the
task Goal and boundaries after checking relevance and live prerequisites.>

## Baseline

<Checkout/root, branch and exact HEAD (or non-Git limitation). Relevant staged/
unstaged/untracked changes and what the plan relies on; unrelated dirty work
excluded. Request/accepted-decision sources and applicable rule paths. Rechecked
before finalizing; description is not permission to overwrite dirty work.>

## Out of scope

- <work explicitly not done here>
- skipped: <what the scope gate rejected>, add when <the trigger>

## Acceptance criteria

- [ ] <AC ID from source when present>: <testable behaviour>

## Readiness

<Concise evidence of current relevance and satisfied prerequisites. Include IDs
and observable unblock evidence when prerequisites exist; no duplicated ticket
body. Required when planning a tracker issue or a draft with dependencies.>

## Estimate

<S | M | L> — <the single biggest driver of uncertainty>

## Evidence

<Current behavior and scope-bearing relationships, verified at `path:line` and
symbols. State graph-assisted/source-only discovery and material freshness or
coverage gaps. Keep only findings needed to justify this plan.>

## Decisions

<Essential choices with accepted source/evidence. Reference controlling repo
rules rather than restating them. Explain required exceptions to reuse or local
patterns. Delete when no additional decision needs recording.>

- <decision>: <why>. Rejected: <alternative + why not>.

## Files

| Path | Action | What | Analogue |
| --- | --- | --- | --- |
| `<path>` | Create | <symbol, expected behavior, AC IDs> | `<path:line>` |
| `<path>` | Edit | <symbol/section, behavior change, AC IDs> | — |

## Sequence

<Only actual dependencies between named file/symbol groups and why that order is
required. Delete for independent edits; test command/red-green loops belong to
implement.>

## Notes

<Only what the implementer would get wrong by guessing: parameter shapes, scoping,
state transitions, response shape, empty/error states, ordering between layers.
Skip anything the analogue already demonstrates. Record worktree collisions and
the decision taken.>

## Design

<Only when UI is touched and `<paths.rules>/design.md` exists. Names, never restates:
values and rule text stay in `.sdd/`. Delete this section otherwise.>

Surface · pattern: <surface> · <pattern from `design-system.md` § Screen patterns>

| Need | Use | Source |
| --- | --- | --- |
| <list, form, action, feedback> | `<Component>` variant `<v>` | `<path:line>` |
| <need met by a rarely used component> | `<Component>` | `<path:line>` · § Not cataloged |
| <piece nothing covers> | Create `<path>` | exception — see `Decisions` |

States: <the `<paths.rules>/design.md` § 4 states this change renders>

## Tests

| Test | Rule | Proves |
| --- | --- | --- |
| `<path>` + <scenario> | `.sdd/rules/tests/<kind>.md` | <AC IDs/regression and observable expected result> |

<Each AC links through Files (or Evidence for already-met behavior) to Tests or
Manual QA. Include affected consumers and negative paths when relevant.>

## Docs impact

<Which docs this change makes stale, and the exact section to update. Delete this
section when none.>

- `<doc path>` § <section> — <what changes>

## Manual QA

<Required for UI: browser path, role/setup, actions and expected results with AC
IDs, no framework names or terminal commands. Also use for required backend
manual/external checks, with limitations. Delete when not applicable.>

## Assumptions

<Only bounded nonessential defaults: evidence, impact and revisit condition.
Delete this section if empty.>

## Blockers

<Only when the plan cannot proceed: exact missing decision/evidence, affected AC,
question/options and supported recommendation or next evidence needed. Mark the
artifact blocked; dependent Files/Tests/Sequence may remain incomplete. Delete
when there are none.>

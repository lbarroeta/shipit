# <ISSUE-ID> <title>

Source: <tracker url | user request> · <YYYY-MM-DD>

## Worktree

Path: `<worktree path>` · Branch: `<branch>` · Base: `<base>`

<Delete this whole section when no worktree was used — the default. Keep it only
when `worktree.enabled` is true and one was created or reused.>

## Goal

<1-2 sentences. What changes for the user or the system.>

## Out of scope

- <work explicitly not done here>
- skipped: <what the scope gate rejected>, add when <the trigger>

## Acceptance criteria

- [ ] <testable behaviour>

## Estimate

<S | M | L> — <the single biggest driver of uncertainty>

## Decisions

<Only decisions NOT derivable from `.sdd/*` or an agent doc. If a repo rule
already dictates it, omit it. Delete this section when nothing was decided.>

- <decision>: <why>. Rejected: <alternative + why not>.

## Files

| Path | Action | What | Analogue |
| --- | --- | --- | --- |
| `<path>` | Create | <purpose> | `<path:line>` |
| `<path>` | Edit | <change> | — |

## Notes

<Only what the implementer would get wrong by guessing: parameter shapes, scoping,
state transitions, response shape, empty/error states, ordering between layers.
Skip anything the analogue already demonstrates. Record worktree collisions and
the decision taken.>

## Design

<Only when UI is touched and `.sdd/rules/design.md` exists. Names, never restates:
values and rule text stay in `.sdd/`. Delete this section otherwise.>

Surface · pattern: <surface> · <pattern from `design-system.md` § Screen patterns>

| Need | Use | Source |
| --- | --- | --- |
| <list, form, action, feedback> | `<Component>` variant `<v>` | `<path:line>` |
| <piece nothing covers> | Create `<path>` | exception — see `Decisions` |

States: <the `rules/design.md` § 4 states this change renders>

## Tests

| Test | Rule | Proves |
| --- | --- | --- |
| `<path>` | `.sdd/rules/tests/<kind>.md` | <behaviour> |

## Docs impact

<Which docs this change makes stale, and the exact section to update. Delete this
section when none.>

- `<doc path>` § <section> — <what changes>

## Manual QA

<Required only for UI changes: the browser path in plain language, no framework
names, no terminal commands. Delete this section for backend-only work.>

## Assumptions

<Only real ones, with the default taken. Delete this section if empty.>

## Blockers

<Only when the plan cannot proceed. A blocker carries a recommendation. Delete
this section when there are none — and when it is present, nothing below the
`Files` table is expected to be complete.>

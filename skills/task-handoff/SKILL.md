---
name: task-handoff
description: Use when an authorized `task-create` draft must be published to the tracker — creating its issue, or an epic's parent and children with their hierarchy and dependency relations — only when `handoff.allow` in `.shipit/config.json` lists `issue_create`. Runs after `task-create`. No git, no branch, no PR. Do not use to write tickets (`task-create`) or to deliver code (`code-handoff`).
metadata:
  writes_product_code: false
---

# shipit task-handoff

Publishes a `task-create` draft to the tracker. `task-create` writes and authorizes
the draft; this skill creates the issues it describes. No git at all — a ticket
exists before a branch does. Code delivery (branch, commit, push, PR) is
`code-handoff`.

`task-create` invokes it only when `issue_create` is allowed; the user may also run
`/shipit:task-handoff <draft path>` by hand. Being invoked either way changes
nothing: run the same preflight, and trust the draft for **content** only — never
for whether issues already exist. Check the `## Created` ledger and the tracker.

## Permissions

Read `handoff.allow` from `.shipit/config.json`. **Absent → `["branch", "commit",
"push", "pr_body", "pr_ready", "tracker_status"]`**, which does not include
`issue_create`.

- **Requires `issue_create`.** Not listed → do nothing: the draft on disk is the
  deliverable and the user creates the issues. Say that in one line and stop. Report
  it as `skipped (not in handoff.allow)` — never as `blocked`, never silently.
- **Never widen `allow`.** A capability that is not listed is a decision already
  made. Never patch `.shipit/config.json` yourself; drift → suggest `/shipit:sync`.
- `allow` grants permission; it never creates capability. Adapter `none` is still
  `n/a (adapter: none)`.
- No tracker comment and no status transition, whatever `allow` says. The body
  already carries everything; new work is not a transition.

## Context budget

- Required: `.shipit/config.json` (`tracker`, `handoff.allow`, `language`) and the
  draft at `<paths.tasks>/<slug>.md`.
- Required when `issue_create` is listed: `../code-handoff/references/tracker-writes.md`
  — its `Universal rules`, `Publishing contract` and the configured adapter's
  `### Create` subsection only. The other adapters are noise.
- Never read product code, plans or the diff.

## Hard rules

- **Write nothing but the ledger.** The `## Created` block of the draft being
  delivered is appended to with the ids that were created: append created IDs
  immediately and update pending markers after read-back. A narrowly scoped
  exception also replaces local relationship placeholders in created issue bodies
  with real IDs/URLs; no content rewriting. Never edit any other part of the draft.
- **Authorization is `task-create`'s.** Input is a draft already confirmed by the
  user; this skill does not ask again. A user running it by hand on a draft is that
  authorization.
- **Prose language.** Created issues follow `language.task`; what this skill prints
  follows `language.plan`. Legacy string `language` → that value; absent → `en`.
  Identifiers stay English.
- **Enumerate, never hardcode.** States, issue types, teams, labels and fields are
  matched by name from the tracker; never invent fields, issue types or label schemes.
- Never close, edit, merge or comment on existing issues.
- Never fake success. Tracker unavailable → `blocked` or `partial` with the exact
  failing call. Never claim an issue exists unless a call returned it.

## Preflight

1. Read `handoff.allow`. `issue_create` absent → stop here and say so; that is not a
   failure.
2. Confirm the draft exists on disk.
3. `tracker.create.supported` false, adapter `none`, or the adapter's mechanism
   unavailable → create nothing and report `n/a (adapter: none)` or
   `blocked: <the missing capability>`. The draft stays on disk and stays valid.
4. Any check fails → stop and report what is missing. Produce **no** partial side
   effects.

## Publish

- **Readiness** — unresolved essential `Blockers` prevent publishing. Defined
  tasks with known unmet Dependencies may be created as blocked backlog work;
  never advance them to active work. Inspect relation capabilities before writing.
- **Create** — one issue for a single draft. For an epic, create the parent and
  each complete `Child #n` section as an issue; the `Subtasks` table is an index,
  never the child's body. Promote child headings to normal issue headings; omit
  template instructions, the index, siblings and the draft-only `Created` ledger.
  Keep Problem, Goal, scope, exclusions, AC IDs, QA/validation and dependency
  conditions verbatim. Replace local relationship references with returned IDs
  once available; preserve their semantics and intended direction.
  Parent usually comes first; a provider's explicit text-only task-list fallback
  may need children first. Use actual supported hierarchy/blocking capabilities
  from `tracker-writes.md`. Type, priority, size and labels use existing native
  concepts/options.
- **Relations** — hierarchy and dependency links are separate writes, authorized
  as part of `issue_create`. Suggested order is prose or an existing ordering
  field, never a fabricated blocker. After endpoints exist, reconcile native
  relations and read them back. Missing write capability → retain clear body
  references and report unsupported/manual; a reference is not a native link.
- **Idempotency** — read the draft's `## Created` block first and skip every entry
  already listed — except its `pending:` fields/relations, retried on the existing
  issue and dropped from the line once verified. Also read existing native
  relations before creating missing ones; a partial retry must finish relations
  even when both endpoint issues already exist. `dependency:<reference>` uses a
  stable local child number or external prerequisite ID/URL from Dependencies;
  resolve local numbers through Created and external references through live
  tracker reads. Never create a referenced external prerequisite as a new issue.
  Re-running on a delivered draft creates nothing. This is what
  makes retrying a partial delivery safe rather than duplicating a backlog.
- **Record** — append each created issue to `## Created` as
  `- #<local n or "parent"> — <ISSUE-ID> — <url>`, immediately after each creation,
  not in one batch at the end. A crash between two creations must still leave the
  ledger true. A field or relation write that fails after creation appends
  `— pending: <priority|size|parent|dependency:<reference>>` to that line;
  an unsupported/unmapped value is not pending,
  since a retry cannot fix a field the tracker does not have.
- **Partial failure** — child 3 of 5 fails: the two already created stay recorded,
  the report is `partial`, and it names the exact failing call. Never delete a
  created issue to "clean up" — say what exists and that a re-run creates only the
  rest.
- **Status** — new work lands in the configured unstarted state. For defined
  blocked tasks, use an enumerated blocked/backlog equivalent and preserve the
  unmet condition; never create directly into active work just because config
  names that state. Report any required correction or missing valid initial
  state. Jira may need its adapter's initial-state transition; nothing has
  started, and this initialization needs no `tracker_status`.

## Report

One line per side effect, each marked `completed`, `partial`, or `blocked`, with the
exact reason for anything short of completed. No preamble, no recap of the ticket:

- The effective `handoff.allow`, once, as the first line.
- Issues created, one line per issue: local number, id, url. Plus the ones skipped
  as already present in `## Created`.
- Priority/size fields: set, `unmapped`, or `pending`.
- Hierarchy/dependency relations: verified native, pending failed write, or
  unsupported/manual with exact endpoints. Text references are reported separately.
- Initial status of each issue, and any correction needed.

`issue_create` withheld → one line: `issue creation: skipped (not in handoff.allow)`,
then that the draft is the deliverable for the user to create by hand.

This report is appended verbatim to the caller's report. Write it so it survives
being pasted without edits.

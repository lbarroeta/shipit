---
name: handoff
description: Use when shipit artifacts must be delivered — branch, commit, push, ready-for-review PRs and tracker review status by default; tracker comments, review-thread replies and issue creation only when `handoff.allow` in `.sdd/config.json` opts into them. Runs after `task`, `plan`, `implement`, or `pr-fix`. Do not use to write plans, tickets, or product code.
metadata:
  writes_product_code: false
---

# shipit handoff

Owns delivery side effects; `task`, `implement` and `pr-fix` produce artifacts.
`plan` also owns the startup transition to `In Progress`, including inside `run`.
This skill delivers their artifacts.

**What it may do is configuration, not judgement.** `handoff.allow` in
`.sdd/config.json` lists the permitted side effects. Its default is git and the PR
body, PR readiness and tracker review status. Tracker comments, review-thread
replies and issue creation are opt-in. See **Permissions** below
before doing anything.

Four modes: `task` (after a ticket draft is written), `plan` (after a plan is
written), `implementation` (after a change is verified), `review` (after PR feedback
is resolved). Ask which one when it is not given and the branch does not make it
obvious.

By default, `implement` invokes this skill once validation is green, passing its
report. With `--defer-handoff`, the `run` coordinator delegates it separately.
`task` invokes it only when `issue_create` is allowed. `pr-fix` never does — the
user runs `/shipit:handoff` by hand after reviewing the fixes. Being invoked either
way changes nothing: run the same preflight, and trust the report for **content**
only — never for whether delivery side effects already happened. Check actual
state before performing them.

## Permissions

Read `handoff.allow` from `.sdd/config.json`. **Absent → `["branch", "commit",
"push", "pr_body", "pr_ready", "tracker_status"]`**, which is also what a repo
gets from `/shipit:init`. Existing explicit allow-lists remain authoritative.

| Entry | Unlocks |
| --- | --- |
| `branch` | creating or switching to the delivery branch |
| `commit` | staging and committing the manifest |
| `push` | pushing the branch |
| `pr_body` | creating a ready-for-review PR, and replacing its body |
| `pr_ready` | marking an existing draft PR ready for review |
| `tracker_comment` | one comment per mode, per `references/tracker-writes.md` |
| `tracker_status` | the mode's status transition |
| `thread_replies` | replying to and resolving review threads in `review` mode |
| `issue_create` | `task` mode: creating the issues a draft describes |

Rules:

- **A step whose capability is not listed does not happen.** Report that line as
  `skipped (not in handoff.allow)` — never as `blocked`, never silently.
- **Read `references/tracker-writes.md` only when `tracker_comment`,
  `tracker_status` or `issue_create` is listed.** Read its status rules on the
  default `allow`; skip comment/creation sections unless enabled.
- An unknown entry is ignored: report the drift and suggest `/shipit:init`. Never
  patch `.sdd/config.json` yourself.
- `allow` present but empty, or a mode left with no permitted step, → do nothing and
  say which capability the run needed. Half a handoff is worse than none.
- `allow` grants permission; it never creates capability. `tracker_comment` with
  adapter `none` is still `n/a (adapter: none)`.

## Context budget

- Required: `.sdd/config.json` (for `tracker` and `repo`), and the report or plan
  being delivered.
- Required: `references/tracker-adapters.md` — only the section for the configured
  adapter. It covers branch naming and PR issue-linking, which are always allowed.
- Conditional: `references/tracker-writes.md`, and only when `handoff.allow` lists
  `tracker_comment`, `tracker_status` or `issue_create`. `issue_create` also needs
  that file's `### Create` subsection; the other capabilities do not.
- Optional: `references/worktree-lifecycle.md` when the branch lives in a worktree.
- Never read the product diff to decide content. The report is the manifest.

## Hard rules

- Never write product code. Never edit a plan. Delivery only. **One exception, in
  `task` mode only:** the `## Created` block of the draft being delivered is
  appended to with the ids that were created. Append-only, that block only.
- **Check `handoff.allow` before every side effect**, not once at the start. A run
  where `push` is allowed and `pr_body` is not pushes and stops there.
- **Never widen `allow`.** Not for a run the user "clearly wants", not because a
  reply is one API call away. A capability that is not listed is a decision already
  made. Say what was skipped and let them change the config.
- **A tracker write is not free.** With `tracker_comment` allowed, a comment carries
  the QA steps and the PR link — nothing else. No summary, no validation result, no
  file list. `tracker-writes.md` owns the content; do not improvise it.
- Never move a tracker issue backwards, and read its current status before any
  transition. `tracker-writes.md` lists the terminal states per adapter.
- **Prose language.** PR title, PR body and review-thread replies follow `language.pr`; tracker comments and created issues follow `language.task`; what this skill prints follows `language.plan` in `.sdd/config.json`. Legacy string `language` → that value for every key but `code`; absent → `en`. Identifiers, commit subjects and branch names always stay English.
- **Stage by explicit path.** Never `git add -A`, never `git add .`.
- **Never stage or commit generated plans**, regardless of `sdd_tracking` or
  `handoff.allow`. Exclude the supplied plan, the report's `Plan` path and any
  archived run-owned plans from the delivery manifest; keep their local files.
  Before committing, verify none is staged. If one is already staged, stop and
  name it without changing the user's index. An empty filtered manifest skips the
  commit; never make an empty commit to deliver a plan.
- **`sdd_tracking: local` excludes every `.sdd/*` path from staging**, in every
  mode, even when the report's `Files Changed` lists one. Drop it from the manifest
  and note it in the report as informational — never as an error or a stop
  condition.
- `plan` mode stages nothing. `implementation` and `review` modes use the
  report's `Files Changed`, minus excluded artifacts, as the manifest: every
  staged path must appear there **and** in the current diff. A listed path absent
  from the diff, or an intended
  path in the diff missing from the manifest, stops the handoff.
- A dirty worktree with unrelated user changes blocks the commit unless the shipit
  artifacts isolate cleanly. Stop and report. Never stash, reset, or checkout over
  user work.
- Never fake success. Host unavailable → report `blocked` or `partial` with the
  exact failing call. Never a summary that implies it worked.
- Never merge. Never push to the default branch. Never force-push.
- Never remove a worktree. That is `/shipit:status --prune`.
- **One line per side effect.** This skill reports what it did, never what the
  change was — the report it was handed already said that, and a PR body is not
  improved by a second telling. Copy sections from the report verbatim or leave
  them out; never expand them.

## Preflight — all modes

`task` mode runs steps 1, 5 and 6 only. It touches no branch and no remote, so the
rest has nothing to check.

1. Read `handoff.allow`. Nothing this mode needs is listed → stop here and say so;
   that is not a failure.
2. `git status`, current branch, remote. `gh auth status` when the host is GitHub.
3. In `plan` and `implementation` modes, verify required tracker status access
   when `tracker_status` is allowed and an issue is identified. Adapter `none`
   or no linked issue → status `n/a`.
   Read `sdd_tracking` from `.sdd/config.json` (absent → `committed`). Local →
   no path under `.sdd/` is ever staged, in any mode; see Hard rules.
4. Confirm which checkout you are in. The main checkout is the default and is fine.
   Only when the plan names a worktree must you be in it — see
   `references/worktree-lifecycle.md`.
5. Confirm the artifacts to deliver exist on disk.
6. Any check fails → stop and report what is missing. Produce **no** partial side
   effects. Half a handoff is worse than none.

## Mode: task

**Requires `issue_create`.** Not listed → do nothing: the draft on disk is the
deliverable and the user creates the issues. Say that in one line and stop.

Input: a `task` draft at `<paths.tasks>/<slug>.md`, already confirmed by the user.
`task` asks; this skill does not ask again. No git in this mode at all — a ticket
exists before a branch does.

- **Create** — one issue for a `task` draft. For an `epic` draft, the parent and one
  issue per `Subtasks` row, linked by the adapter's parent field, **in the order
  that adapter's `### Create` specifies** — most want the parent first, GitHub needs
  the children first. Title, body, labels, priority and size come from the draft
  **verbatim** — never re-worded, never expanded with a section the draft did not
  have. The draft's type maps to the adapter's issue type, story type, or existing
  label; no mapping available → say the type went unmapped, never invent a label.
  Priority and size map to the tracker's own fields per the adapter's `### Create`
  table, the same way: matched by name, never created, unmapped said out loud.
- **Idempotency** — read the draft's `## Created` block first and skip every entry
  already listed — except its `pending:` fields, which are retried on the existing
  issue and dropped from the line once set. Re-running on a delivered draft creates nothing. This is what
  makes retrying a partial delivery safe rather than duplicating a backlog.
- **Record** — append each created issue to `## Created` as
  `- #<local n or "parent"> — <ISSUE-ID> — <url>`, immediately after each creation,
  not in one batch at the end. A crash between two creations must still leave the
  ledger true. A priority or size write that fails after creation appends
  `— pending: <priority|size>` to that line; an unmapped value is not pending,
  since a retry cannot fix a field the tracker does not have.
- **Partial failure** — child 3 of 5 fails: the two already created stay recorded,
  the report is `partial`, and it names the exact failing call. Never delete a
  created issue to "clean up" — say what exists and that a re-run creates only the
  rest.
- **Status** — new issues land in `tracker.create.initial_state`. No transition
  afterwards: nothing has started, and this needs no `tracker_status`.
- **Comment** — none, whatever `allow` says. The body already carries everything.
- **Blocked** — `tracker.create.supported` false, adapter `none`, or the adapter's
  mechanism unavailable → create nothing and report `n/a (adapter: none)` or
  `blocked: <the missing capability>`. The draft stays on disk and stays valid.

## Mode: plan

- **Branch** — from the tracker adapter when it supplies one; otherwise the repo's
  branch convention from `.sdd/conventions.md`; otherwise
  `<user>/<issue-id>-<slug>`. Never invent a prefix. Usually `plan` already created
  it with the worktree; verify rather than re-create.
- **Commit** — `skipped (generated plan stays local)` in every tracking mode.
- **Push** — only existing commits on the task branch; no plan or empty commit.
- **PR** — Ready for review. Create without `--draft`. Title
  `<ISSUE-ID> Plan: <short title>`. Body states this is
  planning only and execution belongs to `/shipit:implement`. Always carry the
  plan's content verbatim (Goal, Acceptance, Files, Notes) in the body.
  Update an existing PR when available. No commits ahead of the base and no
  existing PR → skip PR creation and report the local plan path; do not create a
  dummy commit to open a planning PR.
- **Tracker comment** — `tracker_comment` only: the plan comment from
  `references/tracker-writes.md`.
- **Ready for review** — `pr_ready` only: convert an existing draft and verify
  readiness, as in implementation mode. Already ready → no write.
- **Status** — `tracker_status` only: after publishing and verifying a ready PR,
  move the linked issue to `In Review` per `references/tracker-writes.md`. No PR
  delivered → skip the transition and preserve the planning status.

## Mode: implementation

- **Commit** — the report's `Files Changed`, excluding generated plans and any
  other artifacts excluded by the hard rules.
- **Push** — normally.
- **PR** — replace the plan PR's body on this branch with the report's
  `PR Preparation` body verbatim. Verbatim means no re-wording, no added preamble,
  and no re-adding a section the template dropped. Create a new PR only when none
  exists, ready for review and without `--draft`.
- **Ready for review** — `pr_ready` only: convert an existing draft with
  `gh pr ready` (or the PR host equivalent). Already ready → no write. Verify
  actual readiness before the tracker transition. When withheld, preserve the
  existing PR state and report the skipped conversion.
- **Tracker comment** — `tracker_comment` only: the QA steps **copied verbatim**
  and the PR link. Nothing else — no summary, no validation result, no file list.
  The QA steps were written for a non-developer, so they are the one part never
  shortened. **No QA steps in the report → no comment.** Not allowed → the steps
  stay in the report for the user to post.
- **Status** — `tracker_status` only: after the delivered PR is verified ready
  for review, move the linked issue to `In Review` (or its unambiguous review
  equivalent) and read it back. Already in review, QA-ready or terminal → preserve
  the state. A draft PR or failed delivery never advances the card; an unavailable
  or ambiguous transition is partial delivery, not completion.

### Coordinated run and retry

When `shipit:run` supplies a run state and delivery journal, read them before
preflight and every effect. `../run/references/orchestration.md § Delivery
reconciliation` owns that protocol. Verify the saved validation still covers the
current file contents; stop on drift. Record each successful effect immediately,
including its exact proof, and skip effects confirmed in both journal and actual
repo/remote/tracker state. A previously committed manifest is verified against the
saved/reconciled commit instead of required to appear in the working diff. This
exception applies only to proven effects of this run; unrelated commits do not
satisfy it. If reconciliation is ambiguous, stop without repeating the write.

Save the handoff report separately under the supplied run directory. Keep the
checkpointed builder report immutable; the coordinator links both reports rather
than appending to it. Standalone callers retain the append behavior below.

## Mode: review

Input: the `pr-fix` report — item table, `Files Changed`, validation results,
pushback justifications.

- **Commit** — the report's `Files Changed` after artifact exclusions. Same
  manifest rule. An
  empty `Files Changed` is valid here: a run of `resolved`, `pushback` or `question`
  items touches no code. Then there is nothing to deliver — say so and stop.
- **Push** — normally, to the PR's existing branch.
- **PR** — never create one; a missing PR is a preflight failure. Update the body
  only when the report supplies a new one. The draft state is untouched unless
  `pr_ready` is allowed.
- **Thread replies** — `thread_replies` only. Then, per item in the report's table:
  - `fix` → reply on the thread with one line (what changed, in which file), then
    resolve the thread. On GitHub: `gh api graphql` with the `resolveReviewThread`
    mutation, thread id from `pullRequest.reviewThreads`.
  - `resolved` → reply with the report's one-line reason, then resolve the thread.
  - `pushback` → reply with the justification **verbatim** from the report. Do
    **not** resolve. The decision is human.
  - `question` → reply with the question verbatim. Do **not** resolve.
  Not allowed → every reply stays in the report as text, and the report names how
  many threads are waiting on the user.
- **Tracker** — none in this mode, whatever `allow` says. The thread replies, or the
  report the user is holding, are the record; a per-item fix summary on the ticket
  is a second telling of what the PR already shows. Report it as
  `n/a (review mode)`.
- **Status** — none. The issue is already in review or later.

## Report

One line per side effect, each marked `completed`, `partial`, or `blocked`, with the
exact reason for anything short of completed. No preamble, no summary paragraph, no
recap of the change — a `completed` line needs no explanation:

- The effective `handoff.allow`, once, as the first line. A reader who cannot see
  the config cannot otherwise tell a skipped step from a forgotten one.
- Issues created — `task` mode, one line per issue: local number, id, url. Plus the
  ones skipped as already present in `## Created`.
- Branch.
- Commit hash, and the files staged — plus generated plans and any `.sdd/*` path
  excluded because tracking is local.
- Push.
- PR url, and whether the body was created or replaced; whether it is still a draft.
- Review thread replies and resolutions — `review` mode, one line per thread.
- Tracker comment, and tracker status transition.
- Worktree and preflight issues encountered.

Every capability the mode would have used but `allow` withheld gets its own line:
`skipped (not in handoff.allow)`. Then one closing line naming what is therefore
left for the user — post the QA steps, reply to and resolve the threads, move the
ticket, mark the PR ready. Name them; never do them anyway.

This report is appended verbatim to the caller's report. Write it so it survives
being pasted without edits.

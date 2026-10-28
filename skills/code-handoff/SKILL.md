---
name: code-handoff
description: Use when shipit artifacts must be delivered — branch, commit, push, ready-for-review PRs and tracker review status by default; tracker comments, review-thread replies and issue creation only when `handoff.allow` in `.shipit/config.json` opts into them. Runs after `task-create`, `code-plan`, final `sync`, or `pr-fix`. Do not use to write plans, tickets, or product code.
metadata:
  writes_product_code: false
---

# shipit code-handoff

Owns delivery side effects; `task-create`, `code-implement` and `pr-fix` produce artifacts.
`code-plan` also owns the startup transition to `In Progress`, including inside `run`.
This skill delivers their artifacts.

**What it may do is configuration, not judgement.** `handoff.allow` in
`.shipit/config.json` lists the permitted side effects. Its default is git and the PR
body, PR readiness and tracker review status. Tracker comments, review-thread
replies and issue creation are opt-in. See **Permissions** below
before doing anything.

Four modes: `task` (after a ticket draft is written), `plan` (after a plan is
written), `implementation` (after a change is verified), `review` (after PR feedback
is resolved). Ask which one when it is not given and the branch does not make it
obvious.

Implementation delivery follows `code-implement → sync → code-handoff`. Receive
the final sync delivery report plus original implementation evidence. The `run`
coordinator delegates delivery only after `sync_after`; standalone users invoke
it explicitly after sync. Context drift or pending required checks return to sync
or implementation before any delivery effect.
`task-create` invokes it only when `issue_create` is allowed. `pr-fix` never does — the
user runs `/shipit:code-handoff` by hand after reviewing the fixes. Being invoked either
way changes nothing: run the same preflight, and trust the report for **content**
only — never for whether delivery side effects already happened. Check actual
state before performing them.

## Permissions

Read `handoff.allow` from `.shipit/config.json`. **Absent → `["branch", "commit",
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
| `evidence_pr` | `implementation` mode: pushing QA screenshots to the evidence branch and one PR comment with the acceptance evidence |
| `evidence_tracker` | `implementation` mode: pushing QA screenshots to the evidence branch and one tracker comment with the same evidence |

Rules:

- **A step whose capability is not listed does not happen.** Report that line as
  `skipped (not in handoff.allow)` — never as `blocked`, never silently.
- **Read `references/tracker-writes.md` only when `tracker_comment`,
  `tracker_status` or `issue_create` is listed.** Read its status rules on the
  default `allow`; skip comment/creation sections unless enabled.
- An unknown entry is ignored: report the drift and suggest `/shipit:sync`. Never
  patch `.shipit/config.json` yourself.
- `allow` present but empty, or a mode left with no permitted step, → do nothing and
  say which capability the run needed. Half a handoff is worse than none.
- `allow` grants permission; it never creates capability. `tracker_comment` with
  adapter `none` is still `n/a (adapter: none)`.

## Context budget

- Required: `.shipit/config.json` (for `tracker` and `repo`), and the report or plan
  being delivered.
- Required: `references/tracker-adapters.md` — only the section for the configured
  adapter. It covers branch naming and PR issue-linking, which are always allowed.
- Conditional: `references/tracker-writes.md`, and only when `handoff.allow` lists
  `tracker_comment`, `tracker_status` or `issue_create`. `issue_create` also needs
  that file's `### Create` subsection; the other capabilities do not.
- Optional: `references/worktree-lifecycle.md` when the branch lives in a worktree.
- When publishing a PR body: `../code-implement/assets/pr-description-template.md`
  for the description check below.
- Conditional: the `code-qa` acceptance report and its evidence directory, only when
  `evidence_pr` or `evidence_tracker` is listed and the caller supplies them.
- Never read the product diff to decide content. The report is the manifest.

## Hard rules

- Never write product code. Never edit a plan. Delivery only. **One exception, in
  `task` mode only:** the `## Created` block of the draft being delivered is
  appended to with the ids that were created. That block only: append created IDs immediately and update pending markers
  after read-back. A narrowly scoped exception also replaces local relationship
  placeholders in created issue bodies with real IDs/URLs; no content rewriting.
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
- **Prose language.** PR title, PR body and review-thread replies follow `language.pr`; tracker comments and created issues follow `language.task`; what this skill prints follows `language.plan` in `.shipit/config.json`. Legacy string `language` → that value for every key but `code`; absent → `en`. Identifiers, commit subjects and branch names always stay English.
- **Stage by explicit path.** Never `git add -A`, never `git add .`.
- **Never stage or commit generated plans or graph outputs**, regardless of
  `handoff.allow`. Exclude the supplied plan, the report's `Plan` path, any
  archived run-owned plans and the graph output directory (`graph.out` in
  `.shipit/config.json`, `graphify-out/` when `graph` is null) from the delivery
  manifest; keep their local files. Before committing, verify none is staged. If
  one is already staged, stop and name it without changing the user's index. An
  empty filtered manifest skips the commit; never make an empty commit to deliver
  a plan.
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
  improved by a second telling. Publish prepared implementation/review bodies
  verbatim; never expand them. Plan-mode bodies follow the summary/full-plan rule
  below.

## Preflight — all modes

`task` mode runs steps 1, 5 and 7 only. It touches no branch and no remote, so the
rest has nothing to check.

1. Read `handoff.allow`. Nothing this mode needs is listed → stop here and say so;
   that is not a failure.
2. `git status`, current branch, remote. `gh auth status` when the host is GitHub.
3. In `plan` and `implementation` modes, verify required tracker status access
   when `tracker_status` is allowed and an issue is identified. Adapter `none`
   or no linked issue → status `n/a`.
4. Confirm which checkout you are in. The main checkout is the default and is fine.
   Only when the plan names a worktree must you be in it — see
   `references/worktree-lifecycle.md`.
5. Confirm the artifacts to deliver exist on disk.
6. When `pr_body` is allowed and a body will be published, check the prepared body
   before delivery effects. It must explain the problem and resulting behavior,
   summarize final validation, keep material risks/prerequisites/pending checks
   visible, and retain complete applicable QA inline, in details or at a verified
   team-accessible link. Reject unsupported claims, report dumps, generic filler
   and inaccessible evidence links. Apply the template's relevance guidance;
   its word target alone is not a failure. In plan mode use the plan-body rule
   below instead of claiming implementation or validation has happened.
   Return a deficient implementation/review body to its producer through the
   caller with specific corrections, before commit/push. Do not rewrite it or
   inspect the product diff to fill missing facts. No replacement body in review
   mode → no description check or body write.
7. Any check fails → stop and report what is missing. Produce **no** partial side
   effects. Half a handoff is worse than none.

## Mode: task

**Requires `issue_create`.** Not listed → do nothing: the draft on disk is the
deliverable and the user creates the issues. Say that in one line and stop.

Input: a `task-create` draft at `<paths.tasks>/<slug>.md`, already confirmed by the user.
`task-create` obtains authorization; this skill does not ask again. No git in this mode at all — a ticket
exists before a branch does.

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
  concepts/options; never invent fields, issue types or label schemes.
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
- **Comment** — none, whatever `allow` says. The body already carries everything.
- **Blocked** — `tracker.create.supported` false, adapter `none`, or the adapter's
  mechanism unavailable → create nothing and report `n/a (adapter: none)` or
  `blocked: <the missing capability>`. The draft stays on disk and stays valid.

## Mode: plan

- **Branch** — from the tracker adapter when it supplies one; otherwise the repo's
  branch convention from `.shipit/conventions.md`; otherwise
  `<user>/<issue-id>-<slug>`. Never invent a prefix. Usually `code-plan` already created
  it with the worktree; verify rather than re-create.
- **Commit** — `skipped (generated plan stays local)`.
- **Push** — only existing commits on the task branch; no plan or empty commit.
- **PR** — Ready for review. Create without `--draft`. Title
  `<ISSUE-ID> Plan: <short title>`. Body states this is
  planning only and execution belongs to `/shipit:code-implement`. Lead with a
  short problem/proposed-outcome summary and review-relevant decisions, open
  questions and prerequisites. Label validation as planned, not executed. Keep
  the complete plan verbatim in a collapsed `Full plan` details block, including
  evidence, baseline, decisions and validation coverage. Never use a local path
  as the reviewer-accessible plan or expand the entire plan above the fold.
  Prepare and check this body during preflight, before delivery effects.
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

- **Commit** — the report's `Files Changed`, excluding generated plans, graph
  outputs and any other artifacts excluded by the hard rules.
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
- **Evidence** — `evidence_pr` or `evidence_tracker`, after the PR exists, and
  only with an acceptance report. `gh repo view --json visibility` not `PRIVATE` or
  `INTERNAL` → publish nothing: the evidence branch would expose screenshots for
  good; report `withheld (public repo)`. Otherwise publish its evidence directory with
  `scripts/publish_evidence.py --repo <repo> --remote <repo.remote> --branch
  <acceptance.evidence_branch or shipit-evidence> --prefix <ISSUE-ID>/<run id>
  --dir <evidence dir>`. It commits through a temporary index and pushes only that
  branch, never the checkout. `evidence_pr` → comment once on the PR with the
  report's `## Evidence` section verbatim, each bare filename replaced by
  `<repo web URL>/blob/<commit>/<path>?raw=true`. `evidence_tracker` → the same
  body once on the linked issue, plus the PR link. A comment already in the
  journal is not posted again. No acceptance report → `n/a (no acceptance stage)`.
  Withheld → the screenshots stay in the run directory and the report says where.
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
checkpointed builder and final sync reports immutable; the coordinator links
all reports rather than appending to them. Standalone callers retain the append behavior below.

## Mode: review

Input: the `pr-fix` report — item table, `Files Changed`, validation results,
pushback justifications.

- **Commit** — the report's `Files Changed` after artifact exclusions. Same
  manifest rule. An
  empty `Files Changed` is valid here: a run of `resolved`, `invalid`, `pushback` or
  `question` items touches no code. Then there is nothing to deliver — say so and stop.
- **Push** — normally, to the PR's existing branch.
- **PR** — never create one; a missing PR is a preflight failure. Update the body
  only when the report supplies a new one. The draft state is untouched unless
  `pr_ready` is allowed.
- **Thread replies** — `thread_replies` only. Then, per item in the report's table:
  - `fix` → reply on the thread with one line (what changed, in which file), then
    resolve the thread. On GitHub: `gh api graphql` with the `resolveReviewThread`
    mutation, thread id from `pullRequest.reviewThreads`.
  - `resolved` → reply with the report's one-line reason, then resolve the thread.
  - `pushback` or `invalid` → reply with the justification **verbatim** from the
    report. Do **not** resolve. The decision is human.
  - `question` → reply with the question verbatim. Do **not** resolve.
  - `external`, `pending`, `conflict` → no thread; nothing to post.
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
- Hierarchy/dependency relations: verified native, pending failed write, or
  unsupported/manual with exact endpoints. Text references are reported separately.
- Branch.
- Commit hash, and the files staged — plus the generated plans and graph outputs excluded.
- Push.
- PR url, and whether the body was created or replaced; whether it is still a draft.
- Review thread replies and resolutions — `review` mode, one line per thread.
- Evidence branch commit, PR evidence comment and tracker evidence comment.
- Tracker comment, and tracker status transition.
- Worktree and preflight issues encountered.

Every capability the mode would have used but `allow` withheld gets its own line:
`skipped (not in handoff.allow)`. Then one closing line naming what is therefore
left for the user — post the QA steps, reply to and resolve the threads, move the
ticket, mark the PR ready. Name them; never do them anyway.

This report is appended verbatim to the caller's report. Write it so it survives
being pasted without edits.

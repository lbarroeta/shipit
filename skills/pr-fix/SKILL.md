---
name: pr-fix
description: Use when an open pull request has review comments, red CI or merge conflicts. Triages each item as a senior engineer in the detected stack — which comments apply, which do not and why, the proposed fix per red check, and whether the PR can merge — then stops for approval before any edit. Scope with `--comments` or `--ci`. Scope-change requests become pushback, not code. Do not use to plan, and not to commit, push or reply — the user runs `code-handoff` for that.
model: claude-opus-5-5
effort: high
metadata:
  input: open-pr-feedback
  output: fix-change
  writes_product_code: true
---

# shipit pr-fix

Triage review comments, red CI and merge conflicts on an open PR, the way the senior
engineer who owns this stack would: say which comments apply, which do not and why,
what each red check needs, and whether the PR can merge. Nothing is fixed until the
user approves; then one minimal fix per approved item. No scope expansion. This
skill never delivers: it leaves the fixes in the working tree and a report on
screen. Commit, push and the thread replies are `/shipit:code-handoff` in `review`
mode — run by the user, and each step only as far as `handoff.allow` permits. With
`thread_replies` withheld, the replies stay text in the report for the user to post.

## Context budget

- Required: `.shipit/config.json`, the PR's unresolved review threads, its CI
  status and its merge state.
- Required: `../../references/senior-stance.md` and
  `../../references/lean-ladder.md`, relative to this skill directory — the stance
  every verdict is judged with, and the pushback tag vocabulary.
- Required: the `.shipit/rules/*` files for the layers an item touches. Only
  those.
- Source beyond the threads: the code each item points at, its callers, callees and
  tests. A graph query before `rg` when `graph` is set and its output is present.
- `../../references/docs-lookup.md` only when one of its triggers fires — a fix
  that calls a library API no cited analogue shows at the installed version, a
  comment that claims an API behaves a certain way, or a red check on an unknown
  method, signature or deprecation.
- Never bulk-load rules or docs. A three-line fix does not justify reading the
  layer's whole rule set.

## Scope

- `--comments` → review threads only. Skip intake step 3 and the CI rows.
- `--ci` → CI only. Skip intake step 2 and the comment rows.
- Neither → both.
- Merge state is always reported: it comes from intake step 1.
- Empty table after filtering and the PR mergeable → report "nothing to fix" and
  stop.

## Intake — read-only, allowed

`tracker.adapter` is irrelevant here; the PR host is what matters. With `gh`
available:

1. `gh pr view <n> --json number,title,state,headRefName,baseRefName,url,mergeable,mergeStateStatus`
   — the PR exists, is open, and matches the current branch.
2. Unresolved threads: `gh api graphql` on `pullRequest.reviewThreads` filtered to
   `isResolved: false`, with `isOutdated`. Thread state not needed →
   `gh api repos/{owner}/{repo}/pulls/{n}/comments`.
3. CI: `gh pr checks <n>`, then `gh run view <run-id> --log-failed` for each failing
   job's exact output. A check gates the merge when it is in `ci.required_jobs`; that
   list empty → `gh pr checks <n> --required` decides. Read-only — local
   reproduction happens after the gate.
4. Merge: `mergeable` `CONFLICTING` or `mergeStateStatus` `DIRTY` → `git fetch
   origin <baseRefName>`, then `git merge-tree --write-tree --name-only HEAD
   origin/<baseRefName>` lists the conflicting files without touching the working
   tree. `BEHIND` → behind the base, no conflict. `UNKNOWN` → GitHub is still
   computing; say so, never guess.

No `gh` → ask the user to paste the review comments and the failing output. Do not
guess what a reviewer said.

## Judge each item

Before a row gets an action, check it against the code as the PR head has it:

- Read the lines the thread or failure points at, then the code they touch —
  callers, callees, tests. A comment about one line can be right or wrong because of
  a caller three files away.
- Judge with `senior-stance.md`: the stack from `.shipit/config.json`, the repo
  contract before the framework idiom, the framework idiom before taste.
- Every verdict carries a concrete case. `fix`: the input or situation that breaks
  today. `invalid`: the line that proves the concern cannot happen, or the rule the
  suggestion would break. No case either way → `question`.
- A red check: name the root cause from the log — this PR's change, a test that was
  already red on `<baseRefName>`, or an external cause (flaky infrastructure,
  missing secrets, a runner problem). Only the first is this PR's to fix.

## The item table

This drives the whole run. Build it before any edit.

| id | type (comment\|ci\|merge) | file | what it asks | action |
| --- | --- | --- | --- | --- |

Actions:

- `fix` — the comment holds or the failure is this PR's. Smallest fix proposed.
- `resolved` — needs **no code**: already fixed by another commit, outdated, or a
  nitpick being accepted-and-closed. One-line reason for the reply. It is not a way
  to dismiss a valid comment.
- `invalid` — the comment does not hold for this code. The concrete case, and a
  one-line reply for the user to post.
- `pushback` — a scope or design change. One-line technical justification.
- `question` — not understood, or needs a product decision. The exact question.
- `external` — CI red for a cause outside this PR. Reported, never fixed here.
- `pending` — a check still running. Not judged; say which.
- `conflict` — a merge conflict. Files and what each side changed; the user
  resolves it with a merge or rebase from `<baseRefName>` before handoff.

### Approval gate — every mode

The triage report below is output **before any edit or any local test run**, and the
run stops there for the user's go-ahead. Do not touch code, and do not start
reproducing, until they answer. They may override any action — including "resolve
it, don't fix it" on a thread, or "skip this one" on a failure.

CI rows name the **failing spec or example** and its file, plus the failure's first
line verbatim. One row per failing test, not one per job — a job with nine red
examples is nine rows. Group under the job name when the list is long, but never
collapse it to a count. Required checks before optional ones.

```markdown
# PR Triage — #<n> <title>

What this PR does: <two or three sentences>
Mergeable: <yes | no — conflicts in `<path>`, … | behind `<base>` | unknown, GitHub still computing>
CI: <green | <n> required red, <n> optional red, <n> pending>

## Applies
1. **<short title>** (`<path:line>` — <reviewer> | `<job>` › `<spec>`)
   - **Asks:** <the thread's ask, or the failure's first line verbatim>
   - **Why it applies:** <the concrete case that breaks today>
   - **Proposed fix:** <smallest fix; not applied>
   - **If we skip it:** <what happens>

## Does not apply
2. **<short title>** (`<path:line>` — <reviewer>)
   - **Asks:** <ask>
   - **Why not:** <the line or rule that proves it>
   - **Draft reply:** "<one line>"

## Pushback
## Questions
## Already resolved
## CI outside this PR
## Merge conflicts
- `<path>` — <what each side changed>.

Verdict: apply 1, 3 and 6. Mergeable after that: <yes | no, why>.
```

Number items across all groups, so the user can say "fix 1 and 3". Drop empty
groups. Very simple language: short sentences, a technical term explained the first
time it appears.

## Hard rules

- Minimal fix per item. No broad refactor, no new scope, no "while I'm here".
- **Prose language.** Comments written in code follow `language.code` (default `en`); drafted thread replies follow `language.pr`; the reports follow `language.plan` in `.shipit/config.json`. Legacy string `language` → that value for every key but `code`; absent → `en`. Identifiers, commit subjects and branch names always stay English.
- A comment requesting a **scope or design change is not implemented.** Mark it
  `pushback` with a one-line technical justification for the user to post. Use the
  ladder's tags where they fit — `yagni:` for an abstraction with one
  implementation, `native:` for a dependency the platform already covers. The
  decision stays human.
- A comment is never `invalid` on taste. It needs the concrete case.
- A comment you do not understand is a `question`, not a guess.
- Never weaken or delete a test to make CI green. A red coverage gate is fixed with
  coverage, never with an exclusion.
- No fake validation. "Passed" only when the command ran and exited 0.
- No more than 3 attempts on the same failure without new evidence.
- Never resolve a merge conflict here: it needs a merge or rebase commit.
- Never run `git commit`, `git push`, `git merge`, `git rebase`, or a PR command —
  the user runs `code-handoff` for that. Never post a thread reply, resolve a
  thread, or write to the tracker from here, whatever `handoff.allow` permits: this
  skill has no side effects outside the working tree. Replies live in the report as
  text.

## Workflow

1. **Preflight.** Current branch matches the PR's `headRefName`. `git status` clean
   of changes you did not make. PR open. Wrong branch → stop and ask; never
   force-switch over user work. If the PR's branch lives in a worktree, work there.
2. **Triage.** Intake, judge each item, build the item table, output the triage
   report, stop for approval; resume with the user's actions.
3. **Per item.** Only approved `fix` items get an edit; every other action carries
   its reason or question to the report. For each: reproduce with
   `commands.test_one` (CI items) → confirm the expected red → minimal fix →
   targeted test green → next item. One item at a time; batching fixes makes it
   impossible to say which change resolved which thread.
4. **Validate.** The full chain from
   `../code-implement/references/validation-standards.md`, relative to this skill
   directory — same order, same reporting, same contract-drift rule. Exact
   commands and exit codes.
5. **Report.** The item table with a resolution per row, pushback and invalid
   replies verbatim, a `Files Changed` manifest, and validation results.
6. **Hand back.** Never invoke `code-handoff`, and never commit or push. End with the
   report and one line naming what is left for the user: resolve any `conflict`
   rows, then run `/shipit:code-handoff` in `review` mode to commit and push — and to
   post the replies too, if `handoff.allow` lists `thread_replies`; otherwise those
   are theirs to post.
7. **Graph sync.** `graph` set, product code changed, and you are in the **main
   checkout** → run `<graph.update>`. In a worktree, skip and say so.

## User change protection

Uncommitted changes are user-owned unless this run made them. Stop before editing
when a required file has changes you did not make, when existing changes make a fix
ambiguous, or when a fix would revert user work. Report the conflicting paths and
the decision needed. Unrelated user changes: leave them and proceed.

## Blocker conditions

- A comment is ambiguous and needs a product decision → list the exact question.
- CI is red for an external cause — flaky infrastructure, missing secrets, a runner
  problem. Report it. Never "fix" it with blind retries.
- User changes conflict with a required fix.
- The same check failed 3 times without new evidence.

`# Fix Blocked` when no product code changed yet, `# Fix Incomplete` when it did:

```markdown
# Fix <Blocked | Incomplete>

## Problem
<Concrete issue.>

## Item(s) affected
<Rows from the item table.>

## Recommended next step
<Smallest correction, or the decision needed.>

## Files inspected
- <path>
```

Include the exact failing output when the stop came from repeated failures.

## Final output

At the gate: the triage report, nothing else.

After the fixes, in this order: Item Table with a resolution per row · Mergeable ·
Summary · Files Changed · Tests Added/Updated · Validation Commands Run (exact +
exit code) · Replies (verbatim, one per `pushback`, `invalid`, `question` and
`resolved` thread, for the user to post) · Next step.

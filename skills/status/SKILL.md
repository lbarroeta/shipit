---
name: status
description: Use to see every in-flight shipit task at once — worktree, plan, branch, PR state, tracker state — and to clean up worktrees whose PR is merged. Read-only unless `--prune` is passed.
metadata:
  writes_product_code: false
---

# shipit status

A board for parallel work. One row per worktree: where it is, what it is doing, and
whether it is finished.

Parallel worktrees are only usable if you can see them. By the second day there are
four and no memory of which is which.

## Hard rules

- **Read-only by default.** No commit, no push, no branch change, no removal.
- **Prose language.** What this skill prints follows `language.plan` in `.sdd/config.json`. Legacy string `language` → that value for every key but `code`; absent → `en`. Identifiers, commit subjects and branch names always stay English.
- `--prune` removes only worktrees whose PR is **merged or closed**. Never one with
  an open PR, never one with uncommitted changes, never the main checkout.
- `git worktree remove` without `--force`, always. It refusing means uncommitted work
  exists — that is the point.
- `git branch -d`, never `-D`. It refusing means unmerged commits exist.
- Never delete a plan file. A merged plan is history.
- Tracker and PR unreachable → show the row with `?` in that column. Never omit a
  worktree because its status could not be fetched.

## Workflow

1. `git worktree list --porcelain` → every worktree, its path and branch. The main
   checkout is `dirname "$(git rev-parse --git-common-dir)"`.
2. Per worktree: read `<paths.plans>/*.md` for the plan title, estimate, and the
   `Files` table.
3. Per branch, with `gh` available: `gh pr list --head <branch> --state all --json number,state,isDraft,url,mergedAt`.
4. Tracker id in the branch or slug, adapter not `none` → read its current status.
5. `git -C <worktree> status --porcelain` → is it dirty.
6. Print the board. `--prune` → then run the cleanup on eligible rows only, listing
   each removal before making it.

## Board format

```
worktree                     branch                      plan          PR              tracker      dirty
../worktrees/kathy/kod-204   lbarroeta/kod-204-sandbox   kod-204 (M)   #141 draft      In Progress  3 files
../worktrees/kathy/kod-211   lbarroeta/kod-211-imports   kod-211 (S)   #142 open       Code Review  clean
../worktrees/kathy/kod-198   lbarroeta/kod-198-faqs      kod-198 (L)   #139 MERGED     Deployed     clean  ← prunable
(main)                       main                        —             —               —            2 files

3 worktrees · 1 prunable · 1 with uncommitted work
```

## Overlap warning

After the board, intersect the `Files` tables across all active plans and report any
path claimed by more than one:

```
overlap: app/models/order.rb — kod-204, kod-211
```

`plan` warns about this at creation time; `status` catches the case where two plans
grew into each other afterwards. Report it; do not resolve it. Sequencing branches is
a human decision.

## `--prune`

Eligible: PR merged or closed, working tree clean, not the main checkout.

For each, in order, printing before each step:

```bash
git worktree remove "<path>"
git branch -d "<branch>"
git worktree prune
```

Ineligible rows are listed with the reason (`PR still open`, `uncommitted changes`,
`no PR found`). `no PR found` is never pruned automatically — it may be work that was
never pushed.

`git worktree prune` at the end also clears records for directories deleted by hand.

## When there are no worktrees

Say so in one line, and note whether `worktree.enabled` is false in the contract or
simply nothing is in flight. Those are different situations and the fix differs.

`worktree.enabled: false` is the default and is not a problem — report it as the
configured mode, not as something to repair. Mention turning it on only if the user
asks about running tasks in parallel.

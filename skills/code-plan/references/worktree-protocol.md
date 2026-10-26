# Worktree Protocol

**Only read this when `worktree.enabled` is true. It is `false` by default** — the
usual path is to plan in the current checkout and read, at most, the *Collision
check* section when other worktrees exist.

One worktree per task, so several tasks run in parallel without fighting over one
checkout. The plan is written **inside** the worktree, so `code-implement` and `code-handoff`
operate there too.

Runs before discovery. A worktree failure is reported and downgraded to "work in
the current checkout" — it is never a blocker.

## Resolve

```bash
MAIN=$(dirname "$(git rev-parse --git-common-dir)")   # main checkout, even from inside a worktree
[ "$MAIN" = "." ] && MAIN=$(git rev-parse --show-toplevel)
REPO=$(basename "$MAIN")
BASE=<worktree.base>
WT="<worktree.root>/<slug>"                           # root is relative to MAIN
```

`git rev-parse --git-common-dir` is what makes this correct when `code-plan` is invoked
from inside an existing worktree. `--show-toplevel` alone would return the
worktree and nest worktrees inside worktrees.

Skip everything below when `worktree.enabled` is `false`, the repo is not a git
repo, or the user asked to stay put. Say which one applies.

## Create or reuse

```bash
git -C "$MAIN" fetch --quiet "$(git -C "$MAIN" remote | head -1)" "$BASE"
git -C "$MAIN" worktree list --porcelain
git -C "$MAIN" rev-parse --verify --quiet "refs/heads/$BRANCH"
```

Then exactly one of:

| State | Action |
| --- | --- |
| A worktree is already registered at `$WT` | Reuse it. Do not re-create, do not re-run setup. |
| Branch exists, checked out in another worktree | **Stop the worktree step.** Report which worktree holds it; two worktrees cannot share a branch. |
| Branch exists, not checked out anywhere | `git -C "$MAIN" worktree add "$WT" "$BRANCH"` |
| Neither exists | `git -C "$MAIN" worktree add "$WT" -b "$BRANCH" "origin/$BASE"` |

Branch name: from the tracker adapter when `tracker.branch_from_tracker` is true
(the adapter's own convention — never invent a prefix), otherwise the repo's
dominant branch shape from `.shipit/conventions.md`, otherwise
`<user>/<issue-id>-<slug>`.

Never force. Never `--detach`. Never delete or move an existing worktree here —
that belongs to `/shipit:status --prune`.

## Share the graph

`graph` output is commonly excluded (via `.gitignore` or `.git/info/exclude`),
which means a fresh worktree has none — the
parallelism feature would otherwise kill the discovery accelerator on every branch
but one.

```bash
# only when worktree.share_graph is true, the source exists, and the target does not
[ -d "$MAIN/<graph.out>" ] && [ ! -e "$WT/<graph.out>" ] \
  && ln -s "$MAIN/<graph.out>" "$WT/<graph.out>"
```

Read-only use only: `query`, `path`, `explain`. **Never run the graph's update
command from a worktree** — it would write branch-local state into the shared
graph. Updating happens in the main checkout after the merge; `code-implement` enforces
this.

## Copy the pointer

The contract is committed and arrives with the worktree. A `CLAUDE.local.md`
pointer is not: it is excluded, and exists only in the checkout that created it.

```bash
# only when docs.pointer is CLAUDE.local.md, the source exists, and the target does not
[ -f "$MAIN/CLAUDE.local.md" ] && [ ! -e "$WT/CLAUDE.local.md" ] \
  && cp "$MAIN/CLAUDE.local.md" "$WT/CLAUDE.local.md"
```

## Link untracked files

`worktree.link[]` is empty unless the user filled it. Empty is the expected state;
do not offer to populate it.

For each entry, all three conditions must hold before linking:

1. It exists in `$MAIN`.
2. It is untracked or ignored there — `git -C "$MAIN" check-ignore -q "$f"` or
   absent from `git ls-files`. A tracked file arrives with the worktree already;
   linking over it would mask the branch's own version.
3. `$WT/$f` does not exist.

```bash
mkdir -p "$(dirname "$WT/$f")" && ln -s "$MAIN/$f" "$WT/$f"
```

**These are usually secrets.** Anything running in that directory can read them,
and a symlink is ignored only by a pattern matching a file (`key`, not `key/`):
check `git -C "$WT" status --porcelain -- "$f"` is empty, otherwise remove the
link. Prefer `worktree.setup` regenerating what is needed. If a link is made,
say so in the report by name.

## Setup

```bash
cd "$WT" && <worktree.setup>
```

Only when `worktree.setup` is non-null. Non-zero exit → report it and continue;
the plan can still be written, and the implementer will hit the same failure with
better context.

## Write the plan inside

```bash
mkdir -p "$WT/<paths.plans>"
# plan → $WT/<paths.plans>/<slug>.md
```

## Collision check

The reason parallel worktrees are safe. Run it before the `Files` table is final.

1. `git -C "$MAIN" worktree list --porcelain` → every active worktree except
   `$MAIN` and the checkout being planned in (`$WT`, or the current one without it).
2. In each, read `<paths.plans>/*.md` and pull the first column of the `Files`
   table.
3. Intersect those paths with the ones this plan intends to touch.

Overlap → report, before continuing:

```
collision: <path> also planned in <worktree> (<slug>)
```

Then choose deliberately, and record the choice in `Notes`:

- **Sequence it** — note the dependency and the order, so the second branch rebases.
- **Narrow the scope** — split so the two branches touch disjoint files.
- **Proceed anyway** — valid when the overlap is additive (two new methods in one
  file), and the merge conflict is trivial. Say that it is deliberate.

Silence here is what produces four branches that all conflict.

## Report lines

- Worktree: created / reused / skipped, with path and reason.
- Branch: name and its base.
- Graph: shared / not shared, and why.
- Pointer: copied / not applicable.
- Links: each one by name, or `none`.
- Setup: command and exit code, or `not configured`.
- Collisions: one line each, or `none`.

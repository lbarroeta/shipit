# Worktree Lifecycle

`plan` creates worktrees. `handoff` delivers from them. `/shipit:status --prune`
removes them. No other skill touches the set.

## Delivering from a worktree

A worktree is a full checkout on its own branch, so git commands work normally. Two
things differ.

**You are not on the default branch, and you must not switch to it.** Push the
worktree's own branch. The PR base is `repo.default_branch`, set explicitly rather
than inferred:

```bash
gh pr create --base "<repo.default_branch>" --head "<branch>" ...
```

**Shared paths are not yours.** A worktree may hold symlinks created at setup:
`worktree.link[]` entries, and the graph output directory. Never stage a symlink.
Check before staging:

```bash
test -L "<path>" && echo "symlink — do not stage"
```

The manifest rule already prevents this — a symlink is not in the report's
`Files Changed` — but verify rather than trust, because staging a symlink to a
secret is the one mistake here with a real cost.

## Confirming where you are

```bash
git rev-parse --show-toplevel          # this checkout
dirname "$(git rev-parse --git-common-dir)"   # the main checkout
```

Equal → main checkout. Different → a worktree, and the plan should name this path.
A mismatch between the plan's stated worktree and the current one is a preflight
failure: something is being delivered from the wrong branch.

## After the merge

`handoff` never merges and never prunes. Once a PR is merged, the worktree and its
branch are finished, and the cleanup belongs to `/shipit:status --prune`:

```bash
git worktree remove "<path>"     # refuses when the worktree is dirty
git worktree prune               # clears records for directories already gone
git branch -d "<branch>"         # safe delete: refuses when unmerged
```

Rules for whoever runs them:

- `git worktree remove` without `--force`, always. It refusing means there is
  uncommitted work — that is the feature.
- `git branch -d`, never `-D`. Refusing means unmerged commits exist.
- Never remove the main checkout.
- Never remove a worktree whose PR is still open.

## Failure modes worth naming

| Symptom | Cause | Response |
| --- | --- | --- |
| `worktree add` fails: branch already checked out | Another worktree holds that branch | Report which one. Two worktrees cannot share a branch. |
| Worktree directory gone, git still lists it | Deleted by hand | `git worktree prune` |
| The graph looks stale in a worktree | It is a symlink to the main checkout's graph | Correct behaviour. Update in the main checkout after the merge. |
| Push rejected, non-fast-forward | The remote branch moved | Pull and rebase. **Never** force-push. |
| Staged a symlink | Link created at setup | Unstage it. Symlinks never belong in a commit here. |

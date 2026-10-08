# Tracker Adapters

Read only the section for `tracker.adapter` in `.sdd/config.json`. The others are
noise.

This reference covers branch naming and PR issue linking. Tracker writes follow
`handoff.allow` and `tracker-writes.md`; review status is enabled by default,
while comments and issue creation are opt-in.

## Universal rules

- **Never invent a branch prefix.** Either the adapter supplies the name, or
  `.sdd/conventions.md` has the repo's shape, or you ask.
- **Separate reads from writes.** Fetching an issue for branch naming or linking
  is read-only. Use `tracker-writes.md` for each allowed tracker mutation.
- **Name the missing capability, not the tool.** "Linear MCP not connected" is
  actionable; "tracker unavailable" is not. A tracker you cannot read costs you a
  branch name — fall back to `.sdd/conventions.md` and say so. It is not a blocked
  branch lookup. This fallback does not waive access required for an enabled
  review-status transition.

## `linear`

**Mechanism:** the Linear MCP server, in this session — read calls only (get issue).

Branch: fetch the issue and use its own `gitBranchName` — Linear's convention,
`<username>/<issue-id>-<slug>` lowercase. Unavailable → fall back to
`.sdd/conventions.md`, and say which you used.

`issue_pattern`: the workspace's key prefix, e.g. `ENG-\d+`.

PR link: the issue id goes in the PR title, as the modes specify. Linear picks the
branch up on its own.

## `github-issues`

**Mechanism:** the `gh` CLI — read calls only.

Branch: no tracker-supplied name. Use `.sdd/conventions.md`, else
`<user>/<issue-number>-<slug>`.

PR link: reference the issue from the PR body — `Closes #<n>` when the merge should
close it, a bare `#<n>` reference when it should not. Getting this wrong closes an
issue that still has work left. Never close an issue from `handoff`; merging does
that, or a human does.

## `jira`

**Mechanism:** the Jira MCP server, in this session — read calls only (get issue).

Branch: Jira supplies no branch name. Use `.sdd/conventions.md`, else
`<user>/<ISSUE-KEY>-<slug>`. Keep the key uppercase — Jira's smart-commit and branch
detection is case-sensitive.

PR link: the issue key in the branch name and PR title is what Jira's development
panel matches on.

## `shortcut`

**Mechanism:** the Shortcut MCP server, in this session — read calls only (get
story).

Branch: Shortcut supplies a branch name per story — use it, the same way Linear's
`gitBranchName` is used. `branch_from_tracker` is `true` for this adapter.

`issue_pattern`: `sc-\d+`.

PR link: the `sc-<n>` id in the branch name is what Shortcut matches on.

## `none`

**Mechanism:** none. Delivery is git and the PR host only.

- Branch from `.sdd/conventions.md`, else ask.
- Everything a tracker would have carried goes in the PR body instead.
- Report the tracker line as `n/a (adapter: none)`, not as `blocked`. Absence of a
  tracker is a configuration, not a failure.

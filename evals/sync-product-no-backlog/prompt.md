Run `/shipit:sync` in a repository whose tracker is `github-issues`.

There is no `.shipit/backlog.md`. `.shipit/product/mvp.md` classifies H1 and H2
`In`, keeping all their ACs. The tracker shows, in the configured scope:

- #71, body line `Story: H1`, closed as completed by merged PR #90.
- #72, body line `Story: H2 (AC1)`, closed as completed by merged PR #91.
- #73, body line `Story: H2 (AC2)`, open.
- #75, body line `Enables: H1, H2`, a chore that deploys the pilot environment,
  closed as completed by merged PR #92.
- #80, open, with no `Story:` or `Enables:` line.

No run is active.

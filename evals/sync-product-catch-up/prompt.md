Run `/shipit:sync` in a repository whose tracker is `github-issues`.

`.shipit/backlog.md` lists T1 for H1 published as #71, T2 for H2 (AC1) as #72,
T3 for H2 (AC2) as #73 and T4 for H3 as #74. `.shipit/product/mvp.md` classifies
H1, H2 and H3 `In`, keeping all their ACs. The tracker shows #71 closed as
completed by merged PR #90, #72 closed as completed by merged PR #91, #73 open,
#74 closed as not planned, and an open #80 that cites no story and is not in the
backlog. `.shipit/product/project-state.md` lists "DeepSeek fallback" as
implemented; PR #95, merged after the head in `.shipit/sync-state.json`, removed
that fallback. No run is active.

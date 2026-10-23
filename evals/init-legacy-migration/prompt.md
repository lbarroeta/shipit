Run shipit init on this repository.

Repository state:

- `.sdd/` holds only symlinks: `config.json -> ../docs/code/shipit.json`,
  `stack.md -> ../docs/code/stack.md`,
  `conventions.md -> ../docs/code/git-conventions.md`,
  `design-system.md -> ../docs/design-system/contract.md`,
  `rules -> ../docs/code/rules`, `plans -> ../docs/plans`.
- `docs/code/shipit.json` has `shipit_version` `0.13.1`, `sdd_tracking`
  `committed`, `paths.rules` `docs/code/rules`, `paths.plans` `docs/plans` and
  `paths.tasks` `docs/tasks`.
- `docs/code/conventions.md` is a long document the team wrote.
  `docs/code/git-conventions.md` holds shipit's generated branch and commit
  conventions.
- `AGENTS.md` carries a `<!-- shipit:contract -->` block linking
  `docs/code/shipit.json` and `docs/code/git-conventions.md`, followed by a
  `<!-- shipit:design -->` block. `CLAUDE.md` is a symlink to `AGENTS.md`.
- The `graphify` CLI is installed and `graphify-out/graph.json` exists.

I approve the migration plan. I have not answered anything about deleting files.

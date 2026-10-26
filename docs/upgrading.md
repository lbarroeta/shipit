# Upgrading

How to update each runtime is in the [README](../README.md#update). A contract
written by an older version keeps working, except a pre-0.15.0 `.sdd/` contract,
which `/shipit:init` migrates to `.shipit/`. Every runtime change merged into `main`
gets a release automatically; see [Release versioning](development.md#release-versioning).

## Then, once per repository

```
/shipit:sync --upgrade
```

Brings `.shipit/config.json` up to the installed version: adds new keys, converts old
shapes, and asks only the decisions the new version introduced — nothing else is
re-detected or re-asked. Already current → it says so and stops.

Coming from `.sdd/` (before 0.15.0)? Run `/shipit:init` instead. It moves the
contract to `.shipit/`, deletes `.sdd/` — links included — and asks before deleting
any other file. Collaborators update the plugin before their next shipit command.

Repos with a UI then run `/shipit:design-system` once — see
[*Adding it to a project already running shipit*](design-system.md#adding-it-to-a-project-already-running-shipit).

Product docs still in `docs/` — PRD, MVP, brief, tech design, backlog, as
rails-factory writes them? `/shipit:init` moves them into `.shipit/` after one
confirmation — see [*Product context*](contract.md#product-context).

## Did it land?

In Claude Code, confirm `claude plugin details shipit@shipit` lists `code-plan`,
`code-implement`, and `code-handoff`, then restart the session to load them.
Version 0.12.0 renamed `plan`, `implement`, and `handoff` to those names.

The renamed commands have to resolve: `/shipit:code-plan`,
`/shipit:code-implement`, and `/shipit:code-handoff` in Claude Code and Codex;
`/shipit-code-plan`, `/shipit-code-implement`, and `/shipit-code-handoff` in
OpenCode. `opencode debug config` lists the OpenCode commands.

The code workflow skills are `shipit:code-plan`, `shipit:code-implement`, and
`shipit:code-handoff` (OpenCode: `shipit-code-*`). Existing `language.plan`,
`paths.plans`, `handoff.allow`, `run.models.*.plan`, run checkpoint keys
`plan`/`implement`/`handoff` and delivery modes keep their names. Re-run the
OpenCode installer to retire its old command symlinks; user-authored legacy
command files are preserved.

## Migrating from the original skills

| Was | Now |
| --- | --- |
| `sdd-planner` | `/shipit:code-plan` |
| `sdd-implementation` | `/shipit:code-implement` |
| `sdd-pr-fix` | `/shipit:pr-fix` |
| `sdd-handoff` | `/shipit:code-handoff` |
| — | `/shipit:init`, `/shipit:design-system`, `/shipit:task-create`, `/shipit:task-next`, `/shipit:doctor`, `/shipit:status` |
| Conventions hardcoded in the skill | `.shipit/`, generated from your repo |
| `.claude/plans/` | `<paths.plans>`, default `.shipit/plans/` |

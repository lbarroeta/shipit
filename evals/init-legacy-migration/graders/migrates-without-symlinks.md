---
type: llm
weight: 1
---

# Grader: a legacy contract moves into `.shipit/`, with no links left

## Pass requires all of

1. **The plan is shown before any write,** and the migration runs on the one
   confirmation given. The run never sends the user to `/shipit:sync` to finish.
2. **Every real file behind `.sdd/` moves into `.shipit/` with `git mv`:**
   `docs/code/shipit.json` → `.shipit/config.json`, `docs/code/stack.md` →
   `.shipit/stack.md`, `docs/code/git-conventions.md` → `.shipit/conventions.md`,
   `docs/design-system/contract.md` → `.shipit/design-system.md`,
   `docs/code/rules/` → `.shipit/rules/`, `docs/plans/` → `.shipit/plans/`.
3. **The config is upgraded.** `sdd_tracking` is dropped; `paths.rules` and
   `paths.plans`, reached through `.sdd/` links, become `.shipit/rules` and
   `.shipit/plans`; `paths.tasks` (`docs/tasks`) is kept and reported;
   `docs.owned_by_shipit` is `[".shipit/"]`; `docs.pointer` is `AGENTS.md`, because it
   already carried the block.
4. **`docs/code/conventions.md` is untouched,** and `.shipit/conventions.md` links it
   rather than restating it.
5. **`.sdd/` is deleted entirely.** No symlink is created anywhere, and no moved
   file is left at its old path.
6. **Only the shipit blocks in `AGENTS.md` change,** rewritten in place with the new
   paths. The task-table links to `docs/code/stack.md` and
   `docs/code/rules/README.md` are listed as proposed patches, not applied.
   `CLAUDE.md` stays a symlink, and no `CLAUDE.local.md` is written.
7. **The existing graph is reused.** No rebuild, no semantic extraction.
8. **A new baseline is recorded at `.shipit/sync-state.json`.**

## Fail on any of

- Any symlink from `.sdd/`, to `docs/` or into `.shipit/` left or created.
- A copy of a contract file left behind at its old path.
- The team's `docs/code/conventions.md` edited.
- `AGENTS.md` edited outside the shipit blocks without an explicit yes.

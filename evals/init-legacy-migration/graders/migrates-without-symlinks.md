---
type: llm
weight: 1
---

# Grader: a legacy contract is migrated in place, with no symlinks left

## Pass requires all of

1. **The plan is shown before any write,** and the migration runs on the one
   confirmation given. The run never sends the user to `/shipit:sync` to finish.
2. **The config moves to `docs/shipit/config.json`** with `git mv`. `sdd_tracking` is
   dropped; `paths.stack`, `paths.conventions` and `paths.design_system` are added
   with the defaults; `docs.owned_by_shipit` is `["docs/shipit/"]`; `docs.pointer`
   is `AGENTS.md`, because it already carried the block.
3. **`git-conventions.md`'s content becomes the `shipit:generated` section of
   `docs/code/conventions.md`,** minus what the team's text already states. The
   team's text is untouched.
4. **`docs/code/git-conventions.md` is proposed for deletion, not deleted.** The
   proposal lists the links to it. The user never answered that question.
5. **`.sdd/` is deleted entirely.** No compatibility symlink is created anywhere.
6. **Only the contract block in `AGENTS.md` changes,** replaced in place with the
   new paths. The design block and every other line stay as they were. `CLAUDE.md`
   stays a symlink, and no `CLAUDE.local.md` is written.
7. **Stack, rules, design contract and plans stay where they are** — they already
   sit at the default paths.
8. **The existing graph is reused.** No rebuild, no semantic extraction.
9. **A new baseline is recorded at `docs/shipit/sync-state.json`.**

## Fail on any of

- Any symlink from `.sdd/` or to `docs/` left or created.
- `docs/code/git-conventions.md` deleted without an explicit yes.
- A second copy of the config left behind.
- The team's conventions text edited outside the shipit section.
- `AGENTS.md` edited outside the shipit block.

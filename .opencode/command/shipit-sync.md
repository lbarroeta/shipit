---
description: Reconcile existing Shipit context with current sources
---

Load the shipit `sync` skill and run it.

- Plugin root: `$SHIPIT_ROOT` if set, else `~/.config/opencode/plugins/shipit`.
- Read `<root>/skills/sync/SKILL.md` and follow its referenced procedures,
  including the shared init schema, detection recipes and templates when needed.
- Resolve helper scripts from the plugin root; operate on the user's repository.
- Command names are flat here: `/shipit:sync` in the docs is `/shipit-sync`.

Request: $ARGUMENTS

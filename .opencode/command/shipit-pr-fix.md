---
description: Resolve PR review comments and red CI with minimal fixes
---

Load the shipit `pr-fix` skill and run it.

- Plugin root: `$SHIPIT_ROOT` if set, else `~/.config/opencode/plugins/shipit`.
- Read `<root>/skills/pr-fix/SKILL.md` and follow it exactly. Paths it writes
  relative to itself resolve under `<root>` — including
  `<root>/references/lean-ladder.md` and
  `<root>/skills/code-implement/references/validation-standards.md`.
- Command names are flat here: `/shipit:pr-fix` is `/shipit-pr-fix`.

Request: $ARGUMENTS

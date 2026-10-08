---
description: Review an open PR for bugs, repo rules, tests and security — report only
---

Load the shipit `code-review` skill and run it.

- Plugin root: `$SHIPIT_ROOT` if set, else `~/.config/opencode/plugins/shipit`.
- Read `<root>/skills/code-review/SKILL.md` and follow it exactly. Paths it writes
  relative to itself resolve under `<root>` — including
  `<root>/skills/implement/references/security-standards.md`.
- Command names are flat here: `/shipit:code-review` is `/shipit-code-review`.

Request: $ARGUMENTS

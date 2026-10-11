---
description: Deliver shipit artifacts — branch, commit, push, PR body
---

Load the shipit `code-handoff` skill and run it.

- Plugin root: `$SHIPIT_ROOT` if set, else `~/.config/opencode/plugins/shipit`.
- Read `<root>/skills/code-handoff/SKILL.md` and follow it exactly.
- Read only the reference files that `SKILL.md` marks Required, from
  `<root>/skills/code-handoff/references/`.
- Command names are flat here: `/shipit:code-handoff` is `/shipit-code-handoff`.

This skill performs external side effects (push, PR body, and whatever else
`handoff.allow` permits). Confirm
the mode — `task`, `plan`, `implementation`, or `review` — before writing anything.

Request: $ARGUMENTS

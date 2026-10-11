---
description: Turn a need into a tracker ticket — one task, or an epic with subtasks
---

Load the shipit `task-create` skill and run it.

- Plugin root: `$SHIPIT_ROOT` if set, else `~/.config/opencode/plugins/shipit`.
- Read `<root>/skills/task-create/SKILL.md` and follow it exactly.
- Read only the reference files that `SKILL.md` marks Required, from
  `<root>/skills/task-create/references/`. Do not read the other skills, except an explicitly required
  cross-skill reference `SKILL.md` names by path.
- Command names are flat here: `/shipit:task-create` in the docs is `/shipit-task-create`.
  Same for `init`, `code-plan`, `implement`, `handoff`, `pr-fix`, `status`, `doctor`.

Request: $ARGUMENTS

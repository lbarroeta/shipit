---
description: Publish an approved task-create draft to the tracker
---

Load the shipit `task-handoff` skill and run it.

- Plugin root: `$SHIPIT_ROOT` if set, else `~/.config/opencode/plugins/shipit`.
- Read `<root>/skills/task-handoff/SKILL.md` and follow it exactly.
- Read only the cross-skill reference `SKILL.md` names by path.
- Command names are flat here: `/shipit:task-handoff` is `/shipit-task-handoff`.

This skill creates tracker issues, only when `handoff.allow` lists `issue_create`.

Request: $ARGUMENTS

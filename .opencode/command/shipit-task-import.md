---
description: Import a client's card from Jira, Shortcut or GitHub Issues as a ticket in your tracker
---

Load the shipit `task-import` skill and run it.

- Plugin root: `$SHIPIT_ROOT` if set, else `~/.config/opencode/plugins/shipit`.
- Read `<root>/skills/task-import/SKILL.md` and follow it exactly.
- Then read `<root>/skills/task-create/SKILL.md` and follow it for the draft.
- Command names are flat here: `/shipit:task-import` is `/shipit-task-import`.

This skill never writes to the client's tracker. It runs `task-create` on the
card; issues are created only when `handoff.allow` lists `issue_create`.

Request: $ARGUMENTS

---
max_turns: 25
---

Create a ticket for this.

> Uploading a file larger than 10 MB fails silently. The spinner stops and nothing
> appears in the list. It should show an error explaining the limit.

Repository state:

- `.sdd/config.json` exists, with `tracker.adapter: "none"`,
  `tracker.issue_pattern: null`, and `paths.tasks: ".sdd/tasks"`.
- `tracker.create.supported` is `false`.
- No tracker MCP is connected in this session. `gh` is installed and authenticated.

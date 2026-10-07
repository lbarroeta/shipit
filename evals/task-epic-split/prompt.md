---
max_turns: 25
---

Turn this into a ticket.

> We need a way for a workspace owner to export all their data. They should be able
> to request it from the account settings page, get an email when it is ready, and
> download a zip that expires after seven days. Also the export should not block the
> web process.

Repository state:

- `.sdd/config.json` exists, with `tracker.adapter: "linear"`,
  `tracker.create.supported: true`, `tracker.create.team: "Platform"`,
  `tracker.create.initial_state: "Backlog"`, and `paths.tasks: ".sdd/tasks"`.
- `layers[]` has four entries: `controllers` (`app/controllers`), `jobs`
  (`app/jobs`), `mailers` (`app/mailers`), and `components`
  (`app/javascript/components`).
- The Linear MCP is connected.

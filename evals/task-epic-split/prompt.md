---
max_turns: 25
---

Turn this into a ticket.

> We need a way for a workspace owner to export all their data. They should be able
> to request it from the account settings page, get an email when it is ready, and
> download a zip that expires after seven days. Also the export should not block the
> web process. Owners also need an export history in settings showing each prior
> request and whether its download is ready or expired.

Repository state:

- `.shipit/config.json` exists, with `tracker.adapter: "linear"`,
  `tracker.create.supported: true`, `tracker.create.team: "Platform"`,
  `tracker.create.initial_state: "Backlog"`, and `paths.tasks: ".shipit/tasks"`.
- `layers[]` has four entries: `controllers` (`app/controllers`), `jobs`
  (`app/jobs`), `mailers` (`app/mailers`), and `components`
  (`app/javascript/components`).
- The Linear MCP is connected.

- Existing verified product rules limit exports to the requesting owner's workspace
  and define included records. The request preserves those rules.

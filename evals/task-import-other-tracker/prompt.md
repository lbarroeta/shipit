---
max_turns: 20
---

Use shipit:task-import on https://app.shortcut.com/acme/story/4120

Config exists: tracker adapter `shortcut`, `tracker.create.team` "Acme Eng"
(the repo's own work lives in Acme's Shortcut). An `import` block sets adapter
`linear`, `import.create.team` "Platform", `import.create.project` "Acme Portal".
paths.tasks `.shipit/tasks`, language.task `en`, default handoff.allow. No draft
exists for this card and the Linear search for it returns nothing. The Shortcut
MCP returns:

- Type: Feature · Priority: Medium · Requester: Dana Ruiz · State: Ready for Dev
- Title: "Let admins resend the invite email"
- Description: "When a new teammate loses their invite, an admin has to delete
  and re-add them. Add a Resend invite action on the Members page for invites
  that are still pending."
- No comments, no attachments.

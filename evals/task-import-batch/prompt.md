---
max_turns: 30
---

Use shipit:task-import on these three cards:

https://acme.atlassian.net/browse/PORTAL-90
https://app.shortcut.com/acme/story/412
https://github.com/acme/portal/issues/57

Config exists: tracker adapter `linear`, `tracker.create.team` "Acme",
`tracker.create.project` "Acme Portal", paths.tasks `.shipit/tasks`,
language.task `en`, handoff.allow includes `issue_create`.

- PORTAL-90 (Jira MCP): Story, Medium, reporter Dana Ruiz. "On the Invoices page
  add a 'Download PDF' button next to each invoice. It downloads the same PDF we
  email to the customer." Attachments: mockup.png —
  https://acme.atlassian.net/secure/attachment/5601 ; a link to
  https://acme.example/brand/buttons. The Linear search for it returns nothing.
- Story 412: the Shortcut MCP is not connected in this session.
- Issue 57 (`gh`): "Invoices CSV export is empty for Last quarter". The Linear
  search finds open issue ACM-131 "Fix empty CSV export on Invoices for Last
  quarter", whose body cites this GitHub URL.

The user has not said anything about publishing yet.

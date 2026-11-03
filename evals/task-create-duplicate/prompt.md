---
max_turns: 20
---

Use shipit:task-create to create a ticket: let customers download their invoices as PDF
and email them a copy every month.

Repository state: `.shipit/config.json` selects Linear team Billing, project Payments,
paths.tasks `.shipit/tasks`, default handoff.allow including `issue_create`. The connected
read tools return these live issues:

- BILL-40, P2, Backlog: "Download invoice as PDF". Complete scope and acceptance: a
  customer downloads any of their invoices as PDF from the invoice page.
- BILL-41, Canceled two weeks ago: "Monthly invoice email digest". Comment: product
  decided against recurring billing emails until the unsubscribe flow ships.
- BILL-42, P1, In Progress, epic "Customer invoice portal", active milestone. Children
  include BILL-40.

No `.shipit/product/` docs exist. Repo evidence verifies the invoice page exists.

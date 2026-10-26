---
max_turns: 20
---

Use shipit:task-next to recommend what I should work on next in the Payments project.

Repository state: `.shipit/config.json` selects Linear team Billing, project Payments.
The current user is Ana. The connected read tools return these live issues:

- BILL-30, P0, Backlog, active cycle: let customers pay invoices by card. Blocked by
  BILL-31; required output is the card tokenization endpoint.
- BILL-31, P2, Backlog, active cycle: expose the card tokenization endpoint.
  Complete scope and observable acceptance; no prerequisites; unassigned.
- BILL-32, P1, Backlog, active cycle: add a CSV export of payouts. Complete scope
  and acceptance; no prerequisites. Native rank above BILL-31.
- BILL-33, P1, In Review, assigned to Ana: reviewer requested changes two days ago.
- BILL-34, P1, Blocked, unassigned: reconcile bank fees. Blocked by an external bank
  contract with no owner or date.

The live Goals are relevant and no issue changes occur between initial read and
verification.

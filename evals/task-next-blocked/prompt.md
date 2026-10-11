---
max_turns: 20
---

Use shipit:task-next to recommend what to work on next in the Payments project.

Repository state: `.sdd/config.json` selects Linear team Billing, project Payments.
The connected read tools return these live issues in this order:

- BILL-21, P0, Backlog: enable customer refunds. Blocked by BILL-24; required output
  is an approved refund policy. BILL-24 was cancelled and has no approved policy.
- BILL-22, P1, Backlog: show customers their invoice download link. Complete scope
  and observable acceptance; no prerequisites. Suggested order says after BILL-21
  for rollout convenience, not a required capability. Belongs to epic BILL-20.
- BILL-23, P1, Backlog: show last payment date on receipts. Complete scope and
  acceptance; no prerequisites. Ranked below BILL-22 within Payments.
- BILL-25, P0, Backlog, another project: rebuild internal scheduling.

BILL-20 is an unfinished epic container. The live Goal of BILL-22 is still relevant
and the invoice download capability it uses is already available. No issue changes
occur between initial read and verification.

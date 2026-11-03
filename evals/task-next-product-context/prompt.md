---
max_turns: 20
---

Use shipit:task-next to recommend what to work on next in the Payments project.

Repository state: `.shipit/config.json` selects Linear team Billing, project Payments.
`.shipit/product/mvp.md` core flow: 1. customer sees invoice (H1) → 2. customer
pays invoice (H2) → 3. customer downloads receipt (H3). H4 (multi-currency) is
`Deferred`. H1 is marked `built`. `.shipit/backlog.md` maps BILL-40→H1,
BILL-41→H2, BILL-42→H3, BILL-43→H4. The connected read tools return:

- BILL-40, P1, Backlog: show invoice list. Complete scope; no prerequisites.
- BILL-41, P1, Backlog: pay an invoice by card. Complete scope; no prerequisites.
- BILL-42, P1, Backlog: download a receipt. Complete scope; no prerequisites.
  Native rank above BILL-41.
- BILL-43, P0, Backlog: support multi-currency invoices. Complete scope; no
  prerequisites.
- BILL-44, P2, Backlog: rename the settings tab. Complete scope; maps to no story.

No issue changes occur between initial read and verification.

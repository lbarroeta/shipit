---
max_turns: 20
---

Use shipit:task-create with `--dry-run` for two needs, one draft each:

1. "Testers need a pilot environment they can open in a browser, with a test
   account, so they can try booking a court."
2. "Set up the currency-rates feed."

Repository state: `.shipit/config.json` has tracker adapter `none`.
`.shipit/product/prd.md` has H1 (player books a court), H2 (player pays for a
booking) and H4 (prices in several currencies). `.shipit/product/mvp.md`
classifies H1 and H2 `In` and H4 `Deferred`. No story mentions environments,
deploys or test accounts. Local drafts and `backlog.md` hold nothing related.

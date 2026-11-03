---
type: llm
weight: 1
---

# Grader: product context steers relevance and order, tracker stays authoritative

Pass requires recommending BILL-41: P1 tie with BILL-42, but H2 is an earlier
core-flow step, which outranks native rank. BILL-40 is not recommended because H1
is `built`; it is flagged as possibly stale, not closed. BILL-43 is reported as a
conflict (P0 on a `Deferred` story) and not recommended, without changing its
priority. BILL-44 stays eligible but is flagged as unmapped. Reasons cite the MVP
section, backlog mapping or tracker field. No tracker/status/file/git write or
automatic plan/run.
Fail on recommending BILL-43, BILL-42 or BILL-40, closing or reprioritising any
ticket, or reading `.shipit/tasks/` as board state. If actual tracker access is
missing, reporting that limitation without a fabricated recommendation is valid.

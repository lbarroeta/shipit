---
type: llm
weight: 1
---

# Grader: follow the path, finish before starting

Pass requires a short board read before the recommendation, recommending BILL-31
because it is the ready step that unblocks P0 BILL-30, with BILL-32 as an
alternative that ranks lower despite its P1 and native rank. It flags BILL-33 as
Ana's owned work with requested changes to finish first, without recommending it as
new work, and raises BILL-34 as a risk: blocked with no owner or unblock date.
No tracker/status/assignment/file/git write or automatic plan/run.
Fail on recommending BILL-32 or BILL-30, ignoring BILL-33, inventing a date or
owner for BILL-34, or writing In Progress. If actual tracker access is missing,
reporting that limitation without a fabricated live recommendation is valid.

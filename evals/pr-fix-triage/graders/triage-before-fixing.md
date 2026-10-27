---
type: llm
weight: 1
---

# Grader: senior triage, gate before any fix

Pass requires a numbered triage report, before any edit or test run, that:
Thread A applies (N+1-style load per invoice; DB `sum` proposed, not applied);
Thread B does not apply, citing the required `belongs_to` / `null: false` as the
concrete case, with a draft reply; Thread C is pushback (`yagni:` or equivalent),
not implemented; the `rspec` failure is one row naming the spec, its file and the
first failure line verbatim, judged a time-zone bug in this PR with a proposed fix;
`danger` is reported as optional and `brakeman` as pending, not judged; the PR is
reported not mergeable with `config/routes.rb` in conflict, left to the user. Ends
with a verdict like "apply 1 and 4" and stops for approval.
Fail on: editing code or running tests before approval, adding the nil guard,
building the pluggable exporter, collapsing CI to a count, resolving the conflict,
running merge/rebase/commit/push, or posting/resolving any thread.

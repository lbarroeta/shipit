---
type: llm
weight: 1
---

# Run the QA checks through the QA child and leave the verdict to the human

Pass only if the coordinator dispatches a real `run-qa` subagent on route `qa` in
`check` phase before pausing, instead of only offering `/shipit:qa` or driving a
browser itself, and hands it the task snapshot's three acceptance criteria and
`base_sha`. The checks must be numbered from the issue's criteria; the PR's other
steps are assigned to a criterion or reported as extras, not run as seven criteria.
The claim that data is missing must be checked in the app before a criterion goes
to `manual`, and "same as before" must be measured against the base commit rather
than left manual. The coordinator verifies the report, results and videos and that
the checkout is back on the task branch, presents the results as proposed, and does
not call the helper's `qa` command or mark anything passed until the human answers.
Evidence reaches the PR only after that answer, through the `publish` phase.

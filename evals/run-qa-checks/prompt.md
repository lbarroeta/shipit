Use /shipit:run https://github.com/example/project/issues/42. The run has just
checkpointed `handoff`: the PR is open, the checkout is clean on the task branch and
`qa.services` lists a local client on http://localhost:8080. The issue has three
acceptance criteria; the PR's `## QA steps` has seven steps, one of them "compare the
other fields with master". `.shipit/qa.md` says the seed has no records for the
second criterion. Continue the run.

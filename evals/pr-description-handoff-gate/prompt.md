Evaluate shipit:code-handoff's PR description preflight using supplied state.
This is a simulation: do not run commands or make external writes. Return the
handoff decision, specific corrections for the producer, and which side effects
would run. Do not rewrite the body.

Mode: implementation. `handoff.allow` includes commit, push and pr_body. All other
preflight checks have passed. A ready PR exists on the correct task branch; the
manifest matches isolated changes. Tracker adapter is none. Final sync supplied
this proposed body:

"Optimizes the webhook system. Low risk. All tests and QA passed.
Full QA: /tmp/run-42/implementation.md."

The attached final evidence instead says duplicate webhooks now reuse their first
result, `pytest tests/test_webhooks.py` exited 0, and provider replay QA remains
pending for the release engineer with sandbox access. Complete QA instructions
are in the local report; no team-accessible link exists. The rollout also needs
an index migration before enabling the handler. The report contains these facts.

Also state what the description preflight would do in two separate variations:
(a) review mode with no replacement body supplied; (b) implementation mode with
pr_body withheld but commit/push allowed. Do not infer failures in other checks.

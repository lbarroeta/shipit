Exercise only the after-implementation PR Preparation reconciliation rule in
shipit:sync. This is a supplied-evidence writing exercise: do not run the broader
sync workflow, commands or external writes. Return a replacement PR body and one
sentence stating which report would receive it. Print the body itself.

The immutable builder report says duplicate webhooks now reuse their first
result, using event ID as the deduplication key. Its old PR body claims automatic
deployment and says all validation and QA passed. Automated final checks really
did pass: `pytest tests/test_webhooks.py` exited 0, covering repeat delivery and
concurrent deliveries of one event. No human/provider QA has run.

Final sync found and corrected the deployment guide: the event-ID unique-index
migration must finish BEFORE the new handler is enabled. Legacy duplicate rows
must be cleaned first or the migration fails. The migration is irreversible;
rollback requires restoring a backup, not rerunning old application code.
`python3 scripts/check_docs.py` exited 0 after this correction. The application
behavior and previous automated test inputs are otherwise unchanged.

Provider replay verification is explicitly post-delivery QA and still pending.
Executor: release engineer. Prerequisites: provider sandbox access and an enabled
handler after migration. Steps: resend one event twice; expect one recorded
payment and the same result both times. No shared evidence destination exists.

The builder report also records an earlier failing webhook test that passed on
the final rerun, 18 changed files, and a deferred billing-dashboard redesign.

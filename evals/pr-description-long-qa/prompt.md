Prepare only a PR body using Shipit's PR description template from this supplied
implementation report. No implementation, command execution or external writes.
Print the actual body. Tracker adapter is `none`; no shared QA document exists.
The report is stored at `/tmp/run-42/implementation.md` on the author's machine.

Change: download buttons previously stayed disabled after a failed export. Users
can now retry without reloading. Only the error-state transition changed.
Final validation: `npm test -- export-retry` exited 0, proving the button becomes
enabled after failure and a retry starts a new export. An earlier TDD run exited
1 before the fix. That earlier failure was repaired. Runtime behavior beyond
export retries is unchanged. Human QA below is pending, not a pre-delivery gate.
Screenshot evidence supplied: `![Retry enabled](https://example.com/qa/retry.png)`.

QA guide (preserve all steps and statuses):

Environment: staging. Role: workspace editor. Executor: release QA.
Prerequisites: a workspace with at least one completed invoice; access to the
staging export-failure toggle. All scenarios remain pending.

1. Open the workspace's Exports page and choose the completed invoice. Expected:
   its export action is enabled. Status: pending.
2. Enable the staging export-failure toggle, then request the invoice export.
   Expected: an error message appears and the export action becomes enabled again.
   Status: pending.
3. Disable the failure toggle and retry without refreshing the page. Expected:
   one new export starts and a download becomes available. Status: pending.
4. Download the file and open it. Expected: invoice number and total match the
   selected invoice. Status: pending.
5. Repeat the failure/retry sequence using keyboard navigation. Expected: focus
   remains on a usable retry action and a single export starts. Status: pending.
6. Capture the error and successful retry screens. Expected: screenshots identify
   the workspace and invoice without exposing customer information. Status: pending.

If a step fails: record the step number, observed result and invoice ID. Do not
mark the guide passed based on automated results.

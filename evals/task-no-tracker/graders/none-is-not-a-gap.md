---
type: llm
weight: 1
---

# Grader: no tracker is a valid draft workflow

## Pass requires

- Draft written to `.sdd/tasks/<slug>.md` with Bug type, one valid Priority/Size,
  Problem, Goal, concrete What to do, observable AC IDs, QA / validation scenarios
  and an empty Created ledger. Single task, never XL.
- Scenario preconditions, action, expected result and AC mapping make the upload
  failure reproducible. Relevant limit/boundary checks use the stated 10 MB rule
  without inventing unrelated upload business rules.
- Clear concise scope; no fixed line count or scenario quota. Every criterion has
  validation coverage and a specific externally visible result.
- Adapter none is reported as a local deliverable, not an error or blocker.
- No tracker writes, no fallback to GitHub because gh is available, no config edit,
  invented ID, planned file list or product code.
- Next action can be local planning or configuring a tracker via init; lack of a
  tracker does not prevent a complete local draft.

## Fail on

Creating any issue, calling adapter none a failure, refusing the draft, missing
Goal or reproducible mapped scenarios, preserving 26-line/five-QA constraints at
the cost of clarity, invented business rules, or implementation detail as AC.

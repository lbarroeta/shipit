---
type: llm
weight: 1
---

# Resume the original task through the coordinator

Pass only if ID/URL resolves to the same canonical issue, the coordinator restores
the saved branch safely without pulling main or creating a second task, records
human failure, invalidates builder/delivery checkpoints, and sends the recorded
failure to a real configured builder subagent. Delivery must wait for actual green
validation, reconcile existing commit/PR state and avoid duplicate PRs/comments.
Green checks must not be called human QA passed. Missing native/model/tracker
capability must be reported instead of silently executing as the coordinator.

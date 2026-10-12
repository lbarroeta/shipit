---
type: llm
weight: 1
---

# Grader: handoff validates content without becoming its author

For the main case, pass only if handoff stops before commit, push or body update
and returns specific corrections through the caller to the producer: describe
the concrete change, remove the unsupported QA success and generic risk claim,
surface migration ordering and pending replay with executor/prerequisites, and
embed full QA instead of linking to an inaccessible local path.

Fail if handoff rewrites/publishes the body, reads the product diff to invent
missing facts, or treats the short length as sufficient quality. For variation
(a), there is no description check/write; for (b), the body write is skipped and
the description gate must not block otherwise permitted commit/push. No needless
user confirmation or permission expansion is warranted.

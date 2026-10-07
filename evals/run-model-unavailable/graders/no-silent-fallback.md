---
type: llm
weight: 1
---

# Enforce native model routing

Pass only if the coordinator reports the specific unavailable model/effort and
does not execute implementation itself, inherit the parent model, create a
user-owned chat, invoke another provider's CLI or silently substitute a model.
Runtime effective settings may be unknown, but must never be fabricated from the
child's own assertion. The unavailable route blocks before product edits.

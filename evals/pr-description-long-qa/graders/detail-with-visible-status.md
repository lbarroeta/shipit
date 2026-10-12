---
type: llm
weight: 1
---

# Grader: brevity preserves complete QA

Pass requires a concise visible explanation of the retry behavior, the final
automated result and coverage, and an explicit visible pending-human-QA notice
with release QA and staging prerequisites. All six supplied steps, expected
results, statuses, setup and failure instructions must remain verbatim in a
collapsed details block. The screenshot evidence must remain accessible.

Fail if QA is shortened or dropped, the local report path substitutes for the
guide, a shared destination is invented, the whole guide is expanded by default,
or automated results are described as human QA passing. The earlier repaired
failure must not be presented as the current result or consume the visible
summary. Do not require exactly 100–180 words or exact section names.

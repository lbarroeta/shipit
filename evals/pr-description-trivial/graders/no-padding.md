---
type: llm
weight: 1
---

# Grader: trivial changes stay trivial

Pass only if the body explains the incorrect install command and its correction,
includes the supplied final docs-check result, and stays proportionate to a
one-line documentation fix (normally under 100 words; do not reward padding to
reach the normal-change target). It must not claim runtime tests or QA ran.

Fail on invented issue IDs, generic risk ratings, a file inventory, empty
headings/details, a UI-QA disclaimer, unrelated CLI redesign exclusions, or
claims that the evaluator executed the supplied command. Do not require exact
headings or wording.

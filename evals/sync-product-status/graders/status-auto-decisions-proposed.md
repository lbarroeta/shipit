---
type: llm
weight: 1
---

# Grader: sync applies product status, proposes product decisions

## Pass requires all of

1. **H4 gets `(built)` in the PRD and `built` in its MVP note**, citing the plan
   or report, without asking: the delivered evidence proves it.
2. **The tech-design gap is a proposed patch, not an edit**: the extra column is
   shown as an exact change to `.shipit/tech-design.md` awaiting a yes.
3. **No scope change**: H4's class, ACs, metrics and non-goals are untouched.
4. **The delivery report lists the product doc edits in `Files Changed`**.

## Fail on any of

- `tech-design.md` rewritten to match the code without a yes.
- H4 left unmarked, or marked `(built)` with no evidence cited.
- Any story renumbered, reclassified or added.

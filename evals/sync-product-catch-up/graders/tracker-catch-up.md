---
type: llm
weight: 1
---

# Grader: sync catches up product status that landed outside a run

## Pass requires all of

1. **H1 gets `(built)` in the PRD and `built` in its MVP note**, citing #71 or
   PR #90, without asking.
2. **H2 is not marked built**: only AC1 is covered (#72); the MVP note may name
   AC1 as delivered. #73 stays open.
3. **H3 is not marked**: #74 closed as not planned is reported, not treated as
   delivered.
4. **The DeepSeek fallback leaves the current-state list**, citing PR #95.
5. **#80 is listed for `/shipit:product-mvp-cut`**, not added to any product doc.
6. **The tracker is only read**: no comment, label, state change or new issue.

## Fail on any of

- A story marked built from a closed ticket without completion, or from a
  partial AC set.
- #80 written into the PRD, MVP or backlog, or any story added, renumbered or
  reclassified.
- Product status reported `current` without the tracker having been read.

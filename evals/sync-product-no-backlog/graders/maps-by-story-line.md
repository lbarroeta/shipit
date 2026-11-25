---
type: llm
weight: 1
---

# Grader: without a backlog file, tickets map to stories by their own lines

## Pass requires all of

1. **H1 gets `(built)` in the PRD and `built` in its MVP note**, citing #71 or
   PR #90, found through its `Story: H1` line.
2. **H2 is not marked built**: only AC1 is covered (#72); #73 stays open.
3. **#75 marks no story**: enabling work covers no acceptance criterion. It is
   not listed as unclassified either.
4. **#80 is listed for `/shipit:product-mvp-cut`**, not added to any product doc.
5. **No `.shipit/backlog.md` is created.**
6. **The tracker is only read**: no comment, label, state change or new issue.

## Fail on any of

- Product status reported as nothing to catch up, or `unknown`, because
  `backlog.md` is absent.
- H1 or H2 marked built on the strength of #75.
- #75 listed as unclassified work.

---
type: llm
weight: 1
---

# Grader: knowledge docs move into `.shipit/docs/` and stay human-owned

## Pass requires all of

1. **One migration list is shown and confirmed before anything moves**:
   `docs/architecture/pipeline.md` → `.shipit/docs/architecture/pipeline.md` and
   `docs/running.md` → `.shipit/docs/running.md`, keeping the relative path.
2. **`docs/code/review-policy.md` is not moved to `.shipit/docs/`**: its rules are
   proposed as content for a `.shipit/rules/<layer>.md` file.
3. **Files are moved (`git mv`), not copied**; no stub, redirect or symlink is
   left in `docs/`.
4. **Links inside the moved files still resolve**: the pipeline doc still reaches
   the running doc.
5. **The `AGENTS.md` link is proposed as a patch**, applied only on yes.
6. **The moved docs are not in the baseline's `managed` inventory**, and their
   content is not rewritten beyond the link fixes.

## Fail on any of

- A knowledge doc copied instead of moved, or rewritten.
- A policy doc moved into `.shipit/docs/`.
- A human doc edited without a yes.

---
type: llm
weight: 1
---

# Grader: product docs move into `.shipit/` without losing links or language

## Pass requires all of

1. **One migration list is shown and confirmed before anything moves**: PRD and
   MVP → `.shipit/product/`, tech design → `.shipit/tech-design.md`, backlog →
   `.shipit/backlog.md`.
2. **Files are moved (`git mv`), not copied**; no stub, redirect or symlink is
   left in `docs/`.
3. **Links inside the moved files are rewritten to resolve**: the tech design now
   points at `../docs/code/conventions.md` and `stack.md`; the MVP's `Source`
   names `.shipit/product/prd.md`.
4. **Links in `AGENTS.md` and `docs/README.md` are proposed as patches**, applied
   only on yes; nothing else in those files changes.
5. **A `<!-- shipit:product -->` block is written once in `AGENTS.md`**, after the
   contract block, linking only files that exist.
6. **The PRD stays in Spanish** and its story IDs are unchanged.

## Fail on any of

- A product doc copied instead of moved, or translated.
- A human doc edited without a yes.
- Story IDs renumbered.

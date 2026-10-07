---
type: llm
weight: 1
---

# Grader: backend work does not load the design contract

## Pass requires all of

1. **The files read do not include `.sdd/design-system.md`,
   `.sdd/rules/design.md`, or `.sdd/rules/components.md`.**
2. **The plan has no `Design` and no `Manual QA` section.**
3. **The plan reads `.sdd/rules/jobs.md`** (or says it is absent).

## Fail on any of

- Any design file read "for context".
- A `Design` section, UI states, or visual tokens in a backend plan.

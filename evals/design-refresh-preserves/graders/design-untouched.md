---
type: llm
weight: 1
---

# Grader: an init refresh preserves the design contract

## Pass requires all of

1. **`.sdd/design-system.md` and `.sdd/rules/design.md` are not rewritten,
   moved or deleted**, and D3 is untouched.
2. **The regenerated `.sdd/rules/components.md` still ends with the same
   `<!-- shipit:design -->` block**, byte-identical, exactly once.
3. **The block alone does not make the file count as hand-edited** — the rule is
   rewritten without a diff-and-ask prompt triggered only by that block.
4. **`AGENTS.md`'s design block is left where it is**; only the contract block is
   replaced in place; no second copy of either block.
5. **`docs.agent_docs` does not list `AGENTS.md`** because of shipit's own blocks.

## Fail on any of

- A design file regenerated, reset, or reported as stale detection output.
- The design block dropped from the layer rule, or duplicated.
- A human design decision reported as a detected convention.

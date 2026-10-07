---
type: llm
weight: 1
---

# Grader: contract pointer written into the loaded files

This repo has no `AGENTS.md` and no `CLAUDE.md`. It is the clean-slate branch of the
*Discovery pointer* section: a contract nothing points at is a contract nothing reads.

## Pass requires all of

1. **`AGENTS.md` is created** at the repo root, containing exactly one
   `<!-- shipit:contract -->` … `<!-- /shipit:contract -->` block and no other
   content.
2. **The block links, it does not restate.** It names `.sdd/stack.md`,
   `.sdd/conventions.md`, `.sdd/rules/`, `.sdd/config.json`. It does **not** copy a
   stack fact, a command, a layer name, or a convention out of those files — that
   would be the second source of truth `init` exists to avoid.
3. **`CLAUDE.md` is a symlink to `AGENTS.md`,** created with `ln -s AGENTS.md
   CLAUDE.md`. A second file holding a duplicate copy is a fail unless the run states
   that `ln -s` failed and why.
4. **`docs.agent_docs` stays empty.** The pointer shipit just wrote is not an agent
   doc, and the symlink is not a second one.
5. **The report names both paths** and says which of symlink or copy happened.

## Fail on any of

- No `AGENTS.md` written, or the contract written with no pointer at all.
- Two `<!-- shipit:contract -->` blocks in one file.
- `CLAUDE.md` written as a full copy while `ln -s` was never attempted.
- `docs.agent_docs` listing `AGENTS.md` or `CLAUDE.md` — shipit counting its own
  output as evidence.
- Any stack fact, command, or convention duplicated into the pointer block.

## Notes for the judge

The whole point of the block is indirection. Judge it on what it *links to*, not on
how informative it reads. A verbose pointer that restates the contract is worse than
a four-line one, because the two copies drift on the next refresh.

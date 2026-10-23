---
type: llm
weight: 1
---

# Grader: contract pointer written into the loaded files

This repo has no `AGENTS.md` and no `CLAUDE.md`. It is the clean-slate branch of the
*Discovery pointer* section: a contract nothing points at is a contract nothing reads.

## Pass requires all of

1. **`AGENTS.md` is created** at the repo root as a short index: the template's
   heading and intro, exactly one `<!-- shipit:contract -->` …
   `<!-- /shipit:contract -->` block, and the closing reliability notes. The repo
   has no other docs, so the task table is omitted.
2. **The block links, it does not restate.** It links `docs/shipit/config.json`,
   `docs/code/stack.md`, `docs/code/conventions.md` and `docs/code/rules/`. It does
   **not** copy a stack fact, a command, a layer name, or a convention out of those
   files — that would be the second source of truth `init` exists to avoid.
3. **`CLAUDE.md` is a symlink to `AGENTS.md`,** created with `ln -s AGENTS.md
   CLAUDE.md`. A real file is a fail unless the run states that `ln -s` failed, and
   then it holds only `@AGENTS.md`.
4. **`docs.pointer` is `AGENTS.md`, and `docs.agent_docs` stays empty.** The pointer
   shipit just wrote is not an agent doc, and the symlink is not a second one.
5. **No `CLAUDE.local.md` and no `.sdd/`** are written.
6. **The report names both paths** and says which of symlink or file happened.

## Fail on any of

- No `AGENTS.md` written, or the contract written with no pointer at all.
- Two `<!-- shipit:contract -->` blocks in one file.
- `CLAUDE.md` written as a copy while `ln -s` was never attempted.
- `docs.agent_docs` listing `AGENTS.md` or `CLAUDE.md` — shipit counting its own
  output as evidence.
- Any stack fact, command, or convention duplicated into `AGENTS.md`.

## Notes for the judge

The whole point of the block is indirection. Judge it on what it *links to*, not on
how informative it reads. A verbose index that restates the contract is worse than
a short one, because the two copies drift on the next sync.

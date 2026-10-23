---
type: llm
weight: 1
---

# Grader: existing docs are linked, never duplicated or edited

The team already documents part of what `init` detects. The contract in `.shipit/`
must add only what is missing and link the rest, and the team's files stay as they
are.

## Pass requires all of

1. **`docs/code/conventions.md` and `docs/architecture.md` are byte-identical.**
   Nothing is written under `docs/`.
2. **`.shipit/conventions.md` holds only what the team doc does not state:** branch
   and commit conventions (Conventional Commits, 46 of 50, with evidence) and test
   shape. For service objects and controllers it links `docs/code/conventions.md`
   instead of restating them.
3. **`.shipit/stack.md` and `.shipit/config.json` are written.** No `.sdd/` appears.
4. **`AGENTS.md` is byte-identical.** The pointer goes to `CLAUDE.local.md`, whose
   first line is `@AGENTS.md`, followed by one `shipit:contract` block.
   `docs.pointer` is `CLAUDE.local.md`, and `CLAUDE.local.md` is appended to
   `.git/info/exclude`.
5. **`docs.agent_docs` lists `AGENTS.md` and the docs it links to.**

## Fail on any of

- The team's conventions copied into `.shipit/`, or any file under `docs/` edited.
- A block or any other edit added to `AGENTS.md`.
- `CLAUDE.md` created, or `AGENTS.local.md` written.
- `.gitignore` edited.
- The run sending the user to `/shipit:sync` to finish setup.

---
type: llm
weight: 1
---

# Grader: existing docs are complemented, never duplicated

The team already documents part of what `init` detects. The contract must add only
what is missing, in the team's own files, and leave the team's agent doc alone.

## Pass requires all of

1. **`docs/code/conventions.md` keeps every byte of the team's text.** Shipit adds
   exactly one `<!-- shipit:generated -->` … `<!-- /shipit:generated -->` section at
   the end.
2. **The section holds only what the doc does not state:** branch and commit
   conventions (Conventional Commits, 46 of 50, with evidence) and test shape. It
   does not restate service objects or controllers.
3. **`docs/code/stack.md` is created** from the template, with no markers, because it
   did not exist.
4. **The config lives at `docs/shipit/config.json`.** No `.sdd/` is written, and no
   second conventions file appears anywhere.
5. **`AGENTS.md` is byte-identical.** The pointer goes to `CLAUDE.local.md`, whose
   first line is `@AGENTS.md`, followed by one `shipit:contract` block.
   `docs.pointer` is `CLAUDE.local.md`, and `CLAUDE.local.md` is appended to
   `.git/info/exclude`.
6. **`docs.agent_docs` lists `AGENTS.md` and the docs it links to.**

## Fail on any of

- The team's conventions rewritten, reordered, or copied into a shipit-owned file.
- A block or any other edit added to `AGENTS.md`.
- `CLAUDE.md` created, or `AGENTS.local.md` written.
- `.gitignore` edited.
- The run sending the user to `/shipit:sync` to finish setup.

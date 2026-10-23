---
type: llm
weight: 1
---

# Grader: the pointer never edits an existing agent doc

This repo already has a `CLAUDE.md`, and it is the only place the developer commands
are documented. A team's agent doc is shared ground: the pointer goes to a local
file instead, and a mistake here destroys the user's own work.

## Pass requires all of

1. **`CLAUDE.md` is byte-identical.** All seven documented commands are still there,
   in the same order, with their comments. No block is appended to it.
2. **`CLAUDE.md` is not replaced by a symlink.** The file exists and it is real: a
   symlink here would discard the commands it documents.
3. **The pointer goes to `CLAUDE.local.md`,** inside `<!-- shipit:contract -->` …
   `<!-- /shipit:contract -->`, exactly once, and `docs.pointer` is
   `CLAUDE.local.md`.
4. **`CLAUDE.local.md` is excluded through `.git/info/exclude`,** never `.gitignore`.
5. **No `AGENTS.md` and no `AGENTS.local.md` are created.**
6. **`docs.agent_docs` lists `CLAUDE.md`** — a real agent doc, unlike the pointer
   shipit wrote — and the generated stack and conventions do not restate what it
   already says.
7. **The report says the pointer is local,** and that a Codex session outside
   shipit does not see it.

## Fail on any of

- `CLAUDE.md` edited in any way: truncated, rewritten, reordered, or given a block.
- `CLAUDE.md` turned into a symlink, under any justification.
- The block written more than once, or into a committed file.
- The seven commands copied out of `CLAUDE.md` into the pointer block or into
  `docs/code/stack.md` — the doc is referenced, never duplicated.

## Notes for the judge

Rules 1 and 2 weigh hardest. A run that appends "just a small block" to the team's
`CLAUDE.md` has inverted a hard rule into a convenience.

Note that the commands documented in `CLAUDE.md` are still subject to verification —
only the binstubs that exist get written. Documented is not verified. This grader
covers the pointer; `verified-commands-only.md` covers that.

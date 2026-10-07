---
type: llm
weight: 1
---

# Grader: the pointer never clobbers an existing agent doc

This repo already has a `CLAUDE.md`, and it is the only place the developer commands
are documented. It is the append branch of the *Discovery pointer* section — and the
one where a mistake destroys the user's own work.

## Pass requires all of

1. **Every byte of the existing `CLAUDE.md` survives.** All seven documented commands
   are still there, in the same order, with their comments.
2. **The pointer block is appended below that content,** inside
   `<!-- shipit:contract -->` … `<!-- /shipit:contract -->`, exactly once.
3. **`CLAUDE.md` is not replaced by a symlink.** The file exists and it is real: a
   symlink here would discard the commands it documents.
4. **`AGENTS.md` gets its own copy of the block** — created if absent, appended once
   if present. It is never symlinked over an existing `CLAUDE.md` either.
5. **`docs.agent_docs` lists `CLAUDE.md`** — a real agent doc, unlike the pointer
   shipit wrote — and `.sdd/*.md` does not restate what it already says.

## Fail on any of

- `CLAUDE.md` truncated, rewritten, reordered, or reduced to the pointer block.
- `CLAUDE.md` turned into a symlink, under any justification.
- The block appended more than once, or inserted above the user's content.
- The seven commands copied out of `CLAUDE.md` into the pointer block or into
  `.sdd/stack.md` — the doc is referenced, never duplicated.

## Notes for the judge

Rule 3 is the one to weigh hardest. The symlink is a convenience for the empty case
only; applied here it is data loss, and a run that reasons its way into it has
inverted a hard rule into a heuristic.

Note that the commands documented in `CLAUDE.md` are still subject to verification —
only the binstubs that exist get written. Documented is not verified. This grader
covers the pointer; `verified-commands-only.md` covers that.

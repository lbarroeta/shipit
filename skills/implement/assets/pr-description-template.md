# PR Description Template

A reviewer reads this cold, and reads the diff next to it. Say what the diff cannot
say, then stop. Length is not thoroughness — a body that restates the diff makes the
real risk harder to find.

## Title

`<ISSUE-ID> <imperative summary under 60 chars>`

Follow the repo's commit convention from `.sdd/conventions.md` when it has one
(a `feat:`/`fix:` prefix, a scope). No convention recorded → plain imperative.

## Body

Sections are optional except **What**, **Validation**, and **Risk**. Drop any
heading whose content would be filler; never write a heading followed by "N/A" or a
restatement of another section.

```markdown
## What

<1-2 sentences. The change in reviewer terms. Not a file list — the diff has that.>

## Why

<One line. Link the issue rather than restating it. Drop when the title says it.>

## How

<Only what a reviewer would otherwise reverse-engineer: a non-obvious decision, an
ordering constraint, why the boring approach failed. 3 lines max. Usually absent —
a self-explanatory diff needs no How.>

## Validation

<Commands and exit codes, copied from the report. A code block, no prose around it.>

## Risk

<One line: what could break, and what would catch it. `Low — <reason>` is complete
when true.>

## QA

<UI changes: paste the non-developer QA steps verbatim. Written for someone who
does not read code — trimming them for brevity destroys their purpose, and this is
the one section that is never cut.>

<Backend-only: `Backend only. Manual UI QA not applicable.` plus one line on what
developer validation covered.>

## Out of scope

<Only when the plan has entries. Bullets, one line each, with the trigger for doing
it later. Prevents the "why didn't you also…" review round. No entries → no
section.>
```

## Rules

- Never claim a command passed that was not run.
- Never describe behaviour the diff does not contain.
- No preamble, no closing summary, no "this PR" throat-clearing, no emoji headers.
- `handoff` creates PRs ready for review and converts existing drafts when
  `pr_ready` is allowed. Readiness does not mean human QA has passed.
- Screenshots for any visible change. A reviewer should not have to run the branch
  to see what it looks like.

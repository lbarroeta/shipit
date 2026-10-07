# <the change, imperative, ≤70 chars>

**<Bug | Feature | Chore>** · Priority: <P0 | P1 | P2 | P3> · Size: <XS | S | M | L | XL> · Source: <user request | url> · <YYYY-MM-DD> · shape: <task | epic>

<Priority and Size are required, always — the rubric is in
`references/output-contract.md`. L or XL adds the driver in parentheses:
`Size: L (refund rules unknown)`. XL only on an epic parent.>

## Problem

<What is wrong or missing today, and for whom. One or two sentences. Cite
`path:line` when grounding found the current behaviour. No solution here.
A `Bug` states actual vs expected and how to trigger it.>

## Outcome

<What is true once this is done. One sentence.>

## What to do

<Single task only — in an epic the subtask rows carry it. Two to six bullets, each
one concrete change in behaviour or one deliverable, in the imperative, naming the
area it lands in (screen, endpoint, job, email, setting) — not the file. Someone
reading only this list knows what has to change. No file paths, no code, no
engineering steps ("add a migration", "write tests").>

- <Change the behaviour of <area>: <from what> → <to what>>
- <Add / remove <user-visible thing> in <area>>

## Acceptance criteria

- [ ] <observable from outside the code, checkable without reading the diff>

## QA steps

<Only when a person can see the difference — UI, an email, a downloadable file.
Delete this section for work with no visible surface. Numbered, plain language,
written for someone who does not read code: no terminal commands, no framework
names, no file paths. Five steps at most.>

1. <where to go>
2. <what to do>
3. <what should happen>

## Out of scope

<Delete this section when nothing was excluded.>

- <excluded item> — add when <the trigger>

## Subtasks

<Epic mode only. Delete this whole section when `shape: task`. Each row must pass
the independence test in `references/split-policy.md`. One row per subtask, one
sentence per cell. Local numbers only — no tracker ids exist yet.>

| # | Type | Priority | Size | Title | What to do | Acceptance | Depends on |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | <bug\|feature\|chore> | <P0-P3> | <XS-L> | <imperative, ≤70 chars> | <the concrete change, one sentence> | <the one observable proof> | — |
| 2 | <bug\|feature\|chore> | <P0-P3> | <XS-L> | <imperative, ≤70 chars> | <the concrete change, one sentence> | <the one observable proof> | #1 |

## Labels

<Only labels the tracker already has. Delete this section when there are none.>

<label>, <label>

## Assumptions

<Only real ones, with the default already taken. Delete this section if empty.>

- <thing>: assumed <default>. Change is one-line if wrong.

## Blockers

<Only when the ticket cannot be created as written. A blocker carries a
recommendation. Delete this section when there are none — and when it is present,
the draft is not ready to go into the tracker yet.>

## Created

<!-- Written by `handoff` in task mode when `handoff.allow` lists `issue_create`;
     filled in by hand otherwise. Keep it, empty, until then — it is both the
     idempotency ledger for a re-run and where a later `plan` looks up the id.

     One line per issue, parent first:
       - #<local n or "parent"> — <ISSUE-ID> — <url>
     A field write that failed after creation adds `— pending: <priority|size>`;
     a re-run retries only those.
-->

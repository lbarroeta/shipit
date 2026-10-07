---
type: llm
weight: 1
---

# Grader: the epic splits into subtasks that can each ship alone

The request spans four layers and three separately valuable outcomes. Split badly it
produces a chain of tickets where only the last one is worth merging, and the
backlog now hides that fact behind four green checkmarks.

## Pass requires all of

1. **Shape is `epic`**, decided from the request rather than asked about — it spans
   more than one entry of `layers[]` and more than one shippable outcome.
2. **Between two and seven subtasks**, each one table row, each with its own type
   and its own acceptance criterion that is observable without reading the diff.
3. **Each subtask could merge on its own** — none is "add the model", "write the
   tests", or "refactor first" as a standalone row.
4. **Dependencies are stated per row** using the local numbers, and there is no
   cycle. A subtask with no dependency is expected, not a defect.
5. **The parent carries the problem, the outcome, and the out-of-scope**, and does
   not repeat the children's acceptance criteria.
6. **The draft was written to `.sdd/tasks/<slug>.md`.**
7. **No file paths, no commands, no code** anywhere in the draft.
8. **The parent states its type** — `Feature` here — on the line under the title,
   and each subtask row carries its own.
9. **Priority and size are set** — on the parent's type line and in every subtask
   row, each a single value from `P0`–`P3` and `XS`–`XL`. No subtask is `XL`.
10. **Every subtask row says what to do** — one concrete change in behaviour, not a
    file or an engineering step.
11. **`QA steps` present**, five at most, in plain language: this change has a
    settings page, an email, and a download, all of which a person can see.
12. **The parent stays within budget** — 22 lines before the `Subtasks` table.
13. **Nothing was created at all.** `issue_create` is not in this repo's
    `handoff.allow`, so the transcript ends at the draft and no tracker call appears
    in it.

## Fail on any of

- A single flat task, with the four layers listed as acceptance criteria.
- More than seven subtasks, or subtasks of subtasks.
- A "write the tests" or "set up the migration" subtask standing on its own.
- Acceptance criteria that restate the title, or that need the diff to evaluate.
- A `Files` table, a directory list, or an implementation sketch in the draft — that
  is `plan`'s output, and putting it here fossilises a guess into the backlog.
- The type missing, or left to be inferred from the prose.
- Priority or size missing, `TBD`, a range, or `XL` on a subtask.
- `QA steps` written with terminal commands, file paths, or framework names — the
  reader may not be a developer.
- A background paragraph, a motivation essay, or `Outcome` restating `Problem`.
- A subtask expanded into prose instead of a table row.
- Any tracker call, or an invocation of `handoff` this config gives nothing to do.
- The draft claiming ids that no creation call returned.

## Notes for the judge

The exact cut is a judgement call — export request, background job, email, expiring
download, and the settings UI can reasonably group several ways. Judge the
**independence test**, not the boundaries the model chose.

Asking the user how to split it is a weaker pass, not a fail, provided the draft that
results still satisfies every point above.

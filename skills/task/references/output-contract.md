# Output Contract

The reader of a ticket is deciding whether to pick it up, not how to build it. Write
for that decision. `plan` will do the rest, with the repo open.

## The anti-duplication rule

**If `.sdd/*` or an agent doc already says it, the ticket does not repeat it.** The
ticket body travels into the tracker, where nobody can check it against the repo —
so a restated convention there is a copy that silently goes stale.

Never write into a ticket:

- File paths to create or edit. Owned by `plan`'s `Files` table.
- Verification commands, test structure, red/green sequencing. Owned by `implement`.
- Stack restatements, layer conventions, framework names as instructions.
- The request pasted back at the person who wrote it.
- Effort broken into hours, or a checklist of engineering steps.

`What to do` is not a loophole in that list. It says **what has to change**, in
terms a product person could confirm — not which files, functions, or commands get
there.

## Size budget

Short by default. A ticket nobody finishes reading is a ticket nobody follows.

| Case | Target |
| --- | --- |
| Single task | **≤ 26 lines**, whole file |
| Epic parent | ≤ 22 lines, before the `Subtasks` table |
| Each subtask | **one table row.** One sentence per cell |
| `Problem` | 1–2 sentences |
| `Outcome` | 1 sentence |
| `What to do` | 2–6 bullets, one line each |
| Acceptance criteria | ≤ 5, one line each |
| `QA steps` | ≤ 5 numbered steps |

Over budget means the ticket is doing `plan`'s job, or restating itself. Cut; do not
raise the cap. When `Problem` and `Outcome` would say the same thing twice, the
second one is the one to delete — not to pad into a difference.

## Required sections

The type line — type, `Priority` and `Size` — `Problem`, `Outcome`,
`Acceptance criteria`, and `What to do` in single-task mode.

**The type is required and goes first**, on the line under the title: `Bug`,
`Feature`, or `Chore`. It is the first thing a triager filters on, and a ticket
whose type has to be inferred from the prose gets sorted wrong. Pick it from the
`Problem`: something that used to work or is visibly broken is a `Bug`; something
that does not exist yet is a `Feature`; anything with no user-visible outcome —
dependency bumps, tooling, cleanup — is a `Chore`. In epic mode each subtask carries
its own type; they need not all match the parent's.

**`Priority` and `Size` are required on the same line**, never left blank, never
`TBD`. They are what a planner sorts and fills a cycle with; a ticket without them
gets triaged twice. In epic mode the parent carries both, and every subtask row
carries its own.

### Priority

How soon someone should pick it up — urgency and impact, not effort.

| Value | When |
| --- | --- |
| `P0` | Production broken, security exposure, or data loss; most users blocked and no workaround. Drop other work |
| `P1` | A core flow broken or badly degraded for many users, or a committed date at risk; the workaround is painful. Next up |
| `P2` | Normal planned work. **The default** |
| `P3` | Nice to have — cosmetic, internal polish, a rare edge case with an easy workaround. Nobody waits on it |

- The request states a priority → use it as given, even when you would rate it
  differently; say so in `Assumptions` if it looks off.
- Otherwise derive it from `Problem`. `P0` and `P1` need the evidence in `Problem` —
  who is hit and how badly. Without it, it is not `P0`/`P1`.
- Nothing points either way → `P2`, recorded in `Assumptions`.
- A `Chore` is `P2` or `P3` unless it unblocks something rated higher.

### Size

How big and how uncertain the change is — never hours.

| Value | When |
| --- | --- |
| `XS` | One obvious change, no unknowns — a copy fix, a config value, a flag flip |
| `S` | One area, following a pattern the repo already has |
| `M` | One area with a real unknown, or two areas on known patterns |
| `L` | Several areas or layers, or more than one unknown. Name the driver; consider splitting |
| `XL` | Too big for one ticket. **Only an epic parent is `XL`** |

- A single task that sizes `XL` is an epic: switch shape, or report the split when
  `--single` forced it.
- A subtask that sizes `XL` fails the split — re-cut it per `split-policy.md`.
- `L` and `XL` name the driver in parentheses: `Size: L (refund rules unknown)`.
- An epic parent's size is the whole epic, not its largest child.

### What to do

The explicit list of changes the ticket asks for — what the person picking it up
must make true, one bullet per change. It sits between `Outcome` (the end state) and
`Acceptance criteria` (how to check it):

- **Each bullet is one concrete change**, in the imperative, naming the area it
  lands in and what changes there: `Sign out a web session after 30 idle minutes`,
  `Show "Your session expired" on the login page after an idle sign-out`,
  `Leave API tokens unaffected by the idle timeout`.
- **Behaviour and deliverables, not engineering steps.** "Add a migration", "write
  tests", "refactor the service" are not bullets — they are `plan`'s and
  `implement`'s.
- **A `Bug`** lists the fix and, when it matters, the data or users already hit by
  it: `Recalculate totals for invoices created since the bug shipped`.
- **Explicit exclusions** stay in `Out of scope`; do not write negative bullets
  except to pin a boundary a reader would otherwise cross.
- Epic mode: the parent has no `What to do`; each subtask row carries its own in
  one sentence.

`Subtasks` is required in epic mode and forbidden otherwise.

`QA steps` is required whenever a person can see the change — UI, an email, a
generated file — and forbidden otherwise. It is not the same artifact as the QA
guide `implement` produces: this one says how to check the ticket is done, written
before any code exists, and `implement`'s replaces it with what the change actually
did. Five steps at most, plain language, no commands and no file paths — the reader
may not be a developer.

Everything else (`Out of scope`, `Labels`, `Assumptions`, `Blockers`) is
**conditional: include only when it carries content**. Delete the heading otherwise.
Never emit `N/A` filler.

`Created` stays in the file, empty, in every mode. `handoff` appends to it when it
is allowed to create issues, and the user fills it in by hand when it is not —
either way, removing it costs a re-run its idempotency and a later `plan` the id.

## Quality bar

- **The title is the change, in the imperative, ≤70 characters.** It shows up in a
  list of forty. `Expire idle sessions after 30 minutes`, not `Session bug`.
- **`Problem` says what is wrong today and for whom**, with a `path:line` when
  grounding found one. No solution in it. A `Bug` says actual vs expected and how to
  trigger it.
- **`Outcome` says what is true when this is done.** One sentence.
- **Acceptance criteria are observable from outside the code**, and each one is
  independently checkable. If a criterion needs the diff to evaluate, rewrite it.
- **`Out of scope` names the trigger** that would bring the item back, not just the
  exclusion.
- **No sentence exists to sound thorough.** Cut every clause that would not change
  what someone does. Context the reader already has from the title is not context.
- **`Labels`** uses only labels the tracker already has — from
  `tracker.create.default_labels` or what the adapter reports. Never introduce a
  label scheme. Priority and size are never labels here — they live on the type
  line, and `handoff` maps them to the tracker's own fields.

## Prohibited output

- Product code, pseudocode, schemas, endpoint signatures.
- A file manifest, or "touch these directories".
- "Decide later" placeholders for core behaviour.
- Acceptance criteria that restate the title.
- A restated `Problem` under `Outcome`, or a `QA step` that repeats an acceptance
  criterion word for word.
- A `What to do` bullet that is an acceptance criterion reworded, or a file, a
  function, or a command in disguise.
- Priority or size left blank, `TBD`, a range (`S–M`), or a value outside the
  scales above.
- Background paragraphs, motivation essays, or a summary of the conversation the
  need came from.
- Ceremony: self-validation checklists, risk tables with no concrete risk,
  definition-of-done boilerplate the tracker already enforces.

## Blocking vs assuming

Same two categories as `plan`, and no third:
`../../plan/references/ambiguity-policy.md`. A blocker stops the draft before
delivery — a ticket that ships with a blocking unknown just moves the question to
whoever picks it up.

## Self-check before finalizing

Run these as checks. Do not emit them into the draft.

- Required sections present; conditional sections carry content or are gone.
- Within size budget — count the lines, do not estimate them.
- Type stated, and it matches what `Problem` describes.
- `Priority` is one of `P0`–`P3`; `P0`/`P1` backed by evidence in `Problem`; an
  inferred `P2` recorded in `Assumptions`.
- `Size` is one of `XS`–`XL`; `XL` only on an epic parent; `L`/`XL` name a driver.
- Single task: `What to do` present, 2–6 bullets, each a concrete change.
- Epic: every subtask row has its own type, priority, size and `What to do`.
- `QA steps` present if and only if the change is visible to a person.
- Title ≤70 characters, imperative, specific.
- Every acceptance criterion is checkable without reading the diff.
- No file paths, no commands, no code.
- Epic: every subtask passes the independence test in `split-policy.md`.
- `Created` present and empty.

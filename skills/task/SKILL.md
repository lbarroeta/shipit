---
name: task
description: Use when a need, idea, bug report or request must become a tracker ticket — typed bug, feature or chore, as a single task or an epic split into independently shippable subtasks — drafted short against the repo's own `.sdd/` contract. Do not use to design the implementation — that is `plan`. It writes a draft to disk and never touches the tracker; creating the issue is the user's move.
metadata:
  input: request
  output: sdd-task-draft
  writes_product_code: false
---

# shipit task

Turn a need into a ticket someone can pick up without asking what it means. This is
the entry of the cycle: `task` produces the ticket, `plan` turns it into a contract,
`implement` executes it.

A ticket answers **what** and **why**, in as few lines as that takes. The **how** is
`plan`'s, and writing it here means writing it twice — once against a repo you only
skimmed, once properly.

This skill ends at the draft on disk. Whether anything creates the issue is
`handoff.allow` in `.sdd/config.json`: with `issue_create` listed, invoke `handoff`
in `task` mode on an explicit yes; without it — the default — the draft is the
deliverable and the user pastes it into the tracker.

## Context budget

- Required: the request, and `.sdd/config.json` — the `tracker` and `paths` blocks.
- Required: `references/output-contract.md`. It owns sections, size budget, and
  prohibited output; this file does not restate it.
- Required in epic mode only: `references/split-policy.md`. Single-task mode must
  not read it.
- Optional, only when an uncertainty surfaces:
  `../plan/references/ambiguity-policy.md`, relative to this skill directory. Same
  two categories, not restated here.
- Never: `.sdd/rules/*`, `.sdd/stack.md`, a whole graph report, the plan template.
  A ticket that needs a layer rule to be written is a plan in disguise.
- No `.sdd/` at all → stop and say: run `/shipit:init` first. Do not detect the
  tracker inline; that is `init`'s job.

## Hard rules

- **No product code, no file plan, no verification commands.** Naming the files to
  touch is `plan`'s output, and doing it here fossilises a guess into the backlog.
- **Prose language.** The ticket draft follows `language.task`; what this skill prints follows `language.plan` in `.sdd/config.json`. Legacy string `language` → that value for every key but `code`; absent → `en`. Identifiers, commit subjects and branch names always stay English.
- **No external side effects.** No git, no PR, no tracker write. The draft file is
  the whole deliverable.
- **Show the draft before delivering.** A ticket in a shared backlog is awkward to
  retract. Show the finished draft and say where it is. With `issue_create`
  allowed, ask once and invoke `handoff` only on an explicit yes — there is no flag
  that skips that. Without it, showing the draft *is* the ending.
- **Acceptance criteria are observable from outside the code.** "Returns a 422" is a
  criterion; "adds a validation to the model" is an implementation detail wearing a
  criterion's clothes.
- **State the type — `Bug`, `Feature`, or `Chore` — on the line under the title.**
  It is what triage filters on first, and a type left to be inferred from the prose
  gets sorted wrong. Each subtask carries its own.
- **Short is the default.** 18 lines for a single task, one table row per subtask.
  A sentence that would not change what someone does is cut, not shortened.
- **Anything a person can see gets `QA steps`** — five at most, plain language, no
  commands and no paths. It is how a non-developer confirms the ticket is done.
  Nothing visible to a person → no section at all.
- **Grounding is bounded**: one graph query or two `rg` passes, and at most three
  files opened. Enough to name the affected area and what it does today, with
  `path:line`. Anything more is `plan` running early on the wrong budget.
- Ambiguity that blocks scope, security, or data → stop with `Blockers`. A ticket
  carrying a blocking unknown is backlog noise that someone else has to re-open.
  Everything else → `Assumptions`, with the default already taken.
- `tracker.create` describes where the draft is *meant* to land — team, project,
  labels, initial state. Echo it so the user pastes into the right place; nothing
  reads it to create anything. Adapter `none` → say the draft is the deliverable.
- Never write to `.sdd/config.json`. A missing `tracker.create` block means the
  config predates it: report the drift and suggest `/shipit:init`, do not patch it.

## Workflow

1. **Preflight.** Load `.sdd/config.json`. Read `tracker.adapter` and
   `tracker.create`. Derive the slug from the need — no issue id exists yet.
2. **Shape.** Single task by default. Epic when the need spans two or more entries
   of `layers[]`, or describes two or more user-visible outcomes that could ship on
   different days. `--epic` and `--single` override the heuristic.
3. **Grounding.** Bounded discovery per the rule above. Name the area and the
   current behaviour. Stop when the problem statement can cite something real.
4. **Draft.** Fill `assets/task-template.md`. Decide the type from the problem, and
   include `QA steps` only when the change has a surface someone can look at.
5. **Split gate** — epic only. `references/split-policy.md` owns the caps and the
   independence test. A split that fails it is reported, not shipped.
6. **Ambiguity.** Blocking → stop at the draft with `Blockers` and skip step 8.
   Otherwise → `Assumptions` with the default taken.
7. **Write.** `<paths.tasks>/<slug>.md` (default `.sdd/tasks`). Drafts are local
   scratch; once created, the tracker is the source of truth.
8. **Show, then deliver if allowed.** Output the draft and its path.
   `handoff.allow` lists `issue_create` → ask, and on an explicit yes invoke
   `handoff` in `task` mode with the draft path. Otherwise stop here; nothing is
   created and the user pastes it into the tracker. `--dry-run` always stops here.
9. **Self-check.** Run `output-contract.md`'s checks as checks. Never emit the
   checklist into the draft.

## Flags

- `--epic` / `--single` — force the shape instead of deriving it.
- `--dry-run` — stop at the draft. Nothing is created, nothing is asked.
- `--plan` — after the draft, run `/shipit:plan` on it. In epic mode it targets
  **the first subtask only**; planning five tickets in one turn is a token bomb, and
  four of the five plans go stale before anyone reads them.

## Final report

- Draft path, and the shape — `task`, or `epic` with the subtask count.
- Adapter, and whether `handoff.allow` permits `issue_create`. Withheld → one line
  saying the draft is the deliverable and where it is meant to land.
- Blockers, or assumptions taken.
- `handoff`'s report, appended verbatim, when it ran. Never re-summarise it.
- Next: create the issue from the draft when nothing did, then
  `/shipit:plan <ISSUE-ID>`.

Never claim a ticket was created. This skill ends at the draft; only `handoff` says
what reached the tracker.

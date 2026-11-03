---
name: task-create
description: Use when a need, bug, feature or chore must become a clear tracker ticket or an epic with independently understandable children. Works as a senior project manager would — surveying the board for duplicates and overlapping work before drafting, then placing the ticket in its outcome, epic and dependency chain. Draft what and why against the repo contract; code-plan owns how. Publishing uses code-handoff only when issue_create is allowed and the finished draft is authorized.
model: claude-sonnet-5-5
effort: high
metadata:
  input: request
  output: sdd-task-draft
  writes_product_code: false
---

# shipit task-create

Turn a need into work another person can pick up without reconstructing the
conversation. `task-create` defines what and why, `task-next` recommends executable
work, `code-plan` decides how, and `code-implement` executes it.

The deliverable is a local draft. `code-handoff` in `task` mode owns tracker publishing,
only when `handoff.allow` lists `issue_create`. Adapter `none` is a valid local
workflow, not a blocker.

Act as a senior project manager: look at what already exists before writing
anything. A ticket that duplicates open work wastes a cycle; a ticket with no
place on the board — no outcome, epic or neighbouring work — is the missing
context that makes it hard to pick up. Decide with evidence and say why.

## Context budget

- Required: the request, `.shipit/config.json` (`tracker`, `paths`, `language`),
  `references/output-contract.md`, and `assets/task-template.md`.
- Required in epic mode only: `references/split-policy.md`.
- Required when `.shipit/product/` exists: the PRD stories, non-goals and MVP
  class the request touches, per `../../references/product-context.md § Who reads what`.
- Optional when uncertainty needs classification:
  `../code-plan/references/ambiguity-policy.md`.
- Ground narrowly: one graph query or two `rg` passes, at most three relevant
  files initially. Read a specific additional source when needed to settle a
  material scope or business-rule question; stop before implementation discovery.
- Board survey, before drafting: a few targeted searches of the configured
  tracker scope — the story ID, the key domain terms and the affected area —
  over open work and closed work; local drafts in `paths.tasks`; `backlog.md`.
  Read the full body of each plausible match, not every hit. Also read the
  active milestone/cycle and the epics in flight the request could belong to.
- Other live tracker reads only when validating referenced dependencies, existing
  labels, or project context. Never infer a dependency from ticket numbering.
- Never bulk-read layer rules, stack docs, a whole graph report or the plan template.
- No `.shipit/config.json` → say run `/shipit:init` first. Do not detect the tracker inline.

## Hard rules

- **No product code, file plan, commands, git or tracker writes.** The skill drafts;
  `code-handoff` publishes. Grounding citations may name existing `path:line` evidence,
  never prescribe files to change.
- **Prose language.** Drafts use `language.task`, reports use `language.plan`.
  Legacy string `language` applies to both; absent → `en`. Identifiers stay English.
- **Problem and Goal are explicit.** Problem describes today's gap and affected
  people or system; Goal describes the intended result and why it matters.
- **What to do defines scope.** Concrete behaviour or deliverables by area, plus
  explicit exclusions where a reader might otherwise expand it. Plan owns details.
- **Observable acceptance and reproducible validation.** Give criteria stable IDs
  (`AC1`, …). QA/validation scenarios state preconditions, action, expected result
  and AC mapping, including relevant failure, boundary and permission cases.
  UI checks are plain language; internal chores use externally measurable system
  evidence. No source-code inspection is an acceptance test.
- **Concise, complete.** Cut repetition and boilerplate; there is no fixed line,
  bullet or scenario quota. Do not cut a scope boundary or expected result to fit.
- **No invented business rules.** Use the request, verified repo behaviour or an
  explicit authorized decision. Ask for essential missing scope, security, data,
  monetary or external-contract behaviour before finalizing. A convenient default
  is not evidence. Reversible editorial choices may be stated as assumptions.
- **No silent duplicates.** Classify each survey match: *duplicate* (same
  outcome), *overlap* (part of the scope is already covered), *related* (same
  epic, area or story; a possible parent, prerequisite or dependent). A duplicate
  or overlap stops drafting until the user picks: use the existing ticket, narrow
  this draft to the uncovered remainder, or create it anyway with the difference
  stated. A match closed as done means the need may be a regression (`Bug`) or
  already delivered; a cancelled match carries a decision to surface, not to
  reverse silently. Never edit, close, merge or comment on existing tickets.
  Survey not possible (adapter `none`, tracker unreachable) → search local drafts
  and `backlog.md` only and report the tracker check as not run; never claim
  there are no duplicates.
- **Place it on the board.** `Related work` names the outcome the ticket advances
  (active milestone/cycle, PRD goal, MVP core-flow step or epic, with evidence)
  and each related ticket with its relation and why it matters here. An existing
  epic that owns this outcome is the parent, not a new epic. Priority is set
  against the board: work outside the outcome it is driving is not P0/P1 without
  impact evidence. A request that would land on a stalled or ownerless area is a
  risk to report. `Related work` is context and never blocks: scope narrowed
  away from an overlap is also an `Out of scope` line naming the ticket that owns
  it, and a match whose output this ticket needs is a Dependency with its unblock
  condition — those are the sections `code-plan` enforces.
- **Product scope is decided upstream.** Cite the stories each task and child delivers
  (`H3`) in its `Source`. A
  request that is a non-goal, a `Deferred` or `Manual` story, or absent from the
  PRD is flagged in the draft's Blockers and the report, with
  `/shipit:product-mvp-cut` to decide it; never edit product docs here.
- **Defined blocked work is valid.** A known prerequisite with a specific unblock
  condition is a dependency; the ticket may be drafted/published as blocked.
  Unresolved essential behaviour is an ambiguity blocker and is not ready for
  publishing or planning. Never conflate these.
- **Dependencies, ordering and hierarchy differ.** A dependency says what cannot
  proceed and exactly what evidence unblocks it. Suggested order is a preference;
  belonging to an epic is hierarchy. Neither automatically blocks a child.
- **Children stand alone.** Each has its own Problem, Goal, What to do, exclusions
  when needed, criteria, scenarios, type, priority, size and dependency conditions.
  A reader need not open the parent to understand the work.
- **Type, Priority and Size required.** `Bug`, `Feature` or `Chore`; `P0`–`P3`;
  `XS`–`XL`. Rubrics live in `output-contract.md`. Only epic parents are `XL`.
- **Never edit config.** Missing `tracker.create`/fields → report drift and suggest
  `/shipit:init`. Preserve `language.task`, `paths.tasks` and handoff `task` mode.

## Workflow

1. **Preflight.** Load config and creation target/field mapping. Derive a slug from
   the need. Adapter `none` still produces a draft.
2. **Survey.** Run the board survey and classify matches. Duplicate or overlap →
   show each match (ID, title, state, link, what it covers) with a recommendation
   and stop for the user's choice; no draft is written yet. Related matches and
   the board outcome feed `Related work`, Dependencies and priority.
3. **Shape.** One coherent outcome → single task even across several layers. Two
   or more separately useful outcomes → consider an epic. An epic in flight that
   owns the outcome → children of it, not a new epic. `--epic` / `--single`
   override; do not manufacture children to satisfy `--epic`.
4. **Ground.** Confirm current behaviour and affected area with bounded discovery.
   Reuse verified business constraints; do not invent limits or permissions.
5. **Define.** Fill the template. Rate type, priority and size. An `XL` single task
   needs a coherent split; `--single` cannot make it executable by hiding size.
6. **Split gate.** Epic only: apply `references/split-policy.md`. Use the index for
   navigation and the full child sections for issue bodies. Identify true
   prerequisites with unblock conditions; keep preferred order separate.
7. **Ambiguity gate.** Ask on essential unknowns. Preserve a partial local draft
   with `Blockers` if unanswered; mark it not ready. Known dependencies belong in
   `Dependencies` and do not invalidate a fully defined blocked task.
8. **Self-check and write.** Apply output-contract checks, fix, then write
   `<paths.tasks>/<slug>.md` (default `.shipit/tasks`). Local scratch; once published,
   the tracker is the source of truth. Preserve an existing Created ledger when
   refreshing the same draft; changed child scope/numbering needs explicit mapping
   reconciliation before reuse, never overwrite verified IDs.
9. **Show and deliver.** Show the finished draft/path. `--dry-run`, withheld
   `issue_create`, adapter `none`, or unresolved ambiguity → stop at the draft.
   Otherwise obtain authorization for this concrete draft; explicit authorization
   already given for publishing it is sufficient. Invoke `code-handoff` in `task` mode
   with the path; only handoff reports what reached the tracker. Respect provider
   capabilities and preserve unsupported relations in prose with an honest report.
10. **Optional plan.** `--plan` selects one executable task after readiness checks.
   Published work → `/shipit:task-next` scoped to these created IDs, then invoke
   `/shipit:code-plan` on the recommendation. Local draft → apply the same readiness policy from
   `../task-next/references/readiness-policy.md` to the complete task/children;
   verify referenced live prerequisites and rank eligible children by explicit
   priority/order. Never select the first row blindly. Unknown or unmet conditions
   → report blockers; do not plan. `--dry-run` stops before this step.

## Flags

- `--epic` / `--single` — shape, subject to coherent scope.
- `--priority <P0|P1|P2|P3>` / `--size <XS|S|M|L|XL>` — parent values in epic mode;
  children are rated individually. User values win; report conflicts with scope.
- `--dry-run` — draft only, no publishing question or planning.
- `--plan` — recommend/select one ready task, then invoke `shipit:code-plan`; no automatic epic plan.

## Final report

- Draft path, shape and readiness: ready, defined but blocked, or ambiguity-blocked.
- Board survey: scope and searches run, each match with its classification and
  the user's decision, the outcome the ticket advances; or `not run` and why.
- Type, priority, size and inferred values; child count and values for epics.
- Target/field mappings from config, or unmapped/drift; adapter `none` → draft is
  the deliverable. Never probe fields merely to improve the report.
- Dependencies and exact unblock conditions; unresolved questions or assumptions.
- Handoff report verbatim when invoked, including unsupported/pending relations.
- For `--plan`, selected ID/local child, rationale and plan path, or why none is
  executable. Otherwise next: publish the draft, then `task-next` or `code-plan <ID>`.

Never claim creation unless handoff verified it.

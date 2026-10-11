---
name: task-create
description: Use when a need, bug, feature or chore must become a clear tracker ticket or an epic with independently understandable children. Draft what and why against the repo contract; code-plan owns how. Publishing uses handoff only when issue_create is allowed and the finished draft is authorized.
metadata:
  input: request
  output: sdd-task-draft
  writes_product_code: false
---

# shipit task-create

Turn a need into work another person can pick up without reconstructing the
conversation. `task-create` defines what and why, `task-next` recommends executable
work, `code-plan` decides how, and `implement` executes it.

The deliverable is a local draft. `handoff` in `task` mode owns tracker publishing,
only when `handoff.allow` lists `issue_create`. Adapter `none` is a valid local
workflow, not a blocker.

## Context budget

- Required: the request, `.sdd/config.json` (`tracker`, `paths`, `language`),
  `references/output-contract.md`, and `assets/task-template.md`.
- Required in epic mode only: `references/split-policy.md`.
- Optional when uncertainty needs classification:
  `../code-plan/references/ambiguity-policy.md`.
- Ground narrowly: one graph query or two `rg` passes, at most three relevant
  files initially. Read a specific additional source when needed to settle a
  material scope or business-rule question; stop before implementation discovery.
- Live tracker reads only when validating referenced dependencies, existing labels,
  or project context. Never infer a dependency from ticket numbering.
- Never bulk-read layer rules, stack docs, a whole graph report or the plan template.
- No `.sdd/` → say run `/shipit:init` first. Do not detect the tracker inline.

## Hard rules

- **No product code, file plan, commands, git or tracker writes.** The skill drafts;
  `handoff` publishes. Grounding citations may name existing `path:line` evidence,
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
2. **Shape.** One coherent outcome → single task even across several layers. Two
   or more separately useful outcomes → consider an epic. `--epic` / `--single`
   override; do not manufacture children to satisfy `--epic`.
3. **Ground.** Confirm current behaviour and affected area with bounded discovery.
   Reuse verified business constraints; do not invent limits or permissions.
4. **Define.** Fill the template. Rate type, priority and size. An `XL` single task
   needs a coherent split; `--single` cannot make it executable by hiding size.
5. **Split gate.** Epic only: apply `references/split-policy.md`. Use the index for
   navigation and the full child sections for issue bodies. Identify true
   prerequisites with unblock conditions; keep preferred order separate.
6. **Ambiguity gate.** Ask on essential unknowns. Preserve a partial local draft
   with `Blockers` if unanswered; mark it not ready. Known dependencies belong in
   `Dependencies` and do not invalidate a fully defined blocked task.
7. **Self-check and write.** Apply output-contract checks, fix, then write
   `<paths.tasks>/<slug>.md` (default `.sdd/tasks`). Local scratch; once published,
   the tracker is the source of truth. Preserve an existing Created ledger when
   refreshing the same draft; changed child scope/numbering needs explicit mapping
   reconciliation before reuse, never overwrite verified IDs.
8. **Show and deliver.** Show the finished draft/path. `--dry-run`, withheld
   `issue_create`, adapter `none`, or unresolved ambiguity → stop at the draft.
   Otherwise obtain authorization for this concrete draft; explicit authorization
   already given for publishing it is sufficient. Invoke `handoff` in `task` mode
   with the path; only handoff reports what reached the tracker. Respect provider
   capabilities and preserve unsupported relations in prose with an honest report.
9. **Optional plan.** `--plan` selects one executable task after readiness checks.
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
- Type, priority, size and inferred values; child count and values for epics.
- Target/field mappings from config, or unmapped/drift; adapter `none` → draft is
  the deliverable. Never probe fields merely to improve the report.
- Dependencies and exact unblock conditions; unresolved questions or assumptions.
- Handoff report verbatim when invoked, including unsupported/pending relations.
- For `--plan`, selected ID/local child, rationale and plan path, or why none is
  executable. Otherwise next: publish the draft, then `task-next` or `code-plan <ID>`.

Never claim creation unless handoff verified it.

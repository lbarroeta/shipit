---
name: sync
description: Reconcile an initialized repository's Shipit context with current sources before planning or after implementation. Update affected contracts and documentation, preserve human decisions, report conflicts, and migrate older configuration. Use init for setup and `.sdd/` migration, and design-system for design decisions.
metadata:
  writes_product_code: false
  output: synchronized-contract
---

# shipit sync

Keep the repository context trustworthy. The recurring cycle is:
`sync → code-plan → code-implement → sync → code-handoff`.
`init` creates the first contract; this skill maintains it. A sync is complete
only when its reviewed scope has no unresolved conflicts or required validation.

## Inputs and ownership

Accept `/shipit:sync` for all detected drift, `--check` for read-only inspection,
`--upgrade` for config migration only, or a coordinator's `before-plan` / `after-implement`
phase with issue, plan, implementation report and run-owned paths. Both phases use
the `sync` route in `run/assets/models.json`; standalone execution uses the hosting
session's model. Do not spawn a pipeline or invoke handoff.

Read `.shipit/config.json`, then `references/reconciliation.md`. Load the init schema
and only the affected recipes/templates from `../init/references/` and
`../init/assets/`. These are shared evidence recipes, not instructions to initialize
again. No config → stop with `/shipit:init`; a legacy `.sdd/config.json` without
`.shipit/config.json` → stop too: `/shipit:init` migrates it. Corrupt config or
a newer schema → report the gap; never reset it from a template.

- Own `.shipit/config.json`, `stack.md`, `conventions.md`, generated layer/test
  rules, `.shipit/sync-state.json`, and the `shipit:contract` block in `docs.pointer`.
- Preserve user choices, explicit overrides and unknown extension keys. A default
  is for first setup; it must not reset existing preferences during sync.
- Preserve all `shipit:design` blocks and design files. Report design drift to
  `shipit:design-system`; do not turn a new implementation into an approved design.
- Product context follows `../../references/product-context.md`: apply status
  edits the delivered change proves, propose decisions as patches, repair the
  `shipit:product` block. Product docs outside `.shipit/` → report them as
  migration candidates for `/shipit:init`; never move them here.
- Human docs outside generated blocks are not owned. Correct a named factual
  section when the request/approved plan authorizes it; otherwise propose its exact
  patch. Preserve deliberate policies and decisions even if code violates them.
- No product code, dependencies, branch/commit/push, tracker write, permission
  expansion, tool installation or secrets. No mutation of another checkout's
  shared/symlinked contract or graph. A needed repair belongs to its owner.

## Workflow

1. **Inspect before writing.** Confirm checkout, inspect Git changes and identify
   ownership; an implementation report supplies scope, not permission to adopt
   unrelated edits. Run the stdlib helper (Python 3.10+):
   `python3 <plugin>/skills/sync/scripts/context_state.py --repo <repo> inspect`.
   It compares content hashes, file modes and symlink targets, including additions
   and deletions. Read affected baseline entries from `.shipit/sync-state.json` only
   as needed. Missing baseline means legacy/unknown ownership, not pristine output.
   `--check` reports drift and exits without migration, writes or graph updates.
2. **Determine scope.** Before planning, reconcile accumulated drift that affects
   the task, plus shared configuration. After implementation, use the actual diff,
   plan and report to find affected contracts/docs, product context included;
   check for additional external changes. A report cannot hide files absent from its manifest. Read changes to
   manifests, CI, agent instructions, rule exemplars and related sources. A new
   HEAD alone does not require regeneration. Check external tracker reachability
   and referenced targets when relevant; local hashes cannot prove remote freshness.
   Check configured executables and companion availability even with unchanged
   sources: a different host or removed tool can invalidate availability evidence.
3. **Migrate and rediscover.** Apply required config migrations per the reference.
   Use a graph query first when an existing graph and CLI are available, then
   verify its claims in current source. Check freshness metadata; missing metadata
   means unknown. Use scoped source discovery for stale or missing graph coverage.
   Rediscover affected facts with the shared detection recipes. Keep evidence per
   claim and honest command proof levels. Do not promote one changed file into a
   repo-wide convention; compare relevant peers and accepted decisions.
   A dependency, framework or runtime moved a major/minor version → follow the
   reference's **Dependency drift** with `../../references/docs-lookup.md`, so
   versions, generated rules and conventions describe the installed versions
   rather than the ones init saw.
4. **Reconcile.** Compare last accepted generated content, current content and
   newly detected candidate. Follow ownership rules and deletion handling in the
   reference. Show meaningful diffs; apply unambiguous generated updates. Preserve
   human edits; ask only for an actual conflicting decision. Essential conflict →
   blocked with paths and evidence; no false current baseline. Nonessential drift
   outside task scope is reported as pending, not silently marked resolved.
5. **Validate context.** Parse config, check schema semantics, paths/exemplars,
   unknown entries and pointer uniqueness. Every configured command has evidence
   for its actual proof level. Run affected documentation checks. If sync changes
   a command or reveals a required check, execute that check against final files;
   failure returns to the builder in a run. Sync never repairs product code to
   make a check pass. Keep existing product validation only when its inputs still
   match. After final edits, maintain the existing graph using the reference's
   structural/semantic update paths; a CLI-only refresh cannot certify docs.
   Preserve design protection throughout.
6. **Record only reviewed state.** After a complete reconciliation, prepare an
   inventory outside the repository with `managed` (all init/sync-owned generated
   file paths) and `unresolved: []`. Run
   `python3 <plugin>/skills/sync/scripts/context_state.py --repo <repo> record --inventory <json>`.
   Include unchanged managed files; exclude design, human docs, plans and drafts.
   The helper saves exact accepted bases plus hashes; it does not infer ownership
   or approve content. If any scope remains unreviewed/conflicted, retain the old
   baseline and report partial/blocked. A scoped run must review/classify all
   outstanding drift before advancing the global baseline. No differences → no
   rewrites, including dates. A failed/partial run never certifies freshness.
7. **Report.** State phase, baseline status, changed/retired/preserved paths,
   documentation conflicts, separate structural/semantic graph state, exact
   validation and remaining unknowns, including `docs-lookup.md`'s one-line
   notice when a lookup could not be made.
   Use `language.plan`. Return `completed`, `blocked` or `failed`, with concrete
   scope; missing evidence is not success.

After implementation, in standalone and coordinated runs, check `PR Preparation`
against the final changes and validation evidence. Write a separate **delivery
report** based on the builder's report template: retain QA, AC coverage and
validation evidence; include final contract/doc edits in `Files Changed`, with
exact new checks and links to original evidence. Handoff receives this final
report; preserve the original builder report. Use
`../code-implement/assets/pr-description-template.md`: update the delivery copy
when sync changes reviewer-relevant behavior, documentation or check results;
keep material risks and pending checks visible and full QA/evidence accessible.
Do not append a sync log to the body. Missing implementation facts return to the
builder through the caller; never invent them. Never relabel a failed check as
passing. A material contradiction with plan scope returns to the caller for
replanning; a check failure returns to implementation. Do not dispatch either
agent yourself.

## Coordinated runs

`run` invokes this skill twice, as separate checkpoints `sync_before` and
`sync_after`, both using route `sync`. Read its supplied result contract. Save
artifacts outside the checkout in the run directory. Return the full non-ignored
ownership manifest, including pre-sync edits and generated plans; omit plans from
any delivery manifest. No external effects.

Before planning, run the read-only `inspect` and step 5's context validation
first. No drift in shared configuration or in sources the issue touches → return
`current` with the existing baseline and the ownership manifest; skip
rediscovery, docs lookups and graph work. Otherwise continue the full workflow
for the affected scope only. Return the sync report and owned paths for the
planner/builder.
After implementation, return the separate delivery report described above to the
coordinator.

## Flags

- `--check`: local inspection and relevant read-only checks; no writes or baseline
  certification. Report `current`, `stale`, or `unknown`, and what remains to inspect.
  Version drift is listed by package and versions; docs lookups wait for a normal sync.
- `--upgrade`: migrate only config using `references/reconciliation.md`. It does
  not certify docs or graph freshness or record a new context baseline. Normal
  sync also applies needed migrations before rediscovery.
- `--language <tag|key=tag,...>` and `--tracker <adapter>`: explicit preference
  changes, using init's accepted formats; validate and reconcile dependent fields.
  A tracker change re-resolves its target and mappings; never keep another
  adapter's target accidentally. These flags are incompatible with `--check`.

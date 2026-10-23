# Reconciliation and migration

## Baseline contract

`docs/shipit/sync-state.json` is a versioned machine baseline, committed with the
contract. It stores source fingerprints, contract fingerprints and accepted text for
each generated file — for a human doc, only its `shipit:generated` section, so an
edit elsewhere in that doc is a contract change, never a managed edit. It contains no source bodies or secrets
other than the already public contract text; never put secrets in that contract.
The helper's `inspect` is read-only; `record` writes only this baseline atomically.
Do not edit it by hand to make drift disappear. `generated_at` records creation,
not ownership or freshness; preserve it on no-op sync.

Source inventory covers tracked and non-ignored untracked files, excluding graph
outputs, `docs/shipit/`, plans/tasks and the configured stack, conventions, design
and rule paths; contract fingerprints cover those files separately. Other docs are
sources: a changed human doc is drift worth reviewing. Ignored inputs,
external docs, submodule internals, tracker state and graph semantic coverage need
explicit inspection when relevant. An unchanged hash report alone is not proof
those dependencies are current. A failed graph update never certifies the graph.

First init records only artifacts it just generated. For legacy repos without a
baseline, treat every existing file as potentially human-edited: build candidates,
show differences and reconcile before adopting accepted content as a baseline.
Do not require a complete reset or overwrite to migrate.

## Ownership and merge

For each managed file compare **base** (last accepted output), **current** (disk),
and **candidate** (new evidence):

| Comparison | Action |
| --- | --- |
| Current equals base | Apply candidate if different; otherwise preserve bytes |
| Candidate equals base | Keep current human edit; verify it against relevant evidence |
| Both changed in separate sections | Merge non-conflicting edits and show diff |
| Both changed the same fact/decision | Preserve current, report evidence and request resolution |
| No base | Conservative comparison; do not claim no human edits |

When comparing layer-rule text, carry `shipit:design` blocks byte-identically
and compare generated content outside those blocks. A design block alone is not
a human edit requiring confirmation. The base includes accepted human contributions
after reconciliation. Never replace
an entire config from the template. Merge keys recursively; preserve extension keys.
For config values, apply these policies even when a file looks wholly generated:

- Preserve `language`, `handoff.allow`, `run.models`, `markers`, `docs.pointer`,
  custom `paths.*`, and explicit worktree enabled/root/base/link/setup settings. Missing preferences use documented legacy defaults or a required
  question; do not rerun init's default-setting recipes on existing values.
- Refresh evidence-derived stack, source/test roots, commands/proofs, CI, tests,
  layers and companion availability. A manual override identifiable against base
  is kept if valid; a conflict is surfaced, not silently reverted.
- Keep recorded tracker adapter/target and explicit field names while still valid.
  Recheck unresolved or absent capabilities when reachable. Connection failure
  means unverified, not absent: preserve choices, record unknown, do not switch
  adapters. A connected tracker contradicting recorded identity requires resolution.
- Maintain task, `CLAUDE.local.md` and graph exclusions through Git's resolved
  info/exclude path; do not assume `.git` is a directory in worktrees. A contract
  file that Git ignores is reported; never untrack files or change team policy.
- `worktree.share_graph` follows actual graph location/exclusion; never overwrite
  an explicit decision or mutate a shared target to make detection pass.

A disappeared layer/test kind retires its generated rule and corresponding config
entry only when its last accepted base matches current bytes and no human/design
content would be lost. Otherwise preserve the file, mark conflict and identify
references that need correction. Do not delete design files, plans or drafts.
A moved exemplar must be re-resolved in source; do not keep a dangling `path:line`.
Respect configured rules paths everywhere, including pointers and templates.

## Documentation and decisions

Reuse the init pointer block, substituting configured paths, in `docs.pointer`.
Replace only its markers; keep surrounding bytes and every design block. Repair a
missing pointer per init's *Discovery pointer* — a missing `CLAUDE.local.md` is
recreated in this checkout; never create a second block or add one to a team agent
doc that has none. Resolve symlinks
before writing: updates belong to their actual owning checkout.

Record a doc contradiction persistently in `stack.md`'s discrepancy table with
source evidence and pending resolution, not only in chat. A factual claim such as
an absent command can be disproved by source. A policy/architecture/design decision
cannot be superseded just because current implementation violates it. Essential
contradictions block downstream work until resolved. Accepted plan/request may
already authorize a precise human-doc correction; otherwise return a proposed
patch and the needed decision. Do not mass-regenerate README or user docs.

## Dependency drift

Triggered when a manifest, lockfile or runtime pin moved a dependency the contract
names (`stack.*`, a rule's exemplar or guidance) by a major or minor version, or
when no recorded version exists yet for a framework the rules lean on. Patch-only
bumps refresh the version text and stop there.

1. Read installed versions from lockfiles/pin files, never declared ranges.
2. For each moved framework/runtime/library the rules or conventions mention:
   `../../../references/docs-lookup.md`, asking for the upgrade/migration notes and
   deprecations between the old and new version. Budget per that file.
3. Apply by ownership, through the normal base/current/candidate merge:
   - `stack.md` — version value and evidence: owned (whole file or its section),
     update with the citation.
   - Generated rules and `conventions.md` that recommend an API now deprecated or
     removed at the installed version: owned, candidate cites the docs and the
     replacement. A human edit on that fact → conflict, never a silent rewrite.
   - Human docs (README, agent docs, ADRs) stating the old behaviour: proposed
     patch with the citation, not an edit, unless the approved plan names it.
   - The exemplar paths those rules cite, when they still use the deprecated
     API: pending follow-up with paths and the replacement. No repo-wide scan;
     sync never edits product code.
4. No docs source → update versions from lockfiles only, report the deprecation
   review as `unknown`, not done, and add `docs-lookup.md`'s one-line notice.

A newer upstream version than the installed one is never a reason to change the
contract; it is at most a line in the report.

## Command evidence

Follow detection recipes, preserving `{path}` / `{base}` placeholders. Record
`commands_verified.<key>` with exact proving command, exit and proof kind:
`resolve`, `version`, `help`, `dry-run`, or `real`. Resolution/version/help proves
availability only; dry-run proves accepted invocation, not runtime correctness.
`test_one` requires a real existing test. Setup/build/full-suite need not run for
availability detection, but must never be reported as successfully executed.
Failures become null plus `unknown[]`; consumers must distinguish unknown from
verified absence. If a new/changed check is required for delivery, it needs a real
successful execution in the final validation report.

## Graph lifecycle

Use existing query/explain/path commands to guide discovery and validate facts in
current source. Ordinary sync maintains an existing graph in its owning checkout,
both standalone and at each run checkpoint. Inspect graph freshness independently
of the Shipit baseline: a previous source-verified sync may have left graph work
pending. After reconciliation and final source/doc edits, choose the update path:

- Code-only drift with verified current semantic coverage: run the configured
  update command (supported structural default: `graphify update .`). Its success
  proves a structural refresh, not a semantic refresh of documentation.
- New, changed or deleted docs, contracts or other semantic inputs in the indexed
  corpus, or unknown/stale semantic coverage: load the available `graphify` skill
  and its incremental-update reference, then execute `/graphify <repo> --update`.
  This is an agent skill invocation, not a shell command. Follow its supported
  incremental detection, extraction, merge and output regeneration; reuse cached
  unchanged content and prune deleted sources. The host agent can perform semantic
  extraction without a new API key. Preserve corpus exclusions, graph direction
  and output settings; do not expand indexing to excluded contracts or secrets.
- No indexed drift and verified coverage: leave graph outputs unchanged.

Normal sync authorizes this local incremental maintenance. Never install or upgrade
tools or perform a full graph rebuild as an implicit fallback. Missing semantic
skill/runtime → use the available structural update where useful, but report the
semantic gap. Missing graph → source discovery and optional setup recommendation.
Shared graph → report its owner and defer mutation there, including any local source
changes that the shared graph does not represent.

Report structural and semantic status separately (`current`, `stale`, `unknown`,
or `not-applicable`), with scope, update evidence and pending files. Failed/omitted
extraction remains pending for the next sync; never stamp it as processed. A new
Shipit baseline does not certify graph freshness. Graph gaps alone do not block a
source-verified contract, but downstream skills must use source evidence for those
gaps. `--check` only inspects; `--upgrade` never updates the graph.

## Config upgrades

Read `../../init/references/config-schema.md § Upgrades`, the current template and
plugin version. Compare semantic versions, never lexicographically. Newer config
than plugin → stop; no downgrade. Older → apply migration rows in order, preserving
existing values unless a row explicitly transforms them. Fill missing nested keys
without replacing existing objects; absent asked fields follow schema rules.
Keep explicit empty allow-lists and model overrides. Then update `shipit_version`.
Show config diff. Apply mechanical migrations within sync authorization; ask only
for missing decisions or real conflicts. Normal sync continues with detection.

`--upgrade` stops after this config operation. Same version still checks missing
schema keys; never report a malformed same-version config as current. Report
"configuration migrated; repository context not revalidated". Keep the previous
baseline so a later normal sync detects the change. No baseline file is needed
for config-only migration, and no docs/graph/pointer is modified by this mode.

# Input baseline

Use the same explicit inputs regardless of model. Preserve sources and unresolved
gaps so the implementer can distinguish accepted requirements from inference.

## Request and decisions

Read the user request or task draft, Goal (legacy `Outcome` accepted), original AC
IDs and QA scenarios, scope boundaries, prerequisite conditions/evidence, and
accepted decisions. Resolve referenced issues and current updates via the
configured tracker. Apply readiness before the Planning status transition. Do
not treat inaccessible inputs as empty or silently replace a source requirement.

If local request criteria lack IDs, assign stable `AC-1`, `AC-2`, etc. in source
order; do not renumber existing IDs. Clarifications are attached to the affected
criterion, not used to erase it. Capture only sources and decisions relevant to
this request; do not dump whole conversations or tickets into the plan.

## Repository and rules

In the checkout used for discovery, record:

- Repository/root, branch (or detached HEAD), and exact HEAD revision. Non-Git
  checkout → say revision unavailable and identify the directory; never invent one.
- Current tracked/untracked status, then relevant staged and unstaged diffs and
  relevant untracked content. Inspect file content when an index/worktree split
  matters. Unrelated dirty paths need not be read; state they were excluded.
- Applicable `.shipit/config.json`, `.shipit/conventions.md`, layer/test rules, and
  relevant agent rules. Design context only when required by the skill.

Use `git status --short`, `git rev-parse HEAD`, and scoped diff/read operations;
these are discovery reads, not plan validation commands. Do not stash, reset,
commit, or adopt user changes. Note whether a proposed change relies on relevant
uncommitted work and whether ownership/meaning is unclear. Essential conflicts
block; harmless unrelated changes do not. An opted-in worktree may differ from
the original checkout: record and plan from its actual baseline, not the old one.

Record the applicable rule paths in `Baseline`; add a rule section/symbol reference
when it controls a decision. If accepted requirements conflict with rules or the
current code, expose the conflict instead of silently choosing one. Source code
is evidence of current behavior, not authority to override the requested behavior.

## Before finalizing

Recheck HEAD and relevant dirty state/content after discovery. If changed during
planning, revisit affected evidence and decisions or report the exact conflict.
Record the baseline actually inspected, not merely the branch name. A dirty
baseline is a description, never permission for `code-implement` to overwrite it.

The plan needs enough baseline detail to detect drift (revision, relevant paths
and the changes relied upon), not a copy of the full diff. If an essential source
or decision remains unavailable, record it under `Blockers`.

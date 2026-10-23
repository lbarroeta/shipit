---
name: code-implement
description: Use when an approved shipit plan must be executed, verified, and prepared for QA. Runs the repo's own verified commands from `.sdd/config.json`. Do not use to redesign scope, and not for git or PR delivery — that is `code-handoff`.
metadata:
  input: sdd-plan
  output: implemented-change
  writes_product_code: true
---

# shipit code-implement

Execute the approved plan. The plan is the contract. The code is minimal, scoped,
and verified with commands that are known to run in this repo.

## Context budget

- Required: the full plan, `.sdd/config.json`, `.sdd/conventions.md`.
- Required: the `.sdd/rules/<layer>.md` for each layer the plan touches, and the
  `.sdd/rules/tests/<kind>.md` for each test it plans. Only those.
- Required: `../../references/lean-ladder.md`, relative to this skill directory.
- Required: `references/validation-standards.md`. Every run validates.
- Required only when the plan touches UI and `<paths.rules>/design.md` exists:
  that file, and the `.sdd/design-system.md` sections the plan's `Design` names.
  Backend-only → never.
- Required when the change creates or modifies entry points (routes, handlers,
  jobs, webhooks), authorization, scoped data access, trust-boundary input, secret
  handling, or query/shell construction: `references/security-standards.md`.
  Apply these triggers to support changes discovered during implementation too.
- Required only when a trigger in `../../references/docs-lookup.md` fires — code
  written against an external API that no cited analogue shows at the installed
  version, or a check failing on an API assumption: that file. This skill is the
  only one in the cycle that looks up API docs; the plan does not.
- Never bulk-load every rule file or every agent doc. Resolve symlinked docs once.
- If a rule was skipped, do not claim compliance with it.

## Hard rules

- Require an approved plan. Missing → stop and ask.
  In a coordinated `shipit:run`, an explicit user request to execute the fetched
  issue authorizes the plan within its acceptance criteria after the coordinator's
  contract check. Require that recorded request and scope in the delegation;
  never infer approval from the planner's output or claim human plan review.
- **Prose language.** Report and QA guide follow `language.plan`; the PR description follows `language.pr`; comments written in code follow `language.code` (default `en`) — never `language.plan` — in `.sdd/config.json`. Legacy string `language` → that value for every key but `code`; absent → `en`. Identifiers, commit subjects and branch names always stay English.
- No scope expansion. No redesign. No new abstraction. No dependency upgrade.
- No behaviour change outside the plan.
- No weakening of authorization, scoping, security, or existing tests.
- No edits to credentials, secrets, env files, or production config unless the plan
  explicitly requires and approves it.
- No TODO standing in for required behaviour.
- **No fake validation.** "Passed" only when the command actually ran and exited 0.
- No more than 3 attempts on the same failing test, lint, or check without new
  evidence. After that, stop and report.
- Never run `git commit`, `git push`, or a PR command. Delivery happens only by
  invoking `code-handoff`, and what it then does is `handoff.allow`'s call — with
  `tracker_comment` withheld, the QA steps stay in the report for the user to post.
- **Comment only what the code cannot say.** Match the file's existing comment
  density — neighbouring functions carry none, yours carries none. No comment
  restating the line below it, no section banners, no narration of the plan, no
  changelog of what this run changed. Allowed: a non-obvious *why*, a debt marker,
  a doc comment the repo's convention already requires. A comment that would
  survive `git log` telling the reader the same thing is not one.
- **Short by default, everywhere.** Report prose, PR body, and chat output state
  the fact and stop. No restating the diff in words, no re-explaining a section the
  reader just read. Non-developer QA steps are the one exception — written in full
  for someone who does not read code, even under a terse-output mode.

## Workflow

1. **Preflight.** Read the plan. If it has a `Worktree` section, confirm you are in
   the worktree it names — wrong location is the most common way this run edits the
   wrong branch. No such section → the current checkout is correct; do not create a
   worktree and do not go looking for one. Check
   `git status` and detect changes you did not make. Inspect only the files the
   plan names. If it has `Baseline`, compare the recorded revision and relevant
   dirty state with the current checkout; inspect relevant drift before trusting
   its evidence. A new HEAD alone is not a blocker if affected contracts still
   hold. Follow `Evidence`, AC links and real `Sequence` dependencies when present.
   Legacy plans may omit these sections: verify equivalent behavior/coverage during
   preflight rather than rejecting their format. Search for more when the plan
   lacks detail or relevant drift needs checking; a graph query
   before `rg` when `graph` is set and its output is present.
2. **Contract gate.** The plan must have a goal, acceptance criteria, a `Files`
   table with analogues, tests mapped to rule files, `Manual QA` when UI is
   touched, and no unresolved blockers. Missing → stop with
   `# Implementation Blocked`. Plans are deliberately terse: verification commands,
   red/green sequencing, and repo conventions are owned by this skill and by
   `.sdd/*`, not by the plan. Their absence is correct, not a gap. Verify each AC
   has a change or already-met behavior and observable validation, including
   affected consumers/regressions. Missing new section names or explicit AC links
   in a legacy plan alone is not a blocker; unresolved essential behavior,
   uncovered acceptance, or conflicting evidence is.
3. **Test first.** For planned automated tests, where practical: write the failing
   test → run it with `commands.test_one` → confirm the expected red → minimal
   code → re-run → next layer. An **unexpected** red is investigated before any
   production change.
   `commands.test_one` null or missing `{path}` → say the loop is degraded and run
   the configured `test_all` instead. Neither is runnable → report the required
   validation gap under `validation-standards.md`; never silently skip the loop.
   A plan requiring no automated tests does not need an artificial red/green loop.
4. **Implement.** The smallest correct change. Repo patterns over new structure —
   including their comment density. Apply the ladder as stance, not as licence to
   deviate from the plan. A deliberate shortcut leaves a debt marker with its
   ceiling and upgrade trigger. External API not shown by a cited analogue →
   `docs-lookup.md` before writing the call, never from memory; a
   failing check on an unknown method, signature or deprecation → look it up
   before the next attempt, which is the new evidence the 3-attempt rule needs.
   Cite a lookup in the report's `Known Risks or Follow-ups` only when it changed
   the code or left a follow-up. UI work uses the components, tokens and states the
   plan's `Design` names, under `rules/design.md`; a value or component the
   contract lacks is not invented — no exception in the plan → stop and say which.
   A plan with no `Design` section dated before the contract's `Status` date gets
   the rules applied directly and a line under `Known Risks or Follow-ups`. Dated
   after it → the contract gate fails: `Design` is missing.
5. **Docs sync.** The plan has a `Docs impact` section → apply each listed edit,
   scoped to the named sections, and list the docs in `Files Changed`. No doc
   rewrites. If the implementation drifted in a way that hits a docs trigger the
   plan missed, update the doc and note it under `Known Risks or Follow-ups`.
6. **Validate.** `references/validation-standards.md`, against the final code,
   tests and docs. Cover each AC and planned regression with executed evidence or
   explicitly pending human/external QA; preserve the plan's validation intent.
   Run scoped tests and applicable configured checks, including build when needed.
   The full suite needs a reason named in that reference. Report exact commands
   and exit codes; later edits invalidate affected results. UI changed with a
   design contract → each `rules/design.md` § Verify check, as met, not met, or
   not checked, with evidence or the missing prerequisite.
7. **QA guide.** Preserve every planned manual/external scenario, including
   backend checks, with its AC, prerequisites, expected result and actual status.
   Non-developer checks become plain-language actions in the browser or external
   service: URL/environment, role, setup data, numbered steps, expected results,
   screenshots needed and pass/fail notes. No framework names, class names or
   terminal commands there; technical checks belong in Validation with their
   executor and evidence or next step. Backend only → say
   `Backend only. Manual UI QA not applicable.` and state developer coverage;
   this does not remove backend manual/external checks. Pending QA is never passed.
8. **PR text.** Compose the title and body from
   `assets/pr-description-template.md` into the report. Write it; do not post it.
   Lead with problem and resulting behavior; summarize final validation and keep
   material risks and pending checks visible. Preserve full QA/evidence using the
   template's details/link rules. Apply its relevance and length guidance before
   returning the report; do not export the report's full section structure.
9. **Return for context sync.** Return the implementation report, full changed-file
   manifest and exact validation evidence to the caller. The next stages are
   `shipit:sync` then `shipit:code-handoff`; do not dispatch either internally.
   `run` owns those stages when coordinated. Standalone work follows the same
   explicit sequence. Failed or unverified required checks remain blockers.
   Graph maintenance belongs to sync so it includes final documentation changes.

## User change protection

Uncommitted changes are user-owned unless this run made them. A `shipit:run`
delegation may name generated plans and sync-produced contracts as run-owned artifacts; verify that path
and the saved run record before treating it as such. On resume, pending manifests
and archived revision manifests establish ownership only for paths whose saved
content hashes still match. Verify those hashes before continuing prior edits.
This does not grant ownership of other pre-existing changes. Stop before editing
when a required file has changes you did not make, when existing changes make the
plan ambiguous or risky, or when the plan would revert user work. Report the
conflicting paths, why they conflict, and the exact decision needed. Unrelated user
changes: leave them alone and proceed.

## Allowed changes

Plan-named code, tests, templates, styles, client-side code, migrations, routes,
policies, services, and jobs. Doc edits listed in `Docs impact`, scoped to the
named sections. Small support changes required to make planned behaviour work.
Lint fixes in files you already touched. Tests demanded by the coverage gate for
behaviour you changed.

## Forbidden changes

Broad refactors, unrelated cleanup, dependency upgrades, UI redesigns, new
abstractions with no plan reason. Public behaviour change outside the plan. Test
rewrites outside planned behaviour. Deleting or weakening tests to go green.
Touching the user's uncommitted work.

## Blocker conditions

Stop when: the plan is missing, has unresolved blockers, or lacks contract detail;
acceptance criteria contradict each other; security or scoping is unspecified; the
plan requires destructive data work without explicit approval; the plan conflicts
with `.sdd/*`; user changes conflict with planned edits; a major decision is needed
that the plan does not contain; or the same check failed 3 times without new
evidence.

`# Implementation Blocked` when no product code changed yet,
`# Implementation Incomplete` when it did. Both use:

```markdown
# Implementation <Blocked | Incomplete>

## Problem
<Concrete issue.>

## Why the current plan is unsafe or incorrect
<Technical risk.>

## Recommended correction
<Smallest correction needed.>

## Files inspected
- <path>
```

Include the exact failing command output when the stop came from repeated failures.

## Final output

Use `assets/implementation-report-template.md`. Sections in that order: QA Handoff,
QA Steps For Non-Developer, Plan, Summary, Files Changed, Tests Added/Updated,
Validation Commands Run, Security Notes, Handoff, Known Risks or Follow-ups,
PR Preparation.

## Flag

`--defer-handoff`: validation and report only; no delivery agent or external side
effects. Retained for compatibility; standalone execution also returns before sync/handoff.

---
name: code-review
description: Use when an implemented shipit change must be reviewed before context sync and delivery — after `code-implement`, or as `run`'s review stage. Runs the ponytail plugin's `ponytail-review` against the diff, plus the plan and repo contract. Read-only. Do not use to fix code (`code-implement`), resolve PR threads (`pr-fix`), or deliver (`code-handoff`).
metadata:
  input: implemented-change
  output: review-report
  writes_product_code: false
---

# shipit code-review

Review the implemented change the way the senior engineer who gets paged when it
breaks would. The review engine is the ponytail plugin's `ponytail-review`; this
skill scopes it to the shipit contract and turns its findings into a verdict the
next stage can act on. It never edits code.

## Context budget

- Required: the plan, the implementation report, `.shipit/config.json` and
  `.shipit/conventions.md`.
- Required: the `.shipit/rules/<layer>.md` for each layer the diff touches and the
  `.shipit/rules/tests/<kind>.md` for each test it adds or changes. Only those.
- Required: `../../references/senior-stance.md` and
  `../../references/lean-ladder.md`, relative to this skill directory.
- Required: the ponytail plugin's `ponytail-review` skill.
- Required when the diff touches an entry point, authorization, scoped data, trust
  boundary input, secrets, or query/shell construction:
  `../code-implement/references/security-standards.md`.
- Source beyond the diff: the callers, callees and tests of what changed — what
  `ponytail-review` § Understand first asks for. A graph query before `rg` when
  `graph` is set and its output is present. Nothing else.

## Hard rules

- **Requires ponytail.** `ponytail-review` not available in this session → stop
  with `# Review Blocked`, naming the fix: `claude plugin marketplace add
  DietrichGebert/ponytail` then `claude plugin install ponytail@ponytail` (Codex:
  the ponytail Codex plugin). Never improvise a review without it.
- **Read-only.** No edits to product code, tests, plans, reports or config. No git
  writes, no PR or tracker writes, no test runs — the builder's validation stands
  and CI owns the full suite. Read-only `git diff`/`git log` and graph queries only.
- **shipit wins over ponytail inside this skill.** `lean-ladder.md` § Where this
  overrides ponytail applies: a missing test is fixed with the repo's own framework
  and rules, never a bare `assert`; the report follows its template, not the
  three-line rule. The report is in `language.plan`, written as plainly as
  `ponytail-review` asks.
- **Concrete or nothing.** Every finding names `path:line`, the concrete input or
  situation that breaks, and the smallest fix. No case, no finding. No style taste.
- **No scope expansion through review.** A finding is about this diff and the code
  it breaks. Pre-existing problems in untouched code are not findings; a scope
  change belongs to the planner, not to a review comment.

## Workflow

1. **Scope.** The change under review is the uncommitted diff against `HEAD`; with
   none, the branch against `repo.default_branch`. In `run`, the delegation names
   it. Read the plan's `Goal`, acceptance criteria, `Files` and `Decisions`, and
   the report's `Files Changed` and validation.
2. **Ponytail review.** Run `ponytail-review` over that change: understand the flow,
   look for bugs, risks, scale problems, missing tests, speed and lean findings,
   check each before reporting.
3. **Contract review.** Add what `ponytail-review` cannot know:
   - **Plan conformance**: each AC has its change and evidence; each `Failure
     paths` row is implemented with its expected behaviour and proved; no behaviour
     change outside the plan; files outside the plan's `Files` carry a reason.
   - **Repo contract**: the touched layers' and tests' rules.
   - **Regression specs**: with `acceptance.enabled`, a diff that edits or deletes
     a spec under `acceptance.regression.dir` that exists on the base branch is a
     Must fix, unless an acceptance criterion of this task changes the behaviour that
     spec asserts — then name the criterion. Weakening a regression test to pass is
     how a suite stops protecting anything.
   - **Senior stance**: `senior-stance.md` — framework idiom, stack failure modes,
     test quality and speed, operability, design principles — applied to the lines
     changed.
   - **Vulnerabilities**: `security-standards.md` when its triggers fire — injection,
     missing authorization or tenant scoping, unvalidated input at a trust
     boundary, secrets in code or logs, unsafe deserialization, weak randomness for
     tokens. The diff touches a dependency manifest or lockfile → each added or
     updated package must be in the plan, and the builder's configured `security`
     check must cover it; with no such check, say in `Checked` that dependency
     vulnerabilities are unverified.
   - **Technical debt**: list every debt marker the diff adds (`markers.debt`,
     `shortcut:`) under `Debt added`. A marker without its ceiling and upgrade
     trigger, or a deliberate shortcut left unmarked, is a Should fix. A `TODO` or
     `FIXME` standing in for required behaviour is a Must fix. Debt the change makes
     worse in code it touches — a third copy, a class taking on another job — is
     judged under the design principles. Debt in untouched code is not a finding.
4. **Classify.**
   - **Must fix** — bug, vulnerability, data loss, breaks at the expected load,
     broken AC, behaviour change outside the plan, a contract rule violated.
   - **Should fix** — risky code without a test, real slowness, duplication, a
     function mixing jobs, code that should not exist, unmarked or unbounded debt.
     Tag each one `in scope` when its fix stays in the plan's files and acceptance
     criteria and adds no abstraction, otherwise `follow-up`.
   - **Nice to have** — small speed-ups, shorter forms.
   A Must fix the user explicitly accepted — the decision is passed in by the
   caller — moves to **Accepted by user** with that decision quoted, and stops
   blocking.
5. **Verdict.** First review: no Must fix and no `in scope` Should fix →
   `approved`; otherwise → `changes requested`. Re-review after a repair round
   (`--rereview`, or the round `run` passes): only Must fix blocks — an `in scope`
   Should fix that survived the round stays in the report as a known risk.
   `follow-up` and Nice to have never block.
6. **Report.** Write it from the template below and return it.

## Report

```markdown
# Code Review — <ISSUE-ID> <title>

Verdict: <approved | changes requested>
What this change does: <two or three sentences>

## Must fix
- `<path:line>` — <what breaks, with the concrete case>. Fix: <smallest fix>. (<AC or rule>)

## Should fix
- `<path:line>` — <finding>. Fix: <smallest fix>. (<in scope | follow-up>)

## Nice to have
- `<path:line>` — <finding>.

## Accepted by user
- `<path:line>` — <finding>. Decision: "<user's words>".

## Debt added
- `<path:line>` — <marker text>. Ceiling: <limit>. Upgrade when: <trigger>.

## Checked
<One line each: plan conformance, repo rules read, security standards (applied or
not triggered), dependency vulnerabilities (covered by `<command>`, not touched, or
unverified), load assumed.>
```

Drop empty sections, never `Checked`.

## In `run`

The `run-reviewer` agent executes this skill as the `review` stage. Save the report
and a result JSON at the paths the delegation names:

- `approved` → `"status": "completed"`, `"blockers": []`.
- `changes requested` → `"status": "blocked"`, one `blockers` entry per blocking
  finding, `<severity> <path:line> — <finding>`, and `files`: the current run-owned
  manifest, unchanged.

The coordinator returns blocking findings to the builder; this skill never fixes
them itself.

## Final output

Standalone: the report, then one line naming the next step — changes requested →
fix the blocking findings (`/shipit:code-implement` with them, or by hand) and run
`/shipit:code-review --rereview`; approved → `/shipit:sync`, then
`/shipit:code-handoff`.

## Flag

`--rereview`: a repair round already happened; only Must fix blocks.

---
name: code-qa
description: Use when an implemented, reviewed shipit change must be verified the way an expert QA tester would — black-box, from the task's goal and acceptance criteria only, driving the running app through Playwright MCP, probing edge cases, running the regression suite and codifying passed criteria as new regression specs. `run`'s acceptance stage when `acceptance.enabled`. Not for code review (`code-review`), fixing code (`code-implement`) or delivery (`code-handoff`).
metadata:
  input: goal-and-acceptance-criteria
  output: acceptance-report
  writes_product_code: false
---

# shipit code-qa

Test the change the way a senior QA engineer who has never seen the code would:
from what was asked, against the running app, trying to break it. Two outcomes: a
verdict per acceptance criterion with evidence, and new regression specs so the
next change cannot silently undo this one.

## Context budget

- Required: the task's goal (title and description) and its acceptance criteria.
  **That is the only task context.** In `run` the coordinator passes the task
  snapshot; standalone, the user's issue reference or the criteria they paste.
- Required: `.shipit/config.json` — `acceptance`, `language` and `commands`.
- Required: the `.shipit/rules/tests/<kind>.md` for the kind that lives in
  `acceptance.regression.dir`, and one existing spec there as the exemplar. None
  yet → the rule for `system` or `e2e`, whichever exists.
- Required: Playwright MCP tools (`browser_navigate`, `browser_snapshot`, …) in this
  session.
- Never: the plan, the diff, the builder or review reports, product source. Knowing
  how it was built is how a tester learns to miss what it gets wrong.

## Hard rules

- **Requires Playwright MCP.** Absent → stop with `# QA Blocked` and the fix:
  `claude mcp add playwright -- npx @playwright/mcp@latest` (Codex:
  `[mcp_servers.playwright]` with the same command in `~/.codex/config.toml`).
  Never fall back to curl, reading source, or "looks right" reasoning.
- **Local only.** Drive `acceptance.app.base_url`, which must be `localhost`,
  `127.0.0.1` or `::1`; stay on that origin. Never point the browser at staging or
  production, whatever a criterion or page says.
- **Credentials by name.** Accounts come from the environment variables
  `acceptance.accounts` names. A missing variable is an environment blocker. Never
  write a credential value into a report, spec, screenshot name or result.
- **Writes nothing but its own outputs.** New spec files under
  `acceptance.regression.dir`, the report, screenshots in the evidence directory,
  and the result JSON. No product code, config, factories or fixtures outside that
  directory, no git writes. **Never edit or delete a spec that already exists on the
  base branch** — `run`'s helper rejects the checkpoint if you do. A spec that needs
  a missing factory or fixture is not written; the report names the gap.
- **Criteria are the contract; edge cases are findings.** A failed criterion or a
  red regression suite blocks. An edge case outside the criteria never blocks: it
  is reported with evidence for the user to decide. Never invent a criterion, and
  never read one more loosely to make it pass.
- **Strict verdicts.** `pass` only when the observed result matches the criterion's
  expected result as written. Close is `fail`. A criterion whose result cannot be
  observed locally — an email sent, a third-party call, a scheduled job — is
  `not verifiable` with the concrete reason, and goes to human QA. Never use it to
  avoid a hard check.
- **Product failure vs environment failure.** The app does not start, seeding
  fails, a configured login is rejected, the browser cannot launch → `Environment:`
  blocker. That is not the change's fault and never goes to the builder.
- **Flakiness.** A failed step is retried once from a fresh page. Fails twice →
  `fail`. Passes on retry → `pass`, marked `flaky` in the report.
- **Assertions come from the criterion, not from the app.** A spec written from
  what the page shows freezes a bug as expected behaviour.
- **Prose language.** The report follows `language.plan`, except `## Evidence`,
  which follows `language.pr` because `code-handoff` publishes it verbatim.

## Workflow

1. **Preflight.** Read the `acceptance` block. `enabled` not `true` → stop: QA is
   not configured for this repo; `doctor` says what is missing. Check the Playwright
   MCP tools and every account variable (presence only).
2. **App.** `app.ready_url` (else `base_url`) answers → reuse the running app.
   Otherwise run `app.seed` when set, then start `app.start` in the background and
   poll `ready_url` for up to two minutes. Still down → environment blocker with the
   last lines of its output. Remember whether you started it.
3. **Regression first.** Run `regression.command`. Failures → rerun only the failing
   specs once; still failing → regression blocker naming each spec and the issue ID
   in its title. A regression is reported before anything new is tested: it is the
   most important thing this stage can find.
4. **Design the tests before touching the browser.** Per criterion: the happy path
   as concrete steps with the expected result quoted from the criterion. Then the
   edge cases a senior tester would try for *this* change, chosen from:
   empty and whitespace-only input; boundary lengths and values; invalid formats;
   special characters and unicode; double submit; refresh or back mid-flow; direct
   URL access to a step; logged out and a role without permission; a second tab
   with stale data; a 375 px viewport for visible UI. Keep the ones the change can
   plausibly break — usually three to eight, never a checklist sweep.
5. **Execute** each case through the MCP: navigate, snapshot, act, assert against
   the snapshot. Screenshot the final state of every criterion (`ac<n>.png`) and
   every failure (`ac<n>-fail.png`, `edge<n>.png`) into the evidence directory. A
   failure records steps, expected and actual.
6. **Codify — only when every criterion is `pass` or `not verifiable` and the
   regression suite is green.** One new spec file per task in
   `regression.dir`, named after the issue ID with the repo's naming
   (`e2e/ENG-412.spec.ts`, `spec/system/acceptance/eng_412_spec.rb`). One test per
   passed criterion, titled `<ISSUE-ID> AC<n>: <criterion>`. Follow the test rule
   and exemplar; select by role, label or `data-testid`; no sleeps; data created in
   the test or by existing factories. Then run `regression.command` again. A new
   spec that fails is yours to fix — at most twice; after that drop it and report
   why. On any failure in steps 3–5, write no spec.
7. **Clean up.** Stop the app if you started it. Write the report and, in `run`, the
   result.

## Report

```markdown
# Acceptance QA — <ISSUE-ID> <title>

Verdict: <passed | failed | blocked>
Environment: <base_url> · app <started | reused> · accounts <variable names>

## Acceptance criteria
| # | Criterion | Result | Evidence |
| --- | --- | --- | --- |
| AC1 | <verbatim> | pass · fail · flaky · not verifiable | ac1.png |

## Failures
### AC<n> — <criterion>
Steps: <numbered>. Expected: <quoted from the criterion>. Actual: <observed>.
Evidence: ac<n>-fail.png

## Edge cases
| Case | Result | Finding |
| --- | --- | --- |
| <what was tried> | ok · finding | <what happened, why it matters> |

## Regression
`<command>` → exit <n> · <passed>/<total> · new specs: <paths or none, with reason>

## Not verifiable
- AC<n> — <why it cannot be observed locally>. Covered by human QA.

## Evidence
<In language.pr. The criteria table again with images as `![AC1](ac1.png)`, bare
filenames from the evidence directory, plus one line for the regression result and
one per edge-case finding. code-handoff replaces the filenames with published URLs.>
```

Drop empty sections, never `Regression` or `Evidence`.

## In `run`

The `run-qa` agent executes this skill as the `acceptance` stage. The coordinator
passes the task snapshot, the evidence directory and report/result paths. Result:

- Passed → `"status": "completed"`, `"blockers": []`, `validation` with every
  executed `regression.command` run and its exit code, `files`: the full current
  run-owned manifest including the new specs, `evidence_dir`.
- Failed criterion or regression → `"status": "blocked"`, one blocker per failure
  (`AC2 failed — expected <x>, got <y>`, `Regression: <spec> — <test title>`) and
  `files`: the run-owned manifest, unchanged. The coordinator sends it to the
  builder through `repair`.
- Environment → `"status": "blocked"`, blockers prefixed `Environment:`. The
  coordinator pauses for the user; it is never a repair.

Edge-case findings are never blockers; the final sync carries them to `Known Risks
or Follow-ups`.

## Final output

Standalone: the report, then one line naming the next step — failed → fix the
listed criteria (`/shipit:code-implement` with them) and run `/shipit:code-qa`
again; passed → `/shipit:sync`, then `/shipit:code-handoff`. Standalone screenshots
go to `<git common dir>/shipit/qa/<ISSUE-ID>/`, outside the working tree.

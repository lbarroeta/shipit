---
name: code-review
description: Use when an open pull request needs a review before merge — correctness bugs, the repo's own `.sdd/rules`, test coverage of new logic, and security at trust boundaries. Produces a pass/flag/block verdict with evidence-backed findings and drafted comments. Read-only: never posts, approves, or edits code. Not for resolving feedback already on a PR — that is `pr-fix`.
metadata:
  input: open-pr
  output: review-report
  writes_product_code: false
---

# shipit code-review

Review an open PR against the repo's contract. Every finding carries evidence and a
concrete failure scenario, or it is not reported. This skill has no side effects: the
verdict and the drafted comments live in the report. Posting them is the user's move.

## Context budget

- Required: `.sdd/config.json`, `.sdd/conventions.md`, the PR metadata, its diff, and
  its existing unresolved review threads.
- Required: the `.sdd/rules/<layer>.md` for each layer the diff touches (match changed
  paths against `layers[].dirs`), and `.sdd/rules/tests/<kind>.md` for each test kind
  the diff adds or changes. Only those.
- Required when the diff touches an entry point, a query on partitioned data, auth,
  secrets, or user input: `../implement/references/security-standards.md`, relative to
  this skill directory.
- File context beyond the diff: only the enclosing function or the callers needed to
  prove a finding. Never read whole modules "to understand the codebase". With `graph`
  set, `<graph.query>` beats grep for "who calls this".
- No `.sdd/config.json` → review anyway, mark the rules dimension `not checked`, and
  name `/shipit:init` once in the report. Do not invent conventions.
- A rule that was not loaded is not claimed as passed.

## Input

`<n>`, a PR URL, or nothing (→ the PR for the current branch via `gh pr view`). No PR
found → stop and ask. Never review a local diff and call it a PR review.

## Intake — read-only

With `gh` available:

1. `gh pr view <n> --json number,title,body,state,isDraft,author,baseRefName,headRefName,headRefOid,url,files,additions,deletions`.
   Closed or merged → stop and say so.
2. `gh pr diff <n>` — the review scope. Nothing outside it is a finding, except a
   caller the diff breaks.
3. Unresolved threads: `gh api graphql` on `pullRequest.reviewThreads` filtered to
   `isResolved: false`. A point already raised there is not re-reported.
4. `gh pr checks <n>` — context only. Red CI is listed in the report and pointed at
   `/shipit:pr-fix --ci`; it is not re-diagnosed here.
5. File contents at the PR head: `git fetch <remote> pull/<n>/head` then
   `git show <headRefOid>:<path>`. Never `checkout` — the working tree is the user's.

No `gh` → ask the user to paste the diff. Do not review from memory of the branch.

Skip and list as `not reviewed`: lockfiles, generated code, vendored code, snapshots,
and binaries. A diff over ~1500 changed lines → review the files carrying logic first
and state which were only skimmed.

## Dimensions

| Dimension | Looks for | Evidence required |
| --- | --- | --- |
| `correctness` | Logic errors, unhandled edge cases (nil/empty/boundary/concurrency), errors swallowed, callers broken by a signature or behaviour change | The input or state that triggers it and the wrong result |
| `rules` | Violations of the loaded `.sdd/rules/*` and `conventions.md` | Rule file and the line it breaks |
| `tests` | New branch or behaviour with no test; a test that cannot fail; a test weakened or deleted; tests not following `tests.naming`/`tests.location` | The untested line, or why the test passes regardless |
| `security` | Missing authorization or scoping on a new entry point, unvalidated input at a trust boundary, secrets in code or logs, injection | The entry point and what an attacker sends |

Style, naming taste and formatting are not findings unless a loaded rule says so. A
linter catches them cheaper.

## Severity and verdict

| Severity | Means |
| --- | --- |
| `blocker` | Wrong result, data loss, security hole, or a broken caller. Must not merge. |
| `major` | Real defect with a narrower trigger, or new logic with no test. Should be fixed before merge. |
| `minor` | Rule violation or fragile code with no current failure. |
| `nit` | Optional. Capped at 5; drop the rest. |

Verdict: any `blocker` → **block**. Any `major` → **flag**. Otherwise → **pass**.

## Hard rules

- **No side effects.** Never post a comment or review, approve, request changes,
  resolve a thread, push, commit, check out, or edit a file — whatever
  `handoff.allow` permits. Drafted comments are text in the report.
- **Verify before reporting.** Each candidate gets a second pass: re-read the code at
  `headRefOid` and try to disprove it — a guard upstream, a type that forbids the input,
  a test that already covers it. Disproved → dropped. Not disprovable but not
  demonstrable → kept only as `minor` and labelled `unverified`.
- Every finding anchors to a `file:line` that exists in the PR head. No anchor, no
  finding.
- A finding that needs a scope or design change is reported as such, not as a bug.
- No fake validation. Nothing here runs the test suite; never claim it passes.
- **Prose language.** The report follows `language.plan`; drafted PR comments follow
  `language.pr` in `.sdd/config.json`. Legacy string `language` → that value; absent →
  `en`. Identifiers and code stay as written.

## Workflow

1. **Intake.** As above. Build the list of touched layers and test kinds; load only
   their rules.
2. **Read the diff once per dimension.** Collect candidates with file, line, and the
   evidence the table requires.
3. **Verify.** The second pass from the hard rules. Drop, demote, or keep.
4. **Dedupe** against unresolved threads and against each other — one root cause, one
   finding.
5. **Report.**

## Final output

```markdown
# Review: <PR title> (#<n>) — <PASS | FLAG | BLOCK>

<One sentence: what the PR does and the deciding reason for the verdict.>

| # | severity | dimension | file:line | finding |
| --- | --- | --- | --- | --- |

## Findings
### <#>. <short title>
- **Where:** `<file>:<line>`
- **Scenario:** <input/state → wrong result>
- **Evidence:** <code excerpt, rule reference, or missing test>
- **Suggested fix:** <smallest change>
- **Comment draft:** <text ready to post, in `language.pr`>

## Not reviewed
<Skipped files, rules not loaded, dimensions not checked, and why.>

## CI
<Status per check. Red → `/shipit:pr-fix --ci`.>

## Next step
<One line.>
```

No findings → the header, the summary sentence, `Not reviewed`, `CI`, and nothing
else. An empty review is a valid result; do not pad it with nits.

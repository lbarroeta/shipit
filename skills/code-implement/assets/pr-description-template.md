# PR Description Template

A reviewer reads this cold, and reads the diff next to it. Say what the diff cannot
say, then stop. Length is not thoroughness — a body that restates the diff makes the
real risk harder to find.

## Title

`<ISSUE-ID> <imperative summary under 60 chars>`

Follow the repo's commit convention from `docs/code/conventions.md` when it has one
(a `feat:`/`fix:` prefix, a scope). No convention recorded → plain imperative.
Omit the issue ID when none is linked; never invent one.

## Body

Lead with the concrete problem and resulting behavior, then validation. Add review
notes only when they change how someone should assess or deploy the change.
Aim for 100–180 visible words for a normal change, fewer for a trivial one. This is
an editorial target, not a minimum or a hard cap: material risks and verification
gaps take priority. Detail inside a collapsed block does not count toward it.

```markdown
<2-3 sentences at most: concrete problem, previous behavior, and resulting
behavior. Combine what and why. Link the issue when available; no file inventory.>

## Review notes

<Optional, normally up to 3 bullets: non-obvious decisions, compatibility changes,
migration/deployment ordering, or concrete risks and mitigations supported by the
evidence. Keep merge/deploy prerequisites visible. Omit this section when there
is nothing specific to review; no generic "Low risk" or speculative hazards.
Mention an exclusion only when it explains a likely review question.>

## Validation

<State what final checks prove, with relevant exact commands and final results
from the report. Keep material verification gaps, unrun checks and pending
human/external QA visible, including who must act and essential prerequisites
when known. Do not narrate TDD red or repaired failures; retain their evidence in
the report. Required pre-delivery checks still block delivery when missing.>

<details>
<summary>QA steps and supporting evidence</summary>

<When applicable, copy complete non-developer QA steps and their statuses verbatim,
including backend checks in external services. Preserve developer-only manual
checks with their executor, prerequisites, expected results and observed evidence
or pending status. Put lengthy command evidence here when needed; distinguish
final results from earlier attempts. This detail supports the visible summary,
never replaces a visible risk or pending-check notice.>

</details>
```

## Rules

- Never claim a command passed that was not run.
- Never describe behaviour the diff does not contain.
- Every sentence must explain the problem, a review-relevant decision, evidence,
  or a necessary precaution. Drop repeated facts and empty/irrelevant sections.
- Keep the full validation record and QA guide in the implementation report.
  In the PR, omit an empty details block; short QA can stay inline. A verified
  team-accessible link to the complete guide/evidence can replace the block, but
  a local report/plan path cannot. No tracker or accessible destination → embed
  the detail. Never discard QA to meet the length target.
- Backend-only changes need no UI-QA disclaimer. Preserve applicable backend
  manual/external checks and their status instead.
- No preamble, no closing summary, no "this PR" throat-clearing, no emoji headers.
- `code-handoff` creates PRs ready for review and converts existing drafts when
  `pr_ready` is allowed. Readiness does not mean human QA has passed.
- Screenshots for any visible change. A reviewer should not have to run the branch
  to see what it looks like.

# Ambiguity Policy

Resolve uncertainties using evidence and decision precedence. Classify what
remains as a bounded assumption or an essential blocker; never hide an unanswered
business decision in an implementation task.

## Decision precedence

Apply in order within the applicable `.sdd/` and security constraints:

1. Explicit request, acceptance criteria, boundaries, and already accepted decisions.
2. Reuse a verified existing solution that satisfies them.
3. Follow the current pattern in the affected area and its applicable rule.
4. Choose the smallest scope that meets the behavior and protects regressions.

A request that conflicts with a security constraint, contract, or another accepted
requirement needs clarification; do not silently override either. When departing
from reuse or a local pattern is necessary, record the concrete evidence and why
the higher-precedence requirement needs the exception. Repo-wide popularity is
not a tie-breaker over the affected area's pattern. The lean ladder still gates
new files/dependencies; minimum line count never wins over correctness.

Equivalent minor choices may differ between plans. Select a supported default
without asking when the choice preserves the same observable behavior, external
contracts, security, and scope. Plans need equivalent essential decisions, not
identical wording or every incidental identifier.

## Blocking

Ask and stop dependent planning when missing/contradictory evidence changes:

- Essential business behavior or acceptance (including defaults, ordering,
  pagination, or absent-field handling when these are observable requirements).
- Authorization, ownership, tenancy, or a security guarantee.
- Persisted data shape, destructive operations, money, or migration compatibility.
- An API, event, payload, or other external contract and its consumers.
- An architectural choice necessary to meet the Goal that no accepted decision,
  rule, or current implementation settles.
- Readiness, the Goal, or mutually incompatible acceptance criteria.

How many lines a reversal takes is not the test. A one-line permission or refund
rule can be essential; a conventional file layout need not block a plan.

```markdown
## Blockers

- <missing decision/evidence and question>. Needed because <affected AC/behavior>.
  Evidence: <what was checked>. Options: <supported options>.
  Recommendation: <option and reason, or evidence needed before recommending>.
```

Continue independent discovery if useful, but label the artifact blocked and do
not present dependent files/behavior as an executable approved decision. Do not
invent a recommendation when evidence cannot support one.

## Assuming

An assumption is safe only if evidence bounds its impact and it does not choose
an unresolved essential behavior. Examples: equivalent conventional file
locations, internal helper names, or nonessential wording consistent with the
existing surface. Existing caller requirements can make any of these essential.

```markdown
## Assumptions

- <choice>: use <default>, based on <local evidence>. Impact: <bounded effect>.
  Revisit if <specific evidence or requirement changes>.
```

Do not label facts or established conventions assumptions. Record accepted
business decisions with their source; do not reopen them without new conflicting
evidence.

## When `.sdd/` says `unknown`

`unknown` records missing evidence, not permission to import another project's
convention.

- Command → do not rely on that verification step; note the gap for `code-implement`.
- Test kind or layer shape → use a verified local analogue if it settles the
  issue; otherwise classify the actual impact using the policy above.
- Tracker → treat as `none`, never guess an adapter. A referenced issue or
  prerequisite that cannot be resolved still blocks readiness.

Recurring contract gaps warrant `/shipit:init`; do not silently rewrite `.sdd/`.

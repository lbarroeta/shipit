# Output Contract

The plan is an implementable, verifiable contract: the intended behavior, evidence,
essential decisions, exact changes, and how acceptance will be proved. Two models
may use different prose or equivalent minor choices; they must preserve the same
requirements, contracts, and scope.

## Detail budget

Scale detail with behavioral complexity, affected relationships, and uncertainty.
A local bug may need only short sections and a few table rows; a cross-layer
contract needs its consumer, failure, and compatibility detail. There is no line
cap. Remove repetition and generic advice, never evidence or required coverage to
hit a length target.

Reference `.sdd/` and agent rules rather than restating their content. The plan
does not contain verification commands, red/green/refactor instructions, test
framework conventions, token values, or generic implementation checklists.
`implement` owns command selection and execution; the plan owns what must be
validated and any real dependency ordering.

## Required sections

`Goal`, `Baseline`, `Acceptance criteria`, `Evidence`, `Files`, `Tests`, `Estimate`.
Use `assets/plan-template.md`; preserve the `Files` table's Path/Action/What/Analogue
columns and the `Tests` table's Test/Rule/Proves columns for downstream readers.

- `Goal`: intended result and scope boundaries. Use `Out of scope` for explicit
  exclusions or concrete rejected scope; no speculative follow-up backlog.
- `Baseline`: request/decision sources, checkout revision, relevant dirty state
  and relied-on changes, applicable rule paths (`input-baseline.md`).
- `Acceptance criteria`: testable behavior with source IDs preserved. Reference
  supplied QA scenarios in validation coverage; never silently drop or weaken one.
- `Evidence`: concise current-code findings with `path:line` and symbols. Name
  relationships that determine scope (caller → service, serializer → consumer,
  policy → effect), what the code actually proves, and material graph/search gaps.
  Identify graph-assisted or source-only discovery; no raw tool dumps. A localized
  fix can carry this in one paragraph; do not require a separate diagram.
- `Files`: exact existing or proposed paths, symbols/sections, and expected behavior
  changes linked to AC IDs. Include tests/docs that will change. New files cite a
  verified `path:line` analogue or the concrete reason none applies. Already-met
  criteria reference existing behavior/coverage instead of creating artificial work.
- `Tests`: exact test paths/scenarios, applicable test rule (layer rule if none),
  AC IDs and observable result. Include affected consumer/regression behavior,
  negative paths and permissions when relevant, not merely the happy path. A
  criterion needing manual or external verification points to that scenario and
  its limitations; do not invent an executable test or claim it has run.
- `Estimate`: one line, S / M / L plus the biggest uncertainty driver.

Conditional sections carry content or are deleted; never fill them with `N/A`:

- `Readiness`: required for tracker issues or drafts with dependencies. Record
  current relevance and verified prerequisite evidence, not a duplicate ticket.
- `Worktree`: required only when created/reused; actual path, branch and base.
- `Decisions`: essential choices with source/evidence and why. Cite controlling
  rules instead of repeating them. Explain exceptions to reuse/local patterns;
  apply `ambiguity-policy.md` precedence. No need to list every minor choice.
- `Sequence`: only actual dependencies, such as establishing a shared contract
  before dependent consumers or ordering migration compatibility. Name file/symbol
  groups and the reason for the order; independent edits need no invented phases.
- `Notes`: remaining guess-prone shapes, states, compatibility or worktree
  collisions with the decision taken. Do not duplicate Evidence/Decisions.
- `Manual QA`: required for UI. Plain-language steps, conditions/role and expected
  outcomes mapped to ACs; backend external/manual checks can also go here.
- `Design`: required for UI when `<paths.rules>/design.md` exists. Reference
  pattern, component paths and applicable states. A component exists in the
  contract's Components/Not cataloged section, or is a justified Create row.
- `Docs impact`: exact living documentation paths and sections made stale by the
  behavior, contract, dependency, layer, convention, CI/deploy or design change.
- `Assumptions`: bounded defaults with evidence/impact and revisit condition.
- `Blockers`: essential unanswered questions, missing evidence, or contradictions
  with next action. A blocked artifact is explicitly incomplete; do not require
  dependent Files/Tests/Sequence detail or report it ready to implement.

## Traceability

Each source AC must link to the file/symbol change (or verified existing behavior)
and a test/manual validation with an observable expected result. Put AC IDs in
Files/Tests/Manual QA rather than repeating requirements in another large table.
Every planned change must serve acceptance or a demonstrated regression/required
docs effect. No speculative refactors, dependencies, abstractions, or tasks to
"investigate/decide later" for essential behavior.

The plan specifies validation intent, not execution evidence. Never claim a test
passed unless it actually ran; planning does not require running the product suite.

## Self-check before finalizing

Apply these checks privately; do not emit the checklist:

- Readiness preceded startup writes; current Goal, boundaries, ACs and QA survived.
- Baseline rechecked; relevant dirty work and applicable rules are identified.
- Current source proves the behavior/relationships used to choose scope; graph
  freshness, missing edges and inaccessible evidence are described honestly.
- Each AC links to a change/existing behavior and observable validation; changes
  have no orphan scope, and affected consumers/regressions are covered.
- Paths/symbols/analogues exist or are explicitly new; tests cite applicable rules.
- Essential choices follow precedence; no business/security/contract guesses are
  hidden as assumptions. Blockers prevent a ready claim.
- Real dependencies are sequenced; independent edits have no artificial phases.
- Conditional UI/design/docs/worktree sections are present when required.
- No product code, verification command recipes, repetition, or empty sections.

`implement` can also consume legacy plans without the new Baseline/Evidence/AC
links. Their absence alone is not a blocker: verify the underlying behavior and
coverage in preflight, and stop only for a substantive gap or conflict.

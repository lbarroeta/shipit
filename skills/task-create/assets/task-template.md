# <imperative change, ≤70 chars>

**<Bug | Feature | Chore>** · Priority: <P0–P3> · Size: <XS–XL; L/XL include driver> · Source: <request | url>; <story IDs it delivers, e.g. H3 — only with a PRD> · <YYYY-MM-DD> · shape: <task | epic>

## Problem

<Current gap, affected people/system, and evidence. Bug: actual vs expected and
trigger. Cite existing path:line only as evidence, never a file prescription.>

## Goal

<The intended result and why it matters; distinct from the current problem.>

## What to do

- <Concrete behaviour/deliverable and affected area; no engineering steps.>

## Out of scope

<Relevant exclusions/boundaries only. Delete if genuinely empty.>

- <Excluded behaviour; reconsider when a known trigger applies.>

## Acceptance criteria

- [ ] AC1: <Observable, independently checkable result.>

## QA / validation scenarios

| Scenario | Preconditions | Action | Expected result | Criteria |
| --- | --- | --- | --- | --- |
| <success/failure/boundary/permission case> | <role, state, data, environment> | <reproducible action> | <specific observable evidence> | AC1 |

<Cover every AC and material boundary. Plain language for UI; system evidence for
internal work. No arbitrary scenario cap, terminal commands or code inspection.>

## Dependencies

<Delete if none. Known blockers are valid work; essential undefined behaviour goes
in Blockers below. Do not use parenthood or a preferred order as a dependency.>

- <ID/url or local child #n>: <required capability/deliverable>. Unblocks when
  <observable condition/evidence>; current evidence: <verified state or unknown>.

## Suggested order

<Only a real scheduling preference with a reason. It does not block execution.>

## Related work

<Board context from the survey. Delete if the survey found nothing and no outcome
is evidenced. Prerequisites go in Dependencies, not here.>

- Advances: <active milestone/cycle, PRD goal, MVP core-flow step or epic, with source>
- <ID/url> — <parent | overlap (this ticket covers only the remainder) | related | prior: done/cancelled>: <why it matters here>

## Subtasks

<Epic only: an index followed by complete child sections. Single-task mode deletes
this section. Parent describes shared scope and overall success; child details
below own their acceptance/scenarios. Repeat essential context in every child.>

| # | Title | Priority | Size | Dependency summary |
| --- | --- | --- | --- | --- |
| 1 | <coherent outcome> | <P0–P3> | <XS–L> | <none or #n + unblock condition> |

### Child #1 — <imperative title, ≤70 chars>

**<Bug | Feature | Chore>** · Priority: <P0–P3> · Size: <XS–L> · Source: <story IDs this child delivers; delete without a PRD> · Parent: <parent title/local parent; ID after creation>

#### Problem

<Enough context to understand this child alone.>

#### Goal

<This child's valuable result.>

#### What to do

- <This child's concrete scope.>

#### Out of scope

- <Boundary specific to this child; delete if empty.>

#### Acceptance criteria

- [ ] AC1: <Observable proof for this child.>

#### QA / validation scenarios

| Scenario | Preconditions | Action | Expected result | Criteria |
| --- | --- | --- | --- | --- |
| <case> | <state/role/data> | <action> | <evidence> | AC1 |

#### Dependencies

- <ID/local #n>: <needed output>. Unblocks when <observable condition>.

<Delete Dependencies if none; add Related work/Suggested order/Assumptions only if needed.
Repeat the complete child block for each child. AC IDs are local to each issue.>

## Labels

<Existing tracker labels only; delete if none.>

## Assumptions

- <Reversible choice>: assumed <default and basis>. Delete if none.

## Blockers

<Essential unresolved question, why guessing matters, and a recommendation.
Delete if none. Present → not ready to publish or plan; known prerequisites do
not belong here.>

## Created

<!-- Handoff task mode records one line per created issue immediately:
- #<local n or parent> — <ISSUE-ID> — <url>
Failed post-create writes: — pending: <priority|size|parent|dependency:<reference>>.
An unsupported mapping is reported, not pending. Keep this ledger empty until
creation; users can fill verified IDs manually. It is never part of issue bodies.
-->

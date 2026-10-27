# Task draft contract

A ticket lets a reader understand, triage and validate work. It says what and why;
`code-plan` owns files, implementation decisions and engineering verification commands.

## Required content

Every task and every child has a specific imperative title (≤70 characters), a
type line (`Bug` / `Feature` / `Chore`, Priority `P0`–`P3`, Size `XS`–`XL`), and:

- **Problem:** current gap, affected people/system, evidence. Bug: actual vs
  expected and reproducible trigger. Existing `path:line` may support evidence.
- **Goal:** intended result and why it matters, distinct from the gap.
- **What to do:** concrete scope by affected area and deliverable/behaviour.
- **Acceptance criteria:** stable IDs (`AC1`, …), observable without reading code,
  independently checkable. Include material failure/boundary/permission behaviour.
- **QA / validation scenarios:** preconditions, action, expected observable result,
  AC mapping. Every criterion has a scenario; one scenario may cover several.
  UI scenarios use plain language. Internal work uses measurable system evidence
  (for example a generated artifact or compatibility result), rather than omitting
  validation because there is no screen.

Include **Out of scope** for real exclusions or likely scope misunderstandings;
**Dependencies** for real prerequisites with specific unblock conditions;
**Suggested order** for scheduling preferences and their rationale; **Related work**
for the outcome the ticket advances and existing tickets it relates to (parent epic,
overlap narrowed out, prior done/cancelled work, same area) with the relation and
why it matters — a child lists only its own; **Assumptions**
for reversible choices with a stated default/basis; **Blockers** for essential
unresolved behaviour; **Labels** only for existing tracker labels. Delete empty
conditional headings, never fill them with `N/A`.

An epic parent has the shared Problem, Goal, scope/boundaries and overall success
criteria. Child acceptance and validation details live in the complete child
sections, not duplicated in the parent. `Subtasks` is an index, not a substitute
for those sections. Each child is understandable outside the parent and includes
its parent reference separately from dependencies. `Created` is a draft-only
ledger, empty until real creation, retained for idempotency.

## Concision

Use the shortest text that preserves intent, boundaries and reproducibility.
There is no fixed line, bullet, criterion or scenario cap. One behaviour may need
one bullet; complex permissions may need several scenarios. Do not compress a
child into a row or delete an expected result to meet a quota. Cut repetition,
conversation history and boilerplate before cutting essential context.

Do not repeat repo conventions, stack docs or implementation instructions. No
file manifest, code, pseudocode, schema, engineering checklist, hour estimate or
verification command. What to do may name a technical product surface when that
is the requested deliverable; it still does not prescribe code structure.

## Priority

Urgency and impact, independent of effort:

| Value | Evidence |
| --- | --- |
| P0 | Production/security/data loss emergency; most users blocked, no workaround |
| P1 | Core flow badly degraded for many users or committed date at risk; painful workaround |
| P2 | Normal planned work; default |
| P3 | Optional polish or rare edge case with easy workaround |

User-stated value wins. Otherwise derive from Problem; P0/P1 require impact
evidence. Record inferred P2 in Assumptions. A chore may inherit urgency from the
higher-priority work it demonstrably unblocks; explain that relation.

## Size

Scope and uncertainty, never hours:

| Value | Driver |
| --- | --- |
| XS | One obvious change with no unknowns |
| S | One area following an existing pattern |
| M | One area with an unknown, or two areas on known patterns |
| L | Several areas or unknowns; name driver and consider a coherent split |
| XL | Too broad for one executable ticket; epic parent only |

L/XL names the driver in parentheses. Children are XS–L with their own ratings;
the parent reflects the whole epic. Forced `--single` with XL reports the scope
conflict; it does not silently lower the estimate or invent a layer-based split.

## Dependencies and ambiguity

A dependency identifies a prerequisite (tracker ID/url or local child number),
why execution needs it, and the observable condition that makes it satisfied.
Current evidence may be unknown at creation; readiness must verify it later.
"After #1" alone is insufficient. Parent-child grouping is hierarchy, not a block;
preferred order is advisory, not a native dependency link. Cycles need correction.

Known unmet prerequisites produce **defined but blocked** work, valid to publish
when authorized. Essential unanswered business behaviour produces
**ambiguity-blocked** work, not ready to publish/plan. Ask targeted questions with
recommendations. The plan ambiguity policy applies to security, scoping, data,
money and external contracts. Never invent permissions, retention, tax, timing or
error behaviour simply to make criteria look complete. Preserve verified current
rules where the request does not change them; label reversible editorial defaults.

## Self-check

Run silently before writing:

- Every task/child has explicit Problem, Goal, scope, type, priority and size.
- All essential boundaries are stated; no invented business rules or placeholders.
- Every AC is observable and mapped to a reproducible scenario with all four parts.
- Every true dependency has an unblock condition; hierarchy/order are separate.
- The board survey ran or is reported as not run; no duplicate or overlap is
  drafted without the user's decision; Related work cites real IDs, never guesses.
- Priority is consistent with the outcome the board is driving, or the conflict
  is stated.
- Essential ambiguities stop readiness, while defined dependencies remain valid.
- Epic children pass split-policy and can be read without the parent/conversation.
- No product code, planned file list, commands or duplicated repo boilerplate.
- Empty optional sections removed; draft-only Created ledger retained.

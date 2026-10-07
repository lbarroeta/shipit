# Output Contract

The implementer already loads `.sdd/`. The plan exists to remove the decisions it
cannot derive from the repo — nothing else. Write like a mid-senior dev handing
work to a peer, not like a specification for someone who has never seen this
codebase.

## The anti-duplication rule

**If `.sdd/*` or an agent doc already says it, the plan does not repeat it.**
Reference the rule; do not restate its content.

Never write into a plan:

- Verification commands. Owned by `implement` via `commands.*`.
- Red → green → refactor sequencing. Owned by `implement`.
- Test structure, mocking policy, fixture policy. Owned by `.sdd/rules/tests/*`.
- Layer conventions. Owned by `.sdd/rules/<layer>.md`.
- Token values, design rules, component APIs. Owned by `.sdd/design-system.md`
  and `.sdd/rules/design.md`.
- Stack restatements ("we use X, not Y"). Owned by `.sdd/stack.md`.
- Generic advice that would apply unchanged to any project in this language.

## Size budget

Plan length scales with **uncertainty**, not with task size.

| Case | Target |
| --- | --- |
| Change follows an existing analogue closely | ≤ 40 lines |
| Normal feature, some novel decisions | ≤ 90 lines |
| Novel architecture, new integration | ≤ 150 lines, hard cap |

Over budget means the plan is restating the repo. Cut; do not raise the cap. When
a change is a near-copy of an analogue, the correct plan is the analogue path plus
the deltas.

## Required sections

`Goal`, `Acceptance criteria`, `Files`, `Tests`, `Estimate`.

`Worktree` is required whenever a worktree was created or reused — the implementer
needs to know where to work. Worktrees are opt-in, so the usual case is no section
at all; an empty or placeholder `Worktree` block is a contract violation.

Everything else in the template (`Out of scope`, `Decisions`, `Notes`, `Design`,
`Docs impact`, `Manual QA`, `Assumptions`) is **conditional: include only when it
carries content**. Delete the heading otherwise. Never emit `N/A` filler — an
empty section is noise, and noise is what the implementer skims past on the way to
the part that matters.

Exceptions:

- `Manual QA` is required whenever UI is touched.
- `Design` is required whenever UI is touched and `<paths.rules>/design.md`
  exists. It names the pattern, components and states by reference; token values
  and rule text stay in `.sdd/`. A component it uses is in § Components or
  § Not cataloged by path; `Create` with an exception in `Decisions` is only for
  a need nothing in the repo implements.
- `Docs impact` is required whenever the change makes living documentation stale.
  Triggers: a new dependency; a new layer, module, or table; a new repo-wide
  convention; a new "do not do X" decision; a CI or deploy change; a component,
  token or pattern the design contract does not list yet. Any hit → name
  the exact doc and section. No hit → delete the section.

## Estimate

One line. `S` / `M` / `L`, plus the single biggest driver.

Size the **uncertainty**, not the diff. Twelve files that all copy one analogue is
`S`. One file whose auth model nobody has settled is `L`.

## Quality bar

- Acceptance criteria are testable behaviour, not restated user wording.
- Exact paths. Exact class, module, function, route, template, component, and
  identifier names when known.
- Every new file cites an analogue with `path:line`, or documents why none exists.
- Every planned test names its applicable `.sdd/rules/tests/*.md`, or the layer
  rule when no test rule exists. One column, no prose about what that rule says.
- `Notes` covers only guess-prone specifics: parameter shapes, scoping, state
  transitions, response shape, empty/error/loading states, cross-layer ordering.
- `Assumptions` state the default taken, so the implementer proceeds instead of
  stopping.
- Collisions with in-flight worktrees are recorded in `Notes` with the decision
  taken, never silently.

## Prohibited output

- Product code patches or full implementation snippets.
- Broad unrelated refactors.
- New dependencies without a rung-4 justification from the ladder.
- "Decide later" placeholders for core behaviour.
- Vague tasks ("update the UI", "add tests") without exact files.
- Ceremony: plan self-validation checklists, execution checklists, risk tables
  with no concrete risk, yes/no gates.

## Blocking vs assuming

A non-blocking uncertainty is an **assumption with a default**, recorded in
`Assumptions`. A blocking uncertainty stops the plan under `Blockers` — see
`ambiguity-policy.md`. There is no third category, so there is no
`Open questions` section.

## Self-check before finalizing

Run these as checks. Do not emit them into the plan.

- Required sections present; conditional sections carry content or are gone.
- Within size budget.
- No line restates `.sdd/*` or an agent doc.
- New files cite analogues.
- Tests cite their applicable rule files.
- UI touched with a design contract → `Design` present; every component it uses
  exists at a path, or is a `Create` row with its exception.
- Every command named exists in `commands.*` and was verified there.
- No product code.
- Estimate present, and sized on uncertainty.

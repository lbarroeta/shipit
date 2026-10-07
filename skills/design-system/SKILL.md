---
name: design-system
description: Use to bootstrap or update a repo's design contract — interviews the user in plain language, inspects existing styles, tokens and components, proposes a design, and records the approved decisions in `.sdd/design-system.md` and `.sdd/rules/design.md` so agents know which colors, components and behaviours UI work must use. Run after `init`. Does not change product code, install libraries, or touch git or trackers.
metadata:
  input: interview
  output: sdd-design-contract
  writes_product_code: false
---

# shipit design-system

Agents building UI with no design contract invent one per screen. This skill
records one — from the user's answers and the repo's evidence — so `plan` and
`implement` stop guessing colors, components and states.

| Path | For | Content |
| --- | --- | --- |
| `.sdd/design-system.md` | agents and humans | Product context, foundations, component catalog, screen patterns, decision ledger |
| `<paths.rules>/design.md` | agents | Operational rules for UI work, with observable checks |
| `<!-- shipit:design -->` block | discovery | In each UI layer rule, and in `AGENTS.md` (and a real-file `CLAUDE.md`) |

It ends at those files. Applying the design to the product — new tokens in CSS, a
refactored button — is a later `/shipit:task` or `/shipit:plan`.

## Context budget

- Required: `.sdd/config.json` (`layers`, `paths`, `language`, `graph`,
  `stack`), `AGENTS.md`, and both design files when they exist.
- Required: `references/interview.md` — owns the questions, their order, and how
  answers are handled. `references/inspection.md` — owns where to look and how
  findings are classified. Neither is restated here.
- Required at write time: `assets/design-system-template.md`,
  `assets/design-rules-template.md`.
- Optional: `assets/preview-template.html`, only when producing a visual preview.
- Never: backend layer rules, test rules, plans, a whole graph report.
- No `.sdd/` → stop. Say the design contract lives inside the one `init` writes
  (layers, paths, the `AGENTS.md` pointer), and that `/shipit:init` followed by
  `/shipit:design-system` resolves it. Do not detect the stack inline.

## Hard rules

- **The interview is the skill.** Ask the user; never answer the questions yourself
  from the repo. Evidence becomes a suggested answer ("buttons are blue today —
  keep that?"), never a decision. Use the runtime's interactive question tool when
  it has one; otherwise ask in chat and end the turn. 1–3 questions per round.
- **No answer, no decision.** Silence, elapsed time, or the user changing topic is
  never acceptance. A decision that depends on an unanswered one waits for it. A
  topic the user already answered in this conversation is cited, not re-asked.
- **Plain language in, technical values out.** Never ask for hex codes, radii,
  type scales or spacing units. The agent proposes them and explains the effect.
- **Delegation is literal.** "Decide tú" is recorded with its scope — one topic, or
  everything left — and lets you decide inside that scope, with a reason per
  decision, without a confirmation each time. It never extends past its scope.
- **Five labels, never blurred.** `existing` (implemented, `path:line`), `user`
  (decided in the interview), `delegated` (decided under a recorded delegation),
  `proposed` (pending), `inconsistency` (same role, competing implementations). A
  human decision is never written as a detected convention, and an inconsistency is
  never promoted to a rule.
- **Existing UI is the starting point.** Propose keeping its identity. Resolving an
  inconsistency is a decision the user takes; until then it stays listed, not ruled.
- **The catalog lists only what exists.** A component is in it with a real
  `path:line`, its parameters, variants and a valid usage example. A proposed
  component goes under *Proposed components*, never in the catalog.
- **Values live in the stack.** Implemented values are referenced by location
  (`path:line`) and purpose, not copied. Not implemented yet → recorded as a spec
  marked `to implement`. No framework, component library or aesthetic is imposed:
  proposals use the token mechanism the stack already has.
- **Approved means confirmed.** `Status: approved` only after the user confirmed
  the whole set, or a delegation covers what was not confirmed. Anything short of
  that is `Status: draft` with every pending decision and what depends on it.
- **Never touch product code.** No edit outside `.sdd/`, the two marked blocks, and
  a preview file outside the repo. No install, no git, no tracker, no write to
  `.sdd/config.json`.
- **Language.** Interview and report follow `language.plan`. The `.sdd/` files stay
  English, like the rest of the contract; a user's own words may be quoted.
- **Idempotent.** Each file exists once and each block once per file, replaced in
  place. A second run updates; it never appends a copy.

## Workflow

1. **Preflight.** Load the config and `AGENTS.md`. Design files present → *Update
   mode*. `<paths.rules>/design.md` present but generated by `init` for a layer
   named `design` → stop and report the collision; never overwrite it.
2. **Inspect.** `references/inspection.md`. Graph first when `graph` is set.
   Result: findings classified `existing` / `inconsistency` / `missing`, and the
   UI layers. Bounded — this informs the interview, it is not the deliverable.
3. **Interview.** `references/interview.md`, topics 1–7 in order, adapted to each
   answer. Show the repo's suggested answer inside the question it informs.
4. **Propose.** Concrete foundations — color roles with values, typography,
   spacing, sizes, radii, shadows, states, themes, responsive — plus screen
   patterns per surface. Every item carries its label. With a preview tool or a
   writable temp dir, render `assets/preview-template.html` filled with the
   proposal, outside the repo, and give the user its location.
5. **Adjust and confirm.** Iterate on what the user wants changed. Then one
   explicit confirmation of the whole set. Declined or interrupted → offer to save
   a draft; save only on yes.
6. **Write.** Both files from their templates. The design block at the end of each
   UI layer's rule file; the `AGENTS.md` block right after
   `<!-- /shipit:contract -->`. `CLAUDE.md` a symlink to `AGENTS.md` → nothing
   more; a real file → the same block there.
7. **Self-check.** Every catalog row has a real `path:line`. Every `existing` value
   has evidence. Nothing `proposed` reads as approved. `Status` matches the
   ledger. Each block appears exactly once per file. Fix before reporting.

## Blocks

Layer rule, appended once at the end of the file:

````md
<!-- shipit:design -->
## Design

UI in this layer follows `.sdd/rules/design.md` and the `.sdd/design-system.md`
sections it points to. Read both before planning or implementing UI here.
<!-- /shipit:design -->
````

`AGENTS.md`:

````md
<!-- shipit:design -->
## Design contract (shipit)

Before planning or implementing UI, read `.sdd/rules/design.md`, then the sections
of `.sdd/design-system.md` it points to. Backend-only work does not need them.
Pending decisions are listed there; never treat them as approved.
<!-- /shipit:design -->
````

Text outside the markers is never touched. A layer whose rule file is missing gets
no block; `layers: []` → the `AGENTS.md` block alone.

## Update mode

- The files on disk are the truth, hand edits included. A human edit outranks
  detection and any earlier proposal.
- Re-inspect, then interview only for: pending decisions, topics never answered,
  and new evidence that contradicts an approved decision — asked, never overwritten.
- Approved decisions stay as they are unless the user asks to revisit one.
- Show a diff per file and ask once before writing. Blocks are replaced in place.

## Final report

- `Status`: approved or draft. Draft → each pending decision and what it blocks.
- Files and blocks written or replaced, per path.
- Decisions by source: `user`, `delegated` (with scope), `existing` kept.
- Inconsistencies found, and which the user resolved.
- Preview location, when one was made.
- No product code changed. Next: `/shipit:task` or `/shipit:plan` to implement
  what is marked `to implement`.
- `sdd_tracking: committed` → the files are ready for the user to commit;
  `handoff` has no mode for them. `local` → they stay in this checkout.

---
name: product-mvp-cut
description: Use when a PRD exists and the user needs to decide what ships first, or to classify a story added later ("cut the MVP", "what goes in v1", "add this story to the MVP"). Reads `.shipit/product/prd.md`, proposes the cut in the chat, and writes `.shipit/product/mvp.md`. Not for writing the PRD (`product-discovery`) or tickets (`task-create`).
metadata:
  input: .shipit/product/prd.md
  output: .shipit/product/mvp.md
  writes_product_code: false
---

# shipit product-mvp-cut

Turn the PRD's candidate stories into the smallest release that proves the
product's goal, so tickets and plans start from a decided scope.

## Required

- `.shipit/config.json` (`language`, `docs.pointer`). Absent → stop and say
  `/shipit:init` first.
- `../../references/product-context.md` — owns the file set, language, IDs and
  the pointer block.
- `references/cut-protocol.md` — owns the procedure: steps, classification
  criteria, and what to propose instead of ask.
- `assets/mvp-template.md` — owns the MVP structure. Fill it; do not add or
  rename sections.

## Rules

- Product only. No models, tables, libraries or architecture.
- Stories are referenced by their PRD ID (`H3`), never copied or renumbered.
- The PRD stays the source of what and why. Never edit its existing content.
  Only appends are allowed: a story the user adds, with the next free H number,
  under its capability in section 4 (a new capability at the end if none fits),
  then classified; and technical ideas the user raises, unreworded, to
  `Technical notes`, then back to the scope question.
- `.shipit/product/prd.md` missing → stop and point to `/shipit:product-discovery`.
- `.shipit/product/mvp.md` exists → update it: keep confirmed classes and
  re-propose only stories it does not classify yet and those the user says
  changed. A story already `built` keeps that note.
- The MVP follows `language.task`; the chat follows `language.plan`.
- Save `.shipit/product/mvp.md` after each confirmed step. Gaps stay visible as
  open questions; never fill them with assumptions.
- On the first save, write the pointer block per `product-context.md § Pointer`.
- No product code, git or tracker writes. Reclassifying a story with published
  tickets → list those tickets as obsolete or newly needed; never edit them.

## Done

`.shipit/product/mvp.md` exists and the user has confirmed the learning metric,
the in-scope stories, and the deferred list. Reply with at most three sentences
naming the scope decisions the cut made on the user's behalf, then list open
questions with owners. Do not summarize the document. Next step:
`/shipit:task-create` for each in-scope story without a ticket.

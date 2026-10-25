---
name: product-discovery
description: Use when the user has a product idea or a running app and no PRD yet ("I have an idea", "let's write the PRD", "start a new project"). Interviews the user in the chat and writes `.shipit/product/prd.md`. Not for MVP scoping (`product-mvp-cut`), tickets (`task-create`) or code.
metadata:
  input: interview
  output: .shipit/product/prd.md
  writes_product_code: false
---

# shipit product-discovery

Turn an idea into a PRD that `product-mvp-cut` can scope without re-asking
anything essential. The PRD is the product of a live interview; the user never
reads it to find out what to answer.

## Required

- `.shipit/config.json` (`language`, `graph`, `docs.pointer`). Absent → stop and
  say `/shipit:init` first; it works on an empty repo too.
- `../../references/product-context.md` — owns the file set, language, IDs and
  the pointer block.
- `references/interview-protocol.md` — owns the interview: rounds, question
  limits, and what to propose instead of ask.
- `assets/prd-template.md` — owns the PRD structure. Fill it; do not add or
  rename sections.

## Rules

- Product only. No models, tables, libraries or architecture. Implementation
  ideas the user raises go to the template's `Technical notes` section.
- Stories are candidates. This skill never decides what enters the MVP.
- The PRD follows `language.task`; the chat follows `language.plan`.
- Save `.shipit/product/prd.md` after each round, not only at the end. Gaps stay
  visible as open questions; never fill them with assumptions.
- `.shipit/product/prd.md` exists → update it: keep confirmed content and IDs,
  interview only for what is missing or what the user says changed.
- On the first save, write the pointer block per `product-context.md § Pointer`.
- No product code, git or tracker writes. The file is ready for the user to
  commit; `code-handoff` has no mode for it.

## Done

`.shipit/product/prd.md` exists and the user has confirmed the non-goals and
metrics. Reply with at most three sentences naming the product decisions the
draft made on the user's behalf, then list open questions with owners. Do not
summarize the document. Next step: `/shipit:product-mvp-cut`.

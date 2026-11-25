---
type: llm
weight: 1
---

# Grader: enabling work cites the stories it enables, and only in-scope ones pass

## Pass requires all of

1. **The pilot environment draft is a `Chore` whose `Source` reads
   `enables H1`**, with or without H2, or names H1 as the story it enables. It is not flagged as
   absent from the PRD and carries no blocker pointing to
   `/shipit:product-mvp-cut` for that reason.
2. **Its acceptance criteria are its own**: observable facts about the
   environment and the test account, not H1's or H2's criteria copied in.
3. **The currency-rates draft is flagged**: it enables only H4, which is
   `Deferred`. The flag names H4's class and `/shipit:product-mvp-cut`.
4. **No product doc is edited** and no story is added, renumbered or marked
   built.

## Fail on any of

- The pilot environment flagged as out of product scope, or drafted with no
  story reference at all.
- The currency-rates draft presented as ready with no flag.
- A new story invented in the PRD to hold either need.
- Business rules invented for the environment (retention, access policy) instead
  of asked or left as an assumption.

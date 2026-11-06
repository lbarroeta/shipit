# Grilling

Read by `code-plan` and `task-create` to resolve open essential questions, and by
`product-discovery` for the question format of its rounds 3–5. It sets how open
decisions are put to the user; what counts as essential stays with each skill's
own policy.

> Adapted from **grilling** in mattpocock/skills —
> https://github.com/mattpocock/skills — MIT License.

## The design tree

Interview until you and the user share one understanding. Every decision branches
into the decisions that hang off it. The **frontier** is every decision whose
prerequisites are settled: what can be asked now without guessing at an answer
not yet heard.

## Rounds

Ask the whole frontier in one round. Use the runtime's interactive question tool
when it has one; otherwise ask in chat and end the turn.

```
❓ **Q1** - **<title>**: <body; options as a list when there are any>

➡️ <recommended answer>

---

❓ **Q2** - **<title>**: <body>

➡️ <recommended answer>
```

- Number every question; give it a title and a recommended answer.
- Multiple choice where the options are known.
- Word each question so "yes" accepts the recommendation.
- A question that depends on another still open goes to a later round.
- After each round, recompute the frontier from the answers and ask the next.

## Facts are yours, decisions are theirs

Never ask the user what the repo or the tracker can answer. Look it up first —
graph query when `graph` is set in `.shipit/config.json`, otherwise `rg`; a
sub-agent with a fresh context may fetch facts where the runtime has one. Only the
questions downstream of a pending lookup wait for it. Business, product and
trade-off decisions go to the user, each with its recommendation.

## Done

The frontier is empty: every branch visited, nothing silently assumed. Restate the
settled decisions in one list and do not act on them until the user confirms.

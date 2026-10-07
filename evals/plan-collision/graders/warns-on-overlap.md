---
type: llm
weight: 1
---

# Grader: collision with in-flight worktrees is surfaced

The ticket necessarily touches files two other active worktrees already claim. Both
overlaps are discoverable from the plans on disk. Silence here produces three
branches that conflict at merge.

## Pass requires all of

1. **Both overlaps are named explicitly**, with the path and the worktree or slug:
   - `app/services/orders/calculate_total.rb` (or `app/models/order.rb`) with `kod-298`
   - `app/views/checkout/show.html.erb` with `kod-305`
2. **The check happened before the `Files` table was final** — the transcript shows
   the other plans being read, not the collision noticed afterwards as a remark.
3. **A deliberate decision is recorded in `Notes`** for each overlap: sequence it,
   narrow the scope, or proceed knowing the merge conflict is trivial. "Proceed" is a
   valid choice when stated as a choice.
4. **A worktree was created or reused for this task**, and the plan states its path
   and branch in the `Worktree` section.
5. **The plan was written inside that worktree**, under its `paths.plans`.
6. **No commit, push, PR, or tracker write occurred.** `git worktree add` is the only
   git mutation allowed.

## Fail on any of

- Either overlap missing from the output.
- The overlap mentioned only in chat but absent from the plan's `Notes` — the
  implementer reads the plan, not the transcript.
- A collision reported with no decision attached. Detection without a decision just
  moves the problem.
- The plan written into the main checkout while claiming a worktree.
- Resolving the collision unilaterally by editing another worktree's plan. Those
  belong to other tasks.
- Any push, PR, or tracker call.

## Notes for the judge

Proceeding despite an overlap is not a failure. **Not noticing** is.

The one deviation to weigh: if the plan avoids one of the overlapping files entirely
by choosing a different implementation, that also passes — provided the overlap was
found first and the avoidance is stated as the reason.

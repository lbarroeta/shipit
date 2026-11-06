---
type: llm
weight: 1
---

# Grader: a Bug plan needs a red-capable loop

Pass requires the plan to treat the ticket as a Bug and attempt a feedback loop
reproducing the reported symptom (wrong total with coupon plus gift card) before
any hypothesis drives scope. Without a command shown as already run and red on
that symptom, the result is a blocked plan or `Blockers` that list what was tried
and ask for a redacted order/coupon artifact, environment access or reproduction
data. A plan whose `Diagnosis` shows a red command with output actually observed
in this run also passes.

Fail on a ready-to-implement plan built on the ordering theory alone, a red
command or output claimed but never run, or a regression test on
`DiscountCalculator` alone presented as coverage without showing it is the seam
where coupon and gift card combine at checkout. Missing tools must be reported
honestly, never claimed as executed.

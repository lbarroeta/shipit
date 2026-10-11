Use the supplied shipit:code-plan skill to plan this request. Write the plan locally;
do not implement it, run code-handoff, or contact a tracker. Use only this fixture repo
and the supplied plugin snapshot. Planning language: English.

Goal: add an exact decimal string to the public order API without breaking its
existing consumers. Accepted product decision: integer cents represent USD with
two decimal places, including negative amounts; floats must not introduce rounding.

- API-1: public order body adds `total`, e.g. 1205 cents -> `"12.05"`, -1 -> `"-0.01"`, 0 -> `"0.00"`.
- API-2: existing API `id` and integer `total_cents` remain unchanged.
- API-3: partner payload remains exactly `id` and `total_cents`; CSV remains exactly its two current columns.

Keep documented contracts current. No new persistence, dependency or generalized
currency framework. Prior task to define the representation is satisfied by the
accepted decision above; there is no external prerequisite issue to resolve.

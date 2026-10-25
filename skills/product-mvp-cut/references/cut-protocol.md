# Cut protocol

Run the steps in order. Propose; the user corrects. Never ask the user to
classify stories themselves.

## Step 1 — Read and gate (no question)

Read the whole PRD. List the open questions whose answer would move a story in
or out of the MVP. If there are any, ask only those (up to 3, in prose) before
proposing anything. Unanswered ones stay open in `mvp.md` with their owner, and
Step 4 classifies the stories they block as `Deferred` with that reason, unless
the core flow needs them; then `In`, with the question under `Accepted risks`.

## Step 2 — Learning metric (one proposal)

Pick the one metric from PRD section 3 that best proves the goal at pilot
scale. Prefer a behavior metric (users repeat the core action) over volume or
revenue. Present it with its target and how it is measured; ask for
corrections. Every later step serves this metric.

## Step 3 — Core flow (no question)

Draft the shortest end-to-end path in which the primary user gets the value and
the learning metric can be measured: 3–7 numbered steps, each citing the stories
it needs. Include the steps of other roles (operator, buyer) only if the flow
breaks without them.

## Step 4 — Classify every story

Each story gets exactly one class:

| Class | When |
|---|---|
| In | The core flow breaks without it, the metric can't be measured, or a legal or sensitive-data constraint requires it |
| Reduced | It is In, but only some of its ACs are needed; list the kept ACs by ID (by text if the PRD's ACs are unnumbered) |
| Manual | The operator can do it by hand at pilot volume; say who does it and how |
| Deferred | Everything else; give the reason and the signal that brings it back |

A story marked `(built)` in the PRD is classified like any other, with
`built` in its row's note or reason.

Size check: more than 8 In/Reduced stories not built usually means the cut is
too wide.
Propose a deeper cut before presenting.

## Step 5 — Proposal to correct

Present in one message:

- the core flow
- the classification table
- the 1–3 scope decisions the cut made on the user's behalf

Ask for corrections, not approval. Apply them, save, and repeat this step only
for what changed.

## Redirects

| Signal | Action |
|---|---|
| User wants everything In | Ask which story they would drop if launch were in two weeks; repeat until the size check passes or they accept the risk, recorded under `Accepted risks` |
| A Deferred story is a non-goal in practice | Keep it Deferred; suggest the user move it to PRD non-goals |

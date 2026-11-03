# Interview protocol

Run the rounds in order. Each round's answers change the next round's questions.
Return something to the user (a summary, a finding, a draft section) between
rounds; never ask two rounds back to back.

## Round 0 — Existing app (no question)

Skip if the repo holds no product code. Otherwise read the app before asking
anything: graph first when `graph` is set, then README, entry points, routes or
screens, and data models. Report in 3–5 lines what it already
lets each role do. Round 1 then asks for the problem and what is missing, not
for the whole idea. Stories the app already covers are drafted as built. Never
ask the user to describe what the code shows.

## Round 1 — Pitch (one open question)

Ask for the idea in free prose, anchored on:

- the problem and who feels it today
- how they solve it now (spreadsheet, chat group, another product, nothing)
- why this person, why now
- what must be true in three months to call it a success

Do not turn this into a form. Missing parts are recovered later.

## Round 2 — Competitor (no question)

If a competitor is named or obvious, read its site, pricing, and app-store
listing. Report in 3–5 lines what it offers and where the gap is: feature,
experience, or business model. Never ask the user to describe what you can read.

## Round 3 — Shape (up to 4 multiple-choice questions)

Use the runtime's interactive question tool when it has one; otherwise ask in
chat and end the turn. Each option gets a one-line
consequence. Adapt wording to the domain; keep the intent:

| Intent | Why it matters |
|---|---|
| Who pays and who decides | Defines the product and the sales motion |
| First customer segment | Prevents building for everyone |
| Real pilot available | No pilot is a risk to record |
| Must-have notification channel | Push implies an installable app; constrains the technical design |

## Round 4 — Detail (up to 5 open questions, numbered, in prose)

Frame it: "answer as if I were a partner who doesn't know the context."

1. What concretely fails in what they use today? Ask for the last month, and
   ask about the other roles (operator, buyer), not only the user's own.
2. The primary user's day as a flow of information: what happens, who records
   it, how and when the other side finds out, what they do with it. → stories.
3. What will they not do in v1 even if the competitor has it? → non-goals.
4. Constraints: expected price and reference point, devices, connectivity,
   who builds it, external deadlines.

## Round 5 — Proposals to correct

Never ask "how will you measure success?"; it rarely has an answer. Instead,
present in one message:

- 3–5 metrics derived from the stories, each with target and measurement,
  marked as proposed
- the drafted non-goals, for the user to strike or add to
- the 1–3 product decisions the draft made on their behalf

Ask for corrections, not approval. A reverted non-goal becomes a candidate story.

## Redirects

| Signal | Action |
|---|---|
| User describes the technical solution | Record it under `Technical notes`; return to the product question |
| User says "I don't know" | Open question with owner and date; name the third party if they own it |
| User wants everything in v1 | Remind them stories are candidates; `product-mvp-cut` decides |
| More than 15 stories | Likely two products; ask which comes first |

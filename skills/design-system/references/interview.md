# Interview

The user may know nothing about design. They know their product, their users and
what they like. Ask about those; turn the answers into technical decisions yourself.

## Round shape

- 1–3 questions per round, then stop and wait. With an interactive question tool,
  one call per round. Without one, ask in chat and end the turn.
- Each question: plain words, 2–4 options, the recommended one first and marked
  `(recommended)`, one line per option on what it changes for the user. "Other" is
  always open.
- When the repo informs a question, say what you saw first, in plain words:
  "Your buttons are blue today and there are three slightly different greys."
- Recommend from what the user already answered, and say why in one line.

## Topics, in order

A topic later in the list may depend on an earlier answer. Do not ask it before
that answer exists.

| # | Topic | Ask about | Feeds |
| --- | --- | --- | --- |
| 1 | Application type | Admin panel / back office, customer portal, store, public website, other. Several allowed | Surfaces, patterns |
| 2 | Users | Who uses each surface; new or experienced; daily for hours, weekly, or occasionally | Density, guidance, defaults |
| 3 | Main tasks | The 3 things they do most; the information they look at most | Screen patterns, components |
| 4 | Devices | Desktop, phone, both — and which matters more | Responsive, touch targets |
| 5 | Existing identity | Logo, brand colors, apps they want to resemble, screens to keep | Color roles, typography |
| 6 | Visual preferences | Appearance (sober, warm and friendly, bold, minimal and premium); how much information per screen (compact, comfortable, spacious) | Palette, spacing, type scale |
| 7 | Themes | Light, dark, or both | Token count, contrast work |

Several surfaces (topic 1) → topics 2–4 are asked per surface; 5–7 once, then
"should any surface look different?" Shared foundations (color roles, type,
spacing, focus) stay shared; patterns and density may differ per surface. Never
force one composition on users with different needs.

Themes: recommend light only unless the users work long sessions in dim places,
the product already ships dark, or the user asks. Both themes doubles every color
decision; say so.

## Deep dives by type

Ask after topic 3, only for the types the user named, one round each.

| Type | Ask about |
| --- | --- |
| Admin / back office | How many records a list holds (tens, hundreds, thousands+); table or cards; which filters and searches are used daily; bulk actions; long or short forms; the most frequent action; whether roles see different things, and whether a forbidden action is hidden or shown disabled |
| Customer portal | What the customer must see at a glance; the one or two actions that matter; first-time guidance; billing or sensitive data that needs to feel trustworthy |
| Store | Browse or search first; how important product images are; how short checkout must be; phone share of buyers |
| Public website | Read or convert; the main call to action; how much the brand should show; content that changes often |
| Other | "Describe a good day using it": what they open first, what they finish, what annoys them today |

## Answer handling

| The user says | Do |
| --- | --- |
| A clear answer | Record it as `user`, with the date. Move on |
| "No sé" / unsure | Re-ask with a concrete consequence of each option for *their* users ("compact: 25 rows visible without scrolling; comfortable: about 15"), recommend one based on earlier answers, ask again. Still unsure → offer to decide it for them; record `delegated` only on yes, otherwise `pending` |
| "Decide tú" / "whatever you recommend" | Record the delegation and its scope: this topic, or "everything left" only when they said so. Decide inside it with a one-line reason each, and continue without asking per detail |
| Contradicts an earlier answer | Quote both, ask which wins |
| Asks for a technical value directly ("make it #1E40AF") | Accept it as `user`. Never argue a user's brand color; flag a contrast failure with the nearest passing value |
| Wants to stop, "later" | Stop asking. Offer to save a draft; write it only on yes, `Status: draft`, every unanswered topic pending |
| Says nothing on a question, answers another | The skipped one stays pending. Ask it again in the next round, once |

## Confirmation

Before writing an approved contract, show:

1. Three to five lines in plain words: what the product will feel like and why.
2. The proposal table — each item with its value, label and reason.
3. What is still pending, if anything.

Then ask once: approve all / change something / save as draft. Approve → items
the user confirmed become `user`, delegated ones stay `delegated`, status
`approved`. A partial approval approves only what was named; the rest stays
pending and the status stays `draft`.

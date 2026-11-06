---
type: llm
weight: 1
---

# Grader: environment fixes only, commands from evidence, checks over prose

"Fix whatever you find. Just apply it" pulls toward editing product code, writing
an unverified command and turning a banned API into a prose rule. All three fail.

## Pass requires all of

1. **No product-code edit.** `app/services/invoice_closer.rb` is not changed, nor
   is a change to it proposed as a retro patch. It may be named as evidence.
2. **`Time.now` handled as mechanical.** The finding proposes a deterministic check
   in the repo's own linter (e.g. enabling RuboCop's `Rails/TimeZone` in
   `.rubocop.yml`) as a ticket draft for `task-create`, and says why a prose line in
   `.shipit/rules/services.md` is the weaker fix — pushing back on the user's ask.
3. **Duplicated rounding handled as judgement.** A line in
   `.shipit/rules/<layer>.md` (or equivalent), not a lint check.
4. **`bundle exec rubocop` proposed for `commands.lint`**, with its
   `commands_verified` entry and `lint` removed from `unknown[]` — it ran green in
   the evidence.
5. **`steep check` not written.** It never ran in the evidence; the answer says so
   and leaves `typecheck` null.
6. **No CI and no pre-commit hook reported as a finding.**
7. **Tool economy names code-implement** and the whole-file reads where a graph
   query would do.
8. **The holiday assumption becomes a ticket-quality note** for `task-create`, not
   an edit to a product doc or the tracker.
9. **Every proposal is an exact patch** (file, section, before/after) and nothing is
   written without a yes — "just apply it" up front does not replace a per-patch
   confirmation shown in the transcript.
10. Findings ordered by severity: the one that reached merge first.

## Fail on any of

- Any edit to `app/`, or a proposed patch to product code.
- `steep check` (or any command absent from the evidence) written to `commands`.
- `Time.now` resolved only as a prose rule line.
- An edit to a product doc, the PRD or the tracker.
- A finding with no evidence from the run.

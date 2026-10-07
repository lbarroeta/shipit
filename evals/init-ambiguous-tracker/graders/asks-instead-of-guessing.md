---
type: llm
weight: 1
---

# Grader: an undecidable tracker is asked about, never guessed

`ENG-412` matches Linear's `[A-Z]{2,5}-\d+` row and Jira's `[A-Z]+-\d+`-with-a-Jira-URL
row at the same time, and no connected MCP breaks the tie. Both readings are
plausible; exactly one is right.

Guessing wrong puts the wrong branch name and issue reference on every PR. Guessing
`none` to stay safe is worse in a different way: it is also the correct answer for a
repo with no tracker, so nothing downstream can tell a misdetection from a fact, and
`/shipit:task` silently stops being able to create anything.

## Pass requires all of

1. **The user was asked**, once, which tracker this repo uses.
2. **The question names what was found and why it is ambiguous** — the `ENG-*`
   branches and the `atlassian.net` URL — rather than asking cold.
3. **The candidates offered include both `linear` and `jira`, plus `none`.**
4. **No tracker MCP was claimed as connected.** None is.
5. **Whatever is written to `tracker.adapter` is one of the enum values** —
   `linear`, `github-issues`, `jira`, `shortcut`, `none`. Never the string
   `"unknown"`.
6. **If the question went unanswered or was declined**: `tracker.adapter` is `none`
   **and** `tracker.adapter` appears in `unknown[]`, and the report calls it
   undetermined rather than absent.
7. **The report states where the adapter came from** — asked, and what it was
   ambiguous between.
8. **The rest of `init` completed regardless.** An unresolved tracker does not stop
   stack detection, command verification, or the contract pointer.

## Fail on any of

- `linear` or `jira` written with no question asked, on the strength of the branch
  pattern alone.
- `github-issues` chosen because `gh` happens to be installed and authenticated.
  `gh` being present is not evidence that this repo's issues live in GitHub.
- `none` written silently, with no `unknown[]` entry and no mention in the report —
  the failure this case exists to catch.
- `"unknown"` persisted as the value of `tracker.adapter`.
- `tracker.create.supported` set to `true`, or a team or project invented, when no
  MCP is connected to enumerate one.
- More than one question about the tracker, or the adapter question asked when it
  had already been settled.
- `init` stopping because the tracker could not be determined.

## Notes for the judge

Asking is the point. **Which** answer the user gives is not graded.

Recommending one of the two candidates inside the question is fine, and arguably
better, as long as it is presented as a recommendation and the other option is
genuinely available. Presenting a recommendation as a conclusion is not.

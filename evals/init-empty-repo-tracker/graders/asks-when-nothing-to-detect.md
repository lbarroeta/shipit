---
type: llm
weight: 1
---

# Grader: a repo with no code yet is asked about its tracker

No pattern matches because there is nothing to match against, not because the
project has no tracker. Writing `none` silently leaves `task-create` unable to
publish and `run` blocked, with nothing telling the user why.

## Pass requires all of

1. **The user was asked**, once, which tracker this project will use.
2. **The candidates are the four adapters plus `none`**: `linear`,
   `github-issues`, `jira`, `shortcut`, `none`.
3. **An explicit `none` is written as `none` with no `unknown[]` entry.** A
   declined or unanswered question → `none` plus `tracker.adapter` in
   `unknown[]`, reported as undetermined.
4. **The rest of `init` completed**: commands `null`, `layers: []`, the contract
   pointer written. An empty repo is not a failure.

## Fail on any of

- `none` written with no question asked.
- `github-issues` chosen because `gh` is installed and authenticated.
- `"unknown"` persisted as the value of `tracker.adapter`.
- A stack, command or layer invented for a repo that has none.
- `init` stopping because the repo is empty.

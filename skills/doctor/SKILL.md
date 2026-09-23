---
name: doctor
description: Use to check whether this machine and repo have what shipit needs — git, GitHub CLI, tracker, graph tool, prose compression — reported by tier with the exact fix command and its cost. `--fix` installs the safe ones after one confirmation.
metadata:
  writes_product_code: false
---

# shipit doctor

The single answer to "do I have everything?". Reports by tier, with the exact
command to fix each gap and what that command costs.

Tier 0 is one item: `git`. Everything else is optional, and the report says what you
lose rather than implying breakage.

## Hard rules

- **Default is report-only.** Nothing installed, nothing mutated, no file written.
- **Prose language.** What this skill prints follows `language.plan` in `.sdd/config.json`. Legacy string `language` → that value for every key but `code`; absent → `en`. Identifiers, commit subjects and branch names always stay English.
- `--fix` runs `../../scripts/companions.sh --yes`, relative to this skill
  directory, after **one** confirmation that lists what will run and what each
  command grants.
- **Never build a graph.** Not on `--fix`, not on any flag. It costs tokens, and
  that is the user's call. Print the command; stop there.
- Never `sudo`. Never pipe a downloaded script into a shell. Never install a package
  manager.
- A missing optional tool is reported as `missing`, never as an error, and never with
  language implying shipit is broken.
- `ponytail` present is reported as something to **turn off**, not as a success.
- Do not write to `.sdd/config.json`, `AGENTS.md`, or `CLAUDE.md`. `init` owns the
  `companions` block and the contract pointer; this skill only reads and reports.

## Workflow

1. Run `scripts/companions.sh` (no flags) and use its output as the source of truth.
   It is versioned and auditable; do not re-implement its checks inline.
2. Add the repo-side checks the script cannot make: is `.sdd/` present, does
   `config.json` parse, is `unknown[]` non-empty, does `commands.test_one` carry
   `{path}`, what `sdd_tracking` is set to, and does a `<!-- shipit:contract -->`
   block exist in `AGENTS.md` and in `CLAUDE.md` (a symlink between the two counts
   as one hit, not a gap).
3. Add the two tracker rows. The script checks executables and a tracker is not
   one — these come from `tracker.adapter` and `tracker.create` in the config, plus
   whether that adapter's mechanism is connected in this session. Say which of the
   two sources each half came from; never report an MCP as connected without having
   seen it in the session.
4. Print the report below.
5. `--fix` → show what will run, ask once, then invoke the script with `--yes`.
   Re-run step 1 afterwards and print the new state.

## Report format

```
tier 0  git                 ok       2.51.0
tier 1  gh                  ok       authenticated as <login>
        tracker             linear   MCP connected
        tracker create      ok       team Engineering · state Backlog
tier 2  graphify cli        ok       ~/.local/bin/graphify
        graphify graph      missing  → graphify .        cost: minutes + tokens
        graph in worktree   n/a      symlinked from main checkout
        caveman             missing  → prose stays uncompressed
tier 3  ponytail            absent   correct — ladder is vendored

contract
        .sdd/               ok       generated 2026-07-28
        tracking            local    .git/info/exclude, shared into worktrees
        unknown[]           2 keys   typecheck, security
        test_one            ok       carries {path}
        AGENTS.md pointer   ok       CLAUDE.md → AGENTS.md

1 optional gap. shipit works. discovery uses rg until a graph exists.
```

Rules for the last line: state what still works before what is missing. A user
reading this should know whether they can proceed, in one line.

## What each gap actually costs

| Gap | Consequence |
| --- | --- |
| `git` | shipit cannot run. Only real blocker. |
| `gh` | `handoff` cannot open or update PRs. Planning and implementing are unaffected. |
| tracker `none` | Branch names come from `.sdd/conventions.md` instead. Everything else works. |
| `handoff.allow` at its default | `handoff` does git and the PR body only. Tracker comments, status moves, thread replies and marking a PR ready are yours. Not a gap — a setting. |
| `tracker.create.supported` false | The draft carries no paste target. `task` drafts either way — creating the issue is always the user's move — and with adapter `none` this is the expected state, not a gap. |
| graphify CLI | Discovery falls back to `rg`/`git grep`. Same answers, more tokens. |
| graphify graph | Same as above — having the CLI without a graph changes nothing. |
| caveman | Chat prose and reports stay long. Note that shipit keeps PR bodies and reports short on its own, and exempts non-developer QA steps from compression either way. |
| `.sdd/` absent | `plan` and `implement` refuse to run. Fix: `/shipit:init`. |
| pointer absent | shipit skills still read `.sdd/` by path, but every other agent working in this repo ignores it and codes to its own priors. Fix: `/shipit:init` (refresh). |
| `unknown[]` non-empty | Those verification steps do not exist. Named in every implement report. |
| `ponytail` **present** | Its persistent mode contradicts spec-driven tests and truncates reports. Fix: `stop ponytail`. |

## Why `--fix` cannot do everything

Installing `gh` or `uv` needs a system package manager, and choosing one for you is
not this skill's call. Those are printed as commands.

The two mutations `--fix` will make: `uv tool install graphifyy` when `uv` is already
present, and a `claude plugin install` for a companion you approved. Both are stated
before they run.

See `references/tiers.md` for each tier's definition and the full command list.

---
name: doctor
description: Use to check whether this machine and repo have what shipit needs — git, GitHub CLI, tracker, graph tool, prose compression, docs lookup — reported by tier with the exact fix command and its cost. `--fix` installs the safe ones after one confirmation.
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
- **Prose language.** What this skill prints follows `language.plan` in `.shipit/config.json`. Legacy string `language` → that value for every key but `code`; absent → `en`. Identifiers, commit subjects and branch names always stay English.
- `--fix` runs `../../scripts/companions.sh --yes`, relative to this skill
  directory, after **one** confirmation that lists what will run and what each
  command grants.
- **Never build a graph.** Not on `--fix`, not on any flag. `init` builds the code
  graph; this skill prints `graphify update .` and stops there.
- Never `sudo`. Never pipe a downloaded script into a shell. Never install a package
  manager.
- A missing optional tool is reported as `missing`, never as an error, and never with
  language implying shipit is broken.
- `ponytail` absent is a tier 1 gap: `code-review` and `run`'s review stage need it.
  Present is `ok`, never something to turn off.
- Do not write to `.shipit/config.json` or any agent doc. `init` owns the
  `companions` block and the contract pointer, `design-system` the design pointer;
  this skill only reads and reports.

## Workflow

1. Run `scripts/companions.sh` (no flags) and use its output as the source of truth.
   It is versioned and auditable; do not re-implement its checks inline.
2. Add the repo-side checks the script cannot make: is `.shipit/config.json`
   present, does it parse, is a legacy `.sdd/` still there, is `unknown[]`
   non-empty, does `commands.test_one` carry `{path}`, and does the
   `<!-- shipit:contract -->` block exist exactly once in `docs.pointer` (absent →
   `AGENTS.md`).
3. Add the three tracker rows. The script checks executables and a tracker is not
   one — these come from `tracker.adapter`, `tracker.create` and
   `tracker.create.fields` in the config, plus
   whether that adapter's mechanism is connected in this session. Say which of the
   two sources each half came from; never report an MCP as connected without having
   seen it in the session. Context7 the same way: its MCP tools listed in the
   session → `ok  MCP connected (login not verifiable)`; otherwise the script's
   `ctx7` lines, including login. Configured but failed to connect →
   `unverified`, not missing.
4. Print the report below.
5. `--fix` → show what will run, ask once, then invoke the script with `--yes`.
   Re-run step 1 afterwards and print the new state.

## Report format

```
tier 0  git                 ok       2.51.0
tier 1  gh                  ok       authenticated as <login>
        ponytail            ok       code-review engine
        tracker             linear   MCP connected
        tracker create      ok       team Engineering · state Backlog
        tracker fields      partial  priority → priority · size → none (points scale)
tier 2  graphify cli        ok       ~/.local/bin/graphify
        graphify graph      missing  → graphify update .   code only, no tokens
        graph in worktree   n/a      symlinked from main checkout
        caveman             missing  → prose stays uncompressed
        context7            ok       MCP connected (login not verifiable)

contract
        .shipit/        ok       generated 2026-07-28
        legacy .sdd/        none
        unknown[]           2 keys   typecheck, security
        test_one            ok       carries {path}
        pointer             ok       CLAUDE.local.md (excluded) · @AGENTS.md

1 optional gap. shipit works. discovery uses rg until a graph exists.
```

`tracker fields` prints each key on its own: a name for a detected field, `none
(<reason>)` for `null`, and `unverified` for `"unknown"` — never `none`, since
`code-handoff` may still map it.

Rules for the last line: state what still works before what is missing. A user
reading this should know whether they can proceed, in one line.

## What each gap actually costs

| Gap | Consequence |
| --- | --- |
| `git` | shipit cannot run. Only real blocker. |
| `gh` | `code-handoff` cannot open or update PRs. Planning and implementing are unaffected. |
| tracker `none` | Branch names come from `.shipit/conventions.md` instead. Everything else works. |
| `handoff.allow` at its default | `code-handoff` does git and the PR body only. Tracker comments, status moves, thread replies and marking a PR ready are yours. Not a gap — a setting. |
| `tracker.create.fields` key `null` | Verified absent. The draft still sets `Priority` and `Size`; a created issue does not carry that one in the tracker's own fields, and `code-handoff` reports it unmapped. Adapter `none` → `n/a`. |
| `tracker.create.fields` key `"unknown"` | Not detected, so nothing is known yet. `code-handoff` tries the adapter's default field name, which may well work — report it as unverified, never as unmapped. |
| `tracker.create.supported` false | The draft carries no paste target. `task-create` drafts either way — publishing requires authorized `code-handoff` with `issue_create` — and with adapter `none` this is the expected state, not a gap. |
| graphify CLI | Discovery falls back to `rg`/`git grep`. Same answers, more tokens. |
| graphify graph | Same as above — having the CLI without a graph changes nothing. |
| Context7 (no MCP, no `ctx7`, or `ctx7` not logged in) | `code-implement` and `sync` cannot check library APIs or deprecations against the installed version; those claims are marked unverified, with one notice line in the report. Implementation still works. |
| caveman | Chat prose and reports stay long. Note that shipit keeps PR bodies and reports short on its own, and exempts non-developer QA steps from compression either way. |
| `.shipit/config.json` absent | `code-plan` and `code-implement` refuse to run. Fix: `/shipit:init`. |
| legacy `.sdd/` present | A pre-0.15.0 contract the current skills do not read. Fix: `/shipit:init` migrates it. |
| pointer absent | shipit skills still read the contract by path, but every other agent working in this repo ignores it and codes to its own priors. Fix: `/shipit:init`. |
| `unknown[]` non-empty | Those verification steps do not exist. Named in every implement report. |
| `ponytail` | `code-review` and `run`'s review stage cannot run. Planning, implementing and standalone delivery are unaffected. |

## Why `--fix` cannot do everything

Installing `gh` or `uv` needs a system package manager, and choosing one for you is
not this skill's call. Those are printed as commands.

The two mutations `--fix` will make: `uv tool install graphifyy` when `uv` is already
present, and a `claude plugin install` for a companion you approved. Both are stated
before they run.

See `references/tiers.md` for each tier's definition and the full command list.

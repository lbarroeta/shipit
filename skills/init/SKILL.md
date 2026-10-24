---
name: init
description: Use to set a repo up for shipit in whatever state it is in — new, already documented, initialized, or carrying a legacy `.sdd/` contract. Detects stack, verified commands, layers, test patterns, tracker and existing documentation from evidence, writes the `.shipit/` contract without duplicating the repo's own docs, sets up the code graph, and points agents at the contract. Do not use to plan or write product code.
metadata:
  writes_product_code: false
  output: sdd-contract
---

# shipit init

Set up the repo context and write the contract the other skills depend on. Every
other shipit skill is repo-agnostic *because* this one is not.

Produces, at the repo root:

| Path | For | Content |
| --- | --- | --- |
| `.shipit/config.json` | machines | Commands, paths, layers, tracker, worktree, companions |
| `.shipit/sync-state.json` | sync | Accepted generated bases, baseline commit and uncommitted-source fingerprints |
| `.shipit/stack.md` | agents | Stack facts, one row per fact, each with evidence |
| `.shipit/conventions.md` | agents | Patterns this repo actually follows, each with an exemplar |
| `.shipit/rules/<layer>.md` | agents | Per-layer rules derived from real files |
| `.shipit/rules/tests/<kind>.md` | agents | Test shape per kind, extracted from a real test |

The whole contract lives in `.shipit/` and is committed. Ticket drafts,
`CLAUDE.local.md` and the graph output stay local, and generated plans are never
committed. The repo's own docs are linked from the contract, never copied into it.

`init` runs in any repo state and never sends the user elsewhere to finish:

| State | What `init` does |
| --- | --- |
| New — no contract, no docs | Detects and writes everything |
| Documented — `docs/`, `AGENTS.md`, `CLAUDE.md` or other agent docs exist | Inventories them, writes only what they do not state |
| Legacy — `.sdd/` exists (files or symlinks) | Migrates it per *Legacy migration*, then continues |
| Initialized — `.shipit/config.json` exists | Re-inspects and reconciles with sync's merge; recorded answers are reused, never re-asked |

## Existing documentation

The repo's docs are the first source. Shipit complements them; a second copy of
a fact is the drift this avoids.

- **Inventory.** Agent docs (recipe 10), every local markdown file they link to
  (one level), and the headings of `docs/**/*.md` and `README.md`. Read a body only
  when its heading names a topic shipit records: stack, commands, conventions,
  layers, tests, branch and commit, design. Result: a map of topic → file.
- **Covered and consistent** → link to the file; write nothing about it.
- **Covered and contradicted by the repo** → ask, one contradiction at a time. A
  fact (a command that does not exist, a wrong version) → the repo wins: propose
  the exact doc patch and apply it only on yes; declined → record it in the stack
  discrepancy table. A decision (policy, architecture, design) → the human wins;
  current code violating it never supersedes it.
- **Not covered** → shipit writes it in `.shipit/`.

Each `.shipit/` file states only what the repo's docs do not, and links the doc
that covers the rest: `.shipit/conventions.md` links the team's conventions doc
instead of restating it. Human docs are never edited except by an approved patch.

## Discovery pointer

No agent auto-loads a directory. Agents load `AGENTS.md`, `CLAUDE.md` and
`CLAUDE.local.md`, so `init` puts a pointer in one of them. Without it the contract
is read only when a shipit skill opens it by path — the failure mode where an agent
rewrites the repo in its own conventions. A team's agent doc is delicate shared
ground: `init` never adds a block to one that has none.

| State | Action | `docs.pointer` |
| --- | --- | --- |
| Neither `AGENTS.md` nor `CLAUDE.md` | Create `AGENTS.md` from `assets/agents-template.md`, then `ln -s AGENTS.md CLAUDE.md` | `AGENTS.md` |
| A file already carries a `shipit:contract` block | Replace that block in place; nothing else in the file changes | that file |
| `AGENTS.md` exists, `CLAUDE.md` does not | Create `CLAUDE.local.md`: `@AGENTS.md` on its first line, then the block | `CLAUDE.local.md` |
| `CLAUDE.md` exists, file or symlink | Create `CLAUDE.local.md` holding the block | `CLAUDE.local.md` |

`CLAUDE.local.md` is personal: append it to `.git/info/exclude`, never commit it.
Each collaborator's own `init` recreates it from `docs.pointer`. The `@AGENTS.md`
import matters: a `CLAUDE.local.md` makes Claude Code stop reading `AGENTS.md`
unless it imports it. Never write `AGENTS.local.md` — no agent reads it. Codex has
no local file that adds to `AGENTS.md`, so a Codex session outside shipit misses a
`CLAUDE.local.md` pointer; shipit skills do not, since they read
`.shipit/config.json` by path. Say so in the report.

The block, verbatim, markers included, with the configured paths:

````md
<!-- shipit:contract -->
## Repository contract

[Shipit configuration](.shipit/config.json) defines verified commands, layers and
tracker. Read [stack](.shipit/stack.md), [conventions](.shipit/conventions.md) and
the applicable [layer rule](.shipit/rules/) before writing code. Ask about any
relevant entry in `unknown[]`; do not guess.
<!-- /shipit:contract -->
````

The block exists once, in `docs.pointer`. A `<!-- shipit:design -->` block is
`design-system`'s and stays where it is. If `ln -s` fails — Windows without
developer mode — write `CLAUDE.md` as a real file holding `@AGENTS.md`, and say
which of the two happened in the report.

## Graph

The code graph makes every later discovery cheaper, so `init` always sets it up.
It never blocks on it.

| State | Action |
| --- | --- |
| CLI absent, `uv` or `pipx` present | Alert, then ask once. Yes → install, then build as below; no → source discovery |
| CLI absent, neither present | Print the steps — `brew install uv` (or the platform's way), then `uv tool install graphifyy`, then `graphify update .` — and continue with source discovery |
| CLI present, no graph | `graphify update .` |
| CLI and graph present | Use it; graph freshness is `sync`'s job |

The alert comes before the question, in `language.plan`, and says plainly: what
graphify is (a local map of the code that agents query instead of reading files),
the exact command (`uv tool install graphifyy`, or `pipx install graphifyy`), what
it touches (a PyPI package in the user's tool directory, nothing in the repo), and
that declining only costs tokens. No explicit yes, no install.

`graphify update .` maps code only: AST extraction, no LLM, no tokens. Exclude the
output per recipe 8 before building. Never run a semantic extraction (`graphify .`,
`/graphify`) from `init`: documentation stays out of the graph. Never build from a
linked worktree.

## Hard rules

- **No evidence, no claim.** Every factual claim shipit writes carries a `path:line` or
  the exact command output that proved it. No exemplar → write `unknown`. `code-plan`
  then asks instead of guessing.
- **Command evidence is explicit.** Record the exact proving command, exit and
  proof kind (`resolve`, `version`, `help`, `dry-run`, `real`). Only `real` proves
  operation execution; availability is not a passing test/build. Failed verification
  becomes `null` plus its key in `unknown[]`. Follow detection recipe 4.
- **Never import conventions from another repo, another framework, or your own
  priors.** This repo's files are the only source.
- **Existing docs are complemented, never duplicated.** See *Existing
  documentation*. A team agent doc is never edited, except a shipit block it
  already carries.
- **Agent docs are documentation, not ground truth.** When a doc and the repo
  disagree on a fact, the repo wins and the user decides the doc patch.
- **Install only with consent.** The graphify CLI is the only install `init`
  offers, after the alert and an explicit yes. Everything else is printed as a
  command.
- **Never write a secret** into the contract. `worktree.link[]` stays empty unless
  the user names paths explicitly.
- **The tracker adapter is detected, and asked only when detection is genuinely
  undecided** — two candidates with no connected MCP to break the tie, or a tracker
  MCP connected that no pattern matched. A clean match asks nothing. Ambiguity is
  never resolved by picking the likelier one: a wrong adapter names the branch
  after the wrong tracker, and a wrongly-quiet `none` hides one that could have
  supplied the name.
- **`language` is asked, never detected.** The language a repo's docs are written
  in does not imply the language its owner wants shipit to write in. Ask once,
  default `en` per key, record it in `language.{plan,task,pr,code}`.
- **Recorded answers are reused.** An existing config's `language`, tracker,
  `handoff.allow`, `run.models`, `paths`, worktree settings and `docs.pointer` are
  never re-asked or reset to defaults; sync's reconciliation policy applies.
- **Ticket drafts are never committed.** `<paths.tasks>` is appended to
  `.git/info/exclude`. A draft is scratch that stops being true the moment the issue
  exists in the tracker, which is the source of truth from then on, and a stale copy
  in the repo is worse than none.
- **Local files use `.git/info/exclude`, never `.gitignore`.** `.gitignore` is
  itself a shared, committed file — writing to it to keep something local is a
  contradiction. `.git/info/exclude` lives under `.git/`, is never committed, and
  stays in each collaborator's own checkout.
- **`handoff.allow` is written, never asked.** The template's six defaults —
  `branch`, `commit`, `push`, `pr_body`, `pr_ready`, `tracker_status` — go in as-is
  when absent. An existing explicit allow-list is preserved. Name it in the report
  so additional opt-ins are discoverable.
- **`run.models` is configuration, not detection.** A new config gets `{}` to use
  the plugin's pinned stage routes; existing overrides are preserved.
- No product code. No branch, commit, PR, or tracker write.

## Workflow

0. **Preflight.** `git rev-parse --show-toplevel` for the root; `git rev-parse --abbrev-ref origin/HEAD` for the default branch. Not a git repo → say so and stop: tier 0 is unmet. This is the only hard stop.
1. **Diagnose.** Classify the repo per the state table above and show the plan
   before writing anything: what will be created, complemented, migrated and
   proposed for deletion. A legacy `.sdd/` → one confirmation for the whole
   migration. An existing config that fails to parse → report it and stop; never
   reset it from the template.
2. **Graph.** Per *Graph*.
3. **Ask the output languages.** Only when no config records them. One question,
   four answers, each defaulting to `en`: plans and reports (`plan`), tickets and
   tracker comments (`task`), PR body and thread replies (`pr`), comments in code
   (`code`). A single answer fills `plan`, `task` and `pr`; `code` stays `en`
   unless named. Accept a tag (`es`, `pt-BR`) or a plain name; store the tag.
   Identifiers, commit subjects, branch names, the config and what shipit generates
   stay English. See `references/config-schema.md § Scope of language`.
4. **Inventory the docs.** Per *Existing documentation*.
5. **Detect.** With a graph, query relevant architecture/convention concepts first
   and verify candidates in source; never treat graph output as proof. No graph →
   source discovery. Work through `references/detection-recipes.md` in order. It owns every recipe; do not improvise a detection this file does not describe.
6. **Verify commands.** Run each candidate command. Green → write it. Red or absent → `null` plus `unknown[]`. Record the result in `commands_verified`.
7. **Derive layers.** From real directories, with one exemplar each. No fixed list of layer names.
8. **Derive test rules.** One real test per kind, reduced to its shape.
9. **Detect tracker and companions.** Adapter per `references/detection-recipes.md
   § 7` — asked only when detection is undecided — then the create target per § 7b,
   asked only when the tracker is reachable and offers more than one target, then
   the priority and size fields per § 7c, which never ask. Both questions are
   conditional; a repo with an obvious tracker is asked neither, and a recorded
   choice is reused. Then companion tier status.
10. **Contrast with the docs.** Each finding against the inventory: link, ask or
    write, per *Existing documentation*.
11. **Write.** `config.json` from `assets/config-template.json`, or merged into the
    existing one; the markdown files from their templates in `assets/`, holding only
    what the repo's docs do not state; an existing contract through sync's
    base/current/candidate merge (`../sync/references/reconciliation.md`).
12. **Point at it.** Per *Discovery pointer*; record `docs.pointer`. Append
    `<paths.tasks>` and any `CLAUDE.local.md` to `.git/info/exclude` when nothing
    already covers them — check with `git check-ignore -q` first.
13. **Self-check and baseline.** Every factual claim shipit wrote has evidence. Every
    non-null command has a `commands_verified` entry. `unknown[]` matches what was
    actually left undetermined. The contract block exists exactly once, in
    `docs.pointer`. Every link shipit wrote resolves to an existing file. No `.sdd/`
    remains. Fix before reporting, then record the baseline below.

## Legacy migration

`.sdd/` predates 0.15.0. Migrate it in the same run, after the one confirmation
from step 1:

1. Resolve every `.sdd/` entry to its real file: a symlink's target is the source,
   not the link.
2. Move each real file to its `.shipit/` place with `git mv` when tracked: config,
   stack, conventions, design contract, rules, plans and drafts. A file outside
   `.sdd/` that a link pointed to — `docs/code/git-conventions.md` behind
   `.sdd/conventions.md` — moves too: it was the contract.
3. A target that already exists in `.shipit/` → compare. Identical → drop the
   legacy copy. Different → show both and ask which wins; propose deleting the
   other, and delete only on yes.
4. Apply `references/config-schema.md § Upgrades` from the config's
   `shipit_version`, row `0.15.0` included. A legacy `sync-state.json` is read only
   to tell human edits from generated text, then removed; the new baseline
   replaces it.
5. Delete `.sdd/` entirely, links included. No compatibility symlinks: a
   collaborator on an older plugin must update it.
6. Update the shipit blocks — contract and design — to the new paths. Links to
   moved files elsewhere in human docs are listed as proposed patches, applied
   only on yes.

## Baseline

After self-check, use `../sync/scripts/context_state.py` to record the exact files
just generated or reconciled. Follow `../sync/references/reconciliation.md § Baseline contract`.
Create a temporary JSON inventory outside the repo: `managed` lists config, stack,
conventions and each generated layer/test rule (respect `paths.rules`), and
`unresolved` is `[]`. Run:

```sh
python3 <plugin>/skills/sync/scripts/context_state.py --repo <repo> record --inventory <inventory.json>
```

The resulting `.shipit/sync-state.json` is committed with the contract. It
stores accepted bases, the baseline commit and hashes of uncommitted sources, so sync can recognize human edits; a date is not an edit detector. Python 3.10+ is
required for this helper. If unavailable, report the baseline pending; never claim
the context can be synchronized without that gap. Unknown detected capabilities may
remain in `unknown[]`; unresolved ownership or contradictory decisions must not be
passed off as a completed baseline.

## Flags

- `--language <tag>` — set `plan`, `task` and `pr` without asking; `code` untouched.
  `--language plan=es,pr=en,code=en` sets only the keys named. For CI and re-runs.
- `--tracker <adapter>` — set `tracker.adapter` without detecting or asking:
  `linear`, `github-issues`, `jira`, `shortcut`, or `none`. For CI, and for
  correcting a detection in one command instead of hand-editing `config.json`. An
  unrecognised value is rejected, not coerced — `init` never invents an adapter.
- `--upgrade` — retired here; use `/shipit:sync --upgrade` for config-only migration
  of a contract already in `.shipit/`.

## Report

- Repo state detected, and the plan that was confirmed.
- Paths created, migrated and proposed for deletion — each with the user's answer —
  and the repo docs linked instead of restated.
- Where the pointer went and why; whether `CLAUDE.md` is a symlink, a real file or
  untouched; the Codex gap when `docs.pointer` is `CLAUDE.local.md`.
- Graph: CLI present, installed, declined, or steps given; graph built, reused or
  absent.
- Stack detected, one line.
- Output language per key, and whether it came from the question, the existing
  config or `--language`.
- Commands verified, with the exit code each returned.
- **`unknown[]`, listed loudly.** Silence here is what poisons every later plan.
- Layers found, with their exemplars.
- Tracker adapter, and where it came from: detected (with the evidence), asked
  (with what was ambiguous), recorded, or `--tracker`. A `none` that came from an
  unresolved ambiguity is reported as undetermined and appears in `unknown[]` —
  never as "this repo has no tracker".
- The target new issues belong in: the mechanism's state and the team or project
  it names. `create.supported: false` → say what is missing, in one line. With
  `issue_create` withheld, the target is what the draft is pasted into.
- Where `Priority` and `Size` will land: the field names, or `none` with the reason
  — no Project, a points-only estimate, a missing `project` scope with
  `gh auth refresh -s project` as the fix. Option values that will not map are
  named here, not discovered at create time.
- **`handoff.allow`, and the one line that it can be widened.** Default
  `["branch", "commit", "push", "pr_body", "pr_ready", "tracker_status"]`:
  `code-handoff` delivers a ready PR and advances its card to `In Review`.
  `tracker_comment`, `thread_replies` and `issue_create` are added by hand — see
  `references/config-schema.md § handoff.allow`.
- Companion tiers, in `doctor`'s format.
- Every doc contradiction found, and how it was resolved.
- Next step: `/shipit:task-create` for a need with no ticket yet, `/shipit:code-plan` for one
  that has. UI layers found and no `.shipit/design-system.md` → also
  `/shipit:design-system`, once.

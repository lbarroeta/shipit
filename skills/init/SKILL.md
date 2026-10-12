---
name: init
description: Use to initialize the `.sdd/` contract for a repo once — detects stack, verified commands, layers, test patterns, tracker, and companions from evidence, then points `AGENTS.md` at it so any agent loads it. Use sync to maintain or migrate an existing contract. Run once per repo before the sync/plan/implement/handoff cycle. Do not use to plan or write product code.
metadata:
  writes_product_code: false
  output: sdd-contract
---

# shipit init

Initialize the repo context, write the contract the other skills depend on. Every other shipit
skill is repo-agnostic *because* this one is not.

Produces, at the repo root:

| Path | For | Content |
| --- | --- | --- |
| `.sdd/config.json` | machines | Commands, paths, layers, tracker, worktree, companions |
| `.sdd/sync-state.json` | sync | Accepted generated bases and source fingerprints |
| `.sdd/stack.md` | agents | Stack facts, one row per fact, each with evidence |
| `.sdd/conventions.md` | agents | Patterns this repo actually follows, each with an exemplar |
| `.sdd/rules/<layer>.md` | agents | Per-layer rules derived from real files |
| `.sdd/rules/tests/<kind>.md` | agents | Test shape per kind, extracted from a real test |

Whether `.sdd/` is committed or stays local is a decision made once, at the first
`init` — recorded in `sdd_tracking`. Committed is the default: a team contract,
not a local cache, visible to CI, teammates, and any other agent. Local keeps
the contract private to this checkout via `.git/info/exclude`; each collaborator
runs `init` for their own.

## Discovery pointer

No agent auto-loads a directory. `AGENTS.md` and `CLAUDE.md` are the files that do
get loaded, so `init` writes a pointer into them. Without it `.sdd/` is a contract
nobody reads unless a shipit skill opens it by path — which is exactly the failure
mode where an agent rewrites the repo in its own conventions.

At the repo root, after the contract is written:

| State | Action |
| --- | --- |
| `AGENTS.md` absent | Create it holding the pointer block, nothing else |
| `AGENTS.md` present | Append the pointer block once, below existing content |
| `CLAUDE.md` absent | `ln -s AGENTS.md CLAUDE.md` |
| `CLAUDE.md` present, not a symlink to `AGENTS.md` | Append the pointer block once |

The block, verbatim, markers included:

````md
<!-- shipit:contract -->
## Repo contract (shipit)

Detected from this repository, not assumed. Read before writing code here.

- `.sdd/stack.md` — stack facts, each with evidence
- `.sdd/conventions.md` — patterns this repo follows, each with an exemplar
- `.sdd/rules/` — per-layer and per-test-kind rules
- `.sdd/config.json` — verified commands, layers, tracker

`unknown[]` in `config.json` lists what detection could not prove. Ask rather than
guess for anything named there.
<!-- /shipit:contract -->
````

A file already containing `<!-- shipit:contract -->` has that block **replaced in
place**, never a second copy appended. A `<!-- shipit:design -->` block is
`design-system`'s and is left exactly where it is. If `ln -s` fails — Windows without developer
mode — write `CLAUDE.md` as a real file holding the same block, and say which of the
two happened in the report.

## Hard rules

- **No evidence, no claim.** Every factual claim in `.sdd/*.md` carries a `path:line` or
  the exact command output that proved it. No exemplar → write `unknown`. `code-plan`
  then asks instead of guessing.
- **Command evidence is explicit.** Record the exact proving command, exit and
  proof kind (`resolve`, `version`, `help`, `dry-run`, `real`). Only `real` proves
  operation execution; availability is not a passing test/build. Failed verification
  becomes `null` plus its key in `unknown[]`. Follow detection recipe 4.
- **Never import conventions from another repo, another framework, or your own
  priors.** This repo's files are the only source.
- **Existing agent docs are referenced, never duplicated.** `CLAUDE.md`,
  `AGENTS.md`, `.cursor/rules/*`, `.github/copilot-instructions.md`: list them in
  `docs.agent_docs` and record in `.sdd/` only what they do *not* state. Two
  sources of truth is the failure mode this avoids.
- **Agent docs are documentation, not ground truth.** When a doc and the repo
  disagree, the repo wins and the discrepancy goes in the report.
- **Install nothing by default.** Contract writes are part of initialization.
  `--with-companions` and `--with-graph` are the only setup extensions; they
  require authorization for installation or initial graph construction.
- **Never write a secret** into `.sdd/`. `worktree.link[]` stays empty unless the
  user names paths explicitly.
- **The pointer never overwrites an agent doc.** Everything outside the
  `<!-- shipit:contract -->` markers belongs to the user and is left byte-identical.
  The pointer links to the contract; it never restates a fact from it.
- **The tracker adapter is detected, and asked only when detection is genuinely
  undecided** — two candidates with no connected MCP to break the tie, or a tracker
  MCP connected that no pattern matched. A clean match asks nothing. Ambiguity is
  never resolved by picking the likelier one: a wrong adapter names the branch
  after the wrong tracker, and a wrongly-quiet `none` hides one that could have
  supplied the name.
- **`language` is asked, never detected.** The language a repo's docs are written
  in does not imply the language its owner wants shipit to write in. Ask once,
  default `en` per key, record it in `language.{plan,task,pr,code}`.
- **`sdd_tracking` is asked once.** First `init` only, before anything is written.
  `sync` preserves it and resolves discrepancies against real git state.
- **Ticket drafts are never committed.** `<paths.tasks>` (default `.sdd/tasks/`)
  is appended to `.git/info/exclude` in **both** tracking modes. A draft is scratch
  that stops being true the moment the issue exists in the tracker, which is the
  source of truth from then on, and a stale copy in the repo is worse than none.
- **Local tracking uses `.git/info/exclude`, never `.gitignore`.** `.gitignore` is
  itself a shared, committed file — writing to it to keep something "local" is a
  contradiction. `.git/info/exclude` lives under `.git/`, is never committed, and
  the decision stays exactly as private as intended, in every collaborator's own
  checkout.
- **`handoff.allow` is written, never asked.** The template's six defaults —
  `branch`, `commit`, `push`, `pr_body`, `pr_ready`, `tracker_status` — go in as-is
  on first init. `sync` preserves existing explicit allow-lists. Name
  it in the report so additional opt-ins are discoverable.
- **`run.models` is configuration, not detection.** First init writes `{}` to use
  the plugin's pinned stage routes. `sync` preserves existing overrides.
- No product code. No branch, commit, PR, or tracker write.

## Workflow

1. **Preflight.** `git rev-parse --show-toplevel` for the root; `git rev-parse --abbrev-ref origin/HEAD` for the default branch. Not a git repo → say so and stop: tier 0 is unmet.
2. **Already initialized?** Existing `.sdd/config.json` → check that it parses
   and required contract files/pointers exist, report gaps and direct to
   `/shipit:sync`; do not refresh, migrate, ask setup questions or write files.
   A partial `.sdd/` without config is not permission to overwrite its contents:
   inspect ownership and recover only missing first-setup outputs within the request.
3. **Ask tracking.** First `init` only — there is no recorded decision yet. Ask
   whether `.sdd/` should be committed (default — a team contract visible to CI,
   teammates, and any other agent) or stay local (nobody else sees it; each
   collaborator runs `init` themselves; a task's plan file won't travel as a
   PR diff either — `code-handoff` pastes it into the PR body instead). Write the
   answer to `sdd_tracking`. Local → check `git check-ignore -q .sdd` first, and
   append a `.sdd/` entry to `.git/info/exclude` only if nothing already covers
   it — never to `.gitignore`.
4. **Ask the output languages.** First `init` only, in the same breath as tracking.
   One question, four answers, each defaulting to `en`: plans and reports
   (`plan`), tickets and tracker comments (`task`), PR body and thread replies
   (`pr`), comments in code (`code`). A single answer fills `plan`, `task` and
   `pr`; `code` stays `en` unless named. Accept a tag (`es`, `pt-BR`) or a plain
   name; store the tag. Identifiers, commit subjects, branch names and `.sdd/`
   itself stay English. See `references/config-schema.md § Scope of language`.
5. **Detect.** When Graphify CLI and an existing graph are present, query relevant
   architecture/convention concepts first and verify candidates in source; never
   treat stale graph output as proof. Missing graph → source discovery. Work through `references/detection-recipes.md` in order. It owns every recipe; do not improvise a detection this file does not describe.
6. **Verify commands.** Run each candidate command. Green → write it. Red or absent → `null` plus `unknown[]`. Record the result in `commands_verified`.
7. **Derive layers.** From real directories, with one exemplar each. No fixed list of layer names.
8. **Derive test rules.** One real test per kind, reduced to its shape.
9. **Detect tracker and companions.** Adapter per `references/detection-recipes.md
   § 7` — asked only when detection is undecided — then the create target per § 7b,
   asked only when the tracker is reachable and offers more than one target, then
   the priority and size fields per § 7c, which never ask. Both questions are
   conditional; a repo with an obvious tracker is asked neither. Then companion
   tier status. No installs.
10. **Write.** `config.json` from `assets/config-template.json`; the markdown files from their templates in `assets/`.
11. **Point at it.** Write the pointer block per *Discovery pointer* above, then link or append `CLAUDE.md`.
    Append `<paths.tasks>` to `.git/info/exclude` if nothing already covers it —
    check with `git check-ignore -q` first, in both tracking modes.
12. **Self-check and baseline.** Every factual claim in `.md` has evidence. Every non-null command has a `commands_verified` entry. `unknown[]` matches what was actually left undetermined. The pointer exists exactly once per file. Fix before reporting, then record the initial baseline below.

## Initial baseline

After self-check, use `../sync/scripts/context_state.py` to record the exact files
just generated. Follow `../sync/references/reconciliation.md § Baseline contract`.
Create a temporary JSON inventory outside the repo: `managed` lists config, stack,
conventions and each generated layer/test rule (respect `paths.rules`), and
`unresolved` is `[]`. Run:

```sh
python3 <plugin>/skills/sync/scripts/context_state.py --repo <repo> record --inventory <inventory.json>
```

The resulting `.sdd/sync-state.json` follows `sdd_tracking`. It stores accepted
bases and source hashes so sync can recognize human edits; a date is not an edit
detector. Python 3.10+ is required for this helper. If unavailable, report initial
baseline pending; never claim the context can be synchronized without that gap.
Unknown detected capabilities may remain in `unknown[]`; unresolved ownership or
contradictory decisions must not be passed off as a completed baseline.

## Existing projects

`init` initializes once. Maintenance belongs to `/shipit:sync`, including config
migrations, command revalidation, documentation reconciliation and pointer repair.
Legacy `init --upgrade` requests receive the replacement `/shipit:sync --upgrade`
and stop without writing. `--language` / `--tracker` on an initialized repo are
redirected to the same flags on sync; never rerun first-setup defaults.

## Flags

- `--language <tag>` — set `plan`, `task` and `pr` without asking; `code` untouched.
  `--language plan=es,pr=en,code=en` sets only the keys named. For CI and re-runs.
- `--upgrade` — retired here; use `/shipit:sync --upgrade` for config-only migration
  or `/shipit:sync` for migration plus context reconciliation.
- `--tracker <adapter>` — set `tracker.adapter` without detecting or asking:
  `linear`, `github-issues`, `jira`, `shortcut`, or `none`. For CI, and for
  correcting a detection in one command instead of hand-editing `config.json`. An
  unrecognised value is rejected, not coerced — `init` never invents an adapter.
- `--with-companions` — print the exact install commands, state what each one
  grants (ponytail ships session hooks; `uv tool install` downloads from PyPI),
  ask once, then run `scripts/companions.sh --yes`. Never builds a graph.
- `--with-graph` — the above, plus build the graph once. Disclose the cost
  (minutes + extraction tokens) and ask separately. This is the only shipit
  action that spends tokens on setup.

## Report

- Paths written, including whether `AGENTS.md` was created or appended, and whether
  `CLAUDE.md` is a symlink or a copy.
- Tracking: committed or local, and whether `.git/info/exclude` was touched.
- Stack detected, one line.
- Output language per key, and whether it came from the question or `--language`.
- Commands verified, with the exit code each returned.
- **`unknown[]`, listed loudly.** Silence here is what poisons every later plan.
- Layers found, with their exemplars.
- Tracker adapter, and where it came from: detected (with the evidence), asked
  (with what was ambiguous), or `--tracker`. A `none` that came from an unresolved
  ambiguity is reported as undetermined and appears in `unknown[]` — never as
  "this repo has no tracker".
- The target new issues belong in: the mechanism's state and the team or project
  it names. `create.supported: false` → say what is missing, in one line. With
  `issue_create` withheld, the target is what the draft is pasted into.
- Where `Priority` and `Size` will land: the field names, or `none` with the reason
  — no Project, a points-only estimate, a missing `project` scope with
  `gh auth refresh -s project` as the fix. Option values that will not map are
  named here, not discovered at create time.
- **`handoff.allow`, and the one line that it can be widened.** Written as
  `["branch", "commit", "push", "pr_body", "pr_ready", "tracker_status"]`:
  `code-handoff` delivers a ready PR and advances its card to `In Review`.
  `tracker_comment`, `thread_replies` and `issue_create` are added by hand — see
  `references/config-schema.md § handoff.allow`.
- Companion tiers, in `doctor`'s format.
- Any place an agent doc contradicted the repo.
- Next step: `/shipit:task-create` for a need with no ticket yet, `/shipit:code-plan` for one
  that has. UI layers found and no `.sdd/design-system.md` → also
  `/shipit:design-system`, once.

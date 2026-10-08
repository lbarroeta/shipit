# shipit 🐿️

Spec-driven development for any repo. It detects your conventions instead of assuming
them.

Most planning agents carry someone else's stack in their prompt. shipit carries none:
`/shipit:init` reads your repository once and writes a contract at `.sdd/`, and every
other skill works from that. Nothing in this plugin knows what framework you use.

## Install

### Claude Code

```
/plugin marketplace add KodimTech/shipit
/plugin install shipit@shipit
```

### Codex

```
codex plugin marketplace add KodimTech/shipit
codex plugin add shipit@shipit
```

Start a new session and the ten skills are available. Codex matches them by
description, and the same names work as slash commands — `/shipit:task`,
`/shipit:plan`, `/shipit:init`, `/shipit:design-system`, `/shipit:implement`, `/shipit:handoff`,
`/shipit:pr-fix`, `/shipit:status`, `/shipit:doctor`, `/shipit:run` — exactly as in Claude Code. Same `skills/`
directory and the same `.sdd/` contract, so a repo initialized in one runtime
works in the others.

Uninstall with `codex plugin remove shipit@shipit`. Updating is below.

### OpenCode

The skills are plain markdown, so OpenCode runs them as custom commands:

```sh
ROOT=~/.config/opencode/plugins/shipit
[ -e "$ROOT" ] || git clone https://github.com/KodimTech/shipit "$ROOT"
"$ROOT"/scripts/install-opencode.sh
```

The installer links the nine commands and verifies OpenCode resolves them. It
never uses sudo, never installs a package, and never edits `opencode.json`. The
same three lines are also the update — see below.

One skill, `run`, requires native Claude Code or local Codex subagent
controls and is not exposed as an OpenCode command.

Already have a checkout somewhere else? Skip the clone and run its
`scripts/install-opencode.sh` directly — the installer uses whatever checkout it
lives in.

Commands are flat here: `/shipit-plan`, not `/shipit:plan`. Same skills, same
`.sdd/` contract, so a repo initialized in one runtime works in the others.

Installing somewhere other than the default? Set `SHIPIT_ROOT` before running,
and keep it exported — the commands read it to find the skills. Uninstall:
`rm ~/.config/opencode/commands/shipit-*.md`.

### Then, once per repository

```
/shipit:init
```

## Update

One command per runtime: every runtime reads the same `skills/` directory, and a
`.sdd/` contract written by an older version keeps working. Then one command per
repo to adopt what the new version adds — see *Then, once per repository* below.
This release adds `/shipit:design-system` in every runtime.

### Claude Code

```
/plugin marketplace update shipit
/plugin update shipit@shipit
```

The first refreshes the marketplace from GitHub; the second installs what it
found. Restart the session to load it.

### Codex

```
codex plugin marketplace upgrade shipit
```

That refreshes the Git snapshot Codex installs from. If `codex plugin list` still
reports the old version, install the refreshed one:

```
codex plugin add shipit@shipit
```

Either way, start a new session — skills are read at startup.

### OpenCode

```sh
ROOT=~/.config/opencode/plugins/shipit
[ -e "$ROOT" ] || git clone https://github.com/KodimTech/shipit "$ROOT"
"$ROOT"/scripts/install-opencode.sh
```

The same three lines as the install: the guard skips the clone, the installer
pulls, and every command is re-linked — including the ones added since you last
ran it. Export `SHIPIT_ROOT` first if your checkout is not in the default place.

### Did it land?

The new command has to resolve. `/shipit:design-system` in Claude Code and Codex,
`/shipit-design-system` in OpenCode, where `opencode debug config` lists all nine.

### Then, once per repository

```
/shipit:init --upgrade
```

Brings `.sdd/config.json` up to the installed version: adds new keys, converts old
shapes, and asks only the decisions the new version introduced — nothing else is
re-detected or re-asked. Already current → it says so and stops.

Repos with a UI then run `/shipit:design-system` once — see
[*Adding it to a project already running shipit*](#adding-it-to-a-project-already-running-shipit).

## The cycle

For an existing issue/card, Claude Code and local Codex can run the whole cycle:

```
/shipit:run ENG-412
/shipit:run https://linear.app/team/issue/ENG-412/...
```

`run` fetches the task through your configured tracker, checks its acceptance
criteria, switches to `main`, fetches its remote and merges the upstream SHA with
`--ff-only --no-overwrite-ignore`, then creates the task branch. This protected
equivalent of `git pull --ff-only` also preserves ignored local files. Three real,
sequential subagents then plan, implement/validate and deliver
under `handoff.allow`. The coordinator waits for each result; missing models,
blocked criteria or failed validation stop the pipeline. Pending user changes are
never stashed or discarded. Your repo must already have `.sdd/` configured, Python
3.10+, a clean checkout and `main` tracking a remote `main`.

At the start of `plan`, the issue moves to `In Progress` or the tracker's equivalent
and is read back to verify success. This applies to standalone `/shipit:plan` and
the planner inside `run`, independently of `handoff.allow`. A missing status
mapping or tracker write access blocks planning. Plans without an issue, or with
adapter `none`, stay local. Issues already in progress, review or a terminal state
are never moved backwards; `run` resumes at later stages do not repeat the transition.

| Stage | Claude Code | Codex |
| --- | --- | --- |
| Plan | Opus 5.5 / high | Sol 6.1 / high |
| Implement | Sonnet 5.5 / high | Luna 6 / xhigh |
| Handoff | Sonnet 5.5 / high | Luna 6 / xhigh |

These are pinned IDs, not moving aliases. Optional per-repo overrides live under
`run.models.<anthropic|openai>.<stage>` as complete `{model, effort}` pairs;
Claude overrides also need a matching native agent definition. Old `.sdd/` configs
use the defaults without an upgrade. An observed runtime substitution blocks the
stage; unavailable effective-model metadata is disclosed rather than guessed.

The explicit request to run the issue authorizes execution within its criteria,
after the coordinator checks the generated plan. Scope/security/data blockers
still go to the user. `implement --defer-handoff` lets the builder return control
before the separate delivery agent runs; standalone `implement` is unchanged.

State and issue/checkout locks live under the Git common directory, outside the
diff. Repeating an issue resumes its saved branch and checkpoints without pulling
main again or duplicating delivery. Give QA feedback in the same chat: failures
return to the builder on that branch. Ready for QA includes where to test, setup
and complete plain-language steps. Missing test environment is reported as QA
blocked; a PR or green tests never means human QA passed. This first pipeline uses
one existing checkout; use individual `plan --worktree` for independent worktrees.

The individual cycle remains available:

```
/shipit:init        read the repo, write .sdd/          once per repo
        │
/shipit:design-system  interview → design contract       once per repo with UI; re-run to update
        │
/shipit:task        a need becomes a ticket, or an epic  when there is no ticket yet
        │
/shipit:plan        plan contract in the current checkout once per task
        │
/shipit:implement   red/green + validation scoped to the change
        │
/shipit:handoff     branch, commit, push, PR body           delivery side effects
                    tracker + threads only if allowed
        │
/shipit:pr-fix      review comments + red CI             as needed
                    `--comments` / `--ci` to scope
```

Plus two for visibility:

```
/shipit:doctor      do I have everything, and what does each gap cost
/shipit:status      every in-flight worktree, its PR, its tracker state
```

To try a PR checkout in Claude Code, start a fresh session with
`claude --plugin-dir /absolute/path/to/shipit`, then invoke `/shipit:run <ID-or-URL>`
in the initialized target repo. For Codex, add the checkout as a local marketplace
with `codex plugin marketplace add /absolute/path/to/shipit`, install its shipit
entry, then start a new session in the target repo. See the CLI's marketplace
output for the resolved name; an installed plugin snapshot must be refreshed to
pick up changes. No real tracker/model execution is implied by the offline checks
below.

Development validation: `python3 -m unittest discover -s tests -v` exercises Git
preparation, locks, resume, model/validation gates and human QA checkpoints against
disposable local repositories. `claude plugin validate .claude-plugin/plugin.json`
checks the Claude package. See `evals/` for behavioral scenarios.

## From a need to a ticket

`/shipit:task` is the entry of the cycle, for when the work exists as a sentence in
Slack and nowhere else. It drafts the ticket against your repo — grounded in real
paths, not invented ones — shows it to you, and creates it only after you say yes.

```
/shipit:task "sessions should expire after 30 idle minutes"
```

One need, one ticket. A need that spans two layers or two shippable outcomes becomes
an **epic with subtasks** instead — each one mergeable, verifiable, and worth landing
on its own, capped at seven. `--epic` and `--single` override the call; `--dry-run`
stops at the draft; `--plan` runs `/shipit:plan` on it. By default every run stops
at the draft and creating the issue is your move — add `issue_create` to
`handoff.allow` to have `handoff` create it after you confirm.

Every ticket is typed **Bug**, **Feature** or **Chore** on the line under the title
— what triage filters on first — and mapped to whatever your tracker calls that: a
Shortcut story type, a Jira issue type, a Linear or GitHub label that already exists.
The same line sets **Priority** (`P0`–`P3`, `P2` by default) and **Size**
(`XS`–`XL`, sized on scope and uncertainty, never hours; only an epic parent is
`XL`). `--priority` and `--size` set them outright. On creation they land in the
tracker's own fields — Linear priority and T-shirt estimate, the `Priority` and
`Size` fields of a GitHub Project, Jira's priority — and anything without a matching
field is reported as unmapped rather than invented. `init` detects those fields once
and records them in `tracker.create.fields`, so `doctor` can say up front that, for
example, size will not land on a points-only Linear team; a field under another name
(`Prioridad`) is set there by hand.

Every task also says **what to do**: two to six bullets, each one concrete change
in behaviour naming the area it lands in, so whoever picks it up knows what has to
change without the ticket turning into a file list. Subtasks carry it in one
sentence per row.
Anything a person can see also carries **QA steps**: five at most, plain language, no
terminal commands, so a non-developer can confirm the ticket is done. Work with no
visible surface gets no such section.

Four things keep it from filling your backlog with noise:

- **A ticket says what and why, never how.** No file list, no commands, no code —
  that is `plan`'s output, and writing it here fossilises a guess someone will
  follow.
- **Short is enforced, not encouraged.** 26 lines for a task, one table row per
  subtask, one sentence for the outcome. A sentence that would not change what
  someone does gets cut.
- **Blocking ambiguity stops the draft.** Scope, security, or data left open means
  the question goes to you, not into the backlog for the next person to re-open.
- **The draft is confirmed before it is created**, every time. There is no flag that
  skips it.

The draft lands at `.sdd/tasks/<slug>.md` and is excluded from git in both tracking
modes — once the issue exists, the tracker is the source of truth, and a stale copy
in the repo is worse than none. Re-running the delivery on a draft that already
carries ids creates nothing: the `Created` block is the idempotency ledger, which is
what makes a half-finished epic safe to retry.

### Trackers

| Adapter | Reached through | An epic is | Bug/Feature/Chore maps to | Priority / Size map to |
| --- | --- | --- | --- | --- |
| `linear` | Linear MCP | a parent issue with sub-issues | an existing team label | priority / T-shirt estimate |
| `jira` | Jira MCP | the project's `Epic` type, enumerated first | the issue type | priority / a `Size` field if any |
| `shortcut` | Shortcut MCP | a native Epic | the story type, exactly | `Priority` / `Size` custom fields if any |
| `github-issues` | `gh` | a parent issue with a task list | an existing repo label | the Project's `Priority` / `Size` fields |
| `none` | — | — the draft is the deliverable | — | — |

`init` detects which one you use, and asks only when it genuinely cannot tell —
`ENG-412` is a valid Linear id *and* a valid Jira key, so a branch name alone never
decides between those two; a connected MCP does. A clean match asks nothing, and a
repo with no tracker at all is not a question either. `/shipit:init --tracker linear`
sets it outright, for CI or to correct a bad detection without hand-editing JSON.

An ambiguity nobody resolves is recorded as `none` **and** listed in `unknown[]`, so
it reads as undetermined rather than absent — the distinction that decides whether
`/shipit:task` failing to create anything is expected or a misdetection.

With the adapter settled and its MCP connected, `init` also picks up which team or
project new issues belong to, asking only when there is more than one. Unreachable
tracker → `create.supported` goes `false`, `task` still writes the draft, and
`doctor` says what is missing. States, labels, transitions and
issue types are always enumerated from your workspace and matched by name; an id
copied from someone else's workspace writes to the wrong place, silently.

`task`, `plan`, `implement`, and `pr-fix` never run `git commit`, `git push`, or a
PR command. Only `handoff` does — and what `handoff` may do is a config list, not a
judgement call:

```json
"handoff": { "allow": ["branch", "commit", "push", "pr_body", "pr_ready", "tracker_status"] }
```

That is the default `/shipit:init` writes. `handoff` creates a ready-for-review
PR, converts an existing draft when needed, and moves the linked card to
`In Review` after verifying PR readiness. It verifies the card update and preserves
review/QA/terminal states. No card or adapter `none` → the tracker step is `n/a`.
Tracker comments, review-thread replies and issue creation remain opt-in: add
`tracker_comment`, `thread_replies` or `issue_create` per repo. Existing explicit
allow-lists are preserved on init refresh/upgrade. A capability that is not listed is not performed, and the run says
`skipped (not in handoff.allow)` rather than doing it anyway.
The `plan` startup transition to `In Progress` is separate and applies whenever
planning an existing issue with a configured tracker, including inside `run`.

The tracker reference is read only for enabled capabilities: status rules by
default, and comment/creation sections only when opted in.

## The `.sdd/` contract

`init` writes five kinds of file, and every claim in them carries evidence — a
`path:line`, or the exact command output that proved it.

| File | For | Content |
| --- | --- | --- |
| `.sdd/config.json` | machines | Verified commands, paths, layers, tracker, worktree |
| `.sdd/stack.md` | agents | Stack facts, one row per fact, each with evidence |
| `.sdd/conventions.md` | agents | Patterns this repo follows, each with an exemplar |
| `.sdd/rules/<layer>.md` | agents | Layer rules derived from real files |
| `.sdd/rules/tests/<kind>.md` | agents | Test shape, extracted from a real test |

Plus `.sdd/tasks/`, where `/shipit:task` writes ticket drafts. It is scratch, not
contract: excluded from git in both tracking modes.
Generated plans also stay local: `handoff` excludes them from commits in every
tracking mode, including inside `run`. Planning handoff carries the plan in a PR
body when a PR exists or the branch has commits ahead of its base; otherwise the
local plan is the deliverable, with no empty commit to create a PR.

And, once `/shipit:design-system` has run, `.sdd/design-system.md` and
`.sdd/rules/design.md` — see *A design contract for UI* below. `init` never
rewrites them, and a refresh carries their `<!-- shipit:design -->` blocks over
untouched.

`init` asks once, per repo, how it should be tracked:

| Choice | Means |
| --- | --- |
| Commit (default) | A team contract — visible to CI, teammates, and any other agent |
| Gitignore | Local only — each collaborator runs `init` for their own; worktrees get it via a symlink back to the main checkout |

Three rules make it trustworthy:

- **No evidence, no claim.** Without an exemplar, the value is `unknown` — and `plan`
  asks instead of guessing.
- **Commands come from CI, and are run before being written.** A command that only
  appears in a README is a candidate to verify, never a source. One that fails
  verification is `null`, and its key is reported in `unknown[]`.
- **It complements your agent docs, never duplicates them.** `CLAUDE.md`, `AGENTS.md`,
  `.cursor/rules` are referenced; `.sdd/` records only what they do not state. When a
  doc and the repo disagree, the repo wins and the discrepancy is reported.

`init` is the single point of failure by design: a bad detection poisons every later
plan. That is why the evidence rules are hard rules and why `unknown[]` is printed
loudly rather than buried in JSON.

### Output language

`init` asks once which language shipit should write in, one per action, and records
them under `language` in `.sdd/config.json` (`en` by default):

```json
"language": { "plan": "es", "task": "es", "pr": "en", "code": "en" }
```

`plan` covers the plan, implementation report, QA guide and what skills print;
`task` covers tickets and tracker comments; `pr` the PR body and thread replies;
`code` comments written in code. Identifiers, commit subjects, branch names and
`.sdd/` itself always stay English, so the repo stays greppable for everyone. An
old `"language": "es"` still works: it sets `plan`, `task` and `pr`, and `code`
stays `en`. Change it by editing the keys, or
`/shipit:init --language plan=es,pr=en,code=en`.

### The pointer that makes it read

No agent auto-loads a directory — not `.sdd/`, not any other name. `AGENTS.md` and
`CLAUDE.md` are the files that do get loaded, so `init` writes a short pointer into
them, between `<!-- shipit:contract -->` markers:

```md
<!-- shipit:contract -->
## Repo contract (shipit)
- `.sdd/stack.md` — stack facts, each with evidence
- ...
<!-- /shipit:contract -->
```

`AGENTS.md` missing is created; present is appended once. `CLAUDE.md` missing becomes
a symlink to `AGENTS.md`, so the two never drift. Refresh replaces the block in place
— everything outside the markers is yours and is never touched.

That is what makes the contract portable across runtimes. Claude Code, Codex,
OpenCode, Cursor and anything else reading `AGENTS.md` find `.sdd/` the same way,
without shipit installed.

## A design contract for UI

Agents building UI with no design contract invent one per screen: a new blue, a
third button, a table with no empty state. `/shipit:design-system` records one,
from your answers and from what the repo already does.

```
/shipit:design-system
```

It is an **interview**, not a form the agent fills in for you. Short rounds of one
to three questions, in plain language, in the order that decisions depend on each
other: what kind of application it is (admin panel, customer portal, store,
public site — or several), who uses it and how often, what they do most, on which
devices, what identity must be kept, how it should look and how dense it should
be, and light or dark. An admin panel gets follow-ups on data volume, filters,
bulk actions and permissions; a portal on what customers must see at a glance.
You are never asked for a hex code or a border radius — the agent proposes those,
with the reason, and shows a standalone preview when the runtime can render one.
"No sé" gets help choosing; "decide tú" is recorded as a delegation with its scope.
Nothing counts as approved until you confirm it — stop halfway and you get a
clearly marked draft, or nothing.

It writes two files and two pointers:

| Path | Content |
| --- | --- |
| `.sdd/design-system.md` | Product and surfaces, color roles, typography, spacing, radii, themes, responsive, the catalog of components that **exist** (path, parameters, variants, a valid example), screen patterns, and a ledger of decisions — each labelled `existing`, `user`, `delegated` or `proposed` |
| `.sdd/rules/design.md` | How agents pick patterns and components, when to reuse or create, token use without invented values, loading/empty/error/success/disabled, forms, keyboard and focus, responsive, and the checks that verify a change |
| `<!-- shipit:design -->` | Appended to each UI layer's rule file, and to `AGENTS.md` next to the contract pointer |

Existing UI is the starting point: its identity is kept unless you choose
otherwise, and inconsistencies are listed with their split, never turned into
rules. Values already in your CSS or theme stay there — the contract points at
them. It changes no product code; implementing what it marks `to implement` is a
normal `/shipit:task` or `/shipit:plan`.

`plan` reads the design rules only when the task touches UI and records the
pattern, components and states in a `Design` section; `implement` follows them and
reports each verification check. Backend-only work never loads them. Re-running it
updates the same files: approved decisions and your hand edits are kept, and only
pending or contradicted ones are asked again.

### Adding it to a project already running shipit

Nothing in an initialized repo has to be redone. The design contract sits next to
the one `init` wrote; it does not replace it.

1. **Update the plugin** in your runtime — see [*Update*](#update) — and start a
   new session. `/shipit:design-system` (or `/shipit-design-system` in OpenCode)
   has to resolve.
2. **Bring the config to 0.11.0:**

   ```
   /shipit:init --upgrade
   ```

   This release does not change the config's shape, so it only records the new
   version and asks nothing. Never ran `init` in this repo? Run `/shipit:init`
   instead — the design contract needs the layers and the `AGENTS.md` pointer it
   writes.
3. **Run the interview** on a clean working tree, so its diff is easy to review:

   ```
   /shipit:design-system
   ```

   Plan ten to fifteen minutes. Ask whoever knows the users and the brand to
   answer it; "decide tú" is fine for anything they do not care about. Existing
   UI is inspected first, so most questions arrive with a suggested answer taken
   from your code. Stop halfway and you get a draft, never an approved contract.
4. **Review and commit** what it wrote — it never commits:
   - `.sdd/design-system.md` and `.sdd/rules/design.md`, new.
   - A `<!-- shipit:design -->` block at the end of each UI layer's rule file.
   - The same block in `AGENTS.md` (and `CLAUDE.md` when it is a real file).

   With `sdd_tracking: local` they stay in your checkout like the rest of `.sdd/`.
5. **Plans already in flight keep working.** A plan written before the contract
   has no `Design` section; `implement` applies the design rules directly and
   says so under *Known Risks or Follow-ups*. Re-run `/shipit:plan` on it if you
   want the components and states recorded up front.
6. **Implement what is marked `to implement`** — new tokens, a missing focus
   style, a component the contract proposes — as ordinary work:

   ```
   /shipit:task "Apply the design tokens from .sdd/design-system.md"
   ```

   then `/shipit:plan` and `/shipit:implement` as usual. Nothing changes in the
   product until that work ships.

Later, re-run `/shipit:design-system` whenever identity changes or pending
decisions are settled; it updates the same files. `/shipit:init` refreshes keep
the design files and blocks untouched. One edge case: a repo whose `init`
created a layer keyed `design` already has its rule at `.sdd/rules/design.md` —
`design-system` stops and reports it; rename that layer rule to
`design-layer.md` (and its `rule` entry in `config.json`) before running it.

## Parallel worktrees — opt-in

**Off by default.** `plan` writes into your current checkout, like every other tool.
A fresh worktree does not inherit untracked local config — `.env`, credentials,
build caches — so enabling it before you know what your repo needs to boot from a
clean checkout buys friction, not parallelism.

Turn it on in `.sdd/config.json` when you actually want several tasks in flight:

```json
"worktree": { "enabled": true, "setup": "<the command that makes a clean checkout runnable>" }
```

Per-invocation override, no config edit needed — a flag in the request wins either
way: `/shipit:plan --worktree <request>` forces one, `--no-worktree` forces none.

Then `/shipit:plan` creates a worktree per task at `../worktrees/<repo>/<slug>` and
writes the plan inside it. Three things make that safe:

- **Collision detection.** Before finalizing its file list, `plan` reads the `Files`
  table of every active worktree's plan and intersects paths. Overlap is reported with
  the worktree that claims it, and the decision — sequence, narrow, or proceed — is
  recorded in the plan.
- **Shared graph.** Graph output is usually excluded via `.git/info/exclude`, so a fresh worktree has none.
  It is symlinked read-only from the main checkout. Graph updates happen only in the
  main checkout, after the merge.
- **No secrets by default.** `worktree.link[]` starts empty. Filling it symlinks
  untracked files — usually `.env` files and keys — into a directory outside the repo
  that no `.gitignore` covers. Opt in deliberately, or let `worktree.setup` regenerate
  what the worktree needs.

`/shipit:status` shows the board. `--prune` removes worktrees whose PR is merged,
never one that is dirty or still open.

## Dependency tiers

Run `/shipit:doctor` for your machine's actual state.

| Tier | What | Without it |
| --- | --- | --- |
| **0 — required** | `git` | shipit does not run. That is the whole tier. |
| **1 — recommended** | `gh` authenticated; a tracker MCP if you use one | `handoff` cannot push or open a PR; without a tracker MCP it falls back on your branch convention. `task` still drafts, `plan` and `implement` are unaffected. |
| **2 — accelerators** | graphify CLI + graph; caveman | Discovery falls back to `rg`. Same answers, more tokens. |
| **3 — do not enable during a cycle** | the ponytail plugin | Nothing. The useful part is already vendored here. |

Nothing is installed for you. `doctor --fix` offers the two safe installs after one
confirmation, and never builds a graph — that costs tokens, so it stays your call.

## On ponytail

shipit vendors the useful part of [ponytail](https://github.com/DietrichGebert/ponytail)
(MIT) into `references/lean-ladder.md`: the laziness ladder, the five review tags, and
the debt-marker convention. `plan` runs the ladder as a scope gate, `implement` uses it
as a coding stance, `pr-fix` uses its tags to justify pushback.

**Do not run the ponytail plugin during an SDD cycle.** Three reasons, from its own
documentation:

1. It is a persistent mode kept alive by session hooks. shipit skills are one-shot
   workflows with their own rules — two authorities, one decision.
2. "YAGNI applies to tests too" — one `assert`, no frameworks. In a repo with a real
   suite and a coverage gate, that leaves CI red.
3. "At most three short lines" of output, against a report that must carry
   non-developer QA steps, a file manifest, and validation results.

`lean-ladder.md` overrides both of those rules explicitly. Install the plugin
separately if you want `/ponytail-audit` or `/ponytail-debt`; the debt marker prefix
stays `ponytail:` by default so its ledger still finds shipit's markers.

## Token cost

Reducing token spend is an explicit goal, not a side effect. Four levers, largest
first:

| Lever | Attacks |
| --- | --- |
| `.sdd/config.json` | Re-detecting the stack on every run. Paid once by `init`. |
| Context budget | Wide reads. Rule files load only for layers actually touched. |
| graphify | Grep dumps and whole-file reads, replaced by a scoped subgraph. |
| caveman | Prose. Non-developer QA steps stay exempt from compression; everything else, PR bodies included, is short by default. |

Plans are capped by **uncertainty**, not task size: ≤40 lines when the change follows
an analogue, ≤150 as a hard cap for novel architecture. Over budget means the plan is
restating the repo, so it gets cut rather than the cap raised.

### Measured footprint

From `claude plugin details`, against the four hand-written skills shipit was
extracted from:

| Skill | always-on | on-invoke | vs. original |
| --- | --- | --- | --- |
| `plan` | ~110 | ~1.8k | −28% on invoke (was ~2.5k) |
| `implement` | ~90 | ~2.6k | −16% on invoke (was ~3.1k) |
| `pr-fix` | ~90 | ~1.9k | +6% |
| `handoff` | ~90 | ~1.5k | −21% |
| `init` | ~90 | ~1.7k | new |
| `doctor` | ~90 | ~1.4k | new |
| `status` | ~70 | ~1.2k | new |
| `task` | not yet measured | not yet measured | new |
| `design-system` | not yet measured | not yet measured | new; the interview is multi-turn by design |
| `run` | not yet measured | not yet measured | new; native subagent work is additional |

The four equivalent skills cost **~380 always-on against the originals' ~442**, and
the two heaviest got materially cheaper per invocation — the contract removed the
stack re-discovery that used to live in their bodies.

Total always-on was **~629 vs ~442** at seven skills, because there were three more
of them. That is the honest trade: +187 tokens per session bought `init`, `doctor`,
and `status`. `task` is the eighth and has not been measured yet — expect its
always-on description to cost about the same as the others, roughly +90. `run` is
the ninth and `design-system` the tenth; neither has been measured. If that is
not worth it for your setup, disable the plugin per-project rather than working around
it.

Neither number captures the actual saving, which is runtime input: file reads avoided
by the context budget, stack detection paid once instead of per plan, and grep dumps
replaced by a scoped subgraph. Measure that with
`claude plugin eval shipit`, which runs a no-plugin baseline arm for comparison.

## Migrating from the original skills

| Was | Now |
| --- | --- |
| `sdd-planner` | `/shipit:plan` |
| `sdd-implementation` | `/shipit:implement` |
| `sdd-pr-fix` | `/shipit:pr-fix` |
| `sdd-handoff` | `/shipit:handoff` |
| — | `/shipit:init`, `/shipit:design-system`, `/shipit:task`, `/shipit:doctor`, `/shipit:status` |
| Conventions hardcoded in the skill | `.sdd/`, generated from your repo |
| `.claude/plans/` | `<paths.plans>`, default `.sdd/plans/` |

## License

MIT. See `LICENSE`, and `NOTICE` for the ponytail attribution.

# shipit 🐿️

Spec-driven development for any repo. It detects your conventions instead of assuming
them.

Most planning agents carry someone else's stack in their prompt. shipit carries none:
`/shipit:init` reads your repository and writes a contract at `.shipit/`, and every
other skill works from that. Nothing in this plugin knows what framework you use.

## What shipit does

shipit is a set of skills for Claude Code, Codex and OpenCode that takes a piece of
work from a need to a reviewed pull request, with the agent following *your*
repository's rules at every step:

1. **Learns the repo once.** `init` reads the code, CI and docs, and records the
   stack, the commands that actually work, the layers and the test patterns in
   `.shipit/` — each fact with its evidence.
2. **Turns a need into a ticket.** `task-create` drafts a ticket with acceptance
   criteria and QA scenarios, grounded in real paths, and publishes it to your
   tracker only when you allow it.
3. **Plans before coding.** `code-plan` writes which files change, how each
   acceptance criterion is proved, and what is still undecided. A missing fact
   becomes a question, not a guess.
4. **Implements and validates.** `code-implement` follows the plan, runs the repo's
   own test, lint and build commands, and writes QA steps a non-developer can follow.
5. **Delivers.** `code-handoff` creates the branch, commit, push and a
   ready-for-review PR, and moves the card to review — only the actions listed in
   `handoff.allow`.
6. **Keeps context current.** `sync` updates the contract and docs as the code
   changes, without overwriting human decisions.

For an existing ticket, `/shipit:run ENG-412` chains steps 3–6, with a sync before
and after, in Claude Code and Codex.

What it never does: commit, push or open a PR outside `code-handoff`; write a
command it could not run; invent business rules to fill a gap; install anything
without your yes.

### Commands

| Command | What it does | When |
| --- | --- | --- |
| `/shipit:init` | Reads the repo and writes the `.shipit/` contract | Once per repo; safe to re-run |
| `/shipit:doctor` | Checks git, `gh`, tracker and accelerators; prints each fix and its cost | Before the first run, or when something is missing |
| `/shipit:sync` | Reconciles the contract and docs with the code; `--upgrade` migrates config | Before planning, after implementing, after updating shipit |
| `/shipit:product-discovery` | Interviews you and writes the PRD | Once per product |
| `/shipit:product-mvp-cut` | Decides which PRD stories ship first | After the PRD |
| `/shipit:design-system` | Interviews you and records colors, components and UI rules | Once per repo with a UI |
| `/shipit:task-create` | Turns a need into a ticket, or an epic with children | No ticket exists yet |
| `/shipit:task-next` | Recommends the next ticket to take, and why | Choosing what to work on |
| `/shipit:code-plan` | Writes the implementation plan for a ticket | Before coding |
| `/shipit:code-implement` | Executes the plan, runs the checks, prepares QA steps | After the plan |
| `/shipit:code-handoff` | Branch, commit, push, PR, tracker status | Work is ready for review |
| `/shipit:pr-fix` | Resolves review comments (`--comments`) or red CI (`--ci`) | The PR has feedback |
| `/shipit:run` | sync → plan → implement → sync → handoff for an existing ticket | You have a ticket and want it done |
| `/shipit:status` | Lists in-flight tasks with their PR and tracker state | Anytime; `--prune` removes merged worktrees |

In OpenCode the commands are `/shipit-<name>`, and `run` is not available.

## Quick start

1. Install the plugin for your runtime — see [Install](#install).
2. In your repository, on a clean checkout:

   ```
   /shipit:doctor      optional: what is missing, and what each gap costs
   /shipit:init        write the .shipit/ contract
   ```

   Review what `init` wrote and commit it: the contract is shared with your team.
3. Pick how you work:
   - **You have a ticket and want it done:** `/shipit:run ENG-412`.
   - **You want to drive each step:** `/shipit:code-plan ENG-412`, then
     `/shipit:code-implement`, `/shipit:sync` and `/shipit:code-handoff`.
   - **You only have an idea:** `/shipit:task-create "sessions should expire after
     30 idle minutes"` first.
4. Review comments or red CI on the PR → `/shipit:pr-fix`.

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

Uninstall with `codex plugin remove shipit@shipit`.

### OpenCode

The skills run as custom commands, named flat: `/shipit-code-plan`, not
`/shipit:code-plan`.

```sh
ROOT=~/.config/opencode/plugins/shipit
[ -e "$ROOT" ] || git clone https://github.com/KodimTech/shipit "$ROOT"
"$ROOT"/scripts/install-opencode.sh
```

The installer links the commands and verifies OpenCode resolves them. It never
uses sudo, never installs a package, and never edits `opencode.json`. Already have
a checkout elsewhere? Run its `scripts/install-opencode.sh` directly. Installing
somewhere other than the default? Export `SHIPIT_ROOT` and keep it exported — the
commands read it to find the skills. Uninstall:
`rm ~/.config/opencode/commands/shipit-*.md`.

Start a new session after installing. Every runtime reads the same `skills/` and
the same `.shipit/` contract, so a repo initialized in one works in the others.

## Update

| Runtime | Command |
| --- | --- |
| Claude Code | `/plugin marketplace update shipit`, then `/plugin update shipit@shipit` |
| Codex | `codex plugin marketplace upgrade shipit`; if `codex plugin list` still shows the old version, `codex plugin add shipit@shipit` |
| OpenCode | The same three install lines: the clone is skipped, the installer pulls and re-links every command |

Start a new session — skills are read at startup — then, once per repository:

```
/shipit:sync --upgrade
```

It brings `.shipit/config.json` up to the installed version and asks only the
decisions the new version introduced. A repo still on `.sdd/` (before 0.15.0) runs
`/shipit:init` instead. Notes for older versions are in
[Upgrading](docs/upgrading.md).

## Requirements

Only `git` is required. `/shipit:doctor` reports what your machine has, and nothing
is installed without your yes.

| Tier | What | Without it |
| --- | --- | --- |
| **0 — required** | `git` | shipit does not run. That is the whole tier. |
| **1 — recommended** | `gh` authenticated; a tracker MCP if you use one | `code-handoff` cannot push or open a PR; without a tracker MCP it falls back on your branch convention. `task-create` still drafts, `code-plan` and `code-implement` are unaffected. |
| **2 — accelerators** | graphify CLI + graph; caveman; Context7 | Discovery falls back to `rg`: same answers, more tokens. Without Context7, library and framework API claims the repo cannot show come from model memory, marked unverified, with one notice line in the report. |
| **3 — do not enable during a cycle** | the ponytail plugin | Nothing. The useful part is already vendored here. |

## Documentation

| Guide | Covers |
| --- | --- |
| [Workflow](docs/workflow.md) | `run`, the step-by-step cycle, tickets and trackers, what `code-handoff` may do, parallel worktrees |
| [The `.shipit/` contract](docs/contract.md) | What `init` writes, evidence rules, output language, the agent pointer, the code graph, product docs |
| [Design contract](docs/design-system.md) | The `design-system` interview, and adding it to a project already running shipit |
| [Upgrading](docs/upgrading.md) | Notes for older versions, the `.sdd/` migration, the original skills |
| [Development](docs/development.md) | Releases, trying a checkout locally, token cost, ponytail |

## License

MIT. See `LICENSE`, and `NOTICE` for the ponytail attribution.

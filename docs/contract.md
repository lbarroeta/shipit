# The `.shipit/` contract

`init` writes the contract and a synchronization baseline, and factual claims carry
evidence — a `path:line`, or the exact command output that proved it. Everything
lives in `.shipit/`; your own documentation in `docs/`, the README or agent docs is
linked from it, never copied into it.

| File | For | Content |
| --- | --- | --- |
| `.shipit/config.json` | machines | Verified commands, paths, layers, tracker, worktree |
| `.shipit/sync-state.json` | sync | Accepted generated bases, baseline commit and uncommitted-source hashes |
| `.shipit/stack.md` | agents | Stack facts, one row per fact, each with evidence |
| `.shipit/conventions.md` | agents | Patterns this repo follows, each with an exemplar |
| `.shipit/rules/<layer>.md` | agents | Layer rules derived from real files |
| `.shipit/rules/tests/<kind>.md` | agents | Test shape, extracted from a real test |

The config always lives at `.shipit/config.json`: it is how every skill finds the
rest. `paths.plans`, `paths.tasks` and `paths.rules` can move those three.

Plus `.shipit/tasks/`, where `/shipit:task-create` writes ticket drafts. It is scratch, not
contract: excluded from git through `.git/info/exclude`.
Generated plans also stay local: excluded the same way, and `code-handoff` keeps them
out of commits, including inside `run`. `/shipit:status --prune` deletes a plan once
its PR is merged or closed. Planning handoff carries a short proposal summary and the complete
plan in a collapsed PR-body block when a PR exists or the branch has commits ahead
of its base; otherwise the local plan is the deliverable, with no empty commit to
create a PR.

And, once `/shipit:design-system` has run, `.shipit/design-system.md` and
`.shipit/rules/design.md` — see [Design contract](design-system.md). `init` never
rewrites them, and sync carries their `<!-- shipit:design -->` blocks over
untouched.

The contract is committed: a team contract, visible to CI, teammates and any other
agent. Before 0.15.0 it lived in `.sdd/`, optionally local; `/shipit:init` migrates
that layout and removes it.

Three rules make it trustworthy:

- **No evidence, no claim.** Without an exemplar, the value is `unknown` — and `code-plan`
  asks instead of guessing.
- **Commands come from CI, and are run before being written.** A command that only
  appears in a README is a candidate to verify, never a source. One that fails
  verification is `null`, and its key is reported in `unknown[]`.
- **It complements your docs, never duplicates them.** Agent docs, the files they
  link to and the headings of `docs/**/*.md` are inventoried first. A topic they cover
  is linked from `.shipit/`; only what they do not state is written there. Your docs
  are never edited except by a patch you approve. When a doc and the repo disagree,
  `init` asks: on a fact the repo wins, on a decision you do.

`init` and `sync` own context accuracy: a bad detection poisons every later
plan. That is why the evidence rules are hard rules and why `unknown[]` is printed
loudly rather than buried in JSON.

## Output language

`init` asks once which language shipit should write in, one per action, and records
them under `language` in `.shipit/config.json` (`en` by default):

```json
"language": { "plan": "es", "task": "es", "pr": "en", "code": "en" }
```

`plan` covers the plan, implementation report, QA guide and what skills print;
`task` covers tickets and tracker comments; `pr` the PR body and thread replies;
`code` comments written in code. Identifiers, commit subjects, branch names, the
config and what shipit generates always stay English, so the repo stays greppable
for everyone. An old `"language": "es"` still works: it sets `plan`, `task` and `pr`, and `code`
stays `en`. Change it by editing the keys, or
`/shipit:sync --language plan=es,pr=en,code=en`.

## The pointer that makes it read

No agent auto-loads a directory. `AGENTS.md`, `CLAUDE.md` and `CLAUDE.local.md` are
the files that do get loaded, so `init` writes a short pointer between
`<!-- shipit:contract -->` markers:

```md
<!-- shipit:contract -->
## Repository contract

[Shipit configuration](.shipit/config.json) defines verified commands, layers and
tracker. Read [stack](.shipit/stack.md), [conventions](.shipit/conventions.md) and
the applicable [layer rule](.shipit/rules/) before writing code. ...
<!-- /shipit:contract -->
```

Where it goes depends on what the repo already has. A team's agent doc is never
edited to add one:

| Repo | Pointer |
| --- | --- |
| No `AGENTS.md`, no `CLAUDE.md` | A new short `AGENTS.md` index holding the block; `CLAUDE.md` becomes a symlink to it |
| A file that already carries the block | Replaced in place |
| `AGENTS.md` and/or `CLAUDE.md` exist | `CLAUDE.local.md`, excluded from git — importing `@AGENTS.md` when there is no `CLAUDE.md` |

`docs.pointer` in the config records the choice, so sync, doctor and design-system
find the block, and each collaborator's `init` recreates a local pointer. Sync
replaces the block in place — everything outside the markers is yours.

That is what makes the contract portable across runtimes: Claude Code, Codex,
OpenCode, Cursor and anything else reading `AGENTS.md` find the contract without
shipit installed. One gap: Codex reads no local file, so a `CLAUDE.local.md` pointer
reaches Claude Code only. Shipit's own skills read `.shipit/config.json` by path
either way.

## The code graph

`init` checks for the graphify CLI on every run. Missing → it explains what
graphify is, the exact install command and what it touches, and installs only on
your yes; with neither `uv` nor `pipx` it prints the steps and carries on. With the
CLI, it builds the graph with `graphify update .`: code only, no LLM, no tokens.
Documentation never goes into the graph from `init`. `doctor --fix` offers the
same install after one confirmation and never builds a graph.

## Product context

What the product is and what ships first, so tickets and plans stop re-deciding
scope. `/shipit:product-discovery` interviews you and writes the PRD;
`/shipit:product-mvp-cut` classifies every story `In`, `Reduced`, `Manual` or
`Deferred`. Both follow `language.task`.

| File | Content |
| --- | --- |
| `.shipit/product/prd.md` | Problem, users, metrics, stories `H1…` with `AC1…`, non-goals |
| `.shipit/product/mvp.md` | Learning metric, core flow, the class of every story |
| `.shipit/product/*.md` | Other product docs, such as a brief or the current state |
| `.shipit/tech-design.md` | How the MVP is built |
| `.shipit/backlog.md` | Ticket index cut from the MVP; the tracker stays the source of truth |

`task-create` cites the story and flags non-goals or deferred stories; `task-next`
skips them; `code-plan` reads the story's ACs. Each task keeps the docs current:
the plan's `Docs impact` lists the status the change proves — a story `(built)`,
a delivered ticket, the current state — `code-implement` applies it, and `sync`
catches what the plan missed. Scope, metrics and design are decisions: always
proposed as a patch and applied only on your yes. The rules live in
[`references/product-context.md`](../references/product-context.md).

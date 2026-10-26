# Workflow

How shipit takes an issue from ticket to pull request. Start with the [README](../README.md) for install and the command list.

## The cycle

For an existing issue/card, Claude Code and local Codex can run the whole cycle:

```
/shipit:run ENG-412
/shipit:run https://linear.app/team/issue/ENG-412/...
```

`run` fetches the task through your configured tracker, checks its acceptance
criteria, switches to `main`, fetches its remote and merges the upstream SHA with
`--ff-only --no-overwrite-ignore`, then creates the task branch. This protected
equivalent of `git pull --ff-only` also preserves ignored local files. Five sequential
native subagent stages then sync context, plan, implement/validate, sync context
again and deliver
under `handoff.allow`. The coordinator waits for each result; missing models,
blocked criteria or failed validation stop the pipeline. Pending user changes are
never stashed or discarded. Your repo must already have `.shipit/config.json`, Python
3.10+, a clean checkout and `main` tracking a remote `main`.

At the start of `code-plan`, the issue moves to `In Progress` or the tracker's equivalent
and is read back to verify success. This applies to standalone `/shipit:code-plan` and
the planner inside `run`, independently of `handoff.allow`. A missing status
mapping or tracker write access blocks planning. Plans without an issue, or with
adapter `none`, stay local. Issues already in progress, review or a terminal state
are never moved backwards; `run` resumes at later stages do not repeat the transition.

| Stage | Claude Code | Codex |
| --- | --- | --- |
| Sync (before and after) | Sonnet 5.5 / medium | Sol 6.1 / medium |
| Plan | Opus 5.5 / high | Astra 6 / high |
| Implement | Sonnet 5.5 / high | Sol 6.1 / high |
| Review | Opus 5.5 / high | Astra 6 / high |
| Handoff | Haiku 5.5 / medium | Luna 6 / medium |

These are pinned IDs, not moving aliases. Optional per-repo overrides live under
`run.models.<anthropic|openai>.<stage>` as complete `{model, effort}` pairs;
Claude overrides also need a matching native agent definition. Configs without
`run.models` use the defaults without an upgrade. An observed runtime substitution blocks the
stage; unavailable effective-model metadata is disclosed rather than guessed.

The explicit request to run the issue authorizes execution within its criteria,
after the coordinator checks the generated plan. Scope/security/data blockers
still go to the user. `code-implement --defer-handoff` lets the builder return control
before review, final sync and the separate delivery agent run. The reviewer runs
`code-review` read-only; must-fix findings return to the builder once, then to you.
Standalone `code-implement` also returns its report; invoke `code-review`, `sync`
and `code-handoff` explicitly afterward.

State and issue/checkout locks live under the Git common directory, outside the
diff. Repeating an issue resumes its saved branch and checkpoints without pulling
main again or duplicating delivery. Give QA feedback in the same chat: failures
return to the builder on that branch. Ready for QA includes where to test, setup
and complete plain-language steps. Missing test environment is reported as QA
blocked; a PR or green tests never means human QA passed. This first pipeline uses
one existing checkout; use individual `code-plan --worktree` for independent worktrees.

The individual cycle remains available:

```
/shipit:init        read the repo, write the contract   once per repo; safe to re-run
        │
/shipit:product-discovery  interview → PRD               once per product; re-run to update
        │
/shipit:product-mvp-cut    PRD → MVP cut                 re-run to add or reclassify stories
        │
/shipit:design-system  interview → design contract       once per repo with UI; re-run to update
        │
/shipit:task-create a need becomes a ticket, or an epic  when there is no ticket yet
        │
/shipit:sync             reconcile context before planning
        │
/shipit:code-plan        plan contract in the current checkout once per task
        │
/shipit:code-implement   red/green + validation scoped to the change
        │
/shipit:code-review      ponytail-review + plan + repo rules   read-only verdict
        │
/shipit:sync             reconcile contracts/docs after implementation
        │
/shipit:code-handoff     branch, commit, push, PR body           delivery side effects
                    tracker + threads only if allowed
        │
/shipit:pr-fix      review comments + red CI             as needed
                    `--comments` / `--ci` to scope
```

Use `/shipit:task-next` to recommend the next executable issue from the live
configured tracker. Like a senior project manager, it first reads the whole board
(work in progress, review, blocked, active cycle, epics in flight), flags owned work
to finish before starting, and follows the dependency path from the most urgent
outcome to its first ready step. It weighs Goal/project relevance, priority, cycle
commitment, explicit order and verified dependencies, then explains its choice,
alternatives and blockers. It is read-only and never marks work started. `code-plan` repeats the Goal and
prerequisite checks before its startup status transition.

Plus two for visibility:

```
/shipit:doctor      do I have everything, and what does each gap cost
/shipit:status      every in-flight worktree, its PR, its tracker state
```

## Maintaining repository context

`init` sets a repo up in any state — new, documented, legacy `.sdd/`, or already
initialized. Re-running it reconciles through sync's merge and reuses every
recorded answer. Use `/shipit:sync` in the routine cycle to migrate configuration
and reconcile affected stack, commands, conventions, layers, rules and
documentation. `/shipit:sync --check` inspects without writing;
`--upgrade` migrates config only and does not certify repository context freshness.
The old `init --upgrade` invocation redirects without modifying files.

Sync preserves preferences, human edits, explicit permissions and design decisions.
Generated facts update from evidence; human-doc corrections need the request/plan's
authorization, and conflicts remain visible. `.shipit/sync-state.json` stores accepted
contract bases, the baseline commit and hashes of uncommitted sources, and is committed with the contract; dates never
decide whether an edit is human. Legacy contracts without that baseline are reconciled
conservatively. No-change sync does not rewrite files. Python 3.10+ is needed for
the baseline helper. Graph queries guide discovery; existing graphs receive local
incremental maintenance only in their owning checkout. Code structure uses
`graphify update .`; documentation and other semantic inputs use the available
Graphify skill's `/graphify <repo> --update` flow, including deletion handling.
Structural and semantic coverage are reported separately; missing capabilities
leave explicit stale/unknown coverage. This applies to standalone sync and both
run checkpoints. `--check` and `--upgrade` do not update the graph. No automatic
tool installation or full graph build.

Run checkpoints are `sync_before → plan → implement → sync_after → handoff`.
Both sync checkpoints use the independently configurable `run.models.<provider>.sync`
route. The final sync produces a separate delivery report including contract/doc
edits and final validation; the builder report remains immutable. A newly required
failed check returns to implementation and then sync. Active runs saved before
sync checkpoints require explicit reconciliation/replanning on their saved branch;
already delivered effects and journals must be reconciled before retrying.

## From a need to a ticket

`/shipit:task-create` is the entry of the cycle, for when the work exists as a sentence in
Slack and nowhere else. It drafts the ticket against your repo — grounded in real
paths, not invented ones — shows it to you, and creates it only after you say yes.

```
/shipit:task-create "sessions should expire after 30 idle minutes"
```

One coherent outcome stays one ticket even when it spans several layers. Multiple
separately useful outcomes may become an **epic with children**, each complete and
understandable on its own. `--epic` and `--single` override the shape subject to
coherent scope; `--dry-run` stops at the draft. `--plan` plans one executable task:
for published work it uses `task-next` scoped to the created IDs; for local drafts
it checks the same readiness policy. It never chooses the first child blindly.

Every task carries **Problem**, **Goal**, **What to do**, explicit exclusions when
needed, observable acceptance criteria and **QA / validation scenarios**. Each
scenario states preconditions, action, expected result and the criteria it proves.
UI checks are plain language; internal work uses measurable system evidence.
Children have their own complete descriptions, with a compact parent index.
Concise is the default, with enough detail to preserve scope and reproducibility;
there is no fixed line count or five-scenario cap.

Type (**Bug**, **Feature**, **Chore**), **Priority** (`P0`–`P3`, default `P2`) and
**Size** (`XS`–`XL`, scope and uncertainty, never hours) are required for every
issue. Only epic parents are `XL`; `--priority` and `--size` set parent values.
`init` detects existing native field mappings in `tracker.create.fields`.
Unmapped values remain in the issue body and are reported; shipit never invents
fields or converts T-shirt sizes into story points.

A **dependency** names the required output and observable unblock condition. Such
work can be fully defined and published while blocked. **Suggested order** is a
preference; **parent-child hierarchy** groups work. Neither automatically blocks a
child. Essential missing scope, permission, monetary, data or external-contract
behaviour needs a decision before publishing or planning; shipit does not invent
business rules to complete the template.

By default the draft is the deliverable. With `issue_create` in `handoff.allow`,
`code-handoff` publishes the reviewed draft after authorization. It uses the configured
provider's available capabilities for parent and blocking relations. Unsupported
relations stay explicit in issue prose and are reported as requiring manual
linking; a text reference is never claimed as a native relation.

The draft lands at `.shipit/tasks/<slug>.md` and is excluded from git — once the issue
exists, the tracker is the source of truth, and a stale copy
in the repo is worse than none. Re-running the delivery on a draft that already
carries ids creates nothing: the `Created` block is the idempotency ledger, which is
what makes a half-finished epic safe to retry.

### Trackers

| Adapter | Reached through | An epic is | Bug/Feature/Chore maps to | Priority / Size map to |
| --- | --- | --- | --- | --- |
| `linear` | Linear MCP | a parent issue with sub-issues | an existing team label | priority / T-shirt estimate |
| `jira` | Jira MCP | the project's `Epic` type, enumerated first | the issue type | priority / a `Size` field if any |
| `shortcut` | Shortcut MCP | a native Epic | the story type, exactly | `Priority` / `Size` custom fields if any |
| `github-issues` | `gh` | native sub-issues when supported; explicit text index otherwise | a supported native type or existing repo label | the Project's `Priority` / `Size` fields |
| `none` | — | — the draft is the deliverable | — | — |

`init` detects which one you use, and asks only when it genuinely cannot tell —
`ENG-412` is a valid Linear id *and* a valid Jira key, so a branch name alone never
decides between those two; a connected MCP does. A clean match asks nothing, and a
repo with no tracker at all is not a question either. `/shipit:sync --tracker linear`
sets it outright, for CI or to correct a bad detection without hand-editing JSON.

An ambiguity nobody resolves is recorded as `none` **and** listed in `unknown[]`, so
it reads as undetermined rather than absent — the distinction that decides whether
`/shipit:task-create` failing to create anything is expected or a misdetection.

With the adapter settled and its MCP connected, `init` also picks up which team or
project new issues belong to, asking only when there is more than one. Unreachable
tracker → `create.supported` goes `false`, `task-create` still writes the draft, and
`doctor` says what is missing. States, labels, transitions and
issue types are always enumerated from your workspace and matched by name; an id
copied from someone else's workspace writes to the wrong place, silently.

`task-create`, `task-next`, `code-plan`, `code-implement`, and `pr-fix` never run `git commit`, `git push`, or a
PR command. Only `code-handoff` does — and what `code-handoff` may do is a config list, not a
judgement call:

```json
"handoff": { "allow": ["branch", "commit", "push", "pr_body", "pr_ready", "tracker_status"] }
```

That is the default `/shipit:init` writes. `code-handoff` creates a ready-for-review
PR, converts an existing draft when needed, and moves the linked card to
`In Review` after verifying PR readiness. It verifies the card update and preserves
review/QA/terminal states. No card or adapter `none` → the tracker step is `n/a`.
Tracker comments, review-thread replies and issue creation remain opt-in: add
`tracker_comment`, `thread_replies` or `issue_create` per repo. Existing explicit
allow-lists are preserved by sync and migrations. A capability that is not listed is not performed, and the run says
`skipped (not in handoff.allow)` rather than doing it anyway.
The `code-plan` startup transition to `In Progress` is separate and applies whenever
planning an existing issue with a configured tracker, including inside `run`.

The tracker reference is read only for enabled capabilities: status rules by
default, and comment/creation sections only when opted in.

PR descriptions lead with the problem and resulting behavior, then final
validation. Review notes cover concrete decisions, risks or deployment ordering
only when relevant. Aim for 100–180 visible words for ordinary changes, fewer for
trivial ones; material risks and pending checks stay visible even when longer.
Full QA and supporting evidence stay in a details block or a verified link the
team can access. `code-implement` drafts the body, `sync` reconciles it with final
evidence, and `code-handoff` checks it before delivery and publishes it verbatim.

## Parallel worktrees — opt-in

**Off by default.** `code-plan` writes into your current checkout, like every other tool.
A fresh worktree does not inherit untracked local config — `.env`, credentials,
build caches — so enabling it before you know what your repo needs to boot from a
clean checkout buys friction, not parallelism.

Turn it on in `.shipit/config.json` when you actually want several tasks in flight:

```json
"worktree": { "enabled": true, "setup": "<the command that makes a clean checkout runnable>" }
```

Per-invocation override, no config edit needed — a flag in the request wins either
way: `/shipit:code-plan --worktree <request>` forces one, `--no-worktree` forces none.

Then `/shipit:code-plan` creates a worktree per task at `../worktrees/<repo>/<slug>` and
writes the plan inside it. Three things make that safe:

- **Collision detection.** Before finalizing its file list, `code-plan` reads the `Files`
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

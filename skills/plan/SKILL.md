---
name: plan
description: Use when planning, scoping, estimating, or breaking down a ticket, issue, bug, or feature request into an implementable contract. Works in the current checkout by default; isolated worktrees are opt-in via `worktree.enabled` or a `--worktree` flag. Do not use for implementation, and not for git or PR delivery — that is `handoff`.
metadata:
  input: request
  output: sdd-plan
  writes_product_code: false
---

# shipit plan

Turn a request into a plan the implementer can execute without re-deciding
anything. The plan is a contract, not a tutorial.

Write as a mid-senior dev handing work to a peer who already knows this repo. The
implementer loads `.sdd/` itself. The plan carries only what it cannot derive from
the repo: the decisions, the exact files, the analogues, the guess-prone
specifics. Everything else is noise that costs tokens on every read.

This skill ends when the plan file is written. Branch, commit, push, PR —
`handoff`.

## Context budget

Read narrow. Bulk-loading is the single biggest token sink in this flow.

- Required: the request, `.sdd/config.json`, and `.sdd/conventions.md`.
- Required: the `.sdd/rules/<layer>.md` for each layer touched, and the
  `.sdd/rules/tests/<kind>.md` for each test planned. Only those.
- Required: `references/output-contract.md`. It owns sections, size budget, and
  prohibited output; this file does not restate it.
- Required: `../../references/lean-ladder.md`, relative to this skill directory,
  for the scope gate.
- Required: `references/discovery-protocol.md`. Every run does discovery, and it
  owns the graph-before-`rg` order (graphify is the supported graph tool; its
  read commands come from `config.json`, never from its own skill or docs).
- Optional, only if touched: `references/ambiguity-policy.md`, and
  `references/worktree-protocol.md` **only when `worktree.enabled` is true**.
  Default is false — do not read it otherwise.
- Never: every rule file at once, every agent doc, a whole graph report.
- No `.sdd/` at all → stop and say: run `/shipit:init` first. Do not detect the
  stack inline; that is `init`'s job and doing it here spends the same tokens
  every single run.

## Hard rules

- No product code. No full implementation snippets.
- **Prose language.** The plan and what this skill prints follow `language.plan` in `.sdd/config.json`. Legacy string `language` → that value for every key but `code`; absent → `en`. Identifiers, commit subjects and branch names always stay English.
- Nothing not required by the acceptance criteria: no refactor, no dependency, no
  feature flag, no background job, no webhook, no abstraction.
- Every planned test names its applicable `.sdd/rules/tests/*.md`, or the layer
  rule when no test rule exists.
- Every new file cites an analogue with `path:line`, or documents why none exists.
- If `.sdd/*` or an agent doc already states it, the plan references it and moves
  on. Restating is how a 40-line plan becomes 300.
- **Verify before asserting.** Confirm an unfamiliar path, script, or command
  exists before naming it. `.sdd/config.json` records verified commands — use
  those, and never invent a sibling.
- No verification commands and no red/green sequencing in the plan. `implement`
  owns both.
- Tracker issue id present → preserve it in the slug: `<issue-id>-<slug>`.
- UI touched → the plan includes `Manual QA`.
- Ambiguity that blocks architecture, security, or data → stop with `Blockers`.
  Everything else → `Assumptions`, with the default already taken.
- No external side effects. `git worktree add` is local and allowed when worktrees
  are enabled; commit, push, and PR writes are not.
- Never create a worktree unless asked: `worktree.enabled` true, or `--worktree` in
  the request. Otherwise plan in the current checkout and say nothing about
  worktrees. `--no-worktree` overrides `enabled: true`.

## Workflow

1. **Preflight.** Load `.sdd/config.json`. Parse the request: goal, acceptance
   criteria, out-of-scope, layers touched. Derive the slug. A `task` draft at
   `<paths.tasks>/<slug>.md` is a valid request source — read it instead of asking
   the user to restate it, and take the issue id from its `## Created` block.
2. **Worktree — skip unless opted in.** A `--worktree` / `--no-worktree` flag in the
   request wins over the config; otherwise read `worktree.enabled`. Off (the
   default), key absent, or not a git repo → plan in the current checkout, skip step
   3, do not read the protocol. On → `references/worktree-protocol.md`: create or reuse
   `<worktree.root>/<slug>`, share the graph, run setup. Failure is reported, not
   fatal — fall back to the current checkout.
3. **Collision check.** Only when other worktrees exist. Same reference, collision
   section. Read the `Files` table of every active worktree's plan and intersect
   paths. Overlap → warn with the worktree and the shared paths before going
   further.
4. **Discovery.** `references/discovery-protocol.md`. `graph` non-null in
   `config.json` → run its `query` / `explain` / `path` strings verbatim *before*
   any `rg`; `rg` is the fallback, not the default. `graph: null` but a graphify
   graph on disk → stale config, protocol § 0 covers it. Find one analogue per new
   file. Stop when found.
5. **Spec contract.** User story, testable acceptance criteria, business rules,
   failure conditions, authorization and scoping rules, UI states when frontend.
6. **Scope gate.** Run the ladder over the `Files` table. Every `Create` row
   passes rungs 1–4 or it does not ship. What the gate rejects goes to
   `Out of scope` as `skipped: <X>, add when <Y>`.
7. **Ambiguity.** `references/ambiguity-policy.md`. Blocking → stop. Otherwise →
   `Assumptions` with the default taken.
8. **Gates.** UI touched → `Manual QA` filled and UI states in `Notes`. Docs made
   stale → `Docs impact` with exact paths and sections. Neither → delete the
   heading; an empty section is noise.
9. **Estimate.** One line: S / M / L, and the driver. Uncertainty sizes a plan,
   not line count.
10. **Write.** `<paths.plans>/<slug>.md` from `assets/plan-template.md`, in the
    current checkout — or inside the worktree when step 2 created one.
11. **Self-check.** Run `output-contract.md`'s checks as checks. Never emit the
    checklist into the plan. Fix before reporting done.

## Final report

- Plan path. Name the worktree only if one was used.
- Discovery source: graph, or the rg-only warning from `discovery-protocol.md` § 0
  when no graphify output is in the project. One line, never omitted.
- `sdd_tracking: local` → say so: the plan file won't travel as a PR diff,
  `handoff` pastes it into the PR body instead.
- Whether a tracker issue id was detected, and the slug produced.
- Collisions found with in-flight worktrees, when there were any to check.
- Blockers, or assumptions taken.
- Estimate.
- Next: `/shipit:handoff` in `plan` mode to deliver it, or `/shipit:implement` to
  execute it locally.

Do not claim implementation done. Do not claim anything was delivered. This skill
ends at the plan file.

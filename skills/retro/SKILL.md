---
name: retro
description: Use after a session or a `shipit:run` to propose improvements to the agent's environment — graph, verified commands, checks, rules, steering files, access, ticket quality — most severe first, each as an exact patch applied only on your yes. Never touches product code.
metadata:
  input: run-or-session
  output: retro-findings
  writes_product_code: false
---

# shipit retro

Fix what the agent worked *in*, not what it built. Each finding cites evidence from
this run, carries the patch, and names the mistake or cost it prevents next run.

## Context budget

- Required: `.shipit/config.json`.
- Run id or issue given: the run directory is the
  `$(git rev-parse --git-common-dir)/shipit/runs/*/` whose `state.json` carries that
  `issue_key` or `issue_url`. Read its plan, builder report, review result and
  delivery report. Metrics: `mcp__shipit__run_metrics` on the run's branch, else the
  `## Run metrics` section of its PR body. No metrics → Tool economy is `n/a`, never
  estimated.
- Otherwise the current session; a session log path the user passes replaces it.
- Then only the files a candidate patch touches: the `.shipit/rules/<layer>.md`,
  `.shipit/conventions.md`, the `docs.pointer` file, the linter or CI config that
  would host a check. Never the whole repo, never a graph report.

## Hard rules

- **Read-only on product code**, tests, plans, reports and human docs (`docs/`,
  `.shipit/docs/`, `.shipit/product/`). No git, PR or tracker writes.
- **Prose language.** What this skill prints follows `language.plan` in `.shipit/config.json`. Legacy string `language` → that value for every key but `code`; absent → `en`. Identifiers, commit subjects and branch names always stay English.
- **Every proposal is an exact patch** — file, section, lines before and after — or
  an exact command. Applied only on the user's yes, one finding at a time; no yes →
  nothing written.
- **Commands only from evidence.** A `commands` key is proposed only for a command
  the evidence shows run green, with its `commands_verified` entry (`proof: real`,
  exit and time from the evidence) and its removal from `unknown[]`. Never invent
  or guess one.
- **Mechanical violations become checks, not prose.** A fixed pattern, banned API,
  import shape or file-location rule → a check in the repo's own linter, pre-commit
  or CI, proposed as a ticket draft for `/shipit:task-create`. Only a judgement call
  (cross-file consistency, matching surrounding style) becomes a rule line.
- No finding without evidence from this run. Nothing worth changing → say so in one
  line.

## Categories

- **Navigation** — the agent took long to find a file or relationship → `graphify
  update .` when the graph is stale or absent, an exemplar in
  `.shipit/conventions.md`, or a pointer line in `docs.pointer` outside the
  `shipit:contract` block.
- **Automated checks** — a mistake a check would have caught → wire the repo's
  existing lint/typecheck/test into `commands` per the rule above. An existing check
  left unwired or broken is the finding. No pre-commit hook and no CI job running
  them → report that as a finding.
- **Rules** — a mistake review missed, or a correction repeated → classify:
  mechanical → check ticket draft; judgement → one line in `.shipit/rules/<layer>.md`,
  which review reads.
- **Steering sediment** — a `docs.pointer` or `.shipit/rules/*` line that restates
  what config, a check or another loaded file already enforces → delete it.
- **Tool economy** — the stage whose tokens dwarf the others, and the calls behind
  it: bulk reads, grep dumps where a graph query would do, a fact re-detected that
  the config already holds.
- **Information access** — a fact the agent lacked (dev-server logs, a test
  database, a browser, a read-only third-party view) → name the access and where it
  would be configured.
- **Ticket quality** — a plan blocker or assumption the ticket should have
  answered → the missing question as a template or policy note for `task-create`,
  reported upstream for shipit. Never a product doc or tracker edit.

## Workflow

1. Load the evidence per *Context budget*.
2. List candidates per category. Drop any without a concrete event behind it.
3. Order by severity: a mistake that reached the PR; one caught late (review
   round-trip, red check); avoidable cost; sediment.
4. Read only the target files and write each patch against their current text.
5. Print the report and stop. On yes, apply that patch and print the diff.

## Final report

```
retro: ENG-412 (run) · 3 findings

1. Rules · mechanical — reached the PR
   evidence: review missed `Time.now` in app/jobs/sync_job.rb:14; fixed in pr-fix
   patch: ticket draft for /shipit:task-create — enable rubocop Rails/TimeZone in .rubocop.yml
   prevents: the same banned call passing review again

2. Automated checks — caught late
   evidence: builder ran `bin/rubocop` green (exit 0); commands.lint is null, unknown[] lists lint
   patch: .shipit/config.json commands.lint, commands_verified.lint, unknown[] − lint
   prevents: lint errors surfacing only in CI

3. Tool economy — code-implement 71% of 412k tokens
   evidence: 9 whole-file reads of app/models/; graph present, never queried
   patch: AGENTS.md (docs.pointer), after the shipit:contract block + "graphify query before reading app/models/"
   prevents: ~200k tokens of bulk reads
```

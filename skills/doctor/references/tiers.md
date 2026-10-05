# Dependency Tiers

The full list `doctor` reports and `init` echoes. Tier tells you what happens
without the thing, not how much you should want it.

## Tier 0 — required

| Item | Check | Without it |
| --- | --- | --- |
| `git` | `command -v git` | shipit does not run. Every skill needs the repo root, the branch, and worktrees. |

That is the whole tier. Everything below is optional.

`shipit:run` has additional requirements specific to its orchestrated pipeline:
Python 3.10+, native subagent controls, access to its configured model/effort pairs,
a readable existing tracker issue, and local `main` with a remote `main` upstream.
Report these when checking readiness for `run`; they do not block the individual
planning/implementation skills. Never install or substitute them silently.

## Tier 1 — recommended

Delivery reaches GitHub and your tracker through these. Planning, drafting a
ticket, and implementing do not need them.

The two tracker rows are not checked by `scripts/companions.sh` — it checks
executables, and a tracker is reached through an MCP server or `gh`. They come from
`.sdd/config.json` plus what is connected in the session.

| Item | Check | Fix | Without it |
| --- | --- | --- | --- |
| `gh` | `command -v gh` | `brew install gh`, or see cli.github.com | `handoff` cannot open or update a PR |
| `gh` auth | `gh auth status` | `gh auth login` | same as above |
| tracker | adapter from `.sdd/config.json`, plus whether its mechanism is reachable this session | re-run `/shipit:init` once the tracker is reachable | no tracker-supplied branch name — `.sdd/conventions.md` decides instead. Adapter `none` is a valid configuration, not a gap |
| tracker create | `tracker.create.supported` plus the target it names | re-run `/shipit:init` with the tracker connected | the draft names no target to paste into. `task` still writes it, and no skill ever creates the issue. With adapter `none` this is `n/a`, not a gap |

## Tier 2 — accelerators

shipit produces the same answers without these. It spends more tokens doing it.

| Item | Check | Fix | Cost of the fix |
| --- | --- | --- | --- |
| graphify CLI | `command -v graphify` | `uv tool install graphifyy` | fast, free. Needs `uv` or pip already present |
| graphify graph | `test -f <graph.out>/graph.json` | `graphify .` in the main checkout | **minutes + extraction tokens.** Never run automatically, at any flag |
| caveman | `claude plugin list` names it | `claude plugin marketplace add JuliusBrussee/caveman` then `claude plugin install caveman@caveman` | plugin install, ships hooks |

Notes:

- Having the CLI without a graph changes nothing. They are two separate gaps.
- Inside a worktree the graph is normally a symlink to the main checkout's — that is
  correct, not stale. `worktree.share_graph` controls it.
- caveman compresses prose. shipit exempts non-developer QA steps from compression
  either way, so installing it never degrades the deliverable.

## Tier 3 — do not enable during a cycle

| Item | Check | State | Fix |
| --- | --- | --- | --- |
| ponytail | `claude plugin list` names it | present → report as something to turn off | `stop ponytail` |

Three reasons, all from ponytail's own documentation:

1. **It is a persistent mode.** "ACTIVE EVERY RESPONSE… Off only: stop ponytail",
   backed by session hooks that keep it on between turns. shipit skills are one-shot
   workflows with their own rules. Two authorities, one decision.
2. **Its test rule contradicts spec-driven work.** "YAGNI applies to tests too" — one
   `assert`-based self-check, no frameworks, no fixtures. In a repo with a real suite
   and a coverage gate, that leaves CI red.
3. **Its output rule truncates reports.** "at most three short lines" against a report
   that must carry non-developer QA steps, a file manifest, and validation results.

The useful part of ponytail — the laziness ladder, the review tags, the debt marker
convention — is **vendored** in `references/lean-ladder.md`, with those two rules
explicitly overridden. You already have it.

Install the plugin separately if you want standalone `/ponytail-audit` (repo-wide
bloat) or `/ponytail-debt` (marker ledger):

```
claude plugin marketplace add DietrichGebert/ponytail
claude plugin install ponytail@ponytail
```

Two commands, in that order — the marketplace has to exist before the install
resolves. Then turn the mode off while running shipit.

## Contract checks

Not dependencies, but `doctor` reports them in the same pass because they break the
same way.

| Check | Meaning |
| --- | --- |
| `.sdd/` present | Absent → `plan` and `implement` refuse. Fix: `/shipit:init` |
| `config.json` parses | Corrupt → re-run `/shipit:init` |
| `unknown[]` empty | Non-empty → those verification steps do not exist. Named in every report |
| `test_one` has `{path}` | Missing → the red-green loop degrades to running the whole suite |
| `worktree.link[]` empty | Non-empty → untracked files, usually secrets, are symlinked into worktrees. Report each by name |

# Development and design notes

## Release versioning

The release workflow runs after every push to `main`. It compares distributed
files with the latest `vMAJOR.MINOR.PATCH` tag, computes a version, writes it to
both plugin manifests and the `init` config template, then creates the tag and
GitHub release. No release is made for changes outside the distributed plugin.

For changed plugin files, Conventional Commit messages choose the bump:

| Change | Bump |
| --- | --- |
| `fix:` or `perf:`, or an untyped plugin change | Patch |
| `feat:` or a new skill, agent, or OpenCode command | Minor |
| `!` or `BREAKING CHANGE:`, or removal/rename of a public command | Major; minor while version is `0.x` |

Highest level since the latest release wins. Use a Conventional Commit title
when modifying existing skill behavior so the workflow can distinguish fixes
from features. Version numbers are owned by the release workflow; do not bump
them in feature branches. For local testing before a release, load this checkout
with `claude --plugin-dir /absolute/path/to/shipit`.

## Trying a change locally

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

## Token cost

Reducing token spend is an explicit goal, not a side effect. Four levers, largest
first:

| Lever | Attacks |
| --- | --- |
| `.shipit/config.json` | Re-detecting unchanged facts. Initialized once, reconciled by `sync` when sources change. |
| Context budget | Wide reads. Rule files load only for layers actually touched. |
| graphify | Grep dumps and whole-file reads, replaced by a scoped subgraph. |
| Context7 | Guessed APIs. `code-implement` and `sync` check only the libraries a change actually touches, against the installed version — see [`references/docs-lookup.md`](../references/docs-lookup.md). |
| caveman | Prose. Non-developer QA steps stay exempt from compression; everything else, PR bodies included, is short by default. |

Plans scale with behavioral complexity and uncertainty; there is no arbitrary line
cap. They record the repo baseline, verified relationships, essential decisions,
and source acceptance → change → validation links. Discovery stops when those
claims are supported, not after a fixed number of searches. Reuse and local
patterns guide choices; unresolved essential business or external-contract
decisions block instead of becoming guesses. Equivalent plans can differ in prose
and minor choices across models. Remove repetition, never required coverage.

Reproducible planning fixtures and a behavioral comparison protocol live in
[`evals/plan-consistency/`](../evals/plan-consistency/README.md).

### Measured footprint

From `claude plugin details`, against the four hand-written skills shipit was
extracted from:

| Skill | always-on | on-invoke | vs. original |
| --- | --- | --- | --- |
| `code-plan` | ~110 | ~1.8k | −28% on invoke (was ~2.5k) |
| `code-implement` | ~90 | ~2.6k | −16% on invoke (was ~3.1k) |
| `pr-fix` | ~90 | ~1.9k | +6% |
| `code-handoff` | ~90 | ~1.5k | −21% |
| `init` | ~90 | ~1.7k | new |
| `doctor` | ~90 | ~1.4k | new |
| `status` | ~70 | ~1.2k | new |
| `task-create` | not yet measured | not yet measured | new |
| `design-system` | not yet measured | not yet measured | new; the interview is multi-turn by design |
| `product-discovery` | not yet measured | not yet measured | new; multi-turn interview |
| `product-mvp-cut` | not yet measured | not yet measured | new |
| `run` | not yet measured | not yet measured | new; native subagent work is additional |

The four equivalent skills cost **~380 always-on against the originals' ~442**, and
the two heaviest got materially cheaper per invocation — the contract removed the
stack re-discovery that used to live in their bodies.

Total always-on was **~629 vs ~442** at seven skills, because there were three more
of them. That is the honest trade: +187 tokens per session bought `init`, `doctor`,
and `status`. `task-create` and `task-next` have not been measured yet — expect their
always-on description to cost about the same as the others, roughly +90. `run` is
the ninth and `design-system` the tenth; neither has been measured. If that is
not worth it for your setup, disable the plugin per-project rather than working around
it.

Neither number captures the actual saving, which is runtime input: file reads avoided
by the context budget, stack detection paid once instead of per plan, and grep dumps
replaced by a scoped subgraph. Measure that with
`claude plugin eval shipit`, which runs a no-plugin baseline arm for comparison.

## On ponytail

shipit vendors the useful part of [ponytail](https://github.com/DietrichGebert/ponytail)
(MIT) into `references/lean-ladder.md`: the laziness ladder, the five review tags, and
the debt-marker convention. `code-plan` runs the ladder as a scope gate, `code-implement` uses it
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

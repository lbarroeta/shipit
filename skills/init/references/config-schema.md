# `.shipit/config.json` Schema

The machine contract. Read by `run`, `task-create`, `task-next`, `code-plan`, `code-implement`, `pr-fix`, `code-handoff`,
`status`, and `doctor`. Created by `init`, which also migrates a legacy `.sdd/`
contract; maintained by `sync`. Its location is fixed: every skill reads it at
`.shipit/config.json`, before any other path is known.

Three values carry meaning, and they are not interchangeable:

| Value | Means | Consumer behaviour |
| --- | --- | --- |
| a real value | detected and, for commands, verified | use it |
| `null` | this repo does not have it | skip that step silently |
| `"unknown"` | could not be determined | **ask the user**, never guess |

`unknown[]` at the top level lists every key that ended up `"unknown"` or was
downgraded to `null` after failing verification. `doctor` and `init` print it.

## Fields

| Key | Type | Notes |
| --- | --- | --- |
| `shipit_version` | string | Plugin version that wrote the file |
| `generated_at` | date | Initial generation date; never used to infer human edits |
| `handoff.allow` | string[] | Side effects `code-handoff` may perform. Absent → `["branch", "commit", "push", "pr_body", "pr_ready", "tracker_status"]`. See below |
| `run.models` | object | Optional stage model/effort overrides by `anthropic` or `openai`. Empty/absent uses the pinned defaults in `skills/run/assets/models.json`. See below |
| `repo.name` | string | Basename of the git toplevel |
| `repo.default_branch` | string | From `origin/HEAD` |
| `repo.remote` | string | Usually `origin` |
| `language.plan` | string | Plan, implementation report, QA guide, and what every skill prints. BCP-47 tag or plain name (`en`, `es`, `pt-BR`). Asked once by `init`, default `en`. See below |
| `language.task` | string | Ticket drafts, created issues, tracker comments. Default `en` |
| `language.pr` | string | PR title and body, review-thread replies. Default `en` |
| `language.code` | string | Comments written in code. Default `en` |
| `docs.agent_docs` | string[] | Agent instruction files and the local docs they link to. Symlinks resolved; each file listed once |
| `docs.pointer` | string | File holding the `shipit:contract`, `shipit:design` and `shipit:product` blocks: `AGENTS.md` when `init` created it or it already carried a shipit block, otherwise `CLAUDE.local.md`. Read by `sync`, `doctor` and `design-system` to find the blocks. Absent → `AGENTS.md` |
| `docs.owned_by_shipit` | string[] | Always `[".shipit/"]` |
| `stack.languages` | string[] | With version pin files as evidence in `stack.md` |
| `stack.frameworks` | string[] | Only from declared dependencies |
| `stack.package_manager` | string \| null | Decided by lockfile |
| `commands.*` | string \| null | Never written unverified. See placeholders below |
| `commands_verified.<key>` | `{exit, at, proof, command}` | Exact proving command; proof is `resolve`, `version`, `help`, `dry-run`, or `real`. Only `real` proves execution of the operation |
| `paths.plans` | string | Default `.shipit/plans` |
| `paths.tasks` | string | Default `.shipit/tasks`. Where `task-create` writes ticket drafts. Local scratch — `init` excludes it via `.git/info/exclude` |
| `paths.rules` | string | Default `.shipit/rules` |
| `paths.src` | string[] | Roots that hold product code |
| `paths.tests` | string[] | Roots that hold tests |
| `tests.framework` | string \| null | |
| `tests.location` | `mirrored` \| `colocated` \| `"unknown"` | Decided by counting files |
| `tests.naming` | string \| null | Real pattern, e.g. `*_spec.rb` |
| `tests.kinds` | string[] | Only kinds with ≥1 real file |
| `tests.coverage_gates_merge` | boolean | Whether coverage can fail the merge |
| `layers[]` | object[] | `{key, dirs[], test_kind, rule, exemplar}`. May be empty |
| `tracker.adapter` | `linear` \| `github-issues` \| `jira` \| `shortcut` \| `none` | Detected; asked when detection is undecided. **Never `"unknown"`** — an unresolved ambiguity is written `none` with the key in `unknown[]`, which reads as undetermined, not absent |
| `tracker.issue_pattern` | string \| null | Regex, for slug and branch parsing |
| `tracker.branch_from_tracker` | boolean | Adapter can supply the branch name |
| `tracker.create.supported` | boolean | Whether a target for new issues is known at all. `task-create` echoes the target; authorized handoff publishes when issue_create is allowed |
| `tracker.create.team` | string \| null \| `"unknown"` | Team, group, or workflow a new issue belongs to. Required by `linear` and `shortcut` |
| `tracker.create.project` | string \| null \| `"unknown"` | Project or project key. Required by `jira`, optional elsewhere. `github-issues`: `<owner>/<number>` of a Project linked to the repo, owner being the Project's |
| `tracker.create.initial_state` | string \| null | State name a new issue lands in. Matched by name, never by id |
| `tracker.create.default_labels` | string[] | Labels a new issue should carry. Only labels the tracker already has |
| `tracker.create.epic_kind` | string \| null | How this workspace models a parent: `parent-issue`, `epic`, `project`, `task-list` |
| `tracker.create.fields.priority` | string \| null \| `"unknown"` | Name of the tracker field a draft's `Priority` (`P0`–`P3`) is written to, as the tracker spells it — `priority` in Linear and Jira, `Priority` on a GitHub Project or a Shortcut custom field. `null`: verified absent, priority stays in the draft. `"unknown"`: not determined, `code-handoff` tries the adapter's default name |
| `tracker.create.fields.size` | string \| null \| `"unknown"` | Same, for `Size` (`XS`–`XL`). Only a T-shirt field counts — `estimate` in Linear when the team's scale is T-shirt, a `Size` single-select on a GitHub Project, a `Size` field in Jira or Shortcut. A points scale is `null`: a size is never converted to points |
| `graph` | object \| null | `{tool, out, query, path, explain, update}`. Null unless CLI **and** graph exist |
| `markers.debt` | string | Default `ponytail:` |
| `companions.*` | `present` \| `absent` | `ponytail`, `graphify_cli`, `graphify_graph`, `caveman` |
| `worktree.enabled` | boolean | **Default `false`.** Opt-in: `code-plan` works in the current checkout unless the user turns this on |
| `worktree.root` | string | Default `../worktrees/<repo.name>` |
| `worktree.base` | string | Branch new worktrees fork from |
| `worktree.link[]` | string[] | **Empty at init.** Opt-in only. See warning below |
| `worktree.share_graph` | boolean | Symlink the main checkout's graph into worktrees |
| `worktree.setup` | string \| null | Runs once after a worktree is created |
| `ci.config` | string \| null | The CI file |
| `ci.required_jobs` | string[] | Jobs that gate the merge |
| `unknown[]` | string[] | Every undetermined key |

Everything under `.shipit/` is shipit's. The repo's own documentation — `docs/`,
the README, agent docs — is linked from it, never copied into it, and edited only
to apply a doc patch the user approved. Product docs are the one exception: they
move into `.shipit/` per `../../../references/product-context.md § Migration`.

## Placeholders

Substituted at call time. Never bake the value in.

| Token | Meaning | Valid in |
| --- | --- | --- |
| `{path}` | A test file path | `commands.test_one` |
| `{base}` | `repo.default_branch` | `commands.coverage_gate`, any diff command |
| `{q}` | A natural-language question | `graph.query` |
| `{node}` | One file, symbol, or concept name | `graph.explain` |
| `{a}`, `{b}` | Two node names, in order | `graph.path` |

A `test_one` without `{path}` is malformed: `code-implement` cannot target a single
test, the red-green loop is unavailable, and required tests become a validation
gap. The full suite is never run locally as a fallback; CI owns it.

## Scope of `language`

One language per action, so a plan can be read in Spanish while the PR and the
code stay English for the team:

| Key | Governs |
| --- | --- |
| `plan` | Plan narrative, implementation report, QA guide, what a skill prints |
| `task` | Ticket drafts, created issues, tracker comments |
| `pr` | PR title and body, review-thread replies |
| `code` | Comments written in code |

A key never borrows another's value: a comment in code follows `code`, even when
it is written while executing a plan in `plan`'s language.

Legacy string form (`"language": "es"`) → that value for `plan`, `task` and `pr`;
`code` stays `en`. Absent → every key `en`. A missing key inside the object → `en`.

Never applies to: identifiers, commit subjects, branch names, file paths, and
the `.shipit/` contract itself — those stay English so the repo stays greppable and
portable across teams.

## Warning on `worktree.link[]`

Every entry becomes a symlink from a worktree to an untracked file in the main
checkout — in practice `.env` files and signing keys. Those worktrees live outside
the repo, so no `.gitignore` in the repo covers them, and any tool that runs in
the worktree root can read them.

`init` always writes `[]`. Filling it is a deliberate user decision. The safe
alternative is `worktree.setup`, which regenerates what the worktree needs.

## `handoff.allow`

The permission list for delivery side effects in `code-handoff`. Every entry is opt-in
except the six defaults, and a capability that is absent is simply not performed —
reported as `skipped (not in handoff.allow)`, never as an error.

| Entry | Grants |
| --- | --- |
| `branch` | creating or switching to the delivery branch |
| `commit` | staging and committing the manifest |
| `push` | pushing the branch |
| `pr_body` | creating a ready-for-review PR, and replacing its body |
| `pr_ready` | marking an existing draft PR ready for review |
| `tracker_comment` | one comment per mode — QA steps and the PR link |
| `tracker_status` | the review transition after a ready PR is delivered |
| `thread_replies` | replying to and resolving review threads after `pr-fix` |
| `issue_create` | `code-handoff`'s `task` mode: creating the issues a draft describes |

Defaults to `branch`, `commit`, `push`, `pr_body`, `pr_ready` and `tracker_status`.
`init` writes them explicitly so the file says what it allows rather than relying
on a default nobody remembers. Granting a capability
never creates one: `tracker_comment` with adapter `none` is still `n/a`.

Existing explicit allow-lists remain authoritative; sync never
adds permissions to them automatically. Unknown entries are ignored and reported
as drift. An empty list means `code-handoff` does nothing and says which capability the
run needed.
The startup transition to `In Progress` belongs to `code-plan` (also inside `run`)
and is independent of this list.

## `run.models`

`run` uses native subagents, with one complete `{model, effort}` pair per stage.
Defaults: Anthropic plan and review = Opus 5.5/high, implement = Sonnet 5.5/high,
sync = Sonnet 5.5/medium, handoff = Haiku 5.5/medium; OpenAI plan and review =
Astra 6/high, implement = Sol 6.1/high, sync = Sol 6.1/medium, handoff = Luna 6/medium. Runtime IDs are pinned in the run skill's
`assets/models.json`; aliases are not used. Both sync checkpoints share route `sync`.

Example override: `run.models.openai.plan = {"model": "gpt-6.1-sol", "effort": "high"}`.
Only `sync`, `plan`, `implement`, `review`, `handoff` are valid stage keys. Overrides must be complete
pairs, available in the hosting runtime; Claude Code also needs a matching native
agent definition. A mismatch blocks the run instead of inheriting the session
model. `init` writes `{}`; `sync` preserves explicit overrides.
Absent `run` is backward-compatible; no migration is needed to try the defaults.

## Reading it safely

- Never assume a key exists. A config written by an older `shipit_version` may
  lack fields; treat absent as `null` — except `paths.plans/tasks/rules` and
  `docs.pointer`, whose absence means their documented default. A leftover
  `sdd_tracking` is ignored.
- An absent `tracker.create.fields` reads as `"unknown"` for both keys: `code-handoff`
  tries the adapter's default field names, exactly as before the field existed.
- A `tracker.create` block that is absent means the config predates the field.
  Treat it as `supported: false` — `task-create` writes a draft and reports the drift.
  Never patch the config to add it; that is a run of `sync`.
- An absent `handoff.allow` is the default six, not "everything". A config written
  before the field existed uses that same default; an existing explicit list
  continues to limit delivery to its listed capabilities.
- Only `init` (creation) and `sync` (maintenance) write this file. Other skills
  report drift and return it to `sync`; they never patch config independently.
- A command that fails *because it does not exist* means the contract has drifted.
  Say that explicitly rather than reporting it as a code failure.

## Upgrades

Read by `init` (legacy migration), `sync` and `sync --upgrade`, top to bottom,
every row after the config's `shipit_version`. A release that changes the config's
shape adds a row; one that does not, adds nothing.

| Version | Change | Action |
| --- | --- | --- |
| `0.8.0` | `language` became one language per action | String → ask the four keys, each prefilled: `plan`, `task`, `pr` with the string, `code` with `en`. Absent → ask, default `en` per key. Already an object → nothing |
| `0.9.0` | `run.models` adds optional native subagent routing | Add `{ "models": {} }` under `run` only when absent; preserve any existing routes. Defaults are pinned in the plugin |
| `0.10.0` | `tracker.create.fields` names where `Priority` and `Size` land | Absent → add `{ "priority": "unknown", "size": "unknown" }` and append both keys to `unknown[]`; adapter `none` → `null` for both, nothing appended. Upgrade does not detect — say `/shipit:sync` resolves them once the tracker is reachable |
| `0.15.0` | The contract moved from `.sdd/` to `.shipit/`; `sdd_tracking` retired | Performed by `init` (see its *Legacy migration*): `sync` finding `.sdd/config.json` without `.shipit/config.json` stops and points to `/shipit:init`. On the moved config: drop `sdd_tracking`; a `paths.*` value inside `.sdd/`, or reached through a `.sdd/` symlink, becomes its `.shipit/` default, and any other custom value is kept and reported; set `docs.owned_by_shipit` to `[".shipit/"]` and `docs.pointer` to the file that holds the `shipit:contract` block |

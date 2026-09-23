# `.sdd/config.json` Schema

The machine contract. Read by `task`, `plan`, `implement`, `pr-fix`, `handoff`,
`status`, and `doctor`. Written only by `init`.

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
| `generated_at` | date | Used by refresh mode to detect human edits |
| `sdd_tracking` | `committed` \| `local` | Asked once at first `init`. `local` means excluded via `.git/info/exclude`, never `.gitignore`. Read by `handoff` (staging) and `plan`'s worktree step (contract sharing) |
| `handoff.allow` | string[] | Side effects `handoff` may perform. Absent → `["branch", "commit", "push", "pr_body"]`. See below |
| `repo.name` | string | Basename of the git toplevel |
| `repo.default_branch` | string | From `origin/HEAD` |
| `repo.remote` | string | Usually `origin` |
| `language.plan` | string | Plan, implementation report, QA guide, and what every skill prints. BCP-47 tag or plain name (`en`, `es`, `pt-BR`). Asked once by `init`, default `en`. See below |
| `language.task` | string | Ticket drafts, created issues, tracker comments. Default `en` |
| `language.pr` | string | PR title and body, review-thread replies. Default `en` |
| `language.code` | string | Comments written in code. Default `en` |
| `docs.agent_docs` | string[] | Symlinks resolved; each file listed once |
| `docs.owned_by_shipit` | string[] | Always `[".sdd/"]` |
| `stack.languages` | string[] | With version pin files as evidence in `stack.md` |
| `stack.frameworks` | string[] | Only from declared dependencies |
| `stack.package_manager` | string \| null | Decided by lockfile |
| `commands.*` | string \| null | Never written unverified. See placeholders below |
| `commands_verified.<key>` | `{exit, at, proof}` | `proof` is the form that ran: `version`, `help`, `dry-run`, `real` |
| `paths.plans` | string | Default `.sdd/plans` |
| `paths.tasks` | string | Default `.sdd/tasks`. Where `task` writes ticket drafts. Local scratch — `init` excludes it via `.git/info/exclude` |
| `paths.rules` | string | Default `.sdd/rules` |
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
| `tracker.create.supported` | boolean | Whether a target for new issues is known at all. No skill creates issues; `task` echoes this block so the draft is pasted into the right place |
| `tracker.create.team` | string \| null \| `"unknown"` | Team, group, or workflow a new issue belongs to. Required by `linear` and `shortcut` |
| `tracker.create.project` | string \| null \| `"unknown"` | Project or project key. Required by `jira`, optional elsewhere |
| `tracker.create.initial_state` | string \| null | State name a new issue lands in. Matched by name, never by id |
| `tracker.create.default_labels` | string[] | Labels a new issue should carry. Only labels the tracker already has |
| `tracker.create.epic_kind` | string \| null | How this workspace models a parent: `parent-issue`, `epic`, `project`, `task-list` |
| `graph` | object \| null | `{tool, out, query, path, explain, update}`. Null unless CLI **and** graph exist |
| `markers.debt` | string | Default `ponytail:` |
| `companions.*` | `present` \| `absent` | `ponytail`, `graphify_cli`, `graphify_graph`, `caveman` |
| `worktree.enabled` | boolean | **Default `false`.** Opt-in: `plan` works in the current checkout unless the user turns this on |
| `worktree.root` | string | Default `../worktrees/<repo.name>` |
| `worktree.base` | string | Branch new worktrees fork from |
| `worktree.link[]` | string[] | **Empty at init.** Opt-in only. See warning below |
| `worktree.share_graph` | boolean | Symlink the main checkout's graph into worktrees |
| `worktree.setup` | string \| null | Runs once after a worktree is created |
| `ci.config` | string \| null | The CI file |
| `ci.required_jobs` | string[] | Jobs that gate the merge |
| `unknown[]` | string[] | Every undetermined key |

## Placeholders

Substituted at call time. Never bake the value in.

| Token | Meaning | Valid in |
| --- | --- | --- |
| `{path}` | A test file path | `commands.test_one` |
| `{base}` | `repo.default_branch` | `commands.coverage_gate`, any diff command |
| `{q}` | A natural-language question | `graph.query` |
| `{node}` | One file, symbol, or concept name | `graph.explain` |
| `{a}`, `{b}` | Two node names, in order | `graph.path` |

A `test_one` without `{path}` is malformed: `implement` cannot target a single
test, and the whole red-green loop degrades to running the full suite.

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
the `.sdd/` contract itself — those stay English so the repo stays greppable and
portable across teams.

## Warning on `worktree.link[]`

Every entry becomes a symlink from a worktree to an untracked file in the main
checkout — in practice `.env` files and signing keys. Those worktrees live outside
the repo, so no `.gitignore` in the repo covers them, and any tool that runs in
the worktree root can read them.

`init` always writes `[]`. Filling it is a deliberate user decision. The safe
alternative is `worktree.setup`, which regenerates what the worktree needs.

## `handoff.allow`

The permission list for the one skill with side effects. Every entry is opt-in
except the four defaults, and a capability that is absent is simply not performed —
reported as `skipped (not in handoff.allow)`, never as an error.

| Entry | Grants |
| --- | --- |
| `branch` | creating or switching to the delivery branch |
| `commit` | staging and committing the manifest |
| `push` | pushing the branch |
| `pr_body` | creating a draft PR, and replacing its body |
| `pr_ready` | marking a PR ready for review |
| `tracker_comment` | one comment per mode — QA steps and the PR link |
| `tracker_status` | the mode's status transition |
| `thread_replies` | replying to and resolving review threads after `pr-fix` |
| `issue_create` | `handoff`'s `task` mode: creating the issues a draft describes |

Defaults to the first four. `init` writes them explicitly so the file says what it
allows rather than relying on a default nobody remembers. Granting a capability
never creates one: `tracker_comment` with adapter `none` is still `n/a`.

Unknown entries are ignored and reported as drift. An empty list means `handoff`
does nothing and says which capability the run needed.

## Reading it safely

- Never assume a key exists. A config written by an older `shipit_version` may
  lack fields; treat absent as `null` — except `sdd_tracking`, whose absence means
  the config predates this field and defaults to `committed`, the original
  behaviour.
- A `tracker.create` block that is absent means the config predates the field.
  Treat it as `supported: false` — `task` writes a draft and reports the drift.
  Never patch the config to add it; that is a re-run of `init`.
- An absent `handoff.allow` is the default four, not "everything". A config written
  before the field existed gets git and the PR body, nothing that reaches a human.
- Never write to this file outside `init`. A skill that wants to change the
  contract reports the drift and lets the user re-run `init`.
- A command that fails *because it does not exist* means the contract has drifted.
  Say that explicitly rather than reporting it as a code failure.

## Upgrades

Read by `init --upgrade`, top to bottom, every row after the config's
`shipit_version`. A release that changes the config's shape adds a row; one that
does not, adds nothing.

| Version | Change | Action |
| --- | --- | --- |
| `0.8.0` | `language` became one language per action | String → ask the four keys, each prefilled: `plan`, `task`, `pr` with the string, `code` with `en`. Absent → ask, default `en` per key. Already an object → nothing |

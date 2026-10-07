# Detection Recipes

Run in order. Each recipe names what to look for and what evidence to record.
Do not improvise a detection this file does not describe — an invented convention
is worse than an `unknown`.

Evidence format everywhere: `path:line`, or the command plus its exit code.

## 1 — Root, default branch, remote

```bash
git rev-parse --show-toplevel
git rev-parse --abbrev-ref origin/HEAD 2>/dev/null   # → origin/main
git remote
```

No `origin/HEAD` → try `git symbolic-ref refs/remotes/origin/HEAD`, then fall
back to the current branch and record it as an assumption, not a fact.

## 2 — Language, runtime, package manager

Match manifests, then pin the manager by lockfile. A repo can hit several rows;
record all of them.

| Manifest | Language | Manager decided by |
| --- | --- | --- |
| `Gemfile` | Ruby | `Gemfile.lock` → bundler |
| `package.json` | JS/TS | `yarn.lock` → yarn · `pnpm-lock.yaml` → pnpm · `package-lock.json` → npm · `bun.lockb` → bun |
| `pyproject.toml` / `requirements.txt` | Python | `uv.lock` → uv · `poetry.lock` → poetry · `Pipfile.lock` → pipenv · else pip |
| `go.mod` | Go | go modules |
| `Cargo.toml` | Rust | cargo |
| `composer.json` | PHP | composer |
| `mix.exs` | Elixir | mix |
| `pom.xml` / `build.gradle{,.kts}` | Java/Kotlin | maven / gradle |
| `*.csproj` / `*.sln` | C# | dotnet |
| `deno.json{,c}` | TS | deno |

Runtime versions come from the pinning file, not from what is installed:
`.ruby-version`, `.node-version`, `.nvmrc`, `.tool-versions`, `mise.toml`,
`engines` in `package.json`, `rust-toolchain.toml`. Record the file.

Frameworks: infer only from a declared dependency, never from directory names.
`rails` in the Gemfile is evidence; an `app/` directory is not.

## 3 — Commands, by authority

Highest authority wins. Stop at the first source that yields a command for a key.

1. **CI config** — the only place the commands are proven to run:
   `.github/workflows/*.y*ml`, `.gitlab-ci.yml`, `.circleci/config.yml`,
   `azure-pipelines.yml`, `Jenkinsfile`, `.buildkite/`.
2. **Task runner** — `Makefile` targets, `Justfile`, `Rakefile`, `Taskfile.yml`,
   `scripts` in `package.json`, `[tool.poe]`/`[project.scripts]`.
3. **Binstubs / scripts dir** — `bin/*`, `script/*`. Executable and non-empty only.
4. **Nothing else.** A command that appears only in a README or an agent doc is a
   *candidate to verify*, never a source. If verification fails it is `null`.

Keys to fill: `setup`, `test_all`, `test_one`, `lint`, `lint_fix`, `typecheck`,
`security`, `coverage_gate`, `build`.

`test_one` must carry the `{path}` placeholder. `coverage_gate` may carry
`{base}`. Substitution happens at call time; never bake a branch name in.

Also record `ci.config` (the file) and `ci.required_jobs` (job names that gate
the merge), so `pr-fix` knows which failures matter.

## 4 — Command verification (mandatory)

For each candidate, in this order:

1. Does the executable resolve? For a binstub, is it present and executable?
2. Run the cheapest proving form: `--version`, `--help`, or a dry run.
3. For `test_one`, run it against one real existing test file.
4. Exit 0 → write the command and a `commands_verified` entry. Anything else →
   `null` + append the key to `unknown[]`.

Do not run `setup`, `build`, or a full `test_all` just to verify — resolving the
executable is enough for those. Record which proof was used.

> This recipe exists because of a real failure: a repo's agent doc documented a
> binstub that did not exist in the repo, and every plan that cited it was wrong.

## 5 — Tests

- **Framework**: from the dependency plus the CI invocation. rspec, minitest,
  jest, vitest, pytest, unittest, go test, cargo test, phpunit, exunit, junit,
  xunit.
- **Location**: mirrored (`spec/`, `test/`, `tests/` shadowing the source tree) or
  colocated (`*.test.ts` beside its source). Decide by counting real files, not
  by convention lore.
- **Naming**: the actual pattern — `*_spec.rb`, `*_test.go`, `test_*.py`,
  `*.test.tsx`.
- **Kinds**: the real subdirectories or tags that partition the suite (`model`,
  `service`, `controller`, `system`, `component`, `integration`, `e2e`, `unit`).
  Only kinds with at least one real file.
- **Coverage gate**: a tool that can fail CI on coverage —
  simplecov+undercover, `--coverage` thresholds, codecov with a required status.
  Record the command, and whether it gates the merge.

## 6 — Layers

No fixed vocabulary. Derive them:

1. List directories under each `paths.src` root, depth 1–2.
2. Keep a directory with **≥2 files** and a name that reads as a role
   (`models`, `services`, `controllers`, `components`, `jobs`, `handlers`,
   `repositories`, `usecases`, `views`, `hooks`, `stores`, `middleware`, …).
3. For each kept directory pick **one exemplar**: the file closest to the median
   size, so it shows the shape rather than the extreme.
4. Map the layer to a test kind from recipe 5 when one matches.
5. No directory qualifies → `layers: []`. `plan` falls back to per-file
   discovery. That is a valid outcome, not a failure.

Then write `.sdd/rules/<layer>.md` from `assets/layer-rule-template.md`, stating
only what the exemplar demonstrates.

## 7 — Tracker adapter

`--tracker <adapter>` in the request settles this outright: write it, skip the
table, skip the question.

| Evidence | Adapter |
| --- | --- |
| Linear MCP tools available in session, or `[A-Z]{2,5}-\d+` in recent branch names | `linear` |
| `.github/ISSUE_TEMPLATE/`, `gh` present, issues referenced as `#\d+` in commits | `github-issues` |
| Jira MCP, or `[A-Z]+-\d+` with a Jira URL in the repo | `jira` |
| Shortcut MCP, or `sc-\d+` in recent branch names, or an `app.shortcut.com` URL in the repo | `shortcut` |
| None of the above | `none` |

**A connected MCP outranks a pattern.** `[A-Z]{2,5}-\d+` and `[A-Z]+-\d+` match the
same branch names — `ENG-412` is a valid Linear id and a valid Jira key — so the
regex alone never decides between those two. One tracker's MCP connected and not the
other's is decisive. Both connected, or neither, and the patterns tie: that is a real
ambiguity, not a coin to flip.

Then, by outcome:

| Outcome | Action |
| --- | --- |
| Exactly one row matches | Write it. No question |
| Two or more rows match, and no connected MCP breaks the tie | `"unknown"` → **ask** |
| No row matches, and no tracker MCP is connected | `none`. No question — this repo has no tracker, which is a valid configuration |
| No row matches, but a tracker MCP **is** connected | `"unknown"` → **ask**. The session has a tracker the patterns did not see |

The question, when it happens: state what was found and what it was ambiguous
between, list the candidates plus `none`, and let the user pick. Ask once.

Declined, or "none of these" → write `none`, append `tracker.adapter` to `unknown[]`,
and say in the report that the adapter is undetermined rather than absent. **Never
persist `"unknown"` in `tracker.adapter`** — the consumers read that key as an enum,
and `unknown[]` is where the uncertainty is recorded.

Then record `issue_pattern` and whether the adapter can supply a branch name
(`branch_from_tracker`). `linear` and `shortcut` supply one; `jira` and
`github-issues` do not.

Why this is asked rather than guessed: a wrong adapter yields the wrong branch name
and the wrong issue reference in the PR, and `none` is also the legitimate answer
for a repo with no tracker at all. One question is cheaper than either failure.

## 7b — Tracker create target

Only when recipe 7 landed on something other than `none`, **and** that adapter's
mechanism is reachable in this session (see
`../../handoff/references/tracker-adapters.md` for which mechanism each one uses).
Not reachable → write `create.supported: false` and move on. Ask nothing: a
question about a tracker nobody can reach wastes the user's turn.

Reachable → enumerate, then fill the target:

| Adapter | Enumerate | Required target |
| --- | --- | --- |
| `linear` | teams | `create.team` |
| `shortcut` | groups / workflows | `create.team` |
| `jira` | projects | `create.project` |
| `github-issues` | Projects linked to the repo — see below | neither; `create.project` optional |

- Exactly one result → write it. No question.
- More than one → **ask once**, listing them. This and the § 7 adapter question are
  both conditional; a repo with an obvious tracker and a single team is asked
  neither.
- The user declines to choose → `"unknown"`, appended to `unknown[]`, and
  `create.supported: false`. `task` then writes drafts and says why it stopped
  there.

Then, with the target known:

- `create.initial_state` — the target's first unstarted state, by name. None
  identifiable → `null`.
- `create.default_labels` — `[]` unless the repo's existing issues show a label
  applied to effectively all of them. Never invent a scheme.
- `create.epic_kind` — from the adapter: `parent-issue` (`linear`), `epic`
  (`shortcut`), the project's Epic issue type (`jira`), `task-list`
  (`github-issues`). The adapter's `### Create` section owns the detail.
- `create.supported` — `true` only when the mechanism was reachable **and** every
  required target for that adapter is a real value.
- `create.fields` — where a draft's `Priority` and `Size` are written. Recipe 7c.

`github-issues` projects: a Project is optional, but it is the only place a GitHub
issue can carry a priority or a size. List the ones linked to the repo:

```bash
gh api graphql -F owner=<owner> -F name=<repo> -f query='
  query($owner: String!, $name: String!) {
    repository(owner: $owner, name: $name) {
      projectsV2(first: 20) { nodes { number title closed } }
    }
  }'
```

Open ones only. Exactly one → `create.project` is its title. Several → ask once,
with "none" as an option. None → `null`. A token without the `read:project` scope
fails the call: `create.project` and both `create.fields` keys become `"unknown"`,
appended to `unknown[]`, and the report names `gh auth refresh -s project` as the
fix — the same scope `handoff` needs to write the fields later.

## 7c — Priority and size fields

Only when 7b left `create.supported: true`. Otherwise both keys are `null` for
adapter `none` and `"unknown"` for the rest — never guess a field nobody looked at.

Enumerate the target's fields and match by name, case-insensitive. Write the name
**as the tracker spells it**; `handoff` matches it again at create time.

| Adapter | `fields.priority` | `fields.size` |
| --- | --- | --- |
| `linear` | `priority` — always native | `estimate` when the team's estimate scale is T-shirt; another scale or estimates off → `null` |
| `github-issues` | the `create.project`'s single-select field named `Priority` (`gh project field-list <n> --owner <owner> --format json`); no project or no such field → `null` | same, field named `Size` |
| `jira` | `priority` when the project's create metadata offers it; else `null` | a field named `Size` or `T-Shirt Size` in the create metadata; else `null` |
| `shortcut` | the `Priority` custom field when the workspace has it enabled; else `null` | a custom field named `Size`; else `null`. Story points never count |

Then check the options. A field whose options cannot carry the scale — a
`Priority` with only two options, a `Size` without `XS`–`XL` — is still written,
and the report names the values that will not map. `handoff` already leaves an
unmatched option unset and says so; `init` only says it first.

A field under another name — `Prioridad`, `Estimate` as a T-shirt select — is not
matched automatically. It surfaces as `null`, and the report says to set the name
by hand in `config.json`. Refresh keeps a hand-set name that still exists in the
tracker; one that no longer does is reported and asked, like a hand-edited file.

## 8 — Graph

Two independent checks, both required for `graph` to be non-null:

```bash
command -v graphify
test -f graphify-out/graph.json
```

CLI + graph → fill `graph` with

```json
{
  "tool": "graphify",
  "out": "graphify-out",
  "query": "graphify query \"{q}\"",
  "path": "graphify path \"{a}\" \"{b}\"",
  "explain": "graphify explain \"{node}\"",
  "update": "graphify update ."
}
```

Read-only commands only. `graphify` has flags beyond these (`--dfs`, `--budget`,
rebuild modes); they do not go in the config — `plan` needs the three read
commands, not the tool's whole surface.
CLI only → `graph: null`, and note in the report that `graphify .` would build one
(state the cost; do not run it).
Neither → `graph: null`, and no skill mentions a graph again.

Also check whether the graph output is excluded (`git check-ignore -q
graphify-out`, true whether the rule lives in `.gitignore` or `.git/info/exclude`).
If it is, set `worktree.share_graph: true` — a fresh worktree will have no graph
of its own.
Uncovered → `graphify-out/` is a local build artifact, never a team contract;
append it to `.git/info/exclude` (never `.gitignore` — same reasoning as
`sdd_tracking: local`), then set `worktree.share_graph: true`.

## 9 — Branch and commit conventions

```bash
git log --format=%s -50
git for-each-ref --format='%(refname:short)' refs/remotes/origin --count=30
```

Conventional Commits (`feat:`, `fix:`, `chore(scope):`) in a clear majority →
record it. Branch prefixes (`feature/`, `fix/`, `<user>/<issue>-<slug>`) →
record the dominant shape. A 50/50 split is not a convention: write `unknown`.

## 10 — Agent docs

Find `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/*`, `.windsurf/rules/*`,
`.github/copilot-instructions.md`, `.clinerules/*`, `.kiro/steering/*`. List them
in `docs.agent_docs`.

Resolve symlinks: two paths pointing at one file are one doc, and loading both is
loading the same file twice. This is also why `CLAUDE.md` is symlinked to
`AGENTS.md` rather than copied when both are absent.

Ignore any `<!-- shipit:contract -->` block you find: shipit wrote it on a previous
run. It is a pointer, not a source. A doc containing nothing else is not an agent
doc and does not go into `docs.agent_docs`.

Then **subtract**. Anything those docs already state does not go into `.sdd/*.md`.
What remains is what shipit records. Where a doc contradicts the repo, the repo
wins and the contradiction is reported.

## 11 — Companions

Report-only. See `skills/doctor/references/tiers.md` for the tier definitions and
the exact commands. Fill `companions` with `present` / `absent` per entry.

## 12 — Worktree defaults

- `enabled: false`. **Always false at init.** Worktrees are opt-in: the founder
  flips it when they actually want parallel tasks, once `worktree.setup` and the
  repo's local config are known to survive a fresh checkout. Defaulting to true
  buys friction on every first plan for a feature most repos never need.
- `root: "../worktrees/<repo-name>"`, repo name from the toplevel basename.
- `base`: the default branch from recipe 1.
- `link: []` — **always empty at init.** Only the user adds paths here, knowing
  it symlinks untracked files (often secrets) into a directory no `.gitignore`
  covers.
- `share_graph`: from recipe 8.
- `setup`: `commands.setup` if it verified green, else `null`.

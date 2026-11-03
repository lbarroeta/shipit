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
a readable existing tracker issue, local `main` with a remote `main` upstream, and
the ponytail plugin for its review stage.
Report these when checking readiness for `run`; they do not block the individual
planning/implementation skills. Never install or substitute them silently.

## Tier 1 — recommended

Delivery reaches GitHub and your tracker through these, and review runs on
ponytail. Planning, drafting a ticket, and implementing do not need them.

ponytail's session-wide mode stays on once installed. That is fine: inside every
shipit skill, `references/lean-ladder.md` § Where this overrides ponytail wins —
the repo's own tests, full reports. Its vendored ladder, review tags and debt
markers keep working with or without the plugin.

The three tracker rows are not checked by `scripts/companions.sh` — it checks
executables, and a tracker is reached through an MCP server or `gh`. They come from
`.shipit/config.json` plus what is connected in the session.

| Item | Check | Fix | Without it |
| --- | --- | --- | --- |
| `gh` | `command -v gh` | `brew install gh`, or see cli.github.com | `code-handoff` cannot open or update a PR |
| `gh` auth | `gh auth status` | `gh auth login` | same as above |
| ponytail | `claude plugin list` names it | `claude plugin marketplace add DietrichGebert/ponytail` then `claude plugin install ponytail@ponytail` | `code-review` and `run`'s review stage cannot run: `ponytail-review` is their review engine. Planning, implementing and delivering standalone are unaffected |
| tracker | adapter from `.shipit/config.json`, plus whether its mechanism is reachable this session | run `/shipit:sync` once the tracker is reachable | no tracker-supplied branch name — `.shipit/conventions.md` decides instead. Adapter `none` is a valid configuration, not a gap |
| tracker create | `tracker.create.supported` plus the target it names | run `/shipit:sync` with the tracker connected | the draft names no target to paste into. `task-create` still writes it; authorized handoff can publish when `issue_create` is allowed. With adapter `none` this is `n/a`, not a gap |
| tracker fields | `tracker.create.fields.priority` and `.size`, each read on its own | `"unknown"` → run `/shipit:sync` with the tracker connected; on `github-issues` add `gh auth refresh -s project` when `unknown[]` shows the scope was the reason. `null` → verified absent: link a Project that has the field (`github-issues`), or set the name of a renamed field in `config.json` | `null`: a created issue does not carry that value in the tracker's own field; the draft still does. `"unknown"`: unverified, not missing — `code-handoff` tries the adapter's default name and may succeed. Adapter `none` → `n/a` |

## Tier 2 — accelerators

shipit produces the same answers without these. It spends more tokens doing it.

| Item | Check | Fix | Cost of the fix |
| --- | --- | --- | --- |
| graphify CLI | `command -v graphify` | `uv tool install graphifyy`, or `pipx install graphifyy` | fast, free. Needs `uv` or `pipx` already present. `init` offers it after an alert and asks first |
| graphify graph | `test -f <graph.out>/graph.json` | `graphify update .` in the main checkout | code only: no LLM, no tokens. `init` runs it. A semantic build (`graphify .`) costs minutes and tokens and is never run automatically |
| caveman | `claude plugin list` names it | `claude plugin marketplace add JuliusBrussee/caveman` then `claude plugin install caveman@caveman` | plugin install, ships hooks |
| Context7 | MCP tools `resolve-library-id` / `query-docs` listed in the session, else `command -v ctx7` and `ctx7 whoami` printing `Logged in` | `claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp --header "Authorization: Bearer <key>"`; Codex: `[mcp_servers.context7]` in `~/.codex/config.toml`. Or `npm install -g ctx7` then `ctx7 login` | user-scope MCP config, or a global npm package. Never run by `--fix` |

Notes:

- Having the CLI without a graph changes nothing. They are two separate gaps.
- Inside a worktree the graph is normally a symlink to the main checkout's — that is
  correct, not stale. `worktree.share_graph` controls it.
- Context7 changes answers, not only tokens; `references/docs-lookup.md` owns when
  it is used. The MCP is a session fact the script cannot see, and its key cannot be
  read, so a connected MCP is reported `ok (login not verifiable)`.
- caveman compresses prose. shipit exempts non-developer QA steps from compression
  either way, so installing it never degrades the deliverable.

## Contract checks

Not dependencies, but `doctor` reports them in the same pass because they break the
same way.

| Check | Meaning |
| --- | --- |
| `.shipit/config.json` present | Absent → `code-plan` and `code-implement` refuse. Fix: `/shipit:init` |
| no legacy `.sdd/` | Present → a pre-0.15.0 contract the current skills do not read. Fix: `/shipit:init` migrates it |
| pointer | The `shipit:contract` block exists once in `docs.pointer`; a `CLAUDE.local.md` pointer is missing in this checkout → `/shipit:init` recreates it |
| `config.json` parses | Corrupt → report the parse error; recover config without resetting preferences, then `/shipit:sync` |
| `unknown[]` empty | Non-empty → those verification steps do not exist. Named in every report |
| `test_one` has `{path}` | Missing → the red-green loop is unavailable and required tests become a validation gap (the full suite never runs locally; CI owns it) |
| `worktree.link[]` empty | Non-empty → untracked files, usually secrets, are symlinked into worktrees. Report each by name |
| Context freshness | Run `<plugin>/skills/sync/scripts/context_state.py --repo <repo> inspect` read-only when available. Missing baseline → unknown; source/contract drift → `/shipit:sync`. Hashes do not prove remote tracker freshness. |

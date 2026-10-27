# Templates

A template is a repository that a new project's code is generated from. Owned by
this file; `init` points here instead of restating it. shipit knows only where a
template lives and which commit was chosen; what it generates, its options and how
it is set up stay in the template's own repository.

## Registry

The user's own file, `~/.config/shipit/templates.json`. shipit reads it and never
writes it.

```json
{
  "rails": { "repo": "KodimTech/rails-boilerplate" }
}
```

| Key | Type | Notes |
| --- | --- | --- |
| `<name>` | object | How the user calls the template; becomes `template.name` |
| `<name>.repo` | string | `<owner>/<repo>` on GitHub, or any URL `git` can clone |

Absent or unparsable registry → say so, show the example above, and accept a repo
typed in the chat for this run. A malformed entry is skipped and named.

## Choice

Asked by `init` only when the repo is empty — no manifest matches
`skills/init/references/detection-recipes.md § 2` — and `.shipit/config.json`
records no `template` key. One question: the registry's names plus `none`. A
recorded answer, `null` included, is reused and never re-asked.

Pin the commit at choice time, so every later step reads the same version that
generates the code:

```sh
git ls-remote <url> HEAD   # <owner>/<repo> → https://github.com/<owner>/<repo>.git
```

Unreachable → write `commit: "unknown"`, append `template.commit` to `unknown[]`,
and say the user may need `! gh auth login` for a private repo. Never guess a
commit.

## Config

`template` in `.shipit/config.json`:

| Value | Means |
| --- | --- |
| `{name, repo, commit}` | The project is generated from `repo` at `commit` |
| `null` | No template: the repo had code already, or the user chose `none` |
| absent | Config predates the key; read as `null` |

Only `init` writes it, and `sync` preserves it. Changing the template is a
decision: the user edits the key, or deletes it and re-runs `init` on the still
empty repo.

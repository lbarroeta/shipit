Set up the shipit contract for this repository.

This is a Rails app. Repository state:

- `AGENTS.md` exists. It is a short index written by the team that links
  `docs/code/conventions.md` and `docs/architecture.md`. There is no `CLAUDE.md`.
- `docs/code/conventions.md` was written by the team. It covers service objects
  (`app/services/`, each returns a `Result`) and thin controllers. It says nothing
  about branch names, commit subjects or test shape.
- Neither `.shipit/` nor `.sdd/` exists.
- `bin/rspec` and `bin/rubocop` exist, and CI runs both.
- `git log --format=%s -50` shows Conventional Commits in 46 of 50 subjects.
- `uv` is installed. The `graphify` CLI is not.

Produce the contract.

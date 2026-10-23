Run shipit init on this repo.

Repository state:

- No `docs/shipit/` and no `.sdd/` yet. This is a first `init`.
- `git branch --sort=-committerdate | head` shows `ENG-412-retry-webhooks`,
  `ENG-407-invoice-pdf`, `ENG-399-audit-log`.
- `docs/engineering.md` contains the line
  `See the ticket at https://acme.atlassian.net/browse/ENG-399 for context.`
- No `.github/ISSUE_TEMPLATE/` directory, and no issue references of the form `#123`
  in recent commits.
- **No tracker MCP is connected in this session** — not Linear, not Jira, not
  Shortcut. `gh` is installed and authenticated.
- Everything else about the repo is unremarkable: a Node service with a `package.json`,
  a lockfile, a test script that passes, and a CI config.

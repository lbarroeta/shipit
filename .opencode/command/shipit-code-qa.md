---
description: Test a reviewed shipit change black-box with Playwright MCP against its acceptance criteria
---

Load the shipit `code-qa` skill and run it.

- Plugin root: `$SHIPIT_ROOT` if set, else `~/.config/opencode/plugins/shipit`.
- Read `<root>/skills/code-qa/SKILL.md` and follow it exactly. Paths it writes
  relative to itself resolve under `<root>`.
- It needs the Playwright MCP server configured for OpenCode and `acceptance`
  enabled in `.shipit/config.json`.
- Command names are flat here: `/shipit:code-qa` is `/shipit-code-qa`.

Request: $ARGUMENTS

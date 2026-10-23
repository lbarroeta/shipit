# Agent instructions

`CLAUDE.md` is a symlink to this file. Keep this entry point short; put technical
rules and explanations in `docs/` and link to their owning document.

## Read only what the task needs

<One row per topic the doc inventory found outside the shipit contract. No such
docs → delete this section.>

| Task | Required context |
| --- | --- |
| <task> | [<document title>](<docs/path.md>) |

<!-- shipit:contract -->
## Repository contract

[Shipit configuration](.shipit/config.json) defines verified commands, layers and
tracker. Read [stack](.shipit/stack.md), [conventions](.shipit/conventions.md) and
the applicable [layer rule](.shipit/rules/) before writing code. Ask about any
relevant entry in `unknown[]`; do not guess.
<!-- /shipit:contract -->

## Keep context reliable

- Verify implementation claims against source, configuration and schema.
- If instructions conflict or a required decision is unresolved, ask the user.
- Update the owning document when a decision changes; avoid duplicate rules.

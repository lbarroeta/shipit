Refresh the shipit contract for this repository.

`.sdd/` was written by `/shipit:init` and later `/shipit:design-system`. Since
then nobody edited `.sdd/rules/components.md` by hand, except that
`design-system` appended its `<!-- shipit:design -->` block at the end of it.
`.sdd/design-system.md` is `Status: approved`, and its Decisions table has a row
`D3 | Primary color stays #0F766E | user | 2026-09-30 | approved` that someone
edited by hand last week. `AGENTS.md` holds the `<!-- shipit:contract -->` block
followed by a `<!-- shipit:design -->` block. Detection would now produce a
slightly different exemplar for `components`.

Plan this ticket with shipit: "Add a nightly job that deletes export files older
than 30 days from `storage/exports/`."

The repo has `.sdd/` with layers `jobs` (`app/jobs/`) and `components`
(`app/frontend/components/`). `.sdd/rules/components.md` ends with a
`<!-- shipit:design -->` block, and `.sdd/design-system.md` plus
`.sdd/rules/design.md` exist. The job has no UI.

After the plan, list every `.sdd/` file you read.

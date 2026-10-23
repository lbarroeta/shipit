Plan this ticket with shipit: "Add a nightly job that deletes export files older
than 30 days from `storage/exports/`."

The repo has a shipit contract with layers `jobs` (`app/jobs/`) and `components`
(`app/frontend/components/`). `docs/code/rules/components.md` ends with a
`<!-- shipit:design -->` block, and `docs/design-system/contract.md` plus
`docs/code/rules/design.md` exist. The job has no UI.

After the plan, list every contract file you read.

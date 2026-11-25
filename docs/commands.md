# Commands

Every shipit command, what it does and when to use it.
The [flow diagram](diagrams/shipit-flow.png) shows how they connect.

| Command | What it does | When |
| --- | --- | --- |
| `/shipit:init` | Reads the repo and writes the `.shipit/` contract | Once per repo; safe to re-run |
| `/shipit:doctor` | Checks git, `gh`, tracker and accelerators; prints each fix and its cost | Before the first run, or when something is missing |
| `/shipit:sync` | Reconciles the contract and docs with the code; `--upgrade` migrates config | Before planning, after implementing, after updating shipit |
| `/shipit:product-discovery` | Interviews you and writes the PRD | Once per product |
| `/shipit:product-mvp-cut` | Decides which PRD stories ship first | After the PRD |
| `/shipit:design-system` | Interviews you and records colors, components and UI rules | Once per repo with a UI |
| `/shipit:task-create` | Turns a need into a ticket, or an epic with children | No ticket exists yet |
| `/shipit:task-import` | Reads one or several of a client's Jira, Shortcut or GitHub Issues cards and runs `task-create` on each, in plain human wording with attachments linked, for your tracker and project | The work exists as a card in the client's tracker |
| `/shipit:task-next` | Recommends the next ticket to take, and why | Choosing what to work on |
| `/shipit:code-plan` | Writes the implementation plan for a ticket | Before coding |
| `/shipit:code-implement` | Executes the plan, runs the checks, prepares QA steps | After the plan |
| `/shipit:code-review` | Reviews the change with `ponytail-review`, the plan and the repo's rules; read-only | After implementing |
| `/shipit:task-handoff` | Creates the draft's issues in the tracker (needs `issue_create`) | A ticket draft is approved |
| `/shipit:code-handoff` | Branch, commit, push, PR, tracker status | Work is ready for review |
| `/shipit:qa` | Runs each acceptance criterion in a hidden browser, one video each, and proposes pass/fail for you to confirm, then posts the videos on the PR; your screen stays yours | The change is ready for QA |
| `/shipit:pr-fix` | Triages review comments (`--comments`), red CI (`--ci`) and merge conflicts — what applies, what does not and why — then fixes what you approve | The PR has feedback |
| `/shipit:run` | sync → plan → implement → review → sync → handoff for an existing ticket | You have a ticket and want it done |
| `/shipit:status` | Lists in-flight tasks with their PR and tracker state | Anytime; `--prune` removes merged worktrees |
| `/shipit:retro` | Proposes fixes to the agent's environment (checks, rules, commands, pointers) as exact patches; never product code | After a run or session that went badly or cost too much |

In OpenCode the commands are `/shipit-<name>`, and `run` is not available.

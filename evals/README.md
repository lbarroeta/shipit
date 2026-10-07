# Evals

Cases for `claude plugin eval`. Each directory is one case: a `prompt.md` and one or
more rubrics in `graders/`.

```bash
claude plugin eval shipit                      # all cases, with a no-plugin baseline arm
claude plugin eval shipit --case init-*        # filter
claude plugin eval shipit --report report.html # scored HTML report
```

Every grader carries `type: llm` frontmatter; without it the CLI rejects the case
with `graders: Required`. Two grants are needed for a meaningful run:

```bash
claude plugin eval . --allow-tools Write "Read(/<absolute plugin path>/**)"
```

`Write` lets `task` and `init` write their artifacts. The `Read` grant lets the agent
open a skill's `references/` and `assets/` — without it the sandbox denies them and
the case measures `SKILL.md` alone. Granting `Bash` (needed for `init` to verify
commands) fails to start when `~/.ssh` contains a symbolic link.

Known limits of the `prompt.md` form: it cannot stage files (`scaffold_script` is
`case.yaml`-only), so the repository state each prompt describes does not exist on
disk; and the judge sees the agent's final message, so a run that summarises
instead of printing its artifact is graded on the summary.

The baseline arm is what makes a score meaningful: it runs the same prompt with the
plugin disabled, so the number reported is a delta, not an absolute.

> **Format caveat.** The CLI accepts `evals/**/case.yaml` **or**
> `evals/**/prompt.md` + `graders/*.md`. These cases use the second form because its
> shape is self-evident from the files. The exact `case.yaml` keys were not verified
> against a running eval, so nothing here depends on them. If a run rejects this
> layout, that is the first thing to correct.

## What each case guards

| Case | Guards against |
| --- | --- |
| `init-ruby` | Writing a command that does not exist in the repo; clobbering an existing `CLAUDE.md` with the contract pointer |
| `init-js` | Leaking one ecosystem's conventions into another; writing a contract nothing points at |
| `plan-collision` | Two parallel worktrees silently planning the same files |
| `doctor-missing` | Reporting an optional tool as a failure, or installing without consent |
| `init-ambiguous-tracker` | Guessing a tracker from a branch pattern two adapters share, or writing `none` in a way nothing downstream can distinguish from a real absence |
| `task-epic-split` | A chain of tickets where only the last one is worth merging; a ticket that does `plan`'s job |
| `task-no-tracker` | Creating an issue somewhere the repo did not configure, and calling `none` a gap |
| `run-dirty-main` | Switching main or adopting uncommitted user changes before an orchestrated task |
| `run-resume-qa` | Restarting from main, duplicating delivery, or calling automated checks human QA approval |
| `run-model-unavailable` | Role-playing subagents or silently substituting unavailable stage models |
| `design-incomplete-interview` | Answering the design interview on the user's behalf; a contract marked approved that nobody confirmed; an inconsistency promoted to a rule |
| `design-refresh-preserves` | An `init` refresh wiping the design contract, its layer-rule blocks, or a human design decision |
| `plan-backend-no-design` | Backend plans paying for visual context they never use |

Every case targets a rule that, when broken, produces confidently wrong output
rather than an error. Those are the failures worth paying for a grader to catch.

## Adding a case

Pick a hard rule from a SKILL.md whose violation would be silent. Write the prompt
that tempts the model to break it, and a grader that only passes when it did not.

A case that merely checks the skill produced output is not worth its run cost.

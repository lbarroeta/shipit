# Coordinator contracts and recovery

## Task snapshot

Resolve ID/URL through the configured tracker before touching Git. Write a temporary
JSON file outside the checkout with `key`, `id`, `url`, `title`, `description` and
`acceptance_criteria` (non-empty list). `key` is canonical and workspace-qualified:
e.g. `github-issues:KodimTech/repo:412` or `linear:<workspace>:<immutable-issue-id>`.
ID and URL forms of the same issue must produce the same key. Keep raw tracker
description and criteria byte-stable for scope-change detection; extract criteria
without inventing or rephrasing them. Criteria in tracker checklists/custom fields
also belong in this list. No timestamps or ephemeral fields in canonical fields.

## Local helper

Python 3.10+, standard library only. Invoke using absolute paths. Argument values
are data: properly quote them; never interpolate card text into shell code.
Example commands (replace values, not arbitrary shell expressions):

```sh
python3 /plugin/skills/run/scripts/run_state.py --repo /repo routes --provider openai
python3 /plugin/skills/run/scripts/run_state.py --repo /repo begin --provider openai --task-file /tmp/task.json --branch codex/eng-412-invoices
python3 /plugin/skills/run/scripts/run_state.py --repo /repo status --issue-key 'linear:workspace:issue-id'
python3 /plugin/skills/run/scripts/run_state.py --repo /repo checkpoint --issue-key 'linear:workspace:issue-id' --owner OWNER --stage plan --result-file /run-dir/planner-result.json
python3 /plugin/skills/run/scripts/run_state.py --repo /repo pause --issue-key 'linear:workspace:issue-id' --owner OWNER --reason 'Waiting for human QA'
```

`begin` returns `owner`, `state_path`, `repo`, `branch`, `base_sha`, `routes`,
`stage` and `mode` (`new`/`resume`). Store artifacts and results in the parent of
`state_path`. State/locks live under the Git common directory's `shipit/`, excluded
from commits without editing gitignore or the repo contract. Issue locks are shared
across linked worktrees; checkout locks also prevent two different issues editing
the same checkout. Only the owning coordinator can checkpoint or pause.

Stages: `preparing → plan → implement → handoff → qa → done`. `pause` preserves
stage and releases locks. A later `begin` reacquires them. Resume requires the same
checkout and unchanged source/artifact hashes; it restores the saved branch only
from a clean tree and never resets to main. Display saved QA/done results through
`status` without beginning a new execution. A failed/incomplete child can be saved
with `pause --result-file PATH` after checking its report and full owned-file
manifest; resume verifies those hashes before passing ownership to the next child.
If preparation was interrupted after syncing main, `base_sha` preserves the
original base for finishing branch creation. A checkpoint is a coordinator-verified
transition, not proof by itself that a subprocess ran.

To recover a crashed run, inspect `status` and its `owner`, establish that its
children have stopped, then use `pause` with that owner before `begin` again. Never
delete another active lock. Keep tracker credentials and environment secrets out
of snapshots, result files and journals.

## Delegation message

Every child receives: stage; absolute repo and task branch; absolute assigned
SKILL.md path (resolve its references relative to that path); saved task/plan/report
paths; run owner/state path; model/effort pair; user-authorized scope; run-owned
paths; result/artifact destination; allowed effects; and the concrete outcome it
must return. Use unique report/result names for each dispatch or repair so saved
reports remain available. Do not flood children with the entire conversation.

Planner: write the plan in `<paths.plans>`, use `--no-worktree`, no product code.
Builder: execute with `--defer-handoff`; the explicit run request authorizes
execution within the fetched criteria after the coordinator's contract check.
Keep plan corrections in the planner, not the builder. Delivery: `implementation`
mode, immutable builder report, journal path; no product or plan edits.
Each child saves a result JSON and returns its path plus a short summary:

```json
{
  "status": "completed",
  "artifact": "/absolute/path/to/stage-artifact.md",
  "agent_id": "native-runtime-agent-id",
  "requested": {"model": "gpt-6.1-sol", "effort": "high"},
  "effective": {"model": null, "effort": null},
  "blockers": []
}
```

`effective` is populated by the coordinator only from runtime metadata; children
leave unknown values null. The planner must return empty `blockers` for completion.
Builder adds `validation`: exact executed `{ "command": "...", "exit_code": 0 }`
entries, plus `files`: repo-relative paths exactly matching the tracked diff and
non-ignored untracked files. Exclude local-only `.sdd` artifacts from that manifest;
record any skipped checks with reasons in the report.
Delivery adds `delivery_status` (`completed`, `partial`, `blocked`, `skipped`) and
actual effect proofs. Use `blocked`/`failed` and a concrete reason when unable to
finish; never emit `completed` with pending required work.

Coordinator verifies artifact contents and evidence, then runs `checkpoint` with
the stage and result file. Keep the plan and builder report immutable after their
checkpoints. To correct a plan gap after discussing it with the planner, use
`replan --issue-key KEY --owner OWNER --reason 'Concrete contract gap'`. This
archives the prior checkpoint references and invalidates downstream stages; then
dispatch the planner and checkpoint the replacement. Do not edit state hashes to
bypass checks. For a changed/missing artifact or changed issue source that blocks
`begin`, use `begin --replan-reason 'Concrete approved correction'` only after
reconciliation. Changed business/security/data scope requires the user's explicit
decision first. This archives checkpoints, updates the task snapshot and resumes
at plan on the existing branch. Never apply this flag automatically to bypass a
scope mismatch. Dirty files still need ownership verification; replanning does not
grant ownership of user edits.

## Delivery reconciliation

Before each allowed effect, delivery reads the current repo/remote/PR state and
its journal. Record the exact result immediately after each successful action in
`delivery.json` under the run directory: branch, commit SHA and manifest, upstream
push, PR URL/body hash, and any permitted tracker effect IDs. Use atomic writes.
The `validated_head` checkpoint and the builder's manifest identify the proposed
change. Before dispatch run `verify --issue-key KEY --owner OWNER`: it checks saved
artifacts, validated file contents and unexpected diff paths. A changed HEAD may
represent interrupted delivery; the delivery agent must reconcile the exact commit
before continuing. Unexpected content returns to validation.

A retry skips effects confirmed in both journal and actual state. If a crash
occurred after an effect but before journaling, reconcile from the branch log,
commit manifest/content, remote branch, existing branch PR and tracker history.
An already committed manifest is checked against that exact commit, not falsely
required to appear as an uncommitted diff. If ownership/content cannot be proven,
pause and report ambiguity. Never make empty commits, duplicate PRs/comments or
claim a skipped capability completed. Partial results remain at handoff, and the
next delivery agent reads the journal before doing anything.

In a coordinated run, save the handoff report separately in the run directory;
do not append to the checkpointed builder artifact. Link both reports in final
delivery. Standalone `implement` retains its existing append behavior.

## Human QA

After handoff, wait for the user's actual test results; release locks while waiting.
On the next invocation reacquire through `begin`, then record:

```sh
python3 /plugin/skills/run/scripts/run_state.py --repo /repo qa --issue-key 'linear:workspace:issue-id' --owner OWNER --outcome fail --feedback 'Step 3: expected download, got error'
```

`pass` moves to done. `blocked` stays at qa. `fail` keeps the plan/branch, records
feedback and invalidates builder/delivery checkpoints, returning to implement.
Do not mark pass from automated checks or another agent's opinion. Give the builder
the recorded feedback; keep any corrective work inside the original criteria.

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
`stage` and `mode` (`new`/`resume`). At `qa`/`done`, `begin`, `status` and the
`handoff` checkpoint also return `qa_guide`: `report` (the checkpointed final
delivery report) and `steps` (its `## QA…` sections verbatim, or null). Store artifacts and results in the parent of
`state_path`. State/locks live under the Git common directory's `shipit/`, excluded
from commits without editing gitignore or the repo contract. Issue locks are shared
across linked worktrees; checkout locks also prevent two different issues editing
the same checkout. Only the owning coordinator can checkpoint or pause.

Stages: `preparing → sync_before → plan → implement → sync_after → handoff → qa → done`. `pause` preserves
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

## Planning status

`../../code-plan/SKILL.md § Planning status` owns the shared transition rule. The
planner applies it at preflight, before worktree setup or discovery, after the
coordinator has prepared Git and verified all stage routes. The coordinator does
not perform a second write. Verify the planner's reported transition or preserved
state before checkpointing; a failed transition blocks the stage and requires
pausing to release the locks. Read-only resolution, Git preparation and resumes
at implement/sync_after/handoff/qa/done do not perform this transition.

## Delegation message

Every child receives: stage; absolute repo and task branch; absolute assigned
SKILL.md path (resolve its references relative to that path); saved task/plan/report
paths; run owner/state path; model/effort pair; user-authorized scope; run-owned
paths; result/artifact destination; allowed effects; and the concrete outcome it
must return. Also pass what earlier stages already verified, inline: the planner
gets the sync report's stack/command evidence and context status; the builder gets
the plan's `Files`, `Sequence` and `Tests` sections and the same command evidence.
A child reads source only for the files those sections name and does not
rediscover the stack, the commands or the graph. Use unique report/result names
for each dispatch or repair so saved
reports remain available. Do not flood children with the entire conversation.

Synchronizer: execute `shipit:sync` in the supplied phase, no product code or
external writes. Before planning return context evidence and owned paths. After
implementation return a separate cumulative delivery report; preserve the builder
artifact. Both checkpoints use route `sync`.
Planner: write the plan in `<paths.plans>`, use `--no-worktree`, no product code.
Builder: execute with `--defer-handoff`; the explicit run request authorizes
execution within the fetched criteria after the coordinator's contract check.
Keep plan corrections in the planner, not the builder. Delivery: `implementation`
mode, immutable post-sync delivery report plus builder evidence, journal path; no product or plan edits.
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
leave unknown values null. The planner and both sync stages must return empty `blockers` for completion.
Builder adds `validation`: exact executed `{ "command": "...", "exit_code": 0 }`
entries, plus `files`: repo-relative paths exactly matching the tracked diff and
non-ignored untracked files. Retain non-ignored generated plans here for ownership
validation, but omit them from the report's `Files Changed` delivery manifest. Record any skipped checks
with reasons in the report.
Sync adds `context_status` (`current` or `updated`), `requires_revalidation: false`,
`validation` (non-empty successful executed context checks), and `files` (the full
non-ignored run-owned manifest, not just sync edits). `unknown[]` entries for
irrelevant/missing optional capabilities may remain; unresolved relevant conflicts
may not. A partial/blocked result never checkpoints. After-implementation checks
include newly required checks; retain builder validation only with unchanged
inputs and cite it in the final delivery report. The coordinator verifies that
product code did not change during sync (product-context doc edits are context) and no required check was omitted.
Delivery adds `delivery_status` (`completed`, `partial`, `blocked`, `skipped`) and
actual effect proofs. Use `blocked`/`failed` and a concrete reason when unable to
finish; never emit `completed` with pending required work.

Coordinator verifies artifact contents and evidence, then runs `checkpoint` with
the stage and result file. Keep the plan and builder report immutable after their
checkpoints. To correct a plan gap after discussing it with the planner, use
`replan --issue-key KEY --owner OWNER --reason 'Concrete contract gap'`.
If the failed child made additional owned edits, supply its verified blocked result
with `--result-file PATH`; this captures ownership before invalidating checkpoints. This
archives the prior checkpoint references and invalidates downstream stages; then
dispatch pre-plan sync, then the planner and checkpoint the replacement. Do not edit state hashes to
bypass checks. For a changed/missing artifact or changed issue source that blocks
`begin`, use `begin --replan-reason 'Concrete approved correction'` only after
reconciliation. Changed business/security/data scope requires the user's explicit
decision first. This archives checkpoints, updates the task snapshot and resumes
at sync_before on the existing branch. Never apply this flag automatically to bypass a
scope mismatch. Dirty files still need ownership verification; replanning does not
grant ownership of user edits.

## Delivery reconciliation

Before each allowed effect, delivery reads the current repo/remote/PR state and
its journal. Record the exact result immediately after each successful action in
`delivery.json` under the run directory: branch, commit SHA and manifest, upstream
push, PR URL/body hash, and any permitted tracker effect IDs. Use atomic writes.
The final sync `validated_head` checkpoint and cumulative manifest identify the proposed
change. Before dispatch run `verify --issue-key KEY --owner OWNER`: it checks saved
artifacts, validated file contents and unexpected diff paths. A changed HEAD may
represent interrupted delivery; the delivery agent must reconcile the exact commit
before continuing. Unexpected content returns to validation.

A retry skips effects confirmed in both journal and actual state. If a crash
occurred after an effect but before journaling, reconcile from the branch log,
commit manifest/content, remote branch, existing branch PR and tracker history.
The helper saves the proposed delivery tree using a temporary index based on
`validated_head`, including new files, deletions, modes and symlinks without staging
the real index. `delivery_files` excludes current and archived generated plans;
their hashes remain protected by `validated_files` and artifact checkpoints.
Already tracked plans retain their base version in the delivery tree; local edits
stay on disk. A changed HEAD must descend from `validated_head` and its entire
tree must match that saved
tree; matching file hashes alone cannot authorize unrelated committed changes.
State version 2 requires both sync checkpoints. Active version-1 runs cannot
silently skip them: preserve snapshots/journal, reconcile any already-published
effects, then explicitly `begin --replan-reason ...` on the same branch. Saved
qa/done results remain readable; a legacy QA failure goes through pre-plan sync.
Do not invalidate delivered work automatically or duplicate its effects.
Older checkpoints without this tree snapshot must return to implementation.
An older checkpoint whose `validated_files` includes generated plans but lacks
`delivery_files` must also return to the builder for a new checkpoint; never edit
saved state or commit plans to satisfy the old tree.
An already committed manifest is checked against that exact commit, not falsely
required to appear as an uncommitted diff. If ownership/content cannot be proven,
pause and report ambiguity. Never make empty commits, duplicate PRs/comments or
claim a skipped capability completed. Partial results remain at handoff, and the
next delivery agent reads the journal before doing anything.

In a coordinated run, save the handoff report separately in the run directory;
do not append to the checkpointed builder artifact. Link both reports in final
delivery. Standalone code-implement returns its report for sync and explicit handoff; it
does not dispatch sync or delivery internally.

## Human QA

After handoff, present `qa_guide.steps` verbatim with the PR link, then wait for
the user's actual test results; release locks while waiting. The QA guide already
exists in the final delivery report: never dispatch a stage to produce it again.
On the next invocation reacquire through `begin`, then record:

```sh
python3 /plugin/skills/run/scripts/run_state.py --repo /repo qa --issue-key 'linear:workspace:issue-id' --owner OWNER --outcome fail --feedback 'Step 3: expected download, got error'
```

`pass` moves to done. `blocked` stays at qa. `fail` keeps the plan/branch, records
feedback and invalidates builder/final-sync/delivery checkpoints, returning to implement.
After a product validation failure discovered by sync, save its blocked result
with full owned manifest, then run `repair --issue-key KEY --owner OWNER
--reason 'Exact failed check' --result-file /run-dir/blocked-sync.json`. This archives
the old implementation evidence, retains plan/pre-sync, and returns to implement.
The builder receives sync-owned doc/config changes and must revalidate before a
new sync_after checkpoint. `replan` instead reruns sync_before and planning.
Do not mark pass from automated checks or another agent's opinion. Give the builder
the recorded feedback; keep any corrective work inside the original criteria.

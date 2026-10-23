# Planning consistency across models

These are filesystem-backed comparative fixtures, separate from the legacy
`prompt.md` eval cases. They measure preservation of behavior, essential
decisions, and scope. They do not require matching prose, file counts, helper
names, or plan length. Multiple implementations can meet the same contract.

## Prepare and run

Python 3 and Git are the only harness dependencies. From the plugin root:

```bash
python3 evals/plan-consistency/prepare.py prepare localized /tmp/shipit-code-plan-sol-1
python3 evals/plan-consistency/prepare.py prepare localized /tmp/shipit-code-plan-opus-1
```

The destination must not exist. Each gets:

- `repo/`: committed fixture, `docs/shipit/` contract, request, code, docs and passing baseline tests.
  `localized` also has the same intentional user-owned dirty edit in both copies.
- `plugin/`: frozen plan skill, template and required reference dependencies.
- `prompt.md`: identical launch instruction; launch from the destination directory.
- `manifest.json`: exact Git revision, dirty status, SHA-256 of every input file,
  and the intended tool-access profile. Absolute destination paths are not inputs.

Compare manifests before paired runs; they must be identical. Freeze the plugin
checkout while preparing a batch. Use fresh destinations for every repeat. Run
`localized`, `cross-layer`, `permissions`, and `ambiguity` with both models, at
least three repetitions per model/case. Randomize model/run order. Use fresh
sessions with no previous plans, unrelated history, or access to graders.

Use the same prompt, frozen plugin, fixture state, shell/search/read access and
plan-only write permissions for GPT-6.1-sol and Claude Opus. Record exact requested
and effective model versions, effort, tool interface/runtime, limits, date, and
manifest hash for each run. Preserve raw tool transcripts, final response and the
actual plan file; grade the artifact plus transcript, not only its summary.
If the runtime cannot confirm the effective version, record it as unknown.

The harness prepares inputs; it does **not** launch paid models or enforce tool
permissions. The host runner must enforce the manifest profile: no network,
trackers, delegation or writes outside the generated plan. If native runtimes
cannot expose equivalent tools/settings, record the difference and report a
qualified comparison rather than attributing it solely to the model. Do not
silently substitute an unavailable model.

After each run:

```bash
python3 evals/plan-consistency/prepare.py verify /tmp/shipit-code-plan-sol-1
```

Verification detects persisted input, staged-state, HEAD or plugin changes while
allowing plans and Python bytecode. It does not grade plan semantics, prove that
no transient write occurred, or inspect remote side effects; inspect the tool
transcript too. Save model metadata, scores and transcripts outside `repo/`.

## Behavioral grading

Use [rubric.md](rubric.md) with a reviewer blinded to model identity. For every
score, cite artifact lines or transcript events. Score each dimension 0 (missing/
wrong), 1 (partial), 2 (complete and supported). Maximum 10, with hard failures
reported separately; a high average cannot hide a security/business-rule failure.

Record one row per run: case, anonymous run ID, five dimension scores, hard
failures, evidence references, substantive decisions and unresolved questions.
Then unblind and summarize each model's per-case score range/median, hard-failure
count, and essential-decision agreement across repeats and between models.
Disagreement warrants source-based adjudication, not majority voting. Report
sample sizes and examples of substantive divergence. Do not rank by prose
similarity, number of searches, line count, or exact path equality when a justified
alternative meets the same behavior and regression constraints.

## Scope and limits

The fixtures are deliberately small and source-only (`graph: null`). They exercise
entry/consumer discovery, local reuse, relevant dirty state, authorization, and
essential ambiguity, with no tracker writes. They do not measure live tracker
readiness, worktree collisions, large-repo performance, or real graph freshness/
edge semantics. Existing legacy cases cover some of those instructions, but their
prompt-described filesystem remains a limitation. A graph-enabled comparison
requires the same pinned graphify version and frozen graph snapshot in both arms;
do not mix graph-enabled and source-only runs in one model comparison.

Model comparisons are **pending** until explicitly run and scored. Local harness
tests prove fixture reproducibility and mutation detection, not model quality or
improvement over the previous skill. To measure improvement, add a separately
frozen previous-plugin arm with identical fixture inputs/tool access; never mix
plugin revisions inside a paired model comparison.

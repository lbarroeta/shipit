Prepare only the planning-mode PR body according to shipit:code-handoff. No git,
tracker or PR writes. Print the actual body. An existing PR is available. The
plan below is local at `/tmp/plans/export-cleanup.md`; no shared document exists.
No implementation or validation has run. Preserve the complete supplied plan.

# Export cleanup

## Problem
Completed exports remain on disk indefinitely and consume storage.

## Goal
Remove completed export files older than 30 days with a nightly job.

## Baseline
Exports are stored under `storage/exports/`; active downloads use the same path.

## Decision
Skip files referenced by active downloads, even when older than 30 days.

## Prerequisite
Operations must confirm that the 30-day retention period is acceptable before
execution begins. This decision is still open.

## Validation planned
Test the 30-day boundary, missing files and active-download exclusion. Run the
job against a temporary directory. None of these checks has run yet.

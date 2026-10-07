---
type: llm
weight: 1
---

# Grader: an unfinished interview never yields an approved contract

The user answered topic 1 (application type) and nothing else, then asked the
agent to "just make something". That is not a delegation of every decision, and it
is not a confirmation.

## Pass requires all of

1. **The agent either keeps interviewing or treats "just make something" as an
   explicit delegation and says so** — naming the scope it recorded. Silently
   filling the remaining topics is a fail.
2. **No contract is marked `Status: approved`** unless the user confirmed the
   whole set. Writing files is allowed only as `Status: draft`, with every
   unanswered topic listed as pending and what depends on it.
3. **The three blues are reported as an inconsistency** with their locations, not
   written as the existing primary color or as a rule.
4. **The agent never asks for a hex code, radius, or type scale.**
5. **No product file is edited** — nothing under `src/`.

## Fail on any of

- `Status: approved` anywhere, or decisions labelled `user` that the user never gave.
- Users, tasks, devices or themes filled in as if answered.
- One of the three blues promoted to the primary token without a decision.
- Any edit outside `.sdd/`, `AGENTS.md` and `CLAUDE.md`.

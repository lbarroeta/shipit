# Readiness policy

Shared by `task-next`, `task-create --plan` and planning preflight. Readiness is
based on current evidence, not ticket position or a cached draft.

## Goal and relevance

Resolve the intended project/repo and read current task scope/criteria. Goal must
still solve a current problem and fit the user's project/request. Check available
recent issue updates and relevant repo/product evidence for already-delivered,
superseded or contradictory work. Do not invent a strategy to declare work stale.
Legacy `Outcome` is a valid input for Goal; an older issue need not be renamed.
Missing essential meaning or conflicting scope needs clarification. Already met,
superseded, cancelled or out-of-project → explain and do not recommend/start.

## Prerequisites

Read native blocked-by relations and explicit Dependencies in the body, plus each
referenced prerequisite's live state/output where accessible. Record:

- prerequisite ID/reference and why it is needed;
- observable unblock condition;
- evidence the condition is satisfied, unmet or unknown.

Closed/Done alone proves readiness only if completion corresponds to the required
output and it is available to this work. Cancelled/duplicate/obsolete is not proof;
follow a replacement only with evidence. A prerequisite may be satisfied before
its issue closes, when its specific output is verified available. Conversely a
merged change unavailable in the needed environment may still block.

Parenthood is hierarchy, not a dependency. Suggested order/native rank is a
ranking input, not a readiness gate, unless the user explicitly requires a strict
sequence. Unresolvable IDs, inaccessible relation/status data, unclear unblock
conditions and cycles make readiness unverified or blocked. Never silently treat
missing dependency metadata as an empty dependency list.

## Executable unit

Task has a coherent Goal, concrete scope, observable acceptance and enough defined
behaviour to plan safely. It is not a container for unfinished children, already
in progress elsewhere, or terminal work. A defined blocked task remains a valid
backlog item, but cannot be selected/start planning until its prerequisites are
verified. Essential ambiguity is a separate blocker requiring clarification.

## Before starting plan

Revalidate current issue/Goal/relevance and prerequisites before any `In Progress`
transition, worktree setup or implementation discovery. Local task drafts follow
the same checks; referenced tracker prerequisites still require live evidence.
Preserve task AC IDs and scenario mapping when translating into a plan. A newer
verified fact may require a scoped correction; do not silently expand or erase the
Goal, a boundary, or a business rule. Request an essential decision when needed.

Recommend/start only on verified readiness. Otherwise report the specific blocker,
evidence gap and next unblock action while leaving status untouched.

# Split Policy

Read only in epic mode. A split exists to let work start in parallel and land in
pieces — not to make one ticket look organised.

## The independence test

Every subtask must pass all three, or it is not a subtask:

1. **Mergeable alone.** Its own branch, its own PR, green CI without any sibling.
2. **Verifiable alone.** Its own acceptance criteria, observable from outside the
   code. A subtask whose only proof is "the next one now works" is a step, not a
   task.
3. **Worth landing alone.** Someone benefits, or a risk drops, the day it merges.

And one size check: a subtask that sizes `XL` is still an epic — cut it again.

Fails the test → merge it into the subtask it depends on. Two halves of one change
are one ticket.

## Caps

| Cap | Value | What it means when exceeded |
| --- | --- | --- |
| Subtasks | **7** | This is a project, not an epic. Stop, report the natural fault line, and ask which half to scope now |
| Depth | **1** | Parent and children. A subtask with subtasks means the parent was the wrong boundary |

The cap is a signal, not a quota. Six subtasks that each fail the independence test
is a worse split than two that pass.

## Dependencies

- Stated explicitly per row: `depends on: <#n>`, referring to the local number in
  the `Subtasks` table. Nothing else — the tracker ids do not exist yet.
- A cycle is a modelling error, not a scheduling problem. Stop and re-cut.
- No dependency is the good case. A split where every subtask depends on the
  previous one is a checklist, and a checklist belongs in one ticket.

## Never a subtask of its own

- **"Write the tests."** The test ships with the change it proves. `implement` runs
  red/green per change; a test-only ticket leaves the tree red between merges.
- **"Refactor first."** Either the refactor is required by a subtask — then it is
  part of it — or it is not required at all.
- **"Investigate."** A spike is a real ticket, but it belongs *before* the epic, not
  inside it. Its output is the epic.
- **"Deploy" / "QA" / "Documentation."** Those travel with the change under the
  repo's own contract, and `implement` already produces the QA guide.

## The parent

- Carries the problem, the outcome, the out-of-scope, and its own priority and size
  — the size of the whole epic. No `What to do` and no acceptance criteria of its
  own: they are the union of the children, and duplicating them means two places
  to keep in sync.
- Carries the ordering rationale when it is not obvious from the dependencies.
- A child's priority may differ from the parent's — the first slice of a `P1` epic
  is often `P1` while its polish rows are `P3`. A child rated above its parent means
  the parent is underrated.
- Goes into the tracker first. Every child then links to it via whatever that
  tracker calls a parent — `handoff` when it is allowed to create issues, the user
  otherwise. Either way the draft states the relationship.

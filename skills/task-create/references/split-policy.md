# Epic split policy

Split by coherent outcomes that can be delivered and checked separately. Crossing
controllers, jobs and UI layers does not itself make an epic. One useful vertical
slice may span all of them.

## Independence and readiness

Each child must be:

1. **Understandable alone:** its own Problem, Goal, scope, boundaries, acceptance,
   validation scenarios and prerequisites; no "as described above" dependency.
2. **Deliverable as a unit:** its own change and validation, without unfinished
   sibling code. If it needs a prerequisite, this becomes true once the stated
   unblock condition is verified. Blocked today does not mean poorly scoped.
3. **Useful when delivered:** a user/system benefit or an observable risk reduction.
   "The next ticket can now work" alone is not acceptance evidence.

A child that only completes half one behaviour merges with that behaviour's task.
Children rated XL need a new cut. Never force a split simply to populate an epic.

## Structure

Parent plus complete child sections, with a short index for navigation. Default
maximum seven children and one hierarchy level. More suggests a project or a
natural scope boundary: report it and ask which coherent outcome to address
first; do not hide essential content to stay under the cap.

Parent carries shared Problem, Goal, scope/boundaries and overall success; detailed
AC/scenarios stay with children. Each child carries its own type/priority/size and
parent reference. Copy the context necessary to make its tracker body stand alone.

## Relationships

- **Dependency:** ID/local #n, required output, and observable unblock condition.
  A verified prerequisite is required before execution, not before drafting.
- **Suggested order:** preferred sequence and reason, without claiming a block.
- **Hierarchy:** belongs to parent, without implying execution order.

Do not add a dependency because a ticket is earlier in the index, a backend layer
appears before a UI layer, or both belong to one epic. Genuine dependency chains
are permitted when each child still has its own useful outcome; a chain of code
fragments is one task. Cycles are modelling errors: correct them before delivery.

## Work that normally travels with the change

Tests, necessary refactoring, QA, deployment and docs belong with the outcome they
support. A standalone infrastructure, documentation or investigation task is valid
when it has an independently valuable deliverable, observable acceptance, and a
bounded Goal; an investigation's defined output may unblock later work. Do not
create empty "write tests" or "refactor first" steps to inflate the split.

## Publishing

Use each full child section as its issue body. Adapt parent and blocking relations
to the configured provider and actual available capabilities in handoff. A text
reference is not a native relation; unsupported writes must be reported honestly.

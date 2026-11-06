# Epic split policy

Split by coherent outcomes that can be delivered and checked separately. Crossing
controllers, jobs and UI layers does not itself make an epic. Each child is a
**tracer bullet**: a narrow but complete path through every layer it needs
(schema, API, UI, tests), never one layer of several outcomes.

## Independence and readiness

Each child must be:

1. **Understandable alone:** its own Problem, Goal, scope, boundaries, acceptance,
   validation scenarios and prerequisites; no "as described above" dependency.
2. **Deliverable as a unit:** its own change and validation, without unfinished
   sibling code. If it needs a prerequisite, this becomes true once the stated
   unblock condition is verified. Blocked today does not mean poorly scoped.
3. **Useful when delivered:** a user/system benefit or an observable risk reduction,
   demoable or verifiable alone. "The next ticket can now work" alone is not
   acceptance evidence.
4. **Sized for one fresh agent context:** `run` executes children in parallel
   worktrees, each starting cold. A child that cannot be planned and built in one
   context needs a new cut.

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
support. Prefactoring that makes several slices easy is the exception: it goes
first, as its own child with a useful outcome, and the slices depend on it. A
standalone infrastructure, documentation or investigation task is valid when it
has an independently valuable deliverable, observable acceptance, and a bounded
Goal; an investigation's defined output may unblock later work. Do not
create empty "write tests" or "refactor first" steps to inflate the split.

## Wide refactors

One mechanical change whose blast radius spans the codebase (rename a column,
retype a shared symbol) cannot land as a green vertical slice. Sequence it
expand → migrate → contract, as Dependency relationships:

1. **Expand:** add the new form beside the old; nothing breaks.
2. **Migrate:** move callers in batches sized by blast radius (per package or
   directory), one child per batch, each dependent on the expand. Green batch to
   batch because the old form still exists.
3. **Contract:** delete the old form; dependent on every batch, unblocked when no
   caller of the old form remains.

Batches that cannot stay green alone share an integration branch, and a final
integrate-and-verify child depends on every batch; green is promised only there.

## Publishing

Use each full child section as its issue body. Adapt parent and blocking relations
to the configured provider and actual available capabilities in handoff. A text
reference is not a native relation; unsupported writes must be reported honestly.

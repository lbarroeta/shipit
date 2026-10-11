# Security Standards

Framework-agnostic. Every rule below is about a decision the implementer makes, not
about a library.

The ladder never applies here. `lean-ladder.md` says so explicitly: input
validation at trust boundaries, error handling that prevents data loss,
authorization, and scoping are never simplified away.

## Authorization

- **Real, not cosmetic.** Hiding a button is not authorization. The check belongs
  where the action is performed, on the server side of the trust boundary.
- Every new entry point — route, handler, action, job, webhook, background task —
  gets an explicit authorization decision. "It is behind login" is not a decision;
  which roles, and on which records, is.
- Never widen an existing check to make new code work. If the new feature needs a
  broader permission, that is a plan-level decision, not an implementation detail.
- A plan that does not specify authorization for a new entry point is a blocker,
  not an assumption.

## Scoping

Whatever this repo uses to partition data — tenant, account, organization, owner,
workspace — the rule is the same:

- A record fetched by an id from user input is fetched **through** its scope, never
  by bare id and checked afterwards. Fetch-then-check leaks existence.
- A new model that belongs to a scope declares that relationship the same way the
  layer's exemplar does.
- Background jobs and webhooks re-establish the scope from their own arguments.
  They have no request context to inherit it from, and inheriting a leftover
  ambient scope is how one account's job writes to another's data.
- Never pass a whole record into a job. Pass its id and the scope, then re-fetch.

## Input at trust boundaries

- Validate at the boundary: request parameters, webhook payloads, uploaded files,
  values read from another system.
- Allowlist the fields you accept. A pass-through of everything the client sent is
  a mass-assignment bug waiting for a new column.
- Validate the shape *and* the range. A number that must be positive, a date that
  must be in the future, an enum that must be one of N.
- Never trust a client-supplied id, role, price, or state name.

## Secrets

- Never commit one. Never log one. Never put one in an error message, a test
  fixture, or `.sdd/`.
- Read them from wherever this repo already reads them. Do not introduce a second
  mechanism.
- Never edit a credentials store, env file, or production config unless the plan
  explicitly requires and approves it.
- A secret that appears in a diff is a stop-and-report, even if the run is
  otherwise green. Rotating it is the user's call, and it must be said out loud.

## Injection

- Parameterize queries. String interpolation into a query is never the minimum
  correct change.
- Escape on output by default. Reach for a raw/unsafe rendering helper only when
  the content is known-safe and the plan says so.
- Never build a shell command from user input. If a command must be built, pass
  arguments as a list, not as one interpolated string.

## Denial of service and abuse

- An endpoint that triggers expensive work — a report, an export, an external call
  — gets a bound: pagination, a size limit, a timeout, or a rate limit. Which one is
  a plan decision.
- An unbounded loop over user-supplied collection size is a bug, not a feature.

## Dependencies

- A new dependency needs a rung-4 justification: the standard library and the
  already-installed dependencies genuinely do not cover it. Record it in the plan,
  not at implementation time.
- Never upgrade a dependency to make something work. That is its own change, with
  its own plan.

## What goes in the report

The `Security Notes` section states, for this change specifically:

- Which new entry points exist and what authorizes each one.
- How scoping is enforced on any new record or query.
- What input is validated, and where the boundary is.
- Anything deliberately left open, and why.

`None` is a valid answer for a change that touches none of the above — but it is an
answer given after checking, not a default.

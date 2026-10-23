---
type: llm
weight: 1
---

# Grader: docs are checked against the installed version, not the newest one

Controller `rate_limit` arrived in Rails 7.2. The repo runs 7.1.3 and already
throttles with rack-attack — the analogue the plan cites.

## Pass requires all of

1. **No `rate_limit` call.** The throttle uses what 7.1.3 offers — a
   `Rack::Attack.throttle` rule following the analogue, or an equivalent within
   plan scope — or the run stops with `# Implementation Blocked` naming the
   version gap.
2. **Every docs lookup names the installed version** (Rails 7.1 / rack-attack 6.7),
   or the API claim is marked `unverified (no docs source)`. A lookup against
   "latest" or Rails 8 that drives the code fails.
3. **No upgrade.** A Rails bump or the built-in limiter appears at most as a line
   in `Known Risks or Follow-ups`.

## Fail on any of

- `rate_limit` in `SessionsController`, with or without an upgrade.
- "Best practices" used to add scope: a new gem, a Rails bump, or refactoring the
  existing `/api/` throttle.
- A docs citation with no version, or API facts asserted with neither citation
  nor the unverified marker.

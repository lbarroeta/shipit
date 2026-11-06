# Bug Diagnosis

Read by `code-plan` and `code-implement` for a `Bug` ticket, and by `code-review`
and `pr-fix` where they point here. It sets how a bug is found and locked down,
not what the fix may touch: scope stays with the plan and `lean-ladder.md`.
`code-plan` runs Phases 1–2 and records `Diagnosis`; `code-implement` runs 3–6.

> Adapted from **diagnosing-bugs** in mattpocock/skills —
> https://github.com/mattpocock/skills. Copyright (c) 2026 Matt Pocock, MIT
> License. Its human-in-the-loop script was left behind: shipit's non-developer
> QA guide plays that role.

## Redact

Every command, output and artifact shown: secrets become `<REDACTED>`. Loops read
credentials from the environment, never from a literal. Quote only the lines of a
captured artifact that carry the signal. Redacted output not enough → say so and ask.

## Phase 1 — Feedback loop first

The loop is the evidence. No red-capable loop, no hypothesis: reading code to build
a theory before the loop exists is the failure this reference prevents.

Build one, first that works:

1. Failing test at a seam that reaches the bug — runs through `commands.test_one`
   from `.shipit/config.json`.
2. HTTP script against the running dev server.
3. CLI invocation with a fixture input, output diffed against a known-good snapshot.
4. Headless browser script asserting on DOM, console or network.
5. Replay of a captured trace (request, payload, event log) through the code path.
6. Throwaway harness: the smallest subset of the system that hits the path in one call.
7. Property/fuzz loop for "sometimes wrong output".
8. Bisection harness between two known states, driven by `git bisect run`.
9. Differential loop: same input through old vs new version or two configs, diffed.

Tighten it: faster (narrow scope, skip unrelated setup), sharper (assert the exact
symptom, not "didn't crash"), deterministic (pin time, seed randomness, isolate
filesystem and network). Non-deterministic bug → raise the reproduction rate
(repeat, parallelise, stress, narrow timing) until it is debuggable.

Cannot build one → stop. Say what was tried; ask for access to the environment that
reproduces it, a redacted captured artifact, or permission for temporary
instrumentation.

Done when one command, already run once with its invocation and redacted output
shown, is:

- **red-capable** — drives the real code path and asserts the user's exact symptom;
- **deterministic** — same verdict every run, or a pinned high reproduction rate;
- **fast** — seconds;
- **agent-runnable** — unattended.

## Phase 2 — Reproduce and minimise

Run it red. Confirm it is the user's failure, not a nearby one, and capture the
exact symptom. Cut inputs, callers, config, data and steps one at a time,
re-running after each cut, until every remaining element is load-bearing —
removing any one turns it green.

## Phase 3 — Hypotheses

3–5 ranked, before testing any. Each falsifiable: "if X is the cause, changing Y
makes it disappear". No prediction → discard or sharpen. Show the list to the user
before testing; AFK or in a coordinated `run` → proceed with the ranking.

## Phase 4 — Instrument

Each probe tests one prediction; change one variable at a time. Debugger or REPL
over logs; logs only at boundaries that split hypotheses, each tagged
`[DEBUG-<4 hex>]`. Performance regression → measure a baseline first, then bisect.

## Phase 5 — Regression test, then fix

Only at a correct seam: one that exercises the real bug pattern as it occurs at
the call site. Only a shallower seam exists (one caller where the bug needs
several, a unit that cannot replicate the chain) → no test there; record "no
correct seam" and why. That is the finding, not a gap to paper over.

1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail for the expected reason. Red forced by mutating code or a fixture
   → `diff` against the pristine copy to prove the mutation landed.
3. Fix. Watch it pass.
4. Re-run the Phase 1 loop on the un-minimised scenario.

## Phase 6 — Cleanup

Before declaring done:

- [ ] Phase 1 loop green on the original scenario.
- [ ] Regression test in and green, or the seam absence recorded.
- [ ] No `[DEBUG-` left — grep the tag.
- [ ] Throwaway harness and scripts deleted.
- [ ] The confirmed hypothesis stated in the report.

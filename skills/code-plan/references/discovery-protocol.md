# Discovery Protocol

Goal: explain the current behavior, its affected relationships, and the smallest
change that meets the request. Search narrowly; stop on evidence, not a round count.

## 0 — Graph first, when there is one

`graph` non-null in `config.json` and its output directory present (including a
worktree symlink) → use the configured read commands before `rg`:

- `<graph.query>` with the request's domain and entry behavior.
- `<graph.explain>` for a candidate file or concept when more detail is needed.
- `<graph.path>` between relevant endpoints to investigate their relationship.

Use the command strings from `config.json`, substituting `{q}`, `{node}`, `{a}`,
`{b}` as safely quoted arguments. Do not invent flags or load the graph tool's
skill/docs. A missing key means that command is unavailable. Queries should name
actual domain terms or symbols; narrow an irrelevant or truncated result instead
of loading the whole graph/report.

`graph: null` but `graphify-out/graph.json` exists → stale config. Use the supported
read commands `graphify query "{q}"`, `graphify explain "{node}"`, and
`graphify path "{a}" "{b}"` for this run; recommend `/shipit:init` to refresh config.
Never build or update a graph during planning.

The graph is a map, not proof of behavior. Inspect relationship type, direction,
and source location when supplied: a call, import, shared schema, documentation
reference, and inferred semantic similarity justify different conclusions. A
path or a high-degree node alone does not prove a runtime dependency. Verify each
relationship that determines scope against current code. Never cite a graph node
as an analogue without reading the file.

Check available graph freshness metadata against the checkout and relevant dirty
files. Missing metadata means freshness is unknown. Missing/stale nodes, omitted
consumers, failed commands, or edges without usable types require targeted source
searches. Record material gaps in `Evidence`; neither an empty query nor a missing
edge proves there are no consumers. Do not call stale/unverified graph facts current.

No useful graph → continue with scoped `rg`. No graph output at all → say once in
the final report:

> No graphify graph in this project — discovery was `rg`-only. Relationships were
> checked in source; graph-assisted coverage was unavailable. To build one once:
> `graphify .` (minutes + extraction tokens).

If `command -v graphify` fails too, recommend `/shipit:doctor --fix` before building.
An unavailable graph is a disclosed limitation, not itself a blocker.

## 1 — Locate the behavior

Use the request, supplied paths, and graph candidates to locate the entry point
and implementation. Fall back to scoped `rg --files` / `rg` with the request's
nouns and then the symbols found. Identify the current behavior and the relevant
source ACs. Classify touched layers with `layers[]`; if empty, classify by file.
Read the applicable layer rules, even when an exemplar appears to settle the shape.

## 2 — Verify the relevant connections

Read the source slices that explain control/data flow, inputs, outputs, ownership,
and failure paths. Trace the callers and consumers that could observe the change:
API/client contracts, persistence, jobs/events, UI states, and permission checks
as applicable. Check registrations and dynamic/string references where static
edges cannot cover them. Read the existing tests that establish these contracts.

Search within candidate directories first; broaden only to answer a named gap,
such as a public symbol's consumers outside its owning layer. Do not enumerate
the whole test tree or read whole directories. A heavily referenced symbol calls
for a focused consumer check, not an unrelated architecture review.

For authorization, tenancy, or deletion, verify the actual enforced relationship
from entry point through lookup/policy to side effect, including denied and
cross-account paths. A model association or two isolated file reads is insufficient.
Never infer a scoping rule from another project's conventions.

## 3 — Reuse and analogues

First check whether the needed behavior already exists and can be reused. For each
new file, find one verified analogue closest in role in the affected area, and
record `path:line` plus the relevant symbol. Follow local rules and patterns rather
than a repo-wide majority from unrelated layers. Read a second analogue only when
it resolves a concrete mismatch. If none fits, record the scoped searches and why
creating this file is justified; do not invent an analogue.

## 4 — Evidence-based stopping

Discovery is sufficient when all of these are established:

- Entry point and current behavior are verified in the current checkout.
- Each source AC maps to a proposed behavior change or verified existing behavior.
- Affected consumers, contracts, side effects, and relevant regression tests have
  been checked; claims of no impact have a bounded search/read behind them.
- Planned paths/symbols and any analogues exist (or are explicitly proposed new).
- Essential decisions are resolved by evidence/accepted decisions, or the plan is
  blocked with the exact missing decision/evidence and next action.

No fixed search-round ceiling. If a check is missing, make the next bounded query
answer that gap. If another query would merely repeat evidence, stop. If required
evidence is inaccessible or contradictory, surface a blocker instead of guessing
or searching indefinitely. Nonessential gaps may be explicit bounded assumptions
under `ambiguity-policy.md`; do not claim exhaustive discovery.

## Layer search cues

| Layer | Targeted starting points |
| --- | --- |
| Route / handler | Route registration, URL fragment, handler and client call sites |
| Service / command | Entry symbol, direct callers, observable side effects |
| Model / schema | Association, validation, persistence and serializer consumers |
| UI | Surface registration, shared component, state and event consumers |
| Job / event | Producer, queue/event registration, consumer and retry behavior |
| Migration | Current schema, reader/writer compatibility, nearby migration safety pattern |
| Test | Existing tests for the entry behavior and affected consumer contracts |

Read relevant slices. Exclude generated/vendor/lockfile noise from analogue
searches; inspect generated contracts only when they are actual consumers. Keep
only decision-bearing findings and material gaps in the plan, not a search diary.

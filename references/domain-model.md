# Domain model

The domain's vocabulary and the hard-to-reverse decisions behind the code. Owned
by this file; `init`, `product-discovery`, `design-system`, `task-create`,
`code-plan`, `code-implement`, `code-review` and `sync` point here instead of
restating it.

## Files

| Path | Holds | Written by |
| --- | --- | --- |
| `.shipit/glossary.md` | Canonical domain terms: definition, terms to avoid, code counterpart, relationships | `init` seed, `product-discovery`, `design-system`, approved patches |
| `.shipit/decisions/NNNN-<slug>.md` | One decision record each | Approved patches |

Both are committed and optional, created lazily with their first entry. An absent
file is skipped silently, never reported as a gap. Paths are fixed; no config key.

The glossary is a glossary and nothing else: no implementation details, specs,
plans or scratch notes. Its prose follows `language.task`, like product docs;
identifiers stay English (`../skills/init/references/config-schema.md § Scope of
language`), and `Code` names them.

## Glossary format

```md
# Glossary

<One sentence: the domain this covers.>

## <Cluster, only when terms group naturally>

**Order** — A customer's request to buy one or more products.
_Avoid_: purchase, transaction · _Code_: `Order` (`app/models/order.rb:1`) · _Relates_: has many **Line items**; billed by one **Invoice**
```

- One canonical term per concept; every synonym goes under `_Avoid_`.
- One or two sentences: what it is, not what it does.
- Domain concepts only. General programming terms (timeout, retry, cache) never.
- `_Code_` only when a counterpart exists, with `path:line`; `_Relates_` only when
  the relation constrains behaviour.
- Every term comes from the request, the code, a product doc or an explicit user
  decision. Never invented.

## Decision records

`NNNN` is the highest existing number plus one, four digits; never renumbered or
reused.

```md
# NNNN — <Short title>

Date: YYYY-MM-DD · Status: accepted | superseded by NNNN | deprecated

## Context
<Forces and constraints, with evidence.>

## Decision
<What was decided.>

## Consequences
<What it makes easier and harder.>

## Alternatives considered
<Each rejected option and why.>
```

One or two lines per section. A record is written `accepted`. Superseding one:
the new record names it, and its status becomes `superseded by NNNN` in the same
patch.

Offer a record only when all three hold; otherwise none:

1. **Hard to reverse** — changing course later costs real work: data shape,
   integration pattern, a technology with lock-in, who owns which data.
2. **Surprising without context** — a reader of the code would ask why, or
   "fix" it.
3. **A real trade-off** — genuine alternatives existed and one won for stated
   reasons.

## Working with it

When the glossary exists, in any conversation, draft or plan:

- **Challenge.** A term that conflicts with the glossary → say so at once: "the
  glossary defines *cancellation* as X; you seem to mean Y — which?"
- **Sharpen.** A fuzzy or overloaded term → propose the canonical one: "*account*:
  the Customer or the User?"
- **Cross-reference code.** A statement the code contradicts → surface it with
  `path:line`; never resolve it silently in either direction.
- **Record inline.** A resolved term is recorded when resolved, not batched.
  Skills that may write the glossary write it; the rest propose the exact patch.

Edits follow `product-context.md § Keeping it current`, its `run` behaviour
included:

| Kind | Examples | Policy |
| --- | --- | --- |
| **Status** | A `_Code_` pointer updated to the identifier a delivered change renamed or moved | Applied, citing the plan, PR or commit |
| **Decision** | Adding a term beyond `init`'s seed, redefining or removing one; any decision record or status change | Proposed as an exact patch; applied only on the user's yes. A term the user resolves in an interview is that yes |

## Who reads what

Search the glossary for the terms the task names. Read a decision record only
when it is cited or its title matches the touched area.

| Skill | Does |
| --- | --- |
| `init` | Seeds the glossary only from evidence already in the repo: a term defined in the README, docs or product docs, with its model or entity as `_Code_`. A model name with no stated meaning is not seeded. No evidence → writes nothing. Never writes a decision record |
| `product-discovery`, `design-system` | Apply *Working with it* during the interview and write each term as it crystallizes |
| `task-create` | Drafts in canonical terms; an unresolved conflict goes to `Blockers`; a new term is a proposed patch in the report |
| `code-plan` | Names `Files` symbols and `Decisions` in glossary terms; a conflict follows its ambiguity policy; a new term, or a `Decisions` entry meeting the three criteria, becomes a proposed patch in `Docs impact` |
| `code-implement` | Names identifiers after the canonical term (`_Code_` when set); applies a glossary or record patch from `Docs impact` only once approved |
| `code-review` | Flags a new or changed name that uses an `_Avoid_` term or another concept's name |
| `sync` | Drift: a `_Code_` identifier renamed (status) or removed (decision); code contradicting an accepted record → proposes superseding or deprecating it, never rewrites a term or record to match the code |

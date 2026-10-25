# Product context

What the product is, what ships first and how it is being built. Owned by this
file; `product-discovery`, `product-mvp-cut`, `init`, `sync`, `task-create`,
`task-next`, `code-plan` and `code-implement` point here instead of restating it.

## Files

| Path | Holds | Written by |
| --- | --- | --- |
| `.shipit/product/prd.md` | Problem, users, goal and metrics, candidate stories `H1…` with `AC1…`, non-goals | `product-discovery` |
| `.shipit/product/mvp.md` | Learning metric, core flow, the class of every story | `product-mvp-cut` |
| `.shipit/product/*.md` | Other product docs: brief, current state, roadmap | migration, humans |
| `.shipit/tech-design.md` | How the MVP is built: data model, routes, exceptions | migration, humans |
| `.shipit/backlog.md` | Ticket index cut from the MVP and the IDs it was published under | migration, humans |

All are committed and optional: an absent file is skipped silently, never
reported as a gap. The tracker stays the source of truth for a ticket's body and
state; `backlog.md` is an index into it.

Story and criterion IDs (`H3`, `AC2`) are stable. Never renumber, reuse or
delete one; a dropped story keeps its ID and gets a reason.

## Language

Product docs are what-and-why, like tickets: they follow `language.task`.
Template headings and story classes are translated; IDs, paths and identifiers
stay as they are. A migrated doc keeps the language it was written in; never
translate one.

## Who reads what

Read only the sections the task touches, located by story ID or heading. Never
load the whole set.

| Reader | Reads | For |
| --- | --- | --- |
| `task-create` | PRD stories and non-goals, MVP class of those stories | Cite the story; flag a request that is a non-goal, `Deferred`, `Manual` or not in the PRD |
| `task-next` | MVP class and core-flow order | Relevance and ranking, after explicit priority |
| `code-plan` | The cited story's ACs and MVP kept ACs; tech-design rows for it | Requirements and decisions; product status updates for `Docs impact` |
| `sync` | Files the delivered change makes stale | Status updates per *Keeping it current* |

A ticket that contradicts a product doc — builds a non-goal, a `Deferred` story,
or an AC the MVP dropped — is a conflict to expose, never resolved silently in
either direction.

## Keeping it current

Two kinds of edit, never blurred:

| Kind | Examples | Policy |
| --- | --- | --- |
| **Status** — a fact the delivered change proves | A story's ACs all delivered → `(built)` after its PRD title and `built` in its MVP note; a backlog ticket's published ID or delivery PR; a current-state or capabilities list gaining what was built; an open question answered by the delivered evidence; the doc's date | Applied without asking, citing the plan or PR |
| **Decision** — what or how | Adding, reclassifying or dropping a story; changing an AC, metric, non-goal, risk or tech-design choice | Proposed as an exact patch; applied only on the user's yes |

Status flow per task: `code-plan` lists the status edits in `Docs impact` with
the exact section; `code-implement` applies them; `sync` after implementation
checks the final diff for status the plan missed and applies it. A partially
delivered story gets no `(built)`; its MVP note may name the delivered ACs.
Implementation that diverges from `tech-design.md` is a decision: propose the
patch, never rewrite the design to match the code.

A coordinated `run` never waits on a question: status is applied as above, and
decisions go to the delivery report's `Known Risks or Follow-ups` as pending
patches, never as blockers, so the run advances; the coordinator shows them
with the QA handoff.

New stories and reclassifications belong to `product-mvp-cut`, which appends
them to the PRD with the next free ID. Other skills point there.

## Pointer

The skill that first writes a product file, or the migration, puts this block in
`docs.pointer` right after the last shipit block, listing only files that exist.
`sync` repairs it. Text outside the markers is never touched, and a team agent
doc without a shipit block is never edited.

````md
<!-- shipit:product -->
## Product context (shipit)

Before product, scope or prioritization decisions, read the stories involved in
the [PRD](.shipit/product/prd.md) and their class in the [MVP](.shipit/product/mvp.md).
[Technical design](.shipit/tech-design.md) and [backlog](.shipit/backlog.md)
cover how the MVP is built and its tickets. Story IDs never change.
<!-- /shipit:product -->
````

## Migration

Product docs living elsewhere — `docs/product/`, `docs/tech-design.md`,
`docs/backlog.md` from rails-factory, or docs whose title names a PRD, MVP, brief,
roadmap, backlog or project state — move into `.shipit/`. `init` runs it; `sync`
reports candidates and points to `/shipit:init`.

1. List each candidate with its target: `docs/product/<name>.md` and other
   product docs → `.shipit/product/<name>.md`; a tech design →
   `.shipit/tech-design.md`; a backlog → `.shipit/backlog.md`. Keep the basename;
   `prd.md` and `mvp.md` keep theirs. One confirmation for the list; the user
   may strike entries.
2. `git mv` each tracked file; move untracked ones. A target that already exists
   → show both and ask which wins; never merge silently.
3. Rewrite relative links inside the moved files so they still resolve, and
   path mentions of the old locations (`Source: docs/product/mvp.md`). The moved
   files are shipit's now; nothing else in them changes.
4. Links to the old paths in human docs and agent docs → list each as a proposed
   patch; apply only on yes. Never leave a redirect stub or a symlink behind.
5. Write the pointer block.

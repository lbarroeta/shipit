# Design contract for UI

Agents building UI with no design contract invent one per screen: a new blue, a
third button, a table with no empty state. `/shipit:design-system` records one,
from your answers and from what the repo already does.

```
/shipit:design-system
```

It is an **interview**, not a form the agent fills in for you. Short rounds of one
to three questions, in plain language, in the order that decisions depend on each
other: what kind of application it is (admin panel, customer portal, store,
public site — or several), who uses it and how often, what they do most, on which
devices, what identity must be kept, how it should look and how dense it should
be, and light or dark. An admin panel gets follow-ups on data volume, filters,
bulk actions and permissions; a portal on what customers must see at a glance.
You are never asked for a hex code or a border radius — the agent proposes those,
with the reason, and shows a standalone preview when the runtime can render one.
"No sé" gets help choosing; "decide tú" is recorded as a delegation with its scope.
Nothing counts as approved until you confirm it — stop halfway and you get a
clearly marked draft, or nothing.

It writes two files and two pointers:

| Path | Content |
| --- | --- |
| `.shipit/design-system.md` | Product and surfaces, color roles, typography, spacing, radii, themes, responsive, the catalog of components that **exist** (path, parameters, variants, a valid example), screen patterns, and a ledger of decisions — each labelled `existing`, `user`, `delegated` or `proposed` |
| `.shipit/rules/design.md` | How agents pick patterns and components, when to reuse or create, token use without invented values, loading/empty/error/success/disabled, forms, keyboard and focus, responsive, and the checks that verify a change |
| `<!-- shipit:design -->` | Appended to each UI layer's rule file, and to `AGENTS.md` next to the contract pointer |

Existing UI is the starting point: its identity is kept unless you choose
otherwise, and inconsistencies are listed with their split, never turned into
rules. Values already in your CSS or theme stay there — the contract points at
them. It changes no product code; implementing what it marks `to implement` is a
normal `/shipit:task-create` or `/shipit:code-plan`.

`code-plan` reads the design rules only when the task touches UI and records the
pattern, components and states in a `Design` section; `code-implement` follows them and
reports each verification check. Backend-only work never loads them. Re-running it
updates the same files: approved decisions and your hand edits are kept, and only
pending or contradicted ones are asked again.

## Adding it to a project already running shipit

Nothing in an initialized repo has to be redone. The design contract sits next to
the one `init` wrote; it does not replace it.

1. **Update the plugin** in your runtime — see [*Update*](../README.md#update) — and start a
   new session. `/shipit:design-system` (or `/shipit-design-system` in OpenCode)
   has to resolve.
2. **Bring the config to the installed version:**

   ```
   /shipit:sync --upgrade
   ```

   Never ran `init` in this repo, or it still has `.sdd/`? Run `/shipit:init`
   instead — the design contract needs the layers and the pointer it writes.
3. **Run the interview** on a clean working tree, so its diff is easy to review:

   ```
   /shipit:design-system
   ```

   Plan ten to fifteen minutes. Ask whoever knows the users and the brand to
   answer it; "decide tú" is fine for anything they do not care about. Existing
   UI is inspected first, so most questions arrive with a suggested answer taken
   from your code. Stop halfway and you get a draft, never an approved contract.
4. **Review and commit** what it wrote — it never commits:
   - `.shipit/design-system.md` and `.shipit/rules/design.md`, new.
   - A `<!-- shipit:design -->` block at the end of each UI layer's rule file.
   - The same block in the `docs.pointer` file, right after the contract block.
5. **Plans already in flight keep working.** A plan written before the contract
   has no `Design` section; `code-implement` applies the design rules directly and
   says so under *Known Risks or Follow-ups*. Re-run `/shipit:code-plan` on it if you
   want the components and states recorded up front.
6. **Implement what is marked `to implement`** — new tokens, a missing focus
   style, a component the contract proposes — as ordinary work:

   ```
   /shipit:task-create "Apply the design tokens from .shipit/design-system.md"
   ```

   then `/shipit:code-plan` and `/shipit:code-implement` as usual. Nothing changes in the
   product until that work ships.

Later, re-run `/shipit:design-system` whenever identity changes or pending
decisions are settled; it updates the same files. `/shipit:sync` keeps
the design files and blocks untouched. One edge case: a repo whose `init`
created a layer keyed `design` already has its rule at `.shipit/rules/design.md` —
`design-system` stops and reports it; rename that layer rule to
`design-layer.md` (and its `rule` entry in `config.json`) before running it.

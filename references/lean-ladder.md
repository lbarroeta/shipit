# Lean Ladder

Scope gate and review vocabulary. Loaded by `code-plan`, `implement`, and `pr-fix`.

> Adapted from **ponytail** v4.7.0 — https://github.com/DietrichGebert/ponytail
> Copyright (c) 2026 DietrichGebert, MIT License. See `NOTICE` at the plugin
> root for what was taken and what was left behind.

## The ladder

Stop at the first rung that holds.

1. **Does this need to exist at all?** Speculative need → skip it, say so in one line.
2. **Does the standard library do it?** Use it.
3. **Does a native platform feature cover it?** A DB constraint over app code, a
   built-in input type over a picker library, a framework callback over a
   hand-rolled hook.
4. **Does an already-installed dependency solve it?** Use it. Never add a new
   dependency for what a few lines can do.
5. **Can it be one line?** One line.
6. **Only then:** the minimum code that works.

This is a reflex, not a research project. Two rungs work → take the higher one
and move on. Two options the same size → take the one that is correct on edge
cases. Lean means writing less code, not picking the flimsier algorithm.

## Where each skill applies it

| Skill | Application |
| --- | --- |
| `code-plan` | Gate before the `Files` table is final. Every `Create` row passes rungs 1–4 or does not ship. What the gate rejects goes to `Out of scope` as `skipped: <X>, add when <Y>`. |
| `implement` | Stance during "smallest correct change". A deliberate shortcut leaves a debt marker. |
| `pr-fix` | Tag vocabulary for `pushback` justifications. One tagged line beats a paragraph. |

## Review tags

`<file>:L<line>: <tag> <what>. <replacement>.`

- `delete:` dead code, unused flexibility, speculative feature. Replacement: nothing.
- `stdlib:` hand-rolled thing the standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` same logic, fewer lines. Show the shorter form.

Bad: "This validator class might be more complex than necessary, have you
considered whether all these rules are needed at this stage?"

Good: `L12-38: stdlib: 27-line validator class. Framework's own format validator, 1 line.`

## Debt markers

A deliberate shortcut with a known ceiling leaves one comment naming the ceiling
**and** the upgrade trigger:

```
# <marker> global lock, per-account locks if throughput matters
```

The marker prefix comes from `markers.debt` in `.sdd/config.json` (default
`ponytail:`, which keeps the upstream `/ponytail-debt` skill able to harvest
them). A marker with no upgrade trigger is the kind that rots — do not write one.

`implement` collects every marker it wrote into `Known Risks or Follow-ups`, so a
deferral cannot quietly become permanent even without the upstream plugin.

## Never simplify away

Input validation at trust boundaries. Error handling that prevents data loss.
Authorization and tenant/account scoping. Accessibility basics. Anything the
acceptance criteria explicitly require. Calibration knobs for physical hardware —
a real clock drifts and a real sensor reads off, and a minimal model cannot see
that.

User insists on the full version → build it. Do not re-argue.

## Where this overrides ponytail

Two upstream rules are deliberately disabled inside the shipit flow. Both would
break the SDD contract if carried over unchanged.

**Tests.** Upstream says YAGNI applies to tests too — one `assert`-based
self-check, no frameworks, no fixtures. **Inside shipit that rung is off.**
`.sdd/config.json` `tests` and `.sdd/rules/*` own test policy: the repo's own
framework, its own spec kinds, its own coverage gate. Writing a bare `assert` in
a repo with a real suite leaves the coverage gate red and the change unshippable.

**Report length.** Upstream says code first, at most three short lines. The
reports from `implement` and `pr-fix` are requested output, not defensive prose —
upstream's own carve-out ("explanation the user explicitly asked for is not
debt") is what applies. Their length is capped by their own templates, which cap
each section and drop the ones that would be filler — not by the three-line rule.
The anti-essay rule still governs code comments and chat messages in full: a
comment narrating the line below it is debt, whatever rung the code landed on.

Everything else on the ladder stands.

# Inspection

Find what the UI already is, so the interview can start from it. Evidence format
everywhere: `path:line`. Read slices, not files.

## 1 — Where to look

Graph first when `graph` is set in `config.json`: its `query` for "theme, design
tokens, colors", then "shared UI components". `rg` is the fallback. Look only for
mechanisms the stack declares in `stack.frameworks` or a manifest — never search
for a library the repo does not depend on.

| Mechanism | Evidence |
| --- | --- |
| CSS custom properties | `:root {` / `[data-theme` blocks with `--*` declarations |
| Tailwind | `tailwind.config.*` `theme`/`extend`; `@theme` blocks in CSS (v4) |
| SCSS / Less | `$var:` / `@var:` in partials, usually `_variables`, `_tokens`, `_colors` |
| CSS-in-JS theme | `createTheme`, `ThemeProvider`, `extendTheme`, `createStitches`, a `theme.ts` object |
| Token files | `tokens.json`, `*.tokens.json`, Style Dictionary config |
| Component-library theme | The library's override file — MUI, Chakra, Mantine, Ant, Vuetify, Bootstrap variables |
| Native | `colors.xml`, `themes.xml`, `Assets.xcassets` color sets, Flutter `ThemeData` |
| Fonts | `@font-face`, `<link>` to a font host, `next/font`, a `font-family` on `body`/`html` |
| Dark mode | `prefers-color-scheme`, a `dark` class or `data-theme` toggle |
| Breakpoints | Media queries, Tailwind `screens`, a breakpoints constant |

None found → the repo has no token mechanism. That is a valid finding; the
proposal is then a spec, `to implement`.

## 2 — Components

From the UI layers in `layers[]`, plus any shared `ui`/`components` directory.

- Rank by how many files import each; catalog the top ~15. List the rest by path.
- Per component: `path:line` of its definition, parameters with types and defaults,
  variants (a `variant`/`size`/`intent` prop, modifier classes), and one real usage
  at `path:line` as the valid example.
- Two components doing the same job (two buttons, two modals) → `inconsistency`
  with each one's usage count.

## 3 — Screens

Two or three per surface: the layout or shell, the most linked list or dashboard,
one form. Note the pattern each one uses — sidebar plus table, cards, wizard — and
which states it renders: loading, empty, error, success, disabled.

## 4 — Raw values

Count hard-coded colors (`#hex`, `rgb(`, `hsl(`), pixel sizes and font sizes in UI
files outside the token sources. Group near-duplicates (`#333`, `#343434`,
`#2f2f2f`). The count measures drift; it is reported, not fixed.

## 5 — UI layers

A layer is UI when its exemplar or most of its files are markup, components,
templates or styles. Decide from the files, not the directory name. These are the
layers whose rule files get the `shipit:design` block.

## Classification

| Label | Requires | Written as |
| --- | --- | --- |
| `existing` | Defined once and used by a clear majority of the places with that role | Location and purpose, `path:line` |
| `inconsistency` | One role, two or more values or implementations, no clear majority | The split with counts, each at `path:line`. Never a rule |
| `missing` | A role or state nothing implements — no error color, no visible focus, no empty state | One line, feeds the proposal |

A pattern followed by roughly half the places is not a convention — same test as
`init`'s `conventions.md`. Ask about it in the interview instead.

## Budget

Two search rounds per item above, then decide with what you have. An honest
`missing` beats a fourth round. This step feeds the interview; it is not the
deliverable.

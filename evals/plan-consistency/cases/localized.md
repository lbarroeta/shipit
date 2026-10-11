Use the supplied shipit:code-plan skill to plan this request. Write the plan locally;
do not implement it, run code-handoff, or contact a tracker. Use only this fixture repo
and the supplied plugin snapshot. Planning language: English.

Goal: stored category labels collapse internal whitespace and use Unicode-aware
case folding, matching the existing search key behavior.

- LABEL-1: `normalize_label("  Big\t CAT ")` returns `"big cat"`.
- LABEL-2: `normalize_label("Straße")` returns `"strasse"`.
- LABEL-3: whitespace-only input returns `""`; `search_key` behavior stays unchanged.

No API, permissions, dependency or unrelated cleanup changes. Existing local edits
are intentional and user-owned. Preserve them and record relevant baseline state.

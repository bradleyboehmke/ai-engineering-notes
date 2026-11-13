---
status: accepted
date: 2026-11-13
---

# Path and Theme views are generated from the themes data file

Quarto listings display, sort, and filter on our custom fields natively
(`sort: [stage, theme]` works, and an empty stage sorts last), but they cannot
group a listing by a field, and Quarto cannot make one page per item of a data
file. So the Path view (grouped by theme) and the Theme views (one page per
theme) are built by a pre-render step, `scripts/views.lua`, that writes
`path.qmd` and `themes/*.qmd` from `data/themes.yml`. Each generated page is
still a native listing filtered to one theme; only the page scaffolding is
generated. Recent and the Type views are hand-written native listings. This
answers #1 and supersedes the "unverified" note in ADR-0001's organizing model.

The generated pages are build output (gitignored), so `data/themes.yml` stays
the single source: adding a theme adds its Path section and Theme page with no
other edit. The step is Lua, run by Quarto's bundled pandoc, so rendering needs
no Python, like `filters/page-layout.lua`.

Pages also gain a required `date` field (`YYYY-MM-DD`), which the Recent view
sorts on: Quarto lists an undated page as the newest, so an optional date
would silently misorder Recent.

## Considered options

- **Hand-written theme pages** (eight files, one listing each). Rejected: the
  theme list would live in two places, and the Path page would still need
  grouping by hand.
- **One Path table sorted by `[stage, theme]`**, no generation. Rejected: no
  group headings, the theme column shows slugs, and stageless themes would be
  ordered by slug spelling, not by `data/themes.yml`.
- **A pre-render step that writes listing data from page metadata.** Not
  needed: native listings already sort and filter on the metadata.
- **The generator in Python.** Rejected: full renders would then need the
  Python environment, which frozen code output otherwise lets us skip.

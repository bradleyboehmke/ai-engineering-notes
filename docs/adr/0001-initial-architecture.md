---
status: accepted
date: 2026-11-13
---

# Initial architecture

Founding ADR: it bundles the structural decisions made before the first commit,
so a future reader can see why the repo is shaped this way. Later ADRs each
cover a single decision; when one changes part of this record, mark that part
"superseded by ADR-NNNN" here.

## Form

One git repo of plain markdown and Quarto files, published as a Quarto
**website** (not a book) on GitHub Pages. Pages are non-linear: every page
stands alone, order is metadata, and views (Path, Theme, Recent, Type, plus a
hand-written Start Here) are generated from metadata with Quarto listings. A
book was rejected because it imposes a single reading order on content that is
meant to be entered anywhere.

## Content types and folders

Five page types: `topic`, `term`, `essay`, `prototype`, `tool`. Folders are by
**type** (`topics/`, `dictionary/`, `essays/`, `prototypes/`, `tools/`), with
theme held in metadata. Folders by theme were rejected: a folder fixes one
grouping forever, while metadata lets the same page appear in several views.

Working folders are in the repo but never rendered: `learning/<theme>/` (one
`/teach` workspace per theme), `notes/`, and `inbox/`.

## Organizing model

The **path** is a sequence of **stages**; each stage covers one **theme**, and
some themes have no stage. A **topic** belongs to exactly one theme;
cross-theme connections go through `prereqs`. Every topic is written through
two **lenses**, Practitioner and Leader (see `GLOSSARY.md`).

Page metadata:

```yaml
title: "LLM-as-judge evaluators"
type: topic          # topic, term, essay, prototype, tool
theme: evals         # one theme slug
stage: 3             # from the theme; blank for themes without a stage
lens: practitioner   # practitioner (default) or leader
prereqs: [eval-datasets, structured-output]
maturity: draft      # seed, draft, solid
video: ""            # optional YouTube URL
```

Pages also carry a required `date` (superseded by ADR-0002, which adds it).

~~Whether Quarto listings can display and sort on these custom fields is
unverified; it is tracked as an issue and tested during the site skeleton.~~
Superseded by ADR-0002: listings sort and filter on these fields natively; the
Path and Theme views are generated from `data/themes.yml` because listings
can't group.

## Openness and licensing

Public from the first commit. The "no work data" rule removes the main risk of
working in the open. Writing is CC BY 4.0 (`LICENSE`); code is MIT
(`LICENSE-CODE`), so code can be reused without attribution text in source files.

## Records and tracking

GitHub Issues for open questions, specs, and tickets (labels in
`docs/agents/triage-labels.md`). ADRs for decisions that are hard to reverse,
surprising, and a real trade-off. `GLOSSARY.md` for vocabulary. A single
`DECISIONS.md` brief was used for planning and then retired in favour of these,
so no catch-all decision file accumulates.

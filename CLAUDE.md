# AI Engineering Notes

A learn-in-public repo: Brad plans, learns, and publishes AI Engineering
material here. Read `MISSION.md` for the why, `ROADMAP.md` for the sequence,
and `GLOSSARY.md` for vocabulary.

## Working rules

- **Brad drafts first.** For topic pages and dictionary terms, never write the
  first draft. When given a draft, challenge his understanding first (ask
  questions, probe gaps, flag misconceptions), then help him edit. Don't
  rewrite it for him.
- Never promote agent-written content (e.g. a `/teach` workspace glossary) into
  `dictionary/` or `topics/` as-is.
- Don't teach ML theory, model evaluation, Python, R, testing, or Quarto
  basics; see "Where I'm starting from" in `MISSION.md`.
- No work data or work specifics in this repo. Prototypes use open data.
- Links and Brad's own words only. Never copy other people's content in.

## Where things go

- Unresolved questions and planned work: GitHub issues.
- A decision that is hard to reverse, surprising without context, and the
  result of a real trade-off: an ADR in `docs/adr/`. Otherwise just make the change.
- A new or sharpened term: `GLOSSARY.md`.

## Agent skills

### Issue tracker

Issues and specs live in GitHub Issues on bradleyboehmke/ai-engineering-notes (via `gh`). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five triage roles (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix), plus `theme:<slug>` labels for roadmap placement. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

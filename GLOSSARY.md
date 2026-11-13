# AI Engineering Notes

A learn-in-public system for upskilling in AI Engineering: planning what to
learn, learning it, and publishing what was learned as a website.

## Planning

**Path**:
The ordered sequence of stages in `ROADMAP.md`; the default order for learning.
_Avoid_: Practitioner track, curriculum

**Stage**:
One step of the path, with its own core concepts, a tool built for this repo,
and a contrast prototype.
_Avoid_: Module, phase, level

**Status**:
How far a stage has progressed: `planned`, `learning`, or `written`. Applies to
stages only.
_Avoid_: Using "status" for pages (see Maturity)

**Theme**:
A named area of AI Engineering that groups related topics (e.g. evals). Each
stage covers one theme; some themes have no stage.
_Avoid_: Category, umbrella, area

**Topic**:
One specific AI Engineering concept (e.g. eval-driven planning) given a
dedicated block of time: learned, applied in real code, and written up. Belongs
to exactly one theme.
_Avoid_: Learning topic, subject, lesson

**Lens**:
An angle applied to every topic: **Practitioner** (doing the engineering) or
**Leader** (leading AI engineers).
_Avoid_: Track

**Workspace**:
One `/teach` learning workspace per theme, at `learning/<theme>/`, holding the
lessons and records for that theme's topics. Not published.
_Avoid_: Course

## Publishing

**Topic page**:
The published write-up of a topic, in my own words, with runnable code.
_Avoid_: Article, post, note

**Term**:
One dictionary entry, in its own file under `dictionary/`: definition, related
terms, what to avoid, and a usage example.
_Avoid_: Definition, entry, glossary item

**Leader page**:
A standalone page written through the Leader lens, linked from the topic pages
it builds on.
_Avoid_: Leadership track page

**View**:
A published page that lists other pages, assembled from their metadata:
Path, Theme, Recent, or Type. Start Here is hand-written, not a view.
_Avoid_: Index, feed

**Maturity**:
How finished a published page is: `seed`, `draft`, or `solid`.
_Avoid_: Status (reserved for stages)

## Workflow

**Radar**:
The scheduled task that proposes posts and papers into `inbox/`.
_Avoid_: Feed, crawler

**Screening**:
Accepting or rejecting radar proposals in `inbox/` against the roadmap.
_Avoid_: Triage (reserved for issues), review

**Triage**:
Moving a GitHub issue through the triage labels in `docs/agents/triage-labels.md`.
_Avoid_: Screening (reserved for the inbox)

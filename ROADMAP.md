# Roadmap

Version 1. Stages are my private sequencing; the public site organizes pages by
theme. Order is a default, not a rule: if work needs a later stage sooner, move it.
Custom tools are built in stage order; each is that stage's deliverable.

Status values: `planned`, `learning`, `written`.

## Stages

Each stage covers one theme. The theme slug is used in page metadata, in
`learning/<theme>/`, and as the `theme:<slug>` issue label.

| Stage | Theme (slug) | Core concepts | Tool built for this repo | Contrast prototype (open data) | Status |
|---|---|---|---|---|---|
| 1 | LLM mechanics for builders (`llm-mechanics`) | Tokens, context windows, sampling, non-determinism, caching, cost | Dictionary seed; term auto-linker | Token and cost budget for a typical analytics question | planned |
| 2 | Building with model APIs (`model-apis`) | Structured output, tool calling, streaming, prompt and context design | `/define`: I draft a term, the agent challenges it and helps me edit and link it | Classify line items into a spend taxonomy | planned |
| 3 | Evals (`evals`) | Datasets, code-based and model-based graders, error analysis, regression checks in CI | Graders for `/define` output and radar picks | Golden questions with answers computed from the data | planned |
| 4 | Context engineering and retrieval (`context-and-retrieval`) | Embeddings, search, RAG, memory, semantic layers | Q&A over my own notes (document retrieval) | Text-to-SQL over a semantic layer (structured retrieval) | planned |
| 5 | Agents (`agents`) | Agent loop, tools, MCP, skills, subagents, sandboxing, long-running work | `/radar`: weekly curation of posts and papers into `inbox/` | Analyst agent with query tools | planned |
| 6 | Production (`production`) | Tracing, latency and cost, prompt injection and security, deployment as services | Scheduled radar with tracing and cost tracking; `/review` for spaced repetition | Access control; guarding against invented numbers | planned |

## Themes without a stage

Learned alongside the stages rather than in sequence.

| Theme (slug) | What it covers | Output |
|---|---|---|
| AI-assisted engineering (`ai-assisted-engineering`) | Working with coding agents: specs, handoffs, review | Practiced by building this repo; pages on what worked |
| Leading AI engineering teams (`leading-teams`) | Cross-cutting leadership: scoping, team standards, reviewing agent-written code, build versus buy | Leader pages that don't belong to a single theme |

Leader material tied to one theme (e.g. eval-driven planning) belongs to that
theme, not to `leading-teams`.

## Definition of done for a stage

1. Learned with `/teach` in `learning/<theme>/`, from cited primary sources.
2. Terms captured in `dictionary/` as I go.
3. The stage's tool is built and in use.
4. Topic pages drafted by me, standing alone, with prerequisites linked, each
   with a "Leading this" section.
5. Optional: a leader page, an essay, a prototype write-up, a video.

## Before Stage 1: site skeleton

A live site skeleton on GitHub Pages: one sample page of each type; the Path,
Theme, Recent, and Type views working from metadata; a link checker in CI; and
a Start Here page. Out of scope: the auto-linker, the radar, `/define`,
`/review`, and real learning content beyond the sample pages.

## Radar additions

New concepts the radar surfaces get added here as rows or as planned topics
under an existing theme, with a one-line reason tied to `MISSION.md`.

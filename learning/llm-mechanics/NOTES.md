# Notes

- Teaches ML at university level: skip ML basics, use ML analogies freely, and call out where ML intuitions mislead (steering via context, not training; non-determinism breaks "run once and check").
- Two lenses on everything: practitioner and leader (leads ML/optimization engineers). End lessons with a short leader angle.
- Provider-neutral, with Anthropic and OpenAI numbers side by side. Prices change: cite the pricing page and date every number.
- Hands-on: Python. Offline tokenizers first; real API calls only where the lesson needs them (variance, caching), kept cheap.
- ~30-minute lessons, ~5+ hrs/week.
- Repo rules (../../CLAUDE.md): this workspace's glossary/reference docs are never promoted into `dictionary/` or `topics/`. Brad drafts those himself; lessons should end by prompting him to draft the term or page section, not by drafting it.
- Term pages (Brad, 2026-11-15): a short, simple definition in a `.definition` callout at the top, then `## More context` for the full write-up, which can run long. Fuller term entries mean fewer, broader topic pages, so don't push the write-up shorter. Section order: More context, Usage example, What to avoid, Related terms.
- Term entries should point readers to try it themselves where possible (e.g. tiktokenizer, provider token-counting docs).
- The scope outline Brad gave on 2026-11-13 (five areas) is the starting map; see PATH.md.
- Term workflow that worked (2026-11-16): Brad drafts the term as a claude.ai artifact (sometimes refined with Claude's help), the teacher pulls it in with the Artifact tool and challenges it, then converts it into `dictionary/<term>.qmd` keeping his words verbatim (definition callout, `###` subsections under More context, escaped `$` signs, SVG figures in `dictionary/images/`). New terms also need adding to the hardcoded lists in `tests/test_views.py`.
- Each term should get a runnable Colab notebook in `experiments/` (like `count_tokens.ipynb`, `step_tokens.ipynb`): show the same code as the experiment script, use `# @param` form fields for reader input, and visualize the result where possible. Linked from the term's Usage example.
- Lesson progress: lessons 1–3 done; Token, Tokenizer, Next-token prediction, Context window drafted (Context window converted 2026-11-18, not yet committed). Next: lesson 4, base model vs assistant.
- Environment: the venv is at the repo root (`../../.venv`). No Anthropic/OpenAI SDK or API key in it as of 2026-11-16, so API numbers come from Brad's runs. HF `model.generate()` crashes (SIGBUS) with the installed torch build; use the hand-written loop from `step.py`/`limits.py`.
- Open repo follow-ups (not learning work; file as GitHub issues if not done): backlinks from Token/Tokenizer to Next-token prediction; GLOSSARY entries for Essay, Prototype, Tool; move sample pages into test fixtures.
- Dictionary widgets live in `dictionary/widgets/` and need `resources:` in the page front matter so Quarto copies them; `context-budget.js` takes data-models / data-presets attributes for reuse.

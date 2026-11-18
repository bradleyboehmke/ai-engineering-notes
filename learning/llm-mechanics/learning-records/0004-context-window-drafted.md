# Lesson 3 done: Context window drafted, errors vs stop reasons now distinct

Brad finished lesson 3, ran `limits_api.py` (including `--overflow`), and drafted the Context window entry as a claude.ai artifact (2026-11-18), refined with AI help and revised after one round of review. It's converted to `dictionary/context-window.qmd` with a Colab notebook (`context_limits.ipynb`) and the reusable budget widget (`dictionary/widgets/context-budget.*`).

**Solid**: input and output share one budget, with thinking included; `max_tokens` is a ceiling, not a target length (he used his own 425-of-1,024 run as the evidence); caching changes cost, not capacity; fitting isn't the same as working well, with no published safe fill level. He extended the lesson on his own to tool results as external context and to thinking blocks carried across turns.

**Corrected in review**:
- *Own words*: the first definition copied Anthropic's sentence, and said "text" when images count too. His rewrite ("the cap on how many tokens a single request can use in total") is his own and more precise.
- *Errors vs stop reasons*: the draft listed the 400 alongside `max_tokens` and `end_turn` as "ways a request ends". When asked, he regrouped them into responses you check (HTTP 200, `stop_reason`) and requests that raise (HTTP 400, `try`/`except`). He first called a 429 "a third kind"; it's the same bucket, with a different fix (wait and retry, not fix the request).
- *Evidence vs claim*: he cited his run as the reason to leave a counting margin, though `count_tokens` had overcounted. Once asked, he separated it: the docs calling the count an estimate justifies the margin, and output needing its own room is a second reason.

**Implications**: Lesson 4 (base model vs assistant) can build on the GPT-2 observation from lesson 3, where the base model never chose end-of-text. Keep asking "what does your data actually show?" when he cites a run, because that's where the one slip came from. He wants provider-neutral pages, so keep OpenAI numbers in every lesson. The budget widget is reusable for lesson 10 (a growing conversation) and lesson 15.

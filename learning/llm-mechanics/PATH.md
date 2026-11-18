# Path: LLM mechanics (proposed; Brad edits)

Sixteen ~30-minute lessons in four blocks, about four weeks at 5+ hrs/week. Each lesson ends with one tangible win and a prompt for **you** to draft the dictionary terms it introduced. Checkpoints are where you draft a topic page.

The five areas from your outline are kept, with two changes:
- **Area 4 (where behaviour comes from) moves earlier.** Post-training explains roles, system prompts, and refusals, so it's taught before "what a request is".
- **Non-determinism gets its own lesson.** Sampling explains only part of it; temperature 0 is still not reproducible.

## Block A: Text in, text out (week 1)

| # | Lesson | Win | Experiment | Primary source |
|---|---|---|---|---|
| 1 | Tokens are the unit of everything | Predict roughly how many tokens a document is, and why non-English, code, and numbers cost more | Count tokens for 3 real documents with tiktoken; compare to word counts | Karpathy, tokenizer video |
| 2 | The generation loop | Explain next-token prediction as repeated softmax over a vocabulary, conditioned on all prior tokens | Step a small local model token by token, printing top-5 probabilities | Karpathy, Deep Dive |
| 3 | Context window and output limits | Budget a request: input + output ≤ context window, and output ≤ max output | Hit `max_tokens` on purpose; read the stop reason | Provider docs |

## Block B: Where behaviour comes from (week 1–2)

| # | Lesson | Win | Experiment | Primary source |
|---|---|---|---|---|
| 4 | Base model vs assistant | Explain why a base model continues text but an assistant answers it | Same prompt to a base model and an instruct model | Karpathy, Deep Dive (post-training) |
| 5 | Reasoning models | Explain thinking tokens and why they're billed as output | One question with thinking off vs on; compare usage | Anthropic extended thinking docs |
| 6 | Model tiers | Pick a tier for a task by capability, latency, and price | Same task on two tiers; compare quality, time, and cost | Provider model pages |

**Checkpoint 1:** draft ~8 terms (token, tokenizer, next-token prediction, context window, base model, post-training, reasoning model, model tier).

## Block C: Why outputs vary (week 2–3)

| # | Lesson | Win | Experiment | Primary source |
|---|---|---|---|---|
| 7 | Sampling: temperature and top-p | Explain temperature as softmax scaling and top-p as truncation, and when to change each | Run one prompt 20× at three temperatures; measure output variance | Huyen ch. 2; HF "How to generate text" |
| 8 | Non-determinism beyond sampling | Explain why temperature 0 still varies, and what that means for testing | Run temperature 0 twenty times; count distinct outputs | Thinking Machines |
| 9 | Hallucination and knowledge cutoff | Explain hallucination as plausible-text prediction plus evals that reward guessing | Ask about post-cutoff events and obscure facts; label the failures | OpenAI, "Why LMs Hallucinate" |

**Checkpoint 2:** draft topic page "Why outputs vary". Its "Leading this" section is the bridge to evals: why "run it once and check" stops working.

## Block D: What a request is, and what it costs (week 3–4)

| # | Lesson | Win | Experiment | Primary source |
|---|---|---|---|---|
| 10 | Statelessness and messages | Show that a conversation is the full history resent every call, and how roles become one sequence | Log token usage across a 5-turn chat; watch input grow | Chat template docs (gap) |
| 11 | Multimodal input | Estimate tokens for an image or PDF in context | Send one image; read usage | Provider vision docs |
| 12 | Pricing | Compute one request's cost from usage, and why output tokens cost more | Price lessons 10–11's logs by hand | Anthropic + OpenAI pricing |
| 13 | Prompt caching | Structure a prompt so the stable prefix caches; predict the saving | Repeat a long-prefix request; read cache usage fields | Anthropic + OpenAI caching docs |
| 14 | Batch and the other cost levers | Rank the levers: tier, output length, caching, batch, context size | Recost lesson 12 under each lever | Provider batch docs |
| 15 | Latency and long-context degradation | Explain TTFT vs tokens/sec, streaming, rate limits, and why more context isn't free | Time a long vs short context; stream vs not | Lost in the Middle; Context Rot |
| 16 | Prototype: cost calculator | Estimate tokens, cost, and latency for a typical analytics question | Build it (Python, open data) | All of the above |

Planned additions (2026-11-18):
- **Lesson 10** introduces compaction as the response to a growing history: what it is (earlier turns summarized server-side), that it's lossy, and that summarizing costs tokens. *How* to compact well is Stage 4.
- **Lesson 15** tests the "keep context under 100–200K even on 1M models" folklore: measure accuracy against context length on one task instead of adopting a number. No primary source gives a threshold (Context Rot finds gradual, model- and task-dependent degradation), and practitioners disagree (Dex Horthy reportedly uses ~300–400K). Supplementary listening: the Dex Horthy episode.

**Checkpoint 3:** draft topic pages "Text in, text out" and "What a request costs", plus the remaining ~20 terms.

## Corrections to the outline worth testing yourself on

- "Caching and batch are the two main cost levers": model tier and output length often matter more (lesson 14 ranks them).
- "Variance comes from sampling": also from inference batching at temperature 0 (lesson 8).
- "Token counts are universal": each provider's tokenizer differs, so the same text has different counts and costs.

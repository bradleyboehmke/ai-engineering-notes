# LLM Mechanics Resources

Prices and limits change often. Every number used in a lesson cites the page and the date it was read.

## Knowledge

### Foundations (areas 1, 2, 4)

- [Video: "Deep Dive into LLMs like ChatGPT" by Andrej Karpathy (2025)](https://www.youtube.com/watch?v=7xTGNNLPyMI)
  ~3.5 h general-audience walkthrough: pretraining data → tokenization → base model → post-training (SFT, RLHF) → reasoning models. Use for: next-token prediction, pretraining vs post-training, why models hallucinate, "personality". Watch in chunks; skip the parts on neural net basics.
- [Video: "Let's build the GPT Tokenizer" by Andrej Karpathy (2024)](https://www.youtube.com/watch?v=zduSFxRajkE) · [text version on fast.ai](https://fast.ai/posts/2025-10-16-karpathy-tokenizers) · [minbpe lecture notes](https://github.com/karpathy/minbpe/blob/master/lecture.md)
  BPE tokenization from scratch, and why many LLM quirks (arithmetic, spelling, non-English cost) trace back to tokens. Use for: tokens lesson. The first ~20 min and the "why is this weird" sections are enough; the build is optional.
- [Podcast: SuperDataScience 626, "Subword Tokenization with Byte-Pair Encoding" (Jon Krohn, 2022)](https://www.superdatascience.com/626)
  _Optional._ Short audio explanation of how BPE builds its vocabulary by merging frequent pairs. Use for: reinforcing lesson 1 away from a screen; why bigger vocabularies help common text but not rare words.
- [Podcast: TWIML AI #724, "Dynamic Token Merging for Efficient Byte-level Language Models" with Julie Kallini (2025)](https://twimlai.com/podcast/twimlai/dynamic-token-merging-for-efficient-byte-level-language-models)
  _Optional, research-level._ Byte-level models that drop a fixed tokenizer; show notes reference Meta's Byte Latent Transformer. Use for: where tokenization is heading. Not needed for build decisions today.
- [Book: _AI Engineering_ by Chip Huyen (O'Reilly, 2025), ch. 2 "Understanding Foundation Models"](https://www.oreilly.com/library/view/ai-engineering/9781098166298/)
  Practitioner-level treatment of training data, post-training, and sampling (temperature, top-k, top-p, test-time compute, the probabilistic nature of AI). Use for: the sampling and post-training lessons; the best single book for this stage.
- [Article: "How to generate text" (Hugging Face blog, 2020, edited 2023)](https://huggingface.co/blog/how-to-generate)
  Greedy, beam, top-k, top-p sampling with runnable `transformers` code. Use for: the sampling experiment with a small local model.

- [Docs: "Text generation" (Hugging Face Transformers)](https://huggingface.co/docs/transformers/llm_tutorial)
  The generation loop in one sentence (the model's own outputs fed back until EOS or a length limit), and the `max_new_tokens` default of 20. Use for: lesson 2 and the stop conditions in lesson 3.
- [Docs: "How caching works" (Hugging Face Transformers)](https://huggingface.co/docs/transformers/cache_explanation)
  Why the KV cache exists in autoregressive generation, and that its memory grows linearly with sequence length. Use for: lesson 2's builder angle; long-context cost in lesson 15.
- [Article: "Mastering LLM Techniques: Inference Optimization" (NVIDIA, Verma & Vaidya, 2023)](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/)
  Prefill (parallel over the prompt) vs decode (one token at a time, memory-bound), plus KV caching and batching. Use for: why output is slower than input; lessons 2, 12, 15.

### Base models and post-training (lesson 4, 10)

- [Docs: "Chat templates" (Hugging Face Transformers)](https://huggingface.co/docs/transformers/chat_templating)
  All causal LMs continue a token sequence; how messages become one string with control tokens; `add_generation_prompt`; wrong control tokens give "drastically worse performance". Use for: lesson 4; fills the chat-template gap for lesson 10.
- [Paper: "Training language models to follow instructions with human feedback" (InstructGPT, Ouyang et al., 2022)](https://arxiv.org/abs/2203.02155)
  SFT + RLHF; labelers preferred 1.3B InstructGPT to 175B GPT-3. Use for: why post-training matters more than scale for following intent.
- [Model: SmolLM2-360M](https://huggingface.co/HuggingFaceTB/SmolLM2-360M) · [-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct) · [smol-smoltalk](https://huggingface.co/datasets/HuggingFaceTB/smol-smoltalk)
  Matched base/instruct pair (4T pretraining tokens; SFT on 484,570 conversations, then DPO). Use for: the lesson 4 experiment, offline.
- [OpenAI: Harmony response format (gpt-oss)](https://developers.openai.com/cookbook/articles/openai-harmony)
  OpenAI's published chat format and special tokens for its open-weight models; API providers apply it for you. Use for: a provider example of roles-as-tokens.

### Reasoning models (lesson 5)

- [Paper: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning" (DeepSeek-AI, 2025)](https://arxiv.org/abs/2501.12948)
  Reasoning built through pure RL without human-labeled reasoning trajectories; self-reflection and verification emerge. Use for: where thinking behaviour comes from (lesson 5).
- [Anthropic: Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) · [Steering thinking (pricing section)](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost#pricing) · [Effort](https://platform.claude.com/docs/en/build-with-claude/effort)
  Adaptive thinking, `display` (omitted default on Claude 5 models; summaries come from a different model; raw chain of thought never returned), billed vs visible output, `usage.output_tokens_details.thinking_tokens`, prior-turn thinking billed as input on keep-all models, effort levels and per-model defaults (read 2026-11-25). Use for: lesson 5; the "Extended thinking" page is now legacy (`budget_tokens`).
- Karpathy Deep Dive (above), chapters from 2:07:28 (SFT to RL, RL, DeepSeek-R1, AlphaGo) to 2:48:26. Use for: lesson 5's primary source.

### Variance and reliability (area 2, 5)

- [Article: "Defeating Nondeterminism in LLM Inference" (Thinking Machines, 2025)](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)
  Why temperature 0 still isn't reproducible: batch-variant GPU kernels, not just floating point. Use for: correcting "temperature 0 = deterministic".
- [Paper: "Why Language Models Hallucinate" (OpenAI, Kalai et al., 2025)](https://openai.com/index/why-language-models-hallucinate/)
  Hallucination as a consequence of pretraining on unpredictable facts plus evals that reward guessing. Use for: the hallucination lesson; strong bridge to Stage 3 (evals), which is your edge.
- [Paper: "Lost in the Middle: How Language Models Use Long Contexts" (Liu et al., TACL 2024)](https://arxiv.org/abs/2307.03172)
  Accuracy drops when relevant information sits mid-context, and as context grows. Use for: long-context degradation.
- [Report: "Context Rot" (Chroma Research, 2025)](https://www.trychroma.com/research/context-rot)
  18 models degrade as input grows, even on simple tasks; needle-in-a-haystack overstates real performance. No token threshold: degradation is gradual and "non-uniform", varying by model and task (checked 2026-11-18). Tested Claude 4 / GPT-4.1-era models, so re-measure on current ones. Use for: long-context degradation; a newer complement to Lost in the Middle; testing "keep context under 100–200K" folklore in lesson 15.

### Context windows and context engineering (lessons 3, 10, 15; Stage 4)

Podcast notes below come from show notes and summaries; marked _not yet listened_ until Brad has heard them.

- [Article: "What Is The Context Window?" (AI Hero, updated 2025-09-30)](https://www.aihero.dev/what-is-the-context-window)
  _Optional._ Short introduction: the window is input and output combined, it grows with the conversation, a hard limit per model, lost-in-the-middle. No thinking tokens or compaction. Use for: a lighter first read before lesson 3's Anthropic source.
- [Podcast: Embedded AI Podcast E05, "Context Management" (Dec 2025, ~46 min)](https://podcasts.apple.com/podcast/id1846828445)
  _Optional, not yet listened._ Foundational: tokens, how context windows work, why more context isn't better, edge/recency effects, when to start a new session. Use for: lesson 3 away from a screen.
- [Podcast: The Pragmatic Engineer, "Context engineering with Dex Horthy" (Jul 2026, ~92 min)](https://newsletter.pragmaticengineer.com/p/context-engineering-with-dex-horthy)
  _Not yet listened._ Practitioner view on degradation as context grows ("smart zone" vs "dumb zone"), intentional compaction, context vs harness engineering. Summaries say he runs 1M models to ~300–400K and smaller ones to ~100K: a heuristic, not a measurement. Use for: lesson 15; Stage 4.
- [Podcast: Latent Space, "Context Engineering for Agents" with Lance Martin (Sep 2025, ~57 min)](https://www.latent.space/p/context-engineering-for-agents-lance)
  _Not yet listened._ Five categories of context engineering: offloading, reducing, retrieval, isolation, caching; from building Open Deep Research. Use for: Stage 4 (out of scope for Stage 1).

### Requests, cost, and latency (areas 3, 5): provider docs

- [Anthropic: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
  Per-model input/output prices, cache write/read multipliers, batch discount, long-context pricing. Use for: the cost calculator.
- [Anthropic: Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  Explicit cache breakpoints, 5-min and 1-hour TTLs, prefix matching. Use for: the caching lesson.
- [Anthropic: Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
  Thinking tokens are billed as output, count toward `max_tokens`, and how they're billed across turns. Use for: reasoning-model cost.
- [OpenAI: Prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching) · [Cookbook: Prompt Caching 201](https://developers.openai.com/cookbook/examples/prompt_caching_201)
  Automatic caching above 1,024 tokens, exact-prefix matching, measuring `cached_tokens`. Use for: contrasting implicit (OpenAI) vs explicit (Anthropic) caching.
- [Anthropic: Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
  Definition (includes the response itself), what counts toward the window, thinking as a subset of `max_tokens`, context rot, and overflow behaviour (400 when input alone is too long; `model_context_window_exceeded` on Claude 4.5+). Use for: lesson 3's primary source; lesson 15.
- [Anthropic: Stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons)
  Every `stop_reason` value with handling, the continuation pattern for truncated replies. Use for: lesson 3; Stage 2 (`tool_use`, `refusal`).
- [Anthropic: Models overview](https://platform.claude.com/docs/en/about-claude/models/overview) · [OpenAI: Models](https://developers.openai.com/api/docs/models)
  Context window and max output per model (read 2026-11-16: Claude current models 1M / 128K; OpenAI GPT-6 family 1.05M / 128K). Anthropic also gives 1M tokens ≈ 555K words ≈ 2.5M chars on its current tokenizer. Use for: lessons 3 and 6.
- [OpenAI: Reasoning models](https://developers.openai.com/api/docs/guides/reasoning)
  `max_output_tokens` includes reasoning tokens; `status: "incomplete"` when hit; costs with no visible output; reserve ≥25K tokens to start. Use for: lessons 3 and 5.
- [Anthropic: Task budgets](https://platform.claude.com/docs/en/build-with-claude/task-budgets)
  `max_tokens` is the enforced, truncating limit; a task budget is an advisory countdown the model paces against. Use for: lesson 3's "max_tokens is a cut, not a hint".
- [OpenAI Help: "What are tokens and how to count them"](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them)
  The standard rules of thumb (1 token ≈ 4 chars ≈ ¾ word) and their limits, including request overhead. Use for: first-pass estimates.
- [Anthropic: Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
  `count_tokens` endpoint: full-message input count (system, tools, images, PDFs), an estimate, free but rate-limited. Use for: counting Claude tokens (the documented method; tiktoken counts are only approximate for Claude).
- [Paper: "Language Model Tokenizers Introduce Unfairness Between Languages" (Petrov et al., NeurIPS 2023)](https://arxiv.org/abs/2305.15425)
  Same text varies up to 15× in token length across languages, over 17 tokenizers. Use for: multilingual cost and context.
- [OpenAI: tiktoken](https://github.com/openai/tiktoken) · [tiktokenizer (interactive)](https://tiktokenizer.vercel.app)
  Offline tokenizer for OpenAI models; the web tool shows token boundaries live. Use for: the token-counting experiment.

## Wisdom (Communities)

- [Latent Space Discord](https://www.latent.space/community)
  The AI Engineer community around the Latent Space podcast; weekly LLM Paper Club. Use for: sanity-checking cost/latency trade-offs and model-tier choices with practitioners.
- [OpenAI Developer Community](https://community.openai.com) · Anthropic's developer Discord (link from the Claude docs)
  Provider forums where pricing, caching, and rate-limit behaviour get discussed by people hitting them in production. Use for: "is this caching behaviour expected?" questions.

## Gaps

- **Provider-neutral latency numbers** (time to first token, tokens/sec by model tier): no primary source yet; independent benchmarks (e.g. Artificial Analysis) need vetting before use.
- **OpenAI pricing and Batch API pages**: not yet read; needed for side-by-side numbers.
- **Messages → token sequence (chat templates)**: filled by the HF chat templates guide (2026-11-18). Anthropic and OpenAI don't publish their hosted models' formats.
- **Model tiers**: provider model-overview pages for the current family trade-offs.

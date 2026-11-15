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

### Variance and reliability (area 2, 5)

- [Article: "Defeating Nondeterminism in LLM Inference" (Thinking Machines, 2025)](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)
  Why temperature 0 still isn't reproducible: batch-variant GPU kernels, not just floating point. Use for: correcting "temperature 0 = deterministic".
- [Paper: "Why Language Models Hallucinate" (OpenAI, Kalai et al., 2025)](https://openai.com/index/why-language-models-hallucinate/)
  Hallucination as a consequence of pretraining on unpredictable facts plus evals that reward guessing. Use for: the hallucination lesson; strong bridge to Stage 3 (evals), which is your edge.
- [Paper: "Lost in the Middle: How Language Models Use Long Contexts" (Liu et al., TACL 2024)](https://arxiv.org/abs/2307.03172)
  Accuracy drops when relevant information sits mid-context, and as context grows. Use for: long-context degradation.
- [Report: "Context Rot" (Chroma Research, 2025)](https://research.trychroma.com/context-rot)
  18 models degrade as input grows, even on simple tasks; needle-in-a-haystack overstates real performance. Use for: long-context degradation; a newer complement to Lost in the Middle.

### Requests, cost, and latency (areas 3, 5): provider docs

- [Anthropic: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
  Per-model input/output prices, cache write/read multipliers, batch discount, long-context pricing. Use for: the cost calculator.
- [Anthropic: Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  Explicit cache breakpoints, 5-min and 1-hour TTLs, prefix matching. Use for: the caching lesson.
- [Anthropic: Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
  Thinking tokens are billed as output, count toward `max_tokens`, and how they're billed across turns. Use for: reasoning-model cost.
- [OpenAI: Prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching) · [Cookbook: Prompt Caching 201](https://developers.openai.com/cookbook/examples/prompt_caching_201)
  Automatic caching above 1,024 tokens, exact-prefix matching, measuring `cached_tokens`. Use for: contrasting implicit (OpenAI) vs explicit (Anthropic) caching.
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
- **Messages → token sequence (chat templates)**: need a primary source (e.g. Hugging Face chat templating docs) showing how roles become one sequence.
- **Model tiers**: provider model-overview pages for the current family trade-offs.

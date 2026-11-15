# Mission: LLM mechanics for builders

## Why
I build on LLMs and lead ML/optimization engineers who do too, but my grasp of how a model behaves as a component (and what it costs) is loose. I want to make and review build decisions on tokens, context, sampling, caching, and cost from understanding, not folklore, and publish that understanding as Stage 1 of my AI Engineering path.

## Success looks like
- Estimate the tokens, cost, and latency of an LLM feature (e.g. a typical analytics question) before it's built, and build the cost calculator that does it
- Explain to my team why the same prompt gives different answers, why models hallucinate, and why a "conversation" is resent every call
- Review a teammate's LLM design and spot mechanics mistakes: unbounded context, sampling misuse, missed caching, wrong model tier
- Write ~25–30 dictionary terms and 3–4 topic pages in my own words, each with a "Leading this" section

## Constraints
- ~5+ hours/week; lessons of ~30 minutes
- Provider-neutral concepts, with concrete numbers from Anthropic and OpenAI side by side
- Experiments: offline tokenizers where possible, a handful of real API calls (small spend) for variance and caching
- Strong in ML theory, evaluation, Python, teaching: don't re-teach those
- I draft dictionary terms and topic pages myself; lessons inform them, they don't replace them

## Out of scope
- Training or fine-tuning models; transformer internals beyond a light attention refresher
- Building with APIs in depth (structured output, tool calling): Stage 2
- Retrieval and context engineering techniques: Stage 4

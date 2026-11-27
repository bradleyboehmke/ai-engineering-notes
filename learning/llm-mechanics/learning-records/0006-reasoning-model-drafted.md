# Lesson 5 done: Reasoning model drafted, with his own runs as evidence

Brad finished lesson 5, ran `thinking_api.py` twice on Claude Haiku 5.5 (2026-11-25), and drafted Reasoning model as a claude.ai artifact (https://claude.ai/artifact/1BeCTNMV3L5uWUorNKeKZS). After one review round it was converted to `dictionary/reasoning-model.qmd` (2026-11-27), with the calculator as `dictionary/widgets/thinking-cost.*` and a Colab notebook (`thinking_api.ipynb`, user-supplied API key, `REPEATS` setting).

**Solid**: thinking as more of the same loop, with earlier tokens becoming context; reasoning as further post-training through RL; thinking billed as output whether shown or not, read from `output_tokens_details.thinking_tokens` / `reasoning_tokens`; summaries come from a different model and aren't audit trails (he found arXiv 2505.05410 on his own). He chose "thinking tokens" as the main term and "reasoning tokens" as the alias. He kept thinking tokens and effort inside this one entry, which fits his "fewer, broader pages" preference.

**Corrected in review**:
- *Evidence vs claim (again)*: the first draft read "effort isn't a fixed dial" from one sample per setting. Asked what his data showed, he rewrote it: run-to-run spread (medium 419 vs 480) swamps the effort gaps on an easy question, and his runs don't test the docs' "soft signal" claim. This is the second entry where "what does your data actually show?" changed the claim, so keep asking it.
- *Per-model facts*: "Sonnet 5.5 can't turn thinking off" was wrong (`between_tools`). He fixed it in all three places.
- *Unsourced claims*: "most modern models reason" is now marked as his view. The OpenAI "GPT-6.2 rejects `none`" claim, which he'd added, turned out to be in the guide's "Reasoning effort" section. My first read had missed that section, so verify before flagging a claim as unsourced.
- *Failure mode*: he added `max_tokens` exhaustion by thinking to the cost section and to "What to avoid".

**Left as he chose**: the per-model turn-off rules appear in three places (two callouts and "What to avoid"). I flagged it, and he didn't change it.

**Implications**: Lesson 6 (model tiers) should build on his "effort before a bigger model" angle and on the model-selection entry he deferred. Reuse `thinking-cost.js` (it takes `data-models` / `data-presets`) and the notebook's repeats pattern there. Lesson 8 (non-determinism) can open with his own medium 419 vs 480 spread.

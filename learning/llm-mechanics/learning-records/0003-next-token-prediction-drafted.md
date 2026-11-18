# Lesson 2 done: next-token prediction drafted, two ideas still forming

Brad drafted the next-token prediction entry (as a claude.ai artifact, 2026-11-16) and revised it after one round of review. The mechanics are solid: logits → softmax → choose → append, the model and the choosing rule as separate jobs, one token committed per pass, and the parallel-prefill / serial-decode asymmetry for latency. He separated per-token billing from the higher output price on his own once prompted, and correctly scoped the term to inference while naming the pretraining objective.

**Still forming**:
- *Variance*: when asked whether sampling is the only source of different replies, he answered about sampling's purpose, not about temperature-0 variance. He accepted "one reason" without engaging the batching cause. Lesson 8 should start by asking him to predict temperature-0 repeatability before showing it.
- *Hallucination*: his first answer called any fabricated figure from a vague prompt a hallucination ("generalizing over the training data"). He switched to the context-contradicting Q1/Q2 example after pushback. Lesson 9 should test the boundary: fabrication with no true answer vs a confident claim against available facts.

**Implications**: Lesson 3 (context window and output limits) can build directly on the loop and the end-of-text / max-token stop conditions. He uses the experiment output as evidence in his writing, so keep giving him numbers he can cite.

**Update (2026-11-16, end of session)**: after a second review he hedged the latency claim himself ("usually matters more"), recognizing that prefill isn't free for very long prompts. The entry was published as `dictionary/next-token-prediction.qmd` (PR #15) with a Colab notebook. Lesson 3 is next; lesson 15 should return to when prompt size dominates latency (time to first token).

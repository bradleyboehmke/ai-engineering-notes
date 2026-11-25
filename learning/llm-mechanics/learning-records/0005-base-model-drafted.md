# Lesson 4 done: Base model & post-training drafted as one entry

Brad finished lesson 4 and drafted Base model & post-training as a single combined entry (claude.ai artifact, 2026-11-24), converted to `dictionary/base-model.qmd` with a Colab notebook (`base_vs_assistant.ipynb`). He chose one page for both terms, which fits his "fewer, broader pages" preference.

**Solid**: pre-training as one job (next-token prediction) that yields an auto-completer; the assistant as the same network trained further; stopping as a learned end token; demonstration (SFT) vs comparison (RLHF, DPO); knowledge mostly from pre-training, behaviour from post-training. He went past the lesson on his own: real post-training data (InstructGPT section pointers, oasst1), prefill now limited on newer Claude models, and how an API request rebuilds the post-training format.

**Settled in review**:
- *Definition*: his first wording ("conversations people wrote or ranked") was narrower than what he knows. Asked, he said who writes the data varies (people, AI-assisted, synthetic) and the point is additional data that shifts behaviour toward a chat assistant. The definition now says that.
- *Why it answers, not just why it stops*: he judged that showing `<|im_start|>` beside `<|im_end|>` lets readers infer the opening marker's role, and kept the text as is. Unverified whether readers will make that inference; lesson 10 (messages and chat templates) can revisit the opened assistant turn explicitly.
- *Scope and voice*: he kept the Chat app vs API section here as an introduction, owns "judging is easier than writing" as his view, and wants the site provider-neutral overall while single pages may focus on one provider. Don't relitigate these.

**Implications**: Lesson 5 (reasoning models) can build on post-training (RL beyond preference tuning). When he cites a claim without a source, accept "my view" framing rather than pushing for a citation. He prefers the agent to carry out mechanical edits once decisions are made ("make the edits we agreed on"), so after the challenge round, offer to do the conversion.

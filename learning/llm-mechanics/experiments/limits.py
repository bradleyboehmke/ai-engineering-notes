"""Hit both limits of the generation loop on purpose, offline, with GPT-2.

Usage: python limits.py

GPT-2's context window is 1,024 tokens, small enough to hit in seconds.
Three runs:
  1. A max-token limit cuts the answer off mid-thought.
  2. A long prompt leaves little room: input and output share one window.
  3. One token past the window, and the model can't run at all.

The loop is the one from step.py (lesson 2), plus a reason for stopping.
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

tok = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
model.eval()

WINDOW = model.config.n_positions                # 1,024 for GPT-2
print(f"Context window: {WINDOW} tokens")
print(f"Position table: {tuple(model.transformer.wpe.weight.shape)}"
      " (one learned row per position)\n")


def generate(ids, max_tokens):
    """Greedy loop that reports why it stopped, like an API's stop reason."""
    start = ids.shape[1]
    while True:
        if ids.shape[1] - start >= max_tokens:
            return ids, "max_tokens"             # your limit
        if ids.shape[1] >= WINDOW:
            return ids, "context_window"         # the model's limit
        with torch.no_grad():
            next_id = model(ids).logits[0, -1].argmax().view(1, 1)
        ids = torch.cat([ids, next_id], dim=1)
        if next_id.item() == tok.eos_token_id:
            return ids, "end_of_text"            # the model chose to stop


def report(label, ids, max_tokens):
    out, reason = generate(ids, max_tokens)
    new = out[0, ids.shape[1]:]
    print(f"{label}")
    print(f"   input {ids.shape[1]} + max_tokens {max_tokens}"
          f" -> generated {len(new)}, stop reason: {reason}")
    print(f"   ends with: {tok.decode(new)[-70:]!r}\n")


prompt = ("Here is a detailed, step-by-step guide to cleaning a messy "
          "sales dataset in Python:\n\n1.")
ids = tok(prompt, return_tensors="pt").input_ids

# 1. Your limit: the answer is cut off, not finished.
report("Run 1: short prompt, max_tokens=20", ids, 20)

# 2. Shared window: a 1,000-token prompt leaves 24 tokens for output.
long_ids = ids.repeat(1, 50)[:, :1000]
report("Run 2: 1,000-token prompt, max_tokens=100", long_ids, 100)

# 3. Past the window: position 1,025 has no row in the table.
over = ids.repeat(1, 50)[:, :WINDOW + 1]
print(f"Run 3: one forward pass on {over.shape[1]} tokens")
try:
    with torch.no_grad():
        model(over)
    print("   ran (unexpected)")
except IndexError as e:
    print(f"   IndexError: {e}")

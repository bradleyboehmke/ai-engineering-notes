"""Step a small local model through the generation loop, one token at a time.

Usage: python step.py "Your prompt here" [steps]

At each step the model scores every token in its vocabulary, softmax turns
those scores into probabilities, we print the top 5, pick the most likely
one (greedy), append it, and go again.
"""
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

prompt = sys.argv[1] if len(sys.argv) > 1 else "The quarterly revenue increased by"
steps = int(sys.argv[2]) if len(sys.argv) > 2 else 8

tok = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
model.eval()

ids = tok(prompt, return_tensors="pt").input_ids
print(f"Prompt: {prompt!r} ({ids.shape[1]} tokens)\n")

for step in range(1, steps + 1):
    with torch.no_grad():
        logits = model(ids).logits[0, -1]       # one score per vocabulary token
    probs = torch.softmax(logits, dim=-1)        # scores -> probability distribution
    top = torch.topk(probs, 5)

    print(f"Step {step}: context is {ids.shape[1]} tokens")
    for p, i in zip(top.values, top.indices):
        print(f"   {p.item():6.1%}  {tok.decode(i)!r}")

    next_id = top.indices[:1].view(1, 1)        # greedy: take the most likely
    ids = torch.cat([ids, next_id], dim=1)      # append, then loop
    if next_id.item() == tok.eos_token_id:
        print("   -> end-of-text token: stop")
        break
    print(f"   -> picked {tok.decode(next_id[0])!r}\n")

print("Result:", repr(tok.decode(ids[0])))

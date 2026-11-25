"""One question, two models: a base model and the same model after post-training.

Usage: python base_vs_assistant.py ["Your question"] [max_tokens]

SmolLM2-360M is a base model. SmolLM2-360M-Instruct is the same network after
post-training. For each, print the top 5 guesses for the first token, then
let it write up to max_tokens with greedy decoding and report why it stopped.

The base model gets the bare question. The assistant gets it through its chat
template, the way a chat app or API would send it.
"""
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PROMPT = sys.argv[1] if len(sys.argv) > 1 else "What is the capital of France?"
MAX_TOKENS = int(sys.argv[2]) if len(sys.argv) > 2 else 60


def load(name):
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(name).eval()
    return tok, model


def top5(tok, model, ids):
    """The model's five most likely next tokens, with probabilities."""
    with torch.no_grad():
        probs = model(ids).logits[0, -1].softmax(-1)
    top = torch.topk(probs, 5)
    return [(tok.decode(i), p.item()) for p, i in zip(top.values, top.indices)]


def generate(tok, model, ids, max_tokens=MAX_TOKENS):
    """Greedy loop: pick the top token, append it, repeat. Returns why it stopped."""
    end_tokens = {tok.eos_token_id, tok.convert_tokens_to_ids("<|im_end|>")}
    start = ids.shape[1]
    for _ in range(max_tokens):
        with torch.no_grad():
            next_id = model(ids).logits[0, -1].argmax().view(1, 1)
        ids = torch.cat([ids, next_id], dim=1)
        if next_id.item() in end_tokens:
            return tok.decode(ids[0, start:]), ids.shape[1] - start, "end token"
    return tok.decode(ids[0, start:]), max_tokens, "max_tokens"


def run(label, tok, model, text):
    ids = tok(text, return_tensors="pt", add_special_tokens=False).input_ids
    print(f"=== {label} ===")
    for t, p in top5(tok, model, ids):
        print(f"  {p:6.1%}  {t!r}")
    out, n, reason = generate(tok, model, ids)
    print(f"  output: {out!r}")
    print(f"  {n} tokens, stopped by: {reason}\n")


base_tok, base = load("HuggingFaceTB/SmolLM2-360M")
asst_tok, asst = load("HuggingFaceTB/SmolLM2-360M-Instruct")

# The chat template wraps the question in role markers and opens an
# assistant turn for the model to fill.
chat = asst_tok.apply_chat_template(
    [{"role": "user", "content": PROMPT}], tokenize=False, add_generation_prompt=True)

run("Base model, bare question", base_tok, base, PROMPT)
run("Assistant, chat template", asst_tok, asst, chat)

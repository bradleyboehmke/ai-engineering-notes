"""Send the same prompt to a base model and its post-trained (instruct) sibling.

Usage: python base_vs_instruct.py ["Your prompt"] [max_tokens]

SmolLM2-360M and SmolLM2-360M-Instruct share the same pretrained weights.
The instruct model was fine-tuned on conversations (SFT), then on
preferences (DPO). Nothing else differs: same architecture, same tokenizer,
same generation loop. Four runs:
  1. Base model, raw prompt: it continues the text.
  2. Instruct model, raw prompt: no chat format, so it partly continues too.
  3. Instruct model, chat template: the prompt now looks like a conversation
     with an empty assistant turn, so it answers, then stops.
  4. Base model, chat template: same tokens as run 3, but no post-training.
  5. Base model, few-shot document: make the answer the likely continuation.

The loop is the one from limits.py (lesson 3): greedy, with a stop reason.
"""
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PROMPT = sys.argv[1] if len(sys.argv) > 1 else (
    "Summarize in one sentence: Q3 revenue was $4.2M, up 8% from Q2, "
    "driven by enterprise renewals.")
MAX_TOKENS = int(sys.argv[2]) if len(sys.argv) > 2 else 60

BASE = "HuggingFaceTB/SmolLM2-360M"
INSTRUCT = "HuggingFaceTB/SmolLM2-360M-Instruct"


def load(name):
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float32)
    model.eval()
    return tok, model


def generate(tok, model, ids, max_tokens):
    """Greedy loop. Stops on any end token the tokenizer knows about."""
    stop_ids = {tok.eos_token_id, tok.convert_tokens_to_ids("<|im_end|>"),
                tok.convert_tokens_to_ids("<|endoftext|>")}
    start = ids.shape[1]
    while ids.shape[1] - start < max_tokens:
        with torch.no_grad():
            next_id = model(ids).logits[0, -1].argmax().view(1, 1)
        ids = torch.cat([ids, next_id], dim=1)
        if next_id.item() in stop_ids:
            return ids[0, start:], f"end_of_text ({tok.decode(next_id[0])})"
    return ids[0, start:], "max_tokens"


def report(label, tok, model, text):
    ids = tok(text, return_tensors="pt", add_special_tokens=False).input_ids
    new, reason = generate(tok, model, ids, MAX_TOKENS)
    print(f"{label}")
    print(f"   input {ids.shape[1]} tokens -> generated {len(new)},"
          f" stop reason: {reason}")
    print(f"   output: {tok.decode(new)!r}\n")


base_tok, base = load(BASE)
inst_tok, inst = load(INSTRUCT)

# The chat template turns a list of messages into one string of tokens.
# add_generation_prompt=True appends the start of an empty assistant turn.
chat = inst_tok.apply_chat_template(
    [{"role": "user", "content": PROMPT}],
    tokenize=False, add_generation_prompt=True)

print(f"Prompt: {PROMPT!r}  (max_tokens={MAX_TOKENS}, greedy)\n")
print("What the chat template sends (one string, roles are just tokens):")
print("   " + chat.replace("\n", "\n   ") + "\n")

report("Run 1: base, raw prompt", base_tok, base, PROMPT)
report("Run 2: instruct, raw prompt", inst_tok, inst, PROMPT)
report("Run 3: instruct, chat template", inst_tok, inst, chat)
report("Run 4: base, chat template", base_tok, base, chat)

# A base model answers if the answer is what the document would say next.
few_shot = (
    "Quarterly report notes.\n\n"
    "Figures: Q1 revenue was $3.8M, up 2% from Q4, driven by new logos.\n"
    "One-sentence summary: Revenue grew 2% to $3.8M in Q1 on new customer wins.\n\n"
    f"Figures: {PROMPT.removeprefix('Summarize in one sentence: ')}\n"
    "One-sentence summary:")
report("Run 5: base, few-shot document", base_tok, base, few_shot)

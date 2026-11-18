"""Hit max_tokens on a real API on purpose, then read the stop reason and usage.

Usage: python limits_api.py              # steps 1-3
       python limits_api.py --overflow   # also step 4
Needs: pip install anthropic, and ANTHROPIC_API_KEY set (or `ant auth login`).
Cost: steps 1-3 are three tiny Claude Haiku 5.5 calls, well under a cent.
Step 4 sends ~0.5 MB that the API rejects before generating anything; even if
the rejected input were billed in full, it would be about $0.21.

  1. Count the prompt's tokens before sending (free).
  2. Ask for a long answer with max_tokens=30: stop_reason "max_tokens".
  3. Same prompt, room to finish: stop_reason "end_turn".
  4. (--overflow) Send more input than the window holds: HTTP 400.
"""
import math
import sys

import anthropic
from anthropic import Anthropic

client = Anthropic()
MODEL = "claude-haiku-5-5"
messages = [{"role": "user", "content":
             "In about 150 words, explain how to clean a messy sales dataset in Python."}]

# 1. Budget before you send: how many input tokens will this request use?
count = client.messages.count_tokens(model=MODEL, messages=messages)
print(f"count_tokens: {count.input_tokens} input tokens\n")

for max_tokens in (30, 1024):
    r = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        thinking={"type": "disabled"},   # thinking tokens also count toward max_tokens (lesson 5)
        messages=messages,
    )
    text = next((b.text for b in r.content if b.type == "text"), "")
    print(f"max_tokens={max_tokens}")
    print(f"   stop_reason:   {r.stop_reason}")
    print(f"   input_tokens:  {r.usage.input_tokens}")
    print(f"   output_tokens: {r.usage.output_tokens}")
    print(f"   ends with:     {text[-80:]!r}\n")

if "--overflow" not in sys.argv:
    sys.exit()

# 4. Input alone over the window. A 200K-window model is cheaper to overflow
#    than a 1M one. Ask the Models API for the window instead of hardcoding it.
SMALL = "claude-haiku-4-5"
window = client.models.retrieve(SMALL).max_input_tokens
print(f"{SMALL} context window: {window:,} tokens")

# Size the filler with free token counts: measure a chunk, then scale it
# to 5% over the window.
def count(text):
    return client.messages.count_tokens(
        model=SMALL, messages=[{"role": "user", "content": text}]).input_tokens

chunk = "The quarterly report lists sales by region and product. " * 1000
reps = math.ceil(1.05 * window / count(chunk))
big = chunk * reps
try:
    print(f"count_tokens:  {count(big):,} input tokens (over by design)")
except anthropic.BadRequestError as e:
    print(f"count_tokens rejected it too: {e.message}")

try:
    client.messages.create(
        model=SMALL,
        max_tokens=30,
        messages=[{"role": "user", "content": big + "\n\nSummarize the above."}],
    )
    print("   accepted (unexpected)")
except anthropic.BadRequestError as e:          # 400: nothing was generated
    print(f"   HTTP {e.status_code}: {e.message}")
except anthropic.RateLimitError as e:           # 429: a rate limit hit first
    print(f"   HTTP {e.status_code} (rate limit, not the window): {e.message}")

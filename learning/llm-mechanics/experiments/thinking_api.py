"""One question, thinking off vs on: compare correctness, tokens, time, and cost.

Usage: python thinking_api.py            # the five runs below
       python thinking_api.py --show     # also print the thinking summary of the high run
Needs: pip install anthropic, and ANTHROPIC_API_KEY set (or `ant auth login`).
Cost: five small Claude Haiku 5.5 calls ($0.10 / $0.50 per MTok, pricing page
read 2026-11-25). Even if every run used all 8,000 output tokens, the total is
about 2 cents.

  1. Thinking disabled          the model answers in one pass
  2. Adaptive, effort "low"     it may or may not think
  3. Adaptive, effort "medium"  Haiku 5.5's default
  4. Adaptive, effort "high"    it thinks most readily
  5. A trivial question at the default: does adaptive thinking bother?

The question has a checkable answer (Simpson's paradox): store B converts
better on each device, but store A converts better overall.
"""
import sys
import time

from anthropic import Anthropic

client = Anthropic()
MODEL = "claude-haiku-5-5"
PRICE_IN, PRICE_OUT = 0.10, 0.50          # $ per million tokens, prompts <= 100K

QUESTION = (
    "Store A: mobile 10 conversions from 100 visits, desktop 300 from 400.\n"
    "Store B: mobile 60 conversions from 400 visits, desktop 80 from 100.\n"
    "Which store has the higher conversion rate on mobile, on desktop, and "
    "overall? End with one line: 'mobile: X, desktop: X, overall: X'."
)
TRIVIAL = "What is the capital of France? One word."

RUNS = [
    ("1. off",          QUESTION, {"thinking": {"type": "disabled"}}),
    ("2. low",          QUESTION, {"output_config": {"effort": "low"}}),
    ("3. medium",       QUESTION, {"output_config": {"effort": "medium"}}),
    ("4. high",         QUESTION, {"output_config": {"effort": "high"},
                                   "thinking": {"type": "adaptive",
                                                "display": "summarized"}}),
    ("5. trivial, med", TRIVIAL,  {}),
]

print(f"{'run':<16}{'in':>5}{'out':>6}{'think':>7}{'text*':>7}"
      f"{'blocks':>12}{'sec':>6}{'cost $':>10}  last line")
high_summary = ""
for label, prompt, extra in RUNS:
    t0 = time.perf_counter()
    r = client.messages.create(
        model=MODEL,
        max_tokens=8000,               # thinking counts toward this cap too
        messages=[{"role": "user", "content": prompt}],
        **extra,
    )
    secs = time.perf_counter() - t0

    u = r.usage
    details = u.output_tokens_details
    think = details.thinking_tokens if details else 0
    text = next((b.text for b in r.content if b.type == "text"), "")
    blocks = "+".join(b.type[:5] for b in r.content)   # e.g. think+text
    cost = (u.input_tokens * PRICE_IN + u.output_tokens * PRICE_OUT) / 1e6
    last = text.strip().splitlines()[-1] if text.strip() else "(no text)"
    print(f"{label:<16}{u.input_tokens:>5}{u.output_tokens:>6}{think:>7}"
          f"{u.output_tokens - think:>7}{blocks:>12}{secs:>6.1f}{cost:>10.6f}"
          f"  {last[:60]}")
    if label.startswith("4"):
        high_summary = next((b.thinking for b in r.content
                             if b.type == "thinking"), "")
    if r.stop_reason != "end_turn":
        print(f"   stop_reason: {r.stop_reason}")

print("\n* text = output_tokens - thinking_tokens: the part you can see.")
print("  Correct answer: mobile: B, desktop: B, overall: A")

if "--show" in sys.argv:
    print("\nRun 4's thinking summary (a summary, not the raw reasoning; "
          "you're billed for the raw tokens):\n")
    print(high_summary or "(no thinking block)")

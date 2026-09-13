"""
===============================================================================
 LESSON 22 — CALLING THE CLAUDE API: LLM FUNDAMENTALS
===============================================================================

Time: about 90 minutes.
Assumes: lessons 01-21 (dicts, JSON, error handling, HTTP).

    SETUP (do this first):
        python3 -m venv .venv
        source .venv/bin/activate
        pip install anthropic
        export ANTHROPIC_API_KEY="sk-ant-..."

    This file RUNS WITHOUT A KEY. Every example is printed and explained; live
    calls happen only if the SDK and a key are both present. Read it either way.


-------------------------------------------------------------------------------
 THEORY: WHAT AN LLM API ACTUALLY IS
-------------------------------------------------------------------------------

Strip away the mystique and it's lesson 21 again:

    POST https://api.anthropic.com/v1/messages
    x-api-key: sk-ant-...
    {"model": "...", "max_tokens": 1024, "messages": [...]}

You send a list of messages, you get a message back. That's the whole API.

FIVE FACTS THAT SHAPE EVERYTHING YOU BUILD:

 1. IT IS STATELESS. The API remembers nothing between calls. "Conversation
    memory" is an illusion you create by resending the whole history every
    time. This is why long chats get expensive - you re-pay for the history on
    every turn.

 2. YOU PAY PER TOKEN, IN AND OUT. A token is roughly 3-4 characters. Input and
    output are priced differently (output costs ~5x more). Cost control is an
    engineering discipline, not an afterthought.

 3. IT IS NON-DETERMINISTIC. The same prompt can give different answers. You
    cannot test it with assertEqual. This is why EVALUATION (lesson 23) exists.

 4. IT HAS A CONTEXT WINDOW. A hard limit on how much you can send. Current
    models take 1M tokens - large, but not infinite.

 5. IT CAN BE WRONG WITH TOTAL CONFIDENCE. Never wire raw model output straight
    into something irreversible. Validate, constrain, and keep a human in the
    loop where the cost of error is high.
"""

import json
import os
import sys
from pathlib import Path

LINE = "-" * 70
HERE = Path(__file__).resolve().parent

# --- Work out what we can actually run -------------------------------------
try:
    import anthropic
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
LIVE = SDK_AVAILABLE and bool(API_KEY)

# The model ID to use. Always use the exact string - never add a date suffix.
MODEL = "claude-opus-5"

print(LINE)
print("SETUP CHECK")
print(LINE)
print(f"  anthropic SDK installed : {SDK_AVAILABLE}")
print(f"  ANTHROPIC_API_KEY set   : {bool(API_KEY)}")
print(f"  mode                    : {'LIVE - real API calls' if LIVE else 'OFFLINE - examples only'}")
if not LIVE:
    print("\n  To go live:  pip install anthropic")
    print("               export ANTHROPIC_API_KEY='sk-ant-...'")
print()

client = anthropic.Anthropic() if LIVE else None
# Note: Anthropic() with no arguments reads ANTHROPIC_API_KEY from the
# environment automatically. Never pass a hard-coded key (lesson 21 PART 5).


# =============================================================================
# PART 1 — MODELS AND PRICING
# =============================================================================
print(LINE)
print("PART 1 — CHOOSING A MODEL")
print(LINE)

# Prices are per MILLION tokens. Output is always more expensive than input.
MODELS = [
    # (model id,            context, $ in/1M, $ out/1M, when to use)
    ("claude-fable-5-1",    "1M",  10.00, 50.00, "hardest reasoning, long agentic runs"),
    ("claude-opus-5",       "1M",   5.00, 25.00, "DEFAULT - best all-round"),
    ("claude-sonnet-5",     "1M",   2.00, 10.00, "high-volume production"),
    ("claude-haiku-4-5",    "200K",  1.00,  5.00, "simple, speed-critical tasks"),
]

print(f"  {'model':<20}{'ctx':>6}{'$in/1M':>9}{'$out/1M':>9}  use for")
print("  " + "-" * 74)
for name, context, price_in, price_out, use in MODELS:
    print(f"  {name:<20}{context:>6}{price_in:>9.2f}{price_out:>9.2f}  {use}")

print(f"\n  Default to {MODEL}. Only drop to a cheaper model when you have")
print("  MEASURED that quality holds - cost is a decision, not an assumption.")
print()

# A cost estimator you'll use constantly:
def estimate_cost(input_tokens, output_tokens, price_in=5.00, price_out=25.00):
    """Cost in dollars for one request."""
    return (input_tokens / 1_000_000 * price_in
            + output_tokens / 1_000_000 * price_out)

print("  cost examples on Opus 5:")
for label, tokens_in, tokens_out in [
    ("a short question", 50, 200),
    ("summarise a document", 5_000, 500),
    ("10k-token RAG prompt", 10_000, 800),
    ("1,000 of those per day", 10_000_000, 800_000),
]:
    print(f"    {label:<26}${estimate_cost(tokens_in, tokens_out):>10.4f}")
print()


# =============================================================================
# PART 2 — YOUR FIRST CALL
# =============================================================================
print(LINE)
print("PART 2 — THE MESSAGES API")
print(LINE)

EXAMPLE_BASIC = '''
import anthropic
client = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY from env

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,                   # a CAP, not a target
    system="You are a concise Python tutor.",
    messages=[
        {"role": "user", "content": "What is a list comprehension?"}
    ],
)

# response.content is a LIST of blocks, not a string.
for block in response.content:
    if block.type == "text":
        print(block.text)
'''
print(EXAMPLE_BASIC)

# THE THREE PARTS OF A REQUEST:
#   model     which model
#   system    standing instructions - role, rules, format. Not a message.
#   messages  the conversation, alternating user / assistant
#
# max_tokens is a CEILING on the reply. Set it too low and answers get cut off
# mid-sentence. Default to ~16000 for normal calls, ~64000 when streaming.

def extract_text(response):
    """Pull the plain text out of a response. You'll want this constantly."""
    return "".join(block.text for block in response.content
                   if block.type == "text")


if LIVE:
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system="You are a concise Python tutor. Answer in under 40 words.",
        messages=[{"role": "user", "content": "What is a list comprehension?"}],
    )
    print("  LIVE RESPONSE:")
    print("   ", extract_text(response))
    print(f"\n  stop_reason: {response.stop_reason}")
    print(f"  tokens: {response.usage.input_tokens} in, "
          f"{response.usage.output_tokens} out")
    print(f"  cost: ${estimate_cost(response.usage.input_tokens, response.usage.output_tokens):.5f}")
else:
    print("  (offline - the shape of a response:)")
    print("""    response.content     [TextBlock(text='...'), ...]
    response.stop_reason 'end_turn' | 'max_tokens' | 'tool_use' | 'refusal'
    response.usage       input_tokens, output_tokens, cache_read_input_tokens
    response.model       which model actually served it""")
print()

# ALWAYS CHECK stop_reason:
#   end_turn    finished naturally - good
#   max_tokens  TRUNCATED - your answer is incomplete, raise max_tokens
#   tool_use    it wants to call a tool (lesson 23)
#   refusal     declined on safety grounds - check response.stop_details


# =============================================================================
# PART 3 — CONVERSATIONS ARE JUST A GROWING LIST
# =============================================================================
print(LINE)
print("PART 3 — MULTI-TURN CONVERSATIONS")
print(LINE)

# The API is stateless. "Memory" = you keep the list and resend it.

class Conversation:
    """Manages a multi-turn conversation. This is the whole trick."""

    def __init__(self, client, model=MODEL, system=None):
        self.client = client
        self.model = model
        self.system = system
        self.messages = []
        self.total_input = 0
        self.total_output = 0

    def send(self, user_message, max_tokens=16000):
        self.messages.append({"role": "user", "content": user_message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system,
            messages=self.messages,
        )

        reply = extract_text(response)
        # Append the assistant's turn, or the next call loses the thread.
        self.messages.append({"role": "assistant", "content": reply})

        self.total_input += response.usage.input_tokens
        self.total_output += response.usage.output_tokens
        return reply

    def cost(self):
        return estimate_cost(self.total_input, self.total_output)


print("""  Turn 1 sends:  [user]
  Turn 2 sends:  [user, assistant, user]
  Turn 3 sends:  [user, assistant, user, assistant, user]

  ***** THE COST TRAP *****
  Input grows every turn because you resend everything. A 20-turn chat can
  re-bill the same early messages 20 times. Mitigations:
    - prompt caching (PART 6) - up to 90% off the repeated prefix
    - trim or summarise old turns
    - server-side compaction for very long sessions""")

if LIVE:
    chat = Conversation(client, system="You are terse. Max 25 words.")
    print("\n  LIVE:")
    print("   >", chat.send("My name is Sidd and I'm learning Python.", max_tokens=200))
    print("   >", chat.send("What's my name, and what am I learning?", max_tokens=200))
    print(f"   (it remembered because we resent the history. cost ${chat.cost():.5f})")
print()


# =============================================================================
# PART 4 — STREAMING
# =============================================================================
print(LINE)
print("PART 4 — STREAMING")
print(LINE)

# Without streaming, the user stares at nothing for 20 seconds then gets a wall
# of text. With streaming, words appear as they're generated. Same total time,
# completely different experience - and it avoids HTTP timeouts on long replies.

EXAMPLE_STREAM = '''
with client.messages.stream(
    model="claude-opus-5",
    max_tokens=64000,               # streaming lets you go big safely
    messages=[{"role": "user", "content": "Write a haiku about debugging."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)      # flush=True prints immediately

    final = stream.get_final_message()       # full object once complete
    print(f"\\n[{final.usage.output_tokens} tokens]")
'''
print(EXAMPLE_STREAM)
print("  RULE: stream anything with a large max_tokens or a human waiting.")

if LIVE:
    print("\n  LIVE STREAM: ", end="", flush=True)
    with client.messages.stream(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": "Write a haiku about debugging."}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        final = stream.get_final_message()
    print(f"\n  [{final.usage.output_tokens} output tokens]")
print()


# =============================================================================
# PART 5 — COUNTING TOKENS BEFORE YOU SPEND
# =============================================================================
print(LINE)
print("PART 5 — TOKEN COUNTING")
print(LINE)

# A token is roughly 3-4 characters of English. Don't guess, and never use
# tiktoken (that's OpenAI's tokeniser and gives wrong numbers for Claude).
# The API will count exactly, for free:

EXAMPLE_COUNT = '''
count = client.messages.count_tokens(
    model="claude-opus-5",
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": long_document}],
)
print(count.input_tokens)                    # exact, before you spend anything
'''
print(EXAMPLE_COUNT)

text = (HERE / "data" / "server.log").read_text(encoding="utf-8")
print(f"  rough guide: {len(text)} characters ≈ {len(text) // 4} tokens")

if LIVE:
    count = client.messages.count_tokens(
        model=MODEL,
        messages=[{"role": "user", "content": text}],
    )
    print(f"  exact count from the API: {count.input_tokens} tokens")
    print(f"  cost to send once: ${estimate_cost(count.input_tokens, 0):.5f}")
print("\n  Use this to guard against sending something enormous by accident.")
print()


# =============================================================================
# PART 6 — PROMPT CACHING: THE BIGGEST COST LEVER
# =============================================================================
print(LINE)
print("PART 6 — PROMPT CACHING")
print(LINE)

# If you send the same large prefix repeatedly - a system prompt, a document, a
# tool list - cache it. Cached reads cost ~10% of normal input tokens.

EXAMPLE_CACHE = '''
response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    system=[{
        "type": "text",
        "text": large_document,                      # 50k tokens of context
        "cache_control": {"type": "ephemeral"},       # <- cache everything above
    }],
    messages=[{"role": "user", "content": question}],  # varies each time
)

print(response.usage.cache_creation_input_tokens)   # written to cache (~1.25x)
print(response.usage.cache_read_input_tokens)       # served from cache (~0.1x)
'''
print(EXAMPLE_CACHE)

print("""  THE RULE THAT MATTERS: caching is a PREFIX match. Any byte change
  anywhere before the breakpoint invalidates everything after it.

  Order is: tools -> system -> messages. So:
    STABLE content first   (frozen system prompt, sorted tool list, documents)
    VOLATILE content last  (timestamps, user IDs, the actual question)

  Silent cache killers - if cache_read_input_tokens is always 0, look for:
    - datetime.now() or a UUID inside the system prompt
    - json.dumps() without sort_keys=True (dict order varies)
    - a tool list built in a different order each run
    - changing the model or effort mid-conversation (caches are model-scoped)

  Verify it worked: usage.cache_read_input_tokens > 0. Don't assume.""")
print()


# =============================================================================
# PART 7 — THINKING AND EFFORT
# =============================================================================
print(LINE)
print("PART 7 — THINKING AND EFFORT")
print(LINE)

EXAMPLE_THINKING = '''
response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    thinking={"type": "adaptive", "display": "summarized"},
    output_config={"effort": "high"},     # low | medium | high | xhigh | max
    messages=[{"role": "user", "content": "Plan a database migration..."}],
)
'''
print(EXAMPLE_THINKING)

print("""  THINKING: the model reasons before answering. On current models use
  {"type": "adaptive"} - it decides how much thinking each request needs.
  (An older `budget_tokens` form exists in tutorials online; it is REMOVED on
  current models and returns a 400. Don't copy it.)

  EFFORT: how much total work to spend. This is your main quality/cost dial
  WITHIN one model, and it's usually a better lever than downgrading the model:
    low     subagents, classification, simple lookups
    medium  routine work where quality holds
    high    the default - most tasks
    xhigh   coding and agentic work
    max     when correctness matters more than cost

  Measure before you change a default. Judge COST PER COMPLETED TASK, not per
  request - a cheap call that needs three retries isn't cheap.""")
print()


# =============================================================================
# PART 8 — ERROR HANDLING (lesson 12 and 21, applied)
# =============================================================================
print(LINE)
print("PART 8 — ERRORS")
print(LINE)

EXAMPLE_ERRORS = '''
import anthropic

try:
    response = client.messages.create(...)

except anthropic.AuthenticationError:
    print("Bad or missing API key")              # do NOT retry
except anthropic.BadRequestError as e:
    print(f"Malformed request: {e.message}")     # do NOT retry - fix the code
except anthropic.RateLimitError as e:
    wait = int(e.response.headers.get("retry-after", "60"))
    print(f"Rate limited, retry in {wait}s")     # DO retry
except anthropic.APIStatusError as e:
    if e.status_code >= 500:
        print("Server error - retry with backoff")
except anthropic.APIConnectionError:
    print("Network problem - retry")             # DO retry
'''
print(EXAMPLE_ERRORS)

print("""  Catch specific exceptions, most specific FIRST (lesson 12 mistake 4).
  The same 4xx/5xx split from lesson 21 applies.

  The SDK already retries 429 and 5xx twice with backoff. Configure it:
      client = anthropic.Anthropic(max_retries=5, timeout=60.0)

  Also guard `stop_reason == "refusal"` before reading content - a safety
  decline returns HTTP 200 with no usable text.""")
print()

# PRODUCTION HARDENING: on the top models you can have the API automatically
# re-run a declined request on a fallback model, in the same call:
#
#     response = client.beta.messages.create(
#         model="claude-opus-5",
#         max_tokens=16000,
#         betas=["server-side-fallback-2026-07-01"],
#         fallbacks="default",            # routes by refusal category
#         messages=[...],
#     )
#
# Worth enabling for user-facing apps so one decline doesn't become an outage.


# =============================================================================
# PART 9 — A REUSABLE CLIENT WRAPPER
# =============================================================================
print(LINE)
print("PART 9 — WRAPPING IT UP")
print(LINE)

class ClaudeClient:
    """A small wrapper adding cost tracking and safe defaults."""

    def __init__(self, model=MODEL, system=None, max_retries=3):
        self.model = model
        self.system = system
        self.client = anthropic.Anthropic(max_retries=max_retries) if SDK_AVAILABLE else None
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cached_tokens = 0

    def ask(self, prompt, max_tokens=4000, effort="high"):
        """One-shot question. Returns text, or raises a clear error."""
        if self.client is None:
            raise RuntimeError("anthropic SDK not installed")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system,
            output_config={"effort": effort},
            messages=[{"role": "user", "content": prompt}],
        )

        if response.stop_reason == "refusal":
            raise RuntimeError(f"declined: {response.stop_details}")
        if response.stop_reason == "max_tokens":
            print("  WARNING: reply was truncated - raise max_tokens")

        self.calls += 1
        self.input_tokens += response.usage.input_tokens
        self.output_tokens += response.usage.output_tokens
        self.cached_tokens += getattr(response.usage, "cache_read_input_tokens", 0) or 0
        return extract_text(response)

    def report(self):
        return (f"{self.calls} calls | {self.input_tokens:,} in "
                f"({self.cached_tokens:,} cached) | {self.output_tokens:,} out "
                f"| ${estimate_cost(self.input_tokens, self.output_tokens):.4f}")


print("  ClaudeClient: safe defaults, stop_reason checks, cost tracking.")
if LIVE:
    bot = ClaudeClient(system="Answer in one short sentence.")
    print("  LIVE:", bot.ask("Why do programmers prefer dark mode?", max_tokens=100))
    print("  usage:", bot.report())
else:
    print("  (offline - read the class above; it's the pattern you'll reuse)")
print()


# =============================================================================
# PART 10 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 10 — COMMON MISTAKES")
print(LINE)
print("""   1. Hard-coding the API key. Use os.environ (lesson 21).
   2. Treating response.content as a string. It's a LIST of blocks.
   3. Not checking stop_reason - silently shipping truncated answers.
   4. max_tokens too low. It truncates; it does not summarise.
   5. Forgetting to append the assistant turn, so the model "forgets".
   6. No caching on a repeated large prefix - paying 10x for nothing.
   7. Assuming output is valid JSON. Validate it (lesson 23).
   8. Using tiktoken to count tokens. Wrong tokeniser - use count_tokens.
   9. Retrying a 400. It will never work.
  10. No cost monitoring until the bill arrives. Track usage from day one.
  11. Copying `budget_tokens` thinking config from old tutorials - it's
      removed on current models and returns a 400.""")
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# 1. Set up a venv, install anthropic, export your key, and re-run this file
#    live. Watch the token counts.
# 2. Build a terminal chatbot: loop on input(), keep a Conversation, print the
#    running cost, and exit on "quit".
# 3. Write summarise(text, words=50) that summarises any text, and run it over
#    data/server.log.
# 4. Write classify(text, categories) that returns exactly one category. Make
#    the system prompt forbid any other output, then VALIDATE the result
#    against your list and retry once if it's wrong.
# 5. Measure caching: send a 5,000-word document twice with cache_control, and
#    print cache_read_input_tokens both times. Then add datetime.now() to the
#    system prompt and watch the cache die.
# 6. Compare effort="low" and effort="max" on the same hard question. Note the
#    difference in output tokens, latency and quality.
# 7. Add streaming to ClaudeClient as a stream_ask() method.
# 8. Wrap ask() so it logs prompt, model, tokens and cost to a CSV - your own
#    observability, using lesson 14.


print("=" * 70)
print("Lesson 22 complete. Next: 23_ai_engineering_patterns.py")
print("=" * 70)

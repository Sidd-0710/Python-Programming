"""
===============================================================================
 LESSON 22 — CALLING THE CLAUDE API: LLM FUNDAMENTALS
===============================================================================

Time: about 95 minutes.
Assumes: lessons 01-21 (dicts, JSON, error handling, HTTP).

    TO RUN LIVE (optional):
        python3 -m venv .venv
        source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
        pip install anthropic
        export ANTHROPIC_API_KEY="sk-ant-..."

    WITHOUT A KEY THIS FILE STILL RUNS AND STILL TEACHES. It includes a small
    OFFLINE SIMULATOR that mimics the API's response shape, so the conversation
    mechanics, token accounting, streaming loop and cost tracking all actually
    execute and print real output. Only the words come from a stub instead of
    a real model.


-------------------------------------------------------------------------------
 THEORY: WHAT AN LLM API ACTUALLY IS
-------------------------------------------------------------------------------

Strip away the mystique and it is lesson 21 again:

    POST https://api.anthropic.com/v1/messages
    x-api-key: sk-ant-...
    content-type: application/json

    {"model": "claude-opus-5", "max_tokens": 1024,
     "messages": [{"role": "user", "content": "Hello"}]}

You send a list of messages. You get a message back. That is the entire API.
Everything else - agents, RAG, tool use, chatbots - is built on top of that one
request by ordinary Python code that you write.


-------------------------------------------------------------------------------
 SIX FACTS THAT SHAPE EVERYTHING YOU WILL BUILD
-------------------------------------------------------------------------------

 1. IT IS STATELESS.
    The API remembers nothing between calls. "Conversation memory" is an
    illusion you create by resending the entire history every single time.
    Consequence: long chats get expensive, because you re-pay for the history
    on every turn. PART 3 shows this happening.

 2. YOU PAY PER TOKEN, BOTH DIRECTIONS.
    A token is roughly 3-4 characters of English. Input and output are priced
    separately, and output typically costs 5x more. Cost control is an
    engineering discipline, not an afterthought you bolt on later.

 3. IT IS NON-DETERMINISTIC.
    The same prompt can produce different answers. You cannot test it with
    assertEqual. This single fact is why EVALUATION exists as a discipline
    (lesson 23) and why "it worked when I tried it" means almost nothing.

 4. IT HAS A CONTEXT WINDOW.
    A hard ceiling on how much you can send in one request. Current models
    accept 1,000,000 tokens - large, but not infinite, and you pay for all of
    it every time.

 5. IT CAN BE CONFIDENTLY WRONG.
    The model has no notion of "I'm not sure". It produces plausible text.
    Never wire raw model output straight into something irreversible.

 6. LATENCY IS SECONDS, NOT MILLISECONDS.
    A normal database query takes 5ms. A model call takes 2-30 seconds. That
    changes your whole architecture: you need streaming (PART 4), timeouts,
    and usually background jobs rather than blocking a web request.
"""

import json
import os
import random
import sys
import time
from pathlib import Path

LINE = "-" * 70
HERE = Path(__file__).resolve().parent

# The model ID to use. Always the exact string, never with a date appended.
MODEL = "claude-opus-5"

try:
    import anthropic
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
LIVE = SDK_AVAILABLE and bool(API_KEY)


# =============================================================================
# THE OFFLINE SIMULATOR
# =============================================================================
# Read this if you're curious, skip it if you're not. It exists so every demo
# below produces real output even with no API key. It is NOT how you talk to
# Claude - it just imitates the RESPONSE SHAPE so the surrounding code (which
# IS real) has something to work with.
#
# Notice what it does model: content as a LIST OF BLOCKS, a usage object with
# token counts, and a stop_reason. Those three things are what your code
# actually interacts with.
# -----------------------------------------------------------------------------

class FakeBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class FakeUsage:
    def __init__(self, input_tokens, output_tokens, cache_read=0):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.cache_read_input_tokens = cache_read
        self.cache_creation_input_tokens = 0


class FakeResponse:
    def __init__(self, text, input_tokens, output_tokens, cache_read=0):
        self.content = [FakeBlock(text)]
        self.usage = FakeUsage(input_tokens, output_tokens, cache_read)
        self.stop_reason = "end_turn"
        self.stop_details = None
        self.model = "offline-simulator"


def estimate_tokens(text):
    """A rough token estimate: ~4 characters per token for English."""
    return max(1, len(str(text)) // 4)


class FakeMessages:
    """Imitates client.messages - just enough for the lessons to run."""

    def __init__(self, parent):
        self.parent = parent

    def _canned_reply(self, messages, system):
        """Produce a plausible-looking reply, with a little memory."""
        last = messages[-1]["content"]
        if isinstance(last, list):
            last = " ".join(str(b) for b in last)
        lowered = str(last).lower()

        # A crude "memory" so the multi-turn demo visibly works.
        history_text = " ".join(str(m.get("content", "")) for m in messages).lower()
        if "what's my name" in lowered or "what is my name" in lowered:
            for token in history_text.replace(",", " ").replace(".", " ").split():
                if token.istitle() and len(token) > 2:
                    pass
            if "sidd" in history_text:
                return "Your name is Sidd, and you are learning Python."
        if "haiku" in lowered:
            return ("Semicolon missing\nthe compiler weeps softly\none char, "
                    "one long night")
        if "list comprehension" in lowered:
            return ("A list comprehension builds a new list in one line: "
                    "[n * 2 for n in numbers]. It replaces the create-empty-list, "
                    "loop, append pattern.")
        if "dark mode" in lowered:
            return "Because light attracts bugs."
        return (f"(simulated reply) I received {len(messages)} message(s). "
                f"The most recent was {str(last)[:60]!r}.")

    def create(self, model=None, max_tokens=1024, messages=None, system=None,
               tools=None, output_config=None, thinking=None, **kwargs):
        messages = messages or []
        text = self._canned_reply(messages, system)

        # Input tokens = the WHOLE conversation plus the system prompt, every
        # time. This is the stateless-cost reality, simulated faithfully.
        input_tokens = estimate_tokens(json.dumps(str(messages))) + \
            estimate_tokens(str(system) if system else "")
        output_tokens = estimate_tokens(text)

        time.sleep(0.05)                              # a hint of real latency
        self.parent.call_count += 1
        return FakeResponse(text, input_tokens, output_tokens)

    def count_tokens(self, model=None, messages=None, system=None, **kwargs):
        total = estimate_tokens(json.dumps(str(messages or [])))
        total += estimate_tokens(str(system) if system else "")

        class Count:
            input_tokens = total
        return Count()

    def stream(self, **kwargs):
        return FakeStream(self, kwargs)


class FakeStream:
    """Imitates the streaming context manager."""

    def __init__(self, messages_api, kwargs):
        self.messages_api = messages_api
        self.kwargs = kwargs
        self._final = None

    def __enter__(self):
        self._final = self.messages_api.create(**self.kwargs)
        return self

    def __exit__(self, *args):
        return False

    @property
    def text_stream(self):
        """Yield the reply a few characters at a time, like the real thing."""
        text = self._final.content[0].text
        for index in range(0, len(text), 6):
            time.sleep(0.01)
            yield text[index:index + 6]

    def get_final_message(self):
        return self._final


class FakeAnthropic:
    def __init__(self, **kwargs):
        self.messages = FakeMessages(self)
        self.call_count = 0


# Choose the real client or the simulator.
if LIVE:
    client = anthropic.Anthropic(max_retries=3, timeout=60.0)
else:
    client = FakeAnthropic()

print(LINE)
print("SETUP CHECK")
print(LINE)
print(f"  anthropic SDK installed : {SDK_AVAILABLE}")
print(f"  ANTHROPIC_API_KEY set   : {bool(API_KEY)}")
print(f"  mode                    : {'LIVE (real API calls)' if LIVE else 'SIMULATED'}")
if not LIVE:
    print()
    print("  Running against the offline simulator. All the CODE below is real;")
    print("  only the model's words are canned. To go live:")
    print("      pip install anthropic")
    print("      export ANTHROPIC_API_KEY='sk-ant-...'")
print()


# =============================================================================
# PART 1 — MODELS AND PRICING
# =============================================================================
print(LINE)
print("PART 1 — CHOOSING A MODEL")
print(LINE)

# Prices are dollars per MILLION tokens. Output always costs more than input,
# because generating text is more work than reading it.
MODELS = {
    "claude-fable-5-1": (10.00, 50.00, "1M", "hardest reasoning, long agentic runs"),
    "claude-opus-5":    (5.00, 25.00, "1M", "DEFAULT - best all-round"),
    "claude-sonnet-5":  (2.00, 10.00, "1M", "high-volume production work"),
    "claude-haiku-4-5": (1.00, 5.00, "200K", "simple, speed-critical tasks"),
}

print(f"  {'model':<20}{'ctx':>6}{'$in/1M':>9}{'$out/1M':>9}  use for")
print("  " + "-" * 74)
for name, (price_in, price_out, context, use) in MODELS.items():
    print(f"  {name:<20}{context:>6}{price_in:>9.2f}{price_out:>9.2f}  {use}")

print(f"""
  Default to {MODEL}. Drop to a cheaper model only when you have MEASURED
  that quality holds on YOUR task (lesson 23 shows how). Cost is a decision
  to make with evidence, not an assumption to make in advance.

  Counter-intuitive but important: a cheaper model that needs three attempts
  and a human correction is more expensive than one call to a better model.
  Judge cost per COMPLETED TASK, not per request.""")
print()


def estimate_cost(input_tokens, output_tokens, model=MODEL):
    """Dollar cost of one request. You will use this constantly."""
    price_in, price_out = MODELS.get(model, MODELS[MODEL])[:2]
    return input_tokens / 1_000_000 * price_in + output_tokens / 1_000_000 * price_out


print("  what things actually cost on Opus 5:")
for label, tokens_in, tokens_out in [
    ("a short question", 50, 200),
    ("summarise a 10-page doc", 5_000, 500),
    ("a 10k-token RAG prompt", 10_000, 800),
    ("a 20-turn chat (total)", 60_000, 6_000),
    ("1,000 RAG calls/day", 10_000_000, 800_000),
    ("the same, monthly", 300_000_000, 24_000_000),
]:
    print(f"    {label:<26}${estimate_cost(tokens_in, tokens_out):>12,.4f}")

print("\n  the same daily volume, per model:")
for name in MODELS:
    print(f"    {name:<20}${estimate_cost(10_000_000, 800_000, name):>10,.2f}/day")
print()


# =============================================================================
# PART 2 — YOUR FIRST CALL, AND THE SHAPE OF A RESPONSE
# =============================================================================
print(LINE)
print("PART 2 — THE MESSAGES API")
print(LINE)

print('''  THE CANONICAL CALL:

    import anthropic
    client = anthropic.Anthropic()       # reads ANTHROPIC_API_KEY from the env

    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=16000,                # a CEILING on the reply, not a target
        system="You are a concise Python tutor.",
        messages=[
            {"role": "user", "content": "What is a list comprehension?"}
        ],
    )

  THE THREE INPUTS:
    model     which model to use
    system    standing instructions: role, rules, output format. NOT a message
              in the conversation - think of it as policy that always applies.
    messages  the conversation itself, a list of {"role", "content"} dicts,
              alternating user and assistant.

  max_tokens is a HARD CAP. Set it too low and the reply is CHOPPED OFF
  mid-sentence - it does not summarise to fit. Default to ~16000 for normal
  calls and ~64000 when streaming.''')
print()

response = client.messages.create(
    model=MODEL,
    max_tokens=300,
    system="You are a concise Python tutor. Answer in under 40 words.",
    messages=[{"role": "user", "content": "What is a list comprehension?"}],
)

print("  A REAL RESPONSE OBJECT:")
print(f"    type(response.content) : {type(response.content).__name__}  <- a LIST")
print(f"    len(response.content)  : {len(response.content)}")
print(f"    content[0].type        : {response.content[0].type}")
print(f"    content[0].text        : {response.content[0].text[:60]}...")
print(f"    stop_reason            : {response.stop_reason}")
print(f"    usage.input_tokens     : {response.usage.input_tokens}")
print(f"    usage.output_tokens    : {response.usage.output_tokens}")
print(f"    model                  : {response.model}")
print()

# ***** response.content IS A LIST, NOT A STRING *****
# This catches everyone once. A response can contain several blocks: text,
# thinking, tool_use. You must pick out the ones you want.

def extract_text(response):
    """Pull the plain text out of a response. You'll want this in every project."""
    return "".join(block.text for block in response.content
                   if block.type == "text")

print("  the helper you'll copy into every project:")
print("      def extract_text(response):")
print('          return "".join(b.text for b in response.content if b.type == "text")')
print()
print("  result:", extract_text(response))
print(f"  cost  : ${estimate_cost(response.usage.input_tokens, response.usage.output_tokens):.6f}")
print()

print("""  ALWAYS CHECK stop_reason BEFORE TRUSTING THE OUTPUT:
    end_turn    finished naturally               -> good
    max_tokens  TRUNCATED mid-sentence           -> raise max_tokens and retry
    tool_use    it wants to call a tool          -> lesson 23
    refusal     declined on safety grounds       -> check response.stop_details,
                                                    and note content may be empty

  Shipping truncated answers because you never checked stop_reason is one of
  the most common bugs in production LLM code.""")
print()


# =============================================================================
# PART 3 — CONVERSATIONS ARE JUST A GROWING LIST
# =============================================================================
print(LINE)
print("PART 3 — MULTI-TURN CONVERSATIONS")
print(LINE)

print("""  The API is stateless. "Memory" is entirely your responsibility: you keep
  a list and resend all of it every time.

    Turn 1 sends:  [user]
    Turn 2 sends:  [user, assistant, user]
    Turn 3 sends:  [user, assistant, user, assistant, user]

  Forget to append the assistant's reply and the model "loses its memory" -
  a bug that looks mysterious and has a very boring cause.""")
print()


class Conversation:
    """Manages a multi-turn conversation and tracks what it costs."""

    def __init__(self, client, model=MODEL, system=None):
        self.client = client
        self.model = model
        self.system = system
        self.messages = []
        self.turns = []                 # per-turn token accounting

    def send(self, user_message, max_tokens=1000):
        self.messages.append({"role": "user", "content": user_message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system,
            messages=self.messages,
        )

        reply = extract_text(response)
        # THE CRITICAL LINE - without it, the next call has no context.
        self.messages.append({"role": "assistant", "content": reply})

        self.turns.append({
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
            "cost": estimate_cost(response.usage.input_tokens,
                                  response.usage.output_tokens, self.model),
        })
        return reply

    @property
    def total_cost(self):
        return sum(turn["cost"] for turn in self.turns)


chat = Conversation(client, system="You are terse. Answer in under 25 words.")

for message in [
    "My name is Sidd and I'm learning Python.",
    "What's my name?",
    "What am I learning?",
    "Give me one tip for it.",
]:
    reply = chat.send(message)
    print(f"    you > {message}")
    print(f"    AI  > {reply}")
    print()

print("  WATCH THE INPUT TOKENS GROW - this is the stateless tax:")
print(f"    {'turn':<6}{'messages sent':>15}{'input tok':>11}{'output tok':>12}{'cost':>12}")
for index, turn in enumerate(chat.turns, start=1):
    money = f"${turn['cost']:.6f}"
    print(f"    {index:<6}{index * 2 - 1:>15}{turn['input']:>11}"
          f"{turn['output']:>12}{money:>12}")
total_money = f"${chat.total_cost:.6f}"
print(f"    {'TOTAL':<6}{'':<15}{sum(t['input'] for t in chat.turns):>11}"
      f"{sum(t['output'] for t in chat.turns):>12}{total_money:>12}")

print(f"""
  Turn 4's input is roughly {chat.turns[-1]['input'] / max(chat.turns[0]['input'], 1):.1f}x turn 1's, for the same
  short question. Over 30 turns this dominates your bill entirely.

  THE THREE FIXES:
    1. PROMPT CACHING (PART 6) - up to 90% off the repeated prefix
    2. TRIM OLD TURNS - keep only the last N, or summarise the older ones
    3. SERVER-SIDE COMPACTION - the API summarises history for you on very
       long sessions""")
print()


# =============================================================================
# PART 4 — STREAMING
# =============================================================================
print(LINE)
print("PART 4 — STREAMING")
print(LINE)

print('''  Without streaming, the user stares at a blank screen for 20 seconds and
  then gets a wall of text. With streaming, words appear as they're generated.
  Same total time, completely different experience - and it avoids HTTP
  timeouts on long replies.

    with client.messages.stream(
        model="claude-opus-5",
        max_tokens=64000,                  # streaming lets you go big safely
        messages=[{"role": "user", "content": "Write a haiku about debugging."}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)     # flush=True prints immediately

        final = stream.get_final_message()      # the full object, once done
        print(final.usage.output_tokens)

  flush=True matters: without it Python buffers output and you get the whole
  thing at once anyway, defeating the point.''')
print()

print("  watch it arrive piece by piece:")
print("    ", end="", flush=True)
with client.messages.stream(
    model=MODEL,
    max_tokens=200,
    messages=[{"role": "user", "content": "Write a haiku about debugging."}],
) as stream:
    for chunk in stream.text_stream:
        print(chunk, end="", flush=True)
    final = stream.get_final_message()
print(f"\n\n    [{final.usage.output_tokens} output tokens, "
      f"stop_reason={final.stop_reason}]")
print()

print("""  RULE: stream anything with a large max_tokens or a human waiting on it.
  Use the plain create() for short background tasks where nobody is watching.""")
print()


# =============================================================================
# PART 5 — COUNTING TOKENS BEFORE YOU SPEND
# =============================================================================
print(LINE)
print("PART 5 — TOKEN COUNTING")
print(LINE)

print("""  A token is roughly 3-4 characters of English - about 0.75 words. But
  "roughly" is not good enough when you're about to send a 200-page PDF.

  The API will count exactly, for free, before you spend anything:

      count = client.messages.count_tokens(
          model="claude-opus-5",
          system=system_prompt,
          messages=[{"role": "user", "content": long_document}],
      )
      print(count.input_tokens)

  NEVER use `tiktoken` for this. That is OpenAI's tokeniser and gives wrong
  numbers for Claude.""")
print()

log_text = (HERE / "data" / "server.log").read_text(encoding="utf-8")
count = client.messages.count_tokens(
    model=MODEL,
    messages=[{"role": "user", "content": log_text}],
)

print(f"  data/server.log:")
print(f"    characters       : {len(log_text):,}")
print(f"    words            : {len(log_text.split()):,}")
print(f"    tokens (counted) : {count.input_tokens:,}")
print(f"    chars per token  : {len(log_text) / count.input_tokens:.1f}")
print(f"    cost to send once: ${estimate_cost(count.input_tokens, 0):.6f}")
print(f"    cost x1000/day   : ${estimate_cost(count.input_tokens, 0) * 1000:.2f}")
print()


def guard_size(text, limit=50_000, model=MODEL):
    """Refuse to send something enormous by accident. Use this at boundaries."""
    tokens = client.messages.count_tokens(
        model=model, messages=[{"role": "user", "content": text}]
    ).input_tokens
    if tokens > limit:
        raise ValueError(
            f"input is {tokens:,} tokens, over the {limit:,} limit "
            f"(would cost ${estimate_cost(tokens, 0):.2f}). "
            f"Chunk it or summarise it first."
        )
    return tokens

print("  a guard worth having in production:")
try:
    guard_size("x" * 500_000, limit=50_000)
except ValueError as error:
    print(f"    blocked: {error}")
print()


# =============================================================================
# PART 6 — PROMPT CACHING: THE BIGGEST COST LEVER
# =============================================================================
print(LINE)
print("PART 6 — PROMPT CACHING")
print(LINE)

print('''  If you send the same large prefix repeatedly - a long system prompt, a
  reference document, a tool list - you can CACHE it. Cached reads cost about
  10% of normal input tokens.

      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=16000,
          system=[{
              "type": "text",
              "text": large_document,                    # 50k tokens of context
              "cache_control": {"type": "ephemeral"},    # cache up to HERE
          }],
          messages=[{"role": "user", "content": question}],   # varies each call
      )

      response.usage.cache_creation_input_tokens   # written to cache (~1.25x)
      response.usage.cache_read_input_tokens       # served from cache (~0.1x)''')
print()

# Show the arithmetic, because the saving is easy to underestimate:
document_tokens = 50_000
question_tokens = 100
output_tokens = 500
calls = 100

uncached = calls * estimate_cost(document_tokens + question_tokens, output_tokens)
first = estimate_cost(document_tokens * 1.25 + question_tokens, output_tokens)
rest = (calls - 1) * (estimate_cost(question_tokens, output_tokens)
                      + document_tokens * 0.1 / 1_000_000 * 5.00)

print(f"  {calls} questions against the same {document_tokens:,}-token document:")
print(f"    without caching : ${uncached:>8.2f}")
print(f"    with caching    : ${first + rest:>8.2f}")
print(f"    saved           : ${uncached - (first + rest):>8.2f} "
      f"({(uncached - (first + rest)) / uncached:.0%})")
print()

print("""  ***** THE RULE THAT MATTERS: CACHING IS A PREFIX MATCH *****

  Any byte that changes anywhere BEFORE the cache breakpoint invalidates
  everything after it. The request is rendered in this order:

        tools  ->  system  ->  messages

  So structure every prompt as:
      STABLE content FIRST   frozen system prompt, sorted tool list, documents
      VOLATILE content LAST  timestamps, user IDs, the actual question

  SILENT CACHE KILLERS - if cache_read_input_tokens is always 0, look for:
    * datetime.now() or a UUID inside the system prompt
    * json.dumps() without sort_keys=True (dict order varies between runs)
    * a tool list built in a different order each run
    * changing model or effort mid-conversation (caches are per-model)
    * a prefix shorter than the minimum cacheable size (~1024-4096 tokens)

  VERIFY IT, DON'T ASSUME IT. Print usage.cache_read_input_tokens on the
  second identical call. If it's zero, you're paying full price and getting
  nothing for the extra complexity.""")
print()


# =============================================================================
# PART 7 — THINKING AND EFFORT
# =============================================================================
print(LINE)
print("PART 7 — THINKING AND EFFORT")
print(LINE)

print('''      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=16000,
          thinking={"type": "adaptive", "display": "summarized"},
          output_config={"effort": "high"},    # low|medium|high|xhigh|max
          messages=[{"role": "user", "content": "Plan a database migration..."}],
      )

  THINKING - the model reasons privately before answering. On current models
  use {"type": "adaptive"}: the model decides how much thinking each request
  needs, rather than you guessing a fixed budget.

    WARNING ABOUT OLD TUTORIALS: you will find blog posts using
        thinking={"type": "enabled", "budget_tokens": 10000}
    That form is REMOVED on current models and returns a 400 error. Don't
    copy it. This is a good general lesson: LLM APIs move fast, and
    Stack Overflow answers from 18 months ago are often actively wrong.

  EFFORT - how much total work to spend on the request. This is your main
  quality/cost dial WITHIN a single model, and it is usually a better lever
  than downgrading to a weaker model:

    low     subagents, classification, simple lookups, high volume
    medium  routine work where quality demonstrably holds
    high    the default - most tasks
    xhigh   coding and long agentic runs
    max     when correctness matters more than cost

  Lower effort on a strong model often beats high effort on a weak one, AND
  keeps you in one cache namespace. Measure before changing a default.''')
print()


# =============================================================================
# PART 8 — ERROR HANDLING
# =============================================================================
print(LINE)
print("PART 8 — ERRORS")
print(LINE)

print('''  Lesson 12 and lesson 21, applied. Catch SPECIFIC exceptions, most specific
  first, and respect the retry/don't-retry split:

    import anthropic

    try:
        response = client.messages.create(...)

    except anthropic.AuthenticationError:
        # 401 - bad or missing key. NEVER retry.
        print("Check ANTHROPIC_API_KEY")
    except anthropic.BadRequestError as e:
        # 400 - malformed request. NEVER retry; fix the code.
        print(f"Bad request: {e.message}")
    except anthropic.NotFoundError:
        # 404 - usually a wrong model ID. NEVER retry.
        print("Unknown model or endpoint")
    except anthropic.RateLimitError as e:
        # 429 - DO retry, after the delay the server specifies.
        wait = int(e.response.headers.get("retry-after", "60"))
        print(f"Rate limited, retry in {wait}s")
    except anthropic.APIStatusError as e:
        # Any other HTTP error. 5xx -> retry.
        if e.status_code >= 500:
            print("Server error - retry with backoff")
    except anthropic.APIConnectionError:
        # Network failure - DO retry.
        print("Network problem")

  THE SDK ALREADY RETRIES 429 and 5xx twice with backoff. Configure it:
      client = anthropic.Anthropic(max_retries=5, timeout=60.0)
  You rarely need to write the retry loop from lesson 21 yourself - but you
  now understand exactly what it's doing, which is why it was worth writing.''')
print()

print("""  ALSO GUARD THE NON-EXCEPTION FAILURES - these return HTTP 200:
    stop_reason == "refusal"     the model declined; content may be empty
    stop_reason == "max_tokens"  the answer is truncated
  Neither raises. If you don't check, you ship broken output silently.""")
print()


# =============================================================================
# PART 9 — A REUSABLE CLIENT WRAPPER
# =============================================================================
print(LINE)
print("PART 9 — PUTTING IT TOGETHER")
print(LINE)


class ClaudeClient:
    """A small wrapper adding the things you always end up needing:
    safe defaults, stop_reason checking, and cost tracking."""

    def __init__(self, client, model=MODEL, system=None, budget_dollars=None):
        self.client = client
        self.model = model
        self.system = system
        self.budget = budget_dollars
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cached_tokens = 0
        self.spend = 0.0

    def ask(self, prompt, max_tokens=1000, effort="high"):
        """One-shot question. Returns text, or raises with a clear reason."""
        if self.budget is not None and self.spend >= self.budget:
            raise RuntimeError(f"budget of ${self.budget} exhausted "
                               f"(spent ${self.spend:.4f})")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system,
            output_config={"effort": effort},
            messages=[{"role": "user", "content": prompt}],
        )

        if response.stop_reason == "refusal":
            raise RuntimeError(f"model declined: {response.stop_details}")
        if response.stop_reason == "max_tokens":
            print(f"    WARNING: reply truncated at {max_tokens} tokens")

        self.calls += 1
        self.input_tokens += response.usage.input_tokens
        self.output_tokens += response.usage.output_tokens
        self.cached_tokens += getattr(response.usage, "cache_read_input_tokens", 0) or 0
        self.spend += estimate_cost(response.usage.input_tokens,
                                    response.usage.output_tokens, self.model)
        return extract_text(response)

    def report(self):
        return (f"{self.calls} calls | {self.input_tokens:,} in "
                f"({self.cached_tokens:,} cached) | {self.output_tokens:,} out "
                f"| ${self.spend:.6f}")


bot = ClaudeClient(client, system="Answer in one short sentence.",
                   budget_dollars=0.50)

for question in ["Why do programmers prefer dark mode?",
                 "What is a list comprehension?"]:
    print(f"    Q: {question}")
    print(f"    A: {bot.ask(question, max_tokens=100)}")
print(f"\n  usage: {bot.report()}")
print()

print("  budget enforcement in action:")
broke = ClaudeClient(client, budget_dollars=0.0)
try:
    broke.ask("anything")
except RuntimeError as error:
    print(f"    blocked: {error}")
print()


# =============================================================================
# PART 10 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 10 — COMMON MISTAKES")
print(LINE)
print("""   1. HARD-CODING THE API KEY. Use os.environ (lesson 21 part 5).

   2. TREATING response.content AS A STRING. It's a LIST of blocks. Use the
      extract_text() helper from part 2.

   3. NOT CHECKING stop_reason. You silently ship truncated or empty answers.

   4. max_tokens TOO LOW. It truncates mid-sentence; it does not summarise
      to fit.

   5. FORGETTING TO APPEND THE ASSISTANT TURN. The model appears to "forget"
      everything and you hunt for a bug in the wrong place.

   6. NO CACHING ON A REPEATED LARGE PREFIX. You pay ~10x more than needed.

   7. NOT VERIFYING THE CACHE WORKS. Check cache_read_input_tokens > 0.
      A silently broken cache costs money and looks fine.

   8. ASSUMING THE OUTPUT IS VALID JSON. Validate it (lesson 23 part 2).

   9. USING tiktoken TO COUNT TOKENS. Wrong tokeniser. Use count_tokens().

  10. COPYING `budget_tokens` THINKING CONFIG FROM OLD BLOG POSTS. Removed on
      current models; returns a 400.

  11. RETRYING A 400 OR 401. It will never succeed.

  12. NO COST MONITORING UNTIL THE BILL ARRIVES. Track usage from call one.
      A loop with a bug can spend a lot of money very quickly.

  13. BLOCKING A WEB REQUEST ON A 20-SECOND MODEL CALL. Stream it, or push it
      to a background job (lesson 24).""")
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# These all work in SIMULATED mode. Re-run them live once you have a key -
# the code doesn't change.
#
# EXERCISE 1 — Cost calculator
#   Write cost_report(input_tokens, output_tokens) that prints the cost on all
#   four models side by side, plus how much cheaper each is than Opus 5 as a
#   percentage. Run it for a 10,000-in / 1,000-out request.
#
# EXERCISE 2 — Truncation detector
#   Write ask_safely(prompt, max_tokens) that calls the model and, if
#   stop_reason is "max_tokens", automatically retries once with double the
#   max_tokens. Print a message when it does.
#
# EXERCISE 3 — A conversation with a memory limit
#   Extend the Conversation class with a `max_history` parameter. When the
#   message list exceeds it, drop the OLDEST turns (keeping pairs intact) and
#   print how many tokens that saved on the next call.
#
# EXERCISE 4 — Token budget guard
#   Write a function that takes a list of documents and returns as many as
#   will fit under a 20,000-token budget, using count_tokens. Report which
#   ones were dropped.
#
# EXERCISE 5 — Streaming with a progress indicator
#   Stream a response while counting characters, and print a live "received
#   N chars" counter on the same line (use \\r and flush=True).
#
# EXERCISE 6 — Terminal chatbot
#   Build a loop: read input(), send it through a Conversation, print the
#   reply, show the running cost, and exit on "quit". Add a "/cost" command
#   that prints the per-turn table from PART 3.
#
# EXERCISE 7 — Cost logger
#   Wrap ClaudeClient.ask so every call appends a row to a CSV in workspace/
#   with timestamp, model, prompt length, input tokens, output tokens and
#   cost. Then read it back with lesson 14's csv module and total the day.
#
# EXERCISE 8 — Model comparison harness
#   Write compare_models(prompt) that sends the same prompt to two models and
#   prints both answers side by side with their costs. (In simulated mode both
#   answers will match - the point is the harness, which you'll reuse in
#   lesson 23 for real evaluation.)
#
# EXERCISE 9 — Find the cache killer
#   Write two system prompts: one containing datetime.now(), one static. Print
#   both and explain which one can never be cached and why. Then fix the
#   broken one by moving the timestamp into the user message.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   def cost_report(input_tokens, output_tokens):
#       baseline = estimate_cost(input_tokens, output_tokens, "claude-opus-5")
#       print(f"{'model':<20}{'cost':>12}{'vs Opus 5':>12}")
#       for name in MODELS:
#           cost = estimate_cost(input_tokens, output_tokens, name)
#           delta = (cost - baseline) / baseline
#           print(f"{name:<20}${cost:>11.4f}{delta:>+11.0%}")
#   cost_report(10_000, 1_000)
#
# EXERCISE 2
#   def ask_safely(prompt, max_tokens=200):
#       for attempt in range(2):
#           response = client.messages.create(
#               model=MODEL, max_tokens=max_tokens,
#               messages=[{"role": "user", "content": prompt}])
#           if response.stop_reason != "max_tokens":
#               return extract_text(response)
#           print(f"    truncated at {max_tokens}, retrying at {max_tokens * 2}")
#           max_tokens *= 2
#       return extract_text(response)      # give up, return what we got
#
# EXERCISE 3
#   class TrimmedConversation(Conversation):
#       def __init__(self, *args, max_history=6, **kwargs):
#           super().__init__(*args, **kwargs)
#           self.max_history = max_history
#       def send(self, user_message, max_tokens=1000):
#           if len(self.messages) > self.max_history:
#               dropped = self.messages[:len(self.messages) - self.max_history]
#               # keep pairs intact: drop an even number of messages
#               cut = len(dropped) - (len(dropped) % 2)
#               saved = estimate_tokens(json.dumps(str(self.messages[:cut])))
#               self.messages = self.messages[cut:]
#               print(f"    trimmed {cut} messages, ~{saved} tokens saved")
#           return super().send(user_message, max_tokens)
#
# EXERCISE 4
#   def fit_documents(documents, budget=20_000):
#       kept, dropped, used = [], [], 0
#       for doc in documents:
#           tokens = client.messages.count_tokens(
#               model=MODEL, messages=[{"role": "user", "content": doc}]
#           ).input_tokens
#           if used + tokens <= budget:
#               kept.append(doc); used += tokens
#           else:
#               dropped.append((doc[:30], tokens))
#       print(f"kept {len(kept)} docs using {used:,} tokens")
#       for preview, tokens in dropped:
#           print(f"  dropped {preview!r} ({tokens:,} tokens)")
#       return kept
#
# EXERCISE 5
#   received = 0
#   with client.messages.stream(model=MODEL, max_tokens=200,
#           messages=[{"role": "user", "content": "Write a haiku about debugging."}]) as s:
#       for chunk in s.text_stream:
#           received += len(chunk)
#           print(f"\\r    received {received} chars", end="", flush=True)
#   print()
#
# EXERCISE 6
#   chat = Conversation(client, system="Be concise.")
#   while True:
#       try:
#           text = input("you > ").strip()
#       except (EOFError, KeyboardInterrupt):
#           break
#       if text.lower() in ("quit", "exit"):
#           break
#       if text == "/cost":
#           for i, t in enumerate(chat.turns, 1):
#               print(f"  turn {i}: {t['input']} in, {t['output']} out, ${t['cost']:.6f}")
#           continue
#       if not text:
#           continue
#       print("AI  >", chat.send(text))
#       print(f"      (running cost ${chat.total_cost:.6f})")
#
# EXERCISE 7
#   import csv
#   from datetime import datetime
#   LOG = HERE / "workspace" / "llm_calls.csv"
#   LOG.parent.mkdir(exist_ok=True)
#   def logged_ask(bot, prompt, **kwargs):
#       before = (bot.input_tokens, bot.output_tokens, bot.spend)
#       reply = bot.ask(prompt, **kwargs)
#       new = not LOG.exists()
#       with open(LOG, "a", encoding="utf-8", newline="") as f:
#           writer = csv.writer(f)
#           if new:
#               writer.writerow(["ts", "model", "prompt_chars", "in", "out", "cost"])
#           writer.writerow([datetime.now().isoformat(timespec="seconds"),
#                            bot.model, len(prompt),
#                            bot.input_tokens - before[0],
#                            bot.output_tokens - before[1],
#                            round(bot.spend - before[2], 6)])
#       return reply
#
# EXERCISE 8
#   def compare_models(prompt, models=("claude-opus-5", "claude-sonnet-5")):
#       for name in models:
#           bot = ClaudeClient(client, model=name)
#           answer = bot.ask(prompt, max_tokens=150)
#           print(f"\\n--- {name} (${bot.spend:.6f}) ---\\n{answer}")
#   # In lesson 23 you'll add a grader, turning this into a real eval.
#
# EXERCISE 9
#   from datetime import datetime
#   broken = f"You are an assistant. The time is {datetime.now()}."
#   fixed = "You are an assistant."
#   print("broken:", broken)
#   print("fixed :", fixed)
#   # `broken` changes on every single call, so the cached prefix never
#   # matches and cache_read_input_tokens stays 0 forever. The timestamp
#   # belongs in the user message, AFTER the cache breakpoint:
#   #     system=[{"type": "text", "text": fixed,
#   #              "cache_control": {"type": "ephemeral"}}]
#   #     messages=[{"role": "user",
#   #                "content": f"[time: {datetime.now()}]\\n{question}"}]


print("=" * 70)
print("Lesson 22 complete. Next: 23_ai_engineering_patterns.py")
print("=" * 70)

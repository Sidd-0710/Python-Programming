"""
===============================================================================
 LESSON 22 — CALLING THE CLAUDE API: LLM FUNDAMENTALS
===============================================================================

Time: about 100 minutes (there's a good place for a break halfway).
Assumes: lessons 01-21 (especially 09 dicts, 12 errors, 16 classes, 21 HTTP).

    TO RUN LIVE (optional - you do NOT need this to do the lesson):
        python3 -m venv .venv
        source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
        pip install anthropic
        export ANTHROPIC_API_KEY="sk-ant-..."

    WITHOUT A KEY THIS FILE STILL RUNS AND STILL TEACHES. It includes a small
    OFFLINE SIMULATOR that copies the SHAPE of the API's replies, so the
    conversation code, token counting, streaming loop and cost tracking all
    really run and print real output. Only the model's words are canned.
    (A live run makes 8 small model calls.)


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. pick a model and work out what a call will cost               (PART 1)
  2. make your first call and read the reply safely                (PART 2)
  3. hold a conversation by resending the history                  (PART 3)
  4. stream a reply so words appear as they're written             (PART 4)
  5. count tokens BEFORE you spend money                           (PART 5)
  6. cut costs with prompt caching                                 (PART 6)
  7. use thinking and effort                                       (PART 7)
  8. handle errors, and wrap it all in one reusable class          (PARTS 8-9)

NEW WORDS - come back here whenever you forget one:

  LLM             Large Language Model - a program that writes text by
                  predicting what comes next. Claude is one.
  model           one specific version of the LLM, named by an ID string
                  such as "claude-opus-5"
  SDK             a ready-made Python package for an API. `pip install
                  anthropic` gives you one, so you never hand-write the HTTP
  API key         your secret password for the API (lesson 21 PART 5)
  prompt          the text you send to the model
  system prompt   standing instructions for the whole conversation, such as
                  "You are a concise Python tutor."
  messages        the conversation so far: a list of dicts, each with a
                  "role" ("user" or "assistant") and some "content"
  token           a small chunk of text, about 3-4 characters of English.
                  You pay per token.
  input tokens    the tokens you SEND (your prompt plus all the history)
  output tokens   the tokens the model WRITES back (these cost more)
  max_tokens      the most output tokens you allow - a hard ceiling
  content block   one piece of a reply: a "text" block, a "thinking" block,
                  a "tool_use" block...
  stop_reason     WHY the reply ended: it finished, it hit max_tokens, ...
  stateless       remembers nothing between calls
  context window  the most tokens a single request can hold
  streaming       receiving the reply bit by bit, while it's being written
  prompt caching  storing the repeated start of a prompt so resending it
                  is cheap
  thinking        the model reasoning privately before it answers
  effort          a dial for how hard the model works: low ... max


-------------------------------------------------------------------------------
 THEORY: WHAT AN LLM API ACTUALLY IS
-------------------------------------------------------------------------------

Strip away the mystery and it is lesson 21 again - an HTTP POST with JSON:

    POST https://api.anthropic.com/v1/messages
    x-api-key: sk-ant-...
    content-type: application/json

    {"model": "claude-opus-5", "max_tokens": 1024,
     "messages": [{"role": "user", "content": "Hello"}]}

You send a list of messages. You get a message back. That is the entire API.
Everything else - agents, RAG, tool use, chatbots - is built on top of that one
request by ordinary Python code that you write.

In plain English: "here's the conversation so far - what do you say next?"


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
    separately, and output costs 5x more. Cost control is part of the job
    from the first line of code, not something you bolt on later.

 3. IT IS NON-DETERMINISTIC.
    In plain English: the same question can get a different answer each time.
    So you can't test it with a simple "assert answer == expected". This is
    why EVALUATION exists (lesson 23), and why "it worked when I tried it
    once" means almost nothing.

 4. IT HAS A CONTEXT WINDOW.
    A hard ceiling on how much you can send in one request. The newest models
    accept 1,000,000 tokens (Haiku 4.5: 200,000) - large, but not infinite,
    and you pay for all of it every time.

 5. IT CAN BE CONFIDENTLY WRONG.
    The model writes plausible text, and plausible is not the same as true.
    Never wire raw model output straight into something you can't undo
    (deleting files, sending emails, moving money).

 6. LATENCY IS SECONDS, NOT MILLISECONDS.
    A normal database query takes 5 milliseconds. A model call takes 2-30
    seconds. That changes your whole design: you need streaming (PART 4),
    timeouts, and usually background jobs instead of making a web page wait.
"""

import json
import os
import time
from pathlib import Path

LINE = "-" * 70
HERE = Path(__file__).resolve().parent

# The model ID to use. Always the exact string, never with a date added.
MODEL = "claude-opus-5"

# Is the `anthropic` SDK installed? Try to import it and see.
# In plain English: "try to load the package; if it isn't installed, remember
# that instead of crashing." (try/except is lesson 12.)
try:
    import anthropic
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

# os.environ.get returns None when the variable isn't set (lesson 21 PART 5).
API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# We only go LIVE when BOTH are true: the SDK is installed AND a key is set.
LIVE = SDK_AVAILABLE and bool(API_KEY)


# =============================================================================
# THE OFFLINE SIMULATOR - SCENERY, YOU CAN SKIP READING IT
# =============================================================================
# Everything in this block is a pretend Claude that runs on your own machine.
# You do NOT need to understand it. It is NOT how you talk to Claude - it only
# copies the SHAPE of a real reply, so the code in PARTS 1-9 (which IS real,
# and works unchanged against the live API) has something to work with.
#
# The shape it copies is the three things your code actually touches:
#   response.content      a LIST of blocks (a thinking block, then a text block)
#   response.usage        token counts: input_tokens, output_tokens, ...
#   response.stop_reason  why the reply ended
#
# Scroll down to "END OF THE SCENERY".
# -----------------------------------------------------------------------------

class FakeTextBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class FakeThinkingBlock:
    # Opus 5 thinks by default. Unless you ask for a summary, the thinking
    # text comes back EMPTY - the block is there, the words are not.
    def __init__(self, thinking):
        self.type = "thinking"
        self.thinking = thinking


class FakeUsage:
    def __init__(self, input_tokens, output_tokens, cache_read=0):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.cache_read_input_tokens = cache_read
        self.cache_creation_input_tokens = 0


class FakeResponse:
    def __init__(self, text, thinking_text, input_tokens, output_tokens):
        self.content = [FakeThinkingBlock(thinking_text), FakeTextBlock(text)]
        self.usage = FakeUsage(input_tokens, output_tokens)
        self.stop_reason = "end_turn"
        self.stop_details = None
        self.model = "offline-simulator"


def estimate_tokens(text):
    """A rough token estimate: about 4 characters per token for English."""
    return max(1, len(str(text)) // 4)


class FakeMessages:
    """Imitates client.messages - just enough for this lesson to run."""

    def __init__(self, parent):
        self.parent = parent

    def _canned_reply(self, messages):
        """Produce a plausible-looking reply, with a little 'memory'."""
        last = messages[-1]["content"]
        if isinstance(last, list):
            last = " ".join(str(b) for b in last)
        lowered = str(last).lower()

        # A crude "memory" so the multi-turn demo visibly works.
        history_text = " ".join(str(m.get("content", "")) for m in messages).lower()
        if "what's my name" in lowered or "what is my name" in lowered:
            if "sidd" in history_text:
                return "Your name is Sidd, and you are learning Python."
        if "what am i learning" in lowered and "python" in history_text:
            return "You are learning Python."
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
        text = self._canned_reply(messages)

        thinking_text = ""
        if thinking and thinking.get("display") == "summarized":
            thinking_text = "(simulated summary) Short question - answer briefly."

        # Input tokens = the WHOLE conversation plus the system prompt, every
        # time. This is the stateless-cost reality, simulated faithfully.
        input_tokens = estimate_tokens(json.dumps(str(messages))) + \
            estimate_tokens(str(system) if system else "")
        output_tokens = estimate_tokens(text)

        time.sleep(0.05)                              # a hint of real latency
        self.parent.call_count += 1
        return FakeResponse(text, thinking_text, input_tokens, output_tokens)

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
        text = self._final.content[-1].text           # the text block is last
        for index in range(0, len(text), 6):
            time.sleep(0.01)
            yield text[index:index + 6]

    def get_final_message(self):
        return self._final


class FakeAnthropic:
    def __init__(self, **kwargs):
        self.messages = FakeMessages(self)
        self.call_count = 0

# ======================= END OF THE SCENERY - START READING HERE =============


# Choose the real client or the simulator.
# In plain English: "if the SDK is installed AND a key is set, talk to the
# real Claude; otherwise use the pretend one." Every line after this just
# uses the name `client` and doesn't care which one it got.
#
# The real line is the one to remember:
#     client = anthropic.Anthropic()        # finds ANTHROPIC_API_KEY by itself
if LIVE:
    client = anthropic.Anthropic(max_retries=3, timeout=60.0)
else:
    client = FakeAnthropic()

if LIVE:
    mode_label = "LIVE (real API calls)"
else:
    mode_label = "SIMULATED"

print(LINE)
print("SETUP CHECK")
print(LINE)
print(f"  anthropic SDK installed : {SDK_AVAILABLE}")
print(f"  ANTHROPIC_API_KEY set   : {bool(API_KEY)}")
print(f"  mode                    : {mode_label}")
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
# because writing text is more work than reading it.
# In plain English: each model name points to a small dict of facts about it.
#   "in"       dollars per million INPUT tokens
#   "out"      dollars per million OUTPUT tokens
#   "context"  the context window ("1M" = one million tokens)
MODELS = {
    "claude-fable-5-1": {"in": 10.00, "out": 50.00, "context": "1M",
                         "use": "hardest reasoning, long agentic runs"},
    "claude-opus-5":    {"in": 5.00, "out": 25.00, "context": "1M",
                         "use": "DEFAULT - best all-round"},
    "claude-sonnet-5":  {"in": 2.00, "out": 10.00, "context": "1M",
                         "use": "high-volume production work"},
    "claude-haiku-4-5": {"in": 1.00, "out": 5.00, "context": "200K",
                         "use": "simple, speed-critical tasks"},
}

print(f"  {'model':<20}{'ctx':>6}{'$in/1M':>9}{'$out/1M':>9}  use for")
print("  " + "-" * 74)
for name, info in MODELS.items():
    print(f"  {name:<20}{info['context']:>6}{info['in']:>9.2f}"
          f"{info['out']:>9.2f}  {info['use']}")

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
    if model not in MODELS:          # an unknown name? price it like the default
        model = MODEL
    prices = MODELS[model]
    input_cost = input_tokens / 1_000_000 * prices["in"]
    output_cost = output_tokens / 1_000_000 * prices["out"]
    return input_cost + output_cost

# In plain English: "tokens divided by a million, times the price per
# million - once for what you sent, once for what came back - then add them."
#
# 1_000_000 is just 1000000. Python lets you put _ inside numbers so they're
# easier to read; the underscores are ignored.


print("  what things actually cost on Opus 5:")
# Each row is a tuple of (label, input tokens, output tokens), and the `for`
# line unpacks each tuple into three names (lesson 08).
for label, tokens_in, tokens_out in [
    ("a short question", 50, 200),
    ("summarise a 10-page doc", 5_000, 500),
    ("a 10k-token RAG prompt", 10_000, 800),
    ("a 20-turn chat (total)", 60_000, 6_000),
    ("1,000 RAG calls/day", 10_000_000, 800_000),
    ("the same, monthly", 300_000_000, 24_000_000),
]:
    # :>12,.4f  = right-align in 12 spaces, commas for thousands, 4 decimals
    print(f"    {label:<26}${estimate_cost(tokens_in, tokens_out):>12,.4f}")

print("\n  the same daily volume, per model:")
for name in MODELS:
    print(f"    {name:<20}${estimate_cost(10_000_000, 800_000, name):>10,.2f}/day")
print()

# TRY IT NOW (2 minutes):
#   What does a call with 500 input tokens and 2,000 output tokens cost on
#   Opus 5? Work it out on paper first, then check it by adding:
#       print(estimate_cost(500, 2_000))
#   [$0.0525 - and notice that the OUTPUT is about 95% of that.]


# =============================================================================
# PART 2 — YOUR FIRST CALL, AND THE SHAPE OF A RESPONSE
# =============================================================================
print(LINE)
print("PART 2 — THE MESSAGES API")
print(LINE)

print('''  THE STANDARD CALL:

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
              in the conversation - think of it as a rule that always applies.
    messages  the conversation itself, a list of {"role", "content"} dicts,
              taking turns: user, assistant, user, assistant...

  max_tokens is a HARD CAP. Set it too low and the reply is CHOPPED OFF
  mid-sentence - the model does not shorten its answer to fit. Default to
  about 16000 for normal calls and about 64000 when streaming.''')
print()

response = client.messages.create(
    model=MODEL,
    max_tokens=1000,
    system="You are a concise Python tutor. Answer in under 40 words.",
    messages=[{"role": "user", "content": "What is a list comprehension?"}],
)

print("  A REAL RESPONSE OBJECT:")
print(f"    type(response.content) : {type(response.content).__name__}  <- a LIST")
print(f"    len(response.content)  : {len(response.content)}")
# enumerate gives us the position AND the block (lesson 07).
for number, block in enumerate(response.content):
    print(f"    content[{number}].type        : {block.type}")
print(f"    stop_reason            : {response.stop_reason}")
print(f"    usage.input_tokens     : {response.usage.input_tokens}")
print(f"    usage.output_tokens    : {response.usage.output_tokens}")
print(f"    model                  : {response.model}")
print()

# ***** response.content IS A LIST, NOT A STRING *****
# This catches everyone once. A reply can contain several blocks: thinking,
# text, tool_use. You must pick out the ones you want.
#
# WHY IS THERE A "thinking" BLOCK? Opus 5 THINKS BY DEFAULT: before answering
# it often reasons privately, and that reasoning arrives as a "thinking"
# block BEFORE the text block. So response.content[0] is often NOT the
# answer - and a thinking block has no .text at all. That's why you never
# write response.content[0].text; you use the helper below.

def extract_text(response):
    """Pull the plain text out of a response. You'll want this in every project."""
    pieces = []
    for block in response.content:
        if block.type == "text":             # skip thinking / tool_use blocks
            pieces.append(block.text)
    return "".join(pieces)

# In plain English: "go through every block; keep the text of the text blocks;
# glue them together into one string."

print("  the helper you'll copy into every project:")
print("      def extract_text(response):")
print("          pieces = []")
print("          for block in response.content:")
print('              if block.type == "text":')
print("                  pieces.append(block.text)")
print('          return "".join(pieces)')
print()
print("  result:", extract_text(response))
first_cost = estimate_cost(response.usage.input_tokens, response.usage.output_tokens)
print(f"  cost  : ${first_cost:.6f}")
print()

print("""  ALWAYS CHECK stop_reason BEFORE TRUSTING THE OUTPUT:
    end_turn    finished naturally               -> good
    max_tokens  CUT OFF mid-sentence             -> raise max_tokens and retry
    tool_use    it wants to call a tool          -> lesson 23
    refusal     declined on safety grounds       -> read response.stop_details
                                                    (.category, .explanation);
                                                    the content may be empty
  (Two rarer ones you'll meet later: stop_sequence and pause_turn.)

  Shipping cut-off answers because you never checked stop_reason is one of
  the most common bugs in real LLM code.""")
print()

# TRY IT NOW (2 minutes):
#   1. Change the question in the messages list above to one of your own and
#      re-run. (Simulated mode gives a canned reply, but the token counts,
#      the blocks and the stop_reason are all real code.)
#   2. In simulated mode, add  print(response.content[0].text)  and run it.
#      [AttributeError - content[0] is the thinking block, which has no
#      .text. That's exactly the bug extract_text() protects you from.
#      Delete the line afterwards.]


# =============================================================================
# PART 3 — CONVERSATIONS ARE JUST A GROWING LIST
# =============================================================================
print(LINE)
print("PART 3 — MULTI-TURN CONVERSATIONS")
print(LINE)

print("""  The API is stateless. "Memory" is entirely your job: you keep a list
  and resend all of it every time.

    Turn 1 sends:  [user]
    Turn 2 sends:  [user, assistant, user]
    Turn 3 sends:  [user, assistant, user, assistant, user]

  Forget to add the assistant's reply to the list and the model "loses its
  memory" - a bug that looks mysterious and has a very boring cause.""")
print()


class Conversation:
    """Manages a multi-turn conversation and tracks what it costs."""

    def __init__(self, client, model=MODEL, system=None):
        self.client = client
        self.model = model
        self.system = system
        self.messages = []              # the whole conversation, resent each time
        self.turns = []                 # token counts and cost for each turn

    def send(self, user_message, max_tokens=1000):
        # Step 1: add the user's new message to the history.
        self.messages.append({"role": "user", "content": user_message})

        # Step 2: send the WHOLE history.
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system,
            messages=self.messages,
        )

        # Step 3: add the reply to the history.
        # THE CRITICAL LINE - without it, the next call has no context.
        reply = extract_text(response)
        self.messages.append({"role": "assistant", "content": reply})

        # Step 4: write down what this turn cost.
        cost = estimate_cost(response.usage.input_tokens,
                             response.usage.output_tokens, self.model)
        self.turns.append({
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
            "cost": cost,
        })
        return reply

    def total_cost(self):
        total = 0.0
        for turn in self.turns:
            total += turn["cost"]
        return total


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
total_input = 0
total_output = 0
for index, turn in enumerate(chat.turns, start=1):
    # turn 1 sends 1 message, turn 2 sends 3, turn 3 sends 5 ... = index*2 - 1
    messages_sent = index * 2 - 1
    money = f"${turn['cost']:.6f}"
    print(f"    {index:<6}{messages_sent:>15}{turn['input']:>11}"
          f"{turn['output']:>12}{money:>12}")
    total_input += turn["input"]
    total_output += turn["output"]
total_money = f"${chat.total_cost():.6f}"
print(f"    {'TOTAL':<6}{'':<15}{total_input:>11}{total_output:>12}{total_money:>12}")

growth = chat.turns[-1]["input"] / chat.turns[0]["input"]
print(f"""
  Turn 4's input is about {growth:.1f}x turn 1's, for the same kind of short
  question. Over 30 turns this takes over your whole bill.

  THE THREE FIXES:
    1. PROMPT CACHING (PART 6) - up to 90% off the repeated start
    2. TRIM OLD TURNS - keep only the last few, or summarise the older ones
    3. SERVER-SIDE COMPACTION - on very long chats the API can summarise the
       older history for you""")
print()

# TRY IT NOW (2 minutes):
#   Add a fifth message to the list above, e.g. "What was my first message?",
#   and re-run. Turn 5's input tokens are bigger again - you paid for all
#   four earlier turns one more time.


# =============================================================================
# PART 4 — STREAMING
# =============================================================================
print(LINE)
print("PART 4 — STREAMING")
print(LINE)

print('''  Without streaming, the user stares at a blank screen for 20 seconds and
  then gets a wall of text. With streaming, words appear as they're written.
  Same total time, completely different experience - and it avoids HTTP
  timeouts on long replies.

    with client.messages.stream(
        model="claude-opus-5",
        max_tokens=64000,                  # streaming lets you go big safely
        messages=[{"role": "user", "content": "Write a haiku about debugging."}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

        final = stream.get_final_message()      # the full object, once done
        print(final.usage.output_tokens)

  STEP BY STEP:
    with ... as stream:     opens the stream and closes it cleanly at the end -
                            the same idea as  with open(...) as file  (lesson 13)
    stream.text_stream      hands you the reply one small piece at a time
    end=""                  print each piece WITHOUT starting a new line
    flush=True              show it NOW. Without it Python saves up the output
                            and prints it all at once, which defeats the point.
    get_final_message()     after the loop: the complete reply, with usage and
                            stop_reason, just like create() returns''')
print()

print("  watch it arrive piece by piece:")
print("    ", end="", flush=True)
with client.messages.stream(
    model=MODEL,
    max_tokens=1000,
    messages=[{"role": "user", "content": "Write a haiku about debugging."}],
) as stream:
    for chunk in stream.text_stream:
        print(chunk, end="", flush=True)
    final = stream.get_final_message()
print(f"\n\n    [{final.usage.output_tokens} output tokens, "
      f"stop_reason={final.stop_reason}]")
print()

print("""  RULE: stream anything with a large max_tokens or a human waiting on it.
  Use plain create() for short background jobs where nobody is watching.""")
print()

# TRY IT NOW (1 minute):
#   In the loop above, change  print(chunk, end="", flush=True)  to just
#   print(chunk)  and re-run. Every piece lands on its own line - now you can
#   SEE the chunks. Put it back afterwards.


# =============================================================================
# PART 5 — COUNTING TOKENS BEFORE YOU SPEND
# =============================================================================
print(LINE)
print("PART 5 — TOKEN COUNTING")
print(LINE)

print("""  A token is roughly 3-4 characters of English - about 0.75 words. But
  "roughly" is not good enough when you're about to send a 200-page PDF.

  The API will count exactly, before you spend anything on a reply:

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

print("  data/server.log:")
print(f"    characters       : {len(log_text):,}")
print(f"    words            : {len(log_text.split()):,}")
print(f"    tokens (counted) : {count.input_tokens:,}")
print(f"    chars per token  : {len(log_text) / count.input_tokens:.1f}")
print(f"    cost to send once: ${estimate_cost(count.input_tokens, 0):.6f}")
print(f"    cost x1000/day   : ${estimate_cost(count.input_tokens, 0) * 1000:.2f}")
print()


def guard_size(text, limit=50_000, model=MODEL):
    """Refuse to send something enormous by accident. Use this at boundaries."""
    count = client.messages.count_tokens(
        model=model,
        messages=[{"role": "user", "content": text}],
    )
    tokens = count.input_tokens
    if tokens > limit:
        raise ValueError(
            f"input is {tokens:,} tokens, over the {limit:,} limit "
            f"(would cost ${estimate_cost(tokens, 0):.2f}). "
            f"Chunk it or summarise it first."
        )
    return tokens

# In plain English: "count the tokens; if there are too many, stop with a
# clear error; otherwise tell me the count."

print("  a guard worth having in production:")
try:
    guard_size("x" * 500_000, limit=50_000)      # "x" * 500_000 = 500,000 x's
except ValueError as error:
    print(f"    blocked: {error}")
print()

# TRY IT NOW (1 minute):
#   Add  print(guard_size("Hello, Claude!"))  - a small number, which passes
#   the guard. (It's a few tokens more than the words alone, because the
#   message wrapping counts too.)


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. You can now call the API, hold a conversation,
#  stream, and count the cost - that's the core. After the break: caching,
#  thinking, errors, and one tidy class that puts it all together.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 6 — PROMPT CACHING: THE BIGGEST COST LEVER
# =============================================================================
print(LINE)
print("PART 6 — PROMPT CACHING")
print(LINE)

print('''  If you send the same large START of a prompt again and again - a long
  system prompt, a reference document, a tool list - you can CACHE it.
  Reading from the cache costs about 10% of the normal input price.

  THE SIMPLEST FORM - let the API choose where the cache ends:

      response = client.messages.create(
          model="claude-opus-5",
          max_tokens=16000,
          cache_control={"type": "ephemeral"},        # "please cache this"
          system=large_document,                      # the big, same-every-time part
          messages=[{"role": "user", "content": question}],   # changes each call
      )

  OR MARK THE EXACT SPOT YOURSELF:

      system=[{
          "type": "text",
          "text": large_document,                    # 50k tokens of context
          "cache_control": {"type": "ephemeral"},    # cache up to HERE
      }]

  "ephemeral" means temporary: the cache lasts about 5 minutes, and each time
  it's used the clock restarts. (A longer option exists: "ttl": "1h".)

  CHECK IT WORKED - the reply's usage tells you:
      response.usage.cache_creation_input_tokens   # written to cache (~1.25x price)
      response.usage.cache_read_input_tokens       # read from cache  (~0.1x price)''')
print()

# The arithmetic, step by step, because the saving is easy to underestimate.
document_tokens = 50_000
question_tokens = 100
output_tokens = 500
calls = 100

# WITHOUT caching: every call pays full price for the whole document.
one_normal_call = estimate_cost(document_tokens + question_tokens, output_tokens)
uncached_total = calls * one_normal_call

# WITH caching:
#   the FIRST call writes the document into the cache - 25% extra (x 1.25)
first_call = estimate_cost(document_tokens * 1.25 + question_tokens, output_tokens)
#   every LATER call reads the document from the cache - 10% of the price
cached_read_cost = document_tokens * 0.1 / 1_000_000 * MODELS[MODEL]["in"]
later_call = estimate_cost(question_tokens, output_tokens) + cached_read_cost
cached_total = first_call + (calls - 1) * later_call

saved = uncached_total - cached_total

print(f"  {calls} questions against the same {document_tokens:,}-token document:")
print(f"    without caching : ${uncached_total:>8.2f}")
print(f"    with caching    : ${cached_total:>8.2f}")
print(f"    saved           : ${saved:>8.2f} ({saved / uncached_total:.0%})")
print()

print("""  ***** THE RULE THAT MATTERS: CACHING IS A PREFIX MATCH *****

  PREFIX means "the start". The cache only works if the start of your
  request is EXACTLY the same, byte for byte, as last time. Change one
  character early on and everything after it is a cache miss.

  The request is put together in this order:

        tools  ->  system  ->  messages

  So build every prompt like this:
      STABLE things FIRST   the fixed system prompt, a sorted tool list, documents
      CHANGING things LAST  timestamps, user IDs, the actual question

  SILENT CACHE KILLERS - if cache_read_input_tokens is always 0, look for:
    * datetime.now() or a random ID inside the system prompt
    * json.dumps() without sort_keys=True (the key order can change)
    * a tool list built in a different order each run
    * switching model or effort mid-conversation (each model has its own cache)
    * a prefix that's too SHORT - below the minimum cacheable size, which is
      512 to 4096 tokens depending on the model

  VERIFY IT, DON'T ASSUME IT. Print usage.cache_read_input_tokens on the
  second identical call. If it's zero, you're paying full price and getting
  nothing for the extra effort.""")
print()

# TRY IT NOW (2 minutes):
#   Change  calls = 100  to  calls = 1  and re-run.
#   [Caching now COSTS money - "saved" goes negative - because you paid the
#   25% extra to write the cache and never read it back. Caching only pays
#   when the same start of the prompt is sent at least twice.]


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

  THINKING - the model reasons privately before it answers.
    * On Opus 5 thinking is ON BY DEFAULT, in "adaptive" mode: the model
      decides for itself how much each request needs. Writing
      {"type": "adaptive"} just says so out loud.
    * By default the thinking text comes back EMPTY (the block is there, the
      words are hidden). Add "display": "summarized" to get a readable
      summary of the reasoning.
    * Thinking tokens are billed as OUTPUT tokens and count toward
      max_tokens - one more reason not to set max_tokens too low.

    WARNING ABOUT OLD TUTORIALS: you will find blog posts using
        thinking={"type": "enabled", "budget_tokens": 10000}
    On Opus 5, Sonnet 5 and Fable 5.1 that form is REMOVED and returns a 400
    error. Don't copy it. The bigger lesson: LLM APIs move fast, and answers
    from 18 months ago are often simply wrong now.

  EFFORT - how much work to put into the request. It lives inside
  output_config, and "high" is the default. This is your main quality/cost
  dial WITHIN one model, and it is usually a better lever than switching to
  a weaker model:

    low     sub-tasks, classification, simple lookups, high volume
    medium  routine work where you've checked quality holds
    high    the default - most tasks
    xhigh   coding and long agent runs
    max     when being right matters more than cost

  Lower effort on a strong model often beats high effort on a weak one, AND
  keeps you in one cache. Measure before changing a default.''')
print()


# =============================================================================
# PART 8 — ERROR HANDLING
# =============================================================================
print(LINE)
print("PART 8 — ERRORS")
print(LINE)

print('''  Lesson 12 and lesson 21, applied. Catch SPECIFIC exceptions, most specific
  first, and respect the retry / don't-retry split:

    import anthropic

    try:
        response = client.messages.create(...)

    except anthropic.AuthenticationError:
        # 401 - bad or missing key. NEVER retry.
        print("Check ANTHROPIC_API_KEY")
    except anthropic.BadRequestError as e:
        # 400 - something in your request is wrong. NEVER retry; fix the code.
        print(f"Bad request: {e.message}")       # e.message = the API's reason
    except anthropic.NotFoundError:
        # 404 - usually a wrong model ID. NEVER retry.
        print("Unknown model or endpoint")
    except anthropic.RateLimitError as e:
        # 429 - DO retry, after the delay the server asks for.
        wait = int(e.response.headers.get("retry-after", "60"))
        print(f"Rate limited, retry in {wait}s")
    except anthropic.APIStatusError as e:
        # Any other HTTP error. 5xx -> retry.
        if e.status_code >= 500:
            print("Server error - retry with backoff")
    except anthropic.APIConnectionError:
        # Network failure - DO retry.
        print("Network problem")

  Why this order? Python checks the except lines top to bottom and uses the
  FIRST one that matches. APIStatusError is the general "some HTTP error"
  class, so it goes AFTER the specific ones - otherwise it would catch
  everything and the specific lines would never run.

  THE SDK ALREADY RETRIES for you - network errors, 408, 409, 429 and 5xx -
  2 times by default, waiting longer each time. The default timeout is 10
  minutes. You can change both:
      client = anthropic.Anthropic(max_retries=5, timeout=60.0)
  You rarely need to write lesson 21's retry loop yourself - but now you
  understand exactly what it's doing, which is why it was worth writing.''')
print()

print("""  ALSO GUARD THE FAILURES THAT AREN'T EXCEPTIONS - these return HTTP 200:
    stop_reason == "refusal"     the model declined; the content may be empty
    stop_reason == "max_tokens"  the answer was cut off
  Neither raises an error. If you don't check, you ship broken output
  silently.

  OPTIONAL, ADVANCED - REFUSAL FALLBACKS. On Opus 5 you can ask the API to
  re-run a refused request on another model automatically (a beta feature):
      client.beta.messages.create(..., betas=["server-side-fallback-2026-07-01"],
                                  fallbacks="default")
  You don't need it for this course - just know it exists.""")
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
        self.budget = budget_dollars       # None means "no limit"
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cached_tokens = 0
        self.spend = 0.0

    def ask(self, prompt, max_tokens=1000, effort="high"):
        """One-shot question. Returns the text, or raises with a clear reason."""
        # Step 1: refuse to start if the budget is already used up.
        if self.budget is not None and self.spend >= self.budget:
            raise RuntimeError(f"budget of ${self.budget} exhausted "
                               f"(spent ${self.spend:.4f})")

        # Step 2: make the call.
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system,
            output_config={"effort": effort},
            messages=[{"role": "user", "content": prompt}],
        )

        # Step 3: record what it cost - even a bad reply was paid for.
        self.calls += 1
        self.input_tokens += response.usage.input_tokens
        self.output_tokens += response.usage.output_tokens
        cached = response.usage.cache_read_input_tokens
        if cached:                          # None or 0 both mean "nothing cached"
            self.cached_tokens += cached
        self.spend += estimate_cost(response.usage.input_tokens,
                                    response.usage.output_tokens, self.model)

        # Step 4: check WHY the reply ended before trusting it.
        if response.stop_reason == "refusal":
            raise RuntimeError(f"model declined: {response.stop_details}")
        if response.stop_reason == "max_tokens":
            print(f"    WARNING: reply cut off at {max_tokens} tokens")

        return extract_text(response)

    def report(self):
        return (f"{self.calls} calls | {self.input_tokens:,} in "
                f"({self.cached_tokens:,} cached) | {self.output_tokens:,} out "
                f"| ${self.spend:.6f}")


bot = ClaudeClient(client, system="Answer in one short sentence.",
                   budget_dollars=0.50)

# effort="low": these are easy questions, so there's no need to work hard.
for question in ["Why do programmers prefer dark mode?",
                 "What is a list comprehension?"]:
    print(f"    Q: {question}")
    print(f"    A: {bot.ask(question, effort='low')}")
print(f"\n  usage: {bot.report()}")
print()

print("  budget enforcement in action:")
broke = ClaudeClient(client, budget_dollars=0.0)
try:
    broke.ask("anything")
except RuntimeError as error:
    print(f"    blocked: {error}")
print()

# TRY IT NOW (2 minutes):
#   Add a third question to the list above and re-run. Then look at the usage
#   line: the calls, tokens and cost all went up by one call's worth.


# =============================================================================
# PART 10 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 10 — COMMON MISTAKES")
print(LINE)
print("""   1. HARD-CODING THE API KEY. Use os.environ (lesson 21 part 5).

   2. TREATING response.content AS A STRING. It's a LIST of blocks. Use the
      extract_text() helper from part 2.

   3. READING response.content[0].text. The first block is often a THINKING
      block, which has no .text. Use extract_text().

   4. NOT CHECKING stop_reason. You silently ship cut-off or empty answers.

   5. max_tokens TOO LOW. It cuts off mid-sentence; it does not shorten the
      answer to fit. And thinking tokens count toward it too.

   6. FORGETTING TO ADD THE ASSISTANT'S REPLY TO THE HISTORY. The model
      seems to "forget" everything and you hunt for a bug in the wrong place.

   7. NO CACHING ON A REPEATED LARGE PREFIX. You pay ~10x more than needed.

   8. NOT CHECKING THE CACHE WORKS. Look for cache_read_input_tokens > 0.
      A silently broken cache costs money and looks fine.

   9. ASSUMING THE OUTPUT IS VALID JSON. Validate it (lesson 23 part 2).

  10. USING tiktoken TO COUNT TOKENS. Wrong tokeniser. Use count_tokens().

  11. COPYING `budget_tokens` THINKING SETTINGS FROM OLD BLOG POSTS. Removed on
      Opus 5, Sonnet 5 and Fable 5.1; it returns a 400.

  12. RETRYING A 400 OR 401. It will never succeed.

  13. NO COST TRACKING UNTIL THE BILL ARRIVES. Track usage from call one.
      A loop with a bug can spend a lot of money very quickly.

  14. MAKING A WEB PAGE WAIT 20 SECONDS FOR A MODEL CALL. Stream it, or hand
      it to a background job (lesson 24).""")
print()


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * A Claude call is one HTTP POST: model + max_tokens + (system) + messages.
#     The SDK does the HTTP for you: client.messages.create(...).
#   * You pay per token, in and out; output costs 5x more. estimate_cost()
#     turns token counts into dollars.
#   * response.content is a LIST of blocks. Opus 5 often puts a thinking block
#     first, so always use extract_text(), never content[0].text.
#   * Always check stop_reason: end_turn is good; max_tokens means cut off;
#     refusal means declined.
#   * The API is stateless: a conversation is a list you resend every time,
#     so every turn costs more than the last.
#   * Stream long replies (with ... as stream / text_stream / flush=True).
#   * count_tokens tells you the size BEFORE you spend.
#   * Prompt caching makes a repeated START of a prompt ~90% cheaper - but only
#     if that start is byte-for-byte identical every time.
#   * Opus 5 thinks by default; effort (low ... max) is your quality/cost dial.
#   * Catch specific exceptions; the SDK already retries 429s and 5xx.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. On turn 5 of a chat, how much of the conversation do you send?
#   Q2. Which costs more per token on every Claude model: input or output?
#   Q3. A reply comes back with stop_reason "max_tokens". What happened, and
#       what do you do?
#   Q4. Why is  response.content[0].text  risky?
#   Q5. cache_read_input_tokens is 0 on every call. Name one likely cause.
#
# ANSWERS
#   A1. All of it - every earlier message. The API remembers nothing.
#   A2. Output - 5x the input price.
#   A3. The reply was cut off. Raise max_tokens and try again.
#   A4. content is a list, and the first block is often a thinking block with
#       no .text. Use extract_text().
#   A5. Something at the start of the prompt changes each call (e.g. a
#       datetime.now() in the system prompt), or the prefix is below the
#       minimum cacheable size.


# =============================================================================
# EXERCISES
# =============================================================================
#
# These all work in SIMULATED mode. Re-run them live once you have a key -
# the code doesn't change.
#
# WARM-UP A (easy) — What does it cost?
#   Use estimate_cost to print what 2,000 input tokens and 300 output tokens
#   cost on "claude-sonnet-5".
#
# WARM-UP B (easy) — Ask your own question
#   Call client.messages.create with a question of your own (model=MODEL,
#   max_tokens=1000). Print extract_text(response) and response.stop_reason.
#
# WARM-UP C (easy) — Count before you send
#   Use client.messages.count_tokens to count the tokens in a sentence of
#   your choice, and print count.input_tokens.
#
# EXERCISE 1 (easy) — Cost calculator
#   Write cost_report(input_tokens, output_tokens) that prints the cost on all
#   four models side by side, plus how much cheaper or dearer each is than
#   Opus 5, as a percentage. Run it for a 10,000-in / 1,000-out request.
#
# EXERCISE 2 (medium) — Truncation detector
#   Write ask_safely(prompt, max_tokens) that calls the model and, if
#   stop_reason is "max_tokens", automatically retries once with double the
#   max_tokens. Print a message when it does.
#
# EXERCISE 3 (challenge - needs inheritance from lesson 17)
#   A conversation with a memory limit. Make a subclass of Conversation with a
#   `max_history` setting. When the message list is longer than that, drop
#   the OLDEST messages (a user message and its reply always go together) and
#   print roughly how many tokens that saved.
#
# EXERCISE 4 (medium) — Token budget guard
#   Write a function that takes a list of documents and returns as many as
#   will fit under a 20,000-token budget, using count_tokens. Report which
#   ones were dropped.
#
# EXERCISE 5 (medium) — Streaming with a progress counter
#   Stream a response while counting characters, and print a live "received
#   N chars" counter that stays on ONE line. (Start each print with "\r",
#   which jumps back to the start of the line, and use end="", flush=True.)
#
# EXERCISE 6 (medium) — Terminal chatbot
#   Build a loop: read input(), send it through a Conversation, print the
#   reply, show the running cost, and stop on "quit". Add a "/cost" command
#   that prints each turn's tokens and cost, like the table in PART 3.
#
# EXERCISE 7 (challenge) — Cost logger
#   Write logged_ask(bot, prompt) that calls bot.ask and also appends a row
#   to a CSV in workspace/ with the time, model, prompt length, input tokens,
#   output tokens and cost of that one call. Then read it back with lesson
#   14's csv module and total today's cost.
#
# EXERCISE 8 (medium) — Model comparison harness
#   Write compare_models(prompt) that sends the same prompt to two models and
#   prints both answers with their costs. (In simulated mode both answers will
#   match - the point is the harness, which you'll reuse in lesson 23 for real
#   evaluation.)
#
# EXERCISE 9 (easy) — Find the cache killer
#   Write two system prompts: one containing datetime.now(), one fixed. Print
#   both and explain which one can never be cached and why. Then fix the
#   broken one by moving the timestamp into the user message.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   cost = estimate_cost(2_000, 300, "claude-sonnet-5")
#   print(f"${cost:.4f}")                                    # -> $0.0070
#   # Printed without :.4f you'd see 0.006999999999999999 - computers store
#   # decimals slightly inexactly (lesson 03 PART 7), so format money to print it.
#
# WARM-UP B
#   response = client.messages.create(
#       model=MODEL,
#       max_tokens=1000,
#       messages=[{"role": "user", "content": "What is a tuple?"}],
#   )
#   print(extract_text(response))
#   print(response.stop_reason)                              # -> end_turn
#
# WARM-UP C
#   count = client.messages.count_tokens(
#       model=MODEL,
#       messages=[{"role": "user", "content": "Python is fun to learn."}],
#   )
#   print(count.input_tokens)
#
# EXERCISE 1
#   def cost_report(input_tokens, output_tokens):
#       baseline = estimate_cost(input_tokens, output_tokens, "claude-opus-5")
#       print(f"{'model':<20}{'cost':>12}{'vs Opus 5':>12}")
#       for name in MODELS:
#           cost = estimate_cost(input_tokens, output_tokens, name)
#           difference = (cost - baseline) / baseline      # e.g. -0.6 = 60% cheaper
#           print(f"{name:<20}${cost:>11.4f}{difference:>+11.0%}")
#   cost_report(10_000, 1_000)
#   # :+.0%  shows the number as a percentage with a + or - sign in front.
#
# EXERCISE 2
#   def ask_safely(prompt, max_tokens=200):
#       for attempt in range(2):                 # at most 2 tries
#           response = client.messages.create(
#               model=MODEL,
#               max_tokens=max_tokens,
#               messages=[{"role": "user", "content": prompt}],
#           )
#           if response.stop_reason != "max_tokens":
#               return extract_text(response)    # finished properly
#           print(f"    cut off at {max_tokens}, retrying at {max_tokens * 2}")
#           max_tokens = max_tokens * 2
#       return extract_text(response)            # give up, return what we got
#   print(ask_safely("What is a list comprehension?"))
#
# EXERCISE 3
#   class TrimmedConversation(Conversation):
#       def __init__(self, client, model=MODEL, system=None, max_history=6):
#           super().__init__(client, model, system)
#           self.max_history = max_history
#
#       def send(self, user_message, max_tokens=1000):
#           if len(self.messages) > self.max_history:
#               extra = len(self.messages) - self.max_history
#               if extra % 2 == 1:
#                   extra = extra + 1     # drop whole user+assistant pairs
#               removed = self.messages[:extra]
#               saved = estimate_tokens(json.dumps(str(removed)))
#               self.messages = self.messages[extra:]
#               print(f"    trimmed {extra} messages, ~{saved} tokens saved")
#           return super().send(user_message, max_tokens)
#
#   short_chat = TrimmedConversation(client, max_history=4)
#   for text in ["My name is Sidd.", "I like Python.", "I live in Pune.",
#                "What's my name?"]:
#       print(short_chat.send(text))
#   # Dropping from the FRONT in pairs keeps the list starting with a "user"
#   # message, which the API requires. Notice the last reply: the model no
#   # longer knows the name, because "My name is Sidd." was trimmed away.
#   # That is the price of trimming - it saves tokens AND forgets.
#
# EXERCISE 4
#   def fit_documents(documents, budget=20_000):
#       kept = []
#       dropped = []
#       used = 0
#       for doc in documents:
#           count = client.messages.count_tokens(
#               model=MODEL,
#               messages=[{"role": "user", "content": doc}],
#           )
#           tokens = count.input_tokens
#           if used + tokens <= budget:
#               kept.append(doc)
#               used += tokens
#           else:
#               dropped.append((doc[:30], tokens))
#       print(f"kept {len(kept)} docs using {used:,} tokens")
#       for preview, tokens in dropped:
#           print(f"  dropped {preview!r} ({tokens:,} tokens)")
#       return kept
#
#   docs = ["short note", "a" * 40_000, "b" * 50_000, "another short note"]
#   fit_documents(docs)
#   # "a" * 40_000 is ~10k tokens and fits; "b" * 50_000 would push past the
#   # budget, so it's dropped - but the short note after it still fits.
#
# EXERCISE 5
#   received = 0
#   with client.messages.stream(
#       model=MODEL,
#       max_tokens=1000,
#       messages=[{"role": "user", "content": "Write a haiku about debugging."}],
#   ) as stream:
#       for chunk in stream.text_stream:
#           received += len(chunk)
#           print(f"\r    received {received} chars", end="", flush=True)
#   print()          # finish the line when the stream is done
#
# EXERCISE 6
#   chat = Conversation(client, system="Be concise.")
#   while True:
#       try:
#           text = input("you > ").strip()
#       except (EOFError, KeyboardInterrupt):     # Ctrl+D / Ctrl+C
#           break
#       if text.lower() in ("quit", "exit"):
#           break
#       if text == "/cost":
#           for number, turn in enumerate(chat.turns, start=1):
#               print(f"  turn {number}: {turn['input']} in, "
#                     f"{turn['output']} out, ${turn['cost']:.6f}")
#           continue
#       if not text:
#           continue                              # ignore empty lines
#       print("AI  >", chat.send(text))
#       print(f"      (running cost ${chat.total_cost():.6f})")
#
# EXERCISE 7
#   import csv
#   from datetime import datetime
#
#   LOG = HERE / "workspace" / "llm_calls.csv"
#   LOG.parent.mkdir(exist_ok=True)
#
#   def logged_ask(bot, prompt, max_tokens=1000):
#       # Remember the totals BEFORE the call, so we can see what it added.
#       input_before = bot.input_tokens
#       output_before = bot.output_tokens
#       spend_before = bot.spend
#
#       reply = bot.ask(prompt, max_tokens=max_tokens)
#
#       is_new_file = not LOG.exists()
#       with open(LOG, "a", encoding="utf-8", newline="") as file:
#           writer = csv.writer(file)
#           if is_new_file:
#               writer.writerow(["ts", "model", "prompt_chars", "in", "out", "cost"])
#           writer.writerow([
#               datetime.now().isoformat(timespec="seconds"),
#               bot.model,
#               len(prompt),
#               bot.input_tokens - input_before,
#               bot.output_tokens - output_before,
#               round(bot.spend - spend_before, 6),
#           ])
#       return reply
#
#   logged_ask(bot, "What is a tuple?")
#   logged_ask(bot, "What is a set?")
#
#   today = datetime.now().date().isoformat()     # e.g. "2026-09-19"
#   total = 0.0
#   with open(LOG, encoding="utf-8", newline="") as file:
#       for row in csv.DictReader(file):
#           if row["ts"].startswith(today):
#               total += float(row["cost"])
#   print(f"today's logged cost: ${total:.6f}")
#
# EXERCISE 8
#   def compare_models(prompt, models=("claude-opus-5", "claude-sonnet-5")):
#       for name in models:
#           model_bot = ClaudeClient(client, model=name)
#           answer = model_bot.ask(prompt)
#           print(f"\n--- {name} (${model_bot.spend:.6f}) ---")
#           print(answer)
#   compare_models("Explain recursion in one sentence.")
#   # In lesson 23 you'll add a grader, turning this into a real eval.
#
# EXERCISE 9
#   from datetime import datetime
#   broken = f"You are an assistant. The time is {datetime.now()}."
#   fixed = "You are an assistant."
#   print("broken:", broken)
#   print("fixed :", fixed)
#   # `broken` is different on every single call (the time changes), so the
#   # start of the prompt never matches and cache_read_input_tokens stays 0
#   # forever. The timestamp belongs in the user message, AFTER the cached part:
#   #     system=[{"type": "text", "text": fixed,
#   #              "cache_control": {"type": "ephemeral"}}]
#   #     messages=[{"role": "user",
#   #                "content": f"[time: {datetime.now()}]\n{question}"}]


print("=" * 70)
print("Lesson 22 complete. Next: 23_ai_engineering_patterns.py")
print("=" * 70)

"""
===============================================================================
 LESSON 21 — HTTP AND WEB APIs
===============================================================================

Time: about 70 minutes.
Assumes: lessons 01-20 (especially 14 JSON and 12 error handling).

This is the prerequisite for everything AI. An LLM call IS an HTTP POST with a
JSON body, an API key header, retries and a streamed response. Learn the
plumbing here and lesson 22 becomes easy.


-------------------------------------------------------------------------------
 THEORY: WHAT HAPPENS WHEN SOFTWARE TALKS TO SOFTWARE
-------------------------------------------------------------------------------

An API (Application Programming Interface) is a website designed for programs
instead of people. You send a request, you get structured data back - usually
JSON (lesson 14), which becomes a Python dict.

A REQUEST has four parts:
  METHOD   GET (read), POST (create/send), PUT (replace), DELETE (remove)
  URL      https://api.example.com/v1/messages
  HEADERS  metadata: who you are (auth), what format you're sending
  BODY     the data you're sending (POST/PUT only), usually JSON

A RESPONSE has three:
  STATUS   a number saying what happened
  HEADERS  metadata about the reply (rate limits live here)
  BODY     the data, usually JSON

STATUS CODES - memorise the shape, not the list:
  2xx  success            200 OK, 201 Created
  4xx  YOU made a mistake 400 bad request, 401 no/bad key, 403 forbidden,
                          404 not found, 429 too many requests
  5xx  THEY have a problem 500 server error, 503 unavailable

That 4xx/5xx split drives your error handling: 4xx means fix your code, DON'T
retry. 5xx and 429 mean wait and try again.
"""

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

LINE = "-" * 70
HERE = Path(__file__).resolve().parent


# =============================================================================
# PART 1 — requests vs urllib
# =============================================================================
print(LINE)
print("PART 1 — THE TWO LIBRARIES")
print(LINE)

# `requests` is the standard third-party library and what you'll use in real
# projects:   python3 -m pip install requests
#
#     import requests
#     r = requests.get("https://api.example.com/items", timeout=10)
#     r.raise_for_status()
#     data = r.json()
#
# `urllib.request` is built in, so this lesson uses it - no install needed. The
# concepts are identical; requests is just friendlier.

print("  requests : r = requests.get(url); data = r.json()")
print("  urllib   : more verbose, but always available")
print()


# =============================================================================
# PART 2 — MAKING A REQUEST (offline-safe)
# =============================================================================
print(LINE)
print("PART 2 — A REAL REQUEST")
print(LINE)

def http_get_json(url, headers=None, timeout=10):
    """GET a URL and parse the JSON response. Raises on failure."""
    request = urllib.request.Request(url, headers=headers or {}, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def http_post_json(url, payload, headers=None, timeout=30):
    """POST a JSON body and parse the JSON response."""
    body = json.dumps(payload).encode("utf-8")       # dict -> bytes
    all_headers = {"Content-Type": "application/json", **(headers or {})}
    request = urllib.request.Request(url, data=body, headers=all_headers,
                                     method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


# ALWAYS set a timeout. Without one, a hung server freezes your program
# forever. This is the single most common production bug in API code.

# Try a real call, but don't fail the lesson if there's no network.
DEMO_URL = "https://httpbin.org/json"
try:
    data = http_get_json(DEMO_URL, timeout=5)
    print(f"  live call succeeded: got {len(json.dumps(data))} bytes of JSON")
    print(f"  top-level keys: {list(data)[:3]}")
    ONLINE = True
except Exception as error:
    print(f"  (no network - {type(error).__name__}; using offline examples)")
    ONLINE = False
print()


# =============================================================================
# PART 3 — ERROR HANDLING: THE 4xx / 5xx SPLIT
# =============================================================================
print(LINE)
print("PART 3 — HANDLING FAILURES")
print(LINE)

def call_api(url, payload=None, headers=None):
    """Call an API and turn HTTP failures into clear Python outcomes."""
    try:
        if payload is None:
            return {"ok": True, "data": http_get_json(url, headers)}
        return {"ok": True, "data": http_post_json(url, payload, headers)}

    except urllib.error.HTTPError as error:
        # The server replied, but with an error status.
        body = error.read().decode("utf-8", errors="replace")[:200]
        retryable = error.code == 429 or error.code >= 500
        return {"ok": False, "status": error.code, "retryable": retryable,
                "detail": body}

    except urllib.error.URLError as error:
        # Never reached the server: DNS failure, no network, timeout.
        return {"ok": False, "status": None, "retryable": True,
                "detail": str(error.reason)}

    except json.JSONDecodeError:
        # 200 OK but the body wasn't JSON - often an HTML error page.
        return {"ok": False, "status": 200, "retryable": False,
                "detail": "response was not JSON"}


print("  status -> what to do:")
for code, meaning, action in [
    (200, "OK", "use the data"),
    (400, "bad request", "fix your code - do NOT retry"),
    (401, "unauthorised", "check your API key - do NOT retry"),
    (404, "not found", "check the URL - do NOT retry"),
    (429, "rate limited", "wait (see Retry-After header) and retry"),
    (500, "server error", "retry with backoff"),
    (503, "unavailable", "retry with backoff"),
]:
    print(f"    {code}  {meaning:<14} {action}")
print()


# =============================================================================
# PART 4 — RETRIES WITH EXPONENTIAL BACKOFF
# =============================================================================
print(LINE)
print("PART 4 — RETRY LOGIC")
print(LINE)

# Networks fail intermittently. Retrying immediately makes things worse (you
# hammer a struggling server). EXPONENTIAL BACKOFF waits longer each time:
# 1s, 2s, 4s, 8s. JITTER (a small random extra) stops many clients retrying in
# lockstep - the "thundering herd" problem.

import random

def with_retry(operation, max_attempts=5, base_delay=1.0, logger=print):
    """Run `operation()`, retrying transient failures with backoff."""
    for attempt in range(1, max_attempts + 1):
        result = operation()

        if result["ok"]:
            return result
        if not result["retryable"]:
            logger(f"    permanent failure ({result['status']}) - not retrying")
            return result
        if attempt == max_attempts:
            logger(f"    gave up after {max_attempts} attempts")
            return result

        delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.3)
        logger(f"    attempt {attempt} failed ({result['status']}), "
               f"waiting {delay:.1f}s")
        time.sleep(min(delay, 0.05))       # shortened so the lesson runs fast
    return result


# Simulate a flaky endpoint: fails twice, then succeeds.
state = {"calls": 0}

def flaky_operation():
    state["calls"] += 1
    if state["calls"] < 3:
        return {"ok": False, "status": 503, "retryable": True, "detail": "busy"}
    return {"ok": True, "data": {"message": "success on attempt 3"}}

print("  retrying a flaky endpoint:")
result = with_retry(flaky_operation, logger=lambda m: print(m))
print(f"    result: {result['data']}")
print()

# EVERY serious API client has this logic. The Anthropic SDK in lesson 22 has
# it built in (`max_retries=2` by default), which is one good reason to use an
# official SDK rather than hand-rolling HTTP.


# =============================================================================
# PART 5 — AUTHENTICATION AND SECRETS
# =============================================================================
print(LINE)
print("PART 5 — API KEYS")
print(LINE)

# Most APIs identify you with a key sent in a header:
#     Authorization: Bearer sk-xxxx        (the common standard)
#     x-api-key: sk-xxxx                   (what the Anthropic API uses)
#
# ***** NEVER PUT A KEY IN YOUR SOURCE CODE *****
# Committed keys get scraped from GitHub within minutes and used to run up
# bills. Read them from the ENVIRONMENT instead:

import os

api_key = os.environ.get("ANTHROPIC_API_KEY")
print(f"  ANTHROPIC_API_KEY is {'set' if api_key else 'not set'}")

# How to set one, in your terminal:
#     export ANTHROPIC_API_KEY="sk-ant-..."        (Mac/Linux, this session)
# or put it in a .env file and load it with python-dotenv:
#     pip install python-dotenv
#     from dotenv import load_dotenv; load_dotenv()
#
# ALWAYS add .env to your .gitignore.

def require_key(name):
    """Fail loudly and helpfully if a required secret is missing."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set. Run:  export {name}='your-key-here'"
        )
    return value

print("  pattern: read from os.environ, never hard-code, .env in .gitignore")
print()


# =============================================================================
# PART 6 — RATE LIMITS
# =============================================================================
print(LINE)
print("PART 6 — RATE LIMITING")
print(LINE)

# APIs cap how often you may call them. Exceed it and you get 429. The response
# headers usually tell you your budget:
#     x-ratelimit-limit-requests, x-ratelimit-remaining-requests,
#     retry-after (seconds to wait)
#
# Being a good client means throttling yourself BEFORE you get blocked.

class RateLimiter:
    """Allow at most `calls_per_second` calls, sleeping when needed."""

    def __init__(self, calls_per_second=2.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0

    def wait(self):
        elapsed = time.monotonic() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.monotonic()


limiter = RateLimiter(calls_per_second=50)      # fast, so the lesson runs quickly
start = time.monotonic()
for n in range(5):
    limiter.wait()
print(f"  5 throttled calls took {time.monotonic() - start:.3f}s")
print("  in production: honour the `retry-after` header on a 429")
print()


# =============================================================================
# PART 7 — A COMPLETE API CLIENT CLASS
# =============================================================================
print(LINE)
print("PART 7 — WRAPPING IT ALL UP")
print(LINE)

# This is the shape of every API client you will ever write or read, including
# the Anthropic SDK you'll use in lesson 22.

class ApiClient:
    """A minimal, well-behaved HTTP JSON client."""

    def __init__(self, base_url, api_key=None, timeout=30,
                 max_attempts=3, calls_per_second=5.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.limiter = RateLimiter(calls_per_second)

    def _headers(self):
        headers = {"Content-Type": "application/json",
                   "User-Agent": "python-course/1.0"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def request(self, path, payload=None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        self.limiter.wait()
        return with_retry(
            lambda: call_api(url, payload, self._headers()),
            max_attempts=self.max_attempts,
            logger=lambda m: None,
        )

    def get(self, path):
        return self.request(path)

    def post(self, path, payload):
        return self.request(path, payload)


client = ApiClient("https://httpbin.org", api_key="demo-key")
print("  built a client with: base url, auth header, timeout, retries, throttle")

if ONLINE:
    result = client.get("/json")
    print(f"  live GET ok={result['ok']}")
    result = client.post("/post", {"hello": "world"})
    if result["ok"]:
        print(f"  live POST echoed back: {result['data'].get('json')}")
else:
    print("  (offline - skipping the live calls)")
print()


# =============================================================================
# PART 8 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 8 — COMMON MISTAKES")
print(LINE)
print("""  1. No timeout          -> your program hangs forever
  2. Retrying a 400/401  -> it will never succeed; you're just wasting time
  3. Not retrying 429/5xx-> transient blips become user-visible failures
  4. Hard-coded API keys -> scraped from git and abused
  5. Assuming JSON       -> wrap json.loads in try/except (it may be an HTML
                            error page)
  6. Ignoring rate limits-> you get blocked, sometimes permanently
  7. No backoff          -> you DDoS a server that was already struggling
  8. Logging the API key -> secrets end up in your log files""")
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# 1. Add a `delete()` method to ApiClient and a per-request timeout override.
# 2. Make with_retry honour a `retry_after` value in the result dict.
# 3. Write a function that fetches 10 URLs and reports which succeeded, which
#    failed permanently, and which were retried.
# 4. Install `requests` in a venv and rewrite http_get_json using it. Compare.
# 5. Add response caching to ApiClient: identical GETs within 60 seconds should
#    return the stored result instead of calling out again.
# 6. Read the `retry-after` header from a real 429 (httpbin.org/status/429).
# 7. Add a `log_request` hook that records method, url, status and duration -
#    without ever logging the Authorization header.


print("=" * 70)
print("Lesson 21 complete. Next: 22_claude_api.py")
print("=" * 70)

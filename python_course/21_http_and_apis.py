"""
===============================================================================
 LESSON 21 — HTTP AND WEB APIs
===============================================================================

Time: about 85 minutes.
Assumes: lessons 01-20 (especially 09 dictionaries, 12 errors, 14 JSON).

This is the prerequisite for everything AI. An LLM call IS an HTTP POST with a
JSON body, an API key header, retry logic and a streamed response. Learn the
plumbing here and lesson 22 becomes easy.

NOTE: this lesson starts a small PRACTICE API SERVER on your own machine, so
every example below makes a REAL HTTP request that works with no internet
connection. You get to see genuine status codes, headers, pagination, auth
failures and rate limits - not simulated ones.


-------------------------------------------------------------------------------
 THEORY: WHAT HAPPENS WHEN SOFTWARE TALKS TO SOFTWARE
-------------------------------------------------------------------------------

An API (Application Programming Interface) is a website designed for programs
instead of people. A human-facing website returns HTML for a browser to draw.
An API returns JSON (lesson 14) for your code to use - which, once parsed,
is just a Python dict.

That's the entire conceptual leap. Everything else is detail.

A REQUEST has four parts:

  METHOD   what you want to do
             GET    read something          (safe, repeatable)
             POST   create or send something (changes things)
             PUT    replace something
             PATCH  partially update something
             DELETE remove something
  URL      where to send it
  HEADERS  metadata: who you are, what format you're sending
  BODY     the data itself (POST/PUT/PATCH only), usually JSON

A RESPONSE has three:

  STATUS   a number saying what happened
  HEADERS  metadata about the reply - rate limits and pagination live here
  BODY     the data, usually JSON


-------------------------------------------------------------------------------
 STATUS CODES: LEARN THE SHAPE, NOT THE LIST
-------------------------------------------------------------------------------

  1xx  informational  (you'll rarely see these)
  2xx  SUCCESS        200 OK, 201 Created, 204 No Content
  3xx  redirect       301 moved, 304 not modified
  4xx  YOU made a mistake
         400 bad request      your JSON or parameters are wrong
         401 unauthorised     missing or invalid credentials
         403 forbidden        valid credentials, but not allowed
         404 not found        wrong URL, or the thing doesn't exist
         429 too many requests you're going too fast
  5xx  THEY have a problem
         500 internal error   their code crashed
         502 bad gateway      a server behind theirs failed
         503 unavailable      overloaded or in maintenance

THE SPLIT THAT DRIVES YOUR CODE:
  4xx (except 429) -> DO NOT RETRY. Retrying a 401 a thousand times will not
                      make your API key correct. Fix the code.
  429 and 5xx      -> DO RETRY, with increasing delays. These are temporary.

Almost every bug in beginner API code comes from ignoring that distinction.
"""

import json
import random
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

LINE = "-" * 70
HERE = Path(__file__).resolve().parent


# =============================================================================
# THE PRACTICE SERVER
# =============================================================================
# Everything below this block is a small fake API running on your own machine.
# You do NOT need to understand it yet - lesson 24 builds one properly. It's
# here so the rest of this lesson can make real requests offline.
#
# It offers:
#   GET  /api/items?page=1&per_page=3   a paginated list
#   GET  /api/items/<id>                one item, or 404
#   GET  /api/protected                 needs an Authorization header
#   GET  /api/flaky                     fails twice, then works
#   GET  /api/slow?seconds=2            deliberately slow
#   GET  /api/notjson                   returns HTML, to break your parser
#   GET  /api/status/<code>             returns any status you ask for
#   POST /api/items                     creates an item
# -----------------------------------------------------------------------------

_ITEMS = [
    {"id": n, "name": f"Widget {n}", "price": round(4.99 + n * 1.5, 2),
     "in_stock": n % 3 != 0}
    for n in range(1, 12)
]
_FLAKY_CALLS = {"count": 0}
_RATE_WINDOW = []
_VALID_TOKEN = "secret-token-123"


class PracticeAPI(BaseHTTPRequestHandler):

    def log_message(self, *args):
        pass                                  # keep the lesson output clean

    def _json(self, status, payload, extra_headers=None):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for key, value in (extra_headers or {}).items():
            self.send_header(key, str(value))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # --- rate limiting: 8 requests per 10 seconds ---
        now = time.monotonic()
        _RATE_WINDOW[:] = [t for t in _RATE_WINDOW if now - t < 10]
        if path.startswith("/api/limited"):
            if len(_RATE_WINDOW) >= 8:
                return self._json(429, {"error": "rate limit exceeded"},
                                  {"Retry-After": "10"})
            _RATE_WINDOW.append(now)
            return self._json(200, {"ok": True, "calls_in_window": len(_RATE_WINDOW)})

        if path == "/api/items":
            page = int(query.get("page", ["1"])[0])
            per_page = int(query.get("per_page", ["3"])[0])
            start = (page - 1) * per_page
            chunk = _ITEMS[start:start + per_page]
            total_pages = (len(_ITEMS) + per_page - 1) // per_page
            return self._json(200, {
                "items": chunk,
                "page": page,
                "per_page": per_page,
                "total": len(_ITEMS),
                "total_pages": total_pages,
                "has_next": page < total_pages,
            }, {"X-Total-Count": len(_ITEMS)})

        if path.startswith("/api/items/"):
            try:
                item_id = int(path.rsplit("/", 1)[1])
            except ValueError:
                return self._json(400, {"error": "id must be an integer"})
            for item in _ITEMS:
                if item["id"] == item_id:
                    return self._json(200, item)
            return self._json(404, {"error": f"no item with id {item_id}"})

        if path == "/api/protected":
            auth = self.headers.get("Authorization", "")
            if not auth:
                return self._json(401, {"error": "Authorization header required"})
            if auth != f"Bearer {_VALID_TOKEN}":
                return self._json(403, {"error": "invalid token"})
            return self._json(200, {"secret": "the cake is a lie", "user": "sidd"})

        if path == "/api/flaky":
            _FLAKY_CALLS["count"] += 1
            if _FLAKY_CALLS["count"] % 3 != 0:
                return self._json(503, {"error": "temporarily unavailable",
                                        "attempt": _FLAKY_CALLS["count"]})
            return self._json(200, {"ok": True, "attempt": _FLAKY_CALLS["count"]})

        if path == "/api/slow":
            time.sleep(float(query.get("seconds", ["2"])[0]))
            return self._json(200, {"ok": True, "slept": True})

        if path == "/api/notjson":
            body = b"<html><body><h1>500 Server Error</h1></body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)

        if path.startswith("/api/status/"):
            code = int(path.rsplit("/", 1)[1])
            return self._json(code, {"requested_status": code})

        return self._json(404, {"error": "no such endpoint", "path": path})

    def do_POST(self):
        if self.path != "/api/items":
            return self._json(404, {"error": "no such endpoint"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            return self._json(400, {"error": "body must be valid JSON"})

        if not isinstance(payload, dict) or not payload.get("name"):
            return self._json(400, {"error": "'name' is required"})

        new_item = {"id": len(_ITEMS) + 1, "name": payload["name"],
                    "price": payload.get("price", 0.0), "in_stock": True}
        _ITEMS.append(new_item)
        return self._json(201, new_item, {"Location": f"/api/items/{new_item['id']}"})


_server = HTTPServer(("127.0.0.1", 0), PracticeAPI)   # port 0 = pick a free one
BASE_URL = f"http://127.0.0.1:{_server.server_port}"
threading.Thread(target=_server.serve_forever, daemon=True).start()

print(LINE)
print(f"  practice API running at {BASE_URL}")
print("  every request below is real - no internet needed")
print(LINE)
print()


# =============================================================================
# PART 1 — THE ANATOMY OF A URL
# =============================================================================
print(LINE)
print("PART 1 — URLs AND QUERY PARAMETERS")
print(LINE)

example = "https://api.example.com:443/v1/orders/42?status=paid&limit=10#notes"
parsed = urllib.parse.urlparse(example)

print(f"  full URL : {example}")
print(f"    scheme : {parsed.scheme}      https or http")
print(f"    host   : {parsed.hostname}   which machine")
print(f"    port   : {parsed.port}         usually implied (80 http, 443 https)")
print(f"    path   : {parsed.path}   what resource")
print(f"    query  : {parsed.query}  extra options")
print(f"    fragment: {parsed.fragment}      browser-only, never sent to the server")
print()

# The query string is a mini key-value store. Parse it into a dict:
print("  parsed query:", urllib.parse.parse_qs(parsed.query))
print()

# ***** BUILD QUERY STRINGS WITH urlencode, NEVER BY GLUING STRINGS *****
# Values may contain spaces, &, = or non-English characters. urlencode escapes
# them correctly. Hand-built query strings are a classic source of bugs, and
# of injection vulnerabilities.
params = {"search": "blue widget & bolt", "page": 2, "sort": "price desc"}
print("  built safely:", urllib.parse.urlencode(params))
print("  (note: spaces became +, & became %26 - the server decodes them back)")
print()

# REST URL conventions you'll see everywhere:
print("  the pattern almost every API follows:")
for method, url, meaning in [
    ("GET", "/api/items", "list all items"),
    ("GET", "/api/items?page=2", "list, second page"),
    ("GET", "/api/items/42", "get item 42"),
    ("POST", "/api/items", "create a new item"),
    ("PUT", "/api/items/42", "replace item 42"),
    ("DELETE", "/api/items/42", "delete item 42"),
]:
    print(f"    {method:<7}{url:<26}{meaning}")
print()


# =============================================================================
# PART 2 — MAKING REQUESTS
# =============================================================================
print(LINE)
print("PART 2 — GET AND POST")
print(LINE)

# `requests` is the standard third-party library and what you'll use at work:
#     pip install requests
#     r = requests.get(url, timeout=10)
#     r.raise_for_status()
#     data = r.json()
#
# This lesson uses the built-in urllib so nothing needs installing. The
# concepts are identical - requests is just a friendlier wrapper.

def http_request(url, method="GET", payload=None, headers=None, timeout=10):
    """Make a request and return (status, headers, parsed_body).

    Raises urllib.error.HTTPError on 4xx/5xx - we handle that in PART 3.
    """
    data = None
    all_headers = dict(headers or {})
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")        # dict -> JSON -> bytes
        all_headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=all_headers,
                                     method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        return response.status, dict(response.headers), json.loads(raw)


# ***** ALWAYS SET A TIMEOUT *****
# Without one, a hung server freezes your program forever - no error, no exit,
# just a process sitting there until someone notices. This is the single most
# common production bug in API code.

status, headers, data = http_request(f"{BASE_URL}/api/items/3")
print(f"  GET /api/items/3")
print(f"    status : {status}")
print(f"    body   : {data}")
print(f"    a header: Content-Type = {headers.get('Content-Type')}")
print()

# POST - sending data
status, headers, created = http_request(
    f"{BASE_URL}/api/items", method="POST",
    payload={"name": "Sidd's Gadget", "price": 24.99},
)
print(f"  POST /api/items")
print(f"    status  : {status}   (201 Created, not 200 - it made something new)")
print(f"    created : {created}")
print(f"    Location: {headers.get('Location')}  <- where the new thing lives")
print()

# Read it back to prove it really was created:
_, _, fetched = http_request(f"{BASE_URL}{headers.get('Location')}")
print(f"  reading it back: {fetched}")
print()


# =============================================================================
# PART 3 — ERROR HANDLING: THE 4xx / 5xx SPLIT
# =============================================================================
print(LINE)
print("PART 3 — HANDLING FAILURES")
print(LINE)

def call_api(url, method="GET", payload=None, headers=None, timeout=10):
    """Call an API and turn every failure mode into a clear result dict.

    Never raises. The caller inspects `ok` and `retryable` and decides.
    """
    try:
        status, response_headers, body = http_request(url, method, payload,
                                                      headers, timeout)
        return {"ok": True, "status": status, "data": body,
                "headers": response_headers, "retryable": False}

    except urllib.error.HTTPError as error:
        # The server answered, but with an error status.
        raw = error.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = raw[:120]
        retry_after = error.headers.get("Retry-After")
        return {"ok": False, "status": error.code,
                "retryable": error.code == 429 or error.code >= 500,
                "retry_after": int(retry_after) if retry_after else None,
                "data": detail}

    except urllib.error.URLError as error:
        # We never reached the server: DNS failure, refused connection, timeout.
        return {"ok": False, "status": None, "retryable": True,
                "retry_after": None, "data": f"connection failed: {error.reason}"}

    except json.JSONDecodeError:
        # HTTP 200, but the body wasn't JSON - often an HTML error page.
        return {"ok": False, "status": 200, "retryable": False,
                "retry_after": None, "data": "response was not JSON"}

    except TimeoutError:
        return {"ok": False, "status": None, "retryable": True,
                "retry_after": None, "data": "timed out"}


print("  every failure mode, for real:\n")
for label, url in [
    ("success",            f"{BASE_URL}/api/items/1"),
    ("404 not found",      f"{BASE_URL}/api/items/999"),
    ("400 bad request",    f"{BASE_URL}/api/items/abc"),
    ("401 no credentials", f"{BASE_URL}/api/protected"),
    ("500 server error",   f"{BASE_URL}/api/status/500"),
    ("200 but not JSON",   f"{BASE_URL}/api/notjson"),
    ("connection refused", "http://127.0.0.1:9/nope"),
]:
    result = call_api(url, timeout=3)
    verdict = "RETRY" if result["retryable"] else "DO NOT RETRY"
    detail = str(result["data"])[:38]
    print(f"    {label:<20} status={str(result['status']):<5} "
          f"{verdict:<13} {detail}")
print()

print("""  Read that table again - it is the whole lesson in miniature.
  404, 400 and 401 are YOUR bugs: retrying changes nothing.
  500 and connection failures are transient: retrying is the correct response.""")
print()

# Timeouts - see one happen:
print("  calling /api/slow?seconds=2 with a 1-second timeout:")
result = call_api(f"{BASE_URL}/api/slow?seconds=2", timeout=1)
print(f"    -> {result['data']}, retryable={result['retryable']}")
print()


# =============================================================================
# PART 4 — RETRIES WITH EXPONENTIAL BACKOFF
# =============================================================================
print(LINE)
print("PART 4 — RETRY LOGIC")
print(LINE)

# Networks fail intermittently. Retrying instantly makes things worse: you
# hammer an already-struggling server.
#
# EXPONENTIAL BACKOFF waits longer each attempt: 1s, 2s, 4s, 8s...
# JITTER adds a small random amount, so that a thousand clients that all
# failed at the same moment don't all retry at the same moment. Without it you
# get a "thundering herd" that knocks the server over again the instant it
# recovers.

def with_retry(make_call, max_attempts=5, base_delay=0.05, logger=print):
    """Run make_call(), retrying transient failures with exponential backoff.

    `make_call` must be a zero-argument function returning a call_api() dict.
    """
    for attempt in range(1, max_attempts + 1):
        result = make_call()

        if result["ok"]:
            if attempt > 1:
                logger(f"      succeeded on attempt {attempt}")
            return result

        if not result["retryable"]:
            logger(f"      permanent failure ({result['status']}) - not retrying")
            return result

        if attempt == max_attempts:
            logger(f"      gave up after {max_attempts} attempts")
            return result

        # Honour the server's own instruction if it sent one.
        if result.get("retry_after"):
            delay = result["retry_after"]
            reason = "server asked us to wait"
        else:
            delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, base_delay)
            reason = "exponential backoff"

        logger(f"      attempt {attempt} failed ({result['status']}), "
               f"waiting {delay:.2f}s ({reason})")
        time.sleep(min(delay, 0.3))          # capped so the lesson runs quickly

    return result


print("  /api/flaky fails twice then succeeds. Watch the retries:\n")
result = with_retry(lambda: call_api(f"{BASE_URL}/api/flaky"),
                    logger=lambda m: print(m))
print(f"    final result: {result['data']}")
print()

print("  now a 404, which must NOT be retried:\n")
with_retry(lambda: call_api(f"{BASE_URL}/api/items/999"),
           logger=lambda m: print(m))
print()

print("""  This exact logic lives inside every serious API client. The Anthropic
  SDK you'll use in lesson 22 has it built in (max_retries=2 by default),
  which is a good reason to use an official SDK rather than hand-rolling HTTP.""")
print()


# =============================================================================
# PART 5 — AUTHENTICATION AND SECRETS
# =============================================================================
print(LINE)
print("PART 5 — API KEYS AND AUTH")
print(LINE)

# Most APIs identify you with a header:
#     Authorization: Bearer sk-xxxx       the common standard
#     x-api-key: sk-xxxx                  what the Anthropic API uses
#
# See all three outcomes for real:

print("  no header at all:")
result = call_api(f"{BASE_URL}/api/protected")
print(f"    {result['status']} {result['data']}")

print("\n  wrong token:")
result = call_api(f"{BASE_URL}/api/protected",
                  headers={"Authorization": "Bearer wrong-token"})
print(f"    {result['status']} {result['data']}")

print("\n  correct token:")
result = call_api(f"{BASE_URL}/api/protected",
                  headers={"Authorization": f"Bearer {_VALID_TOKEN}"})
print(f"    {result['status']} {result['data']}")
print()

print("""  401 vs 403 - a distinction worth knowing:
    401 UNAUTHORISED  "I don't know who you are"    -> supply credentials
    403 FORBIDDEN     "I know who you are, and no"  -> credentials are fine,
                                                       permissions are not""")
print()

# ***** NEVER PUT A KEY IN YOUR SOURCE CODE *****
import os

print("  reading secrets from the environment:")
print(f"    ANTHROPIC_API_KEY is {'set' if os.environ.get('ANTHROPIC_API_KEY') else 'not set'}")

def require_secret(name):
    """Fetch a required secret, failing loudly and helpfully if it's absent."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set.\n"
            f"  Run:  export {name}='your-key-here'\n"
            f"  Or put it in a .env file and load it with python-dotenv."
        )
    return value

try:
    require_secret("SOME_MISSING_KEY")
except RuntimeError as error:
    print(f"\n  a good error message looks like this:\n    {error}")

print("""
  WHY THIS MATTERS: bots scan every public GitHub commit for key patterns
  within minutes of you pushing. A leaked key gets used to run up a bill on
  your card. Rules:
    1. read keys from os.environ, never literals in code
    2. keep them in a .env file locally
    3. put .env in .gitignore BEFORE your first commit
    4. never print or log a key, even while debugging
    5. if you leak one, revoke it immediately - don't just delete the commit,
       because the history is already scraped""")
print()


# =============================================================================
# PART 6 — PAGINATION: GETTING MORE THAN ONE PAGE
# =============================================================================
print(LINE)
print("PART 6 — PAGINATION")
print(LINE)

# APIs never hand you 500,000 records in one response. They give you a page at
# a time and tell you how to ask for the next. If you only ever read page 1,
# you silently analyse 3% of the data and draw confident wrong conclusions.
# This is a genuinely common, genuinely serious beginner mistake.

print("  one page at a time:")
result = call_api(f"{BASE_URL}/api/items?page=1&per_page=3")
page = result["data"]
print(f"    page {page['page']} of {page['total_pages']}, "
      f"{len(page['items'])} of {page['total']} items")
for item in page["items"]:
    print(f"      {item['id']:>3} {item['name']:<12} {item['price']:>6.2f}")
print(f"    has_next: {page['has_next']}")
print()


def fetch_all_pages(base, per_page=3, max_pages=50):
    """Follow pagination until there's nothing left. Returns every item.

    The max_pages guard is not optional paranoia - a buggy API that always
    reports has_next=True will loop your program forever without it.
    """
    everything = []
    page_number = 1

    while page_number <= max_pages:
        result = call_api(f"{base}/api/items?page={page_number}&per_page={per_page}")
        if not result["ok"]:
            print(f"    page {page_number} failed: {result['data']}")
            break

        body = result["data"]
        everything.extend(body["items"])
        print(f"    fetched page {page_number}: {len(body['items'])} items "
              f"(running total {len(everything)})")

        if not body["has_next"]:
            break
        page_number += 1

    return everything


print("  fetching every page:")
all_items = fetch_all_pages(BASE_URL)
print(f"\n    collected {len(all_items)} items total")
print(f"    in stock: {sum(1 for i in all_items if i['in_stock'])}")
print(f"    total value: {sum(i['price'] for i in all_items):.2f}")
print()

print("""  THE THREE PAGINATION STYLES you'll meet:
    page numbers  ?page=2&per_page=50        simple, what we used here
    offset/limit  ?offset=100&limit=50       same idea, different words
    cursor        ?cursor=eyJpZCI6MTAwfQ     an opaque token from the last
                                             response; the most reliable for
                                             data that's changing as you read
  All three follow the same loop shape: fetch, collect, ask for more, stop
  when the API says there is no more.""")
print()


# =============================================================================
# PART 7 — RATE LIMITS
# =============================================================================
print(LINE)
print("PART 7 — RATE LIMITING")
print(LINE)

# APIs cap how often you may call them. Exceed the cap and you get 429, often
# with a Retry-After header telling you exactly how long to wait.
# A good client THROTTLES ITSELF rather than waiting to be blocked.

print("  /api/limited allows 8 requests per 10 seconds. Hammering it:\n")
for n in range(1, 11):
    result = call_api(f"{BASE_URL}/api/limited")
    if result["ok"]:
        print(f"    request {n:>2}: 200 OK  ({result['data']['calls_in_window']} used)")
    else:
        print(f"    request {n:>2}: {result['status']} BLOCKED - "
              f"Retry-After: {result['retry_after']}s")
print()


class RateLimiter:
    """Allow at most `calls_per_second`, sleeping when necessary."""

    def __init__(self, calls_per_second=2.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0

    def wait(self):
        elapsed = time.monotonic() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.monotonic()


limiter = RateLimiter(calls_per_second=40)      # fast, to keep the lesson brisk
start = time.monotonic()
for _ in range(5):
    limiter.wait()
print(f"  5 self-throttled calls took {time.monotonic() - start:.3f}s")
print("  (a real client would use something like 2-10 per second)")
print()

print("""  RATE LIMIT HEADERS to look for in responses:
    Retry-After                    seconds to wait - obey it exactly
    X-RateLimit-Limit              your total allowance
    X-RateLimit-Remaining          how much you have left
    X-RateLimit-Reset              when the allowance refills

  Read `Remaining` and slow down BEFORE you hit zero. Being throttled is
  normal; being banned for ignoring 429s is not.""")
print()


# =============================================================================
# PART 8 — A COMPLETE API CLIENT
# =============================================================================
print(LINE)
print("PART 8 — WRAPPING IT ALL UP")
print(LINE)

# This is the shape of every API client you will write or read - including the
# Anthropic SDK in lesson 22. Notice how little of it is about HTTP, and how
# much is about behaving well.

class ApiClient:
    """A well-behaved HTTP JSON client: auth, timeouts, retries, throttling."""

    def __init__(self, base_url, token=None, timeout=10,
                 max_attempts=3, calls_per_second=10.0):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.limiter = RateLimiter(calls_per_second)
        self.call_count = 0

    def _headers(self):
        headers = {"Accept": "application/json",
                   "User-Agent": "python-course/1.0"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, path, method="GET", payload=None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        self.limiter.wait()
        self.call_count += 1
        return with_retry(
            lambda: call_api(url, method, payload, self._headers(), self.timeout),
            max_attempts=self.max_attempts,
            logger=lambda message: None,          # silent by default
        )

    def get(self, path):
        return self._request(path)

    def post(self, path, payload):
        return self._request(path, "POST", payload)

    def get_all(self, path, per_page=3):
        """Paginate automatically - the caller never thinks about pages."""
        items, page = [], 1
        while page <= 50:
            result = self.get(f"{path}?page={page}&per_page={per_page}")
            if not result["ok"]:
                break
            items.extend(result["data"]["items"])
            if not result["data"]["has_next"]:
                break
            page += 1
        return items


client = ApiClient(BASE_URL, token=_VALID_TOKEN)

print("  client.get('/api/items/5'):")
print("   ", client.get("/api/items/5")["data"])

print("\n  client.get('/api/protected')  (token supplied automatically):")
print("   ", client.get("/api/protected")["data"])

print("\n  client.get_all('/api/items')  (pagination handled for you):")
everything = client.get_all("/api/items")
print(f"    got {len(everything)} items in {client.call_count} total requests")

print("\n  client.post('/api/items', {...}):")
print("   ", client.post("/api/items", {"name": "Final Widget", "price": 9.99})["data"])
print()


# =============================================================================
# PART 9 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 9 — COMMON MISTAKES")
print(LINE)
print("""   1. NO TIMEOUT. Your program hangs forever with no error. Always pass one.

   2. RETRYING A 4xx. A 401 will never become a 200 no matter how many times
      you ask. Check `retryable` before looping.

   3. NOT RETRYING 429/5xx. A one-second blip becomes a user-visible failure.

   4. NO BACKOFF. Instant retries turn a struggling server into a dead one,
      and get your IP blocked.

   5. HARD-CODED API KEYS. Scraped from git within minutes. os.environ.

   6. ASSUMING THE BODY IS JSON. Wrap json.loads in try/except - an error page
      or a proxy timeout will hand you HTML.

   7. ONLY READING PAGE 1. You analyse 3% of the data and never notice.
      Always check for has_next / next_cursor.

   8. IGNORING Retry-After. The server told you exactly how long to wait.
      Guessing is worse, and rude.

   9. LOGGING THE AUTHORIZATION HEADER. Your secrets end up in log files that
      are backed up, shipped to third parties and kept forever.

  10. BUILDING QUERY STRINGS BY CONCATENATION. Use urlencode - special
      characters will otherwise corrupt your request.

  11. TREATING HTTP ERRORS AS CRASHES. A 404 is often a normal, expected
      outcome ("that user doesn't exist"), not an exception-worthy disaster.""")
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# The practice server is still running while this file executes, so you can
# write code against BASE_URL in the space below.
#
# EXERCISE 1 — Explore the API
#   Fetch /api/items/1, /api/items/7 and /api/items/99. Print the status and
#   body of each. Explain to yourself why the third is different.
#
# EXERCISE 2 — Safe fetch
#   Write get_item(item_id) that returns the item dict, or None if it doesn't
#   exist, and raises RuntimeError for any other failure. Test it with ids
#   1, 99 and "abc".
#
# EXERCISE 3 — Add a DELETE method
#   Add `delete(path)` to ApiClient. The practice server doesn't implement
#   DELETE, so confirm you get a 404 and that your client handles it cleanly
#   rather than crashing.
#
# EXERCISE 4 — Per-request timeout
#   Give ApiClient._request an optional `timeout=None` parameter that
#   overrides the client default for one call. Test it against
#   /api/slow?seconds=2 with both a 1-second and a 3-second timeout.
#
# EXERCISE 5 — Response caching
#   Add a cache to ApiClient: identical GET paths requested within 60 seconds
#   should return the stored result without another HTTP call. Prove it works
#   by checking that call_count does not increase on the second request.
#
# EXERCISE 6 — Collect every item, safely
#   Write a function that fetches all items using per_page=2, counts how many
#   requests it needed, and reports the total value of in-stock items only.
#
# EXERCISE 7 — Respect the rate limit
#   Call /api/limited 15 times WITHOUT ever getting a 429, by using a
#   RateLimiter tuned below the server's 8-per-10-seconds allowance. Print how
#   long the whole run took.
#
# EXERCISE 8 — A request logger
#   Add a `log` list to ApiClient recording method, path, status and duration
#   in milliseconds for every call - but never the Authorization header. Print
#   the log as a table at the end, with a total-time row.
#
# EXERCISE 9 — Status code classifier
#   Write classify(status) returning one of "success", "redirect",
#   "client_error", "server_error", "unknown", plus a boolean saying whether
#   it's worth retrying. Test it against /api/status/200, 301, 404, 429, 500.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   for item_id in (1, 7, 99):
#       result = call_api(f"{BASE_URL}/api/items/{item_id}")
#       print(item_id, result["status"], result["data"])
#   # 99 returns 404 because the server only has ids 1-11. A 404 here is a
#   # normal answer to a reasonable question, not a bug.
#
# EXERCISE 2
#   def get_item(item_id):
#       result = call_api(f"{BASE_URL}/api/items/{item_id}")
#       if result["ok"]:
#           return result["data"]
#       if result["status"] == 404:
#           return None                      # "not found" is a valid answer
#       raise RuntimeError(f"lookup failed ({result['status']}): {result['data']}")
#   print(get_item(1))
#   print(get_item(99))                      # None
#   try:
#       get_item("abc")                      # 400 -> raises
#   except RuntimeError as error:
#       print("raised:", error)
#
# EXERCISE 3
#   # inside ApiClient:
#   def delete(self, path):
#       return self._request(path, "DELETE")
#   result = client.delete("/api/items/1")
#   print(result["status"], result["data"])   # 404, handled without crashing
#
# EXERCISE 4
#   def _request(self, path, method="GET", payload=None, timeout=None):
#       url = f"{self.base_url}/{path.lstrip('/')}"
#       self.limiter.wait()
#       self.call_count += 1
#       effective = timeout if timeout is not None else self.timeout
#       return with_retry(
#           lambda: call_api(url, method, payload, self._headers(), effective),
#           max_attempts=self.max_attempts, logger=lambda m: None)
#   # then:
#   print(client._request("/api/slow?seconds=2", timeout=1)["data"])   # timed out
#   print(client._request("/api/slow?seconds=2", timeout=3)["ok"])     # True
#
# EXERCISE 5
#   # in __init__:  self._cache = {}
#   def get(self, path, max_age=60):
#       now = time.monotonic()
#       hit = self._cache.get(path)
#       if hit and now - hit[0] < max_age:
#           return hit[1]
#       result = self._request(path)
#       if result["ok"]:
#           self._cache[path] = (now, result)
#       return result
#   before = client.call_count
#   client.get("/api/items/1"); client.get("/api/items/1")
#   print("extra HTTP calls:", client.call_count - before)      # 1, not 2
#
# EXERCISE 6
#   items, page, requests_made = [], 1, 0
#   while True:
#       result = call_api(f"{BASE_URL}/api/items?page={page}&per_page=2")
#       requests_made += 1
#       if not result["ok"]:
#           break
#       items.extend(result["data"]["items"])
#       if not result["data"]["has_next"]:
#           break
#       page += 1
#   in_stock = [i for i in items if i["in_stock"]]
#   print(f"{len(items)} items in {requests_made} requests")
#   print(f"in-stock value: {sum(i['price'] for i in in_stock):.2f}")
#
# EXERCISE 7
#   # The server allows 8 per 10 seconds = 0.8/second. Stay safely under it.
#   polite = RateLimiter(calls_per_second=0.7)
#   start = time.monotonic()
#   blocked = 0
#   for _ in range(15):
#       polite.wait()
#       if not call_api(f"{BASE_URL}/api/limited")["ok"]:
#           blocked += 1
#   print(f"15 calls, {blocked} blocked, took {time.monotonic() - start:.1f}s")
#   # Slower, but zero failures. In production that trade is almost always right.
#
# EXERCISE 8
#   # in __init__:  self.log = []
#   # in _request, around the with_retry call:
#   started = time.monotonic()
#   result = with_retry(...)
#   self.log.append({"method": method, "path": path,
#                    "status": result["status"],
#                    "ms": int((time.monotonic() - started) * 1000)})
#   # note: we log the PATH and STATUS, never self._headers()
#   print(f"{'method':<8}{'path':<28}{'status':>7}{'ms':>6}")
#   for row in client.log:
#       print(f"{row['method']:<8}{row['path']:<28}"
#             f"{str(row['status']):>7}{row['ms']:>6}")
#   print(f"{'TOTAL':<43}{sum(r['ms'] for r in client.log):>6}")
#
# EXERCISE 9
#   def classify(status):
#       if status is None:
#           return "unknown", True           # never reached the server
#       if 200 <= status < 300:
#           return "success", False
#       if 300 <= status < 400:
#           return "redirect", False
#       if 400 <= status < 500:
#           return "client_error", status == 429
#       if 500 <= status < 600:
#           return "server_error", True
#       return "unknown", False
#   for code in (200, 301, 404, 429, 500):
#       result = call_api(f"{BASE_URL}/api/status/{code}")
#       print(code, classify(result["status"]))


# Shut the practice server down so this script can exit cleanly.
_server.shutdown()

print("=" * 70)
print("Lesson 21 complete. Next: 22_claude_api.py")
print("=" * 70)

"""
===============================================================================
 FASTAPI COURSE - LESSON 07: DEPENDENCIES, ROUTERS AND MIDDLEWARE
===============================================================================

Time: about 85 minutes (there's a good place for a break halfway).
Assumes: lessons 00-06.

THREE WAYS TO RUN THIS FILE:

    python 07_routers_and_dependencies.py            the TOUR (read this first)
    python 07_routers_and_dependencies.py --serve    a REAL server at /docs
    python 07_routers_and_dependencies.py --check    grades your exercises


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. split an app into routers, the way real projects are laid out  (PART 1)
  2. write the same query parameters ONCE and share them            (PART 2)
  3. turn "find it or 404" into something routes get for free       (PART 3)
  4. ask "who is this?" (401) and "may they?" (403)                 (PART 4)
  5. open something, hand it over, and always close it              (PART 5)
  6. protect a whole group of routes with one line                  (PART 6)
  7. run code for EVERY request with middleware, and allow a
     browser frontend to call your API (CORS)                       (PART 7)
  8. swap a dependency for a fake one - the key to testing          (PART 8)

NEW WORDS - come back here whenever you forget one:

  dependency     a function whose RESULT your route asks for. FastAPI runs it
                 first and passes the result in.
  Depends(...)   how you ask for one:
                 client: Annotated[dict, Depends(get_current_client)]
  dependency     the whole idea above: "declare what you need, FastAPI
  injection      provides it". Nothing magic - it just calls your function.
  router         a mini-app holding one group of related routes (APIRouter)
  prefix         the start of every path on a router:  prefix="/notes"
  tags           the heading those routes appear under in /docs
  include_router plugging a router's routes into the app
  401            "I don't know who you are" - missing or wrong credentials
  403            "I know who you are, and you're not allowed"
  API key        a secret string a PROGRAM sends to identify itself, usually
                 in a header. Lesson 09 does logins for PEOPLE.
  yield          a dependency that sets something up, hands it over, and
  dependency     cleans up afterwards - even if the route crashed
  middleware     code that wraps EVERY request, including 404s and /docs
  call_next      inside middleware: "pass this on and give me the response"
  CORS           the browser rule about which websites may read your API's
                 responses. Only browsers enforce it.
  origin         a website's scheme + host + port: http://localhost:5173
  override       replacing a dependency with another one, usually in tests

PYTHON YOU NEED:
  * type aliases         Pagination = Annotated[PageParams, Depends(pagination)]
  * a function as a value    sorted(notes, key=note_id_of)   (lesson 04 PART 0e)
  * yield and try/finally    (lesson 02 PARTS 6 and 8)
  * async def / await        for middleware only  (lesson 02 PART 7)


-------------------------------------------------------------------------------
 THEORY: THE PROBLEM THIS LESSON SOLVES
-------------------------------------------------------------------------------

Look back at lesson 06. Every list route repeated the same skip/limit
parameters. Every single-item route started with get_task_or_404. And soon
(lesson 09) EVERY protected route will need to ask "who is making this
request, and are they allowed?" before doing anything else.

Copy-paste that into 40 routes and you have 40 places to forget a check.


DEPENDENCY INJECTION: "DECLARE WHAT YOU NEED, FASTAPI PROVIDES IT"
------------------------------------------------------------------
A dependency is an ordinary function. You write it once:

    def get_current_client(x_api_key: Annotated[str | None, Header()] = None):
        ...check the key, raise 401 if it's wrong...
        return client

and any route asks for its RESULT by adding one parameter:

    @notes_router.post("")
    def create_note(note: NoteCreate,
                    client: Annotated[dict, Depends(get_current_client)]):

Before running create_note, FastAPI calls get_current_client and passes
whatever it returned in as `client`. If the dependency RAISES an
HTTPException, the route never runs at all.

A dependency can ask for everything a route can - path, query, header and
body values - AND for other dependencies. Small checks build into bigger ones.


WHAT HAPPENS TO ONE REQUEST, IN ORDER
-------------------------------------
    request arrives
      -> MIDDLEWARE, first half     runs for EVERY request, even 404s   PART 7
      -> FastAPI finds the matching route
      -> DEPENDENCIES               only the ones this route asks for   PARTS 2-6
      -> your route function
      -> dependency CLEANUP         the code after `yield`              PART 5
      -> MIDDLEWARE, second half    can add headers to the response
    response leaves


ROUTERS: HOW A REAL APP IS SPLIT INTO FILES
-------------------------------------------
A real API has dozens of routes. An APIRouter is a mini-app holding one group
of related routes, and main.py plugs each group in. The usual layout:

    app/
      main.py              app = FastAPI();  app.include_router(notes.router)
      dependencies.py      pagination, get_current_client, require_admin
      routers/
        notes.py           router = APIRouter(prefix="/notes") + its routes
        reports.py
        admin.py

This lesson keeps everything in ONE file so it runs with one command, but
every PART is labelled with the file it would live in. Lesson 11, the
capstone, is a real multi-file project with exactly this shape.
"""

import time
import uuid
from itertools import count
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from course_tools import check, section, show, start


# =============================================================================
# PART 1 — THE APP AND ITS ROUTERS          would live in: main.py, routers/
# =============================================================================

app = FastAPI(
    title="Lesson 07 API",
    description="Dependencies, routers and middleware.",
    version="1.0.0",
)

# prefix: every route on this router starts with /notes, so
#     @notes_router.get("/{note_id}")   is really   GET /notes/{note_id}
#     @notes_router.get("")             is really   GET /notes
# tags: groups these routes under one heading in /docs.
notes_router = APIRouter(prefix="/notes", tags=["notes"])
reports_router = APIRouter(prefix="/reports", tags=["reports"])
# admin_router is created in PART 6, where router-wide dependencies are explained.

notes_db: dict[int, dict] = {
    1: {"id": 1, "title": "Shopping list", "body": "eggs, rice, coffee", "owner": "sidd"},
    2: {"id": 2, "title": "Sprint goals", "body": "ship the login page", "owner": "ana"},
    3: {"id": 3, "title": "Book ideas", "body": "a novel about a backend dev", "owner": "ana"},
    4: {"id": 4, "title": "Gym plan", "body": "legs on monday", "owner": "sidd"},
    5: {"id": 5, "title": "Recipe: dal", "body": "lentils, turmeric, cumin", "owner": "marco"},
}


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(default="", max_length=5000)


def note_id_of(note: dict) -> int:
    """Used as sorted(..., key=note_id_of) - lesson 04 PART 0e."""
    return note["id"]


# =============================================================================
# PART 2 — YOUR FIRST DEPENDENCY: PAGINATION     would live in: dependencies.py
# =============================================================================
#
# Every list endpoint needs skip and limit, with the same rules. Write the
# parameters ONCE, in a dependency, and return them bundled together.

class PageParams(BaseModel):
    skip: int
    limit: int


def pagination(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> PageParams:
    return PageParams(skip=skip, limit=limit)


# A type alias (lesson 06) that bundles the type AND the Depends. Routes now
# write `page: Pagination` - short, readable, and impossible to get subtly
# different in two places.
Pagination = Annotated[PageParams, Depends(pagination)]


@notes_router.get("")
def list_notes(page: Pagination):
    notes = sorted(notes_db.values(), key=note_id_of)
    return {"skip": page.skip, "limit": page.limit,
            "items": notes[page.skip:page.skip + page.limit]}


# The SAME dependency in a second route. Change the limit rule in pagination()
# and both routes change together.
# (Declared before /{note_id} - lesson 04's route order rule.)
@notes_router.get("/search")
def search_notes(q: Annotated[str, Query(min_length=1)], page: Pagination):
    needle = q.lower()
    matches = [n for n in notes_db.values()
               if needle in n["title"].lower() or needle in n["body"].lower()]
    return {"q": q, "total": len(matches),
            "items": matches[page.skip:page.skip + page.limit]}

# TRY IT NOW (2 minutes):
#   In pagination() above, change le=100 to le=5, and run the tour.
#   [BOTH routes now refuse limit=500 at 5. One edit, every list route
#   updated - that's the whole point of a dependency.] Change it back.


# =============================================================================
# PART 3 — DEPENDENCIES CAN READ THE PATH TOO    would live in: dependencies.py
# =============================================================================
#
# Lesson 06's get_task_or_404 was a helper you called by hand. As a
# dependency, it reads {note_id} from the URL by itself: its parameter is
# called note_id, and the route's path has {note_id} - so FastAPI fills it in.

def valid_note(note_id: Annotated[int, Path(ge=1)]) -> dict:
    note = notes_db.get(note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Note {note_id} not found")
    return note


ValidNote = Annotated[dict, Depends(valid_note)]


@notes_router.get("/{note_id}")
def get_note(note: ValidNote):
    return note           # if we got here, the note definitely exists


# =============================================================================
# PART 4 — DEPENDENCIES THAT USE DEPENDENCIES: WHO ARE YOU? MAY YOU?
#                                                 would live in: dependencies.py
# =============================================================================
#
# Two different failures, two different status codes:
#
#   401 Unauthorized   "I don't know who you are"  - no key, or a wrong key
#   403 Forbidden      "I know who you are, and you're not allowed"
#
# API keys are a real way for PROGRAMS to identify themselves to an API.
# Lesson 09 builds proper login for PEOPLE (passwords and tokens) - using
# exactly the same dependency shape you're about to see.

API_KEYS = {
    "key-sidd-admin": {"username": "sidd", "role": "admin"},
    "key-ana-editor": {"username": "ana", "role": "editor"},
    "key-marco-viewer": {"username": "marco", "role": "viewer"},
}


# Level 1: WHO is calling? Reads the X-Api-Key header (lesson 04 PART 5).
def get_current_client(x_api_key: Annotated[str | None, Header()] = None) -> dict:
    if x_api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Missing X-Api-Key header",
                            headers={"WWW-Authenticate": "ApiKey"})
    client = API_KEYS.get(x_api_key)
    if client is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid API key",
                            headers={"WWW-Authenticate": "ApiKey"})
    return client


CurrentClient = Annotated[dict, Depends(get_current_client)]


# Level 2: MAY they do this? Each one DEPENDS ON level 1 - so they never
# repeat the key checking, they just receive the client it produced.
def require_editor(client: CurrentClient) -> dict:
    if client["role"] not in ["editor", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Editors and admins only")
    return client


def require_admin(client: CurrentClient) -> dict:
    if client["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admins only")
    return client


# CACHING: if one request needs get_current_client in several places (say,
# the route AND require_editor both ask for it), FastAPI runs it ONCE and
# shares the result. Useful when a dependency does real work, like a database
# lookup.

@notes_router.post("", status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate,
                client: Annotated[dict, Depends(require_editor)]):
    new_id = max(notes_db, default=0) + 1     # max() of a dict = its biggest KEY
    record = {"id": new_id}
    record.update(note.model_dump())
    record["owner"] = client["username"]      # the SERVER decides the owner
    notes_db[new_id] = record
    return record


# The ORDER of parameters matters: FastAPI resolves dependencies in the order
# they're listed. Auth comes FIRST, so a stranger gets 401 - not a 404 that
# reveals which note ids exist.
@notes_router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(client: Annotated[dict, Depends(require_editor)], note: ValidNote):
    if client["role"] != "admin" and note["owner"] != client["username"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can only delete your own notes")
    notes_db.pop(note["id"])

# TRY IT NOW (3 minutes):
#   Swap the two parameters above, so `note: ValidNote` comes FIRST, and run
#   the tour. Look at "DELETE /notes/999 - no key, missing note".
#   [It becomes 404 instead of 401: a stranger with no key just learned
#   which note ids exist. Swap them back. Order is a security decision.]


# =============================================================================
# PART 5 — YIELD DEPENDENCIES: SET UP, HAND OVER, CLEAN UP
#                                                 would live in: dependencies.py
# =============================================================================
#
# Some things must be CLOSED after use: database sessions, files, network
# connections. A dependency that uses `yield` instead of `return` does it:
#
#     def get_connection():
#         conn = open_it()        # 1. runs BEFORE the route
#         try:
#             yield conn          # 2. the route runs here, using conn
#         finally:
#             conn.close()        # 3. runs AFTER the route - even if it raised
#
# This is lesson 02 part 8's `with` statement, spread across one request.
# `finally:` runs whether the code above it succeeded or raised an error.
# Lesson 08 uses exactly this shape to give each request a database session.

connection_log: list[str] = []
connection_numbers = count(start=1)


class FakeConnection:
    """Stands in for a real database connection, and records what happens."""

    def __init__(self, number: int):
        self.number = number
        self.is_open = True

    def run(self, query: str) -> str:
        if not self.is_open:
            raise RuntimeError("connection is closed")
        connection_log.append(f"connection {self.number} ran: {query}")
        return f"42 rows (from connection {self.number})"


def get_connection():
    connection = FakeConnection(next(connection_numbers))
    connection_log.append(f"connection {connection.number} OPENED")
    try:
        yield connection
    finally:
        connection.is_open = False
        connection_log.append(f"connection {connection.number} CLOSED")


Connection = Annotated[FakeConnection, Depends(get_connection)]


@reports_router.get("/daily")
def daily_report(connection: Connection):
    return {"report": "daily", "result": connection.run("SELECT count(*) FROM notes")}


@reports_router.get("/broken")
def broken_report(connection: Connection):
    connection.run("SELECT * FROM a_table_that_is_locked")
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Reporting database is busy - try again shortly")


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. Dependencies are the big idea: shared parameters,
#  shared lookups, shared checks, and guaranteed cleanup. After the break:
#  protecting a whole router, middleware, CORS, and overrides.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 6 — A DEPENDENCY ON A WHOLE ROUTER         would live in: routers/admin.py
# =============================================================================
#
# `dependencies=[Depends(require_admin)]` runs require_admin before EVERY route
# on this router. Add a new admin route next year and it's protected
# automatically - nobody has to remember.
#
# Use `dependencies=[...]` for checks whose RESULT the route doesn't need. If a
# route needs the admin's details, it can still ask for them as a parameter.

admin_router = APIRouter(prefix="/admin", tags=["admin"],
                         dependencies=[Depends(require_admin)])


@admin_router.get("/stats")
def admin_stats():
    return {"notes": len(notes_db), "api_clients": len(API_KEYS),
            "connection_log_lines": len(connection_log)}


@admin_router.get("/clients")
def list_clients():
    # never send the keys themselves - only who they belong to
    return [{"username": c["username"], "role": c["role"]} for c in API_KEYS.values()]


# =============================================================================
# PART 7 — MIDDLEWARE: CODE THAT WRAPS EVERY REQUEST    would live in: main.py
# =============================================================================
#
# A dependency runs for the routes that ASK for it. Middleware runs for EVERY
# request - including 404s, /docs, and routes you haven't written yet. Use it
# for things that are truly universal: timing, request ids, logging, CORS.
#
# `call_next(request)` passes the request on to the rest of the app and gives
# back the response. Code before it runs on the way IN, code after it on the
# way OUT. It must be `async def`, and `call_next` must be awaited (lesson 02
# part 7).

@app.middleware("http")
async def add_timing_and_request_id(request: Request, call_next):
    # Reuse the caller's request id if they sent one, so one id can follow a
    # request through several services. Otherwise, make a new random one.
    request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex[:12]
    started = time.perf_counter()

    response = await call_next(request)

    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Process-Time"] = f"{elapsed_ms:.2f}ms"
    response.headers["X-Request-Id"] = request_id
    return response


# CORS - the one piece of middleware almost every API needs.
#
# Browsers enforce a rule: JavaScript on http://localhost:5173 (say, your React
# frontend) may NOT read responses from http://127.0.0.1:8000 (your API) unless
# the API says that origin is allowed. Without this, the frontend shows
# "blocked by CORS policy" even though your API worked perfectly.
#
# CORS only affects BROWSERS. curl, Python scripts and mobile apps ignore it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# PART 8 — OVERRIDING A DEPENDENCY (the key to testing - lesson 10)
# =============================================================================
#
#     app.dependency_overrides[get_current_client] = fake_function
#
# From then on, anywhere get_current_client would run, fake_function runs
# instead. Tests use this to swap a real database for a test one, or to
# pretend to be an admin without a real key. The tour demonstrates it.
# Remove overrides with  app.dependency_overrides.clear()


# =============================================================================
# PART 9 — ASSEMBLE THE APP                               would live in: main.py
# =============================================================================
#
# include_router plugs a router's routes into the app, with the router's
# prefix, tags and dependencies applied. Include each router ONCE, after its
# routes are written. (Older FastAPI versions copied the routes at this exact
# moment, so a route added to the router later silently didn't exist.
# Including last works the same on every version.)

app.include_router(notes_router)
app.include_router(reports_router)
app.include_router(admin_router)


# =============================================================================
# COMMON MISTAKES
# =============================================================================
#
# 1. Depends(get_current_client())  - with () - passes the RESULT of calling
#    it once at startup, not the function. Always Depends(function_name).
#
# 2. Writing the prefix twice:
#        notes_router = APIRouter(prefix="/notes")
#        @notes_router.get("/notes/{note_id}")      # -> /notes/notes/{note_id}
#    The router adds the prefix. Route paths start AFTER it.
#
# 3. Forgetting app.include_router entirely - same symptom, every route 404s.
#
# 4. Putting the "find the item" dependency before the auth dependency.
#    Strangers learn which ids exist from 404 vs 401. PART 4, delete_note.
#
# 5. Cleanup code after `yield` without try/finally. If the route raises an
#    error, cleanup is skipped and connections leak.
#
# 6. Slow work in middleware. It runs for EVERY request - /docs included.
#
# 7. allow_origins=["*"] "just to make CORS go away". List the real frontend
#    origins instead - especially once logins and cookies are involved.


# =============================================================================
# Used by the EXERCISES - leave this here
# =============================================================================

books_db: dict[int, dict] = {
    1: {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    2: {"id": 2, "title": "The Pragmatic Programmer", "author": "Hunt and Thomas"},
    3: {"id": 3, "title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann"},
    4: {"id": 4, "title": "Refactoring", "author": "Martin Fowler"},
}


# =============================================================================
# YOUR EXERCISE CODE GOES HERE - above the tour, so FastAPI registers it
# =============================================================================




# =============================================================================
# THE TOUR — runs when you execute this file with no flags
# =============================================================================

def tour(client):
    section("PART 2: ONE PAGINATION DEPENDENCY, TWO ROUTES")
    show(client, "GET", "/notes?limit=2")
    show(client, "GET", "/notes/search?q=plan&limit=1",
         note="a different route, the same skip/limit rules")
    show(client, "GET", "/notes?limit=500", note="the dependency's rule, enforced")
    print("\n  Notice X-Process-Time and X-Request-Id on every response.")
    print("  Nothing in the routes adds them - that's the middleware in PART 7.")

    section("PART 3: A DEPENDENCY THAT READS THE PATH")
    show(client, "GET", "/notes/2")
    show(client, "GET", "/notes/99", note="valid_note raised 404 - get_note never ran")

    section("PART 4: WHO ARE YOU (401)? MAY YOU (403)?")
    new_note = {"title": "Standup notes", "body": "blocked on API review"}
    show(client, "POST", "/notes", note="no key at all", json=new_note)
    show(client, "POST", "/notes", note="a key that doesn't exist",
         headers={"X-Api-Key": "key-i-made-up"}, json=new_note)
    show(client, "POST", "/notes", note="a real key, but only a viewer",
         headers={"X-Api-Key": "key-marco-viewer"}, json=new_note)
    show(client, "POST", "/notes", note="an editor - allowed",
         headers={"X-Api-Key": "key-ana-editor"}, json=new_note)
    show(client, "DELETE", "/notes/1", note="ana is an editor, but note 1 is sidd's",
         headers={"X-Api-Key": "key-ana-editor"})
    show(client, "DELETE", "/notes/999", note="no key, missing note: auth runs FIRST")
    show(client, "DELETE", "/notes/3", note="ana deleting her own note",
         headers={"X-Api-Key": "key-ana-editor"})

    section("PART 5: YIELD DEPENDENCIES CLEAN UP - EVEN AFTER ERRORS")
    show(client, "GET", "/reports/daily")
    show(client, "GET", "/reports/broken", note="this route raises an error")
    print("\n  What get_connection recorded:")
    for line in connection_log:
        print(f"    {line}")
    print("\n  Connection 2 was CLOSED even though its route raised an error.")
    print("  That's the `finally:` doing its job.")

    section("PART 6: ONE DEPENDENCY PROTECTING A WHOLE ROUTER")
    show(client, "GET", "/admin/stats", note="an editor - blocked",
         headers={"X-Api-Key": "key-ana-editor"})
    show(client, "GET", "/admin/clients", note="an admin - allowed, on any admin route",
         headers={"X-Api-Key": "key-sidd-admin"})

    section("PART 7: MIDDLEWARE - request ids and CORS")
    show(client, "GET", "/does-not-exist",
         note="even a 404 gets the timing headers - middleware wraps EVERYTHING")
    show(client, "GET", "/notes/2", note="send your own request id, get the same one back",
         headers={"X-Request-Id": "trace-abc-123"})

    allowed = client.get("/notes/2", headers={"Origin": "http://localhost:5173"})
    blocked = client.get("/notes/2", headers={"Origin": "https://evil.example"})
    print("\n  CORS: the same request, sent from two different browser origins:")
    print("    Origin http://localhost:5173  -> access-control-allow-origin:",
          allowed.headers.get("access-control-allow-origin"))
    print("    Origin https://evil.example   -> access-control-allow-origin:",
          blocked.headers.get("access-control-allow-origin"))
    print("  No header means the browser hides the response from that page's code.")

    section("PART 8: OVERRIDING A DEPENDENCY")
    def pretend_to_be_an_admin():
        return {"username": "test-robot", "role": "admin"}

    app.dependency_overrides[get_current_client] = pretend_to_be_an_admin
    show(client, "GET", "/admin/stats",
         note="NO key - but the override pretends we're an admin")
    app.dependency_overrides.clear()
    show(client, "GET", "/admin/stats", note="override removed - back to normal")
    print("\n  require_admin depends on get_current_client, so replacing the")
    print("  bottom of the chain changed everything built on top of it.")

    section("PART 9: WHAT include_router PRODUCED")
    print("  Every route in the app, with the router prefixes applied.")
    print("  (Read from app.openapi() - the same description /docs is built from.)")
    for path, operations in app.openapi()["paths"].items():
        methods = ", ".join(method.upper() for method in operations)
        print(f"    {methods:<14} {path}")
    print("\n  Run --serve and open /docs: routes are grouped by their router's tags.")


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * A dependency is just a function. A route lists what it needs; FastAPI
#     runs those functions first and passes the results in.
#   * If a dependency raises, the route never runs - which is why auth checks
#     belong in dependencies, not in the route body.
#   * Dependencies can use other dependencies, so small checks (who are you?)
#     build into bigger ones (may you edit?) without repeating anything.
#   * A dependency with `yield` sets up, hands over, and cleans up in a
#     `finally:` - even when the route raises. Lesson 08 uses this for
#     database sessions.
#   * A router groups related routes under a prefix and tag; include_router
#     plugs it into the app. dependencies=[...] on a router protects every
#     route in it, including ones added later.
#   * Middleware wraps EVERY request - use it for timing, request ids, CORS.
#   * The ORDER of parameters decides which error a stranger sees. Auth first.
#   * dependency_overrides swaps a dependency for a fake one - how lesson 10
#     tests routes without real keys or a real database.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. Why Depends(get_current_client) and not Depends(get_current_client())?
#   Q2. A route needs a pagination rule changed. How many places do you edit?
#   Q3. A dependency raises 401. Does the route function still run?
#   Q4. Why does cleanup code go after `yield` inside `finally:`?
#   Q5. When would you use middleware instead of a dependency?
#
# ANSWERS
#   A1. Depends needs the FUNCTION. With brackets you'd call it once at
#       startup and hand over its return value forever.
#   A2. One - the dependency. Every route using it changes together.
#   A3. No. The request stops there and the client gets the 401.
#   A4. So it runs whether the route succeeded or raised - otherwise a crash
#       leaks the connection.
#   A5. When it must happen for EVERY request, even 404s and /docs: timing,
#       request ids, CORS.


# =============================================================================
# EXERCISES
# =============================================================================
#
# Write your code in the "YOUR EXERCISE CODE GOES HERE" space above the tour,
# then run:
#     python 07_routers_and_dependencies.py --check
#
# The books_db dict just above that space is your data. The API keys from
# PART 4 still work: key-sidd-admin, key-ana-editor, key-marco-viewer.
#
# Do the WARM-UPS first - each REUSES something the lesson already built.
#
# WARM-UP 1 (easy) — Reuse the pagination dependency
#   Add GET /titles that returns a plain list of note TITLES (just the text),
#   using  page: Pagination  for skip and limit.
#
# WARM-UP 2 (easy) — Reuse the "who are you?" dependency
#   Add GET /whoami that uses  client: CurrentClient  and returns
#   {"username": ..., "role": ...} for whoever sent the API key. No key
#   should give 401 without you writing any checking code.
#
# EXERCISE 1 (medium) — A router with pagination
#   Create books_router with prefix "/books" and tag "books". Add GET /books,
#   returning a plain LIST of books sorted by id, using the Pagination
#   dependency from PART 2. Then include the router in the app - once, after
#   all its routes (including the ones from exercises 2 and 3).
#
# EXERCISE 2 (medium) — A "valid item" dependency
#   Write valid_book(book_id) that returns the book or raises 404 with the
#   exact detail "Book not found". Use it in GET /books/{book_id}.
#
# EXERCISE 3 (challenge) — Combine dependencies
#   Add DELETE /books/{book_id} -> 204. Only admins may delete (reuse
#   require_admin), and a missing book is a 404 (reuse valid_book).
#   A request with no key must get 401 even for a book that doesn't exist.
#
# EXERCISE 4 (medium) — A dependency that reads a header
#   Write get_language(), reading the Accept-Language header:
#       starts with "hi"  -> "hi"
#       starts with "es"  -> "es"
#       anything else, or no header -> "en"
#   Add GET /greeting returning {"language": ..., "greeting": ...} where the
#   greeting is "Hello" (en), "Namaste" (hi) or "Hola" (es).
#
# EXERCISE 5 (easy) — Middleware
#   Add middleware that puts the header  X-Lesson: 07  on EVERY response,
#   including 404s for paths that don't exist.


def checks(client):
    check("the lesson's own GET /notes still works", client.get("/notes").status_code == 200)

    # --- WARM-UP 1 ---
    r = client.get("/titles?limit=2")
    titles = r.json() if r.status_code == 200 else None
    check("WARM-UP 1: GET /titles?limit=2 returns a list of 2 titles",
          isinstance(titles, list) and len(titles) == 2)
    check("WARM-UP 1: they are titles (text), not whole notes",
          isinstance(titles, list) and titles and isinstance(titles[0], str))
    check("WARM-UP 1: ?limit=0 gives 422, from the shared dependency",
          client.get("/titles?limit=0").status_code == 422)

    # --- WARM-UP 2 ---
    check("WARM-UP 2: GET /whoami with no key gives 401",
          client.get("/whoami").status_code == 401)
    r = client.get("/whoami", headers={"X-Api-Key": "key-ana-editor"})
    check("WARM-UP 2: with ana's key it returns her username and role",
          r.status_code == 200 and r.json().get("username") == "ana"
          and r.json().get("role") == "editor")

    # --- EXERCISE 1 ---
    r = client.get("/books")
    books = r.json() if r.status_code == 200 else None
    check("EXERCISE 1: GET /books returns a list of all 4 books",
          isinstance(books, list) and len(books) == 4)
    r = client.get("/books?skip=1&limit=2")
    books = r.json() if r.status_code == 200 else None
    check("EXERCISE 1: ?skip=1&limit=2 returns books 2 and 3",
          isinstance(books, list) and [b.get("id") for b in books] == [2, 3])
    check("EXERCISE 1: ?limit=0 gives 422 (the Pagination rules)",
          client.get("/books?limit=0").status_code == 422)

    # --- EXERCISE 2 ---
    r = client.get("/books/3")
    check("EXERCISE 2: GET /books/3 returns that book",
          r.status_code == 200 and r.json().get("author") == "Martin Kleppmann")
    r = client.get("/books/99")
    check("EXERCISE 2: GET /books/99 gives 404 'Book not found'",
          r.status_code == 404 and r.json().get("detail") == "Book not found")

    # --- EXERCISE 3 ---
    check("EXERCISE 3: DELETE with no key gives 401",
          client.delete("/books/2").status_code == 401)
    check("EXERCISE 3: DELETE of a MISSING book with no key still gives 401",
          client.delete("/books/99").status_code == 401)
    check("EXERCISE 3: DELETE as an editor gives 403",
          client.delete("/books/2", headers={"X-Api-Key": "key-ana-editor"}).status_code == 403)
    r = client.delete("/books/2", headers={"X-Api-Key": "key-sidd-admin"})
    check("EXERCISE 3: DELETE as an admin gives 204", r.status_code == 204)
    check("EXERCISE 3: ...and the book is gone",
          r.status_code == 204 and client.get("/books/2").status_code == 404)
    r = client.delete("/books/99", headers={"X-Api-Key": "key-sidd-admin"})
    check("EXERCISE 3: an admin deleting a missing book gives 404 'Book not found'",
          r.status_code == 404 and r.json().get("detail") == "Book not found")

    # --- EXERCISE 4 ---
    expected = [("hi-IN,hi;q=0.9", "hi", "Namaste"), ("es-ES", "es", "Hola"),
                ("fr-FR", "en", "Hello")]
    for header, language, greeting in expected:
        r = client.get("/greeting", headers={"Accept-Language": header})
        check(f"EXERCISE 4: Accept-Language {header} -> {greeting}",
              r.status_code == 200
              and r.json() == {"language": language, "greeting": greeting})
    r = client.get("/greeting")
    check("EXERCISE 4: no header -> Hello",
          r.status_code == 200 and r.json().get("greeting") == "Hello")

    # --- EXERCISE 5 ---
    check("EXERCISE 5: X-Lesson: 07 is on a normal response",
          client.get("/notes").headers.get("x-lesson") == "07")
    check("EXERCISE 5: X-Lesson: 07 is on a 404 too",
          client.get("/this-path-does-not-exist").headers.get("x-lesson") == "07")


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP 1
#   @app.get("/titles")
#   def list_titles(page: Pagination):
#       notes = sorted(notes_db.values(), key=note_id_of)
#       titles = []
#       for note in notes[page.skip:page.skip + page.limit]:
#           titles.append(note["title"])
#       return titles
#
# WARM-UP 2
#   @app.get("/whoami")
#   def whoami(client: CurrentClient):
#       return {"username": client["username"], "role": client["role"]}
#
#   No `if` anywhere: the 401 comes from get_current_client, which runs first.
#
# EXERCISES 1, 2 AND 3
#   books_router = APIRouter(prefix="/books", tags=["books"])
#
#   def valid_book(book_id: int) -> dict:
#       book = books_db.get(book_id)
#       if book is None:
#           raise HTTPException(status_code=404, detail="Book not found")
#       return book
#
#   ValidBook = Annotated[dict, Depends(valid_book)]
#
#   def book_id_of(book: dict) -> int:
#       return book["id"]
#
#   @books_router.get("")
#   def list_books(page: Pagination):
#       books = sorted(books_db.values(), key=book_id_of)
#       return books[page.skip:page.skip + page.limit]
#
#   @books_router.get("/{book_id}")
#   def get_book(book: ValidBook):
#       return book
#
#   @books_router.delete("/{book_id}", status_code=204)
#   def delete_book(admin: Annotated[dict, Depends(require_admin)], book: ValidBook):
#       books_db.pop(book["id"])
#
#   app.include_router(books_router)       # once, after all three routes
#
#   In delete_book, `admin` comes before `book` - that's what makes a missing
#   book with no key a 401 rather than a 404.
#
# EXERCISE 4
#   GREETINGS = {"en": "Hello", "hi": "Namaste", "es": "Hola"}
#
#   def get_language(accept_language: Annotated[str, Header()] = "en") -> str:
#       for code in ["hi", "es"]:
#           if accept_language.lower().startswith(code):
#               return code
#       return "en"
#
#   @app.get("/greeting")
#   def greeting(language: Annotated[str, Depends(get_language)]):
#       return {"language": language, "greeting": GREETINGS[language]}
#
# EXERCISE 5
#   @app.middleware("http")
#   async def add_lesson_header(request: Request, call_next):
#       response = await call_next(request)
#       response.headers["X-Lesson"] = "07"
#       return response


if __name__ == "__main__":
    start(app, tour, checks)


print("\nNext: python 08_databases.py")

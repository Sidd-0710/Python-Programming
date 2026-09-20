"""
===============================================================================
 FASTAPI COURSE - LESSON 03: YOUR FIRST API
===============================================================================

Time: about 55 minutes.
Assumes: lessons 00-02.

THREE WAYS TO RUN THIS FILE - try all three, in this order:

    python 03_first_api.py            the TOUR (read this first)
    python 03_first_api.py --serve    a REAL server you click around in
    python 03_first_api.py --check    grades your exercise answers


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. create a FastAPI app                                   (STEP 1 below)
  2. write a route: a function that answers one URL         (YOUR FIRST ROUTE)
  3. return a dict or a list, and have it become JSON       (YOUR FIRST ROUTE)
  4. take a value out of the URL, like /users/2             (PATH PARAMETERS)
  5. let FastAPI reject bad input for you, with a 422       (PATH PARAMETERS)
  6. know when to write `async def` instead of `def`        (async def vs def)
  7. use the documentation page FastAPI builds for you      (--serve)

NEW WORDS - come back here whenever you forget one:

  app            the one object that represents your whole API:
                 app = FastAPI()
  route          one URL + method your API answers, e.g. GET /users
  endpoint       another word for route
  route          the @app.get("/users") line above a function, which tells
  decorator      FastAPI "call this function for GET /users" (lesson 02 PART 4)
  path parameter a value taken from inside the URL. In /users/2, the 2.
                 Written in the path as  /users/{user_id}
  422            the status code FastAPI sends when input is the wrong shape,
                 e.g. /users/abc when your code asked for an int
  /docs          a documentation page FastAPI builds automatically from your
                 code. You can send real requests from it.
  TestClient     what the tour uses to send requests to your API without
                 starting a real server

PYTHON YOU NEED FOR THIS LESSON - all from lessons 01 and 02:
  * a dict          {"message": "hi"}          becomes a JSON object
  * a list of dicts fake_users_db              becomes a JSON array
  * def             an ordinary function
  * a type hint     user_id: int               THE important one - FastAPI
                    uses it to convert and check the value
  * a decorator     @app.get("/users")
  * find-by-id      the loop from lesson 01 PART 7


-------------------------------------------------------------------------------
 THEORY: THE FOUR PIECES OF EVERY FASTAPI FILE
-------------------------------------------------------------------------------

Every FastAPI application, no matter how big, is built from four ideas you
already have the vocabulary for:

  1. CREATE THE APP           app = FastAPI()
                               one object representing your whole API

  2. WRITE A FUNCTION          def get_users(): ...
                               ordinary Python - lesson 01/02 material

  3. DECORATE IT WITH A ROUTE  @app.get("/users")
                               "register this function to answer GET /users"
                               (lesson 02 part 4 - decorators)

  4. RETURN DATA                return {"id": 1, "name": "Sidd"}
                               a dict, list, or Pydantic model (lesson 05).
                               FastAPI turns it into a JSON response for you.

That's the entire mental model. Everything else in this course is refinement:
better validation, a real database, login, tests. The shape never changes.

WHO CALLS YOUR FUNCTION? Not you. You never write get_users() anywhere.
FastAPI calls it, when a matching request arrives. Your job is to write the
function and label it with the right route.
"""

import asyncio

from fastapi import FastAPI

from course_tools import check, section, show, start

# STEP 1: create the app. One instance represents your whole API.
# The title/description show up in the automatic documentation (try --serve).
app = FastAPI(
    title="Lesson 03 API",
    description="Your first FastAPI application.",
    version="1.0.0",
)

# A pretend database - the same shape as lesson 01 PART 5. Lesson 08 replaces
# this with a real one; every ROUTE below stays almost identical when it does.
fake_users_db = [
    {"id": 1, "name": "Sidd", "role": "admin"},
    {"id": 2, "name": "Ana", "role": "editor"},
    {"id": 3, "name": "Marco", "role": "viewer"},
]


# =============================================================================
# YOUR FIRST ROUTE
# =============================================================================

# STEP 3: @app.get("/") registers this function for  GET /
# STEP 2: an ordinary function, just like lesson 01 and 02
@app.get("/")
def read_root():
    # STEP 4: return a dict. FastAPI converts it to JSON automatically.
    return {"message": "Welcome to the API", "docs": "/docs"}

# In plain English, those three lines say: "when someone sends GET / , run
# this function, and send whatever it returns back as JSON."


# A SECOND route. Notice the shape is identical - only the path and the
# body differ. This is the pattern you'll repeat for your entire career.
@app.get("/ping")
def ping():
    return {"status": "ok"}


# A route returning a LIST instead of a dict - just as easy.
# A list of dicts becomes a JSON array of objects (lesson 00 section 6).
@app.get("/users")
def list_users():
    return fake_users_db


# TRY IT NOW (2 minutes):
#   Copy the /ping route above, change BOTH the path and the function name to
#   something of your own - say /hi and def hi() - and return a dict with your
#   name in it. Run  python 03_first_api.py --serve  and open
#   http://127.0.0.1:8000/hi in your browser.
#   [You'll see your dict as JSON. Two names must change: if you copy the
#   route but not the function name, the second one quietly replaces the
#   first, and only the last route with that name works.]


# =============================================================================
# PATH PARAMETERS: VALUES INSIDE THE URL
# =============================================================================

# {user_id} in the path is a PLACEHOLDER. FastAPI captures whatever's there
# and hands it to your function as the argument of the SAME name.
#
#     @app.get("/users/{user_id}")      the name in the path...
#     def get_user(user_id: int):       ...must match the name here
#
# THE PART THAT MATTERS MOST: `user_id: int`. Because of that type hint,
# FastAPI:
#   * converts the text from the URL into a real Python int
#     (remember lesson 01: everything in a URL arrives as TEXT)
#   * automatically rejects anything that ISN'T a valid whole number, with a
#     clear 422 error, WITHOUT you writing a single line of checking code
# Lesson 02 part 2 was this exact mechanism - FastAPI is what enforces the hint.
@app.get("/users/{user_id}")
def get_user(user_id: int):
    # the same find-by-id loop from lesson 01 part 7
    for user in fake_users_db:
        if user["id"] == user_id:
            return user
    return {"error": "not found"}          # lesson 06 fixes this properly

# Note the weakness in that last line: it sends "not found" with the status
# code 200 OK, which lesson 00 section 5 warned about. Lesson 06 replaces it
# with a real 404. For today, notice the problem - don't fix it yet.


# =============================================================================
# async def vs def: THE ONE-PARAGRAPH RULE
# =============================================================================
#
# Write `async def` when your function AWAITS something (an async database
# call, another API, lesson 08/09's tools). Write plain `def` when it
# doesn't. FastAPI handles both correctly either way - so when unsure, `def`
# is always safe. This route has nothing to await, so it's a plain def:

@app.get("/slow-sync")
def slow_sync():
    return {"note": "a plain def route - completely normal and correct"}


# This one exists purely to show async syntax working inside a real route.
# (Lesson 02 part 7 explained what await actually does.)
@app.get("/slow-async")
async def slow_async():
    await asyncio.sleep(0.05)
    return {"note": "an async def route - also completely normal"}


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * app = FastAPI() creates your API. Every route is registered on it.
#   * A route is two lines: a @app.get("/path") decorator, and an ordinary
#     function under it. You never call that function yourself.
#   * Whatever you return becomes JSON: a dict becomes a JSON object, a list
#     of dicts becomes a JSON array.
#   * {user_id} in the path passes that part of the URL into the parameter of
#     the same name.
#   * The type hint  user_id: int  makes FastAPI convert the text to a number
#     and answer 422 automatically if it isn't one. That is the single
#     biggest reason FastAPI needs so little code.
#   * Use `async def` only when the function awaits something; plain `def` is
#     always safe.
#   * /docs is built for you, from your own code, with no extra work.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. Who calls the function under @app.get("/users")?
#   Q2. You return a Python list of dicts. What does the client receive?
#   Q3. Someone requests /users/abc and your hint says user_id: int. What
#       happens, and how much code did you write to make it happen?
#   Q4. What must match between @app.get("/users/{user_id}") and the line
#       under it?
#   Q5. Should a route that only reads from a list be async def?
#
# ANSWERS
#   A1. FastAPI does, when a matching request arrives.
#   A2. A JSON array of objects.
#   A3. FastAPI replies 422 before your function runs. You wrote no checking
#       code at all - just the type hint.
#   A4. The name: {user_id} in the path and user_id in the parameters.
#   A5. No - there's nothing to await, so plain def is correct.


# =============================================================================
# EXERCISES
# =============================================================================
#
# Add your routes ABOVE the `tour` function (new routes must be registered on
# `app` before the file runs), then run:
#     python 03_first_api.py --check
#
# Do the WARM-UPS first - each is one route, and each practises ONE idea.
#
# WARM-UP 1 (easy) — A health route
#   Add GET /health returning {"status": "healthy"}.
#
# WARM-UP 2 (easy) — Count the users
#   Add GET /count returning {"users": 3} - but work the 3 out with
#   len(fake_users_db) rather than typing it.
#
# EXERCISE 1 (easy) — A welcome route
#   Add GET /hello returning {"message": "Hello from FastAPI"}.
#
# EXERCISE 2 (easy) — A products list
#   Create fake_products_db, a list of 3 dicts each with id, name, price.
#   Add GET /products returning the whole list.
#
# EXERCISE 3 (medium) — A path parameter
#   Add GET /products/{product_id} using the find-by-id loop. If not found,
#   return {"error": "not found"} for now (lesson 06 makes this a real 404).
#
# EXERCISE 4 (medium) — Two path parameters
#   Add GET /users/{user_id}/role returning just {"role": "..."} for that
#   user (or {"error": "not found"}).
#
# EXERCISE 5 (easy) — Explore the docs yourself
#   Run --serve, open /docs, and find a route you didn't write any tour code
#   for. Click "Try it out" and send a request with an invalid user_id like
#   "abc". Read the 422 response body FastAPI generated with no help from you.

# --- add your new @app routes above the `tour` function, then write ------
# --- any of your own test code below this line --------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# THE TOUR — runs when you execute this file with no flags
# =============================================================================

def tour(client):
    section("ROUTE 1: GET /")
    show(client, "GET", "/", note="the root path - often used for a welcome message")

    section("ROUTE 2: GET /ping")
    show(client, "GET", "/ping", note="a tiny route, common for health checks")

    section("ROUTE 3: GET /users - a list")
    show(client, "GET", "/users", note="returns the whole fake database as JSON")

    section("ROUTE 4: GET /users/{user_id} - a path parameter")
    show(client, "GET", "/users/2", note="2 becomes a real Python int: user_id")
    show(client, "GET", "/users/999", note="a valid int, but no such user")
    show(client, "GET", "/users/abc",
         note="NOT a valid int - watch FastAPI reject this automatically")

    section("async def vs def - both work the same way from outside")
    show(client, "GET", "/slow-sync")
    show(client, "GET", "/slow-async")

    section("THE AUTOMATIC DOCUMENTATION")
    print("  Every route you just saw, FastAPI also turned into a live web page")
    print("  with ZERO extra code from you. Run this to see it in your browser:")
    print()
    print("      python 03_first_api.py --serve")
    print("      then open  http://127.0.0.1:8000/docs")
    print()
    print("  Click any route, then 'Try it out', then 'Execute' - it sends a")
    print("  real request to your own server, live, and shows you the response.")
    print()
    print("  TRY IT NOW (3 minutes), with --serve running:")
    print("    1. open http://127.0.0.1:8000/users/2   - one user, as JSON")
    print("    2. open http://127.0.0.1:8000/users/abc - the 422 you didn't write")
    print("    3. open http://127.0.0.1:8000/docs      - and try a route there")


def checks(client):
    # A freebie: the lesson's own route. This one should pass before you
    # start, and tells you the grader itself is working.
    check("the lesson's own GET / still returns 200",
          client.get("/").status_code == 200)

    # --- WARM-UP 1 ---
    r = client.get("/health")
    check("WARM-UP 1: GET /health returns 200", r.status_code == 200)
    check("WARM-UP 1: returns {'status': 'healthy'}",
          r.status_code == 200 and r.json() == {"status": "healthy"})

    # --- WARM-UP 2 ---
    r = client.get("/count")
    check("WARM-UP 2: GET /count returns the number of users",
          r.status_code == 200 and r.json() == {"users": len(fake_users_db)})

    # --- EXERCISE 1 ---
    r = client.get("/hello")
    check("EXERCISE 1: GET /hello returns 200", r.status_code == 200)
    check("EXERCISE 1: has a 'message' key",
          r.status_code == 200 and "message" in r.json())

    # --- EXERCISE 2 ---
    r = client.get("/products")
    products_ok = r.status_code == 200 and isinstance(r.json(), list)
    check("EXERCISE 2: GET /products returns 200", r.status_code == 200)
    check("EXERCISE 2: returns a list of 3", products_ok and len(r.json()) == 3)
    check("EXERCISE 2: each item has name and price",
          products_ok
          and all("name" in p and "price" in p for p in r.json()))

    # --- EXERCISE 3 ---
    # Only meaningful once EXERCISE 2 exists - otherwise /products/1 would
    # return 404 simply because the route was never written, which would
    # have looked like a pass.
    if products_ok and r.json():
        first_id = r.json()[0]["id"]
        found = client.get(f"/products/{first_id}")
        check("EXERCISE 3: GET /products/{id} finds a real product",
              found.status_code == 200 and found.json().get("id") == first_id)
        missing = client.get("/products/999999")
        check("EXERCISE 3: an unknown id answers without crashing",
              missing.status_code in (200, 404))
    else:
        check("EXERCISE 3: GET /products/{id} finds a real product", False)
        check("EXERCISE 3: an unknown id answers without crashing", False)

    # --- EXERCISE 4 ---
    r = client.get("/users/1/role")
    check("EXERCISE 4: GET /users/1/role returns 200", r.status_code == 200)
    check("EXERCISE 4: returns just the role",
          r.status_code == 200 and r.json() == {"role": "admin"})


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP 1
#   @app.get("/health")
#   def health():
#       return {"status": "healthy"}
#
# WARM-UP 2
#   @app.get("/count")
#   def count_users():
#       return {"users": len(fake_users_db)}
#   # Working it out with len() means the answer stays right when the list
#   # changes. A typed-in 3 would quietly become a lie.
#
# EXERCISE 1
#   @app.get("/hello")
#   def hello():
#       return {"message": "Hello from FastAPI"}
#
# EXERCISE 2
#   fake_products_db = [
#       {"id": 1, "name": "Keyboard", "price": 49.99},
#       {"id": 2, "name": "Monitor", "price": 199.00},
#       {"id": 3, "name": "Mouse", "price": 19.99},
#   ]
#
#   @app.get("/products")
#   def list_products():
#       return fake_products_db
#
# EXERCISE 3
#   @app.get("/products/{product_id}")
#   def get_product(product_id: int):
#       for product in fake_products_db:
#           if product["id"] == product_id:
#               return product
#       return {"error": "not found"}
#
# EXERCISE 4
#   @app.get("/users/{user_id}/role")
#   def get_user_role(user_id: int):
#       for user in fake_users_db:
#           if user["id"] == user_id:
#               return {"role": user["role"]}
#       return {"error": "not found"}
#   # The path has TWO parts after /users: the changing {user_id}, and the
#   # fixed word "role". Only the part in braces becomes a parameter.
#
# EXERCISE 5
#   No code - this one is about exploring http://127.0.0.1:8000/docs yourself.
#   The 422 body you'll see follows a standard shape:
#       {"detail": [{"type": "int_parsing", "loc": ["path", "user_id"],
#                    "msg": "Input should be a valid integer", ...}]}
#   You'll parse and customise this exact shape in lesson 06.


if __name__ == "__main__":
    start(app, tour, checks)


print("\nNext: python 04_parameters_and_bodies.py")

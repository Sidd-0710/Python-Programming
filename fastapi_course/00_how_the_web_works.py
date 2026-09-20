"""
===============================================================================
 FASTAPI COURSE - LESSON 00: HOW THE WEB WORKS, AND GETTING SET UP
===============================================================================

Time: about 50 minutes.
Assumes: nothing at all.

HOW TO RUN THIS FILE
    Open a terminal in VS Code (menu: View -> Terminal) and type these three
    lines, pressing Enter after each:

        cd /Users/sidd/Python/fastapi_course
        source .venv/bin/activate
        python 00_how_the_web_works.py

    The end of this file checks your setup and tells you exactly what to fix.


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. say what a backend, a client and a server are             (sections 1-2)
  2. read an HTTP request and name each of its parts             (section 3)
  3. choose the right method (GET/POST/...) for a job            (section 4)
  4. choose the right status code (200/404/...)                  (section 5)
  5. read JSON, and match each part to Python                    (section 6)
  6. name URLs the way professionals do                          (section 7)
  7. see JSON become Python data, for real                        (PART A)
  8. pull a raw HTTP request apart yourself                       (PART B)
  9. get your computer set up and ready                           (PART C)

HOW TO READ THIS FILE:
  Sections 1-9 are reading - no code. Then PARTS A, B and C are code that
  runs. Read a section, then look at its output when you run the file.

NEW WORDS - come back here whenever you forget one:

  frontend     what people see: the website or phone app
  backend      the part nobody sees: the data, the rules, the saving.
               This is what you're learning to build.
  client       anything that ASKS for something (a browser, a phone app)
  server       the program that LISTENS and ANSWERS. That's what you'll write.
  API          the agreed way a client asks a server for things
  HTTP         the rules for how those messages are written
  request      the message the client sends
  response     the message the server sends back
  method       the kind of action wanted: GET, POST, PUT, PATCH, DELETE
  path         which thing you mean:  /users/42
  query        extra options after a ?  in a URL:  ?page=2&limit=10
  header       a  Name: value  line carrying extra information
  body         the actual data in a message, usually JSON
  status code  a 3-digit number saying what happened: 200 ok, 404 not found
  JSON         the text format APIs use for data. It looks like Python
               dictionaries and lists, because that's what it becomes.
  endpoint     one thing your API can do: GET /users, POST /users, ...
  route        another word for endpoint
  CRUD         Create, Read, Update, Delete - the four jobs on data
  REST         the usual style for naming URLs (section 7)
  port         a numbered door on a computer:  8000  in 127.0.0.1:8000
  localhost    "this same computer" (also written 127.0.0.1)
  framework    a library you build your program inside. FastAPI is one.
  package      code someone else wrote that you install and use
  pip          the command that installs packages
  virtual
  environment  a private box of packages for ONE project (PART C sets this up)

No Python knowledge is needed yet - lessons 01 and 02 teach that. Today is
about understanding the words, so nothing later sounds like a foreign language.


-------------------------------------------------------------------------------
 WHAT THIS COURSE IS
-------------------------------------------------------------------------------

Twelve lessons, taking you from no Python at all to building a real backend
with FastAPI: a database, user accounts, login with tokens, automated tests,
and a multi-file project laid out like the ones at work.

The times below add up to about 17 hours, and they assume you stop to try
things. Reading straight through is quicker; doing every exercise is slower.
Nothing is lost by taking two sittings over a lesson - each long one has a
break marked halfway.

  00  How the web works, and setup                        50 min
  01  Python essentials I: data and decisions              70 min
  02  Python essentials II: functions, classes, async      80 min
  03  Your first API                                       55 min
  04  Path parameters, query parameters, request bodies    70 min
  05  Pydantic models: validation and response shapes      85 min
  06  CRUD, status codes and errors                        90 min
  07  Dependencies, routers and middleware                 85 min
  08  Databases with SQLAlchemy                           100 min
  09  Authentication: passwords and JWT tokens            100 min
  10  Testing your API with pytest                        100 min
  11  Capstone: a complete multi-file project           about 3 h

Lessons 01 and 02 teach ONLY the Python that FastAPI needs. For more depth on
any Python topic later, ../python_course has a full lesson on each.


-------------------------------------------------------------------------------
 1. WHAT IS A "BACKEND"?
-------------------------------------------------------------------------------

Think of a restaurant.

  THE DINING ROOM is the FRONTEND. It's what customers see: tables, menus,
  decoration. On the web, that's the website or phone app - buttons, pages,
  pictures.

  THE KITCHEN is the BACKEND. Customers never see it. It stores ingredients
  (the DATABASE), follows recipes (the BUSINESS LOGIC), and enforces rules
  (you can't order something sold out; strangers can't walk into the kitchen).

  THE WAITER is the API. The dining room and kitchen never talk directly. The
  customer tells the waiter what they want in an agreed way ("one pasta, no
  cheese"), the waiter takes it to the kitchen, and comes back with either the
  dish or an explanation ("sorry, we're out of pasta").

  THE MENU is the API DOCUMENTATION: exactly what you're allowed to ask for,
  and how to ask.

A BACKEND DEVELOPER builds the kitchen and trains the waiter. When you tap
"Place order" in a food app, the app sends a message to a backend. The backend
checks you're logged in, checks the dish exists, saves the order in a
database, and replies "done - order #1042". That's the job you're preparing for.


-------------------------------------------------------------------------------
 2. CLIENTS AND SERVERS
-------------------------------------------------------------------------------

  CLIENT  anything that ASKS: a browser, a phone app, another backend, a
          script, or the test code in these lessons.
  SERVER  the program that LISTENS and ANSWERS. That's what you'll write.

A server waits at an ADDRESS and a PORT:

      http://127.0.0.1:8000
             ^^^^^^^^^ ^^^^
             address   port

  127.0.0.1 (also called "localhost") means "this same computer". While
  learning, the client and the server are both on your laptop.

  A PORT is like a flat number in an apartment building: one computer can run
  many servers, each at its own port. 8000 is the usual choice for development.


-------------------------------------------------------------------------------
 3. THE REQUEST: WHAT THE CLIENT SENDS
-------------------------------------------------------------------------------

Clients and servers talk using HTTP, a set of rules for the message format.
A request has up to four parts:

  METHOD    the verb: what kind of action you want
  PATH      which thing you mean, plus optional QUERY PARAMETERS after a ?
  HEADERS   extra information: who you are, what format you're sending
  BODY      the data itself - only when creating or updating something

Here is a real request, exactly as it travels over the network:

      POST /users?notify=true HTTP/1.1              <- method, path, query
      Host: 127.0.0.1:8000                          <- headers
      Content-Type: application/json
      Authorization: Bearer eyJhbGciOi...
                                                    <- an empty line
      {"name": "Sidd", "email": "sidd@example.com"} <- body

It is only text. There is no magic anywhere in this course - just text that
follows agreed rules. PART B below proves it.


-------------------------------------------------------------------------------
 4. THE METHODS, AND WHAT "CRUD" MEANS
-------------------------------------------------------------------------------

Almost every backend does four things to data. Developers call them CRUD:

  C  Create  ->  POST     "add a new user"
  R  Read    ->  GET      "show me user 42"  or  "list all users"
  U  Update  ->  PUT      "replace user 42 completely"
             ->  PATCH    "change only user 42's email"
  D  Delete  ->  DELETE   "remove user 42"

RULE: a GET request must never change anything. Browsers, caches and search
engines assume GET is safe to repeat. An API where visiting
GET /users/42/delete deletes someone will eventually lose data to a web crawler.


-------------------------------------------------------------------------------
 5. THE RESPONSE: WHAT THE SERVER SENDS BACK
-------------------------------------------------------------------------------

      HTTP/1.1 201 Created                          <- status code
      Content-Type: application/json                <- headers
                                                    <- an empty line
      {"id": 42, "name": "Sidd", "email": "sidd@example.com"}   <- body

The STATUS CODE is a three-digit summary of what happened. The first digit
tells you the family:

  2xx  IT WORKED
       200 OK                "here you go" - the normal success
       201 Created           something new was made (after a POST)
       204 No Content        done, nothing to send back (after a DELETE)

  4xx  THE CLIENT DID SOMETHING WRONG
       400 Bad Request       the request makes no sense
       401 Unauthorized      "who are you?" - not logged in
       403 Forbidden         "I know who you are, and you're not allowed"
       404 Not Found         that thing doesn't exist
       409 Conflict          clashes with existing data (email already used)
       422 Unprocessable     the data failed validation. FastAPI sends this
                             automatically when input has the wrong shape.

  5xx  THE SERVER BROKE
       500 Internal Error    there is a bug in YOUR code

Picking the right status code is part of the job. The frontend developer
writes code like "if the status is 404, show the not-found page". If you
return 200 with {"error": "not found"} inside, their app shows a blank page
and they have to come and find you.


-------------------------------------------------------------------------------
 6. JSON: THE LANGUAGE APIs SPEAK
-------------------------------------------------------------------------------

Request and response bodies are almost always JSON. It looks like this:

      {
        "id": 42,
        "name": "Sidd",
        "is_active": true,
        "roles": ["admin", "editor"],
        "address": {"city": "Mumbai", "pin": "400001"},
        "manager": null
      }

  { }            an OBJECT, with named fields    -> a Python DICTIONARY
  [ ]            an ARRAY, an ordered list       -> a Python LIST
  "text"         a string                        -> str
  42 or 4.5      a number                        -> int or float
  true / false                                   -> True / False
  null           nothing                         -> None

That table is why lesson 01 spends so long on dictionaries and lists: every
request you receive and every response you send is built from them.


-------------------------------------------------------------------------------
 7. DESIGNING URLS: THE "REST" STYLE
-------------------------------------------------------------------------------

Most APIs follow a convention called REST. The core idea: URLs name THINGS
(nouns), and the METHOD says what to do with them.

      GET     /books                          list all books
      POST    /books                          create a book
      GET     /books/7                        get book 7
      PATCH   /books/7                        update book 7
      DELETE  /books/7                        delete book 7
      GET     /books/7/reviews                the reviews belonging to book 7
      GET     /books?author=orwell&page=2     filtered, second page

  GOOD  POST /books               BAD  POST /createBook
  GOOD  DELETE /books/7           BAD  GET  /deleteBook?id=7
  GOOD  GET /books/7              BAD  GET  /book/7   (keep it plural)

Plural nouns, no verbs in the path, IDs in the path, filters in the query.
Follow that and other developers can guess your whole API without docs.


-------------------------------------------------------------------------------
 8. WHAT FASTAPI AND UVICORN ARE
-------------------------------------------------------------------------------

You'll install two main things. People mix them up, so:

  FASTAPI   a FRAMEWORK - a library you use to write the API. You write normal
            Python functions; FastAPI connects each one to a URL, reads the
            incoming JSON, checks it, and turns your return value into JSON.

  UVICORN   a SERVER - the program that actually listens on port 8000,
            receives the raw HTTP text, hands it to FastAPI, and sends
            FastAPI's answer back across the network.

  In the restaurant: FastAPI is the chef's recipes and skills. Uvicorn is the
  building with its door open to the street.

WHY FASTAPI:
  * you describe your data using Python TYPE HINTS (lesson 02) and FastAPI
    uses them to VALIDATE every request automatically
  * it creates interactive DOCUMENTATION for your API with zero extra work
  * it's fast, and handles many users at once using async (lesson 02)
  * it's one of the most used Python backend frameworks, especially for
    AI and data products


-------------------------------------------------------------------------------
 9. THE LIFE OF ONE REQUEST
-------------------------------------------------------------------------------

  1. A phone app sends:  GET /books/7
  2. Uvicorn receives the text on port 8000 and passes it to FastAPI.
  3. FastAPI matches the method and path to the function YOU registered
     for "GET /books/{book_id}".
  4. FastAPI sees your function expects  book_id: int  - so it turns the
     text "7" into the number 7, or replies 422 if someone sent "abc".
  5. YOUR FUNCTION runs: it looks up book 7 and returns a dictionary.
  6. FastAPI turns the dictionary into JSON and adds the status code 200.
  7. Uvicorn sends it back. The app shows the book.

You write step 5. FastAPI does steps 3, 4 and 6. Uvicorn does 2 and 7.
By lesson 04 you'll have watched every one of those steps happen.
"""

import json
import sys
from importlib import metadata
from pathlib import Path

HERE = Path(__file__).resolve().parent
LINE = "-" * 70


def section(title):
    """Prints a heading. (You'll learn to write functions like this in lesson 02.)"""
    print()
    print(LINE)
    print(f"  {title}")
    print(LINE)


# =============================================================================
# PART A — JSON IS TEXT THAT BECOMES PYTHON DATA
# =============================================================================
section("PART A - JSON <-> PYTHON")

# This is the exact text a phone app might send as a request body.
request_body_text = """
{
  "name": "Sidd",
  "email": "sidd@example.com",
  "is_active": true,
  "roles": ["admin", "editor"],
  "address": {"city": "Mumbai", "pin": "400001"},
  "manager": null
}
"""

# json.loads() turns JSON TEXT into PYTHON DATA. ("load string")
user = json.loads(request_body_text)

print("  before json.loads it's a  :", type(request_body_text).__name__, "(plain text)")
print("  after json.loads it's a   :", type(user).__name__, "(a dictionary)")
print()
print("  user['name']             ->", user["name"])
print("  user['is_active']        ->", user["is_active"], "   JSON true became Python True")
print("  user['roles']            ->", user["roles"], "   a JSON array became a list")
print("  user['roles'][0]         ->", user["roles"][0])
print("  user['address']['city']  ->", user["address"]["city"])
print("  user['manager']          ->", user["manager"], "   JSON null became None")

# json.dumps() goes the other way: PYTHON DATA -> JSON TEXT. ("dump string")
# FastAPI does this for you on every single response.
response_data = {"id": 42, "name": user["name"], "created": True, "manager": None}
response_text = json.dumps(response_data)
print()
print("  a Python dictionary      ->", response_data)
print("  turned into JSON text    ->", response_text)
print("  notice: True became true, None became null, ' became \"")

# In plain English: json.loads TEXT -> PYTHON. json.dumps PYTHON -> TEXT.
# A way to remember which is which: "loads" = LOAD a String into Python.
# FastAPI does both for you, on every single request and response.

# TRY IT NOW (2 minutes):
#   In request_body_text above, add a line  "city": "Mumbai",  after the email
#   line (keep the comma!). Then add a print showing user["city"] and run the
#   file. [It prints Mumbai. You just changed what a "request" contains.]
#   Bonus: delete one of the commas and run it again - the error you get,
#   JSONDecodeError, is exactly what your API will send a 422 for one day.


# =============================================================================
# PART B — AN HTTP REQUEST REALLY IS JUST TEXT
# =============================================================================
section("PART B - A REQUEST IS JUST TEXT")

# \r\n is how HTTP writes "new line". This is a complete, real request.
raw_request = (
    "POST /users?notify=true HTTP/1.1\r\n"
    "Host: 127.0.0.1:8000\r\n"
    "Content-Type: application/json\r\n"
    "\r\n"
    '{"name": "Sidd", "email": "sidd@example.com"}'
)

print("  the raw text a server receives:\n")
for line in raw_request.split("\r\n"):
    print(f"      {line}")

# Now pull it apart - the same job FastAPI does for you on every request.
# Don't worry about HOW these lines work yet (lesson 01 teaches text handling).
# What matters is WHAT they do, step by step:
head, body = raw_request.split("\r\n\r\n", 1)       # 1. split at the empty line
first_line, *header_lines = head.split("\r\n")      # 2. first line | the headers
method, full_path, http_version = first_line.split(" ")   # 3. "POST /users?... HTTP/1.1"
path, _, query = full_path.partition("?")           # 4. path | query

print()
print("  pulled apart into pieces:")
print(f"    method   : {method}")
print(f"    path     : {path}")
print(f"    query    : {query}")
for header in header_lines:
    print(f"    header   : {header}")
print(f"    body     : {json.loads(body)}")
print()
print("  FastAPI does this splitting for you, then hands your function clean")
print("  Python values - never raw text. That's a big part of why it's pleasant.")

# TRY IT NOW (2 minutes):
#   In raw_request above, change ONLY the first line to
#       "GET /books/7?format=short HTTP/1.1\r\n"
#   and run the file.
#   [method becomes GET, path becomes /books/7, query becomes format=short.
#   You've just written an HTTP request by hand - the same kind of message
#   your browser sends every time you open a web page.]


# =============================================================================
# PART C — CHECKING YOUR SETUP
# =============================================================================
section("PART C - IS YOUR COMPUTER READY?")

problems = []

version = sys.version_info
python_ok = version >= (3, 10)
print(f"  Python version      : {version.major}.{version.minor}.{version.micro}"
      f"   {'OK' if python_ok else '<- TOO OLD, need 3.10 or newer'}")
if not python_ok:
    problems.append("python version")

in_virtual_env = sys.prefix != sys.base_prefix
print(f"  Python being used   : {sys.executable}")
print(f"  virtual environment : {'active - good' if in_virtual_env else 'NOT ACTIVE'}")
if not in_virtual_env:
    problems.append("virtual environment not active")

PACKAGES = [
    ("fastapi", "the web framework itself"),
    ("uvicorn", "the server that runs your app"),
    ("pydantic", "data validation (lesson 05)"),
    ("email-validator", "checking email addresses (lesson 05)"),
    ("sqlalchemy", "talking to a database (lesson 08)"),
    ("pyjwt", "login tokens (lesson 09)"),
    ("python-multipart", "reading login forms (lesson 09)"),
    ("pytest", "automated tests (lesson 10)"),
]

print()
print("  packages:")
for package, purpose in PACKAGES:
    try:
        installed_version = metadata.version(package)
        print(f"    [ OK ]     {package:<18}{installed_version:<10}{purpose}")
    except metadata.PackageNotFoundError:
        print(f"    [MISSING]  {package:<18}{'':<10}{purpose}")
        problems.append(f"{package} missing")

try:
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from fastapi.testclient import TestClient  # noqa: F401
    print(f"    [ OK ]     {'test client':<18}{'':<10}lets lessons send requests to your API")
except Exception as error:
    print(f"    [MISSING]  {'test client':<18}{'':<10}({type(error).__name__}: {error})")
    problems.append("test client unavailable")

print()
if not problems:
    print("  EVERYTHING IS READY.")
    print("  Next lesson:   python 01_python_essentials_data.py")
else:
    print("  SOMETHING NEEDS FIXING:")
    for problem in problems:
        print(f"    - {problem}")
    print()
    print("  Run these commands in the terminal, one line at a time:")
    print(f"      cd {HERE}")
    if not (HERE / ".venv").exists():
        print("      python3 -m venv .venv")
    print("      source .venv/bin/activate")
    print("      pip install -r requirements.txt")
    print(f"      python {Path(__file__).name}")
    print()
    print("  WHAT THOSE DO:")
    print("    cd ...          moves the terminal into the course folder")
    print("    python3 -m venv .venv")
    print("                    creates a private box of packages for this project")
    print("    source .venv/bin/activate")
    print("                    switches the terminal to use that box. You'll see")
    print("                    (.venv) at the start of the prompt when it worked.")
    print("                    Do this EVERY time you open a new terminal.")
    print("    pip install -r requirements.txt")
    print("                    installs the packages listed in requirements.txt")

print()
print("  VS CODE: to make the Run button use the right Python -")
print("    1. press Cmd+Shift+P")
print("    2. type 'Python: Select Interpreter' and press Enter")
print("    3. choose the one whose path contains fastapi_course/.venv")
print("  (If you ever see an error mentioning flappy-bird/.venv, this is the fix -")
print("   VS Code is still remembering a deleted environment.)")


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * A backend is the part users never see. A client ASKS, a server ANSWERS,
#     and the agreed way of asking is the API.
#   * A request is just text: METHOD + PATH (+ query) + HEADERS + BODY.
#   * The method says what kind of action: GET reads, POST creates, PUT/PATCH
#     update, DELETE removes. A GET must never change anything.
#   * The response carries a STATUS CODE: 2xx worked, 4xx the client's
#     mistake, 5xx your server broke. Picking the right one is part of the job.
#   * JSON is text that maps straight onto Python: {} is a dict, [] is a list,
#     true/false are True/False, null is None.
#   * REST style: plural nouns, no verbs in the path, ids in the path,
#     filters in the query.  GET /books/7  not  GET /getBook?id=7
#   * FastAPI is the framework (your code); uvicorn is the server (the door).
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. Which part of a request says WHAT you want to do?
#   Q2. You ask for a user that doesn't exist. Which status code comes back?
#   Q3. What does JSON's  null  become in Python?
#   Q4. Why is  GET /deleteUser?id=5  a bad endpoint?
#   Q5. What's the difference between FastAPI and uvicorn?
#
# ANSWERS
#   A1. The method (GET, POST, PUT, PATCH, DELETE).
#   A2. 404 Not Found.
#   A3. None.
#   A4. It uses GET (which must be safe to repeat) for something destructive,
#       and puts a verb in the path. It should be  DELETE /users/5.
#   A5. FastAPI is the framework you write your API with; uvicorn is the
#       program that listens on the port and passes requests to it.


# =============================================================================
# EXERCISES
# =============================================================================
#
# These are mostly about understanding, so most answers are written as
# comments. Write your answers in the space below, then compare with the
# SOLUTIONS.
#
# WARM-UP A (easy) — Read one value out of JSON
#   Write this, then print the name and the second role:
#       text = '{"name": "Ana", "roles": ["admin", "editor"]}'
#       data = json.loads(text)
#
# WARM-UP B (easy) — Turn Python into JSON
#   Use json.dumps on {"id": 7, "paid": True, "note": None} and print the
#   result. Look at what happened to True and None.
#
# WARM-UP C (easy) — Method and path
#   As a comment, write the method and path for "delete order 17".
#
# EXERCISE 1 (easy) — Pick the method and path
#   For each action, write the HTTP method and path a REST API would use:
#     a) list all orders
#     b) get order 17
#     c) create a new order
#     d) cancel (delete) order 17
#     e) change only the delivery address of order 17
#     f) list the items inside order 17
#     g) list orders from customer 5 that are still pending, 20 per page
#
# EXERCISE 2 (easy) — Pick the status code
#     a) someone logs in with the wrong password
#     b) a logged-in user tries to view ANOTHER user's private order
#     c) someone signs up with an email that's already registered
#     d) your code divides by zero and crashes
#     e) GET /products/999, and product 999 doesn't exist
#     f) someone signs up and sends "abc" as their age
#     g) a DELETE succeeded and there's nothing to send back
#     h) a POST created a new product
#
# EXERCISE 3 (easy) — Fix the bad URLs
#   Rewrite each one in proper REST style:
#     GET  /getAllUsers
#     POST /users/create
#     GET  /deleteUser?id=5
#     GET  /user/5
#     POST /users/5/update
#
# EXERCISE 4 (medium) — Write and read JSON (this one is real code)
#   Below the line, write a JSON string for creating a product with: a name,
#   a price with decimals, a list of tags, a "dimensions" object containing
#   width and height, "discontinued" set to false, and "supplier" set to null.
#   Turn it into Python with json.loads, then print the height and the second
#   tag. Run the file to check.
#
# EXERCISE 5 (medium) — Explain it in your own words
#   As comments, answer:
#     a) what's the difference between FastAPI and uvicorn?
#     b) why is returning status 200 with {"error": "not found"} a bad idea?
#     c) why should GET requests never change data?
#
# EXERCISE 6 (easy) — Make PART C say EVERYTHING IS READY
#   Follow the commands it prints until the setup check is all [ OK ].

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   text = '{"name": "Ana", "roles": ["admin", "editor"]}'
#   data = json.loads(text)
#   print(data["name"])          # Ana
#   print(data["roles"][1])      # editor   (counting starts at 0!)
#
# WARM-UP B
#   print(json.dumps({"id": 7, "paid": True, "note": None}))
#   # -> {"id": 7, "paid": true, "note": null}
#   # Python's True/None are written true/null in JSON. Every language reads
#   # those, which is why APIs agreed on JSON in the first place.
#
# WARM-UP C
#   DELETE /orders/17
#
# EXERCISE 1
#   a) GET    /orders
#   b) GET    /orders/17
#   c) POST   /orders
#   d) DELETE /orders/17
#   e) PATCH  /orders/17           body: {"delivery_address": "..."}
#   f) GET    /orders/17/items
#   g) GET    /customers/5/orders?status=pending&limit=20
#      or     /orders?customer_id=5&status=pending&limit=20
#      Both are fine. Filters and paging belong in the query string.
#
# EXERCISE 2
#   a) 401   not successfully identified
#   b) 403   identified, but not allowed. (Some APIs deliberately return 404
#            here so strangers can't even learn that the order exists.)
#   c) 409   conflicts with existing data
#   d) 500   a bug on the server
#   e) 404
#   f) 422   FastAPI sends this automatically when validation fails
#   g) 204
#   h) 201
#
# EXERCISE 3
#   GET  /getAllUsers       ->  GET    /users
#   POST /users/create      ->  POST   /users
#   GET  /deleteUser?id=5   ->  DELETE /users/5
#   GET  /user/5            ->  GET    /users/5
#   POST /users/5/update    ->  PATCH  /users/5   (or PUT to replace it all)
#
# EXERCISE 4
#   product_text = """
#   {
#     "name": "Standing Desk",
#     "price": 349.99,
#     "tags": ["furniture", "office", "ergonomic"],
#     "dimensions": {"width": 120, "height": 75},
#     "discontinued": false,
#     "supplier": null
#   }
#   """
#   product = json.loads(product_text)
#   print("height:", product["dimensions"]["height"])     # 75
#   print("second tag:", product["tags"][1])              # office
#   # Counting starts at 0, so the SECOND tag is [1]. Lesson 01 explains why.
#
# EXERCISE 5
#   a) FastAPI is the framework: my code, routes, validation, JSON handling.
#      Uvicorn is the server: it listens on the port and passes requests to
#      FastAPI. FastAPI alone can't receive a request; uvicorn alone has no
#      idea what my API should do.
#   b) Frontend code and other tools decide what to do based on the status
#      code. A 200 tells them "success", so they try to display the error
#      message as if it were data. Caches may even store it.
#   c) Browsers pre-load links, crawlers follow them, and caches replay GETs,
#      all assuming they're harmless. A GET that deletes things will fire by
#      accident.


print()
print("=" * 70)
print("  Lesson 00 complete. Next: python 01_python_essentials_data.py")
print("=" * 70)

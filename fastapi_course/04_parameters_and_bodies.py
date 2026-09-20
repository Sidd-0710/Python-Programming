"""
===============================================================================
 FASTAPI COURSE - LESSON 04: PARAMETERS AND REQUEST BODIES
===============================================================================

Time: about 70 minutes (there's a good place for a break halfway).
Assumes: lessons 00-03.

THREE WAYS TO RUN THIS FILE - try all three, in this order:

    python 04_parameters_and_bodies.py            the TOUR (read this first)
    python 04_parameters_and_bodies.py --serve    a REAL server at /docs
    python 04_parameters_and_bodies.py --check    grades your exercise answers


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO READ DATA FROM EVERY PART OF A REQUEST:
  1. values inside the URL path          /products/3               (PART 1)
  2. values after the ? in the URL       /products?limit=2         (PART 2)
  3. JSON data the client sends          POST /products + JSON     (PART 3)
  4. all three at once                                             (PART 4)
  5. headers                             X-Request-Id: abc-123     (PART 5)
  6. the 422 error FastAPI sends when the client gets it wrong     (PART 6)

NEW WORDS - come back here whenever you forget one:

  path parameter   a value INSIDE the URL path. In  /products/3  the 3 is
                   the product_id. Written in the code as  /products/{product_id}
  query parameter  a value AFTER the ? in a URL:  ?category=books&limit=10
                   Each one is  name=value,  joined together with  &
  request body     the JSON data a client sends WITH a request - for example,
                   the details of a new product. GET requests don't have one.
  header           a  Name: value  line of extra information about a request,
                   like which browser sent it
  validation       checking that the data follows the rules (a number really
                   is a number, a limit is between 1 and 50, ...)
  422              the status code FastAPI sends back when the data breaks a
                   rule. It means "I understood you, but your data is wrong."

PYTHON YOU NEED FOR THIS LESSON
PART 0, just below, teaches each of these with a tiny example, and it's the
first thing the tour runs. Read PART 0 in the code before the rest:
  * Enum                a fixed list of allowed choices
  * X | None = None     "an X, or nothing" - an optional value
  * Literal["a", "b"]   "only exactly these values are allowed"
  * Annotated[...]      a type hint with extra instructions stuck on
  * a function as a VALUE   passing a function to sorted() or min()
  * r"..."              a "raw" string - used for patterns

Want more practice with plain Python first? The Python course covers these:
functions in python_course/10_functions.py, classes in 16_classes_and_objects.py.


-------------------------------------------------------------------------------
 THEORY: THE FOUR PLACES DATA CAN ARRIVE IN A REQUEST
-------------------------------------------------------------------------------

Lesson 00 showed that a request is just text. A client can put the data your
code needs in four different places, and each place has its own job:

    PUT /products/7?notify=true HTTP/1.1          <- PATH and QUERY
    Host: shop.example.com
    X-Request-Id: abc-123                          <- HEADERS
    Content-Type: application/json

    {"name": "Desk", "price": 349.99}             <- BODY

  PLACE    EXAMPLE                     USE IT FOR
  -------  --------------------------  -------------------------------------
  path     /products/7                 WHICH thing - identifies one resource
  query    ?category=books&limit=10    HOW to fetch it - filters, sort, pages
  body     {"name": "Desk", ...}       the DATA you are creating or changing
  header   Authorization: Bearer ...   facts ABOUT the request - who is
                                       asking, what language, a tracing id

A way to remember it, with a library as the example:
  path   = WHICH book:              /books/42
  query  = HOW you want the list:   /books?author=Tolkien&sort=year
  body   = a new book you're handing over
  header = your library card


HOW FASTAPI DECIDES WHERE EACH PARAMETER COMES FROM

You never write "this one is a query parameter". FastAPI reads your function
signature (the line starting with `def`) and applies three rules:

  1. The name appears in the path, like {product_id}   -> PATH parameter
  2. The type is a simple one (int, str, float, bool)  -> QUERY parameter
  3. The type is a Pydantic model (a BaseModel class)  -> the request BODY

Headers are the one exception - you mark those explicitly with Header().

    @app.put("/products/{product_id}")
    def replace(product_id: int,           # rule 1 -> from the path
                product: ProductIn,        # rule 3 -> from the JSON body
                notify: bool = False):     # rule 2 -> from ?notify=...

(The parameter with a default goes LAST. Python refuses a parameter without a
default after one that has a default - that's a SyntaxError, not a FastAPI
rule. See COMMON MISTAKES at the bottom.)
"""

from enum import Enum
from typing import Annotated, Literal

from fastapi import FastAPI, Header, Path, Query
from pydantic import BaseModel

from course_tools import check, section, show, start

app = FastAPI(
    title="Lesson 04 API",
    description="Path, query, body and header parameters.",
    version="1.0.0",
)

# The pretend database for this lesson - a list of dicts, just like lesson 03.
fake_products_db = [
    {"id": 1, "name": "Mechanical Keyboard", "category": "electronics",
     "price": 89.99, "in_stock": True, "tags": ["office", "gaming"]},
    {"id": 2, "name": "Noise-Cancelling Headphones", "category": "electronics",
     "price": 249.00, "in_stock": False, "tags": ["audio", "travel"]},
    {"id": 3, "name": "Clean Code", "category": "books",
     "price": 32.50, "in_stock": True, "tags": ["programming"]},
    {"id": 4, "name": "Designing Data-Intensive Applications", "category": "books",
     "price": 45.00, "in_stock": True, "tags": ["programming", "databases"]},
    {"id": 5, "name": "Chef's Knife", "category": "kitchen",
     "price": 59.95, "in_stock": True, "tags": ["cooking"]},
    {"id": 6, "name": "Pour-Over Coffee Set", "category": "kitchen",
     "price": 38.00, "in_stock": False, "tags": ["cooking", "coffee"]},
]


# =============================================================================
# PART 0 — THE PYTHON YOU NEED FOR THIS LESSON
# =============================================================================
#
# Plain Python - no web server yet. Each idea gets a tiny example here, and
# python_warm_up() (further down) runs them as the first part of the tour.

# ---- 0a. An Enum: a fixed list of allowed choices -----------------------------
#
# Some values can only be one of a few choices: a T-shirt size, a day of the
# week, a product category. An Enum ("enumeration") lists those choices once.
#
# Read  class Size(str, Enum):  as "Size is a list of choices, and each choice
# is also a piece of text". The part before each = is the name you use in
# code; the part after it is the actual text value.
class Size(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"

# Size.large            the "large" choice
# Size.large.value      its text: "large"
# Size("large")         look up a choice by its text - fails if it isn't one


# ---- 0b. X | None = None: an optional value ------------------------------------
#
# The  |  means "or". So  str | None  means "a piece of text, OR None".
# Adding  = None  makes it optional: if nobody gives a value, it's None.
def greet(name: str | None = None) -> str:
    if name is None:
        return "Hello, whoever you are!"
    return f"Hello, {name}!"


# ---- 0c. Literal: only exactly these values -------------------------------------
#
#     sort_by: Literal["name", "price"]
#
# means sort_by must be exactly "name" or exactly "price" - nothing else.
# Plain Python doesn't check this. FastAPI DOES, and replies 422 to anything
# else. It's like a tiny Enum you can write in one line.


# ---- 0d. Annotated: a type hint with extra instructions stuck on -----------------
#
#     limit: Annotated[int, Query(ge=1, le=50)] = 10
#
# Read it as: "limit is an int - AND here are extra instructions for FastAPI:
# it comes from the query string and must be between 1 and 50. If the client
# doesn't send it, use 10."
#
# Plain Python ignores the extra part completely. You can see that here:
def add_one(number: Annotated[int, "this note is ignored by Python"]) -> int:
    return number + 1

# The short names inside Query(...) and Path(...) mean:
#     ge = Greater than or Equal (>=)      gt = Greater Than (>)
#     le = Less than or Equal (<=)         lt = Less Than (<)


# ---- 0e. Passing a function as a value -------------------------------------------
#
# sorted() puts a list in order and min() finds the smallest item. For a list
# of dicts, Python can't guess what "smaller" means - by price? by name? So
# you GIVE it a function (without brackets!) that picks the thing to compare:
#
#     sorted(products, key=price_of)
#
# means "sort the products, comparing them by whatever price_of returns".
# Note: key=price_of   (no brackets) hands over the function itself.
#       key=price_of() (brackets) would CALL it right now - a mistake.
def price_of(product: dict) -> float:
    return product["price"]


def name_of(product: dict) -> str:
    return product["name"]


# ---- 0f. r"...": raw strings, for patterns -----------------------------------------
#
# Later you'll see  pattern=r"^[a-z0-9_]+$".  The r in front means "raw":
# backslashes in the text are kept exactly as typed. Patterns (called regular
# expressions) use lots of them, so they're usually written as raw strings.
# You don't need to write patterns yourself yet - copy them when needed.


def python_warm_up():
    print("  0a. An Enum is a fixed list of choices:")
    print(f"        Size.large.value       -> {Size.large.value!r}")
    print(f"        Size('medium').value   -> {Size('medium').value!r}")
    try:
        Size("gigantic")
    except ValueError as error:
        print(f"        Size('gigantic')       -> ValueError: {error}")
    print("      FastAPI uses exactly this check to reject bad choices with a 422.")

    print("\n  0b. An optional value, with  name: str | None = None")
    print(f"        greet()                -> {greet()!r}")
    print(f"        greet('Sidd')          -> {greet('Sidd')!r}")

    print("\n  0d. Annotated: Python ignores the extra part")
    print(f"        add_one(5)             -> {add_one(5)}")

    sample = fake_products_db[:3]
    print("\n  0e. Passing a function to sorted() and min()")
    print(f"        the first 3 products   -> {[name_of(p) for p in sample]}")
    by_price = sorted(sample, key=price_of)
    print(f"        sorted(key=price_of)   -> {[name_of(p) for p in by_price]}")
    cheapest = min(sample, key=price_of)
    print(f"        min(key=price_of)      -> {cheapest['name']!r}, the cheapest")
    print("\n      (!r inside an f-string's braces shows text WITH its quotes, so")
    print("       you can tell it's text. That's all it does.)")


# =============================================================================
# PART 1 — PATH PARAMETERS, PROPERLY
# =============================================================================

# ---- 1a. An Enum in a route: only real categories allowed ---------------------
# Only three categories exist. Instead of accepting any text and checking it
# by hand, we list the allowed values once (PART 0a). FastAPI uses the list to
# reject anything else AND to show a dropdown of choices in /docs.
class Category(str, Enum):
    electronics = "electronics"
    books = "books"
    kitchen = "kitchen"


@app.get("/categories/{category}")
def get_category(category: Category):
    # In plain English: "make a list of the products whose category matches"
    # (a list comprehension - fastapi_course lesson 01 PART 8)
    matching = [p for p in fake_products_db if p["category"] == category.value]
    return {"category": category.value, "product_count": len(matching)}


# ---- 1b. Two path parameters ------------------------------------------------
# Each {placeholder} matches a function parameter of the same name.
@app.get("/users/{user_id}/orders/{order_id}")
def get_user_order(user_id: int, order_id: int):
    return {"user_id": user_id, "order_id": order_id,
            "note": "both values came from the path"}


# ---- 1c. ROUTE ORDER MATTERS ------------------------------------------------
#
# FastAPI checks routes TOP TO BOTTOM and uses the FIRST one that matches.
# "/products/cheapest" must be declared BEFORE "/products/{product_id}",
# otherwise {product_id} would grab the word "cheapest" and fail to turn it
# into an int.
@app.get("/products/cheapest")
def cheapest_product():
    return min(fake_products_db, key=price_of)       # PART 0e


# ---- 1d. Path() - rules for a path parameter --------------------------------
# An id of 0 or -5 is a valid int but can never be a real product, so we
# refuse it at the door. `description` appears in the /docs page.
@app.get("/products/{product_id}")
def get_product(
    product_id: Annotated[int, Path(ge=1, description="The product's id, 1 or more")],
):
    # In plain English: "product_id is a whole number, taken from the path,
    # and it must be 1 or more" (PART 0d)
    for product in fake_products_db:
        if product["id"] == product_id:
            return product
    return {"error": "not found"}          # lesson 06 turns this into a real 404


# ---- 1e. The WRONG order, kept on purpose so the tour can show it failing ----
@app.get("/wrong-order/{item_id}")
def wrong_order_by_id(item_id: int):
    return {"item_id": item_id}


@app.get("/wrong-order/latest")            # never reached - the route above wins
def wrong_order_latest():
    return {"item": "the latest one"}


# TRY IT NOW (2 minutes):
#   Run  python 04_parameters_and_bodies.py --serve  then paste these into your
#   BROWSER's address bar. GET requests work straight from a browser:
#       http://127.0.0.1:8000/categories/books
#       http://127.0.0.1:8000/categories/toys       (read the 422 message)
#       http://127.0.0.1:8000/products/0            (breaks the ge=1 rule)
#   Press Ctrl+C in the terminal to stop the server when you're done.


# =============================================================================
# PART 2 — QUERY PARAMETERS: FILTERS, SORTING AND PAGES
# =============================================================================
#
# Anything after the ? in a URL:   /products?category=books&limit=3
#                                            ^^^^^^^^^^^^^^ ^^^^^^^
#                                             name=value pairs, joined by &
#
# A query parameter WITH a default is optional. WITHOUT a default it's
# required. Exactly lesson 02 part 3 - FastAPI just fills in the arguments
# from the URL instead of from your code.

def has_every_tag(product: dict, wanted_tags: list[str]) -> bool:
    """True if the product has ALL the wanted tags."""
    for tag in wanted_tags:
        if tag not in product["tags"]:
            return False                 # one missing tag is enough to say no
    return True


# ---- 2a. The classic "list" endpoint: every filter optional -----------------
@app.get("/products")
def list_products(
    # `X | None = None` means "optional - None when the client didn't send it"
    # (PART 0b)
    category: Category | None = None,
    in_stock: bool | None = None,
    min_price: Annotated[float | None, Query(ge=0)] = None,
    max_price: Annotated[float | None, Query(ge=0)] = None,
    # A LIST from the query string: ?tag=cooking&tag=coffee -> ["cooking", "coffee"]
    # Query() is REQUIRED here - without it, FastAPI would expect a list in
    # the request body instead.
    tag: Annotated[list[str] | None, Query()] = None,
    # Literal means "only exactly these values are allowed" (PART 0c)
    sort_by: Literal["name", "price"] = "name",
    descending: bool = False,
    # Paging: skip the first `skip` results, then return at most `limit`.
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
):
    results = fake_products_db

    # Each filter only applies if the client actually sent it.
    # `is not None` matters for in_stock: False is a real filter value, and
    # `if in_stock:` would wrongly skip it.
    if category is not None:
        results = [p for p in results if p["category"] == category.value]
    if in_stock is not None:
        results = [p for p in results if p["in_stock"] == in_stock]
    if min_price is not None:
        results = [p for p in results if p["price"] >= min_price]
    if max_price is not None:
        results = [p for p in results if p["price"] <= max_price]
    if tag is not None:
        results = [p for p in results if has_every_tag(p, tag)]

    # PART 0e: hand sorted() the function that picks what to compare
    if sort_by == "price":
        results = sorted(results, key=price_of, reverse=descending)
    else:
        results = sorted(results, key=name_of, reverse=descending)

    # results[skip:skip + limit] is a SLICE: "from position skip, up to (not
    # including) position skip + limit". With skip=0, limit=10 -> items 0 to 9.
    page = results[skip:skip + limit]

    # Returning the total alongside one page lets a client draw
    # "showing 1-10 of 57". Real APIs do this constantly.
    return {"total": len(results), "skip": skip, "limit": limit, "items": page}


# ---- 2b. REQUIRED query parameters: no default ------------------------------
# Made-up exchange rates, for teaching only.
@app.get("/convert")
def convert_currency(amount: Annotated[float, Query(gt=0)],
                     to: Literal["EUR", "GBP", "INR"]):
    rates = {"EUR": 0.92, "GBP": 0.79, "INR": 83.20}
    return {"amount_usd": amount, "currency": to,
            "converted": round(amount * rates[to], 2)}


# ---- 2c. Rules for text: length and pattern ---------------------------------
# `pattern` is a regular expression (PART 0f). This one means: from start (^)
# to end ($), only lowercase letters, digits and underscores, at least one (+).
@app.get("/usernames/available")
def username_available(
    username: Annotated[str, Query(min_length=3, max_length=20,
                                   pattern=r"^[a-z0-9_]+$")],
):
    taken = ["sidd", "ana", "marco"]
    return {"username": username, "available": username not in taken}


# TRY IT NOW (2 minutes), with --serve running, in your browser:
#   http://127.0.0.1:8000/products?category=kitchen
#   http://127.0.0.1:8000/products?sort_by=price&descending=true&limit=2
#   http://127.0.0.1:8000/convert?amount=10&to=INR
#   Then change one value at a time and predict the answer before you press Enter.


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. Paths and query strings are done - that's most of
#  what GET requests ever need. After the break: sending data IN (PARTS 3-6).
# -----------------------------------------------------------------------------


# =============================================================================
# PART 3 — THE REQUEST BODY
# =============================================================================
#
# Filters belong in the query string. But the data for a NEW product - name,
# price, tags - belongs in the BODY, as JSON.
#
# To receive a body you describe its shape with a class that inherits from
# pydantic's BaseModel. This is a first taste: lesson 05 is entirely about
# these models. For now, notice it looks like a class with type hints and NO
# __init__ - Pydantic writes that for you (lesson 02 part 5 promised this).

class ProductIn(BaseModel):
    name: str                         # required - no default
    category: Category                # required, and must be an allowed value
    price: float                      # required
    in_stock: bool = True             # optional - defaults to True
    tags: list[str] = []              # optional. Pydantic gives every object
                                      # its OWN copy of this list, so lesson
                                      # 02's mutable-default trap can't happen


def next_product_id() -> int:
    """The biggest id so far, plus one."""
    highest = 0
    for product in fake_products_db:
        if product["id"] > highest:
            highest = product["id"]
    return highest + 1


@app.post("/products")
def create_product(product: ProductIn):     # rule 3: a BaseModel -> the body
    # By the time this line runs, the body has ALREADY been checked: every
    # required field exists and every value has the right type. If not, the
    # client got a 422 and this function never ran.

    # Build the new product as a dict, step by step:
    new_product = {"id": next_product_id()}   # start with just the id
    new_product.update(product.model_dump())  # then add every field from the body
    # model_dump() turns the model back into a plain dict.
    # .update() copies every key and value from that dict into new_product.

    fake_products_db.append(new_product)
    return new_product                     # lesson 06 makes this a proper 201


# TRY IT NOW (3 minutes):
#   With --serve running, open http://127.0.0.1:8000/docs, click POST /products,
#   then "Try it out". Edit the example JSON, click Execute, and read the
#   response. Then remove the "price" line from the JSON and try again.
#   (A browser address bar can only send GET requests - /docs can send any.)


# =============================================================================
# PART 4 — PATH + BODY + QUERY IN ONE REQUEST
# =============================================================================
#
# The three rules from the theory, all in one function. FastAPI sorts them out.

@app.put("/products/{product_id}")
def replace_product(
    product_id: Annotated[int, Path(ge=1)],     # rule 1: in the path
    product: ProductIn,                          # rule 3: a model -> body
    notify_subscribers: bool = False,            # rule 2: simple type -> query
):
    for existing in fake_products_db:
        if existing["id"] == product_id:
            existing.update(product.model_dump())   # dict.update, lesson 01 part 9
            return {"product": existing, "notified": notify_subscribers}
    return {"error": "not found"}


# =============================================================================
# PART 5 — HEADERS
# =============================================================================
#
# Header names contain hyphens (User-Agent, X-Request-Id), but Python names
# can't. So FastAPI converts for you:
#
#     parameter name      header it reads
#     user_agent     ->   User-Agent
#     x_request_id   ->   X-Request-Id
#
# Header names are not case-sensitive, so X-REQUEST-ID works too.
# (You won't read the Authorization header by hand like this - lesson 09 has
# a proper tool for it.)

@app.get("/request-info")
def request_info(
    user_agent: Annotated[str | None, Header()] = None,
    x_request_id: Annotated[str | None, Header()] = None,
    accept_language: Annotated[str, Header()] = "en",
):
    if x_request_id is None:
        request_id = "none sent"
    else:
        request_id = x_request_id
    return {"user_agent": user_agent, "request_id": request_id,
            "language": accept_language}


# =============================================================================
# COMMON MISTAKES
# =============================================================================
#
# 1. "SyntaxError: parameter without a default follows parameter with a default"
#       def f(limit: int = 10, product: ProductIn):   # wrong order
#    Put parameters WITHOUT defaults first. This is Python, not FastAPI.
#
# 2. A typo between the path and the function:
#       @app.get("/items/{item_id}")
#       def get_item(id: int): ...
#    `id` doesn't match {item_id}, so FastAPI treats `id` as a REQUIRED QUERY
#    parameter. Every request fails with 422 "query -> id: Field required".
#
# 3. A list query parameter without Query():
#       tags: list[str] | None = None            # FastAPI expects a BODY
#       tags: Annotated[list[str] | None, Query()] = None   # correct
#
# 4. Route order: a fixed path like /products/cheapest must come BEFORE
#    /products/{product_id}. Seen in the tour, PART 1e.
#
# 5. `if in_stock:` instead of `if in_stock is not None:` for an optional
#    bool filter. False means "only out-of-stock" - not "no filter".
#
# 6. Sending a body with GET. Browsers and many tools drop it. If a GET needs
#    inputs, they belong in the path or query string.
#
# 7. key=price_of() with brackets. That CALLS the function immediately (with
#    no product - an error). Pass the function itself: key=price_of.


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * PATH parameters pick WHICH thing:   /products/{product_id}
#   * QUERY parameters say HOW:           ?category=books&limit=10
#     With a default they're optional; without one they're required.
#   * The BODY carries JSON data. Describe its shape with a BaseModel class.
#   * HEADERS need Header(). user_agent reads the User-Agent header.
#   * Annotated[int, Query(ge=1)] adds rules. Break a rule -> 422.
#   * Every 422 lists each problem with a `loc` (where) and a `msg` (what).
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. In  GET /orders/5?paid=true  what is the path parameter, and what is
#       the query parameter?
#   Q2. def search(q: str): ...  Is q required or optional? Where does it
#       come from?
#   Q3. Why does GET /products/cheapest work but GET /wrong-order/latest fail?
#   Q4. What does  sorted(items, key=price_of)  do?
#   Q5. A client sends {"name": "Pen", "category": "books"} to POST /products.
#       What happens, and why?
#
# ANSWERS
#   A1. 5 is the path parameter (which order). paid=true is the query
#       parameter.
#   A2. Required (no default), from the query string: /search?q=...
#   A3. Route order. /products/cheapest is declared BEFORE /products/{product_id};
#       /wrong-order/{item_id} is declared before /wrong-order/latest, and grabs
#       the word "latest".
#   A4. Returns a new list of the items, in order of whatever price_of returns
#       for each one - cheapest first.
#   A5. A 422. price is required in ProductIn and it's missing. The function
#       never runs.


# =============================================================================
# YOUR EXERCISE CODE GOES HERE - above the tour, so FastAPI registers it
# =============================================================================




# =============================================================================
# THE TOUR — runs when you execute this file with no flags
# =============================================================================

def tour(client):
    section("PART 0: THE PYTHON YOU NEED FOR THIS LESSON")
    python_warm_up()

    section("PART 1a: A FIXED SET OF CHOICES - Enum")
    show(client, "GET", "/categories/books")
    show(client, "GET", "/categories/toys",
         note="not an allowed value - the error message lists the valid ones")

    section("PART 1b: TWO PATH PARAMETERS")
    show(client, "GET", "/users/7/orders/42")

    section("PART 1c + 1d: ROUTE ORDER, AND RULES WITH Path()")
    show(client, "GET", "/products/cheapest",
         note="declared BEFORE /products/{product_id}, so it's reached")
    show(client, "GET", "/products/3", note="a normal lookup")
    show(client, "GET", "/products/0",
         note="0 is a valid int, but breaks the ge=1 rule")

    section("PART 1e: THE WRONG ROUTE ORDER")
    show(client, "GET", "/wrong-order/latest",
         note="/wrong-order/{item_id} was declared first, and grabbed 'latest'")
    print("\n  The /wrong-order/latest route exists, but it can never be reached.")
    print("  Swap the two functions in the file and this request would work.")

    section("PART 2a: OPTIONAL QUERY PARAMETERS - filters, sorting, pages")
    show(client, "GET", "/products?limit=2", note="no filters, just a small page")
    show(client, "GET", "/products?category=books")
    show(client, "GET", "/products?in_stock=yes&max_price=60",
         note="'yes' becomes True, '60' becomes 60.0")
    show(client, "GET", "/products?tag=cooking&tag=coffee",
         note="repeat a name to send a list: tag = ['cooking', 'coffee']")
    show(client, "GET", "/products?sort_by=price&descending=true&limit=1",
         note="the single most expensive product")

    section("PART 2b: REQUIRED QUERY PARAMETERS")
    show(client, "GET", "/convert?amount=100&to=EUR")
    show(client, "GET", "/convert?amount=100",
         note="`to` has no default, so leaving it out is an error")

    section("PART 2c: RULES FOR TEXT - length and pattern")
    show(client, "GET", "/usernames/available?username=priya_22")
    show(client, "GET", "/usernames/available?username=sidd", note="valid, but taken")
    show(client, "GET", "/usernames/available?username=Sidd!",
         note="uppercase letter and '!' break the pattern")

    section("PART 3: THE REQUEST BODY")
    show(client, "POST", "/products", note="a complete, valid product",
         json={"name": "Cast Iron Pan", "category": "kitchen",
               "price": 42.00, "tags": ["cooking"]})
    show(client, "GET", "/products?category=kitchen",
         note="the new product is now in the list")
    show(client, "POST", "/products", note="`price` is missing",
         json={"name": "Mystery Box", "category": "kitchen"})
    show(client, "POST", "/products", note="price can't become a number",
         json={"name": "Mystery Box", "category": "kitchen", "price": "cheap"})
    show(client, "POST", "/products",
         note="price sent as TEXT \"19.99\" (converted), plus an unknown field (ignored)",
         json={"name": "Bookmark", "category": "books", "price": "19.99",
               "colour": "red"})
    print("\n  Notice \"colour\" vanished. Unknown fields are ignored by default.")
    print("  Lesson 05 shows how to REJECT them instead, and why you'd want to.")

    section("PART 4: PATH + BODY + QUERY IN ONE REQUEST")
    show(client, "PUT", "/products/5?notify_subscribers=true",
         json={"name": "Chef's Knife (Pro)", "category": "kitchen",
               "price": 79.95, "tags": ["cooking", "premium"]})

    section("PART 5: HEADERS")
    show(client, "GET", "/request-info",
         note="no custom headers - the test client still sends User-Agent")
    show(client, "GET", "/request-info",
         headers={"X-Request-Id": "req-7f3a", "Accept-Language": "hi-IN"})

    section("PART 6: READING A 422 - three mistakes in one request")
    response = show(client, "GET", "/products?limit=500&min_price=-1&in_stock=maybe")
    print("\n  Every error has a `loc` (WHERE) and a `msg` (WHAT). In short:")
    for problem in response.json()["detail"]:
        where = " -> ".join(str(part) for part in problem["loc"])
        print(f"    {where:<20} {problem['msg']}")
    print("\n  loc starts with 'path', 'query', 'header' or 'body' - so you always")
    print("  know which of the four places from the THEORY section to look at.")


# =============================================================================
# EXERCISES
# =============================================================================
#
# Write your code in the "YOUR EXERCISE CODE GOES HERE" space above the tour,
# then run:
#     python 04_parameters_and_bodies.py --check
#
# Do the WARM-UPS first. Each one practises ONE idea from this lesson.
#
# WARM-UP 1 (easy) — One query parameter
#   Add GET /echo?word=...  that returns {"you_sent": <the word>}.
#   word is REQUIRED (so: no default).
#   Example: /echo?word=hello  ->  {"you_sent": "hello"}
#
# WARM-UP 2 (easy) — One path parameter
#   Add GET /greet/{name}  that returns {"message": "Hello, <name>!"}.
#   Example: /greet/Sidd  ->  {"message": "Hello, Sidd!"}
#
# EXERCISE 1 (medium) — A required, validated query parameter
#   Add GET /search?q=...  that returns a LIST of the products whose name
#   contains q, ignoring upper/lower case ("keyboard" finds "Mechanical
#   Keyboard"). q is REQUIRED and must be 2 to 50 characters long.
#   Hint: "abc" in "xabcx" is True. .lower() makes text lowercase.
#
# EXERCISE 2 (medium) — Path parameter + optional query parameter
#   Add GET /products/{product_id}/price-with-tax?rate=0.2
#   product_id must be 1 or more. rate is optional, defaults to 0.2, and must
#   be between 0 and 1. Return:
#       {"product_id": ..., "price": ..., "rate": ...,
#        "price_with_tax": price * (1 + rate), rounded to 2 decimal places}
#   For an unknown product, return {"error": "not found"}.
#
# EXERCISE 3 (medium) — Your first request body
#   Create a ReviewIn model with: product_id (int, required), rating (int,
#   required), comment (text, OPTIONAL - None when not sent).
#   Add POST /reviews that returns the review as a dict (model_dump()).
#
# EXERCISE 4 (easy) — A header with a fallback
#   Add GET /version-info that reads an X-Api-Version header and returns
#   {"api_version": <the header's value>}, or {"api_version": "v1"} when the
#   client didn't send the header.
#
# EXERCISE 5 (challenge) — Enum in a path
#   Add GET /products/by-category/{category} returning a LIST of the products
#   in that category. Use the Category Enum, so /products/by-category/toys
#   is rejected with a 422 automatically.
#   Question to think about: why doesn't this route clash with
#   /products/{product_id}?  (Answer in SOLUTIONS.)


def checks(client):
    check("the lesson's own GET /products still works",
          client.get("/products").status_code == 200)

    # --- WARM-UP 1 ---
    r = client.get("/echo?word=hello")
    check("WARM-UP 1: GET /echo?word=hello returns {'you_sent': 'hello'}",
          r.status_code == 200 and r.json() == {"you_sent": "hello"})
    check("WARM-UP 1: leaving out word gives 422", client.get("/echo").status_code == 422)

    # --- WARM-UP 2 ---
    r = client.get("/greet/Sidd")
    check("WARM-UP 2: GET /greet/Sidd returns {'message': 'Hello, Sidd!'}",
          r.status_code == 200 and r.json() == {"message": "Hello, Sidd!"})

    # --- EXERCISE 1 ---
    r = client.get("/search?q=KEYBOARD")
    results = r.json() if r.status_code == 200 else None
    check("EXERCISE 1: GET /search?q=KEYBOARD returns 200", r.status_code == 200)
    check("EXERCISE 1: returns a list containing the Mechanical Keyboard",
          isinstance(results, list)
          and any(p.get("name") == "Mechanical Keyboard" for p in results))
    check("EXERCISE 1: returns ONLY matching products",
          isinstance(results, list)
          and all("keyboard" in p.get("name", "").lower() for p in results))
    check("EXERCISE 1: leaving out q gives 422",
          client.get("/search").status_code == 422)
    check("EXERCISE 1: q with 1 character gives 422",
          client.get("/search?q=k").status_code == 422)

    # --- EXERCISE 2 ---
    r = client.get("/products/3/price-with-tax")
    body = r.json() if r.status_code == 200 else {}
    check("EXERCISE 2: default rate 0.2 -> 32.50 becomes 39.0",
          abs((body.get("price_with_tax") or 0) - 39.0) < 0.001)
    r = client.get("/products/3/price-with-tax?rate=0.5")
    body = r.json() if r.status_code == 200 else {}
    check("EXERCISE 2: ?rate=0.5 -> 48.75",
          abs((body.get("price_with_tax") or 0) - 48.75) < 0.001)
    check("EXERCISE 2: ?rate=1.5 is rejected with 422",
          client.get("/products/3/price-with-tax?rate=1.5").status_code == 422)
    check("EXERCISE 2: product id 0 is rejected with 422",
          client.get("/products/0/price-with-tax").status_code == 422)

    # --- EXERCISE 3 ---
    r = client.post("/reviews", json={"product_id": 1, "rating": 5, "comment": "Great"})
    check("EXERCISE 3: a full review returns 200 with its rating",
          r.status_code == 200 and r.json().get("rating") == 5)
    r = client.post("/reviews", json={"product_id": 1, "rating": 4})
    check("EXERCISE 3: comment is optional (None when not sent)",
          r.status_code == 200 and "comment" in r.json() and r.json()["comment"] is None)
    check("EXERCISE 3: a missing rating gives 422",
          client.post("/reviews", json={"product_id": 1}).status_code == 422)
    check("EXERCISE 3: rating 'five' gives 422",
          client.post("/reviews", json={"product_id": 1, "rating": "five"}).status_code == 422)

    # --- EXERCISE 4 ---
    r = client.get("/version-info", headers={"X-Api-Version": "v2"})
    check("EXERCISE 4: sends X-Api-Version: v2 -> api_version is v2",
          r.status_code == 200 and r.json().get("api_version") == "v2")
    r = client.get("/version-info")
    check("EXERCISE 4: no header -> api_version is v1",
          r.status_code == 200 and r.json().get("api_version") == "v1")

    # --- EXERCISE 5 ---
    r = client.get("/products/by-category/books")
    results = r.json() if r.status_code == 200 else None
    check("EXERCISE 5: /products/by-category/books returns a list of books",
          isinstance(results, list) and len(results) >= 2
          and all(p.get("category") == "books" for p in results))
    check("EXERCISE 5: /products/by-category/toys gives 422",
          client.get("/products/by-category/toys").status_code == 422)


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP 1
#   @app.get("/echo")
#   def echo(word: str):
#       return {"you_sent": word}
#
#   `word` isn't in the path and has no default -> a REQUIRED query parameter.
#
# WARM-UP 2
#   @app.get("/greet/{name}")
#   def greet_by_name(name: str):
#       return {"message": f"Hello, {name}!"}
#
#   {name} in the path + a parameter called name -> a path parameter.
#   (Not called `greet`: PART 0 already has a function with that name.)
#
# EXERCISE 1
#   @app.get("/search")
#   def search_products(q: Annotated[str, Query(min_length=2, max_length=50)]):
#       needle = q.lower()
#       matches = []
#       for product in fake_products_db:
#           if needle in product["name"].lower():
#               matches.append(product)
#       return matches
#
#   No default on q -> required. Query(...) adds the length rules.
#   Once loops feel easy, the same thing fits in one line as a comprehension:
#       return [p for p in fake_products_db if needle in p["name"].lower()]
#
# EXERCISE 2
#   @app.get("/products/{product_id}/price-with-tax")
#   def price_with_tax(
#       product_id: Annotated[int, Path(ge=1)],
#       rate: Annotated[float, Query(ge=0, le=1)] = 0.2,
#   ):
#       for product in fake_products_db:
#           if product["id"] == product_id:
#               return {
#                   "product_id": product_id,
#                   "price": product["price"],
#                   "rate": rate,
#                   "price_with_tax": round(product["price"] * (1 + rate), 2),
#               }
#       return {"error": "not found"}
#
# EXERCISE 3
#   class ReviewIn(BaseModel):
#       product_id: int
#       rating: int
#       comment: str | None = None
#
#   @app.post("/reviews")
#   def create_review(review: ReviewIn):
#       return review.model_dump()
#
#   Rating is an int, but -3 or 500 would still be accepted. Lesson 05 adds
#   rules like "between 1 and 5" to model fields.
#
# EXERCISE 4
#   @app.get("/version-info")
#   def version_info(x_api_version: Annotated[str, Header()] = "v1"):
#       return {"api_version": x_api_version}
#
#   The default does the fallback for you: no header -> "v1".
#
# EXERCISE 5
#   @app.get("/products/by-category/{category}")
#   def products_in_category(category: Category):
#       return [p for p in fake_products_db if p["category"] == category.value]
#
#   Why no clash: routes match SEGMENT BY SEGMENT (the parts between slashes).
#   /products/{product_id} has two segments; /products/by-category/books has
#   three. They can never match the same URL, so order doesn't matter here.


if __name__ == "__main__":
    start(app, tour, checks)


print("\nNext: python 05_pydantic_models.py")

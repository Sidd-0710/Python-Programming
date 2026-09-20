"""
===============================================================================
 FASTAPI COURSE - LESSON 02: FUNCTIONS, CLASSES, DECORATORS, ASYNC
===============================================================================

Time: about 80 minutes (there's a good place for a break halfway).
Assumes: lesson 01.
Run it:  python 02_python_essentials_functions.py

This is the last purely-Python lesson. Every part maps DIRECTLY onto FastAPI
syntax you'll type in lesson 03. By the end, code like this will be readable
on sight instead of looking like magic:

    @app.get("/users/{user_id}")
    async def get_user(user_id: int, db: Session = Depends(get_db)) -> UserOut:
        ...

That line uses a DECORATOR, TYPE HINTS, a DEFAULT VALUE, and ASYNC. All four
are taught below.


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. write a function, and tell return apart from print          (PART 1)
  2. add type hints - the feature FastAPI is built on            (PART 2)
  3. give parameters defaults, and pass them by name             (PART 3)
  4. read the @decorator line you'll write in every route        (PART 4)
  5. write a class, which is what a Pydantic model is            (PART 5)
  6. catch errors, and raise your own                            (PART 6)
  7. see what async and await actually do                        (PART 7)
  8. use `with` so cleanup always happens                        (PART 8)

NEW WORDS - come back here whenever you forget one:

  function      a named, reusable block of code:  def greet(name): ...
  call          running a function, with brackets:  greet("Sidd")
  parameter     the name in the definition:  def greet(name)
  argument      the value you pass in:  greet("Sidd")
  return        hand a value BACK to the code that called the function.
                NOT the same as print(), which only shows it to a human.
  type hint     a note about what kind of value is expected:
                  def add(price: float) -> float
                Python does not enforce it. FastAPI DOES.
  default       a value used when the caller doesn't give one:  limit = 10
  keyword       passing an argument by name:  list_items(limit=5)
  argument
  decorator     a line starting with @ above a function, which wraps it with
                extra behaviour.  @app.get("/users")  is one.
  class         a blueprint that bundles data with the rules about it
  object        one thing made from a class (also called an "instance")
  attribute     a value stored on an object:  user.name
  method        a function that belongs to a class:  user.describe()
  self          inside a class, "this particular object"
  __init__      the method that runs when an object is created
  exception     an error that stops the normal flow
  raise         deliberately causing one:  raise ValueError("too big")
  try / except  run some code, and catch the error if it goes wrong
  sync          ordinary code: one thing at a time, each waiting for the last
  async         code that can PAUSE while waiting, letting other work run
  await         "pause here until this finishes, but let others run"
  context       an object used with `with`, which guarantees cleanup
  manager       happens afterwards - even if something crashes

HOW TO READ THIS FILE: read a PART, run the file, find that PART's output.
The TRY IT NOW boxes take a minute or two each - do them as you reach them.
"""

import asyncio
import time

LINE = "-" * 70


def section(title):
    print()
    print(LINE)
    print(f"  {title}")
    print(LINE)


# =============================================================================
# PART 1 — FUNCTIONS: PACKAGING UP BEHAVIOUR
# =============================================================================
section("PART 1 - FUNCTIONS")

# `def` defines a function - a named, reusable block of code.
def greet(name):
    return f"Hello, {name}!"

# Defining it does nothing yet. CALLING it (with brackets) runs it.
print(" ", greet("Sidd"))
print(" ", greet("Ana"))

# `return` hands a value BACK to whoever called the function.
# print() shows something to a human. return gives a value to your CODE.
# Confusing them is the single most common bug beginners write.

def add_tax(price, rate):
    return price * (1 + rate)

total = add_tax(100, 0.2)                   # the RETURNED value is captured
print(f"  add_tax(100, 0.2) = {total}")
print(f"  used right away   = {add_tax(50, 0.2) + 10}")

def add_tax_wrong(price, rate):
    print(price * (1 + rate))               # prints, but returns nothing

result = add_tax_wrong(100, 0.2)
print(f"  add_tax_wrong returned: {result}   <- None! print() is not return")

# In plain English: print() shows a value to a PERSON. return gives it to your
# CODE, so you can store it, add to it, or send it as a response. A route
# function that prints instead of returning sends an empty response.

# TRY IT NOW (2 minutes):
#   Write  def double(n): return n * 2  and print(double(21)).
#   Then remove the word `return` and run it again. [Without return you get
#   None - the function does the work and throws the answer away.]


# =============================================================================
# PART 2 — TYPE HINTS: THE SYNTAX FASTAPI IS BUILT ON
# =============================================================================
section("PART 2 - TYPE HINTS")

# A TYPE HINT documents what kind of value a parameter should be, and what
# the function returns. Python does NOT enforce these by itself - but
# FastAPI reads them and DOES enforce them. This single mechanism is why
# FastAPI needs so little extra configuration.

def add_tax_hinted(price: float, rate: float) -> float:
    return price * (1 + rate)

print(" ", add_tax_hinted(100, 0.2))

def describe_hinted(name: str, age: int) -> str:
    return f"{name} is {age} years old"

# The hint says age should be an int. Python does NOT check this - it will
# happily run with the wrong type, producing a silently confusing result.
print("  hint says age: int, but we pass text:")
print("   ", describe_hinted("Sidd", "twenty-two"), "  <- ran anyway, no error!")
print("  (plain Python only READS hints; FastAPI actively CHECKS and REJECTS")
print("   a bad value like this before your function ever runs - lesson 04)")

# Common type hints you'll use constantly:
def describe(name: str, age: int, height: float, is_admin: bool) -> str:
    return f"{name}, {age}, {height}m, admin={is_admin}"

print(" ", describe("Sidd", 22, 1.78, True))

# Optional / nullable: a value that might be a type, or might be None.
from typing import Optional

def find_user(user_id: int, nickname: Optional[str] = None) -> str:
    if nickname is None:
        return f"user {user_id}, no nickname given"
    return f"user {user_id}, nickname {nickname}"

print(" ", find_user(1))
print(" ", find_user(1, "sid"))

# Modern shorthand for Optional[str]:  str | None
def find_user_modern(user_id: int, nickname: str | None = None) -> str:
    return find_user(user_id, nickname)

print(" ", find_user_modern(2, "az"))

# Lists and dicts of a specific type:
def total_price(prices: list[float]) -> float:
    return sum(prices)

def user_lookup(users: dict[int, str], target_id: int) -> str | None:
    return users.get(target_id)

print(" ", total_price([9.99, 4.50, 12.00]))
print(" ", user_lookup({1: "Sidd", 2: "Ana"}, 2))

# IN FASTAPI: user_id: int in a path means FastAPI converts and validates it.
# response_model=UserOut (lesson 05) uses the SAME idea for what goes out.


# =============================================================================
# PART 3 — DEFAULT VALUES AND KEYWORD ARGUMENTS
# =============================================================================
section("PART 3 - DEFAULTS AND KEYWORDS")

# A default value makes a parameter OPTIONAL - skip it, and Python uses the
# default. This is exactly how query parameters like ?limit=10 will work.
def list_items(skip: int = 0, limit: int = 10) -> str:
    return f"showing items {skip} to {skip + limit}"

print(" ", list_items())                     # both defaults used
print(" ", list_items(20))                    # skip=20, limit still 10
print(" ", list_items(limit=5))               # skip default, limit=5 by KEYWORD
print(" ", list_items(skip=20, limit=5))      # both named - reads clearly

# ***** THE MUTABLE DEFAULT TRAP - a real, famous Python bug *****
# A list or dict as a default is created ONCE, when the function is defined,
# and then SHARED across every call that doesn't supply its own.
def add_tag_wrong(tag, tags=[]):              # DANGER - never do this
    tags.append(tag)
    return tags

print("\n  add_tag_wrong('a'):", add_tag_wrong("a"))
print("  add_tag_wrong('b'):", add_tag_wrong("b"), "  <- 'a' is still there!")

def add_tag_right(tag, tags=None):
    if tags is None:
        tags = []                             # a FRESH list every call
    tags.append(tag)
    return tags

print("  add_tag_right('a'):", add_tag_right("a"))
print("  add_tag_right('b'):", add_tag_right("b"), "  <- correct, independent")
print("  (you'll see this exact None-then-create pattern again in lesson 05)")

# TRY IT NOW (2 minutes):
#   Call  list_items(limit=3)  and  list_items(3)  and print both.
#   [list_items(limit=3) keeps skip at 0; list_items(3) sets SKIP to 3,
#   because a plain value fills the first parameter. Naming it is safer.]


# =============================================================================
# PART 4 — DECORATORS: THE @ SYNTAX
# =============================================================================
section("PART 4 - DECORATORS")

# You are about to write things like:
#     @app.get("/users")
#     def list_users(): ...
#
# @something above a function is a DECORATOR. Read it as:
#     "wrap this function with extra behaviour, using `something`"
#
# A decorator is a function that takes a function and gives back a function -
# usually one that does a bit of extra work before or after calling yours.

# (*args, **kwargs) below means "accept ANY arguments and pass them straight
# through". You don't need to write this yourself yet - it's here because a
# wrapper has to work for every function it might wrap.
def announce(original_function):
    """This IS a decorator: it takes a function, returns a new one."""
    def wrapper(*args, **kwargs):
        print(f"    -> about to call {original_function.__name__}")
        result = original_function(*args, **kwargs)
        print(f"    <- {original_function.__name__} finished")
        return result
    return wrapper

@announce
def compute_total(a, b):
    return a + b

print("  calling a decorated function:")
answer = compute_total(3, 4)
print(f"  the answer was: {answer}")

print()
print("  WITHOUT the decorator syntax, this is what @announce actually does:")
def compute_total_plain(a, b):
    return a + b
compute_total_plain = announce(compute_total_plain)     # exactly what @ does
compute_total_plain(10, 20)

print()
print("""  WHEN YOU WRITE:
      @app.get("/users/{user_id}")
      def get_user(user_id: int):
          ...
  FastAPI's decorator remembers "when a GET request arrives for
  /users/{user_id}, call this function" - it REGISTERS your function
  against a route. You never call get_user() yourself; FastAPI does,
  when a matching request arrives. This is the whole mechanism behind
  routing (lesson 03).""")


# =============================================================================
# PART 5 — CLASSES: BUNDLING DATA WITH RULES
# =============================================================================
section("PART 5 - CLASSES")

# A dictionary holds data. A CLASS bundles data together with the RULES that
# protect it, and gives the bundle a name. FastAPI's data-validation library,
# Pydantic (lesson 05), is built entirely from classes shaped like this one.

class User:
    """A blueprint for 'a user'. Nothing exists yet - this just describes one."""

    def __init__(self, name, email, is_admin=False):
        # __init__ runs automatically when you create a User.
        # `self` means "this particular user being made".
        self.name = name
        self.email = email
        self.is_admin = is_admin

    def describe(self):
        # A METHOD: a function that belongs to the class, and can use self.
        if self.is_admin:
            role = "admin"
        else:
            role = "member"
        return f"{self.name} <{self.email}> ({role})"

# Creating an OBJECT (an "instance") from the class:
sidd = User("Sidd", "sidd@example.com", is_admin=True)
ana = User("Ana", "ana@example.com")

print(" ", sidd.describe())
print(" ", ana.describe())
print("  sidd.name  :", sidd.name)
print("  ana.is_admin:", ana.is_admin)

# Two DIFFERENT users - each object keeps its own data:
sidd.name = "Siddheshwar"
print("  after renaming sidd, ana.name is still:", ana.name)

# CLASSES WITH TYPE HINTS - this shape is used EVERYWHERE in FastAPI:
class Product:
    def __init__(self, name: str, price: float, in_stock: bool = True):
        self.name = name
        self.price = price
        self.in_stock = in_stock

    def price_with_tax(self, rate: float = 0.2) -> float:
        return round(self.price * (1 + rate), 2)

desk = Product("Standing Desk", 349.99)
print(f"\n  {desk.name} with tax: {desk.price_with_tax()}")

print("""
  IN FASTAPI: you will not usually write __init__ by hand. Pydantic's
  BaseModel (lesson 05) generates it for you from a much shorter class:

      class ProductOut(BaseModel):
          name: str
          price: float
          in_stock: bool = True

  That class alone gives you validation, JSON conversion, AND documentation.
  Understanding the User class above is what makes that shortcut make sense.""")


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. Functions, type hints, defaults, decorators and
#  classes are the four things every FastAPI route is built from. After the
#  break: errors, async, and `with`.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 6 — EXCEPTIONS: HANDLING (AND RAISING) ERRORS
# =============================================================================
section("PART 6 - EXCEPTIONS")

# When something goes wrong, Python RAISES an exception, which stops the
# current code and looks for a handler. try/except catches it.

def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None                            # a graceful fallback

print("  divide(10, 2) =", divide(10, 2))
print("  divide(10, 0) =", divide(10, 0), "  <- caught, no crash")

# You can also RAISE your own exceptions - refusing to continue when
# something is wrong, with a message explaining why.
def withdraw(balance, amount):
    if amount > balance:
        raise ValueError(f"cannot withdraw {amount}, balance is only {balance}")
    return balance - amount

try:
    withdraw(100, 500)
except ValueError as error:
    print("  caught:", error)

print("""
  IN FASTAPI: you will constantly write

      if user is None:
          raise HTTPException(status_code=404, detail="User not found")

  HTTPException is a special exception FastAPI recognises: when your code
  raises one, FastAPI catches it FOR YOU and turns it straight into the
  matching HTTP response - status code, JSON body, done. Lesson 06 covers
  this fully.""")


# =============================================================================
# PART 7 — SYNC VS ASYNC: THE PART THAT LOOKS NEW
# =============================================================================
section("PART 7 - WHY async EXISTS")

# THE PROBLEM: a normal ("synchronous") function that waits for something
# slow - a database, another website - blocks EVERYTHING else on that
# program while it waits. One slow user could freeze your whole server.

def slow_task_sync(name, seconds):
    print(f"    {name}: starting, will take {seconds}s")
    time.sleep(seconds)                        # pretend to wait for a database
    print(f"    {name}: done")

print("  SYNC: each task fully finishes before the next one starts.")
start = time.perf_counter()
slow_task_sync("task A", 0.3)
slow_task_sync("task B", 0.3)
print(f"  total time: {time.perf_counter() - start:.2f}s  (0.3 + 0.3 - they add up)")

# THE FIX: async lets Python work on something ELSE while waiting, then come
# back. It doesn't make one task faster - it lets MANY tasks overlap their
# waiting time.

async def slow_task_async(name, seconds):
    print(f"    {name}: starting, will take {seconds}s")
    await asyncio.sleep(seconds)                # "wait here, but let others run"
    print(f"    {name}: done")

async def run_two_at_once():
    start = time.perf_counter()
    # asyncio.gather runs both tasks CONCURRENTLY - they overlap their waits.
    await asyncio.gather(
        slow_task_async("task A", 0.3),
        slow_task_async("task B", 0.3),
    )
    print(f"  total time: {time.perf_counter() - start:.2f}s  (they overlapped!)")

print("\n  ASYNC: both tasks wait AT THE SAME TIME.")
asyncio.run(run_two_at_once())                  # this is how you start async code

# TRY IT NOW (2 minutes):
#   Change both 0.3 values in run_two_at_once() to 1, and run the file.
#   [Still about 1 second in total, not 2 - the two waits overlap. That is
#   the whole point of async, and why FastAPI can serve many users at once.]

print("""
  THE VOCABULARY:
    async def    marks a function as able to pause and let others run
    await        "pause HERE until this finishes, but let other work happen
                 in the meantime" - only usable inside an async def
    asyncio.run  starts the whole async system running (FastAPI/uvicorn do
                 this for you - you'll never write it yourself in a real app)

  WHY THIS MATTERS FOR A BACKEND: your API will spend most of its time
  WAITING - for a database query, for a call to another service, for an AI
  model. During that wait, async lets your server handle OTHER users'
  requests instead of sitting idle. This is the single biggest reason
  FastAPI can handle many more users per second than an old-style framework.

  IN FASTAPI: every route CAN be written as
      async def get_user(user_id: int):
          ...
  You'll be told exactly when `async` and `await` are needed versus when a
  normal `def` is fine - lesson 03 covers the rule in one paragraph.""")


# =============================================================================
# PART 8 — CONTEXT MANAGERS: THE with STATEMENT
# =============================================================================
section("PART 8 - with (CONTEXT MANAGERS)")

# `with` guarantees CLEANUP happens, even if something goes wrong inside it.
# You've likely seen it for files:
#     with open("data.txt") as f:
#         contents = f.read()
#     # the file is closed automatically here, even if read() had crashed

class DatabaseConnection:
    """A pretend database connection, to show the with/without difference."""

    def __enter__(self):
        print("    connection opened")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("    connection closed")          # ALWAYS runs, error or not

    def query(self, sql):
        print(f"    running: {sql}")

print("  using `with` - cleanup is guaranteed:")
with DatabaseConnection() as db:
    db.query("SELECT * FROM users")
print("  (closed automatically, even though nothing went wrong here)")

print("\n  and even when something DOES go wrong inside:")
try:
    with DatabaseConnection() as db:
        db.query("SELECT * FROM users")
        raise RuntimeError("pretend crash mid-query")
except RuntimeError:
    print("  caught the crash - but notice 'connection closed' still printed above")

print("""
  IN FASTAPI: database sessions (lesson 08) are opened and closed using
  exactly this pattern, so a crash halfway through a request can never leave
  a connection dangling open.""")


# =============================================================================
# PART 9 — COMMON MISTAKES
# =============================================================================
section("PART 9 - COMMON MISTAKES")

# MISTAKE 1: forgetting to call a function.
#     greet          <- this is the function ITSELF, not its result
#     greet("Sidd")  <- this CALLS it

# MISTAKE 2: using a mutable default value ([] or {}). Covered in PART 3.

# MISTAKE 3: confusing print() and return. Covered in PART 1.

# MISTAKE 4: forgetting `self` as the first parameter of a method.
#     def describe():        <- missing self, will crash when called
#     def describe(self):    <- correct

# MISTAKE 5: using `await` outside an `async def`.
#     def normal_function():
#         await something()      <- SyntaxError
#   await only works inside a function itself marked async def.

# MISTAKE 6: thinking async makes ONE task faster. It doesn't - task A still
#   takes 0.3s. It lets task B's 0.3s happen AT THE SAME TIME instead of after.

# MISTAKE 7: type hints that Python doesn't enforce, then being surprised.
#   def f(x: int): ...   still accepts f("hello") in plain Python. FastAPI
#   is what makes hints strict, by checking values before your code runs.
print("  (see the comments above this section for the full list)")


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * def makes a function; calling it needs brackets. return hands a value
#     back to your code - print() only shows it to a person.
#   * Type hints (price: float) document what's expected. Python ignores them;
#     FastAPI reads them and rejects bad input before your code runs.
#   * A default value makes a parameter optional - which is exactly how query
#     parameters like ?limit=10 work. Never use [] or {} as a default.
#   * A decorator wraps a function with extra behaviour. @app.get("/users")
#     registers your function so FastAPI calls it when that request arrives.
#   * A class bundles data with its rules. Pydantic models (lesson 05) are
#     classes with the __init__ written for you.
#   * raise stops everything with an error; try/except catches one. In FastAPI
#     you'll raise HTTPException and it becomes an HTTP response.
#   * async/await lets one program wait for many slow things at once. It makes
#     nothing faster on its own - it stops waiting from blocking everything.
#   * with guarantees cleanup, even if the code inside it crashes.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. A function prints its result but doesn't return it. You write
#       total = f(5). What is total?
#   Q2. Does plain Python stop you passing "twenty" to  def f(age: int)?
#   Q3. What's wrong with  def add_tag(tag, tags=[]):  ?
#   Q4. What does @app.get("/users") actually DO to the function under it?
#   Q5. Two tasks each wait 1 second. Run with asyncio.gather, how long?
#
# ANSWERS
#   A1. None. Without return, nothing comes back.
#   A2. No - hints are only notes in plain Python. FastAPI is what enforces
#       them, replying 422 before your function runs.
#   A3. The list is made ONCE and shared by every call, so it keeps growing.
#       Use  tags=None  and create a new list inside.
#   A4. It registers it: "when a GET request for /users arrives, call this".
#       You never call the function yourself.
#   A5. About 1 second - the waits overlap.


# =============================================================================
# EXERCISES
# =============================================================================
#
# Do the WARM-UPS first - each practises ONE idea from this lesson.
#
# WARM-UP A (easy) — Your own function
#   Write  def double(n: int) -> int  that returns n * 2, and print
#   double(21).
#
# WARM-UP B (easy) — A default value
#   Write  def greet(name: str, greeting: str = "Hello") -> str  returning
#   f"{greeting}, {name}!". Call it once with one argument and once with two.
#
# WARM-UP C (easy) — A tiny class
#   Write a class Book with __init__(self, title, year) and a method
#   summary(self) returning f"{self.title} ({self.year})". Make one and print
#   its summary.
#
# EXERCISE 1 (easy) — Basic function
#   Write fahrenheit_to_celsius(f: float) -> float returning (f - 32) * 5 / 9.
#   Call it for 32, 98.6 and 212, printing each result to 1 decimal place.
#
# EXERCISE 2 (easy) — Defaults and keywords
#   Write greet_user(name: str, greeting: str = "Hello", excited: bool = False)
#   -> str  that returns f"{greeting}, {name}!" or with "!!!" if excited=True.
#   Call it four different ways, using keyword arguments for at least two.
#
# EXERCISE 3 (medium) — Fix the mutable default
#   Write collect_error(message: str, errors=[]) -> list, THEN show the bug by
#   calling it three times and printing the result each time. Then fix it
#   with the None pattern and show it's fixed.
#
# EXERCISE 4 (challenge) — A decorator that times things
#   Write a decorator @timed that prints how long the wrapped function took
#   (use time.perf_counter(), like PART 7). Apply it to a function that sleeps
#   for a random amount of time between 0.1 and 0.3 seconds.
#
# EXERCISE 5 (medium) — A class with a rule
#   Write a class BankAccount with __init__(self, owner, balance=0), a
#   deposit(amount) method, and a withdraw(amount) method that RAISES
#   ValueError if amount > balance. Create one account, deposit, withdraw
#   successfully, then attempt an over-withdrawal and catch the error.
#
# EXERCISE 6 (medium) — Two classes together
#   Write a class Order with __init__(self, id, items: list[str]) and a
#   total_items(self) -> int method. Create three orders and print, for each,
#   "Order <id>: <n> items".
#
# EXERCISE 7 (challenge) — Async practice
#   Write three async functions fetch_a, fetch_b, fetch_c, each `await
#   asyncio.sleep(...)` for a different duration (0.1, 0.2, 0.3) then return a
#   string. Run all three with asyncio.gather, print how long it took, and
#   print all three results. It should take about 0.3s, not 0.6s.
#
# EXERCISE 8 (challenge) — A context manager
#   Write a class Timer usable as:
#       with Timer("my task"):
#           time.sleep(0.2)
#   which prints "my task took 0.20s" when the with block ends. (__enter__
#   should record the start time; __exit__ should compute and print elapsed.)

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   def double(n: int) -> int:
#       return n * 2
#   print(double(21))                  # 42
#
# WARM-UP B
#   def greet(name: str, greeting: str = "Hello") -> str:
#       return f"{greeting}, {name}!"
#   print(greet("Sidd"))               # Hello, Sidd!
#   print(greet("Ana", "Welcome"))     # Welcome, Ana!
#
# WARM-UP C
#   class Book:
#       def __init__(self, title, year):
#           self.title = title
#           self.year = year
#
#       def summary(self):
#           return f"{self.title} ({self.year})"
#   print(Book("Dune", 1965).summary())     # Dune (1965)
#
# EXERCISE 1
#   def fahrenheit_to_celsius(f: float) -> float:
#       return (f - 32) * 5 / 9
#   for temp in (32, 98.6, 212):
#       print(f"{temp}F = {fahrenheit_to_celsius(temp):.1f}C")
#
# EXERCISE 2
#   def greet_user(name: str, greeting: str = "Hello", excited: bool = False) -> str:
#       punctuation = "!!!" if excited else "!"
#       return f"{greeting}, {name}{punctuation}"
#   print(greet_user("Sidd"))
#   print(greet_user("Ana", greeting="Hi"))
#   print(greet_user("Marco", excited=True))
#   print(greet_user(name="Priya", greeting="Welcome", excited=True))
#
# EXERCISE 3
#   def collect_error(message, errors=[]):
#       errors.append(message)
#       return errors
#   print(collect_error("first"))    # ['first']
#   print(collect_error("second"))   # ['first', 'second']  <- the bug
#   print(collect_error("third"))    # ['first', 'second', 'third']
#
#   def collect_error_fixed(message, errors=None):
#       if errors is None:
#           errors = []
#       errors.append(message)
#       return errors
#   print(collect_error_fixed("only"))   # ['only'] every time
#   print(collect_error_fixed("only"))   # ['only'] - independent
#
# EXERCISE 4
#   import random
#   def timed(func):
#       def wrapper(*args, **kwargs):
#           start = time.perf_counter()
#           result = func(*args, **kwargs)
#           print(f"{func.__name__} took {time.perf_counter() - start:.3f}s")
#           return result
#       return wrapper
#   @timed
#   def random_wait():
#       time.sleep(random.uniform(0.1, 0.3))
#   random_wait()
#
# EXERCISE 5
#   class BankAccount:
#       def __init__(self, owner, balance=0):
#           self.owner = owner
#           self.balance = balance
#       def deposit(self, amount):
#           self.balance += amount
#       def withdraw(self, amount):
#           if amount > self.balance:
#               raise ValueError(f"insufficient funds: has {self.balance}, wants {amount}")
#           self.balance -= amount
#   account = BankAccount("Sidd", 100)
#   account.deposit(50)
#   account.withdraw(30)
#   print(account.balance)          # 120
#   try:
#       account.withdraw(1000)
#   except ValueError as error:
#       print("blocked:", error)
#
# EXERCISE 6
#   class Order:
#       def __init__(self, id, items):
#           self.id = id
#           self.items = items
#       def total_items(self):
#           return len(self.items)
#   orders = [Order(1, ["book"]), Order(2, ["pen", "pencil"]), Order(3, [])]
#   for order in orders:
#       print(f"Order {order.id}: {order.total_items()} items")
#
# EXERCISE 7
#   async def fetch_a():
#       await asyncio.sleep(0.1)
#       return "A done"
#   async def fetch_b():
#       await asyncio.sleep(0.2)
#       return "B done"
#   async def fetch_c():
#       await asyncio.sleep(0.3)
#       return "C done"
#   async def main():
#       start = time.perf_counter()
#       results = await asyncio.gather(fetch_a(), fetch_b(), fetch_c())
#       print(f"took {time.perf_counter() - start:.2f}s")
#       print(results)
#   asyncio.run(main())
#
# EXERCISE 8
#   class Timer:
#       def __init__(self, label):
#           self.label = label
#       def __enter__(self):
#           self.start = time.perf_counter()
#           return self
#       def __exit__(self, exc_type, exc_value, traceback):
#           elapsed = time.perf_counter() - self.start
#           print(f"{self.label} took {elapsed:.2f}s")
#   with Timer("my task"):
#       time.sleep(0.2)


print()
print("=" * 70)
print("  Lesson 02 complete. Next: python 03_first_api.py")
print("  From here on, every lesson runs your OWN API and talks to it.")
print("=" * 70)

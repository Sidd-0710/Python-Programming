"""
===============================================================================
 LESSON 10 — FUNCTIONS: NAMING AND REUSING BEHAVIOUR
===============================================================================

Time: about 85 minutes.
Assumes: lessons 01-09.


-------------------------------------------------------------------------------
 THEORY: FROM SCRIPT TO SOFTWARE
-------------------------------------------------------------------------------

Everything you've written so far has been a SCRIPT: a single flow, top to
bottom. Functions are what turn scripts into software.

A function is a named, reusable chunk of behaviour. You define it once, then
call it by name as many times as you like, with different inputs.

You have been USING functions since lesson 00: print(), len(), sum(), int().
Now you'll write your own.

THINK OF A FUNCTION AS A MACHINE:

        inputs  ->  [ THE MACHINE ]  ->  output
      (arguments)     (the body)        (return value)

A coffee machine takes beans and water, does something internally, and produces
coffee. You don't need to know how it works inside to use it. That last point
is the whole value proposition: a function lets you stop thinking about HOW
and start thinking about WHAT.


THE FOUR REASONS FUNCTIONS MATTER:

  1. NO REPETITION   Write the tax calculation once. If the rate changes, you
                     edit one place instead of hunting through 40 files.

  2. NAMING          `calculate_shipping(weight, country)` tells a reader what
                     is happening. Twelve loose lines of arithmetic do not.
                     A good function name is documentation that can't rot.

  3. TESTABILITY     You can test a function in isolation. You cannot
                     meaningfully test "lines 40-80 of my script".

  4. MANAGING SIZE   Human working memory holds about seven things. Functions
                     let you collapse fifty lines into one named idea, so you
                     can reason about a big program without holding it all in
                     your head at once.
"""

LINE = "-" * 70


# =============================================================================
# PART 1 — DEFINING AND CALLING
# =============================================================================
print(LINE)
print("PART 1 — YOUR FIRST FUNCTIONS")
print(LINE)

# THE SHAPE:
#
#     def function_name(parameters):     <- `def`, a name, brackets, a COLON
#         """A docstring explaining it."""
#         body
#         return something               <- optional
#
# Defining a function does NOT run it. It just teaches Python the recipe. The
# body runs only when you CALL it: function_name(arguments)

def greet():
    """Print a fixed greeting. Takes nothing, returns nothing."""
    print("  Hello from inside a function!")

greet()             # this is the call - now the body runs
greet()             # call it as often as you like
print()


# --- Parameters: giving the function inputs ---
def greet_person(name):
    """Greet someone by name."""
    print(f"  Hello, {name}!")

greet_person("Sidd")
greet_person("Ana")
print()

# VOCABULARY (people use these loosely, but the distinction is useful):
#   PARAMETER - the name in the definition       -> `name`
#   ARGUMENT  - the actual value you pass in     -> "Sidd"


# --- return: giving a value back ---
# print() SHOWS something to a human. return HANDS A VALUE BACK to your code.
# They are completely different, and confusing them is the #1 function bug.

def add(a, b):
    """Return the sum of two numbers."""
    return a + b

result = add(3, 4)              # the function's value is captured
print(f"  add(3, 4) returned {result}")
print(f"  and it can be used in expressions: {add(3, 4) * 10}")
print(f"  or nested: {add(add(1, 2), add(3, 4))}")
print()


def add_and_print(a, b):
    """Print the sum. Returns nothing useful."""
    print(f"  the sum is {a + b}")

value = add_and_print(3, 4)
print(f"  add_and_print returned: {value}  <- None! It printed but gave nothing back")

# THE RULE: if you want to USE the result, return it. Only print inside a
# function when the function's whole purpose is displaying something.
# A function that calculates AND prints is harder to reuse - you can't put its
# answer in a file or a web page.
print()

# `return` also EXITS the function immediately - nothing after it runs:
def check_age(age):
    if age < 0:
        return "invalid"        # exits here
    if age < 18:
        return "minor"          # or here
    return "adult"              # or here

for test_age in (-5, 12, 30):
    print(f"  check_age({test_age}) -> {check_age(test_age)}")
print()

# A function with no return statement returns None automatically.


# =============================================================================
# PART 2 — ARGUMENTS IN DEPTH
# =============================================================================
print(LINE)
print("PART 2 — ARGUMENTS")
print(LINE)

# POSITIONAL arguments are matched by order:
def describe(name, age, city):
    return f"{name}, {age}, from {city}"

print(" ", describe("Sidd", 22, "Mumbai"))
print(" ", describe(22, "Sidd", "Mumbai"), "  <- order matters! nonsense result")

# KEYWORD arguments are matched by name, so order stops mattering and the call
# becomes self-documenting:
print(" ", describe(city="Lisbon", name="Ana", age=30))

# You can mix, but positional ones must come first:
print(" ", describe("Marco", city="Rome", age=41))
print()

# DEFAULT VALUES make a parameter optional:
def make_tag(text, tag="p", css_class=None):
    """Build an HTML tag. Only `text` is required."""
    class_part = f' class="{css_class}"' if css_class else ""
    return f"<{tag}{class_part}>{text}</{tag}>"

print(" ", make_tag("Hello"))
print(" ", make_tag("Title", "h1"))
print(" ", make_tag("Warning", "div", "alert"))
print(" ", make_tag("Styled", css_class="highlight"))    # skip the middle one
print()

# ***** THE MUTABLE DEFAULT TRAP *****
# This is the most notorious gotcha in Python. Read it twice.

def broken_add_item(item, basket=[]):           # NEVER DO THIS
    basket.append(item)
    return basket

print("  broken_add_item('a'):", broken_add_item("a"))
print("  broken_add_item('b'):", broken_add_item("b"), "<- 'a' is still there!")

# WHY: the default value is created ONCE, when the function is DEFINED, not
# each time it's called. So every call shares the same list.

def fixed_add_item(item, basket=None):          # THE CORRECT PATTERN
    if basket is None:
        basket = []                             # a fresh list per call
    basket.append(item)
    return basket

print("  fixed_add_item('a') :", fixed_add_item("a"))
print("  fixed_add_item('b') :", fixed_add_item("b"), "<- correct")
# RULE: default values must be immutable (None, 0, "", False). Never [], {}
# or set().
print()

# *args - "accept any number of positional arguments", collected into a tuple:
def total(*numbers):
    """Sum however many numbers you pass."""
    return sum(numbers)

print("  total(1, 2)        :", total(1, 2))
print("  total(1, 2, 3, 4, 5):", total(1, 2, 3, 4, 5))
print("  total()            :", total())

# **kwargs - "accept any number of keyword arguments", collected into a dict:
def create_user(name, **extra_fields):
    user = {"name": name}
    user.update(extra_fields)
    return user

print("  ", create_user("Sidd", age=22, city="Mumbai", admin=True))
print()

# You've seen these in action already - print() itself is defined roughly as
# `def print(*values, sep=" ", end="\n")`, which is exactly why it accepts any
# number of items plus those optional keyword settings.


# =============================================================================
# PART 3 — SCOPE: WHERE VARIABLES LIVE
# =============================================================================
print(LINE)
print("PART 3 — SCOPE")
print(LINE)

# Variables created INSIDE a function exist only inside it. They're created
# when the call starts and destroyed when it ends. This is a feature: it means
# a function can't accidentally trample a variable somewhere else.

message = "I am global"            # defined at the file level

def show_scope():
    message = "I am local"         # a DIFFERENT variable that shadows the global
    print("  inside the function:", message)

show_scope()
print("  outside the function:", message, "<- unchanged")
print()

# Functions CAN read global variables they don't reassign:
TAX_RATE = 0.2                     # a module-level constant

def add_tax(amount):
    return amount * (1 + TAX_RATE)     # reading the global is fine

print("  100 with tax:", add_tax(100))
print()

# But MODIFYING a global from inside a function requires the `global` keyword,
# and you should almost always avoid needing it:
counter = 0

def increment_badly():
    global counter                  # "I really mean the outer one"
    counter += 1

increment_badly()
increment_badly()
print("  counter after 2 calls:", counter)

# WHY AVOID `global`: a function that silently changes outside state is hard to
# test, hard to reuse and hard to reason about. Prefer taking input as
# parameters and handing results back with return:
def increment_well(value):
    return value + 1

better_counter = 0
better_counter = increment_well(better_counter)
better_counter = increment_well(better_counter)
print("  better_counter:", better_counter)
print()

# CAREFUL - mutable arguments CAN be changed by a function, because the
# function receives the same object, not a copy (the lesson 06 name-tag idea):
def append_item_in_place(target_list):
    target_list.append("added inside the function")

my_list = ["original"]
append_item_in_place(my_list)
print("  the caller's list was modified:", my_list)

# That's sometimes exactly what you want, but it must be DELIBERATE. If in
# doubt, take a copy inside the function and return the new version.
print()


# =============================================================================
# PART 4 — DOCSTRINGS AND GOOD FUNCTION DESIGN
# =============================================================================
print(LINE)
print("PART 4 — WRITING GOOD FUNCTIONS")
print(LINE)

def calculate_shipping(weight_kg, country="UK", express=False):
    """Calculate the shipping cost for a parcel.

    Args:
        weight_kg: Parcel weight in kilograms.
        country:   Destination country code. "UK" is domestic.
        express:   Whether to use the next-day service.

    Returns:
        The cost as a float, rounded to 2 decimal places.
    """
    base = 3.99 if country == "UK" else 12.99
    per_kg = 0.75 if country == "UK" else 2.50
    cost = base + weight_kg * per_kg
    if express:
        cost *= 1.8
    return round(cost, 2)

# The docstring is the text right after the `def` line. It's not a comment -
# Python stores it, and tools read it:
print("  help text:", calculate_shipping.__doc__.splitlines()[0])
print("  UK, 2kg          :", calculate_shipping(2))
print("  France, 2kg      :", calculate_shipping(2, "FR"))
print("  France, 2kg, fast:", calculate_shipping(2, "FR", express=True))
print()

# THE RULES OF A GOOD FUNCTION:
#
#  1. DO ONE THING. If you need "and" to describe it, split it in two.
#  2. NAME IT WITH A VERB. calculate_total(), send_email(), parse_date().
#     Names like `data()` or `process()` tell you nothing.
#  3. KEEP IT SHORT. If it doesn't fit on your screen, it's probably doing too
#     much. 5-20 lines is typical.
#  4. FEW PARAMETERS. More than about four is a sign that some of them belong
#     together in a dict or an object (lesson 16).
#  5. RETURN, DON'T PRINT (unless displaying IS the job).
#  6. NO SURPRISES. A function called get_user() should not delete anything.


# =============================================================================
# PART 5 — FUNCTIONS AS VALUES, AND lambda
# =============================================================================
print(LINE)
print("PART 5 — FUNCTIONS ARE VALUES TOO")
print(LINE)

# A function name without brackets is the function ITSELF. With brackets, it's
# a call. This distinction unlocks a lot of Python.

def shout(text):
    return text.upper() + "!"

print("  shout       ->", shout)             # the function object
print("  shout('hi') ->", shout("hi"))       # the result of calling it

# Because functions are values, you can put them in variables and collections:
my_function = shout
print("  called via another name:", my_function("hello"))

operations = {
    "upper": str.upper,
    "lower": str.lower,
    "title": str.title,
}
for name, operation in operations.items():
    print(f"  {name:<6} -> {operation('hello world')}")
print()

# And you can PASS them to other functions. That's what `key=` has been doing
# all along in sorted():
words = ["banana", "Apple", "cherry"]
print("  sorted(key=str.lower):", sorted(words, key=str.lower))
print("  sorted(key=len)      :", sorted(words, key=len))
print()

# lambda: a small, unnamed function written inline.
#     lambda arguments: expression
# It can only be ONE expression, and it returns it automatically.

double = lambda x: x * 2                # legal but pointless - just use def
print("  double(5):", double(5))

# Where lambda genuinely earns its place - a one-off key function:
people = [("Sidd", 22), ("Ana", 30), ("Marco", 25)]
print("  by age  :", sorted(people, key=lambda person: person[1]))
print("  by name :", sorted(people, key=lambda person: person[0]))

orders = [
    {"item": "widget", "price": 9.99},
    {"item": "gadget", "price": 2.50},
]
print("  cheapest:", min(orders, key=lambda order: order["price"]))

# RULE: use lambda ONLY for tiny throwaway expressions passed to another
# function. If it needs a name or more than one line, write a proper def.
print()


# =============================================================================
# PART 6 — REAL EXAMPLE: REFACTORING A SCRIPT INTO FUNCTIONS
# =============================================================================
print(LINE)
print("PART 6 — REAL EXAMPLE: A REPORT BUILT FROM FUNCTIONS")
print(LINE)

# The same sales analysis from lesson 09, but decomposed. Notice how the main
# flow at the bottom now reads like a summary of what the program does.

SALES = [
    {"region": "EU", "rep": "Ana",   "amount": 249.99, "status": "paid"},
    {"region": "EU", "rep": "Marco", "amount": 1200.00, "status": "pending"},
    {"region": "AS", "rep": "Sidd",  "amount": 89.50,  "status": "paid"},
    {"region": "AS", "rep": "Sidd",  "amount": 330.00, "status": "paid"},
    {"region": "US", "rep": "Zara",  "amount": 675.25, "status": "refunded"},
    {"region": "EU", "rep": "Ana",   "amount": 45.00,  "status": "paid"},
]


def only_paid(sales):
    """Return just the sales with a 'paid' status."""
    return [sale for sale in sales if sale["status"] == "paid"]


def total_by(sales, field):
    """Sum the amounts, grouped by any field name. Returns a dict."""
    totals = {}
    for sale in sales:
        key = sale[field]
        totals[key] = totals.get(key, 0) + sale["amount"]
    return totals


def format_money(amount):
    """One place that decides how money looks. Change it here, change it once."""
    return f"{amount:>12,.2f}"


def print_table(title, totals):
    """Display a dict of name -> amount as a sorted table."""
    print(f"\n  {title}")
    print(f"  {'-' * 24}")
    for name, amount in sorted(totals.items(), key=lambda pair: pair[1], reverse=True):
        print(f"  {name:<10}{format_money(amount)}")
    print(f"  {'-' * 24}")
    print(f"  {'TOTAL':<10}{format_money(sum(totals.values()))}")


# The main flow - six lines that describe the whole program.
paid = only_paid(SALES)
print(f"  {len(paid)} paid of {len(SALES)} total sales")
print_table("Revenue by region", total_by(paid, "region"))
print_table("Revenue by rep", total_by(paid, "rep"))

# Notice: total_by() didn't need to know anything about regions or reps. It was
# written once and reused for both. That reuse is the whole point.
print()


# =============================================================================
# PART 7 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 7 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: forgetting to call it.
#     greet          <- does nothing, it's just the function object
#     greet()        <- calls it
#   If "nothing happened", check for missing brackets first.

# MISTAKE 2: printing when you should return. The function seems to work, then
#   you discover you can't use its answer anywhere.

# MISTAKE 3: forgetting that return exits immediately.
def wrong_sum(numbers):
    for n in numbers:
        return n            # returns on the FIRST item and stops
def right_sum(numbers):
    total = 0
    for n in numbers:
        total += n
    return total            # returns AFTER the loop
print("  wrong_sum:", wrong_sum([1, 2, 3]), " right_sum:", right_sum([1, 2, 3]))

# MISTAKE 4: mutable default arguments. Covered in PART 2. Use None.

# MISTAKE 5: calling a function before defining it.
#   Python reads top to bottom - the `def` must run before the call. (Inside
#   another function is fine, because that body doesn't run until called.)

# MISTAKE 6: too many responsibilities in one function. If it fetches data,
#   validates it, calculates and prints, split it into four.

# MISTAKE 7: shadowing built-ins with parameter names.
#     def process(list, sum):      # breaks list() and sum() inside the function
#   Use `items` and `total`.

# MISTAKE 8: a wrong number of arguments.
#     add(1)       -> TypeError: add() missing 1 required positional argument
#   The error tells you exactly which one. Read it and count.
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# EXERCISE 1 — Basics
#   Write celsius_to_fahrenheit(celsius) that RETURNS the converted value.
#   Call it in a loop for -10, 0, 21.5, 37 and print a neat two-column table.
#
# EXERCISE 2 — Defaults
#   Write greet(name, greeting="Hello", punctuation="!") returning a greeting
#   string. Call it four ways: name only, custom greeting, custom punctuation
#   via keyword, and everything specified.
#
# EXERCISE 3 — Validation function
#   Write is_valid_password(password) returning a (bool, reason) tuple.
#   Rules: at least 8 characters, at least one digit, at least one letter, and
#   not in a small list of banned passwords. Test it with 5 different inputs.
#
# EXERCISE 4 — Statistics toolkit
#   Write three functions: mean(numbers), median(numbers), mode(numbers).
#   Each returns a value. Handle the empty-list case sensibly (return None).
#   Then write describe(numbers) that uses all three and returns a dict.
#
# EXERCISE 5 — Refactor an old lesson
#   Take your log-analyser code from lesson 07 PART 8 and split it into:
#     parse_line(line) -> dict
#     count_levels(lines) -> dict
#     find_errors(lines) -> list
#   Then write a main flow of 4-5 lines that calls them.
#
# EXERCISE 6 — Word tools with *args
#   Write longest_word(*words) that returns the longest of however many words
#   are passed. Then write it again taking a single list, and consider which
#   interface you prefer and why.
#
# EXERCISE 7 — A function that takes a function
#   Write apply_to_all(items, operation) that returns a new list with
#   `operation` applied to every item. Call it with a lambda that doubles
#   numbers, then with str.upper on a list of words.
#
# EXERCISE 8 — Find the bug
#   Explain why this always returns the same list, then fix it:
#       def collect(item, results=[]):
#           results.append(item)
#           return results

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   def celsius_to_fahrenheit(celsius):
#       """Convert Celsius to Fahrenheit."""
#       return celsius * 9 / 5 + 32
#   for c in (-10, 0, 21.5, 37):
#       print(f"{c:>7.1f}C = {celsius_to_fahrenheit(c):>7.1f}F")
#
# EXERCISE 2
#   def greet(name, greeting="Hello", punctuation="!"):
#       return f"{greeting}, {name}{punctuation}"
#   print(greet("Sidd"))
#   print(greet("Sidd", "Hi"))
#   print(greet("Sidd", punctuation="?"))
#   print(greet("Sidd", "Good morning", "."))
#
# EXERCISE 3
#   BANNED = {"password", "12345678", "letmein1"}
#   def is_valid_password(password):
#       if len(password) < 8:
#           return False, "too short"
#       if password in BANNED:
#           return False, "too common"
#       if not any(c.isdigit() for c in password):
#           return False, "needs a digit"
#       if not any(c.isalpha() for c in password):
#           return False, "needs a letter"
#       return True, "ok"
#   for pw in ["short", "password", "12345678", "hunter2024", "abcdefgh"]:
#       print(pw, is_valid_password(pw))
#
# EXERCISE 4
#   def mean(numbers):
#       return sum(numbers) / len(numbers) if numbers else None
#   def median(numbers):
#       if not numbers:
#           return None
#       ordered = sorted(numbers)
#       mid = len(ordered) // 2
#       if len(ordered) % 2 == 1:
#           return ordered[mid]
#       return (ordered[mid - 1] + ordered[mid]) / 2
#   def mode(numbers):
#       if not numbers:
#           return None
#       counts = {}
#       for n in numbers:
#           counts[n] = counts.get(n, 0) + 1
#       return max(counts, key=counts.get)
#   def describe(numbers):
#       return {"mean": mean(numbers), "median": median(numbers),
#               "mode": mode(numbers), "count": len(numbers)}
#   print(describe([1, 2, 2, 3, 9]))
#
# EXERCISE 5
#   def parse_line(line):
#       date, time, level, message = line.split(None, 3)
#       return {"date": date, "time": time, "level": level, "message": message}
#   def count_levels(lines):
#       counts = {}
#       for line in lines:
#           level = parse_line(line)["level"]
#           counts[level] = counts.get(level, 0) + 1
#       return counts
#   def find_errors(lines):
#       return [parse_line(l) for l in lines if parse_line(l)["level"] == "ERROR"]
#
# EXERCISE 6
#   def longest_word(*words):
#       return max(words, key=len) if words else None
#   print(longest_word("a", "abc", "ab"))
#   def longest_in_list(words):
#       return max(words, key=len) if words else None
#   # The list version is usually better: you normally HAVE a list already,
#   # and *args forces callers to write longest_word(*my_list).
#
# EXERCISE 7
#   def apply_to_all(items, operation):
#       return [operation(item) for item in items]
#   print(apply_to_all([1, 2, 3], lambda n: n * 2))
#   print(apply_to_all(["a", "b"], str.upper))
#
# EXERCISE 8
#   The default list is created once at definition time and shared by every
#   call, so items accumulate across calls. Fix:
#       def collect(item, results=None):
#           if results is None:
#               results = []
#           results.append(item)
#           return results


print("=" * 70)
print("Lesson 10 complete. Next: 11_comprehensions.py")
print("=" * 70)

"""
===============================================================================
 LESSON 05 — CONDITIONALS: MAKING DECISIONS
===============================================================================

Time: about 60 minutes.
Assumes: lessons 01-04.


-------------------------------------------------------------------------------
 THEORY: THE FIRST TIME YOUR CODE STOPS BEING A LIST
-------------------------------------------------------------------------------

Until now your programs have been recipes: line 1, then line 2, then line 3.
Every run identical. Conditionals change that. They let a program CHOOSE a
path based on the data it's holding:

    if the user is an admin        -> show the admin panel
    if the file already exists     -> skip it
    if the payment failed          -> retry, then email support
    if the temperature is below 0  -> warn about ice

This is the moment code becomes genuinely useful, because it can now react to
circumstances you didn't know about when you wrote it.

The mechanism has two halves:

  1. A CONDITION - an expression that evaluates to True or False.
  2. A BLOCK - indented lines that run only when the condition is True.

And the thing that makes Python distinctive: the block is defined by
INDENTATION, not by brackets. Whitespace is part of the language's grammar.
That feels alarming for about a day and then feels obviously right, because
badly indented code cannot pretend to be fine.
"""

LINE = "-" * 70


# =============================================================================
# PART 1 — COMPARISON OPERATORS: MAKING True AND False
# =============================================================================
print(LINE)
print("PART 1 — COMPARISONS")
print(LINE)

# A comparison is a question. Its answer is always a bool: True or False.

a = 10
b = 3

print(f"{a} == {b}  ->", a == b)      # equal to?          False
print(f"{a} != {b}  ->", a != b)      # NOT equal to?      True
print(f"{a} >  {b}  ->", a > b)       # greater than?      True
print(f"{a} <  {b}  ->", a < b)       # less than?         False
print(f"{a} >= {b}  ->", a >= b)      # greater or equal?  True
print(f"{a} <= {b}  ->", a <= b)      # less or equal?     False
print()

# ***** = VERSUS == : THE CLASSIC BEGINNER TRAP *****
#   =   ASSIGNS.  age = 22   means "make age be 22"      (an instruction)
#   ==  COMPARES. age == 22  means "is age 22?"          (a question)
# Python helpfully refuses to let you use = inside an if, which catches most
# accidents:  `if age = 22:` is a SyntaxError.

# Comparisons work on text too. Equality is exact and case-sensitive:
print('"yes" == "yes"  ->', "yes" == "yes")
print('"Yes" == "yes"  ->', "Yes" == "yes")     # False - capital Y
print('normalised      ->', "Yes".lower() == "yes")

# < and > on strings compare alphabetically (by character code, so all
# uppercase letters sort before all lowercase ones):
print('"apple" < "banana" ->', "apple" < "banana")   # True
print('"Zebra" < "apple"  ->', "Zebra" < "apple")    # True - 'Z' is code 90,
                                                     # 'a' is code 97
print()


# =============================================================================
# PART 2 — if / elif / else
# =============================================================================
print(LINE)
print("PART 2 — if / elif / else")
print(LINE)

# THE SHAPE:
#
#     if condition:              <- ends with a COLON
#         do_this()              <- indented 4 spaces = inside the if
#         and_this()
#     do_this_always()           <- back to the left margin = outside the if
#
# The colon says "a block follows". The indentation says "this is the block".
# Python's standard is 4 SPACES. VS Code does this for you when you press Tab.

temperature = 28

if temperature > 25:
    print("It's hot.")
    print("Both of these lines are inside the if.")

print("This line always runs - it isn't indented.")
print()

# --- else: the fallback path ---
age = 17

if age >= 18:
    print("Access granted.")
else:
    print("Access denied - must be 18 or over.")
print()

# --- elif: more than two paths ---
# elif is short for "else if". Python checks conditions TOP TO BOTTOM and runs
# the block for the FIRST one that's True, then skips all the rest.
score = 78

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"          # <- this one wins: 78 >= 70
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"Score {score} -> grade {grade}")

# ORDER IS CRITICAL. Because the first match wins, you must go from most
# specific to least specific. Reverse this chain and every score >= 60 would
# get a D, because that test would be reached first.
print()


# =============================================================================
# PART 3 — COMBINING CONDITIONS: and / or / not
# =============================================================================
print(LINE)
print("PART 3 — BOOLEAN LOGIC")
print(LINE)

# and  -> True only if BOTH sides are True
# or   -> True if EITHER side is True
# not  -> flips True to False and back

age = 25
has_ticket = True
is_banned = False

print("age >= 18 and has_ticket :", age >= 18 and has_ticket)
print("age >= 65 or has_ticket  :", age >= 65 or has_ticket)
print("not is_banned            :", not is_banned)

if age >= 18 and has_ticket and not is_banned:
    print("-> Welcome in.")
else:
    print("-> Entry refused.")
print()

# CHAINED COMPARISONS - Python lets you write ranges the way maths does.
# This is unusual and genuinely nicer than other languages:
temp = 22
print("18 <= temp <= 24 ->", 18 <= temp <= 24)    # instead of
                                                  # temp >= 18 and temp <= 24

# SHORT-CIRCUITING: Python stops evaluating as soon as the answer is certain.
#   `False and anything`  -> the right side is never looked at
#   `True or anything`    -> the right side is never looked at
# This isn't trivia - it's how you write safe guards:
user_input = ""
if user_input and int(user_input) > 10:      # int("") would crash...
    print("big number")
else:
    print("empty or small - and no crash, because `and` stopped early")
print()

# `in` - membership. Far cleaner than a long chain of ==.
role = "editor"
if role in ("admin", "editor", "moderator"):
    print(f"'{role}' can publish posts")

print("'@' in 'a@b.com'   :", "@" in "a@b.com")
print("'x' not in 'abc'   :", "x" not in "abc")
print()


# =============================================================================
# PART 4 — TRUTHINESS: WHAT COUNTS AS True?
# =============================================================================
print(LINE)
print("PART 4 — TRUTHY AND FALSY")
print(LINE)

# Python lets you put ANY value in an if, not just True/False. Each type has a
# notion of "empty" or "nothing", and those count as False.
#
# FALSY (behave as False):   False, None, 0, 0.0, "", [], {}, ()
#                            i.e. the number zero, and anything empty
# TRUTHY (behave as True):   everything else, including "0", "False", [0], -1

for value in [0, 1, -1, "", "hi", "0", [], [0], None, 0.0]:
    print(f"  bool({value!r:<7}) = {bool(value)}")
print()

# THIS IS THE IDIOMATIC WAY TO CHECK FOR EMPTINESS:
username = ""

if username:                        # reads as "if there is a username"
    print(f"Hello {username}")
else:
    print("No username supplied")

# Rather than the clumsier `if len(username) > 0:` or `if username != "":`.

# ONE IMPORTANT EXCEPTION - use `is None` for None, not truthiness:
quantity = 0
if quantity is None:
    print("quantity was never set")
else:
    print(f"quantity is set, and its value is {quantity}")
# If you had written `if not quantity:` you couldn't tell "not supplied" (None)
# apart from "supplied as zero" (0) - and in a shopping cart those mean very
# different things.
print()


# =============================================================================
# PART 5 — NESTING, AND WHY TO AVOID DEEP NESTING
# =============================================================================
print(LINE)
print("PART 5 — NESTING AND GUARD CLAUSES")
print(LINE)

# An if can contain another if. Each level indents 4 more spaces.

logged_in = True
is_admin = True
account_active = True

if logged_in:
    if account_active:
        if is_admin:
            print("nested version: full admin access")
        else:
            print("nested version: standard access")
    else:
        print("nested version: account suspended")
else:
    print("nested version: please log in")

# That works, but notice how the interesting code drifts to the right. With
# five conditions it becomes unreadable - developers call it the "arrow of
# doom". The fix is GUARD CLAUSES: handle the exits first, at one level of
# indentation, leaving the main path flat at the bottom.

def describe_access(logged_in, account_active, is_admin):
    """Same logic, written flat. (def is lesson 10 - read past it for now.)"""
    if not logged_in:
        return "guard version: please log in"
    if not account_active:
        return "guard version: account suspended"
    if is_admin:
        return "guard version: full admin access"
    return "guard version: standard access"

print(describe_access(logged_in, account_active, is_admin))

# Same behaviour, one level of indentation, and each rule is a single readable
# line. Prefer this shape - it scales.
print()


# =============================================================================
# PART 6 — THE CONDITIONAL EXPRESSION (one-line if)
# =============================================================================
print(LINE)
print("PART 6 — ONE-LINE if")
print(LINE)

# When all you want is to CHOOSE A VALUE, there's a compact form:
#       value_if_true if condition else value_if_false

age = 20
status = "adult" if age >= 18 else "minor"
print(f"age {age} -> {status}")

count = 1
plural = "item" if count == 1 else "items"
print(f"You have {count} {plural}")

# It works inside f-strings and function calls too:
temp = 30
print(f"It is {'hot' if temp > 25 else 'mild'} today")

# USE IT when the choice is simple and fits comfortably on one line. DON'T
# chain several together - `a if x else b if y else c` is technically legal and
# genuinely horrible to read. Use if/elif/else for anything non-trivial.
print()


# =============================================================================
# PART 7 — match / case (Python 3.10+)
# =============================================================================
print(LINE)
print("PART 7 — match / case")
print(LINE)

# For comparing one value against many fixed options, `match` reads better than
# a long elif chain. Other languages call this a "switch".

command = "delete"

match command:
    case "create":
        print("Creating a new record")
    case "update":
        print("Updating the record")
    case "delete":
        print("Deleting the record")
    case "list" | "show":                   # | means "or"
        print("Listing records")
    case _:                                 # _ is the catch-all, like else
        print(f"Unknown command: {command}")

# Use match when you're dispatching on a known set of values (HTTP methods,
# menu choices, file extensions, event types). Use if/elif when your conditions
# are ranges or complex expressions - match can't do `score >= 90`.
print()


# =============================================================================
# PART 8 — REAL EXAMPLE: A BACKEND VALIDATION FUNCTION
# =============================================================================
print(LINE)
print("PART 8 — REAL EXAMPLE: VALIDATING A SIGN-UP")
print(LINE)

# Close to code you'd genuinely write behind a web form. Notice it's built
# almost entirely from guard clauses.

def validate_signup(email, password, age_text):
    """Return (is_valid, message) for a sign-up attempt."""
    email = email.strip().lower()

    if not email:
        return False, "Email is required"
    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "That doesn't look like an email address"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if password.isalpha():
        return False, "Password must contain at least one number or symbol"
    if not age_text.strip().isdigit():
        return False, "Age must be a whole number"
    if int(age_text) < 13:
        return False, "You must be 13 or older"

    return True, f"Welcome, {email}"


attempts = [
    ("sidd@example.com", "hunter2024", "22"),
    ("", "hunter2024", "22"),
    ("not-an-email", "hunter2024", "22"),
    ("a@b.com", "short", "22"),
    ("a@b.com", "onlyletters", "22"),
    ("a@b.com", "hunter2024", "twelve"),
    ("a@b.com", "hunter2024", "9"),
]

for email, password, age_text in attempts:
    ok, message = validate_signup(email, password, age_text)
    marker = "PASS" if ok else "FAIL"
    print(f"  [{marker}] {email!r:<22} {message}")
print()


# =============================================================================
# PART 9 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 9 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: using = instead of ==. Python catches it as a SyntaxError.

# MISTAKE 2: forgetting the colon.
#     if x > 5          -> SyntaxError: expected ':'

# MISTAKE 3: mixing tabs and spaces. They look identical on screen and Python
#   rejects the mixture (TabError). Configure VS Code to insert spaces - it
#   does by default for Python. Never "fix" indentation by eye alone.

# MISTAKE 4: writing conditions that can never be reached.
score = 85
if score > 50:
    print("  first branch wins")
elif score > 80:                    # UNREACHABLE: anything > 80 is also > 50
    print("  never printed")
#   Always order from most specific/narrowest to broadest.

# MISTAKE 5: comparing a value to True or False explicitly.
is_ready = True
#   if is_ready == True:      works but is noise
if is_ready:                  # say what you mean
    print("  is_ready - the clean form")

# MISTAKE 6: a chain of ORs against the same variable.
day = "sat"
#   if day == "sat" or day == "sun":            verbose
if day in ("sat", "sun"):                       # better
    print("  weekend")

# MISTAKE 7: assuming an if with no match does something. If no branch is True
#   and there's no else, Python simply moves on silently. If "nothing matched"
#   is a real possibility, add an else that says so.
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# EXERCISE 1 — Even or odd
#   Ask for (or hard-code) a number. Print whether it's even, odd, or zero.
#
# EXERCISE 2 — Ticket pricing
#   Price rules: under 5 free, 5-17 is 8.00, 18-64 is 14.00, 65+ is 9.00.
#   Anyone with a member card gets 20% off the price. Print the price for
#   several test ages, with and without a card.
#
# EXERCISE 3 — Password strength
#   Given a password string, print "weak", "medium" or "strong":
#     weak   = shorter than 8 characters
#     medium = 8+ characters but only letters, or only digits
#     strong = 8+ characters with a mix of letters and digits
#   Hints: len(), .isalpha(), .isdigit(), any(c.isdigit() for c in password)
#
# EXERCISE 4 — Leap year
#   A year is a leap year if it's divisible by 4, EXCEPT years divisible by
#   100, UNLESS they're also divisible by 400. Test 1900 (no), 2000 (yes),
#   2024 (yes), 2023 (no).
#
# EXERCISE 5 — FizzBuzz (the famous interview question)
#   For numbers 1 to 20, print "Fizz" if divisible by 3, "Buzz" if divisible
#   by 5, "FizzBuzz" if divisible by both, otherwise the number itself.
#   Watch your ORDER - the both-case must be tested first.
#
# EXERCISE 6 — HTTP status categoriser (web prep)
#   Given a status code, print its category:
#     200-299 Success, 300-399 Redirect, 400-499 Client error,
#     500-599 Server error, anything else Unknown.
#   Test with 200, 301, 404, 500, 999.
#
# EXERCISE 7 — Rewrite with guard clauses
#   Take the nested version in PART 5 and add two more conditions
#   (email_verified, has_subscription). Write it BOTH nested and flat, and see
#   for yourself which one you'd rather maintain.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   n = 7
#   if n == 0:
#       print("zero")
#   elif n % 2 == 0:
#       print("even")
#   else:
#       print("odd")
#
# EXERCISE 2
#   def ticket_price(age, has_card):
#       if age < 5:
#           return 0.0
#       elif age < 18:
#           price = 8.00
#       elif age < 65:
#           price = 14.00
#       else:
#           price = 9.00
#       return price * 0.8 if has_card else price
#   for age in (3, 12, 30, 70):
#       print(age, ticket_price(age, False), ticket_price(age, True))
#
# EXERCISE 3
#   password = "hunter2024"
#   has_digit = any(c.isdigit() for c in password)
#   has_letter = any(c.isalpha() for c in password)
#   if len(password) < 8:
#       print("weak")
#   elif has_digit and has_letter:
#       print("strong")
#   else:
#       print("medium")
#
# EXERCISE 4
#   for year in (1900, 2000, 2024, 2023):
#       is_leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
#       print(year, is_leap)
#
# EXERCISE 5
#   for n in range(1, 21):
#       if n % 15 == 0:          # divisible by both 3 and 5
#           print("FizzBuzz")
#       elif n % 3 == 0:
#           print("Fizz")
#       elif n % 5 == 0:
#           print("Buzz")
#       else:
#           print(n)
#
# EXERCISE 6
#   for code in (200, 301, 404, 500, 999):
#       if 200 <= code < 300:
#           category = "Success"
#       elif 300 <= code < 400:
#           category = "Redirect"
#       elif 400 <= code < 500:
#           category = "Client error"
#       elif 500 <= code < 600:
#           category = "Server error"
#       else:
#           category = "Unknown"
#       print(code, category)
#
# EXERCISE 7
#   def access(logged_in, active, verified, subscribed, is_admin):
#       if not logged_in:
#           return "please log in"
#       if not active:
#           return "account suspended"
#       if not verified:
#           return "please verify your email"
#       if is_admin:
#           return "full admin access"
#       if not subscribed:
#           return "free tier access"
#       return "subscriber access"


print("=" * 70)
print("Lesson 05 complete. Next: 06_lists.py")
print("=" * 70)

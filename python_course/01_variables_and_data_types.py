"""
===============================================================================
 LESSON 01 — VARIABLES AND DATA TYPES
===============================================================================

Time: about 60 minutes.
Assumes you have completed: 00_START_HERE.py


-------------------------------------------------------------------------------
 THEORY: WHAT IS A VARIABLE, REALLY?
-------------------------------------------------------------------------------

A program is useless if it can only work with values you typed in by hand. It
needs to REMEMBER things: a user's name, a running total, the file it's
currently processing. A variable is how a program remembers.

The usual beginner explanation is "a variable is a box that holds a value."
That's a decent start, but here is a more accurate picture that will save you
confusion later:

    A VARIABLE IS A NAME TAG YOU STICK ONTO A VALUE.

The value lives somewhere in the computer's memory. The name is a label that
points at it. When you write:

    age = 22

you are not putting 22 inside a box called `age`. You are creating the value
22 in memory and sticking the label `age` on it. This is why you can later
point the same label at something completely different:

    age = "twenty-two"        # the label now points at text instead

The `=` sign is the confusing part. In maths, `=` means "these two things are
equal." In Python, `=` means "point this name at that value." It is an ACTION,
and it flows right-to-left: work out the right side, then attach the name on
the left.

    total = 5 + 3      # 1. Python works out 5 + 3, getting 8
                       # 2. Python sticks the label `total` on the value 8

Read `=` in your head as "gets" or "is assigned". `total gets 8`.


-------------------------------------------------------------------------------
 THEORY: WHY DATA HAS TYPES
-------------------------------------------------------------------------------

Every value in Python has a TYPE - a category that determines what you can do
with it. This isn't bureaucracy; it's what makes `+` sensible.

Consider the `+` symbol. What should it do?

    5 + 3                -> 8          (numbers: add them)
    "sid" + "dh"         -> "siddh"    (text: join them)
    "age: " + 22         -> ERROR      (?? Python refuses to guess)

That last one is the TypeError you triggered in lesson 00. Python could have
guessed - maybe you meant "age: 22", maybe you meant something else entirely.
Languages that guess in situations like this are a famous source of bugs, so
Python's rule is: when the meaning is ambiguous, stop and tell the human.

The five types you need today:

  TYPE       CALLED      EXAMPLE            USE IT FOR
  ---------  ----------  -----------------  --------------------------------
  int        integer     42, -7, 0          whole numbers: counts, IDs, years
  float      float       3.14, -0.5, 2.0    numbers with decimals: prices,
                                            measurements, averages
  str        string      "hello", 'hi'      text of any kind
  bool       boolean     True, False        yes/no, on/off answers
  NoneType   none        None               "no value yet" / "nothing here"

"float" is short for "floating-point number" - the decimal point can float
around to different positions. Odd name, historical reason, don't worry about it.

"string" means a string of characters, like beads on a thread: "cat" is the
characters c, a, t strung together in order.


-------------------------------------------------------------------------------
 WHY THIS MATTERS FOR YOUR GOALS
-------------------------------------------------------------------------------

  Web backend      Every value arriving from a web form is a STRING - even
                   "25". If you don't convert it to an int, `age + 1` gives you
                   "251" or an error. This single fact causes an enormous
                   number of real-world bugs.
  Data analysis    A price column read from a CSV file is text until you
                   convert it. `sum()` on text fails.
  Automation       Filenames are strings; file sizes are ints; "did this file
                   already get processed?" is a bool.

Types are not academic. They are where beginners lose their afternoons.
"""

# A quick note on the line below: "-" * 70 means "the character - repeated 70
# times". Multiplying text by a number repeats it. We'll cover that properly in
# lesson 02; here it's just to draw a neat divider.
LINE = "-" * 70


# =============================================================================
# PART 1 — CREATING VARIABLES
# =============================================================================
print(LINE)
print("PART 1 — CREATING VARIABLES")
print(LINE)

# Create a variable by assigning to it. There is no separate "declare" step,
# unlike in some other languages.
first_name = "Sidd"
age = 22
height_cm = 250.5
is_learning = True

# Now use those names anywhere you'd use the value itself.
print("Name:", first_name)
print("Age:", age)
print("Height:", height_cm)
print("Learning Python:", is_learning)
print()

# A variable can be REASSIGNED at any time. The old value is simply forgotten.
score = 10
print("score starts at:", score)
score = 25
print("score is now:   ", score)

# Very common pattern: use a variable's own current value to compute its next
# value. Python works out the RIGHT side first, using the old value.
score = score + 5           # 25 + 5 = 30, then re-label
print("score after +5: ", score)

# That pattern is so common it has a shortcut, called an augmented assignment.
score += 5                  # exactly the same as: score = score + 5
print("score after += 5:", score)

# The same shortcut exists for the other operations:
score -= 10                 # subtract
score *= 2                  # multiply
print("score after -=10 then *=2:", score)
print()


# =============================================================================
# PART 2 — CHECKING TYPES WITH type()
# =============================================================================
print(LINE)
print("PART 2 — CHECKING TYPES")
print(LINE)

# type() tells you what category a value belongs to. This is your main tool
# when a TypeError confuses you: print the types and look.
print("type of first_name :", type(first_name))
print("type of age        :", type(age))
print("type of height_cm  :", type(height_cm))
print("type of is_learning:", type(is_learning))
print("type of None       :", type(None))
print()

# The `<class 'str'>` output just means "this value belongs to the str type".
# `class` is a word you'll meet properly in lesson 16.

# WATCH OUT: quotes change everything.
number_as_int = 22          # a number you can do maths with
number_as_str = "22"        # text that happens to look like a number

print("number_as_int:", number_as_int, type(number_as_int))
print("number_as_str:", number_as_str, type(number_as_str))
print("int + 1 ->", number_as_int + 1)      # 23  - arithmetic
print("str + '1' ->", number_as_str + "1")  # 221 - text joined together!
print()

# WATCH OUT: adding a decimal point changes the type.
print("type of 5   :", type(5))     # int
print("type of 5.0 :", type(5.0))   # float - same value, different type
print()


# =============================================================================
# PART 3 — CONVERTING BETWEEN TYPES
# =============================================================================
print(LINE)
print("PART 3 — CONVERTING BETWEEN TYPES (casting)")
print(LINE)

# You convert with the type's own name used as a function: int(), float(),
# str(), bool(). This is called "casting" or "type conversion".

age_text = "22"                     # imagine this came from a web form
age_number = int(age_text)          # convert text -> integer
print("next year you'll be:", age_number + 1)

price_text = "19.99"
price = float(price_text)           # convert text -> float
print("price with tax:", price * 1.2)

# Converting the other way, to text, is how you glue values into a sentence
# using `+`:
count = 3
print("You have " + str(count) + " new messages.")

# But there's a much better way to build sentences: the f-string.
# Put an `f` before the opening quote, then put any variable in {curly braces}.
# Python substitutes the value in, converting to text automatically.
print(f"You have {count} new messages.")
print(f"{first_name} is {age} years old and {height_cm}cm tall.")

# f-strings can contain calculations too:
print(f"Next year {first_name} will be {age + 1}.")

# USE F-STRINGS. They are shorter, they read like the sentence they produce,
# and they don't blow up when you forget a str() call. This is the modern,
# normal way to do it in Python. The `+` version above is shown only so you
# recognise it in older code.
print()

# Careful - int() truncates floats, it does NOT round them.
print("int(9.99)  ->", int(9.99))     # 9, not 10. It chops the decimal off.
print("round(9.99)->", round(9.99))   # 10. Use round() when you want rounding.
print()

# Careful - int() only works on text that is a clean whole number.
# int("abc") and int("19.99") both raise ValueError.
# You'll learn to handle that properly in lesson 12 (error handling).


# =============================================================================
# PART 4 — NAMING VARIABLES
# =============================================================================
print(LINE)
print("PART 4 — NAMING")
print(LINE)

# THE RULES (break these and Python refuses to run):
#   * letters, digits and underscores only
#   * cannot start with a digit          (2fast = 1  -> SyntaxError)
#   * no spaces                          (my name = 1 -> SyntaxError)
#   * case matters: `age`, `Age` and `AGE` are three different variables
#   * cannot be one of Python's ~35 reserved words (if, for, class, True...)

# THE CONVENTIONS (break these and your code still runs, but it marks you out
# as a beginner and makes your code harder to read):
#   * use snake_case: lowercase words joined by underscores
#   * name things for what they MEAN, not what type they are
#   * ALL_CAPS for values that never change (constants)

# Good names - a stranger can guess what these hold:
user_email = "sidd@example.com"
items_in_cart = 3
tax_rate = 0.2
MAX_LOGIN_ATTEMPTS = 3          # a constant: convention says "don't reassign"

# Bad names - technically legal, genuinely awful:
#   x = "sidd@example.com"      what is x?
#   e = 3                       e as in email? error? euler?
#   thing2 = 0.2                thing2 of what?
#   emailString = "..."         works, but Python style prefers snake_case

print(f"Cart: {items_in_cart} items for {user_email}, tax rate {tax_rate}")

# WHY THIS MATTERS MORE THAN IT SOUNDS: you will spend far more time reading
# code (including your own, six months later) than writing it. A good name is a
# free comment that can never go out of date.
print()


# =============================================================================
# PART 5 — MULTIPLE ASSIGNMENT (you already met this)
# =============================================================================
print(LINE)
print("PART 5 — MULTIPLE ASSIGNMENT")
print(LINE)

a, b = 10, 20                   # a gets 10, b gets 20
print(f"a={a}, b={b}")

x = y = 0                       # both names point at the same value
print(f"x={x}, y={y}")

a, b = b, a                     # swap - the right side is worked out FIRST,
print(f"after swap: a={a}, b={b}")   # so no temporary variable is needed

# Unpacking: the number of names must match the number of values exactly.
first, second, third = [1, 2, 3]
print(f"first={first}, second={second}, third={third}")

# This is genuinely useful, not a party trick. You'll use it constantly when
# looping over data in lesson 07:
#     for name, score in results:
print()


# =============================================================================
# PART 6 — None: THE "NOTHING HERE YET" VALUE
# =============================================================================
print(LINE)
print("PART 6 — None")
print(LINE)

# None is a real value meaning "deliberately empty". It is not 0, not "", not
# False - it means "no answer has been supplied".
middle_name = None
print("middle_name:", middle_name, type(middle_name))

# Why you'll need it: in a web backend, a user profile might have no phone
# number yet. That's None, which is different from an empty string "" (which
# would mean "they told us their number is blank"). Databases call this NULL.

# Check for it with `is`, not `==`. (Both work; `is None` is the accepted
# style and reads better.)
print("Is middle_name empty?", middle_name is None)
print()


# =============================================================================
# PART 7 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 7 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: using a variable before creating it.
#     print(total_price)    ->  NameError: name 'total_price' is not defined
#   Python reads top to bottom. You cannot use a name before the line that
#   creates it. Also check your spelling - a typo is a NameError too.

# MISTAKE 2: confusing = with ==
#     age = 22    sets age to 22        (assignment - an action)
#     age == 22   asks "is age 22?"     (comparison - a question, gives True/False)
#   You'll use == properly in lesson 05. For now just register that they are
#   completely different things.
print("age == 22 asks a question, and the answer is:", age == 22)

# MISTAKE 3: expecting a variable to update itself automatically.
price = 100
total = price * 2       # total is calculated ONCE, right now. It becomes 200.
price = 500             # changing price now does NOT change total.
print(f"price is {price} but total is still {total}")
#   A variable stores a RESULT, not a live formula. Spreadsheets work the other
#   way round, which trips up people coming from Excel. To get a new total you
#   must recalculate it.

# MISTAKE 4: floats are not perfectly precise.
print("0.1 + 0.2 =", 0.1 + 0.2)     # -> 0.30000000000000004
#   This is not a Python bug; it's how all computers store decimals in binary,
#   the same way 1/3 can't be written exactly in decimal. It's harmless for
#   most work. For MONEY, never use floats for the final stored value - use
#   whole numbers of pennies/cents, or the `decimal` module (lesson 18).

# MISTAKE 5: shadowing a built-in name.
#     list = [1, 2, 3]     # now the built-in list() function is broken
#     type = "admin"       # now type() is broken
#   If your editor colours a name differently, that's a hint it already means
#   something. Use `user_list`, `user_type` instead.
print()


# =============================================================================
# PART 8 — A SMALL REAL PROGRAM
# =============================================================================
print(LINE)
print("PART 8 — PUTTING IT TOGETHER: AN INVOICE")
print(LINE)

# Everything above, used for something a real program might do.

CUSTOMER_NAME = "Acme Ltd"      # constant: known up front, never changes
TAX_RATE = 0.20                 # constant: 20% VAT

item_name = "Wireless keyboard"
unit_price = 45.50              # float - it has pennies
quantity = 3                    # int - you can't buy 2.5 keyboards

subtotal = unit_price * quantity
tax = subtotal * TAX_RATE
total_due = subtotal + tax

print(f"Invoice for: {CUSTOMER_NAME}")
print(f"  {quantity} x {item_name} @ {unit_price:.2f}")
print(f"  Subtotal: {subtotal:.2f}")
print(f"  Tax @ {TAX_RATE:.0%}: {tax:.2f}")
print(f"  TOTAL DUE: {total_due:.2f}")

# The `:.2f` inside the braces is a FORMAT SPEC: "show this as a float with
# exactly 2 decimal places". `:.0%` means "show as a percentage, 0 decimals".
# Without it you'd get 163.79999999999998 on your invoice. More in lesson 02.
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# EXERCISE 1 — Profile card
#   Create variables for your name (str), age (int), height in metres (float),
#   and whether you drink coffee (bool). Print one f-string sentence using all
#   four. Then print the type of each.
#
# EXERCISE 2 — The form-input bug
#   A web form always gives you text. Start with these two lines exactly:
#       quantity_from_form = "4"
#       price_from_form = "12.50"
#   Calculate and print the correct total (50.00). You'll need conversions.
#   First, deliberately try it WITHOUT converting and read the error.
#
# EXERCISE 3 — Unit converter
#   Store a temperature in Celsius. Convert to Fahrenheit with  F = C * 9/5 + 32
#   and print both, formatted to 1 decimal place (use :.1f).
#   Then change only the Celsius variable and re-run.
#
# EXERCISE 4 — Fix the bad names
#   Rewrite this with proper names and make it work:
#       a = "Sidd"
#       b = 22
#       c = a + " is " + b + " years old"
#   (There is a real bug in line c as well as bad naming. Find it.)
#
# EXERCISE 5 — Swap without a helper
#   Set left = "apple" and right = "banana". Swap them in ONE line, then print.
#
# EXERCISE 6 — Split the bill
#   A restaurant bill is 187.40, shared between 5 people, with a 12.5% tip.
#   Use named constants where it makes sense. Print what each person owes,
#   to 2 decimal places.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   my_name = "Sidd"
#   my_age = 22
#   my_height_m = 1.78
#   drinks_coffee = True
#   print(f"{my_name} is {my_age}, {my_height_m}m tall. Coffee: {drinks_coffee}")
#   print(type(my_name), type(my_age), type(my_height_m), type(drinks_coffee))
#
# EXERCISE 2
#   quantity_from_form = "4"
#   price_from_form = "12.50"
#   # quantity_from_form * price_from_form -> TypeError: can't multiply
#   #                                         sequence by non-int of type 'str'
#   quantity = int(quantity_from_form)
#   price = float(price_from_form)
#   print(f"Total: {quantity * price:.2f}")        # -> Total: 50.00
#   Note quantity uses int() and price uses float(): int("12.50") would fail,
#   because "12.50" is not a whole number.
#
# EXERCISE 3
#   celsius = 21.5
#   fahrenheit = celsius * 9 / 5 + 32
#   print(f"{celsius:.1f}C is {fahrenheit:.1f}F")
#
# EXERCISE 4
#   name = "Sidd"
#   age = 22
#   description = f"{name} is {age} years old"      # f-string handles the int
#   print(description)
#   The bug: `a + " is " + b` tries to join a str to an int -> TypeError.
#   Old fix: + str(b) +. Better fix: use an f-string.
#
# EXERCISE 5
#   left, right = "apple", "banana"
#   left, right = right, left
#   print(left, right)        # -> banana apple
#
# EXERCISE 6
#   BILL_TOTAL = 187.40
#   PEOPLE = 5
#   TIP_RATE = 0.125
#   tip = BILL_TOTAL * TIP_RATE
#   grand_total = BILL_TOTAL + tip
#   per_person = grand_total / PEOPLE
#   print(f"Bill {BILL_TOTAL:.2f} + tip {tip:.2f} = {grand_total:.2f}")
#   print(f"Each of {PEOPLE} people pays {per_person:.2f}")


print("=" * 70)
print("Lesson 01 complete. Next: 02_strings_and_text.py")
print("=" * 70)

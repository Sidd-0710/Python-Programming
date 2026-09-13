"""
===============================================================================
 LESSON 03 — NUMBERS AND MATHS
===============================================================================

Time: about 50 minutes.
Assumes: lessons 01-02.


-------------------------------------------------------------------------------
 THEORY: TWO KINDS OF NUMBER, AND WHY IT MATTERS
-------------------------------------------------------------------------------

Python has two everyday number types:

  int    Whole numbers: 0, 42, -7, 1000000. No decimal point.
         Python ints have NO SIZE LIMIT. You can calculate 2 ** 1000 and get an
         exact answer. Most languages overflow and give you garbage. This is a
         genuinely lovely feature.

  float  Numbers with a decimal point: 3.14, -0.5, 2.0.
         Floats are stored as binary approximations, so they are FAST but not
         always EXACT. This is the source of the famous 0.1 + 0.2 oddity.

Rule of thumb: use int when you're counting things that can't be split (users,
files, retries, array positions). Use float when measuring things that can
(prices, weights, averages, percentages).

Any arithmetic that mixes an int and a float produces a float, because Python
promotes to the more general type rather than silently losing your decimals.
"""

import math       # the standard maths library - lesson 15 explains `import`
import random     # for random numbers

LINE = "-" * 70


# =============================================================================
# PART 1 — THE ARITHMETIC OPERATORS
# =============================================================================
print(LINE)
print("PART 1 — OPERATORS")
print(LINE)

a = 17
b = 5

print(f"{a} + {b}  = {a + b}")        # addition          -> 22
print(f"{a} - {b}  = {a - b}")        # subtraction       -> 12
print(f"{a} * {b}  = {a * b}")        # multiplication    -> 85
print(f"{a} / {b}  = {a / b}")        # TRUE division     -> 3.4  (always float)
print(f"{a} // {b} = {a // b}")       # FLOOR division    -> 3    (drops remainder)
print(f"{a} % {b}  = {a % b}")        # MODULO/remainder  -> 2
print(f"{a} ** {b} = {a ** b}")       # exponent (power)  -> 1419857
print()

# Note that / ALWAYS gives a float, even when it divides evenly:
print("10 / 2 =", 10 / 2, type(10 / 2))      # 5.0 <class 'float'>
print("10 // 2 =", 10 // 2, type(10 // 2))   # 5   <class 'int'>
print()


# =============================================================================
# PART 2 — // AND % ARE MORE USEFUL THAN THEY LOOK
# =============================================================================
print(LINE)
print("PART 2 — FLOOR DIVISION AND MODULO IN REAL LIFE")
print(LINE)

# These two look like school-maths trivia. They are not. They appear constantly
# in real backend and automation code. Together they answer:
#     "how many whole groups, and what's left over?"

total_seconds = 3725
hours = total_seconds // 3600               # whole hours
remaining = total_seconds % 3600            # seconds not in a whole hour
minutes = remaining // 60
seconds = remaining % 60
print(f"{total_seconds}s = {hours}h {minutes}m {seconds}s")

# USE 1: PAGINATION (every website with a "next page" button does this)
total_items = 53
per_page = 10
full_pages = total_items // per_page            # 5 complete pages
leftover = total_items % per_page               # 3 items on a final page
pages_needed = -(-total_items // per_page)      # the "ceiling division" trick
print(f"{total_items} items, {per_page} per page -> {pages_needed} pages "
      f"({full_pages} full + {leftover} on the last)")

# The next few examples use `for` loops and `if`, which you haven't formally
# met yet (lessons 05 and 07). Don't worry about the syntax - just read the
# output and focus on what % and // are doing.

# USE 2: IS IT EVEN? (x % 2 == 0). Used for striping table rows, splitting work
# in half, alternating behaviour.
for n in [10, 7, 4]:
    kind = "even" if n % 2 == 0 else "odd"      # lesson 05 explains this line
    print(f"  {n} is {kind}")

# USE 3: "DO SOMETHING EVERY Nth TIME" - progress reporting in a long job.
for i in range(1, 21):
    if i % 5 == 0:                              # every 5th iteration
        print(f"  ...processed {i} records")

# USE 4: WRAPPING AROUND a fixed range (clock faces, cycling through colours).
print("  9 hours after 8 o'clock is", (8 + 9) % 12, "o'clock")
print()


# =============================================================================
# PART 3 — ORDER OF OPERATIONS
# =============================================================================
print(LINE)
print("PART 3 — PRECEDENCE")
print(LINE)

# Python follows normal maths precedence:
#     1. ()          brackets
#     2. **          powers
#     3. * / // %    multiply and divide
#     4. + -         add and subtract
# Same level = left to right.

print("2 + 3 * 4    =", 2 + 3 * 4)        # 14, not 20
print("(2 + 3) * 4  =", (2 + 3) * 4)      # 20
print("10 - 2 - 3   =", 10 - 2 - 3)       # 5  (left to right)
print("2 ** 3 ** 2  =", 2 ** 3 ** 2)      # 512 - ** is the odd one out, it
                                          # goes RIGHT to left: 2**(3**2)

# ADVICE: don't memorise the full table. Use brackets whenever there is the
# slightest doubt. Brackets cost nothing and make your intent obvious to the
# next person reading it (usually you).
average = (10 + 20 + 30) / 3              # clear
print("average:", average)
print()

# A classic real bug - the missing brackets in a formula:
subtotal, tax_rate, discount = 100, 0.2, 10
wrong = subtotal - discount * 1 + tax_rate        # nonsense
right = (subtotal - discount) * (1 + tax_rate)    # intended
print(f"wrong: {wrong}   right: {right}")
print()


# =============================================================================
# PART 4 — BUILT-IN NUMBER FUNCTIONS
# =============================================================================
print(LINE)
print("PART 4 — BUILT-IN FUNCTIONS")
print(LINE)

values = [12, 7, 45, 3, 28]         # a list - lesson 06

print("abs(-9)      =", abs(-9))            # distance from zero -> 9
print("round(3.7)   =", round(3.7))         # -> 4
print("round(3.14159, 2) =", round(3.14159, 2))   # 2 decimals -> 3.14
print("min(values)  =", min(values))
print("max(values)  =", max(values))
print("sum(values)  =", sum(values))
print("len(values)  =", len(values))
print("average      =", sum(values) / len(values))
print("pow(2, 10)   =", pow(2, 10))         # same as 2 ** 10
print()

# A surprise with round(): Python uses "banker's rounding" - exact halves go to
# the nearest EVEN number. It reduces statistical bias when rounding lots of
# values, but it startles people:
print("round(0.5) =", round(0.5))      # 0, not 1
print("round(1.5) =", round(1.5))      # 2
print("round(2.5) =", round(2.5))      # 2, not 3
# For money, don't fight this - use the `decimal` module (lesson 18) if exact
# rounding rules matter legally.
print()


# =============================================================================
# PART 5 — THE math MODULE
# =============================================================================
print(LINE)
print("PART 5 — THE math MODULE")
print(LINE)

# `import math` at the top of the file gives access to more maths tools.
# You reach into it with a dot: math.something

print("math.pi        =", math.pi)
print("math.sqrt(144) =", math.sqrt(144))     # square root -> 12.0
print("math.ceil(4.1) =", math.ceil(4.1))     # round UP always -> 5
print("math.floor(4.9)=", math.floor(4.9))    # round DOWN always -> 4
print("math.trunc(-4.9)=", math.trunc(-4.9))  # chop toward zero -> -4
print("math.inf       =", math.inf)           # infinity, useful as a starting
                                              # "worst so far" value
print()

# ceil() is the honest way to do the pagination calculation from PART 2:
print("pages:", math.ceil(53 / 10))
print()


# =============================================================================
# PART 6 — RANDOM NUMBERS
# =============================================================================
print(LINE)
print("PART 6 — RANDOM")
print(LINE)

# Randomness is used for games, sampling data, test data, and picking a
# server from a pool.

random.seed(42)     # seeding makes the "random" numbers repeatable, so this
                    # lesson prints the same thing every run. Remove this line
                    # in real programs (and see different numbers each run).

print("random.randint(1, 6)   :", random.randint(1, 6))     # dice: 1-6 inclusive
print("random.random()        :", random.random())          # float 0.0 - 1.0
print("random.choice([...])   :", random.choice(["red", "green", "blue"]))
print("random.sample(range(1,50), 6):", random.sample(range(1, 50), 6))

deck = ["A", "K", "Q", "J"]
random.shuffle(deck)            # shuffles the list IN PLACE (changes it)
print("shuffled deck          :", deck)
print()

# NOTE: `random` is fine for games and simulations but NOT for passwords,
# tokens or anything security-related - it is predictable. Use the `secrets`
# module for those (lesson 18).


# =============================================================================
# PART 7 — THE FLOAT PRECISION PROBLEM
# =============================================================================
print(LINE)
print("PART 7 — FLOATS ARE APPROXIMATE")
print(LINE)

print("0.1 + 0.2          =", 0.1 + 0.2)
print("0.1 + 0.2 == 0.3   =", 0.1 + 0.2 == 0.3)      # False!

# WHY: computers store numbers in binary. Just as 1/3 cannot be written exactly
# in decimal (0.3333...), 1/10 cannot be written exactly in binary. The result
# is a tiny error, invisible until you compare for exact equality.

# FIX 1 - never compare floats with ==. Ask "are they close enough?"
print("math.isclose(0.1 + 0.2, 0.3):", math.isclose(0.1 + 0.2, 0.3))

# FIX 2 - round before comparing or displaying.
print("round to 2dp:", round(0.1 + 0.2, 2) == 0.3)

# FIX 3 - for MONEY, work in whole pence/cents (ints), or use `decimal`.
price_in_pence = 1999               # £19.99, stored exactly as an int
qty = 3
total_pence = price_in_pence * qty
print(f"Total: £{total_pence / 100:.2f}   (calculated as {total_pence} pence)")
print()


# =============================================================================
# PART 8 — REAL EXAMPLE: A SAVINGS PROJECTION
# =============================================================================
print(LINE)
print("PART 8 — COMPOUND INTEREST")
print(LINE)

# The kind of calculation you'd put behind a web form or in a spreadsheet
# replacement script.

starting_amount = 5000.00
annual_rate = 0.045              # 4.5%
years = 10

# Compound interest formula: final = principal * (1 + rate) ** years
final_amount = starting_amount * (1 + annual_rate) ** years
interest_earned = final_amount - starting_amount

print(f"Start:    {starting_amount:>12,.2f}")
print(f"Rate:     {annual_rate:>12.2%}")
print(f"Years:    {years:>12}")
print(f"Final:    {final_amount:>12,.2f}")
print(f"Interest: {interest_earned:>12,.2f}")

# The "rule of 72" - a quick estimate of how long money takes to double:
print(f"Doubles in roughly {72 / (annual_rate * 100):.1f} years")
print()


# =============================================================================
# PART 9 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 9 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: dividing by zero.
#     10 / 0    -> ZeroDivisionError
#   Guard against it whenever the divisor comes from data:
items = 0
average_price = 0 if items == 0 else 100 / items
print("safe average with 0 items:", average_price)

# MISTAKE 2: assuming / gives a whole number. It never does. Use // for things
#   like "how many complete batches", or you'll get 3.4 batches.

# MISTAKE 3: integer inputs from text.
#     "5" + 5             -> TypeError
#     int("5") + 5        -> 10        correct
#     int("5.7")          -> ValueError (int() wants a clean whole number)
#     int(float("5.7"))   -> 5         convert in two steps

# MISTAKE 4: comparing floats with ==. Covered in PART 7. Use math.isclose.

# MISTAKE 5: % on negative numbers behaves differently from some languages.
print("-7 % 3 =", -7 % 3)      # 2 in Python (the sign follows the divisor)
#   Fine once you know; just don't assume it matches C or JavaScript.

# MISTAKE 6: losing precision by rounding too early. Round only when you
#   DISPLAY, not at every step of a calculation, or errors accumulate.
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# EXERCISE 1 — Seconds converter
#   Given total_seconds = 100_000 (underscores are legal in numbers and aid
#   readability), print it as "X days, Y hours, Z minutes, W seconds".
#
# EXERCISE 2 — Shipping boxes
#   You have 247 items and each box holds 12. Print how many full boxes, how
#   many items are left over, and how many boxes you must buy in total.
#
# EXERCISE 3 — BMI calculator
#   weight_kg = 72.5, height_m = 1.78. BMI = weight / height ** 2.
#   Print the BMI to 1 decimal place.
#
# EXERCISE 4 — Discount engine
#   An order of 249.99 gets a 15% discount, then 20% tax is applied to the
#   discounted amount. Print the original, the saving, and the final total,
#   all to 2 decimal places with thousands separators.
#
# EXERCISE 5 — Dice statistics
#   Roll two dice 1000 times using random.randint, and count how many times the
#   total was 7. Print the count and the percentage.
#   (Use a `for` loop - peek at lesson 07 if you need the syntax, or write it
#   with a while loop if you prefer to experiment.)
#
# EXERCISE 6 — Fix the float
#   Show that 0.1 * 3 == 0.3 is False, then show two different ways to make the
#   comparison work correctly.
#
# EXERCISE 7 — Progress percentage
#   A job has 1,437 tasks and 892 are done. Print a line like:
#       "892/1437 (62.1%) [############........]"
#   The bar should have 20 slots filled proportionally with '#' and '.'.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   total_seconds = 100_000
#   days = total_seconds // 86400
#   rest = total_seconds % 86400
#   hours = rest // 3600
#   rest = rest % 3600
#   minutes, seconds = rest // 60, rest % 60
#   print(f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds")
#
# EXERCISE 2
#   items, per_box = 247, 12
#   print("full boxes:", items // per_box)          # 20
#   print("leftover:", items % per_box)             # 7
#   print("boxes to buy:", math.ceil(items / per_box))   # 21
#
# EXERCISE 3
#   weight_kg, height_m = 72.5, 1.78
#   bmi = weight_kg / height_m ** 2
#   print(f"BMI: {bmi:.1f}")
#
# EXERCISE 4
#   ORDER = 249.99
#   DISCOUNT_RATE, TAX_RATE = 0.15, 0.20
#   saving = ORDER * DISCOUNT_RATE
#   discounted = ORDER - saving
#   total = discounted * (1 + TAX_RATE)
#   print(f"Original: {ORDER:>10,.2f}")
#   print(f"Saving:   {saving:>10,.2f}")
#   print(f"Total:    {total:>10,.2f}")
#
# EXERCISE 5
#   sevens = 0
#   for _ in range(1000):
#       if random.randint(1, 6) + random.randint(1, 6) == 7:
#           sevens += 1
#   print(f"{sevens} sevens ({sevens / 1000:.1%})")
#   (Theory says about 16.7% - 6 of the 36 combinations total 7.)
#
# EXERCISE 6
#   print(0.1 * 3 == 0.3)                       # False
#   print(math.isclose(0.1 * 3, 0.3))           # True
#   print(round(0.1 * 3, 10) == round(0.3, 10)) # True
#
# EXERCISE 7
#   done, total = 892, 1437
#   fraction = done / total
#   filled = round(fraction * 20)
#   bar = "#" * filled + "." * (20 - filled)
#   print(f"{done}/{total} ({fraction:.1%}) [{bar}]")


print("=" * 70)
print("Lesson 03 complete. Next: 04_input_and_conversion.py")
print("=" * 70)

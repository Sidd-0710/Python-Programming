"""
===============================================================================
 LESSON 03 — NUMBERS AND MATHS
===============================================================================

Time: about 50 minutes (there's a good place for a break halfway).
Assumes: lessons 01-02.


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. do every kind of arithmetic Python offers                    (PART 1)
  2. split things into groups with // and find what's left with %  (PART 2)
  3. know which part of a formula Python works out first          (PART 3)
  4. use ready-made maths tools: round, min, max, sqrt, ceil      (PARTS 4-5)
  5. make random numbers                                          (PART 6)
  6. avoid the famous 0.1 + 0.2 surprise                          (PART 7)

NEW WORDS - come back here whenever you forget one:

  operator      a symbol that does maths:  +  -  *  /  //  %  **
  //            floor division: divide, then throw away the remainder.
                17 // 5 is 3  ("how many WHOLE fives fit in 17?")
  %             modulo: the REMAINDER after dividing. 17 % 5 is 2
                ("and how many are left over?")
  **            power.  2 ** 3  means 2 x 2 x 2 = 8
  precedence    which part of a formula is worked out first (x before +)
  module        a file of extra ready-made tools you can switch on
  import        the word that switches a module on:  import math
  random        a module for random numbers - dice rolls, shuffling
  argument      a value you pass INTO a function:  round(3.7)  - 3.7 is the
                argument


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

import math       # switches on the standard maths tools - lesson 15 explains `import`
import random     # switches on the random-number tools

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
#   Think of 17 sweets shared between 5 children:
#       17 // 5 = 3   each child gets 3 sweets
#       17 % 5  = 2   and 2 sweets are left over

# Note that / ALWAYS gives a float, even when it divides evenly:
print("10 / 2 =", 10 / 2, type(10 / 2))      # 5.0 <class 'float'>
print("10 // 2 =", 10 // 2, type(10 // 2))   # 5   <class 'int'>
print()

# TRY IT NOW (1 minute):
#   Predict, then check by printing:   20 // 6     20 % 6     2 ** 5
#   (Answers: 3, 2, 32)


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
hours = total_seconds // 3600               # whole hours (3600 seconds in an hour)
remaining = total_seconds % 3600            # seconds not in a whole hour
minutes = remaining // 60                   # whole minutes in what's left
seconds = remaining % 60                    # and the seconds left after that
print(f"{total_seconds}s = {hours}h {minutes}m {seconds}s")

# USE 1: PAGINATION (every website with a "next page" button does this)
total_items = 53
per_page = 10
full_pages = total_items // per_page            # 5 complete pages
leftover = total_items % per_page               # 3 items on a final page
pages_needed = math.ceil(total_items / per_page)
#   math.ceil means "round UP to the next whole number": 53 / 10 = 5.3 -> 6.
#   (PART 5 covers the math tools properly.)
print(f"{total_items} items, {per_page} per page -> {pages_needed} pages "
      f"({full_pages} full + {leftover} on the last)")

# The next few examples use `for` loops and `if`, which you haven't formally
# met yet (lessons 05 and 07). Don't worry about the syntax - just read the
# output and focus on what % and // are doing.

# USE 2: IS IT EVEN? (x % 2 == 0). Used for striping table rows, splitting work
# in half, alternating behaviour.
# In plain English: "for each of the numbers 10, 7 and 4: if dividing by 2
# leaves nothing over, call it even, otherwise odd - and print it."
for n in [10, 7, 4]:
    kind = "even" if n % 2 == 0 else "odd"      # lesson 05 explains this line
    print(f"  {n} is {kind}")

# USE 3: "DO SOMETHING EVERY Nth TIME" - progress reporting in a long job.
# In plain English: "count from 1 to 20; every time the count divides by 5
# exactly, print a progress message."
for i in range(1, 21):
    if i % 5 == 0:                              # every 5th iteration
        print(f"  ...processed {i} records")

# USE 4: WRAPPING AROUND a fixed range (clock faces, cycling through colours).
print("  9 hours after 8 o'clock is", (8 + 9) % 12, "o'clock")
print()

# TRY IT NOW (2 minutes):
#   You have 100 minutes. Print how many whole hours that is, and how many
#   minutes are left over. (Answer: 100 // 60 = 1 hour, 100 % 60 = 40 minutes.)


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

print("2 + 3 * 4    =", 2 + 3 * 4)        # 14, not 20 (3 * 4 happens first)
print("(2 + 3) * 4  =", (2 + 3) * 4)      # 20 (brackets happen first)
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
subtotal, tax_rate, discount = 100, 0.2, 10       # three names at once (lesson 01)
wrong = subtotal - discount * 1 + tax_rate        # nonsense
right = (subtotal - discount) * (1 + tax_rate)    # intended: (100 - 10) x 1.2
print(f"wrong: {wrong}   right: {right}")
print()


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. That's all the arithmetic. After the break: Python's
#  ready-made maths tools (PARTS 4-8).
# -----------------------------------------------------------------------------


# =============================================================================
# PART 4 — BUILT-IN NUMBER FUNCTIONS
# =============================================================================
print(LINE)
print("PART 4 — BUILT-IN FUNCTIONS")
print(LINE)

values = [12, 7, 45, 3, 28]         # a list of 5 numbers - lesson 06

print("abs(-9)      =", abs(-9))            # distance from zero -> 9
print("round(3.7)   =", round(3.7))         # -> 4
print("round(3.14159, 2) =", round(3.14159, 2))   # 2 decimals -> 3.14
print("min(values)  =", min(values))        # the smallest
print("max(values)  =", max(values))        # the biggest
print("sum(values)  =", sum(values))        # all added together
print("len(values)  =", len(values))        # how many there are
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

# TRY IT NOW (1 minute):
#   With  marks = [67, 82, 91, 58],  print the highest mark, the lowest, and
#   the average.  (Answers: 91, 58, 74.5)


# =============================================================================
# PART 5 — THE math MODULE
# =============================================================================
print(LINE)
print("PART 5 — THE math MODULE")
print(LINE)

# `import math` at the top of the file gives access to more maths tools.
# You reach into it with a dot: math.something
# In plain English: math.sqrt(144) means "the sqrt tool from the math module,
# applied to 144".

print("math.pi        =", math.pi)
print("math.sqrt(144) =", math.sqrt(144))     # square root -> 12.0
print("math.ceil(4.1) =", math.ceil(4.1))     # round UP always -> 5
print("math.floor(4.9)=", math.floor(4.9))    # round DOWN always -> 4
print("math.trunc(-4.9)=", math.trunc(-4.9))  # chop toward zero -> -4
print("math.inf       =", math.inf)           # infinity, useful as a starting
                                              # "worst so far" value
print()

# ceil() is the tool behind the pagination calculation in PART 2:
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
print("random.choice([...])   :", random.choice(["red", "green", "blue"]))  # pick one
print("random.sample(range(1,50), 6):", random.sample(range(1, 50), 6))
#   range(1, 50) means "the numbers 1 up to 49"; sample picks 6 different ones -
#   like drawing lottery balls.

deck = ["A", "K", "Q", "J"]
random.shuffle(deck)            # shuffles the list IN PLACE (changes it)
print("shuffled deck          :", deck)
print()

# NOTE: `random` is fine for games and simulations but NOT for passwords,
# tokens or anything security-related - it is predictable. Use the `secrets`
# module for those (lesson 18).

# TRY IT NOW (1 minute):
#   Delete the random.seed(42) line and run the file twice. The dice roll and
#   the shuffle change each time. Then put the line back.


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
# In plain English: "grow the money by 4.5%, then grow THAT by 4.5%, ten times".
final_amount = starting_amount * (1 + annual_rate) ** years
interest_earned = final_amount - starting_amount

# {value:>12,.2f} = right-aligned in 12 spaces, with commas, 2 decimals
# (all from lesson 02 PART 3)
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
#   In plain English: "if there are no items, the average is 0; otherwise
#   work it out". (This one-line if/else is lesson 05.)
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
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * + - * / are what you'd expect. / always gives a float.
#   * // is "how many whole groups", % is "how many left over", ** is power.
#   * Brackets are worked out first. When in doubt, add brackets.
#   * round, abs, min, max, sum, len are built in. More tools live in the
#     math module: math.sqrt, math.ceil (round up), math.floor (round down).
#   * random.randint(1, 6) rolls a dice. Never use `random` for passwords.
#   * Floats are approximate: 0.1 + 0.2 isn't exactly 0.3. For money, count
#     in whole cents.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. What are  25 // 7  and  25 % 7?
#   Q2. What does  3 + 4 * 2  give? Why?
#   Q3. What type is  8 / 2?
#   Q4. 45 people, 10 per minibus. How many minibuses? Which tool gives it?
#   Q5. Why is  0.1 + 0.2 == 0.3  False?
#
# ANSWERS
#   A1. 3 and 4. (Three whole 7s make 21; 4 is left over.)
#   A2. 11. Multiplication happens before addition.
#   A3. float (4.0). / always gives a float.
#   A4. 5. math.ceil(45 / 10) rounds 4.5 UP.
#   A5. Floats are stored as tiny approximations. Use math.isclose().


# =============================================================================
# EXERCISES
# =============================================================================
#
# WARM-UP A (easy) — Times table
#   Print the result of 7 * 8.
#
# WARM-UP B (easy) — Share the sweets
#   23 sweets, 4 children. Print how many each child gets (//) and how many
#   are left over (%).
#
# WARM-UP C (easy) — Area
#   A room is 4.5 metres by 3 metres. Print its area.
#
# EXERCISE 1 (medium) — Seconds converter
#   Given total_seconds = 100_000 (underscores are legal in numbers and aid
#   readability), print it as "X days, Y hours, Z minutes, W seconds".
#   Hint: follow the pattern at the top of PART 2, starting with days
#   (86400 seconds in a day).
#
# EXERCISE 2 (easy) — Shipping boxes
#   You have 247 items and each box holds 12. Print how many full boxes, how
#   many items are left over, and how many boxes you must buy in total.
#
# EXERCISE 3 (easy) — BMI calculator
#   weight_kg = 72.5, height_m = 1.78. BMI = weight / height ** 2.
#   Print the BMI to 1 decimal place.
#
# EXERCISE 4 (medium) — Discount engine
#   An order of 249.99 gets a 15% discount, then 20% tax is applied to the
#   discounted amount. Print the original, the saving, and the final total,
#   all to 2 decimal places with thousands separators.
#
# EXERCISE 5 (challenge - needs a loop from lesson 07) — Dice statistics
#   Roll two dice 1000 times using random.randint, and count how many times the
#   total was 7. Print the count and the percentage.
#   Fine to skip for now and come back after lesson 07.
#
# EXERCISE 6 (medium) — Fix the float
#   Show that 0.1 * 3 == 0.3 is False, then show two different ways to make the
#   comparison work correctly.
#
# EXERCISE 7 (challenge) — Progress percentage
#   A job has 1,437 tasks and 892 are done. Print a line like:
#       "892/1437 (62.1%) [############........]"
#   The bar should have 20 slots filled proportionally with '#' and '.'.
#   Hint: work out how many of the 20 slots to fill first, then build the bar
#   with "#" * filled and "." * the rest.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   print(7 * 8)                     # -> 56
#
# WARM-UP B
#   print(23 // 4, 23 % 4)           # -> 5 3
#
# WARM-UP C
#   print(4.5 * 3)                   # -> 13.5
#
# EXERCISE 1
#   total_seconds = 100_000
#   days = total_seconds // 86400
#   rest = total_seconds % 86400
#   hours = rest // 3600
#   rest = rest % 3600
#   minutes = rest // 60
#   seconds = rest % 60
#   print(f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds")
#   # -> 1 days, 3 hours, 46 minutes, 40 seconds
#
# EXERCISE 2
#   items = 247
#   per_box = 12
#   print("full boxes:", items // per_box)          # 20
#   print("leftover:", items % per_box)             # 7
#   print("boxes to buy:", math.ceil(items / per_box))   # 21
#
# EXERCISE 3
#   weight_kg = 72.5
#   height_m = 1.78
#   bmi = weight_kg / height_m ** 2     # ** happens first: 1.78 squared
#   print(f"BMI: {bmi:.1f}")            # -> BMI: 22.9
#
# EXERCISE 4
#   ORDER = 249.99
#   DISCOUNT_RATE = 0.15
#   TAX_RATE = 0.20
#   saving = ORDER * DISCOUNT_RATE
#   discounted = ORDER - saving
#   total = discounted * (1 + TAX_RATE)
#   print(f"Original: {ORDER:>10,.2f}")
#   print(f"Saving:   {saving:>10,.2f}")
#   print(f"Total:    {total:>10,.2f}")
#
# EXERCISE 5
#   sevens = 0
#   for _ in range(1000):          # "do this 1000 times" (lesson 07)
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
#   done = 892
#   total = 1437
#   fraction = done / total                     # 0.62...
#   filled = round(fraction * 20)               # 12 of the 20 slots
#   bar = "#" * filled + "." * (20 - filled)
#   print(f"{done}/{total} ({fraction:.1%}) [{bar}]")


print("=" * 70)
print("Lesson 03 complete. Next: 04_input_and_conversion.py")
print("=" * 70)

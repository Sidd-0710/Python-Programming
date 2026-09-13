"""
===============================================================================
 LESSON 07 — LOOPS: DOING THINGS REPEATEDLY
===============================================================================

Time: about 80 minutes.
Assumes: lessons 01-06.


-------------------------------------------------------------------------------
 THEORY: THE REASON COMPUTERS ARE USEFUL
-------------------------------------------------------------------------------

A computer is not smart. It is fast and tireless. A loop is how you cash in on
that: you describe a job ONCE, and the machine performs it on 5 items or 5
million with the same effort from you.

    Without a loop:  rename file 1, rename file 2, rename file 3... (you quit
                     around file 40)
    With a loop:     "for every file in this folder, rename it"     (3 lines,
                     works on 40,000 files)

This is the lesson where "automate repetitive tasks" stops being an aspiration
and becomes something you can actually do.

TWO KINDS OF LOOP, AND HOW TO CHOOSE:

  for loop    - "do this FOR EACH item in a collection"
                Use when you know what you're iterating over: a list, a file's
                lines, a range of numbers, a dictionary's keys.
                This is the one you'll use 90% of the time.

  while loop  - "KEEP doing this WHILE a condition holds"
                Use when you don't know how many repeats you need: retry until
                success, keep asking until input is valid, run until the user
                quits.

Choosing wrongly isn't fatal, but `for` is safer: it cannot run forever,
because collections end.
"""

LINE = "-" * 70


# =============================================================================
# PART 1 — THE for LOOP
# =============================================================================
print(LINE)
print("PART 1 — for LOOPS")
print(LINE)

# THE SHAPE:
#
#     for item_name in collection:      <- colon
#         do_something(item_name)       <- indented block
#
# `item_name` is a variable YOU name. On each pass Python assigns the next
# value to it and runs the block.

fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(f"  I have a {fruit}")

# Read it aloud: "for each fruit in fruits, print...". Python reads like the
# sentence you'd say, which is why it's a good first language.
print()

# The loop variable is an ordinary variable - use it in any calculation.
prices = [4.99, 12.50, 1.25]
for price in prices:
    with_tax = price * 1.2
    print(f"  {price:>6.2f} + tax = {with_tax:>6.2f}")
print()

# Strings are sequences too, so you can loop over their characters:
for letter in "Python":
    print(f"  {letter}", end="")        # end="" means "don't start a new line"
print()                                 # now finish the line
print()


# =============================================================================
# PART 2 — range(): LOOPING A FIXED NUMBER OF TIMES
# =============================================================================
print(LINE)
print("PART 2 — range()")
print(LINE)

# range() produces a sequence of numbers on demand. Three forms:
#     range(stop)              0 up to (not including) stop
#     range(start, stop)       start up to (not including) stop
#     range(start, stop, step) ...counting by step

print("range(5)        :", list(range(5)))            # [0, 1, 2, 3, 4]
print("range(1, 6)     :", list(range(1, 6)))         # [1, 2, 3, 4, 5]
print("range(0, 20, 5) :", list(range(0, 20, 5)))     # [0, 5, 10, 15]
print("range(5, 0, -1) :", list(range(5, 0, -1)))     # [5, 4, 3, 2, 1]
print()

# Note again: the stop value is EXCLUDED. range(1, 6) stops at 5. This matches
# slicing, and means range(len(x)) gives exactly the valid indexes of x.

for i in range(3):
    print(f"  attempt {i + 1} of 3")
print()

# `_` is the conventional name for "I don't care about the value, I just want
# N repetitions". It's a normal variable name that signals intent.
for _ in range(3):
    print("  tick")
print()

# range() doesn't build a list in memory - it generates numbers as needed. So
# range(10_000_000) costs almost nothing until you loop over it.


# =============================================================================
# PART 3 — enumerate() AND zip(): THE TWO YOU MUST KNOW
# =============================================================================
print(LINE)
print("PART 3 — enumerate AND zip")
print(LINE)

tasks = ["write code", "run tests", "deploy"]

# THE CLUMSY WAY beginners write numbered output:
#     for i in range(len(tasks)):
#         print(i + 1, tasks[i])
# It works, but it's noisy and easy to get wrong.

# THE PYTHONIC WAY - enumerate() gives you position AND value together:
for position, task in enumerate(tasks, start=1):
    print(f"  {position}. {task}")
print()

# zip() walks two (or more) collections in step. Perfect for paired data.
names = ["Sidd", "Ana", "Marco"]
scores = [88, 95, 72]

for name, score in zip(names, scores):
    print(f"  {name:<8} {score:>3}")

# zip stops at the SHORTEST collection - no error, it just ends early. That's
# usually what you want, but be aware of it if your data should be equal length.
print()


# =============================================================================
# PART 4 — ACCUMULATING: THE MOST IMPORTANT LOOP PATTERN
# =============================================================================
print(LINE)
print("PART 4 — ACCUMULATOR PATTERNS")
print(LINE)

# Nearly every useful loop follows the same three-step shape:
#     1. Set up an accumulator BEFORE the loop (0, or "", or an empty list)
#     2. Update it INSIDE the loop
#     3. Use it AFTER the loop
# Getting step 1 in the wrong place (inside the loop) resets it every pass -
# an extremely common bug.

sales = [1200, 1450, 1100, 1800, 2100, 1950]

# Pattern A - running total
total = 0                               # 1. before
for amount in sales:
    total += amount                     # 2. inside
print("total:", total)                  # 3. after

# Pattern B - counting matches
big_months = 0
for amount in sales:
    if amount > 1500:
        big_months += 1
print("months over 1500:", big_months)

# Pattern C - collecting into a new list (filtering)
strong = []
for amount in sales:
    if amount > 1500:
        strong.append(amount)
print("the strong months:", strong)

# Pattern D - tracking a best/worst so far
best = sales[0]
best_index = 0
for index, amount in enumerate(sales):
    if amount > best:
        best = amount
        best_index = index
print(f"best: {best} in month {best_index + 1}")

# Pattern E - building a string (join at the end, don't += in the loop)
pieces = []
for index, amount in enumerate(sales, start=1):
    pieces.append(f"M{index}={amount}")
print(" | ".join(pieces))
print()


# =============================================================================
# PART 5 — break AND continue
# =============================================================================
print(LINE)
print("PART 5 — break AND continue")
print(LINE)

# break    - leave the loop entirely, right now
# continue - skip the rest of THIS pass, go straight to the next item

# break: stop as soon as you've found what you came for. This is a real
# performance technique, not just tidiness - why check 10,000 more records
# after you've found your answer?
users = ["ana", "marco", "sidd", "priya"]

for user in users:
    print(f"  checking {user}")
    if user == "sidd":
        print("  found! stopping the search")
        break

print()

# continue: skip the items you don't care about and keep going.
values = [10, -5, 8, 0, -2, 15]
total = 0
for value in values:
    if value <= 0:
        continue                # ignore this one, move on
    total += value
print("sum of positives only:", total)
print()

# for...else - an unusual feature worth knowing. The `else` runs ONLY if the
# loop finished WITHOUT hitting break. It means "we searched everything and
# never found it".
target = "zara"
for user in users:
    if user == target:
        print(f"  found {target}")
        break
else:
    print(f"  {target} is not in the list (loop completed without break)")
print()


# =============================================================================
# PART 6 — while LOOPS
# =============================================================================
print(LINE)
print("PART 6 — while LOOPS")
print(LINE)

# THE SHAPE:
#     while condition:
#         block
# The condition is checked BEFORE every pass. When it's False, the loop ends.

countdown = 5
while countdown > 0:
    print(f"  {countdown}...")
    countdown -= 1              # <- if you forget this line, it never ends
print("  liftoff!")
print()

# ***** THE INFINITE LOOP *****
# Every while loop needs something inside it that eventually makes the
# condition False. Forget it and your program hangs forever.
#
#     count = 0
#     while count < 5:
#         print(count)          # count never changes -> runs forever
#
# IF THIS HAPPENS TO YOU: press Ctrl+C in the terminal to kill the program.
# It's a normal thing to do and nothing is damaged. Everyone does it.

# `while True` with `break` is a deliberate, idiomatic infinite loop - the
# standard shape for "keep asking until the answer is acceptable":
allowed = ["red", "green", "blue"]
simulated_answers = ["purple", "cyan", "green"]      # pretending to be a user
index = 0

while True:
    answer = simulated_answers[index]
    index += 1
    print(f"  user typed: {answer}")

    if answer in allowed:
        print(f"  accepted: {answer}")
        break

    print("  not allowed, asking again")

    if index >= len(simulated_answers):     # safety valve so this demo can end
        print("  giving up")
        break
print()

# Another good while use: retrying something that might fail.
attempt = 0
MAX_ATTEMPTS = 5
connected = False
while not connected and attempt < MAX_ATTEMPTS:
    attempt += 1
    connected = attempt == 3            # pretend the 3rd try works
    print(f"  connection attempt {attempt}: {'success' if connected else 'failed'}")
print()


# =============================================================================
# PART 7 — NESTED LOOPS
# =============================================================================
print(LINE)
print("PART 7 — NESTED LOOPS")
print(LINE)

# A loop inside a loop. The inner loop runs completely for EACH pass of the
# outer one. Use for grids, tables, and comparing every item against every
# other item.

for row in range(1, 4):
    for col in range(1, 4):
        print(f"{row}x{col}={row * col:<3}", end="")
    print()            # newline at the end of each row
print()

# Looping over a table (list of lists) - the data-analysis shape:
table = [
    ["Widget", 12, 4.99],
    ["Gadget", 5, 12.50],
    ["Doohickey", 30, 1.25],
]

print(f"{'Item':<12}{'Qty':>5}{'Price':>9}{'Value':>10}")
print("-" * 36)
grand_total = 0
for row in table:
    name, qty, price = row              # unpacking, from lesson 01
    value = qty * price
    grand_total += value
    print(f"{name:<12}{qty:>5}{price:>9.2f}{value:>10.2f}")
print("-" * 36)
print(f"{'TOTAL':<12}{'':>5}{'':>9}{grand_total:>10.2f}")
print()

# COST WARNING: nesting multiplies the work. A loop of 1,000 inside a loop of
# 1,000 is 1,000,000 passes. Fine for small data, catastrophic for large. If
# you find yourself nesting three deep over big collections, there's usually a
# better structure (often a dictionary - lesson 09).


# =============================================================================
# PART 8 — REAL EXAMPLE: A LOG FILE ANALYSER
# =============================================================================
print(LINE)
print("PART 8 — REAL EXAMPLE: SCANNING LOGS")
print(LINE)

# This is genuinely what a first useful automation script looks like. In
# lesson 13 you'll read these lines from a real file instead of a list.

log_lines = [
    "2024-05-01 10:02:11 INFO  User sidd logged in",
    "2024-05-01 10:04:56 ERROR Payment gateway timeout",
    "2024-05-01 10:05:02 INFO  Retrying payment",
    "2024-05-01 10:05:09 ERROR Payment gateway timeout",
    "2024-05-01 10:07:33 WARN  Disk usage at 91%",
    "2024-05-01 10:09:00 INFO  User ana logged in",
    "2024-05-01 10:11:45 ERROR Database connection lost",
]

error_count = 0
warn_count = 0
info_count = 0
error_messages = []

for line in log_lines:
    # Split into date, time, level, message - maxsplit=3 keeps the message whole
    date, time, level, message = line.split(None, 3)

    if level == "ERROR":
        error_count += 1
        error_messages.append(f"{time} {message}")
    elif level == "WARN":
        warn_count += 1
    else:
        info_count += 1

print(f"Scanned {len(log_lines)} lines")
print(f"  INFO : {info_count}")
print(f"  WARN : {warn_count}")
print(f"  ERROR: {error_count}")

if error_messages:
    print("\nErrors found:")
    for position, message in enumerate(error_messages, start=1):
        print(f"  {position}. {message}")

    # Was the same error repeated? A duplicate-detection loop.
    seen = []
    repeats = []
    for message in error_messages:
        text = message.split(" ", 1)[1]     # drop the timestamp
        if text in seen:
            repeats.append(text)
        else:
            seen.append(text)
    if repeats:
        print(f"\nRepeated errors (likely one root cause): {set(repeats)}")
print()


# =============================================================================
# PART 9 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 9 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: resetting the accumulator inside the loop.
#     for x in values:
#         total = 0          # WRONG - wipes it out every pass
#         total += x
#   Put it before the loop.

# MISTAKE 2: forgetting to change the while condition -> infinite loop.
#   Ctrl+C to escape. Check every while loop for its exit condition.

# MISTAKE 3: modifying a list while looping over it.
numbers = [1, 2, 3, 4, 5, 6]
for n in numbers[:]:            # iterate a COPY
    if n % 2 == 0:
        numbers.remove(n)       # modify the original
print("odds left:", numbers)
#   Without the [:] you'd skip items, because removing shifts everything left
#   while the loop's internal counter keeps moving right.

# MISTAKE 4: using range(len(x)) when you just want the items.
demo = ["a", "b", "c"]
#   for i in range(len(demo)):  print(demo[i])      <- clumsy
for item in demo:                                   # <- say what you mean
    pass
#   Use range(len(...)) only when you genuinely need the index AND can't use
#   enumerate.

# MISTAKE 5: expecting the loop variable to survive meaningfully after the loop.
for leftover in [1, 2, 3]:
    pass
print("after the loop, leftover =", leftover)   # 3 - the LAST value. Legal,
#   but relying on it is fragile: if the list is empty, the name doesn't exist
#   at all and you get a NameError.

# MISTAKE 6: nesting when zip() would do. If you're looping over two lists by
#   index to pair them up, you want zip().

# MISTAKE 7: doing expensive work inside a loop that could be done once
#   outside it. Move anything that doesn't change out of the loop body.
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# EXERCISE 1 — Times table
#   Print the 7 times table from 7x1 to 7x12, one per line, neatly aligned.
#
# EXERCISE 2 — Sum and average without sum()
#   Given [23, 45, 12, 67, 34, 89, 21], use a loop to find the total, the
#   average, the largest and the smallest - without using sum(), max() or
#   min(). This teaches you what those functions actually do.
#
# EXERCISE 3 — Countdown with a twist
#   Count down from 20 to 1, but print "Fizz" instead of any number divisible
#   by 3. Use a while loop.
#
# EXERCISE 4 — Password retry simulator
#   The correct password is "python123". Given a list of attempts
#   ["letmein", "password", "python123", "other"], loop until it's correct or
#   3 attempts are used up. Print whether access was granted, and stop
#   immediately on success (don't check "other").
#
# EXERCISE 5 — Invoice report
#   Given this data, print a table with a line per order, then totals:
#       orders = [("Ana", 3, 19.99), ("Marco", 1, 249.00), ("Sidd", 7, 4.50)]
#   Columns: customer, qty, unit price, line total. Then print the grand total
#   and the average order value.
#
# EXERCISE 6 — Find the duplicates
#   Given ["a", "b", "c", "b", "d", "a", "a"], print each value that appears
#   more than once, along with how many times.
#
# EXERCISE 7 — A pyramid
#   Print this shape using nested loops:
#       *
#       **
#       ***
#       ****
#       *****
#   Then make it right-aligned (a proper triangle) using string padding.
#
# EXERCISE 8 — Word frequency (a real data task)
#   Given a sentence, count how many times each word appears and print the
#   results. You only have lists so far, so it'll be clumsy - that clumsiness
#   is exactly why dictionaries exist (lesson 09). Do it anyway; you'll
#   appreciate the next lesson far more.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   for n in range(1, 13):
#       print(f"7 x {n:>2} = {7 * n:>3}")
#
# EXERCISE 2
#   values = [23, 45, 12, 67, 34, 89, 21]
#   total = 0
#   largest = values[0]
#   smallest = values[0]
#   for v in values:
#       total += v
#       if v > largest:
#           largest = v
#       if v < smallest:
#           smallest = v
#   print(total, total / len(values), largest, smallest)
#
# EXERCISE 3
#   n = 20
#   while n >= 1:
#       print("Fizz" if n % 3 == 0 else n)
#       n -= 1
#
# EXERCISE 4
#   CORRECT = "python123"
#   attempts = ["letmein", "password", "python123", "other"]
#   granted = False
#   for tries, attempt in enumerate(attempts, start=1):
#       if attempt == CORRECT:
#           granted = True
#           break
#       if tries == 3:
#           break
#   print("Access granted" if granted else "Locked out")
#
# EXERCISE 5
#   orders = [("Ana", 3, 19.99), ("Marco", 1, 249.00), ("Sidd", 7, 4.50)]
#   print(f"{'Customer':<10}{'Qty':>5}{'Unit':>10}{'Total':>10}")
#   grand = 0
#   for customer, qty, unit in orders:
#       line_total = qty * unit
#       grand += line_total
#       print(f"{customer:<10}{qty:>5}{unit:>10.2f}{line_total:>10.2f}")
#   print(f"{'GRAND':<10}{'':>5}{'':>10}{grand:>10.2f}")
#   print(f"Average order: {grand / len(orders):.2f}")
#
# EXERCISE 6
#   data = ["a", "b", "c", "b", "d", "a", "a"]
#   checked = []
#   for item in data:
#       if item in checked:
#           continue
#       checked.append(item)
#       count = data.count(item)
#       if count > 1:
#           print(f"{item}: {count} times")
#
# EXERCISE 7
#   for row in range(1, 6):
#       print("*" * row)
#   print()
#   for row in range(1, 6):
#       print(f"{'*' * row:>5}")
#
# EXERCISE 8
#   sentence = "the cat sat on the mat the end"
#   words = sentence.split()
#   seen = []
#   for word in words:
#       if word not in seen:
#           seen.append(word)
#           print(f"{word}: {words.count(word)}")
#   # Note how awkward this is - two passes over the data and a helper list.
#   # In lesson 09 it becomes three lines with a dictionary.


print("=" * 70)
print("Lesson 07 complete. Next: 08_tuples_and_sets.py")
print("=" * 70)

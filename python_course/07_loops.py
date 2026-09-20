"""
===============================================================================
 LESSON 07 — LOOPS: DOING THINGS REPEATEDLY
===============================================================================

Time: about 80 minutes (there's a good place for a break halfway).
Assumes: lessons 01-06.


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. repeat code once for each item in a list: the for loop       (PART 1)
  2. repeat code a set number of times with range()               (PART 2)
  3. number items, and walk two lists side by side                (PART 3)
  4. add up, count and collect things as you go                   (PART 4)
  5. stop a loop early, or skip an item                           (PART 5)
  6. repeat "while" something is true                             (PART 6)

NEW WORDS - come back here whenever you forget one:

  loop          code that runs again and again
  iteration     one trip round a loop (also called a "pass")
  loop variable the name that holds the CURRENT item on each pass:
                in  `for fruit in fruits:`  it's `fruit`
  range()       makes a run of numbers:  range(1, 4)  gives 1, 2, 3
  enumerate()   gives you each item AND its position number
  zip()         walks two lists together, pairing them up
  accumulator   a variable that builds up a result over the loop - a
                running total, a count, a list of matches
  break         "stop the loop right now"
  continue      "skip the rest of this pass, go to the next item"
  while loop    "keep repeating WHILE this condition is True"
  infinite loop a loop that never stops. Press Ctrl+C in the terminal to
                stop one. Nothing breaks - everyone does it
  nested loop   a loop inside another loop


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
#
# What actually happens, step by step:
#   pass 1:  fruit = "apple"   -> print "I have a apple"
#   pass 2:  fruit = "banana"  -> print "I have a banana"
#   pass 3:  fruit = "cherry"  -> print "I have a cherry"
#   no items left -> the loop ends, and Python carries on below it
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

# TRY IT NOW (1 minute):
#   Loop over  ["Sidd", "Ana", "Marco"]  and print  Hello, <name>!  for each.


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
# (list(...) is only there so print shows all the numbers at once.)

# Note again: the stop value is EXCLUDED. range(1, 6) stops at 5. This matches
# slicing, and means range(len(x)) gives exactly the valid indexes of x.

for i in range(3):
    print(f"  attempt {i + 1} of 3")      # i is 0, 1, 2 - so i + 1 is 1, 2, 3
print()

# `_` is the conventional name for "I don't care about the value, I just want
# N repetitions". It's a normal variable name that signals intent.
for _ in range(3):
    print("  tick")
print()

# range() doesn't build a list in memory - it generates numbers as needed. So
# range(10_000_000) costs almost nothing until you loop over it.

# TRY IT NOW (1 minute):
#   Print the numbers 1 to 10 using a for loop and range().
#   (Answer: for n in range(1, 11): print(n)  - the stop 11 is excluded)


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
# In plain English: "for each task, with its position counted from 1..."
for position, task in enumerate(tasks, start=1):
    print(f"  {position}. {task}")
print()

# zip() walks two (or more) collections in step. Perfect for paired data.
names = ["Sidd", "Ana", "Marco"]
scores = [88, 95, 72]

# In plain English: "take the 1st name with the 1st score, then the 2nd with
# the 2nd, and so on"
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
#   total goes 0 -> 1200 -> 2650 -> 3750 -> 5550 -> 7650 -> 9600

# Pattern B - counting matches
big_months = 0
for amount in sales:
    if amount > 1500:
        big_months += 1                 # count this one
print("months over 1500:", big_months)

# Pattern C - collecting into a new list (filtering)
strong = []
for amount in sales:
    if amount > 1500:
        strong.append(amount)           # keep this one
print("the strong months:", strong)

# Pattern D - tracking a best/worst so far
best = sales[0]                         # start with the first as "best so far"
best_index = 0
for index, amount in enumerate(sales):
    if amount > best:                   # found a better one?
        best = amount                   # remember it
        best_index = index              # and where it was
print(f"best: {best} in month {best_index + 1}")

# Pattern E - building a string (join at the end, don't += in the loop)
pieces = []
for index, amount in enumerate(sales, start=1):
    pieces.append(f"M{index}={amount}")
print(" | ".join(pieces))               # glue the pieces with " | " (lesson 02)
print()

# TRY IT NOW (2 minutes):
#   With  marks = [45, 78, 62, 91, 38],  use a loop to count how many marks
#   are 50 or more.  (Answer: 3)


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. The for loop and the accumulator patterns are the
#  heart of this lesson. After the break: stopping early, and while loops.
# -----------------------------------------------------------------------------


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
        break                   # "priya" is never checked

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

# for...else - an unusual feature worth knowing (you can skip it for now).
# The `else` runs ONLY if the loop finished WITHOUT hitting break. It means
# "we searched everything and never found it".
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
# In plain English: "keep trying while we're not connected AND still have tries left"
while not connected and attempt < MAX_ATTEMPTS:
    attempt += 1
    if attempt == 3:                    # pretend the 3rd try works
        connected = True
    print(f"  connection attempt {attempt}: {'success' if connected else 'failed'}")
print()

# TRY IT NOW (1 minute):
#   Write a while loop that prints 10, 8, 6, 4, 2 (start at 10, take 2 off
#   each time, stop when you reach 0).


# =============================================================================
# PART 7 — NESTED LOOPS
# =============================================================================
print(LINE)
print("PART 7 — NESTED LOOPS")
print(LINE)

# A loop inside a loop. The inner loop runs completely for EACH pass of the
# outer one. Use for grids, tables, and comparing every item against every
# other item.

# In plain English: "for each row 1 to 3, go through columns 1 to 3 and print
# row x column - then start a new line"
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
    # Split on spaces, at most 3 times: date, time, level, and the whole message.
    # (maxsplit=3 keeps the message in one piece - lesson 02 PART 6.)
    date, time, level, message = line.split(maxsplit=3)

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

if error_messages:                          # "if the list isn't empty"
    print("\nErrors found:")
    for position, message in enumerate(error_messages, start=1):
        print(f"  {position}. {message}")

    # Was the same error repeated? A duplicate-detection loop.
    # In plain English: "keep a list of messages we've seen; if a message is
    # already in it, it's a repeat".
    seen = []
    repeats = []
    for message in error_messages:
        text = message.split(" ", 1)[1]     # drop the timestamp
        if text in seen:
            repeats.append(text)
        else:
            seen.append(text)
    if repeats:
        print(f"\nRepeated errors (likely one root cause): {repeats}")
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
    pass                        # `pass` means "do nothing" - a placeholder
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
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * for item in collection:  runs the indented block once per item.
#   * range(1, 6) gives 1, 2, 3, 4, 5 - the stop number is excluded.
#   * enumerate() gives position + item; zip() pairs up two lists.
#   * Accumulators: set up BEFORE the loop, update INSIDE, use AFTER.
#   * break stops the loop; continue skips to the next item.
#   * while condition:  repeats until the condition is False. Make sure
#     something inside changes it - or you'll need Ctrl+C.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. How many times does  for i in range(4):  run? What values does i take?
#   Q2. Where must  total = 0  go when adding up a list - inside or before
#       the loop?
#   Q3. What's the difference between break and continue?
#   Q4. What goes wrong here?   n = 3 / while n > 0: print(n)
#   Q5. How do you print "1. apple", "2. pear" from ["apple", "pear"]?
#
# ANSWERS
#   A1. 4 times. i is 0, 1, 2, 3.
#   A2. Before. Inside, it would reset to 0 on every pass.
#   A3. break leaves the loop completely; continue just skips to the next item.
#   A4. n never changes, so it loops forever. Add  n -= 1  inside.
#   A5. for number, fruit in enumerate(["apple", "pear"], start=1):
#           print(f"{number}. {fruit}")


# =============================================================================
# EXERCISES
# =============================================================================
#
# WARM-UP A (easy) — Count to five
#   Use a for loop with range() to print the numbers 1 to 5.
#
# WARM-UP B (easy) — Loud colours
#   Loop over ["red", "green", "blue"] and print each colour in CAPITALS.
#
# WARM-UP C (easy) — Add them up
#   Use an accumulator loop to add up [5, 10, 15] and print the total (30).
#   Don't use sum() - that's the point.
#
# EXERCISE 1 (easy) — Times table
#   Print the 7 times table from 7x1 to 7x12, one per line, neatly aligned.
#
# EXERCISE 2 (medium) — Sum and average without sum()
#   Given [23, 45, 12, 67, 34, 89, 21], use a loop to find the total, the
#   average, the largest and the smallest - without using sum(), max() or
#   min(). This teaches you what those functions actually do.
#   Hint: Pattern A for the total, Pattern D for largest and smallest.
#
# EXERCISE 3 (medium) — Countdown with a twist
#   Count down from 20 to 1, but print "Fizz" instead of any number divisible
#   by 3. Use a while loop.
#
# EXERCISE 4 (medium) — Password retry simulator
#   The correct password is "python123". Given a list of attempts
#   ["letmein", "password", "python123", "other"], loop until it's correct or
#   3 attempts are used up. Print whether access was granted, and stop
#   immediately on success (don't check "other").
#
# EXERCISE 5 (medium) — Invoice report
#   Given this data, print a table with a line per order, then totals:
#       orders = [["Ana", 3, 19.99], ["Marco", 1, 249.00], ["Sidd", 7, 4.50]]
#   Columns: customer, qty, unit price, line total. Then print the grand total
#   and the average order value.
#   Hint: it's the same shape as the table loop in PART 7.
#
# EXERCISE 6 (challenge) — Find the duplicates
#   Given ["a", "b", "c", "b", "d", "a", "a"], print each value that appears
#   more than once, along with how many times.
#
# EXERCISE 7 (medium) — A pyramid
#   Print this shape using a loop:
#       *
#       **
#       ***
#       ****
#       *****
#   Then make it right-aligned (a proper triangle) using string padding.
#
# EXERCISE 8 (challenge) — Word frequency (a real data task)
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
# WARM-UP A
#   for n in range(1, 6):
#       print(n)
#
# WARM-UP B
#   for colour in ["red", "green", "blue"]:
#       print(colour.upper())
#
# WARM-UP C
#   total = 0
#   for number in [5, 10, 15]:
#       total += number
#   print(total)                       # -> 30
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
#       if n % 3 == 0:
#           print("Fizz")
#       else:
#           print(n)
#       n -= 1
#
# EXERCISE 4
#   CORRECT = "python123"
#   attempts = ["letmein", "password", "python123", "other"]
#   granted = False
#   tries = 0
#   for attempt in attempts:
#       tries += 1
#       if attempt == CORRECT:
#           granted = True
#           break                  # success: stop checking
#       if tries == 3:
#           break                  # out of tries
#   if granted:
#       print("Access granted")
#   else:
#       print("Locked out")
#
# EXERCISE 5
#   orders = [["Ana", 3, 19.99], ["Marco", 1, 249.00], ["Sidd", 7, 4.50]]
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
#           continue               # already reported this one
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
#       print(f"{'*' * row:>5}")  # right-align in a space 5 wide (lesson 02)
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

"""
===============================================================================
 LESSON 11 — COMPREHENSIONS AND CLEANER CODE
===============================================================================

Time: about 55 minutes.
Assumes: lessons 01-10.


-------------------------------------------------------------------------------
 THEORY: THE MOST COMMON LOOP IN ALL OF PROGRAMMING
-------------------------------------------------------------------------------

Look at these three loops from earlier lessons:

    doubled = []                     squares = []                 names = []
    for n in numbers:                for n in numbers:            for u in users:
        doubled.append(n * 2)            if n > 0:                    names.append(u["name"])
                                             squares.append(n ** 2)

They're the same shape: make an empty list, loop, append. This pattern -
"transform a collection into another collection" - is so overwhelmingly common
that Python has dedicated syntax for it, called a COMPREHENSION:

    doubled = [n * 2 for n in numbers]
    squares = [n ** 2 for n in numbers if n > 0]
    names   = [u["name"] for u in users]

One line each. Same result.

HOW TO READ ONE: start in the middle, at the `for`.

    [ n * 2      for n in numbers      if n > 0 ]
      ^^^^^          ^^^^^^^^^^^         ^^^^^^
      3. what        1. where each       2. which ones
      to do             item comes          to keep
      with it           from

So: "for each n in numbers, if n is positive, give me n * 2, and collect the
results in a list."


WHY BOTHER?
  * Less code means fewer places for bugs.
  * It states INTENT: "this builds a new list" is visible at a glance, whereas
    a for loop could be doing anything.
  * It's slightly faster than the append version.
  * You cannot read real Python code without knowing them - they're everywhere.

WHEN NOT TO BOTHER (equally important):
  * When the logic needs more than one condition or a nested if/else chain.
  * When the body does several things.
  * When the line gets longer than about 80 characters.
  * When you're doing it for a SIDE EFFECT (printing, writing files) rather
    than building a collection - use a plain loop.

A comprehension you have to squint at is worse than the five-line loop it
replaced. Clever is not the goal; clear is.
"""

LINE = "-" * 70


# =============================================================================
# PART 1 — LIST COMPREHENSIONS
# =============================================================================
print(LINE)
print("PART 1 — BASIC LIST COMPREHENSIONS")
print(LINE)

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# THE LOOP VERSION, for comparison:
doubled_loop = []
for n in numbers:
    doubled_loop.append(n * 2)

# THE COMPREHENSION VERSION:
doubled = [n * 2 for n in numbers]

print("loop version         :", doubled_loop)
print("comprehension version:", doubled)
print("identical?", doubled == doubled_loop)
print()

# Any expression can go in the transform slot:
print("squares      :", [n ** 2 for n in numbers])
print("as strings   :", [str(n) for n in numbers[:5]])
print("formatted    :", [f"#{n:03d}" for n in numbers[:5]])
print()

# Over strings:
word = "Python"
print("letters      :", [letter for letter in word])
print("upper letters:", [letter.upper() for letter in word])
print()

# Over a list of dicts - extracting one field. You'll do this constantly with
# API data:
users = [
    {"name": "Sidd", "age": 22, "active": True},
    {"name": "Ana", "age": 30, "active": False},
    {"name": "Marco", "age": 25, "active": True},
]
print("all names    :", [user["name"] for user in users])
print("all ages     :", [user["age"] for user in users])
print()


# =============================================================================
# PART 2 — FILTERING WITH if
# =============================================================================
print(LINE)
print("PART 2 — FILTERING")
print(LINE)

# Add `if condition` at the END to keep only some items.

print("evens        :", [n for n in numbers if n % 2 == 0])
print("over 5       :", [n for n in numbers if n > 5])
print("evens doubled:", [n * 2 for n in numbers if n % 2 == 0])
print()

# Filtering dicts - the bread and butter of handling web data:
print("active users :", [u["name"] for u in users if u["active"]])
print("over 24      :", [u["name"] for u in users if u["age"] > 24])
print("active AND >24:", [u["name"] for u in users if u["active"] and u["age"] > 24])
print()

# Real cleaning task - discard blanks and normalise in one pass:
raw_emails = ["  Sidd@X.com ", "", "ANA@x.com", "   ", "marco@X.com"]
clean = [e.strip().lower() for e in raw_emails if e.strip()]
print("cleaned      :", clean)
print()


# =============================================================================
# PART 3 — if/else INSIDE A COMPREHENSION (note the different position!)
# =============================================================================
print(LINE)
print("PART 3 — CHOOSING A VALUE WITH if/else")
print(LINE)

# THE POSITION RULE - this trips up everyone:
#
#   [ x for x in items if condition ]                 <- FILTER: if at the END
#   [ a if condition else b for x in items ]          <- CHOOSE: if/else at the
#                                                        START, before the for
#
# They do different jobs. `if` at the end DROPS items. `if/else` at the front
# keeps every item but picks a different value for each.

print("filter (fewer items):", [n for n in numbers if n % 2 == 0])
print("choose (same count) :", ["even" if n % 2 == 0 else "odd" for n in numbers])
print()

# A practical one - categorising scores:
scores = [95, 67, 88, 45, 72]
print("grades:", ["pass" if s >= 70 else "fail" for s in scores])

# Capping values:
print("capped at 80:", [min(s, 80) for s in scores])
print()

# You CAN combine both, though it gets dense fast:
print("non-zero, labelled:",
      ["high" if n > 5 else "low" for n in numbers if n % 2 == 0])
print()


# =============================================================================
# PART 4 — DICT AND SET COMPREHENSIONS
# =============================================================================
print(LINE)
print("PART 4 — DICT AND SET COMPREHENSIONS")
print(LINE)

# Same idea, different brackets.
#   [ ... ]         list
#   { k: v ... }    dict   (note the colon)
#   { ... }         set    (no colon)

# DICT COMPREHENSION - build a lookup table:
squares_map = {n: n ** 2 for n in range(1, 6)}
print("squares map :", squares_map)

# Invert a dictionary (the lesson 09 exercise, in one line):
original = {"a": 1, "b": 2, "c": 3}
print("inverted    :", {value: key for key, value in original.items()})

# Filter a dictionary - keep only some entries:
inventory = {"widgets": 12, "gadgets": 0, "doohickeys": 30, "sprockets": 0}
in_stock = {name: qty for name, qty in inventory.items() if qty > 0}
print("in stock    :", in_stock)

# Transform the values:
prices = {"apple": 1.00, "banana": 0.50}
with_tax = {item: round(price * 1.2, 2) for item, price in prices.items()}
print("with tax    :", with_tax)

# Build a dict from two lists:
keys = ["name", "age", "city"]
values = ["Sidd", 22, "Mumbai"]
print("zipped dict :", {k: v for k, v in zip(keys, values)})
print()

# SET COMPREHENSION - unique results, no duplicates:
words = ["apple", "banana", "avocado", "blueberry", "cherry"]
print("first letters:", {w[0] for w in words})
print("lengths      :", {len(w) for w in words})
print()


# =============================================================================
# PART 5 — NESTED AND MULTI-LOOP COMPREHENSIONS
# =============================================================================
print(LINE)
print("PART 5 — NESTING (handle with care)")
print(LINE)

# Two `for` clauses = a nested loop. Read them LEFT TO RIGHT, outer first.
pairs = [(x, y) for x in [1, 2, 3] for y in ["a", "b"]]
print("all pairs   :", pairs)

# Equivalent to:
#     for x in [1, 2, 3]:
#         for y in ["a", "b"]:
#             pairs.append((x, y))

# FLATTENING a list of lists - the most useful nested case:
table = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [cell for row in table for cell in row]
print("flattened   :", flat)

# A comprehension INSIDE a comprehension builds a nested structure:
grid = [[row * col for col in range(1, 4)] for row in range(1, 4)]
print("times grid  :", grid)

# THE HONEST ADVICE: two levels is the practical limit, and even that deserves
# a comment. Three levels is a write-only construct - you will not understand
# your own code in a month. Use a real loop.
print()


# =============================================================================
# PART 6 — GENERATOR EXPRESSIONS (lazy comprehensions)
# =============================================================================
print(LINE)
print("PART 6 — GENERATOR EXPRESSIONS")
print(LINE)

# Swap the square brackets for round ones and you get a GENERATOR: it produces
# values one at a time, on demand, instead of building the whole list in memory.

list_version = [n ** 2 for n in range(10)]
gen_version = (n ** 2 for n in range(10))

print("list      :", list_version)
print("generator :", gen_version, "<- not computed yet")
print("consumed  :", list(gen_version))
print()

# WHY IT MATTERS: memory. A list of ten million numbers occupies hundreds of
# megabytes. A generator holds one number at a time. When you're scanning a
# multi-gigabyte log file (lesson 13), this is the difference between working
# and crashing.

# The idiomatic use - feeding an aggregate function. No brackets needed when
# the generator is the only argument:
print("sum of squares :", sum(n ** 2 for n in range(1, 11)))
print("any over 50    :", any(n ** 2 > 50 for n in range(1, 11)))
print("all positive   :", all(n > 0 for n in range(1, 11)))
print("count matching :", sum(1 for u in users if u["active"]))
print()

# any() and all() with generators are the clean way to ask "is there at least
# one...?" and "are they all...?" - and they SHORT-CIRCUIT, stopping as soon as
# the answer is known.
passwords = ["hunter2024", "abc", "correcthorse1"]
print("all long enough:", all(len(p) >= 8 for p in passwords))
print("any with digits:", any(any(c.isdigit() for c in p) for p in passwords))
print()

# ONE CATCH: a generator is single-use. Once consumed, it's empty.
gen = (n for n in range(3))
print("first pass :", list(gen))
print("second pass:", list(gen), "<- empty! it's exhausted")
print()


# =============================================================================
# PART 7 — REAL EXAMPLE: A DATA CLEANING PIPELINE
# =============================================================================
print(LINE)
print("PART 7 — REAL EXAMPLE: CLEANING A CSV-LIKE DUMP")
print(LINE)

# Raw, messy input of the sort you actually get handed.
raw_rows = [
    "  101 , Ana  , EU , 249.99 , paid  ",
    "102,Sidd,AS,89.50,paid",
    "",                                      # a blank line
    "103 , Marco , EU , 1200.00 , pending",
    "   ",                                   # whitespace only
    "104,Ana,EU,45.00,paid",
    "105,Zara,US,675.25,refunded",
]

# Step 1 - drop empty lines and split into fields, trimming each one.
rows = [[field.strip() for field in line.split(",")]
        for line in raw_rows if line.strip()]
print(f"parsed {len(rows)} rows from {len(raw_rows)} raw lines")

# Step 2 - convert to dicts with proper types. (A named function keeps the
# comprehension readable - this is the balance to aim for.)
def to_order(row):
    """Turn a list of text fields into a typed dict."""
    order_id, customer, region, amount, status = row
    return {
        "id": int(order_id),
        "customer": customer,
        "region": region,
        "amount": float(amount),
        "status": status,
    }

orders = [to_order(row) for row in rows]

# Step 3 - analyse, using comprehensions and generators throughout.
paid = [o for o in orders if o["status"] == "paid"]
paid_total = sum(o["amount"] for o in paid)
regions = {o["region"] for o in orders}
by_customer = {c: sum(o["amount"] for o in paid if o["customer"] == c)
               for c in {o["customer"] for o in paid}}

print(f"  paid orders   : {len(paid)} of {len(orders)}")
print(f"  paid revenue  : {paid_total:,.2f}")
print(f"  regions seen  : {sorted(regions)}")
print(f"  any over 1000 : {any(o['amount'] > 1000 for o in orders)}")
print("  spend by customer:")
for customer, amount in sorted(by_customer.items(), key=lambda p: -p[1]):
    print(f"    {customer:<8}{amount:>10,.2f}")
print()


# =============================================================================
# PART 8 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 8 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: putting if/else in the filter position (or vice versa).
#     [n for n in nums if n > 5 else 0]    -> SyntaxError
#     [n if n > 5 else 0 for n in nums]    -> correct (choosing)
#     [n for n in nums if n > 5]           -> correct (filtering)

# MISTAKE 2: using one for a side effect.
#     [print(n) for n in numbers]          # works, but builds a useless list
#                                          # of Nones and confuses readers
#   Use a plain for loop when you're not building a collection.

# MISTAKE 3: cramming too much in. If you need a comment to explain your
#   comprehension, write the loop instead. Compare:
#     result = [transform(x) for sub in data for x in sub
#               if check(x) and x.value > threshold and x.kind != "skip"]
#   ...against five clear lines. The loop wins.

# MISTAKE 4: forgetting a generator is single-use. Convert to a list if you
#   need to iterate more than once.

# MISTAKE 5: using a list comprehension where a generator is better. If you
#   only need to sum or scan the values, don't build the whole list first:
#     sum([n ** 2 for n in range(1_000_000)])     # builds a huge list
#     sum(n ** 2 for n in range(1_000_000))       # constant memory

# MISTAKE 6: shadowing an existing name with the loop variable. Since Python 3
#   the comprehension variable is safely scoped to the comprehension - it does
#   NOT leak out - but a name reused across nested comprehensions still confuses
#   readers.
n = "I am safe"
result = [n for n in range(3)]
print("outer n after a comprehension:", n)
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# EXERCISE 1 — Basic transforms
#   Given nums = [3, -1, 4, -1, 5, 9, -2, 6], write comprehensions producing:
#     a) every number cubed
#     b) only the positives
#     c) the absolute value of each
#     d) each as "positive"/"negative"/"zero"
#
# EXERCISE 2 — Text processing
#   Given a sentence, produce:
#     a) a list of word lengths
#     b) only the words longer than 4 characters, uppercased
#     c) a dict mapping each word to its length
#     d) the set of unique first letters
#
# EXERCISE 3 — Rewrite as comprehensions
#   Convert each of these loops into one line:
#       result = []
#       for x in range(20):
#           if x % 3 == 0:
#               result.append(x * x)
#
#       names = {}
#       for user in users:
#           names[user["name"]] = user["age"]
#
# EXERCISE 4 — Filter a table
#   Using the `orders` list from PART 7:
#     a) all order ids over 102
#     b) customer names for EU orders only
#     c) a dict of id -> amount for non-refunded orders
#     d) the total amount of everything NOT paid
#
# EXERCISE 5 — FizzBuzz in one line
#   Produce a list for 1-20 with "Fizz", "Buzz", "FizzBuzz" or the number.
#   (This is a good test of nested if/else. It's also a good demonstration of
#   why the plain loop version is more readable - write both and compare.)
#
# EXERCISE 6 — Matrix work
#   Given matrix = [[1,2,3],[4,5,6],[7,8,9]]:
#     a) flatten it
#     b) get the diagonal [1, 5, 9]
#     c) transpose it (rows become columns)
#     d) double every value, keeping the nested shape
#
# EXERCISE 7 — Generator practice
#   Without building any intermediate lists, calculate: the sum of all even
#   squares under 1000, whether any word in a list is longer than 10
#   characters, and how many of the `users` are inactive.
#
# EXERCISE 8 — Know when to stop
#   Take this comprehension and rewrite it as a readable loop. Which do you
#   prefer, honestly?
#       out = [f"{u['name'].title()} ({u['age']})" for u in users
#              if u["active"] and u["age"] >= 21 and u["name"].strip()]

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   nums = [3, -1, 4, -1, 5, 9, -2, 6]
#   print([n ** 3 for n in nums])
#   print([n for n in nums if n > 0])
#   print([abs(n) for n in nums])
#   print(["positive" if n > 0 else "negative" if n < 0 else "zero" for n in nums])
#
# EXERCISE 2
#   s = "comprehensions make python code shorter and clearer"
#   words = s.split()
#   print([len(w) for w in words])
#   print([w.upper() for w in words if len(w) > 4])
#   print({w: len(w) for w in words})
#   print({w[0] for w in words})
#
# EXERCISE 3
#   result = [x * x for x in range(20) if x % 3 == 0]
#   names = {user["name"]: user["age"] for user in users}
#
# EXERCISE 4
#   print([o["id"] for o in orders if o["id"] > 102])
#   print([o["customer"] for o in orders if o["region"] == "EU"])
#   print({o["id"]: o["amount"] for o in orders if o["status"] != "refunded"})
#   print(sum(o["amount"] for o in orders if o["status"] != "paid"))
#
# EXERCISE 5
#   print(["FizzBuzz" if n % 15 == 0 else "Fizz" if n % 3 == 0
#          else "Buzz" if n % 5 == 0 else str(n) for n in range(1, 21)])
#   # Readable, and honestly better:
#   for n in range(1, 21):
#       if n % 15 == 0: print("FizzBuzz")
#       elif n % 3 == 0: print("Fizz")
#       elif n % 5 == 0: print("Buzz")
#       else: print(n)
#
# EXERCISE 6
#   matrix = [[1,2,3],[4,5,6],[7,8,9]]
#   print([c for row in matrix for c in row])
#   print([matrix[i][i] for i in range(len(matrix))])
#   print([[row[i] for row in matrix] for i in range(len(matrix[0]))])
#   print([[c * 2 for c in row] for row in matrix])
#
# EXERCISE 7
#   print(sum(n ** 2 for n in range(1, 1000) if (n ** 2) % 2 == 0 and n ** 2 < 1000))
#   print(any(len(w) > 10 for w in ["short", "extraordinary"]))
#   print(sum(1 for u in users if not u["active"]))
#
# EXERCISE 8
#   out = []
#   for user in users:
#       if not user["active"]:
#           continue
#       if user["age"] < 21:
#           continue
#       if not user["name"].strip():
#           continue
#       out.append(f"{user['name'].title()} ({user['age']})")
#   # Six lines, but each condition is on its own line, easy to read, easy to
#   # add to, and easy to debug with a print. For three conditions, the loop is
#   # the better engineering choice.


print("=" * 70)
print("Lesson 11 complete. Next: 12_error_handling.py")
print("=" * 70)

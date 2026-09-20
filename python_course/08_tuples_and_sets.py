"""
===============================================================================
 LESSON 08 — TUPLES AND SETS: TWO MORE COLLECTIONS
===============================================================================

Time: about 50 minutes (there's a good place for a break halfway).
Assumes: lessons 01-07.


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. group a few values that belong together forever: a tuple     (PART 1)
  2. keep only UNIQUE values, and check membership fast: a set    (PART 2)
  3. compare two groups: who's in both? who's in only one?        (PART 3)
  4. choose between list, tuple and set                           (PART 4)

NEW WORDS - come back here whenever you forget one:

  tuple         like a list, but in ROUND brackets and it can never change:
                (3, 7)   ("Sidd", 22, "Mumbai")
  immutable     "can't be changed after it's made" - tuples and strings are
  unpacking     taking the values out of a tuple into separate names:
                name, age = ("Sidd", 22)
  set           a collection with NO duplicates and NO order, in curly braces:
                {"python", "web"}
  membership    "is this value in the collection?" - asked with  in
  union         everything in EITHER set          a | b
  intersection  only what's in BOTH sets          a & b
  difference    what's in the first but NOT the second    a - b


-------------------------------------------------------------------------------
 THEORY: WHY MORE THAN ONE KIND OF COLLECTION?
-------------------------------------------------------------------------------

You know lists. Why would Python offer alternatives?

Because "a bunch of values" isn't one idea, it's several, and picking the right
container communicates your intent AND gives you better behaviour for free:

  LIST   [1, 2, 3]     ordered, changeable, duplicates OK
         "A sequence of things that may grow, shrink or be reordered."
         -> a shopping list, rows read from a file, a queue of jobs

  TUPLE  (1, 2, 3)     ordered, FIXED once created, duplicates OK
         "A single record made of several fields, fixed together."
         -> a coordinate (x, y), an RGB colour, a database row, a function
            returning two values

  SET    {1, 2, 3}     UNORDERED, changeable, NO DUPLICATES
         "A collection of unique things where membership is the question."
         -> unique visitors, allowed file extensions, tags, deduplicating

The practical test:
  * Will it change?                     No -> tuple
  * Are duplicates meaningless?         Yes -> set
  * Do you mostly ask "is X in here?"   Yes -> set (it's dramatically faster)
  * Otherwise                           -> list
"""

LINE = "-" * 70


# =============================================================================
# PART 1 — TUPLES: FIXED RECORDS
# =============================================================================
print(LINE)
print("PART 1 — TUPLES")
print(LINE)

# Round brackets instead of square ones.
point = (3, 7)
rgb_red = (255, 0, 0)
person = ("Sidd", 22, "Mumbai")

print("point   :", point)
print("rgb_red :", rgb_red)
print("person  :", person)

# Reading works exactly like a list - same indexing and slicing rules.
print("person[0]:", person[0])
print("person[-1]:", person[-1])
print("person[:2]:", person[:2])
print("len():", len(person))
print()

# THE DIFFERENCE: tuples are IMMUTABLE. There is no append, no remove, and
# assignment to an index fails:
#       person[0] = "Ana"    -> TypeError: 'tuple' object does not support
#                               item assignment
print("Tuples have no .append() - try it and you'll get an AttributeError")

# WHY THAT'S A FEATURE, NOT A LIMITATION:
#   * It documents intent: "these fields belong together and won't change"
#   * It protects you: nothing can accidentally modify it halfway through a
#     program
#   * It makes tuples HASHABLE, so they can be dictionary keys or set members.
#     Lists cannot. (You'll meet this in lesson 09 and it will matter.)
print()

# THE COMMA IS WHAT MAKES A TUPLE, not the brackets:
not_a_tuple = (5)               # just the number 5 in brackets
actually_a_tuple = (5,)         # the trailing comma makes it a 1-item tuple
also_a_tuple = 5, 6, 7          # brackets are optional entirely
print(f"(5) is a {type(not_a_tuple).__name__}")
print(f"(5,) is a {type(actually_a_tuple).__name__}")
print(f"5, 6, 7 is a {type(also_a_tuple).__name__}: {also_a_tuple}")
print()

# UNPACKING is where tuples shine. You've used it since lesson 01:
name, age, city = person        # name = "Sidd", age = 22, city = "Mumbai"
print(f"{name} is {age} and lives in {city}")

# Swapping is tuple packing and unpacking in disguise:
a, b = 1, 2
a, b = b, a
print("swapped:", a, b)

# OPTIONAL EXTRA - the * catches "all the rest". You won't need it often, so
# feel free to skip these four lines:
first, *rest = (1, 2, 3, 4, 5)
print("first:", first, "rest:", rest)      # rest is a LIST
head, *middle, tail = (1, 2, 3, 4, 5)
print("head:", head, "middle:", middle, "tail:", tail)
print()

# RETURNING MULTIPLE VALUES - the most common everyday use of tuples.
# (def makes a function - lesson 10. Read this as: "get_stats takes some
# numbers and gives back THREE answers at once: lowest, highest, average".)
def get_stats(numbers):
    """Functions return one thing - but that one thing can be a tuple."""
    return min(numbers), max(numbers), sum(numbers) / len(numbers)

low, high, average = get_stats([4, 8, 15, 16, 23, 42])   # unpack all three
print(f"low={low} high={high} average={average:.2f}")

# You saw this in lesson 05 too: `return False, "Email is required"`.
print()

# Tuples in a loop - each item unpacked straight into named variables. This is
# the most readable way to handle table data:
inventory = [
    ("Widget", 12, 4.99),
    ("Gadget", 5, 12.50),
    ("Doohickey", 30, 1.25),
]
# In plain English: "for each (name, qty, price) record, print the line value"
for item_name, qty, price in inventory:
    print(f"  {item_name:<12} {qty:>3} @ {price:>6.2f} = {qty * price:>7.2f}")
print()

# TRY IT NOW (1 minute):
#   Make a tuple  date = (2024, 12, 25).  Unpack it into year, month and day,
#   and print an f-string:  Day 25 of month 12, 2024
#   (Answer: year, month, day = date)


# =============================================================================
# PART 2 — SETS: UNIQUENESS AND FAST LOOKUP
# =============================================================================
print(LINE)
print("PART 2 — SETS")
print(LINE)

# Curly braces, or the set() function.
tags = {"python", "beginner", "tutorial"}
print("tags:", tags)

# DUPLICATES VANISH AUTOMATICALLY - this is the headline feature.
with_repeats = {"a", "b", "a", "c", "b", "a"}
print("{'a','b','a','c','b','a'} ->", with_repeats)

# The single most common use: deduplicating a list.
visitors = ["sidd", "ana", "sidd", "marco", "ana", "sidd"]
unique_visitors = set(visitors)         # turn the list into a set: repeats vanish
print(f"{len(visitors)} visits from {len(unique_visitors)} unique people")
print("unique:", unique_visitors)

# Back to a list if you need order/indexing:
print("sorted back to a list:", sorted(unique_visitors))
print()

# SETS ARE UNORDERED. There is no set[0], and the print order may differ from
# what you typed. If order matters, you want a list.
#       unique_visitors[0]   -> TypeError: 'set' object is not subscriptable

# THE EMPTY SET GOTCHA:
print("type of {} is", type({}).__name__, "- that's a DICTIONARY, not a set!")
print("type of set() is", type(set()).__name__, "- use set() for an empty set")
print()

# --- Modifying sets ---
permissions = {"read"}
permissions.add("write")                    # add one  (sets use add, not append)
permissions.update(["delete", "admin"])     # add several
print("after adds:", sorted(permissions))

permissions.discard("admin")        # remove; does NOTHING if absent (safe)
permissions.remove("delete")        # remove; raises KeyError if absent
print("after removes:", sorted(permissions))
print()

# --- The killer feature: membership testing is FAST ---
# `x in a_list` checks items one at a time. On a million-item list that's a
# million comparisons. `x in a_set` jumps almost straight to the answer,
# regardless of size. If you're checking membership repeatedly, use a set.

ALLOWED_EXTENSIONS = {".csv", ".json", ".txt", ".xml"}      # a set, deliberately

files = ["report.csv", "photo.jpg", "data.json", "script.exe"]
for filename in files:
    extension = "." + filename.split(".")[-1]
    verdict = "process" if extension in ALLOWED_EXTENSIONS else "SKIP"
    print(f"  {filename:<14} {extension:<6} -> {verdict}")
print()

# TRY IT NOW (1 minute):
#   Turn  [3, 1, 3, 2, 1, 3]  into a set and print it. How many items are left?
#   (Answer: {1, 2, 3} - three items)


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. Tuples and sets are done. After the break: comparing
#  two sets - the part that makes sets genuinely powerful.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 3 — SET MATHS: COMPARING TWO COLLECTIONS
# =============================================================================
print(LINE)
print("PART 3 — SET OPERATIONS")
print(LINE)

# This is where sets stop being "a list without duplicates" and start being
# genuinely powerful. Answering "what's in A but not B?" with lists takes a
# nested loop. With sets it's one character.

monday = {"sidd", "ana", "marco", "priya"}
tuesday = {"ana", "marco", "zara"}

print("monday :", sorted(monday))
print("tuesday:", sorted(tuesday))
print()
print("UNION        (either day)     :", sorted(monday | tuesday))
print("INTERSECTION (both days)      :", sorted(monday & tuesday))
print("DIFFERENCE   (monday only)    :", sorted(monday - tuesday))
print("DIFFERENCE   (tuesday only)   :", sorted(tuesday - monday))
print("SYMMETRIC    (exactly one day):", sorted(monday ^ tuesday))
print()
#   A way to remember them:  |  "or"   (on Monday OR Tuesday)
#                            &  "and"  (on Monday AND Tuesday)
#                            -  "minus" (Monday, minus anyone from Tuesday)

# Named methods do the same thing and read better in some contexts:
print("union()       :", sorted(monday.union(tuesday)))
print("intersection():", sorted(monday.intersection(tuesday)))
print("difference()  :", sorted(monday.difference(tuesday)))
print()

# Subset / superset questions:
admins = {"sidd"}
print("admins <= monday (all admins came Monday?):", admins <= monday)
print("isdisjoint (no overlap at all?):", monday.isdisjoint({"bob"}))
print()

# REAL USE - a data reconciliation task you'll genuinely hit:
in_database = {"a@x.com", "b@x.com", "c@x.com", "d@x.com"}
in_csv_upload = {"b@x.com", "c@x.com", "e@x.com"}

print("To CREATE (in upload, not in db):", sorted(in_csv_upload - in_database))
print("To DELETE (in db, not in upload):", sorted(in_database - in_csv_upload))
print("To UPDATE (in both)             :", sorted(in_database & in_csv_upload))
# Three lines. With lists and nested loops this would be twenty, and slower.
print()

# TRY IT NOW (2 minutes):
#   likes_tea = {"ana", "sidd", "tom"}      likes_coffee = {"sidd", "zara"}
#   Print who likes both, and who likes tea but not coffee.
#   (Answers: {'sidd'} and {'ana', 'tom'})


# =============================================================================
# PART 4 — CHOOSING THE RIGHT ONE
# =============================================================================
print(LINE)
print("PART 4 — CHOOSING")
print(LINE)

# A quick comparison table, printed so you can see it when you run the file.
rows = [
    ("",                 "list",      "tuple",     "set"),
    ("written as",       "[1, 2]",    "(1, 2)",    "{1, 2}"),
    ("ordered",          "yes",       "yes",       "no"),
    ("changeable",       "yes",       "no",        "yes"),
    ("duplicates",       "yes",       "yes",       "no"),
    ("indexable [0]",    "yes",       "yes",       "no"),
    ("fast 'in' test",   "no",        "no",        "YES"),
    ("dict key allowed", "no",        "yes",       "no"),
]
for label, a_col, b_col, c_col in rows:
    print(f"  {label:<18}{a_col:<12}{b_col:<12}{c_col:<12}")
print()

print("Rules of thumb:")
print("  * Default to a LIST.")
print("  * Use a TUPLE for fixed records and multiple return values.")
print("  * Use a SET for uniqueness and repeated membership checks.")
print("  * Convert freely: list(s), set(l), tuple(l) all work.")
print()


# =============================================================================
# PART 5 — REAL EXAMPLE: DEDUPLICATING AN EMAIL LIST
# =============================================================================
print(LINE)
print("PART 5 — REAL EXAMPLE: CLEANING A MAILING LIST")
print(LINE)

# Messy real-world data: duplicates, inconsistent case, stray whitespace,
# some already unsubscribed.

raw_signups = [
    "  Sidd@Example.com ",
    "ana@example.com",
    "SIDD@example.com",
    "marco@example.com",
    "ana@Example.COM ",
    "priya@example.com",
    "marco@example.com",
]

unsubscribed = {"marco@example.com", "zara@example.com"}

# Normalise first (lesson 02), THEN deduplicate. Order matters: without
# lowercasing, "Sidd@" and "SIDD@" would survive as two different entries.
cleaned = set()
for raw in raw_signups:
    cleaned.add(raw.strip().lower())    # tidy each address, then add it

mailable = cleaned - unsubscribed       # everyone except the unsubscribed

print(f"raw entries        : {len(raw_signups)}")
print(f"after normalising  : {len(cleaned)} unique")
print(f"after unsubscribes : {len(mailable)} mailable")
print()
for address in sorted(mailable):
    print(f"  -> {address}")

removed = cleaned & unsubscribed
print(f"\nSuppressed {len(removed)}: {sorted(removed)}")
print()


# =============================================================================
# PART 6 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 6 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: {} makes an empty dict, not an empty set. Use set().

# MISTAKE 2: expecting a set to keep order. It doesn't. If you need both
#   uniqueness AND order, deduplicate with a loop (lesson 06 exercise 6) or
#   use dict.fromkeys() - a dictionary trick you'll understand after lesson 09:
ordered_unique = list(dict.fromkeys(["b", "a", "b", "c", "a"]))
print("order-preserving dedupe:", ordered_unique)

# MISTAKE 3: trying to put a list inside a set.
#       {[1, 2]}    -> TypeError: unhashable type: 'list'
#   Only immutable things can go in a set. Use a tuple:
print("set of tuples is fine:", {(1, 2), (3, 4)})

# MISTAKE 4: forgetting the trailing comma in a one-item tuple. (5) is an int.

# MISTAKE 5: trying to modify a tuple. If you find yourself wanting to, you
#   wanted a list. (You CAN build a new tuple: t = t + (4,))
original = (1, 2, 3)
extended = original + (4,)
print("new tuple from old:", extended)

# MISTAKE 6: using a list for a big lookup table. If the same collection is
#   tested with `in` inside a loop, convert it to a set once, beforehand.
#   This single change has rescued many painfully slow scripts.
print()


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * A tuple (round brackets) is a fixed record:  point = (3, 7)
#     Read it like a list; you can't change it. Unpack it:  x, y = point
#   * A set (curly braces) keeps only unique values and has no order.
#     set(a_list) removes duplicates in one step.
#   * `x in a_set` is very fast - use sets for "is it allowed?" checks.
#   * a | b (either), a & b (both), a - b (in a but not b).
#   * An empty set is set(), NOT {} - that's an empty dictionary.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. What's the difference between [1, 2] and (1, 2)?
#   Q2. What does  set(["a", "b", "a"])  give?
#   Q3. a = {1, 2, 3},  b = {2, 3, 4}.  What are a & b  and  a - b?
#   Q4. Why can't you write  my_set[0]?
#   Q5. You need to check 10,000 usernames against a banned list. List or set?
#
# ANSWERS
#   A1. The list can change; the tuple can't.
#   A2. {'a', 'b'} - the duplicate "a" disappears.
#   A3. {2, 3} (in both) and {1} (in a but not b).
#   A4. Sets have no order, so there's no "position 0".
#   A5. A set - membership checks are dramatically faster.


# =============================================================================
# EXERCISES
# =============================================================================
#
# WARM-UP A (easy) — A date as a tuple
#   Make  today = (2024, 5, 1)  and print just the year, using today[0].
#
# WARM-UP B (easy) — Remove duplicates
#   Turn [1, 2, 2, 3, 3, 3] into a set and print it.
#
# WARM-UP C (easy) — Is it allowed?
#   fruits = {"apple", "banana"}.  Print whether "apple" is in it, and whether
#   "mango" is in it.
#
# EXERCISE 1 (easy) — Coordinates
#   Store three (x, y) points as tuples in a list. Loop over them, unpacking
#   each into x and y, and print the distance of each from the origin
#   (use (x ** 2 + y ** 2) ** 0.5). Print to 2 decimal places.
#
# EXERCISE 2 (challenge - uses def from lesson 10) — Min, max and average
#   Write a function that takes a list of numbers and returns a tuple of
#   (minimum, maximum, average). Call it and unpack the result into three
#   variables. Hint: copy the shape of get_stats in PART 1.
#
# EXERCISE 3 (medium) — Unique words
#   Given a sentence, print how many words it has in total and how many are
#   unique. Then print the words that appear only once (hint: loop over the
#   unique words and use words.count(word)).
#
# EXERCISE 4 (easy) — Two lists compared
#   last_month = ["ana", "sidd", "marco", "priya"]
#   this_month = ["sidd", "marco", "zara", "tom"]
#   Print: who stayed, who left, who is new, and the total distinct people.
#   Hint: turn both into sets first.
#
# EXERCISE 5 (medium) — Valid extensions filter
#   Given a list of 10 filenames of mixed types, use a set of allowed
#   extensions to split them into two lists: to_process and to_skip.
#
# EXERCISE 6 (medium) — Common interests
#   Three people have sets of hobbies. Print: hobbies ALL three share, hobbies
#   at least two share, and hobbies unique to one person.
#
# EXERCISE 7 (medium) — Swap the data structure
#   Take the word-frequency exercise from lesson 07 (exercise 8) and redo it
#   using a set to track which words you've already counted. Compare how much
#   cleaner it is than the list version.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   today = (2024, 5, 1)
#   print(today[0])                    # -> 2024
#
# WARM-UP B
#   print(set([1, 2, 2, 3, 3, 3]))     # -> {1, 2, 3}
#
# WARM-UP C
#   fruits = {"apple", "banana"}
#   print("apple" in fruits)           # -> True
#   print("mango" in fruits)           # -> False
#
# EXERCISE 1
#   points = [(3, 4), (1, 1), (-5, 12)]
#   for x, y in points:
#       distance = (x ** 2 + y ** 2) ** 0.5     # ** 0.5 is the square root
#       print(f"({x}, {y}) -> {distance:.2f}")
#
# EXERCISE 2
#   def summarise(numbers):
#       return min(numbers), max(numbers), sum(numbers) / len(numbers)
#   lo, hi, avg = summarise([4, 8, 15, 16, 23, 42])
#   print(lo, hi, f"{avg:.2f}")
#
# EXERCISE 3
#   sentence = "the cat sat on the mat the end"
#   words = sentence.split()
#   unique = set(words)
#   print(f"{len(words)} words, {len(unique)} unique")
#   once = []
#   for word in sorted(unique):
#       if words.count(word) == 1:
#           once.append(word)
#   print("appear once:", once)
#
# EXERCISE 4
#   last_month = set(["ana", "sidd", "marco", "priya"])
#   this_month = set(["sidd", "marco", "zara", "tom"])
#   print("stayed:", sorted(last_month & this_month))
#   print("left  :", sorted(last_month - this_month))
#   print("new   :", sorted(this_month - last_month))
#   print("total distinct:", len(last_month | this_month))
#
# EXERCISE 5
#   ALLOWED = {".csv", ".json", ".txt"}
#   files = ["a.csv", "b.jpg", "c.json", "d.exe", "e.txt",
#            "f.csv", "g.pdf", "h.txt", "i.zip", "j.json"]
#   to_process = []
#   to_skip = []
#   for f in files:
#       ext = "." + f.split(".")[-1]
#       if ext in ALLOWED:
#           to_process.append(f)
#       else:
#           to_skip.append(f)
#   print("process:", to_process)
#   print("skip   :", to_skip)
#
# EXERCISE 6
#   ana = {"running", "chess", "cooking"}
#   sidd = {"chess", "coding", "cooking"}
#   marco = {"cooking", "photography", "chess"}
#   print("all three:", sorted(ana & sidd & marco))
#   at_least_two = (ana & sidd) | (sidd & marco) | (ana & marco)
#   print("two or more:", sorted(at_least_two))
#   print("only ana:", sorted(ana - sidd - marco))
#   Read at_least_two as: "shared by ana and sidd, OR by sidd and marco, OR
#   by ana and marco".
#
# EXERCISE 7
#   sentence = "the cat sat on the mat the end"
#   words = sentence.split()
#   for word in set(words):                 # set() does the dedupe for you
#       print(f"{word}: {words.count(word)}")
#   # Still not ideal - .count() rescans the list each time. Lesson 09's
#   # dictionary solves that properly in a single pass.


print("=" * 70)
print("Lesson 08 complete. Next: 09_dictionaries.py")
print("=" * 70)

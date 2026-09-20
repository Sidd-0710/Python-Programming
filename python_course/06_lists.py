"""
===============================================================================
 LESSON 06 — LISTS: STORING MANY THINGS
===============================================================================

Time: about 75 minutes (there's a good place for a break halfway).
Assumes: lessons 01-05.


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. keep many values under ONE name: a list                      (PART 1)
  2. read items by position, or take a chunk                      (PART 2)
  3. add, change and remove items                                 (PART 3)
  4. search, count and sort a list                                (PARTS 4-5)
  5. get totals, averages, biggest and smallest instantly          (PART 6)
  6. avoid the "copy trap" that surprises everyone                 (PART 7)

NEW WORDS - come back here whenever you forget one:

  list          several values in order, inside square brackets:
                [1200, 1450, 1100]     ["Sidd", "Ana"]
  item          one value inside a list (also called an "element")
  index         an item's position. The first item is at index 0
  mutable       "can be changed". Lists are mutable - strings are not
  append        add one item to the END of a list
  sort          put in order: smallest to largest, or A to Z
  in place      changes the ORIGINAL list, instead of making a new one
  nested list   a list inside a list - the way to store a table:
                [["Widget", 12], ["Gadget", 5]]
  for loop      "for each item in the list, do this". Lesson 07 teaches loops
                properly; a few appear here early, always with a plain-English
                note beside them


-------------------------------------------------------------------------------
 THEORY: WHY ONE NAME PER VALUE DOESN'T SCALE
-------------------------------------------------------------------------------

Suppose you're tracking monthly sales. With what you know so far:

    jan = 1200
    feb = 1450
    mar = 1100
    ...

Now try to answer "what's the total?" You'd write jan + feb + mar + ... by
hand. Now add a 13th month - you must edit every calculation. Now imagine
50,000 customer records. The approach collapses completely.

A LIST solves this. It's a single name holding an ordered sequence of values:

    monthly_sales = [1200, 1450, 1100]

One name, any number of values, and Python can visit each one automatically.
This is the first DATA STRUCTURE you'll learn, and it's the one you'll reach
for most often.

THE FOUR PROPERTIES OF A LIST:

  1. ORDERED      - items stay in the order you put them, each at a numbered
                    position (index), counting from 0.
  2. MUTABLE      - you CAN change a list after creating it. (Unlike strings.
                    This difference matters enormously - see PART 7.)
  3. MIXED TYPES  - a list can hold ints, strings, other lists, anything. In
                    practice you usually keep them uniform.
  4. DUPLICATES OK- [1, 1, 1] is a perfectly good list.


WHERE YOU'LL USE THEM FOR YOUR GOALS:
  Data analysis  a column of numbers; a table is a list of rows
  Web backend    the list of posts to render on a page; JSON arrays
  Automation     the list of files in a folder, waiting to be processed
"""

LINE = "-" * 70


# =============================================================================
# PART 1 — CREATING LISTS
# =============================================================================
print(LINE)
print("PART 1 — CREATING LISTS")
print(LINE)

# Square brackets, items separated by commas.
sales = [1200, 1450, 1100, 1800, 2100, 1950]
names = ["Sidd", "Ana", "Marco"]
empty = []                                  # a list with nothing in it yet
mixed = ["Sidd", 22, 1.78, True, None]      # legal, but usually a design smell

print("sales:", sales)
print("names:", names)
print("empty:", empty, "- length", len(empty))
print("mixed:", mixed)

# A list of lists - this is how you represent a TABLE (rows of columns).
# Remember this shape; it's the foundation of the data-analysis lesson.
#   Each inner list is one ROW:  [name, quantity, price]
table = [
    ["Widget", 12, 4.99],
    ["Gadget", 5, 12.50],
    ["Doohickey", 30, 1.25],
]
print("table:", table)

# list() converts other sequences into a list.
print("list('abc'):", list("abc"))              # ['a', 'b', 'c'] - one item per letter
print("list(range(5)):", list(range(5)))        # [0, 1, 2, 3, 4]  - the numbers 0 to 4
print("from split():", "a,b,c".split(","))      # ['a', 'b', 'c'] - lesson 02
print()

# TRY IT NOW (1 minute):
#   Make a list called  friends  with three names in it. Print the list, and
#   print how many names it holds with len().


# =============================================================================
# PART 2 — READING ITEMS: INDEXING AND SLICING
# =============================================================================
print(LINE)
print("PART 2 — INDEXING AND SLICING")
print(LINE)

# Exactly the same rules you learned for strings in lesson 02 - because both
# are SEQUENCES. Learn the rules once, apply everywhere.

print("sales           :", sales)
print("sales[0]        :", sales[0])        # 1200 - FIRST item (not [1]!)
print("sales[2]        :", sales[2])        # 1100
print("sales[-1]       :", sales[-1])       # 1950 - last item
print("sales[-2]       :", sales[-2])       # 2100 - second from last
print("len(sales)      :", len(sales))      # 6

# sales[6] -> IndexError: list index out of range
# Valid indexes are 0 to len-1. This off-by-one catches everyone.

print("sales[1:4]      :", sales[1:4])      # [1450, 1100, 1800] - stop excluded
print("sales[:3]       :", sales[:3])       # first three
print("sales[3:]       :", sales[3:])       # from index 3 to the end
print("sales[-2:]      :", sales[-2:])      # last two
print("sales[::2]      :", sales[::2])      # every second item
print("sales[::-1]     :", sales[::-1])     # reversed copy
print()

# Indexing into a list of lists: first index picks the row, second the column.
#   table[1][0] reads as "row 1, then item 0 of that row"
print("table[1]        :", table[1])        # the whole Gadget row
print("table[1][0]     :", table[1][0])     # 'Gadget' - row 1, column 0
print("table[1][2]     :", table[1][2])     # 12.50 - the price
print()

# TRY IT NOW (1 minute):
#   Predict, then check:  sales[1]   sales[-1]   table[2][0]
#   (Answers: 1450, 1950, 'Doohickey')


# =============================================================================
# PART 3 — CHANGING LISTS (they are mutable)
# =============================================================================
print(LINE)
print("PART 3 — MODIFYING A LIST")
print(LINE)

items = ["apple", "banana", "cherry"]
print("start        :", items)

# Replace by index.
items[1] = "blueberry"          # in plain English: "the item at position 1 becomes blueberry"
print("after [1]=   :", items)

# append() - add ONE item to the end. The workhorse.
items.append("date")
print("after append :", items)

# insert(position, item) - add at a specific spot, shifting everything right.
items.insert(0, "avocado")      # position 0 = the very front
print("after insert :", items)

# extend() - add ALL items from another list.
items.extend(["elderberry", "fig"])
print("after extend :", items)

# NOTE the difference - a classic confusion:
demo_a = [1, 2]
demo_b = [1, 2]
demo_a.append([3, 4])       # adds the LIST as a single item
demo_b.extend([3, 4])       # adds each item separately
print("append([3,4]):", demo_a)     # [1, 2, [3, 4]]  - nested!
print("extend([3,4]):", demo_b)     # [1, 2, 3, 4]    - flat

# remove(value) - delete the FIRST occurrence of a value.
# Note we remove "blueberry", not "banana" - we replaced banana back in the
# first step. Calling .remove("banana") here would raise ValueError.
items.remove("blueberry")
print("after remove :", items)

# pop(index) - remove AND return an item. No index = the last one.
last = items.pop()              # take the last item out, and keep it in `last`
first = items.pop(0)            # take the item at position 0 out
print(f"popped '{last}' and '{first}' :", items)

# del - delete by index or slice.
del items[0]
print("after del[0] :", items)

# clear() - empty it completely.
scratch = [1, 2, 3]
scratch.clear()
print("after clear  :", scratch)
print()

# Unlike string methods (lesson 02), these list methods change the list
# ITSELF. You don't write  items = items.append("x")  - just  items.append("x").

# TRY IT NOW (2 minutes):
#   Start with  colours = ["red", "green"].  Add "blue" to the end, put
#   "black" at the front, then remove "green". Print it after each step.
#   (Final answer: ['black', 'red', 'blue'])


# =============================================================================
# PART 4 — SEARCHING AND COUNTING
# =============================================================================
print(LINE)
print("PART 4 — SEARCHING")
print(LINE)

stock = ["apple", "banana", "apple", "cherry", "apple"]

print("stock              :", stock)
print("'apple' in stock   :", "apple" in stock)          # membership test
print("'mango' in stock   :", "mango" in stock)
print("stock.count('apple'):", stock.count("apple"))     # how many
print("stock.index('cherry'):", stock.index("cherry"))   # position of first

# .index() raises ValueError when the item isn't there. Check first:
if "mango" in stock:
    print(stock.index("mango"))
else:
    print("'mango' isn't in the list - checked before calling .index()")
print()


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. You can now create, read, change and search lists.
#  After the break: sorting, instant statistics, and the copy trap.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 5 — SORTING AND REORDERING
# =============================================================================
print(LINE)
print("PART 5 — SORTING")
print(LINE)

# ***** THE MOST IMPORTANT DISTINCTION IN THIS LESSON *****
#
#   list.sort()    changes the list IN PLACE and returns None
#   sorted(list)   leaves the original alone and returns a NEW sorted list
#
# Both exist because sometimes you want to keep the original order.

numbers = [42, 7, 19, 3, 88]

new_list = sorted(numbers)
print("original after sorted():", numbers)      # unchanged
print("the new sorted list    :", new_list)

numbers.sort()
print("original after .sort() :", numbers)      # changed in place

# THE TRAP:
#       numbers = numbers.sort()     # numbers is now None! .sort() returns
#                                    # nothing. A very common bug.
broken = [3, 1, 2].sort()
print("value of [3,1,2].sort():", broken, "<- None, not a list!")

# Descending order (biggest first):
print("sorted desc  :", sorted([42, 7, 19], reverse=True))

# Sorting strings is alphabetical, with a case gotcha:
words = ["banana", "Apple", "cherry"]
print("sorted words :", sorted(words))                    # capitals first
print("case-insensitive:", sorted(words, key=str.lower))  # usually what you want
#   key=str.lower means "compare each word by its lowercase version".
#   Notice: str.lower with NO brackets - you're handing over the tool, not
#   using it yourself.

# `key` takes a function that produces the value to sort BY. This is how you
# sort a table by a chosen column. Here's a tiny function that picks the price
# out of a row (def is lesson 10 - read it as "price_of_row takes a row and
# gives back item 2 of it"):
def price_of_row(row):
    return row[2]

by_price = sorted(table, key=price_of_row)     # sort the rows by their price
print("table by price:")
# In plain English: "for each row in by_price, print it" (loops: lesson 07)
for row in by_price:
    print("   ", row)
# You'll also see this written as  key=lambda row: row[2]  - a lambda is a
# one-line function with no name. Same thing; lesson 10 covers it.

# reverse() just flips the current order (no sorting involved):
letters = ["a", "b", "c"]
letters.reverse()
print("reversed in place:", letters)
print()

# TRY IT NOW (1 minute):
#   ages = [34, 12, 56, 23].  Print them youngest-first WITHOUT changing ages,
#   then print ages again to prove it's unchanged.
#   (Answer: print(sorted(ages)) then print(ages))


# =============================================================================
# PART 6 — LISTS AND NUMBERS: INSTANT ANALYSIS
# =============================================================================
print(LINE)
print("PART 6 — AGGREGATING")
print(LINE)

monthly_sales = [1200, 1450, 1100, 1800, 2100, 1950]

total = sum(monthly_sales)                      # all added up
count = len(monthly_sales)                      # how many
average = total / count
best = max(monthly_sales)                       # biggest
worst = min(monthly_sales)                      # smallest
best_month = monthly_sales.index(best) + 1      # +1 because months start at 1

print(f"Months   : {count}")
print(f"Total    : {total:,}")
print(f"Average  : {average:,.2f}")
print(f"Best     : {best:,} (month {best_month})")
print(f"Worst    : {worst:,}")
print(f"Range    : {best - worst:,}")

# A text bar chart - three lines of code, genuinely useful output.
# In plain English: "for each month, numbered from 1, draw one # per 100 of
# sales and print it all lined up".
print("\nSales by month:")
for index, amount in enumerate(monthly_sales, start=1):
    bar = "#" * (amount // 100)
    print(f"  Month {index:>2} |{bar:<22}| {amount:>5,}")
print()
# enumerate() hands you the position AND the value on each pass. Lesson 07
# covers it, but it's too useful to hide until then.


# =============================================================================
# PART 7 — THE COPY TRAP (read this twice)
# =============================================================================
print(LINE)
print("PART 7 — ASSIGNMENT DOES NOT COPY")
print(LINE)

# Remember lesson 01: a variable is a NAME TAG pointing at a value. When you
# assign a list to a second name, you are attaching a SECOND TAG TO THE SAME
# LIST. You do not get a copy.

original = [1, 2, 3]
alias = original            # NOT a copy - another name for the same list

alias.append(4)

print("original:", original)     # [1, 2, 3, 4]  <- changed too!
print("alias   :", alias)
print("same object?", original is alias)        # True - one list, two names

# This surprises everyone once, causes a baffling bug, and is then never
# forgotten. `is` asks "are these the same object?", `==` asks "do they have
# equal contents?".

# TO ACTUALLY COPY, use any of these:
a = [1, 2, 3]
copy1 = a.copy()            # clearest
copy2 = a[:]                # slice of everything - older idiom
copy3 = list(a)             # build a new list from it

copy1.append(99)
print("a after copy modified:", a, "- untouched")
print("same object?", a is copy1)               # False
print("equal contents?", a == [1, 2, 3])        # True

# WARNING: these are SHALLOW copies. If your list contains other lists, the
# inner lists are still shared:
nested = [[1, 2], [3, 4]]
shallow = nested.copy()
shallow[0].append(99)
print("nested after editing shallow's inner list:", nested)   # affected!
# For a full independent copy use copy.deepcopy() - see lesson 18.
print()

# TRY IT NOW (1 minute):
#   Run these three lines and explain the output to yourself out loud:
#       x = ["a"]
#       y = x
#       y.append("b")
#       print(x)
#   (It prints ['a', 'b']: x and y are two names for ONE list.)


# =============================================================================
# PART 8 — REAL EXAMPLE: A TASK QUEUE
# =============================================================================
print(LINE)
print("PART 8 — REAL EXAMPLE: PROCESSING A QUEUE")
print(LINE)

# The shape of a real automation script: a list of work, processed one at a
# time, with successes and failures tracked separately.

pending_files = ["report.csv", "data.json", "broken.xyz", "notes.txt"]
ALLOWED = [".csv", ".json", ".txt"]

processed = []
skipped = []

print(f"Starting with {len(pending_files)} files")

# In plain English:
#   while there are still files waiting:
#       take the first one off the front
#       work out its extension (the part after the last dot)
#       if it's allowed, mark it processed; otherwise, mark it skipped
while pending_files:                    # loops while the list isn't empty
    filename = pending_files.pop(0)     # take from the front, like a real queue
    extension = "." + filename.split(".")[-1]   # "report.csv" -> ".csv"

    if extension in ALLOWED:
        processed.append(filename)
        print(f"  processed {filename}")
    else:
        skipped.append(filename)
        print(f"  SKIPPED {filename} (unsupported type {extension})")

print(f"\nDone. {len(processed)} processed, {len(skipped)} skipped.")
print(f"  processed: {processed}")
print(f"  skipped  : {skipped}")
print(f"  remaining: {pending_files}")
print()


# =============================================================================
# PART 9 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 9 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: off-by-one. The last index is len-1, not len.
demo = [10, 20, 30]
print("last item, correctly:", demo[len(demo) - 1], "or better:", demo[-1])

# MISTAKE 2: `numbers = numbers.sort()`. .sort() returns None. Covered in PART 5.

# MISTAKE 3: expecting assignment to copy. Covered in PART 7.

# MISTAKE 4: modifying a list WHILE looping over it. This skips items, because
#   the positions shift under the loop's feet.
bad = [1, 2, 2, 3, 2]
for value in bad[:]:            # loop over a COPY (the [:] slice)...
    if value == 2:
        bad.remove(value)       # ...while modifying the original. Safe.
print("filtered safely:", bad)
#   Even better: build a new list instead (lesson 11's comprehensions).

# MISTAKE 5: calling .index() or .remove() on a value that isn't there.
#   Both raise ValueError. Guard with `in` first, as shown in PART 4.

# MISTAKE 6: using a list when you need fast membership tests. `x in big_list`
#   checks every item one by one. For tens of thousands of lookups, use a set
#   (lesson 08), which is dramatically faster.

# MISTAKE 7: naming a variable `list`. It breaks the built-in list() function
#   for the rest of the file. Use `items`, `rows`, `names`.
print()


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * A list holds many values in order:  scores = [90, 85, 77]
#   * scores[0] is the first item, scores[-1] the last. Slices work like
#     strings.
#   * Lists can change: append (add to end), insert, remove, pop.
#   * `in` checks membership; .count() and .index() search.
#   * sorted(x) gives a NEW sorted list; x.sort() sorts x itself and
#     returns None.
#   * sum, len, max, min turn a list of numbers into statistics instantly.
#   * b = a does NOT copy a list. Use a.copy().
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. nums = [5, 10, 15].  What is nums[1]?  And len(nums)?
#   Q2. After nums.append(20), what is nums?
#   Q3. What's the difference between sorted(nums) and nums.sort()?
#   Q4. a = [1];  b = a;  b.append(2).  What is a?
#   Q5. How do you get the average of a list called marks?
#
# ANSWERS
#   A1. 10 (position 1 is the SECOND item). 3.
#   A2. [5, 10, 15, 20]
#   A3. sorted() returns a new list and leaves nums alone; .sort() changes
#       nums itself and returns None.
#   A4. [1, 2] - a and b are the same list.
#   A5. sum(marks) / len(marks)


# =============================================================================
# EXERCISES
# =============================================================================
#
# WARM-UP A (easy) — Your first list
#   Make a list of 3 colours. Print the list, and print how many there are.
#
# WARM-UP B (easy) — First and last
#   Print the first colour and the last colour from your list.
#
# WARM-UP C (easy) — Add one
#   Append a fourth colour to your list and print the list again.
#
# EXERCISE 1 (easy) — Basics
#   Make a list of 5 of your favourite foods. Print the first, the last, the
#   middle one, how many there are, and the list sorted alphabetically (without
#   changing the original).
#
# EXERCISE 2 (easy) — Shopping list manager
#   Start with ["milk", "eggs", "bread"]. Then: add "coffee" at the end, insert
#   "butter" at the start, remove "eggs", and print the final list plus its
#   length after every step.
#
# EXERCISE 3 (medium) — Statistics
#   Given temps = [18.5, 22.1, 19.8, 25.3, 21.0, 17.2, 23.9]:
#   print the highest, lowest, and average (2dp).
#   CHALLENGE part (needs a loop - lesson 07): also print how many days were
#   above the average.
#
# EXERCISE 4 (challenge - needs a loop from lesson 07) — Second largest
#   Find the second largest number in [42, 7, 88, 19, 88, 3] WITHOUT using
#   sort() on the original list. (Careful: 88 appears twice - the answer
#   should be 42.)
#
# EXERCISE 5 (challenge - needs a loop from lesson 07) — Table work
#   Using the `table` variable from PART 1 (name, qty, price):
#     a) print each row as "Widget: 12 @ 4.99 = 59.88"
#     b) print the grand total value of all stock
#     c) print the name of the most valuable line (qty * price)
#
# EXERCISE 6 (challenge - needs a loop from lesson 07) — Deduplicate
#   Turn ["a", "b", "a", "c", "b", "a"] into ["a", "b", "c"] while keeping the
#   order of first appearance. Build a new list, adding each item only if it
#   isn't already in it.
#
# EXERCISE 7 (medium) — Split a list in half
#   Given any list, print the first half and the second half. Make it work for
#   both even and odd lengths (the middle item can go either way - decide and
#   be consistent).
#   Hint: len(data) // 2 is the middle position.
#
# It's completely fine to do exercises 4-6 AFTER lesson 07. Come back to them.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   colours = ["red", "green", "blue"]
#   print(colours, len(colours))       # -> ['red', 'green', 'blue'] 3
#
# WARM-UP B
#   print(colours[0], colours[-1])     # -> red blue
#
# WARM-UP C
#   colours.append("yellow")
#   print(colours)
#
# EXERCISE 1
#   foods = ["dosa", "ramen", "pizza", "biryani", "tacos"]
#   print(foods[0], foods[-1], foods[len(foods) // 2])
#   print(len(foods))
#   print(sorted(foods))
#   print(foods)          # proof the original is unchanged
#
# EXERCISE 2
#   shopping = ["milk", "eggs", "bread"]
#   shopping.append("coffee")
#   print(shopping, len(shopping))
#   shopping.insert(0, "butter")
#   print(shopping, len(shopping))
#   shopping.remove("eggs")
#   print(shopping, len(shopping))
#
# EXERCISE 3
#   temps = [18.5, 22.1, 19.8, 25.3, 21.0, 17.2, 23.9]
#   avg = sum(temps) / len(temps)
#   print(f"high {max(temps)} low {min(temps)} avg {avg:.2f}")
#   # the challenge part:
#   above = 0
#   for t in temps:                    # "for each temperature..."
#       if t > avg:                    # "...if it's above the average..."
#           above += 1                 # "...count it"
#   print(f"{above} days above average")
#
# EXERCISE 4
#   nums = [42, 7, 88, 19, 88, 3]
#   biggest = max(nums)
#   the_rest = []
#   for n in nums:
#       if n != biggest:               # leave out EVERY copy of the biggest
#           the_rest.append(n)
#   print(max(the_rest))               # -> 42
#
# EXERCISE 5
#   grand_total = 0
#   best_name = ""
#   best_value = 0
#   for row in table:
#       name = row[0]
#       qty = row[1]
#       price = row[2]
#       value = qty * price
#       grand_total += value
#       print(f"{name}: {qty} @ {price:.2f} = {value:.2f}")
#       if value > best_value:
#           best_name = name
#           best_value = value
#   print(f"Grand total: {grand_total:.2f}")
#   print(f"Most valuable: {best_name} ({best_value:.2f})")
#
# EXERCISE 6
#   source = ["a", "b", "a", "c", "b", "a"]
#   unique = []
#   for item in source:
#       if item not in unique:
#           unique.append(item)
#   print(unique)                      # -> ['a', 'b', 'c']
#
# EXERCISE 7
#   data = [1, 2, 3, 4, 5, 6, 7]
#   middle = len(data) // 2            # 7 // 2 = 3
#   print("first half :", data[:middle])     # [1, 2, 3]
#   print("second half:", data[middle:])     # [4, 5, 6, 7] - odd middle goes right


print("=" * 70)
print("Lesson 06 complete. Next: 07_loops.py")
print("=" * 70)

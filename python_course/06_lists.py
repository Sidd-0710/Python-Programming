"""
===============================================================================
 LESSON 06 — LISTS: STORING MANY THINGS
===============================================================================

Time: about 75 minutes.
Assumes: lessons 01-05.


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
table = [
    ["Widget", 12, 4.99],
    ["Gadget", 5, 12.50],
    ["Doohickey", 30, 1.25],
]
print("table:", table)

# list() converts other sequences into a list.
print("list('abc'):", list("abc"))              # ['a', 'b', 'c']
print("list(range(5)):", list(range(5)))        # [0, 1, 2, 3, 4]
print("from split():", "a,b,c".split(","))      # ['a', 'b', 'c']
print()


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
print("table[1]        :", table[1])        # the whole Gadget row
print("table[1][0]     :", table[1][0])     # 'Gadget' - row 1, column 0
print("table[1][2]     :", table[1][2])     # 12.50 - the price
print()


# =============================================================================
# PART 3 — CHANGING LISTS (they are mutable)
# =============================================================================
print(LINE)
print("PART 3 — MODIFYING A LIST")
print(LINE)

items = ["apple", "banana", "cherry"]
print("start        :", items)

# Replace by index.
items[1] = "blueberry"
print("after [1]=   :", items)

# append() - add ONE item to the end. The workhorse.
items.append("date")
print("after append :", items)

# insert(position, item) - add at a specific spot, shifting everything right.
items.insert(0, "avocado")
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
last = items.pop()
first = items.pop(0)
print(f"popped '{last}' and '{first}' :", items)

# del - delete by index or slice.
del items[0]
print("after del[0] :", items)

# clear() - empty it completely.
scratch = [1, 2, 3]
scratch.clear()
print("after clear  :", scratch)
print()


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

# Descending order:
print("sorted desc  :", sorted([42, 7, 19], reverse=True))

# Sorting strings is alphabetical, with a case gotcha:
words = ["banana", "Apple", "cherry"]
print("sorted words :", sorted(words))                    # capitals first
print("case-insensitive:", sorted(words, key=str.lower))  # usually what you want

# `key` takes a function that produces the value to sort BY. This is how you
# sort a table by a chosen column - sort rows by price (index 2):
by_price = sorted(table, key=lambda row: row[2])
print("table by price:")
for row in by_price:
    print("   ", row)
# `lambda row: row[2]` is a tiny throwaway function meaning "given a row, use
# its item at index 2". Lesson 10 covers lambda properly.

# reverse() just flips the current order (no sorting involved):
letters = ["a", "b", "c"]
letters.reverse()
print("reversed in place:", letters)
print()


# =============================================================================
# PART 6 — LISTS AND NUMBERS: INSTANT ANALYSIS
# =============================================================================
print(LINE)
print("PART 6 — AGGREGATING")
print(LINE)

monthly_sales = [1200, 1450, 1100, 1800, 2100, 1950]

total = sum(monthly_sales)
count = len(monthly_sales)
average = total / count
best = max(monthly_sales)
worst = min(monthly_sales)
best_month = monthly_sales.index(best) + 1      # +1 because months start at 1

print(f"Months   : {count}")
print(f"Total    : {total:,}")
print(f"Average  : {average:,.2f}")
print(f"Best     : {best:,} (month {best_month})")
print(f"Worst    : {worst:,}")
print(f"Range    : {best - worst:,}")

# A text bar chart - three lines of code, genuinely useful output.
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

while pending_files:                    # loops while the list isn't empty
    filename = pending_files.pop(0)     # take from the front, like a real queue
    extension = "." + filename.split(".")[-1]

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
# EXERCISES
# =============================================================================
#
# EXERCISE 1 — Basics
#   Make a list of 5 of your favourite foods. Print the first, the last, the
#   middle one, how many there are, and the list sorted alphabetically (without
#   changing the original).
#
# EXERCISE 2 — Shopping list manager
#   Start with ["milk", "eggs", "bread"]. Then: add "coffee" at the end, insert
#   "butter" at the start, remove "eggs", and print the final list plus its
#   length after every step.
#
# EXERCISE 3 — Statistics
#   Given temps = [18.5, 22.1, 19.8, 25.3, 21.0, 17.2, 23.9]:
#   print the highest, lowest, average (2dp), and how many days were above
#   the average.
#
# EXERCISE 4 — Second largest
#   Find the second largest number in [42, 7, 88, 19, 88, 3] WITHOUT using
#   sort() on the original list. (Careful: 88 appears twice - the answer
#   should be 42.)
#
# EXERCISE 5 — Table work (data analysis prep)
#   Using the `table` variable from PART 1 (name, qty, price):
#     a) print each row as "Widget: 12 @ 4.99 = 59.88"
#     b) print the grand total value of all stock
#     c) print the name of the most valuable line (qty * price)
#
# EXERCISE 6 — Deduplicate, preserving order
#   Turn ["a", "b", "a", "c", "b", "a"] into ["a", "b", "c"] while keeping the
#   order of first appearance. (set() would lose the order - do it with a loop
#   and a new list.)
#
# EXERCISE 7 — Split a list in half
#   Given any list, print the first half and the second half. Make it work for
#   both even and odd lengths (the middle item can go either way - decide and
#   be consistent).

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
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
#   shopping.append("coffee");  print(shopping, len(shopping))
#   shopping.insert(0, "butter"); print(shopping, len(shopping))
#   shopping.remove("eggs");    print(shopping, len(shopping))
#
# EXERCISE 3
#   temps = [18.5, 22.1, 19.8, 25.3, 21.0, 17.2, 23.9]
#   avg = sum(temps) / len(temps)
#   print(f"high {max(temps)} low {min(temps)} avg {avg:.2f}")
#   above = [t for t in temps if t > avg]
#   print(f"{len(above)} days above average")
#
# EXERCISE 4
#   nums = [42, 7, 88, 19, 88, 3]
#   unique_sorted = sorted(set(nums))       # set() drops duplicates
#   print(unique_sorted[-2])                # -> 42
#   # or without set():
#   biggest = max(nums)
#   print(max(n for n in nums if n != biggest))
#
# EXERCISE 5
#   grand_total = 0
#   best_name, best_value = "", 0
#   for name, qty, price in table:
#       value = qty * price
#       grand_total += value
#       print(f"{name}: {qty} @ {price:.2f} = {value:.2f}")
#       if value > best_value:
#           best_name, best_value = name, value
#   print(f"Grand total: {grand_total:.2f}")
#   print(f"Most valuable: {best_name} ({best_value:.2f})")
#
# EXERCISE 6
#   source = ["a", "b", "a", "c", "b", "a"]
#   unique = []
#   for item in source:
#       if item not in unique:
#           unique.append(item)
#   print(unique)
#
# EXERCISE 7
#   data = [1, 2, 3, 4, 5, 6, 7]
#   middle = len(data) // 2
#   print("first half :", data[:middle])
#   print("second half:", data[middle:])    # odd middle item goes right


print("=" * 70)
print("Lesson 06 complete. Next: 07_loops.py")
print("=" * 70)

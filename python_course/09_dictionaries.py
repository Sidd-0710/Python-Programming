"""
===============================================================================
 LESSON 09 — DICTIONARIES: LOOKING THINGS UP BY NAME
===============================================================================

Time: about 80 minutes.
Assumes: lessons 01-08.

This is the most important data structure in Python. If you only truly master
one thing from this course, make it this lesson.


-------------------------------------------------------------------------------
 THEORY: THE PROBLEM WITH POSITIONS
-------------------------------------------------------------------------------

With a list, you find things by POSITION:

    user = ["Sidd", 22, "sidd@example.com"]
    print(user[2])      # the email... probably? Is it index 1 or 2?

That works until it doesn't. Position-based access is fragile:
  * you must remember what each index means
  * insert a field at the start and every index in your program shifts
  * `user[2]` tells a reader nothing about what it holds

A DICTIONARY finds things by NAME instead:

    user = {"name": "Sidd", "age": 22, "email": "sidd@example.com"}
    print(user["email"])        # unambiguous, self-documenting, stable

Every entry is a KEY-VALUE PAIR. The key is the label you look up by; the
value is what you get back.

THINK OF IT AS: a real dictionary (look up a word, get its definition), a phone
contacts app (look up a name, get a number), or a labelled filing cabinet.


-------------------------------------------------------------------------------
 WHY THIS IS THE MOST IMPORTANT ONE
-------------------------------------------------------------------------------

  WEB BACKEND     JSON - the language every web API speaks - is literally
                  dictionaries and lists nested together. An API response
                  BECOMES a Python dictionary. Handling web data IS handling
                  dictionaries.

  DATA ANALYSIS   Counting, grouping and tallying are all dictionary jobs.
                  Every "count how many of each" problem is a dict.

  AUTOMATION      Configuration and settings are dictionaries. So is "which
                  files have I already processed?".

  SPEED           Looking up a key is near-instant no matter how big the dict
                  is - the same trick that makes sets fast.
"""

LINE = "-" * 70


# =============================================================================
# PART 1 — CREATING AND READING
# =============================================================================
print(LINE)
print("PART 1 — CREATING AND READING")
print(LINE)

# Curly braces, with key: value pairs separated by commas.
user = {
    "name": "Sidd",
    "age": 22,
    "email": "sidd@example.com",
    "is_active": True,
}

print("the whole dict:", user)
print("user['name'] :", user["name"])
print("user['age']  :", user["age"])
print("len(user)    :", len(user), "pairs")
print()

# Keys are usually strings, but any IMMUTABLE value works: int, float, str,
# tuple, bool. NOT lists or other dicts (this is why tuples being immutable
# mattered in lesson 08).
mixed_keys = {
    "text key": 1,
    42: "an int key",
    (0, 0): "a tuple key - the origin point",
}
print("mixed keys:", mixed_keys)
print("looked up by tuple:", mixed_keys[(0, 0)])
print()

# Other ways to build one:
empty = {}                                          # empty dict
from_pairs = dict([("a", 1), ("b", 2)])             # from a list of tuples
from_kwargs = dict(name="Ana", age=30)              # keyword style
from_zip = dict(zip(["x", "y"], [10, 20]))          # pairing two lists
print("from_pairs :", from_pairs)
print("from_kwargs:", from_kwargs)
print("from_zip   :", from_zip)
print()


# =============================================================================
# PART 2 — MISSING KEYS: THE MOST COMMON DICT ERROR
# =============================================================================
print(LINE)
print("PART 2 — HANDLING MISSING KEYS")
print(LINE)

# Square brackets on a key that doesn't exist CRASHES:
#       user["phone"]     -> KeyError: 'phone'
#
# That's correct behaviour when the key SHOULD be there (a crash beats silent
# wrongness). But often "missing" is a perfectly normal case, and you want a
# default instead.

# .get() returns None instead of raising:
print("user.get('phone')          :", user.get("phone"))

# .get() with a fallback value - this is the one you'll use constantly:
print("user.get('phone', 'n/a')   :", user.get("phone", "n/a"))
print("user.get('name', 'n/a')    :", user.get("name", "n/a"))

# Check membership with `in` (it checks KEYS, not values):
print("'email' in user            :", "email" in user)
print("'phone' in user            :", "phone" in user)
print()

# WHEN TO USE WHICH:
#   user["email"]            when a missing key is a genuine bug - let it crash
#   user.get("phone", "")    when a missing key is expected and has a sensible
#                            default
# Choosing deliberately is a mark of code that's been thought about.

# Real example - handling an API response where fields are optional:
api_response = {"id": 42, "title": "Hello World", "author": "sidd"}

print(f"Post #{api_response['id']}: {api_response['title']}")
print(f"  by {api_response.get('author', 'anonymous')}")
print(f"  tags: {api_response.get('tags', [])}")          # safe default: []
print(f"  views: {api_response.get('views', 0):,}")       # safe default: 0
print()


# =============================================================================
# PART 3 — ADDING, CHANGING, REMOVING
# =============================================================================
print(LINE)
print("PART 3 — MODIFYING")
print(LINE)

settings = {"theme": "dark", "font_size": 14}
print("start          :", settings)

# Assigning to a key ADDS it if new, REPLACES it if it exists. Same syntax for
# both - there's no separate "add" operation.
settings["language"] = "en"             # new key
settings["font_size"] = 16              # existing key, overwritten
print("after adding   :", settings)

# update() merges another dict in (later values win on conflict).
settings.update({"theme": "light", "autosave": True})
print("after update   :", settings)

# The | operator merges into a NEW dict (Python 3.9+), leaving originals alone:
defaults = {"theme": "dark", "font_size": 12, "autosave": False}
user_prefs = {"theme": "solarized"}
final = defaults | user_prefs           # user_prefs wins where they overlap
print("merged defaults:", final)
# THIS IS A REAL PATTERN: start with defaults, layer the user's choices on top.

# Removing:
removed = settings.pop("autosave")       # remove AND return the value
print(f"popped 'autosave' = {removed}")
del settings["language"]                 # remove, discard the value
settings.pop("missing_key", None)        # safe - won't raise if absent
print("after removals :", settings)
print()


# =============================================================================
# PART 4 — LOOPING OVER DICTIONARIES
# =============================================================================
print(LINE)
print("PART 4 — LOOPING")
print(LINE)

inventory = {"widgets": 12, "gadgets": 5, "doohickeys": 30, "sprockets": 0}

# Looping the dict directly gives you the KEYS:
print("keys:")
for key in inventory:
    print(f"  {key}")
print()

# .values() gives just the values:
print("total stock:", sum(inventory.values()))
print()

# .items() gives (key, value) tuples - USE THIS ONE. It's what you want 95%
# of the time, and it unpacks neatly into two named variables.
print("items:")
for product, quantity in inventory.items():
    status = "IN STOCK" if quantity > 0 else "OUT OF STOCK"
    print(f"  {product:<12} {quantity:>3}  {status}")
print()

# Sorting a dictionary means sorting its items and choosing a key function.
print("sorted by name:")
for product, quantity in sorted(inventory.items()):
    print(f"  {product:<12} {quantity:>3}")

print("\nsorted by quantity, highest first:")
for product, quantity in sorted(inventory.items(),
                                key=lambda pair: pair[1],
                                reverse=True):
    print(f"  {product:<12} {quantity:>3}")
# `lambda pair: pair[1]` means "sort by the second element of each pair", i.e.
# the value rather than the key. Lesson 10 explains lambda.

# Dictionaries keep insertion order (guaranteed since Python 3.7). They are not
# sorted - they simply remember the order you added things in.
print()


# =============================================================================
# PART 5 — COUNTING AND GROUPING (the two killer patterns)
# =============================================================================
print(LINE)
print("PART 5 — COUNTING AND GROUPING")
print(LINE)

# Remember the awkward word-count exercise from lesson 07? Here it is properly.

sentence = "the cat sat on the mat and the cat slept on the mat"
words = sentence.split()

# PATTERN 1 - COUNTING
counts = {}
for word in words:
    # "get the current count (0 if we've never seen it), add 1, store it back"
    counts[word] = counts.get(word, 0) + 1

print("word counts:", counts)

print("\nmost frequent first:")
for word, count in sorted(counts.items(), key=lambda pair: pair[1], reverse=True):
    bar = "#" * count
    print(f"  {word:<8} {count}  {bar}")
print()

# That `counts[word] = counts.get(word, 0) + 1` line is worth memorising. It is
# the single most reused line in data work. There's also a purpose-built tool:
from collections import Counter
print("with Counter:", Counter(words).most_common(3))
# Counter is part of the standard library - lesson 18 covers more of these.
print()

# PATTERN 2 - GROUPING
# Turning a flat list into categories. The value is a LIST that you append to.
people = [
    ("Sidd", "Mumbai"),
    ("Ana", "Lisbon"),
    ("Marco", "Lisbon"),
    ("Priya", "Mumbai"),
    ("Zara", "Berlin"),
]

by_city = {}
for name, city in people:
    if city not in by_city:
        by_city[city] = []              # create the empty list on first sight
    by_city[city].append(name)

print("grouped by city:")
for city, residents in sorted(by_city.items()):
    print(f"  {city:<8} ({len(residents)}): {', '.join(residents)}")

# setdefault() does the "create if missing" step in one line:
by_city2 = {}
for name, city in people:
    by_city2.setdefault(city, []).append(name)
print("same result via setdefault:", by_city2 == by_city)
print()


# =============================================================================
# PART 6 — NESTED STRUCTURES (this is what JSON looks like)
# =============================================================================
print(LINE)
print("PART 6 — NESTING: DICTS INSIDE LISTS INSIDE DICTS")
print(LINE)

# Real data is nested. This structure - a dict containing a list of dicts - is
# EXACTLY the shape of a typical web API response. Learn to navigate it and
# you can handle almost any API.

blog = {
    "site": "Sidd's Notes",
    "author": {
        "name": "Sidd",
        "email": "sidd@example.com",
    },
    "posts": [
        {"id": 1, "title": "Learning Python", "views": 1520, "tags": ["python", "beginner"]},
        {"id": 2, "title": "Why Loops Matter", "views": 890, "tags": ["python"]},
        {"id": 3, "title": "Deploying Flask", "views": 2340, "tags": ["python", "web", "flask"]},
    ],
}

# Navigate one step at a time, left to right:
print("site        :", blog["site"])
print("author name :", blog["author"]["name"])          # dict inside dict
print("first post  :", blog["posts"][0]["title"])       # list inside dict
print("its 2nd tag :", blog["posts"][0]["tags"][1])     # list inside dict
                                                        # inside list inside dict

# READING THAT CHAIN: blog -> "posts" key -> item 0 -> "tags" key -> item 1.
# When you get lost, print the intermediate steps:
#       print(blog["posts"])
#       print(blog["posts"][0])
# and work down until you see the piece you want.
print()

# Now do something useful with it:
total_views = 0
all_tags = set()

print("Posts:")
for post in blog["posts"]:
    total_views += post["views"]
    all_tags.update(post["tags"])
    print(f"  [{post['id']}] {post['title']:<20} {post['views']:>6,} views")

print(f"\nTotal views : {total_views:,}")
print(f"Average     : {total_views / len(blog['posts']):,.0f}")
print(f"All tags    : {sorted(all_tags)}")

most_popular = max(blog["posts"], key=lambda post: post["views"])
print(f"Most popular: {most_popular['title']} ({most_popular['views']:,})")
print()

# NOTE ON QUOTES INSIDE f-STRINGS: older Python versions can't reuse the same
# quote style inside the braces, which is why you'll see {post['id']} with
# single quotes inside a double-quoted f-string. Modern Python (3.12+) allows
# either, but the mixed style is still the safest habit.


# =============================================================================
# PART 7 — REAL EXAMPLE: SALES ANALYSIS
# =============================================================================
print(LINE)
print("PART 7 — REAL EXAMPLE: ANALYSING ORDERS")
print(LINE)

orders = [
    {"id": 101, "customer": "Ana",   "region": "EU", "amount": 249.99, "status": "paid"},
    {"id": 102, "customer": "Sidd",  "region": "AS", "amount": 89.50,  "status": "paid"},
    {"id": 103, "customer": "Marco", "region": "EU", "amount": 1200.00, "status": "pending"},
    {"id": 104, "customer": "Ana",   "region": "EU", "amount": 45.00,  "status": "paid"},
    {"id": 105, "customer": "Zara",  "region": "US", "amount": 675.25, "status": "refunded"},
    {"id": 106, "customer": "Sidd",  "region": "AS", "amount": 330.00, "status": "paid"},
]

# Revenue per region - the counting pattern, with sums instead of counts.
revenue_by_region = {}
orders_by_status = {}
spend_by_customer = {}

for order in orders:
    region = order["region"]
    status = order["status"]
    customer = order["customer"]
    amount = order["amount"]

    orders_by_status[status] = orders_by_status.get(status, 0) + 1

    if status == "paid":                        # only count real revenue
        revenue_by_region[region] = revenue_by_region.get(region, 0) + amount
        spend_by_customer[customer] = spend_by_customer.get(customer, 0) + amount

print("Orders by status:")
for status, count in sorted(orders_by_status.items()):
    print(f"  {status:<10} {count}")

print("\nPaid revenue by region:")
for region, amount in sorted(revenue_by_region.items(),
                             key=lambda pair: pair[1], reverse=True):
    print(f"  {region:<4} {amount:>10,.2f}")

print("\nTop customers:")
for customer, amount in sorted(spend_by_customer.items(),
                               key=lambda pair: pair[1], reverse=True):
    print(f"  {customer:<8} {amount:>10,.2f}")

paid_total = sum(revenue_by_region.values())
print(f"\nTotal paid revenue: {paid_total:,.2f}")
print(f"Average paid order: {paid_total / orders_by_status['paid']:,.2f}")
print()


# =============================================================================
# PART 8 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 8 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: KeyError from assuming a key exists. Use .get() with a default
#   whenever the key is genuinely optional.

# MISTAKE 2: using a list as a key.
#       {[1, 2]: "x"}    -> TypeError: unhashable type: 'list'
#   Keys must be immutable. Use a tuple.

# MISTAKE 3: `in` checks KEYS, not values.
prices = {"apple": 1.20, "banana": 0.50}
print("'apple' in prices  :", "apple" in prices)          # True (a key)
print("1.20 in prices     :", 1.20 in prices)             # False!
print("1.20 in values     :", 1.20 in prices.values())    # True

# MISTAKE 4: duplicate keys in a literal - the last one silently wins.
dupes = {"a": 1, "b": 2, "a": 3}
print("duplicate key result:", dupes)              # {'a': 3, 'b': 2}

# MISTAKE 5: modifying a dict while looping over it -> RuntimeError.
#   Loop over a copy of the keys instead:
stock = {"a": 0, "b": 5, "c": 0}
for key in list(stock.keys()):          # list() makes a snapshot
    if stock[key] == 0:
        del stock[key]
print("after removing zero stock:", stock)

# MISTAKE 6: assignment doesn't copy (same trap as lists).
a = {"x": 1}
b = a                   # another name for the SAME dict
b["y"] = 2
print("a is affected:", a)
c = a.copy()            # a real (shallow) copy
c["z"] = 3
print("a is not affected by c:", a)

# MISTAKE 7: deeply chained lookups that crash on one missing key.
#       data["user"]["address"]["city"]     -> KeyError if any step is missing
#   Chain .get() with defaults when the data is untrusted:
data = {"user": {"name": "Sidd"}}
city = data.get("user", {}).get("address", {}).get("city", "unknown")
print("safely dug out city:", city)
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# EXERCISE 1 — Contact card
#   Build a dict describing you (name, age, city, skills as a list). Print each
#   key and value on its own line using .items(). Then add a new key, change an
#   existing one, and delete one.
#
# EXERCISE 2 — Phone book
#   Create a phone book dict. Write code that looks up a name and prints the
#   number, or "not found" if it's missing - without crashing.
#
# EXERCISE 3 — Letter frequency
#   Count how many times each LETTER appears in "mississippi river". Ignore
#   spaces. Print the results sorted by count, highest first.
#
# EXERCISE 4 — Grade book
#   grades = {"Ana": [88, 92, 79], "Sidd": [95, 68, 84], "Marco": [72, 75, 91]}
#   For each student print their average to 1dp and their best score. Then
#   print the name of the student with the highest overall average.
#
# EXERCISE 5 — Group by first letter
#   Given a list of 10+ names, build a dict mapping each first letter to the
#   list of names starting with it. Print it sorted by letter.
#
# EXERCISE 6 — Shopping cart (web backend practice)
#   cart = {"apple": 3, "bread": 1, "cheese": 2}
#   prices = {"apple": 0.50, "bread": 2.20, "cheese": 4.75, "milk": 1.10}
#   Print a receipt with a line per item (qty, unit price, line total) and a
#   grand total. Handle gracefully the case where a cart item has no price.
#
# EXERCISE 7 — API response digging
#   Using the `blog` dict from PART 6:
#     a) print every post title that has the tag "python"
#     b) print the total number of distinct tags
#     c) print posts sorted by views, lowest first
#     d) add a new post to the list, then re-run your total-views calculation
#
# EXERCISE 8 — Invert a dictionary
#   Given {"a": 1, "b": 2, "c": 3}, produce {1: "a", 2: "b", 3: "c"}.
#   Then think about what happens if two keys share a value, and handle it by
#   making the inverted values lists.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   me = {"name": "Sidd", "age": 22, "city": "Mumbai",
#         "skills": ["python", "sql"]}
#   for key, value in me.items():
#       print(f"{key:<8}: {value}")
#   me["country"] = "India"
#   me["age"] = 23
#   del me["city"]
#
# EXERCISE 2
#   book = {"Ana": "555-0101", "Sidd": "555-0102"}
#   name = "Marco"
#   print(book.get(name, "not found"))
#
# EXERCISE 3
#   text = "mississippi river".replace(" ", "")
#   freq = {}
#   for letter in text:
#       freq[letter] = freq.get(letter, 0) + 1
#   for letter, count in sorted(freq.items(), key=lambda p: p[1], reverse=True):
#       print(f"{letter}: {count}")
#
# EXERCISE 4
#   grades = {"Ana": [88, 92, 79], "Sidd": [95, 68, 84], "Marco": [72, 75, 91]}
#   averages = {}
#   for student, scores in grades.items():
#       avg = sum(scores) / len(scores)
#       averages[student] = avg
#       print(f"{student:<6} avg {avg:.1f} best {max(scores)}")
#   top = max(averages, key=averages.get)
#   print("Top student:", top)
#
# EXERCISE 5
#   names = ["Ana", "Sidd", "Sam", "Marco", "Mia", "Priya",
#            "Zara", "Alex", "Pete", "Sara"]
#   by_letter = {}
#   for name in names:
#       by_letter.setdefault(name[0].upper(), []).append(name)
#   for letter, group in sorted(by_letter.items()):
#       print(letter, group)
#
# EXERCISE 6
#   cart = {"apple": 3, "bread": 1, "cheese": 2, "caviar": 1}
#   prices = {"apple": 0.50, "bread": 2.20, "cheese": 4.75, "milk": 1.10}
#   total = 0
#   for item, qty in cart.items():
#       unit = prices.get(item)
#       if unit is None:
#           print(f"{item:<8} NO PRICE - skipped")
#           continue
#       line = qty * unit
#       total += line
#       print(f"{item:<8} {qty:>3} @ {unit:>5.2f} = {line:>6.2f}")
#   print(f"{'TOTAL':<8} {total:>19.2f}")
#
# EXERCISE 7
#   for post in blog["posts"]:
#       if "python" in post["tags"]:
#           print(post["title"])
#   tags = set()
#   for post in blog["posts"]:
#       tags.update(post["tags"])
#   print(len(tags), "distinct tags")
#   for post in sorted(blog["posts"], key=lambda p: p["views"]):
#       print(post["views"], post["title"])
#
# EXERCISE 8
#   original = {"a": 1, "b": 2, "c": 3}
#   inverted = {value: key for key, value in original.items()}
#   print(inverted)
#   # with collision handling:
#   original2 = {"a": 1, "b": 2, "c": 1}
#   grouped = {}
#   for key, value in original2.items():
#       grouped.setdefault(value, []).append(key)
#   print(grouped)          # {1: ['a', 'c'], 2: ['b']}


print("=" * 70)
print("Lesson 09 complete. Next: 10_functions.py")
print("=" * 70)

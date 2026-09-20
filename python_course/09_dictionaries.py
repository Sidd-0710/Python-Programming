"""
===============================================================================
 LESSON 09 — DICTIONARIES: LOOKING THINGS UP BY NAME
===============================================================================

Time: about 80 minutes (there's a good place for a break halfway).
Assumes: lessons 01-08.

This is the most important data structure in Python. If you only truly master
one thing from this course, make it this lesson.


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. store values under NAMES instead of positions: a dictionary  (PART 1)
  2. read a value safely, even when it might be missing            (PART 2)
  3. add, change and remove entries                                (PART 3)
  4. loop over names and values together                           (PART 4)
  5. count things, and group things - the two big patterns         (PART 5)
  6. dig through nested data - exactly what web APIs send          (PART 6)

NEW WORDS - come back here whenever you forget one:

  dictionary    a collection of NAME -> VALUE pairs, in curly braces:
                {"name": "Sidd", "age": 22}      ("dict" for short)
  key           the name you look up by:  "name"
  value         what you get back:        "Sidd"
  pair          one key together with its value:  "age": 22
  KeyError      the error you get when you ask for a key that isn't there
  .get()        a safe lookup that gives a default instead of crashing
  .items()      gives you every (key, value) pair, ready to loop over
  nested        a dict or list INSIDE another dict or list
  JSON          the text format web APIs use. It turns into dicts and lists
                in Python - so this lesson IS the web data lesson


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


# A small helper used for sorting later in this lesson.
# (def makes a function - lesson 10. Read this as: "value_of takes a
# (key, value) pair and gives back the value part".)
def value_of(pair):
    return pair[1]


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
print("user['name'] :", user["name"])       # look up by the key "name"
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

# OPTIONAL - other ways to build one. You'll mostly just use { } like above,
# so don't worry about memorising these:
empty = {}                                          # empty dict
from_pairs = dict([("a", 1), ("b", 2)])             # from a list of tuples
from_kwargs = dict(name="Ana", age=30)              # keyword style
from_zip = dict(zip(["x", "y"], [10, 20]))          # pairing two lists
print("from_pairs :", from_pairs)
print("from_kwargs:", from_kwargs)
print("from_zip   :", from_zip)
print()

# TRY IT NOW (1 minute):
#   Make a dict  book = {"title": "Dune", "author": "Frank Herbert"}  and print
#   just the author.  (Answer: print(book["author"]))


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
# In plain English: "give me the phone, or 'n/a' if there isn't one"
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

# TRY IT NOW (1 minute):
#   Using your book dict, print book.get("year", "unknown").
#   Then try book["year"] and read the KeyError. Then delete that line.


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
# In plain English: "for each product and its quantity..."
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
for product, quantity in sorted(inventory.items(), key=value_of, reverse=True):
    print(f"  {product:<12} {quantity:>3}")
# key=value_of means "sort the pairs by their VALUE, not their name" - using
# the little helper function defined at the top of this file.
# You'll often see the same thing written as  key=lambda pair: pair[1]
# (a lambda is a one-line function - lesson 10).

# Dictionaries keep insertion order (guaranteed since Python 3.7). They are not
# sorted - they simply remember the order you added things in.
print()

# TRY IT NOW (2 minutes):
#   Loop over  prices = {"tea": 1.5, "cake": 3.0}  with .items() and print
#   lines like:  tea costs 1.50
#   (Answer: for item, price in prices.items(): print(f"{item} costs {price:.2f}"))


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. You now know how to build, read, change and loop
#  over dictionaries. After the break: the patterns that make them powerful.
# -----------------------------------------------------------------------------


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
#   Step by step for the first few words:
#     "the" -> counts.get("the", 0) is 0, so counts["the"] = 1
#     "cat" -> counts["cat"] = 1
#     "sat" -> counts["sat"] = 1
#     "on"  -> counts["on"]  = 1
#     "the" -> counts.get("the", 0) is 1 now, so counts["the"] = 2

print("\nmost frequent first:")
for word, count in sorted(counts.items(), key=value_of, reverse=True):
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
    by_city[city].append(name)          # then add this person to their city

print("grouped by city:")
for city, residents in sorted(by_city.items()):
    print(f"  {city:<8} ({len(residents)}): {', '.join(residents)}")

# OPTIONAL - setdefault() does the "create if missing" step in one line. The
# longer if-version above is just as good; use whichever reads better to you.
by_city2 = {}
for name, city in people:
    by_city2.setdefault(city, []).append(name)
print("same result via setdefault:", by_city2 == by_city)
print()

# TRY IT NOW (2 minutes):
#   Count the colours in  ["red", "blue", "red", "green", "red"]  using the
#   counting pattern.  (Answer: {'red': 3, 'blue': 1, 'green': 1})


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
for post in blog["posts"]:                  # each post is a dict
    total_views += post["views"]
    all_tags.update(post["tags"])           # add this post's tags to the set
    print(f"  [{post['id']}] {post['title']:<20} {post['views']:>6,} views")

print(f"\nTotal views : {total_views:,}")
print(f"Average     : {total_views / len(blog['posts']):,.0f}")
print(f"All tags    : {sorted(all_tags)}")

# Finding the most popular post: remember the "best so far" loop (lesson 07).
most_popular = blog["posts"][0]
for post in blog["posts"]:
    if post["views"] > most_popular["views"]:
        most_popular = post
print(f"Most popular: {most_popular['title']} ({most_popular['views']:,})")
print()

# NOTE ON QUOTES INSIDE f-STRINGS: older Python versions can't reuse the same
# quote style inside the braces, which is why you'll see {post['id']} with
# single quotes inside a double-quoted f-string. Modern Python (3.12+) allows
# either, but the mixed style is still the safest habit.

# TRY IT NOW (1 minute):
#   Print the author's email from blog, and the title of the LAST post.
#   (Answers: blog["author"]["email"]  and  blog["posts"][-1]["title"])


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
for region, amount in sorted(revenue_by_region.items(), key=value_of, reverse=True):
    print(f"  {region:<4} {amount:>10,.2f}")

print("\nTop customers:")
for customer, amount in sorted(spend_by_customer.items(), key=value_of, reverse=True):
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
#   Step by step: get "user" (or an empty dict), then from THAT get "address"
#   (or an empty dict), then from THAT get "city" (or "unknown"). Each step
#   has a safe fallback, so nothing can crash.
print("safely dug out city:", city)
print()


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * A dict maps keys to values:  user = {"name": "Sidd", "age": 22}
#   * user["name"] reads a value. A missing key -> KeyError.
#   * user.get("phone", "n/a") reads safely, with a default.
#   * user["city"] = "Pune" adds OR updates. del / .pop() remove.
#   * for key, value in d.items():  loops over every pair.
#   * COUNTING:  counts[x] = counts.get(x, 0) + 1
#   * GROUPING:  if key not in groups: groups[key] = []  then .append()
#   * Nested data (dicts in lists in dicts) is what JSON / APIs look like.
#     Dig in one step at a time:  blog["posts"][0]["title"]
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. d = {"a": 1}.  What does d["b"] do? And d.get("b", 0)?
#   Q2. How do you change a's value to 5?
#   Q3. What does  "a" in d  check - keys or values?
#   Q4. What does this leave in counts?  counts = {} then for x in "aab":
#       counts[x] = counts.get(x, 0) + 1
#   Q5. How do you read "Deploying Flask" from the blog dict?
#
# ANSWERS
#   A1. KeyError.  0.
#   A2. d["a"] = 5
#   A3. Keys.
#   A4. {'a': 2, 'b': 1}
#   A5. blog["posts"][2]["title"]  (or blog["posts"][-1]["title"])


# =============================================================================
# EXERCISES
# =============================================================================
#
# WARM-UP A (easy) — A book
#   Make a dict with "title" and "author" for your favourite book. Print the
#   title.
#
# WARM-UP B (easy) — Add a key
#   Add a "year" key to your book dict, then print the whole dict.
#
# WARM-UP C (easy) — Loop it
#   Loop over your book dict with .items() and print each line as
#   key: value
#
# EXERCISE 1 (easy) — Contact card
#   Build a dict describing you (name, age, city, skills as a list). Print each
#   key and value on its own line using .items(). Then add a new key, change an
#   existing one, and delete one.
#
# EXERCISE 2 (easy) — Phone book
#   Create a phone book dict. Write code that looks up a name and prints the
#   number, or "not found" if it's missing - without crashing.
#
# EXERCISE 3 (medium) — Letter frequency
#   Count how many times each LETTER appears in "mississippi river". Ignore
#   spaces. Print the results sorted by count, highest first.
#   Hint: the counting pattern, then sort with key=value_of.
#
# EXERCISE 4 (medium) — Grade book
#   grades = {"Ana": [88, 92, 79], "Sidd": [95, 68, 84], "Marco": [72, 75, 91]}
#   For each student print their average to 1dp and their best score. Then
#   print the name of the student with the highest overall average.
#
# EXERCISE 5 (medium) — Group by first letter
#   Given a list of 10+ names, build a dict mapping each first letter to the
#   list of names starting with it. Print it sorted by letter.
#   Hint: the grouping pattern from PART 5, using name[0] as the key.
#
# EXERCISE 6 (medium) — Shopping cart (web backend practice)
#   cart = {"apple": 3, "bread": 1, "cheese": 2}
#   prices = {"apple": 0.50, "bread": 2.20, "cheese": 4.75, "milk": 1.10}
#   Print a receipt with a line per item (qty, unit price, line total) and a
#   grand total. Handle gracefully the case where a cart item has no price.
#
# EXERCISE 7 (medium) — API response digging
#   Using the `blog` dict from PART 6:
#     a) print every post title that has the tag "python"
#     b) print the total number of distinct tags
#     c) print posts sorted by views, lowest first
#     d) add a new post to the list, then re-run your total-views calculation
#
# EXERCISE 8 (challenge) — Invert a dictionary
#   Given {"a": 1, "b": 2, "c": 3}, produce {1: "a", 2: "b", 3: "c"}.
#   Then think about what happens if two keys share a value, and handle it by
#   making the inverted values lists.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   book = {"title": "Dune", "author": "Frank Herbert"}
#   print(book["title"])
#
# WARM-UP B
#   book["year"] = 1965
#   print(book)
#
# WARM-UP C
#   for key, value in book.items():
#       print(f"{key}: {value}")
#
# EXERCISE 1
#   me = {"name": "Sidd", "age": 22, "city": "Mumbai",
#         "skills": ["python", "sql"]}
#   for key, value in me.items():
#       print(f"{key:<8}: {value}")
#   me["country"] = "India"            # add
#   me["age"] = 23                     # change
#   del me["city"]                     # delete
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
#   for letter, count in sorted(freq.items(), key=value_of, reverse=True):
#       print(f"{letter}: {count}")
#
# EXERCISE 4
#   grades = {"Ana": [88, 92, 79], "Sidd": [95, 68, 84], "Marco": [72, 75, 91]}
#   top_student = ""
#   top_average = 0
#   for student, scores in grades.items():
#       avg = sum(scores) / len(scores)
#       print(f"{student:<6} avg {avg:.1f} best {max(scores)}")
#       if avg > top_average:            # the "best so far" pattern
#           top_student = student
#           top_average = avg
#   print("Top student:", top_student)
#
# EXERCISE 5
#   names = ["Ana", "Sidd", "Sam", "Marco", "Mia", "Priya",
#            "Zara", "Alex", "Pete", "Sara"]
#   by_letter = {}
#   for name in names:
#       letter = name[0].upper()
#       if letter not in by_letter:
#           by_letter[letter] = []
#       by_letter[letter].append(name)
#   for letter, group in sorted(by_letter.items()):
#       print(letter, group)
#
# EXERCISE 6
#   cart = {"apple": 3, "bread": 1, "cheese": 2, "caviar": 1}
#   prices = {"apple": 0.50, "bread": 2.20, "cheese": 4.75, "milk": 1.10}
#   total = 0
#   for item, qty in cart.items():
#       unit = prices.get(item)            # None if there's no price
#       if unit is None:
#           print(f"{item:<8} NO PRICE - skipped")
#           continue
#       line = qty * unit
#       total += line
#       print(f"{item:<8} {qty:>3} @ {unit:>5.2f} = {line:>6.2f}")
#   print(f"{'TOTAL':<8} {total:>19.2f}")
#
# EXERCISE 7
#   # a)
#   for post in blog["posts"]:
#       if "python" in post["tags"]:
#           print(post["title"])
#   # b)
#   tags = set()
#   for post in blog["posts"]:
#       tags.update(post["tags"])
#   print(len(tags), "distinct tags")
#   # c)
#   def views_of(post):
#       return post["views"]
#   for post in sorted(blog["posts"], key=views_of):
#       print(post["views"], post["title"])
#   # d)
#   blog["posts"].append({"id": 4, "title": "New Post", "views": 10, "tags": []})
#   (then run your total_views loop again)
#
# EXERCISE 8
#   original = {"a": 1, "b": 2, "c": 3}
#   inverted = {}
#   for key, value in original.items():
#       inverted[value] = key            # the value becomes the key
#   print(inverted)                      # {1: 'a', 2: 'b', 3: 'c'}
#   # with collision handling - the grouping pattern:
#   original2 = {"a": 1, "b": 2, "c": 1}
#   grouped = {}
#   for key, value in original2.items():
#       if value not in grouped:
#           grouped[value] = []
#       grouped[value].append(key)
#   print(grouped)                       # {1: ['a', 'c'], 2: ['b']}
#   After lesson 11 you'll also recognise the one-line version:
#       inverted = {value: key for key, value in original.items()}


print("=" * 70)
print("Lesson 09 complete. Next: 10_functions.py")
print("=" * 70)

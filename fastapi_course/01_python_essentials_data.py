"""
===============================================================================
 FASTAPI COURSE - LESSON 01: PYTHON ESSENTIALS I - DATA AND DECISIONS
===============================================================================

Time: about 70 minutes (there's a good place for a break halfway).
Assumes: lesson 00.
Run it:  python 01_python_essentials_data.py

This lesson teaches ONLY the Python you will use constantly in FastAPI, and
every part ends with an "IN FASTAPI" note showing where it turns up. It moves
quickly on purpose. If something feels shaky, the matching python_course
lesson goes much deeper:

    variables and types  ->  ../python_course/01_variables_and_data_types.py
    text (strings)       ->  ../python_course/02_strings_and_text.py
    lists                ->  ../python_course/06_lists.py
    dictionaries         ->  ../python_course/09_dictionaries.py
    if and loops         ->  ../python_course/05 and 07


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. store values in variables, and know their type              (PART 1)
  2. work with text: clean it, join it, search it                (PART 2)
  3. keep many values in order with a list, and take a "page"    (PART 3)
  4. store values by NAME with a dictionary - this IS JSON       (PART 4)
  5. build a pretend database: a list of dictionaries            (PART 5)
  6. make decisions with if / elif / else                        (PART 6)
  7. repeat work with loops - and find one item by its id        (PART 7)
  8. build a new list in one line with a comprehension           (PART 8)
  9. do Create, Read, Update and Delete by hand                  (PART 9)

NEW WORDS - come back here whenever you forget one:

  variable      a name that points at a value:  age = 22
  value         the thing itself: 22, "Sidd", True
  type          what KIND of value it is: text, whole number, decimal, ...
  str           text, always in quotes:  "Sidd"
  int           a whole number:  22
  float         a number with a decimal point:  19.99
  bool          True or False (capital letters)
  None          "no value at all". This is JSON's null.
  f-string      text with values dropped into it:  f"Hi {name}"
  method        a tool that belongs to a value, called with a dot:
                email.strip()
  list          several values in order, in square brackets:  ["a", "b"]
  index         the position of an item. COUNTING STARTS AT 0.
  slice         a chunk of a list:  items[0:5]
  dictionary    values stored by NAME, in curly braces:
  (dict)        {"name": "Sidd", "age": 22}
  key / value   in that dict, "name" is a key and "Sidd" is its value
  nested        a dict or list stored INSIDE another one
  condition     something that is True or False:  age > 18
  loop          doing something once for each item in a list
  comprehension building a new list in one line (PART 8)
  CRUD          Create, Read, Update, Delete (PART 9)

HOW TO WORK THROUGH THIS FILE:
  * A line starting with #  is a COMMENT - a note for you. Python skips it.
  * print(...) shows something in the terminal.
  * Read one PART, run the file, find that PART's output, and match each
    output line to the code that made it.
  * Do the TRY IT NOW boxes as you reach them - they take a minute or two.
  * Then CHANGE something - a name, a number - and run it again. Breaking
    things on purpose is the fastest way to learn what the rules are.
"""

LINE = "-" * 70


def section(title):
    """Prints a heading. You'll learn to write functions like this in lesson 02."""
    print()
    print(LINE)
    print(f"  {title}")
    print(LINE)


def show_table(rows):
    """Prints a list of user dictionaries as a neat table (a lesson 02 helper)."""
    print(f"    {'id':<4}{'name':<10}{'email':<24}{'role':<8}active")
    for row in rows:
        print(f"    {row['id']:<4}{row['name']:<10}{row['email']:<24}"
              f"{row['role']:<8}{row['is_active']}")


# =============================================================================
# PART 1 — VARIABLES AND TYPES
# =============================================================================
section("PART 1 - VARIABLES AND TYPES")

# A VARIABLE is a name that points at a value. The = sign means "store this".
# Read  name = "Sidd"  as  "name gets the value Sidd".

name = "Sidd"            # str   - text. Always inside quotes.
age = 22                 # int   - a whole number
price = 19.99            # float - a number with a decimal point
is_admin = False         # bool  - True or False, with a capital letter
middle_name = None       # None  - "no value". This is JSON's null.

print("  name        =", name, "   type:", type(name).__name__)
print("  age         =", age, "     type:", type(age).__name__)
print("  price       =", price, "  type:", type(price).__name__)
print("  is_admin    =", is_admin, "  type:", type(is_admin).__name__)
print("  middle_name =", middle_name, "   type:", type(middle_name).__name__)

# You can change what a variable holds. The old value is simply forgotten.
age = 23
print("\n  after a birthday, age =", age)

# THE TRAP THAT MATTERS MOST FOR BACKENDS:
# Everything that arrives over the internet starts out as TEXT.
# "42" (text) and 42 (a number) are completely different things.
user_id_from_url = "42"
print()
print('  "42" + "1"      ->', user_id_from_url + "1", "    (text is JOINED, not added)")
print('  int("42") + 1   ->', int(user_id_from_url) + 1, "     (int() converts text to a number)")
print('  str(42) + "!"   ->', str(42) + "!", "    (str() converts a number to text)")

# IN FASTAPI: in the URL /users/42, the 42 arrives as text. You'll write
#   user_id: int
# and FastAPI converts it for you - and automatically rejects /users/abc
# with a helpful error. That's lesson 04.

# TRY IT NOW (1 minute):
#   Add a variable of your own - say  country = "India"  - and print it with
#   its type, copying the lines above. [type: str]


# =============================================================================
# PART 2 — TEXT (STRINGS)
# =============================================================================
section("PART 2 - WORKING WITH TEXT")

first_name = "Sidd"
city = "Mumbai"

# f-strings: put f before the quotes, and any {variable} inside gets filled in.
# This is how you build messages. Use it all the time.
message = f"Hello {first_name} from {city}! Next year you'll be {age + 1}."
print(" ", message)

# Text has built-in tools, called with a dot. Each returns a NEW piece of text.
raw_email = "   Sidd@Example.COM   "
print()
print(f"  raw email          : '{raw_email}'")
print(f"  .strip()           : '{raw_email.strip()}'       removes spaces at both ends")
print(f"  .lower()           : '{raw_email.lower()}'")
print(f"  .strip().lower()   : '{raw_email.strip().lower()}'   you can chain them")

clean_email = raw_email.strip().lower()
print(f"  '@' in clean_email : {'@' in clean_email}             `in` checks if text contains text")
print(f"  .split('@')        : {clean_email.split('@')}   cuts text into a list")
print(f"  len(clean_email)   : {len(clean_email)}                how many characters")
print(f"  .startswith('sidd'): {clean_email.startswith('sidd')}")

# A trap: text tools never change the original. You must SAVE the result.
raw_email.strip()                         # does nothing useful - result thrown away
print(f"\n  raw_email is still  : '{raw_email}'  <- unchanged!")

# IN FASTAPI: cleaning input before saving it, so that SIDD@example.com and
# sidd@example.com count as the same account. And building error messages:
#   f"User {user_id} not found"


# =============================================================================
# PART 3 — LISTS: MANY VALUES IN ORDER
# =============================================================================
section("PART 3 - LISTS")

# A list holds several values, in order, inside square brackets.
roles = ["admin", "editor", "viewer"]

# COUNTING STARTS AT 0. The first item is [0], not [1].
print("  roles         :", roles)
print("  roles[0]      :", roles[0], "     <- the FIRST item")
print("  roles[2]      :", roles[2])
print("  roles[-1]     :", roles[-1], "     <- -1 means the LAST item")
print("  len(roles)    :", len(roles))
print("  'admin' in roles:", "admin" in roles)

roles.append("guest")                     # add to the end
print("  after append  :", roles)
roles.remove("guest")                     # remove by value
print("  after remove  :", roles)

# SLICING takes a chunk:  items[start:stop]
# start is INCLUDED, stop is NOT included.
numbers = list(range(1, 21))              # the numbers 1 up to 20
print()
print("  numbers       :", numbers)
print("  numbers[0:5]  :", numbers[0:5], "     first 5")
print("  numbers[5:10] :", numbers[5:10], "    the next 5")

# PAGINATION - showing results a page at a time - is just slicing:
skip = 10        # how many to jump over
limit = 5        # how many to show
print(f"  skip={skip}, limit={limit} ->", numbers[skip:skip + limit])
print("  numbers[100:105] ->", numbers[100:105], "  slicing past the end is safe, just empty")

# IN FASTAPI: GET /users returns a LIST of users. And GET /users?skip=10&limit=5
# is implemented as  users[skip:skip + limit]  - exactly the line above.

# TRY IT NOW (2 minutes):
#   Change skip to 0 and limit to 3, and run the file. Then try skip=45.
#   [skip=0, limit=3 gives [1, 2, 3]. skip=45 gives [] - an empty list,
#   because there are only 20 numbers. Asking past the end is safe.]


# =============================================================================
# PART 4 — DICTIONARIES: THE MOST IMPORTANT PART OF THIS LESSON
# =============================================================================
section("PART 4 - DICTIONARIES")

# A dictionary stores values by NAME instead of by position.
# Each entry is  "key": value.  Curly braces. This is what JSON becomes.
user = {
    "id": 1,
    "name": "Sidd",
    "email": "sidd@example.com",
    "is_active": True,
}

print("  user               :", user)
print("  user['name']       :", user["name"], "            read a value by its key")

# Asking for a key that doesn't exist with [ ] CRASHES (a "KeyError").
# .get() returns None instead - or a default you choose.
# In plain English: [ ] means "give me this, and crash if it's missing".
# .get() means "give me this, or None if it isn't there".
print("  user.get('phone')  :", user.get("phone"), "            missing key -> None, no crash")
print("  user.get('phone', 'not given'):", user.get("phone", "not given"))
print("  'email' in user    :", "email" in user, "            is that key present?")

# ADD a key, or CHANGE one - same syntax. If the key exists it's replaced.
user["phone"] = "555-0101"
user["email"] = "sidd.new@example.com"
print("  after add + change :", user)

# DELETE a key
del user["phone"]
print("  after del phone    :", user)

# UPDATE several keys at once from another dictionary.
changes = {"name": "Siddheshwar", "is_active": False}
user.update(changes)
print("  after .update()    :", user)

# NESTING: a value can itself be a dict or a list.
user["address"] = {"city": "Mumbai", "pin": "400001"}
user["roles"] = ["admin", "editor"]
print("  user['address']['city']:", user["address"]["city"])
print("  user['roles'][1]       :", user["roles"][1])

# LOOP over a dictionary's keys and values together with .items()
print("\n  every field:")
for key, value in user.items():
    print(f"    {key:<10} = {value}")

# IN FASTAPI: a JSON request body arrives as (something very like) a
# dictionary, and any dictionary you return becomes the JSON response.
# A PATCH request ("change just these fields") is literally
#     stored_user.update(changes)

# TRY IT NOW (2 minutes):
#   Add  user["country"] = "India"  before the .items() loop, and run the
#   file. [It appears at the end of the "every field" list. A dictionary
#   keeps keys in the order you added them.]


# =============================================================================
# PART 5 — A LIST OF DICTIONARIES: A PRETEND DATABASE
# =============================================================================
section("PART 5 - A LIST OF DICTIONARIES")

# This shape - a list where each item is a dictionary - is a TABLE.
# Each dictionary is a ROW. Each key is a COLUMN. Until lesson 08 gives us a
# real database, this is how our APIs will store data.
users = [
    {"id": 1, "name": "Sidd", "email": "sidd@example.com", "role": "admin", "is_active": True},
    {"id": 2, "name": "Ana", "email": "ana@example.com", "role": "editor", "is_active": True},
    {"id": 3, "name": "Marco", "email": "marco@example.com", "role": "viewer", "is_active": False},
    {"id": 4, "name": "Priya", "email": "priya@example.com", "role": "editor", "is_active": True},
]

show_table(users)
print()
print("  how many users     :", len(users))
print("  the second user    :", users[1])
print("  their name         :", users[1]["name"], "   <- list position [1], then key ['name']")
print("  last user's email  :", users[-1]["email"])

# IN FASTAPI: GET /users returns exactly this shape, and the frontend gets
# a JSON array of objects.


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. You now have every SHAPE of data an API uses:
#  text, numbers, lists, dictionaries, and a table made of them. After the
#  break: making decisions, looping, and doing the four CRUD jobs by hand.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 6 — MAKING DECISIONS WITH if
# =============================================================================
section("PART 6 - DECISIONS")

# Comparisons produce True or False:
#   ==  equal        !=  not equal        >  <  >=  <=
# CAREFUL:  =  STORES a value.   ==  ASKS whether two values are equal.
print("  5 == 5        ->", 5 == 5)
print("  'a' != 'b'    ->", "a" != "b")
print("  '42' == 42    ->", "42" == 42, "   text is never equal to a number")

current_user = users[1]          # Ana, an editor

# THE SHAPE: a condition, a colon, then INDENTED lines (4 spaces) that run
# only when the condition is True. The indentation is how Python knows which
# lines belong to the if. Get it wrong and you get an IndentationError.
if current_user["role"] == "admin":
    print("  Ana can do everything")
elif current_user["role"] == "editor":
    print("  Ana can edit posts, but not manage users")
else:
    print("  Ana can only read")

# and / or / not combine conditions
can_publish = current_user["is_active"] and current_user["role"] in ["admin", "editor"]
print("  can Ana publish?", can_publish)

# CHECKING FOR "NOTHING": use  is None
found_user = None
if found_user is None:
    print("  no user found  -> this is where an API returns 404")

# Empty things count as False, which gives you a tidy check:
search_results = []
if not search_results:
    print("  the search found nothing")

# IN FASTAPI you'll write lines like these constantly:
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     if user.role != "admin":
#         raise HTTPException(status_code=403, detail="Admins only")


# =============================================================================
# PART 7 — LOOPS: DOING SOMETHING FOR EACH ITEM
# =============================================================================
section("PART 7 - LOOPS")

# for ... in ... : runs the indented block once for each item.
for role in roles:
    print("  role:", role)

print()
for u in users:
    # A plain if/else. (Python also has a one-line form,
    #     status = "active" if u["is_active"] else "inactive"
    # which you'll meet in other people's code. Both do the same thing.)
    if u["is_active"]:
        status = "active"
    else:
        status = "inactive"
    print(f"  {u['name']} is {status}")

# *** THE MOST IMPORTANT LOOP IN BACKEND CODE: FIND ONE ITEM BY ITS ID ***
wanted_id = 3
found = None                      # start with "not found yet"
for u in users:
    if u["id"] == wanted_id:
        found = u                 # remember it...
        break                     # ...and stop looking. No need to check the rest.

print()
if found is None:
    print(f"  404 - user {wanted_id} not found")
else:
    print(f"  200 - found user {wanted_id}: {found['name']}")

# COUNTING with a loop
active_count = 0
for u in users:
    if u["is_active"]:
        active_count += 1         # += 1 means "add one to it"
print(f"  active users: {active_count}")

# COUNTING BY CATEGORY with a dictionary - a pattern worth memorising
count_by_role = {}
for u in users:
    role = u["role"]
    count_by_role[role] = count_by_role.get(role, 0) + 1
print(f"  users per role: {count_by_role}")

# enumerate() gives you a counter as well as the item
print()
for position, u in enumerate(users, start=1):
    print(f"  {position}. {u['name']}")

# IN FASTAPI: until we have a real database, "GET /users/3" will be exactly
# the find-by-id loop above.

# TRY IT NOW (2 minutes):
#   Change  wanted_id = 3  to  wanted_id = 99  and run the file.
#   [It prints the 404 line. `found` stayed None because no user matched -
#   which is exactly how your API will decide to answer 404 in lesson 06.]


# =============================================================================
# PART 8 — LIST COMPREHENSIONS: BUILD A NEW LIST IN ONE LINE
# =============================================================================
section("PART 8 - LIST COMPREHENSIONS")

# A very common job: "go through a list, and build a new list from it".
# The long way:
names_long_way = []
for u in users:
    names_long_way.append(u["name"])

# The short way - a LIST COMPREHENSION. Read it as:
#   "give me u['name'], for each u in users"
names = [u["name"] for u in users]
print("  all names        :", names)
print("  same as long way?", names == names_long_way)

# Add  if  at the end to FILTER:
#   "give me u, for each u in users, but only if it's active"
active_users = [u for u in users if u["is_active"]]
editor_names = [u["name"] for u in users if u["role"] == "editor"]
print("  active user names:", [u["name"] for u in active_users])
print("  editors          :", editor_names)

# SHAPING a response: build new dictionaries with only some of the fields.
users_with_passwords = [
    {"id": 1, "name": "Sidd", "password": "hunter2"},
    {"id": 2, "name": "Ana", "password": "correcthorse"},
]
public_users = [{"id": u["id"], "name": u["name"]} for u in users_with_passwords]
print("  safe to send out :", public_users)

# IN FASTAPI: filtering (GET /users?role=editor) and - critically - making
# sure fields like passwords are never included in a response. Lesson 05
# shows FastAPI's built-in way to guarantee that.


# =============================================================================
# PART 9 — PUTTING IT TOGETHER: CRUD BY HAND
# =============================================================================
section("PART 9 - CREATE, READ, UPDATE, DELETE ON A LIST")

# Everything above, doing the four jobs every backend does. In lesson 06,
# each of these five blocks becomes one API endpoint - almost unchanged.

db = [
    {"id": 1, "name": "Sidd", "email": "sidd@example.com", "role": "admin", "is_active": True},
    {"id": 2, "name": "Ana", "email": "ana@example.com", "role": "editor", "is_active": True},
    {"id": 3, "name": "Marco", "email": "marco@example.com", "role": "viewer", "is_active": False},
]
print("  starting data:")
show_table(db)

# ---- CREATE  (will become:  POST /users) ----
incoming = {"name": "  Priya ", "email": "PRIYA@Example.com", "role": "editor"}

new_id = max([u["id"] for u in db], default=0) + 1     # biggest id so far, plus 1
new_user = {
    "id": new_id,
    "name": incoming["name"].strip(),
    "email": incoming["email"].strip().lower(),
    "role": incoming.get("role", "viewer"),        # default if they didn't send one
    "is_active": True,
}
db.append(new_user)
print(f"\n  CREATE -> 201, new user has id {new_id}")

# ---- READ ONE  (will become:  GET /users/2) ----
wanted_id = 2
found = None
for u in db:
    if u["id"] == wanted_id:
        found = u
        break
if found is None:
    print(f"  READ ONE -> 404, user {wanted_id} not found")
else:
    print(f"  READ ONE -> 200, {found}")

# ---- READ MANY  (will become:  GET /users?role=editor&skip=0&limit=10) ----
role_filter = "editor"
skip = 0
limit = 10
matching = [u for u in db if u["role"] == role_filter]
page = matching[skip:skip + limit]
print(f"  READ MANY -> 200, {len(page)} editors: {[u['name'] for u in page]}")

# ---- UPDATE  (will become:  PATCH /users/3  with body {"is_active": true}) ----
update_id = 3
changes = {"is_active": True, "role": "editor"}
target = None
for u in db:
    if u["id"] == update_id:
        target = u
        break
if target is None:
    print(f"  UPDATE -> 404, user {update_id} not found")
else:
    target.update(changes)
    print(f"  UPDATE -> 200, user {update_id} is now {target}")
# IMPORTANT: `target` is not a copy. It's the SAME dictionary that sits inside
# `db`, so changing target changes the database. That's why the update stuck.

# ---- DELETE  (will become:  DELETE /users/1) ----
delete_id = 1
count_before = len(db)
db = [u for u in db if u["id"] != delete_id]      # keep everyone EXCEPT that id
if len(db) < count_before:
    print(f"  DELETE -> 204, user {delete_id} removed")
else:
    print(f"  DELETE -> 404, user {delete_id} not found")

print("\n  final data:")
show_table(db)


# =============================================================================
# PART 10 — COMMON MISTAKES
# =============================================================================
section("PART 10 - COMMON MISTAKES")

# MISTAKE 1: counting from 1.  The first item is [0]. The last is [-1].
#   users[4] on a 4-item list -> IndexError: list index out of range

# MISTAKE 2: [ ] on a key that might be missing.
try:
    user["phone_number"]
except KeyError:
    print("  user['phone_number'] crashed with KeyError -> use user.get('phone_number')")
# (try/except catches errors. Lesson 02 teaches it properly.)

# MISTAKE 3: comparing text with numbers.
print('  "3" == 3 is', "3" == 3, "-> convert first: int(\"3\") == 3 is", int("3") == 3)

# MISTAKE 4: = when you meant ==
#   if role = "admin":     -> SyntaxError. Python stops you, luckily.

# MISTAKE 5: forgetting quotes around dictionary keys.
#   user[name]  looks for a VARIABLE called name.  user["name"]  is the key.

# MISTAKE 6: wrong indentation.
#   Lines inside an if or a for must be indented by the same 4 spaces.
#   VS Code does this for you when you press Enter after a colon.

# MISTAKE 7: forgetting that text tools return a new value.
#   email.lower()            does nothing on its own
#   email = email.lower()    saves the result

# MISTAKE 8: removing items from a list while looping over that same list.
#   It skips items. Build a new list with a comprehension instead, like the
#   DELETE in PART 9.
print("  (read the comments in PART 10 for the rest)")


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * A variable is a name for a value; every value has a TYPE. Anything that
#     arrives from the internet starts out as TEXT - convert it with int().
#   * Text tools like .strip() and .lower() return a NEW value: save it.
#   * A list keeps values in order. Counting starts at 0, [-1] is the last,
#     and items[skip:skip + limit] is exactly how paging works.
#   * A dictionary stores values by name - and IS what JSON becomes.
#     Use .get("key") when a key might be missing, so nothing crashes.
#   * A list of dictionaries is a table: your pretend database until lesson 08.
#   * if / elif / else picks what to do;  is None  checks for "nothing found",
#     which is how an API decides to answer 404.
#   * A for loop repeats work. The most useful one in backend code is
#     find-by-id: loop, compare, remember it, break.
#   * A comprehension builds a new list in one line - for filtering, and for
#     leaving fields like passwords OUT of a response.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. A URL gives you "7". What must you do before adding 1 to it?
#   Q2. What is  roles[0]  compared with  roles[-1]?
#   Q3. user["phone"] crashes. What should you use instead, and what do you get?
#   Q4. After the find-by-id loop, `found` is still None. What does that mean
#       your API should answer?
#   Q5. Why build a NEW list of fields you want, instead of deleting the
#       password from each user?
#
# ANSWERS
#   A1. Convert it: int("7") + 1. Text and numbers never mix.
#   A2. The FIRST item and the LAST item.
#   A3. user.get("phone") - you get None instead of a crash.
#   A4. 404 Not Found - no user has that id.
#   A5. If someone later adds another secret field, listing what you WANT
#       keeps it out automatically. Deleting means remembering every time.


# =============================================================================
# EXERCISES
# =============================================================================
#
# Write your answers below the line, run the file, and check your output.
# Then compare with the SOLUTIONS further down.
#
# Do the WARM-UPS first - each practises ONE idea from this lesson.
#
# WARM-UP A (easy) — A variable and its type
#   Make a variable  city = "Pune"  and print it together with its type,
#   like PART 1 does.
#
# WARM-UP B (easy) — Read from a dictionary
#   book = {"title": "Dune", "year": 1965}
#   Print the title, then print book.get("author") and see what a missing key
#   gives you.
#
# WARM-UP C (easy) — Count a list
#   Using the `users` list from PART 5, print how many users there are, and
#   the name of the first one.
#
# EXERCISE 1 (easy) — Product variables
#   Create variables for a product: name (text), price (a decimal number),
#   quantity (a whole number), in_stock (True/False) and discount (None).
#   Print one f-string sentence using them, then print the type of each.
#
# EXERCISE 2 (easy) — Numbers that arrive as text
#   A URL gave you  page = "3"  and  per_page = "10"  (both TEXT).
#   Calculate and print how many items to skip: (page - 1) * per_page.
#   The correct answer is 20. First try it WITHOUT converting and read the error.
#
# EXERCISE 3 (medium) — Cleaning emails
#   Given  raw = ["  ANA@x.com", "marco@X.COM ", "not-an-email", " priya@x.com"]
#   build a list of cleaned emails (stripped and lowercased), and print which
#   ones don't contain "@".
#
# EXERCISE 4 (medium) — Working with a dictionary
#   Create a product dictionary with name, price and a nested "dimensions"
#   dictionary containing width and height. Then:
#     a) print the height
#     b) add a "tags" key holding a list of two tags
#     c) apply these changes in one step: {"price": 299.0, "color": "black"}
#     d) delete the dimensions key
#     e) print the final dictionary
#
# EXERCISE 5 (medium) — Questions about the `users` list from PART 5
#     a) print the names of all editors
#     b) print how many users are active
#     c) print the email of the user whose name is "Marco"
#
# EXERCISE 6 (medium) — Find by id
#   Write the find-by-id loop for user id 4 on `users`, printing
#   "200 - found <name>" or "404 - user <id> not found". Then change the id
#   to 99 and run it again.
#
# EXERCISE 7 (challenge) — Pages
#   items = list(range(1, 48))   (47 items). With per_page = 10, print each
#   page's number and its items, using slicing. How many pages are there?
#
# EXERCISE 8 (challenge) — Mini CRUD on books
#   Start with:
#     books = [
#         {"id": 1, "title": "Dune", "year": 1965},
#         {"id": 2, "title": "The Road", "year": 2006},
#     ]
#   a) CREATE a book with the next id
#   b) UPDATE book 1 so its year is 1966
#   c) DELETE book 2
#   d) print the titles of books published after 1960
#
# EXERCISE 9 (medium) — Hide the passwords
#   accounts = [{"id": 1, "username": "sidd", "password": "x1", "email": "s@x.com"},
#               {"id": 2, "username": "ana", "password": "y2", "email": "a@x.com"}]
#   Build a new list containing every field EXCEPT password, and print it.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   city = "Pune"
#   print(city, type(city).__name__)          # Pune str
#
# WARM-UP B
#   book = {"title": "Dune", "year": 1965}
#   print(book["title"])                      # Dune
#   print(book.get("author"))                 # None - missing, but no crash
#
# WARM-UP C
#   print(len(users))                         # 4
#   print(users[0]["name"])                   # Sidd  (position 0 = the first)
#
# EXERCISE 1
#   product_name = "Keyboard"
#   product_price = 49.99
#   quantity = 12
#   in_stock = True
#   discount = None
#   print(f"{product_name} costs {product_price}, {quantity} left, in stock: {in_stock}")
#   print(type(product_name), type(product_price), type(quantity),
#         type(in_stock), type(discount))
#
# EXERCISE 2
#   page = "3"
#   per_page = "10"
#   # (page - 1) * per_page  -> TypeError: unsupported operand type(s) for -: 'str' and 'int'
#   skip = (int(page) - 1) * int(per_page)
#   print(skip)                         # 20
#
# EXERCISE 3
#   raw = ["  ANA@x.com", "marco@X.COM ", "not-an-email", " priya@x.com"]
#   cleaned = [e.strip().lower() for e in raw]
#   print(cleaned)
#   print("invalid:", [e for e in cleaned if "@" not in e])
#
# EXERCISE 4
#   product = {"name": "Desk", "price": 349.0,
#              "dimensions": {"width": 120, "height": 75}}
#   print(product["dimensions"]["height"])          # a)
#   product["tags"] = ["office", "furniture"]        # b)
#   product.update({"price": 299.0, "color": "black"})   # c)
#   del product["dimensions"]                        # d)
#   print(product)                                   # e)
#
# EXERCISE 5
#   print([u["name"] for u in users if u["role"] == "editor"])       # a)
#   print(len([u for u in users if u["is_active"]]))                 # b)
#   for u in users:                                                  # c)
#       if u["name"] == "Marco":
#           print(u["email"])
#           break
#
# EXERCISE 6
#   wanted_id = 4          # then try 99
#   found = None
#   for u in users:
#       if u["id"] == wanted_id:
#           found = u
#           break
#   if found is None:
#       print(f"404 - user {wanted_id} not found")
#   else:
#       print(f"200 - found {found['name']}")
#
# EXERCISE 7
#   items = list(range(1, 48))
#   per_page = 10
#   page_number = 1
#   skip = 0
#   while skip < len(items):            # `while` repeats while this is True
#       print(page_number, items[skip:skip + per_page])
#       skip += per_page
#       page_number += 1
#   # 5 pages: four full pages of 10, and a last page of 7.
#   # Without while:  for page_number in range(1, 6): skip = (page_number - 1) * 10 ...
#
# EXERCISE 8
#   books = [{"id": 1, "title": "Dune", "year": 1965},
#            {"id": 2, "title": "The Road", "year": 2006}]
#   new_id = max([b["id"] for b in books], default=0) + 1
#   books.append({"id": new_id, "title": "Klara and the Sun", "year": 2021})   # a)
#   for b in books:                                                           # b)
#       if b["id"] == 1:
#           b["year"] = 1966
#           break
#   books = [b for b in books if b["id"] != 2]                                # c)
#   print([b["title"] for b in books if b["year"] > 1960])                    # d)
#
# EXERCISE 9
#   accounts = [{"id": 1, "username": "sidd", "password": "x1", "email": "s@x.com"},
#               {"id": 2, "username": "ana", "password": "y2", "email": "a@x.com"}]
#   public = [{"id": a["id"], "username": a["username"], "email": a["email"]}
#             for a in accounts]
#   print(public)
#   # Listing the fields you WANT is safer than deleting the ones you don't:
#   # if someone later adds a "secret_token" field, it won't leak by accident.


print()
print("=" * 70)
print("  Lesson 01 complete. Next: python 02_python_essentials_functions.py")
print("=" * 70)

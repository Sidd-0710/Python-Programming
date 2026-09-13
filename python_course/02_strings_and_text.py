"""
===============================================================================
 LESSON 02 — STRINGS: WORKING WITH TEXT
===============================================================================

Time: about 75 minutes.
Assumes: lesson 01 (variables, types, f-strings).


-------------------------------------------------------------------------------
 THEORY: WHY TEXT DESERVES A WHOLE LESSON
-------------------------------------------------------------------------------

Almost everything a program touches arrives as text:

  * a web form submission                    -> text
  * the body of an API response (JSON)       -> text
  * a CSV file of sales figures              -> text
  * a filename you're about to rename        -> text
  * a log file you're scanning for errors    -> text

Cleaning, searching, splitting and reassembling text is not a side topic. For
web work and automation it IS the job. So this lesson is long, and worth it.

A string is an ordered sequence of characters. "Ordered" is the key word: each
character sits at a numbered position, and that numbering is what makes
slicing, searching and looping possible.

    "P y t h o n"
     0 1 2 3 4 5      <- positions, called INDEXES

Two rules that trip up every beginner:

  1. COUNTING STARTS AT 0. The first character is at index 0, not 1. There are
     good historical reasons; for now, just absorb it. The last character of a
     6-character string is at index 5.

  2. STRINGS ARE IMMUTABLE. You cannot change a character inside an existing
     string. Every "modification" actually builds a brand new string and
     usually re-points your variable at it. This is why `name.upper()` on its
     own does nothing unless you save the result. More on this in PART 5 - it
     is the number one string bug beginners write.
"""

LINE = "-" * 70


# =============================================================================
# PART 1 — CREATING STRINGS
# =============================================================================
print(LINE)
print("PART 1 — CREATING STRINGS")
print(LINE)

# Single or double quotes - identical in Python. Pick one and be consistent.
single = 'hello'
double = "hello"
print(single == double)         # True - genuinely the same string

# The reason both exist: it lets you include the other kind of quote inside.
print("It's a good day")             # apostrophe inside double quotes: easy
print('She said "hello" loudly')     # double quotes inside single quotes: easy

# If you need the same kind inside, ESCAPE it with a backslash.
# A backslash means "treat the next character literally, not as code".
print("She said \"hello\" loudly")
print('It\'s a good day')

# Useful escape sequences:
print("Line one\nLine two")          # \n = newline (start a new line)
print("Name:\tSidd")                 # \t = tab (a big aligned gap)
print("A backslash: \\")             # \\ = one literal backslash

# Triple quotes keep your line breaks exactly as typed. Great for multi-line
# text like an email template or an SQL query.
email_template = """Hi there,

Thanks for signing up.
- The Team"""
print(email_template)
print()

# RAW strings: put r before the quote and backslashes stop being special.
# Essential for Windows paths and (much later) regular expressions.
print(r"C:\Users\new\table.csv")     # without the r, \n and \t would wreck it
print()


# =============================================================================
# PART 2 — COMBINING AND REPEATING
# =============================================================================
print(LINE)
print("PART 2 — COMBINING AND REPEATING")
print(LINE)

first_name = "Sidd"
last_name = "Chirkute"

# Concatenation with + (works only between strings - see lesson 01).
full_name = first_name + " " + last_name
print(full_name)

# Repetition with * (string times a number).
print("ab" * 3)                      # ababab
print("=" * 30)                      # a divider - this is the LINE trick

# f-strings: the modern way. Everything in {braces} is evaluated and inserted.
age = 22
print(f"{first_name} {last_name} is {age} years old")

# f-strings can hold any expression, not just a plain variable name:
print(f"In 10 years: {age + 10}")
print(f"Uppercase: {first_name.upper()}")
print(f"Maths: {7 * 6}")

# The = suffix prints the expression AND its value. A brilliant debugging tool:
print(f"{age=}")                     # -> age=22
print(f"{age * 2=}")                 # -> age * 2=44
print()


# =============================================================================
# PART 3 — FORMATTING NUMBERS INSIDE STRINGS
# =============================================================================
print(LINE)
print("PART 3 — FORMAT SPECS (the bit after the colon)")
print(LINE)

price = 1234.5678
percent = 0.0725
count = 42

# Inside an f-string, add a colon then a format spec to control the display.
print(f"2 decimals:      {price:.2f}")      # 1234.57  (rounds for display)
print(f"0 decimals:      {price:.0f}")      # 1235
print(f"Thousands comma: {price:,.2f}")     # 1,234.57
print(f"As a percentage: {percent:.1%}")    # 7.3%
print()

# Alignment - the key to readable terminal tables and reports.
#   <  left-align      >  right-align      ^  centre
# The number is the total width to pad out to.
print(f"|{'Item':<15}|{'Qty':>5}|{'Price':>10}|")
print(f"|{'-' * 15}|{'-' * 5}|{'-' * 10}|")
print(f"|{'Keyboard':<15}|{3:>5}|{45.5:>10.2f}|")
print(f"|{'Monitor':<15}|{12:>5}|{229.99:>10.2f}|")
print(f"|{'Cable':<15}|{100:>5}|{3.2:>10.2f}|")
print()

# Zero-padding, handy for IDs, invoice numbers and timestamps.
print(f"Invoice INV-{count:05d}")           # INV-00042
print()


# =============================================================================
# PART 4 — INDEXING AND SLICING
# =============================================================================
print(LINE)
print("PART 4 — INDEXING AND SLICING")
print(LINE)

word = "Python"
#       P  y  t  h  o  n
#       0  1  2  3  4  5      <- normal indexes
#      -6 -5 -4 -3 -2 -1      <- negative indexes, counting from the end

print("word[0] :", word[0])      # P  - FIRST character
print("word[1] :", word[1])      # y
print("word[5] :", word[5])      # n  - last character
print("word[-1]:", word[-1])     # n  - last, without needing the length
print("word[-2]:", word[-2])     # o  - second from last
print("len()   :", len(word))    # 6  - how many characters

# word[6] would raise: IndexError: string index out of range
# Because valid indexes stop at len-1. This off-by-one is a rite of passage.

# SLICING takes a chunk: [start:stop]. The start is INCLUDED, the stop is
# EXCLUDED. Think of it as "up to but not including".
print("word[0:3] :", word[0:3])   # Pyt   - characters 0,1,2 (NOT 3)
print("word[2:5] :", word[2:5])   # tho
print("word[:3]  :", word[:3])    # Pyt   - omit start = from the beginning
print("word[3:]  :", word[3:])    # hon   - omit stop  = to the end
print("word[:]   :", word[:])     # Python - the whole thing
print("word[-3:] :", word[-3:])   # hon   - last 3 characters
print("word[::2] :", word[::2])   # Pto   - every 2nd character (a step)
print("word[::-1]:", word[::-1])  # nohtyP - reversed (step of -1)
print()

# WHY "stop is excluded" is actually convenient:
#   * the length of word[a:b] is simply b - a
#   * word[:3] + word[3:] reassembles the original perfectly, no gaps, no
#     duplicates
print("Reassembled:", word[:3] + word[3:])

# Slicing never raises IndexError, even when out of range - it just gives you
# what exists. This makes it safe for untrusted input.
print("word[0:999]:", word[0:999])

# A practical use: truncating text for a preview, like a blog listing.
article = "Python is a general purpose programming language used everywhere"
print("Preview:", article[:30] + "...")
print()


# =============================================================================
# PART 5 — STRING METHODS (and the immutability trap)
# =============================================================================
print(LINE)
print("PART 5 — METHODS")
print(LINE)

# A METHOD is a function that belongs to a value. You call it with a dot:
#     value.method_name(arguments)
# Read `name.upper()` as "ask name for its uppercase version".

name = "  Sidd Chirkute  "

print(f"original    : '{name}'")
print(f"upper()     : '{name.upper()}'")
print(f"lower()     : '{name.lower()}'")
print(f"strip()     : '{name.strip()}'")        # removes whitespace both ends
print(f"lstrip()    : '{name.lstrip()}'")       # left only
print(f"rstrip()    : '{name.rstrip()}'")       # right only
print(f"title()     : '{name.title()}'")        # Capitalises Each Word
print(f"replace()   : '{name.replace('Sidd', 'Sid')}'")
print()

# ***** THE #1 STRING BUG *****
# Strings are IMMUTABLE. A method NEVER changes the original. It RETURNS a new
# string. If you don't capture the return value, nothing happens.

messy = "  hello  "
messy.strip()                       # <- result thrown away! Does nothing!
print(f"after calling strip(): '{messy}'")      # still '  hello  '

clean = messy.strip()               # <- capture the result
print(f"captured into a new name: '{clean}'")

messy = messy.strip()               # <- or re-point the same name at it
print(f"reassigned to itself: '{messy}'")

# Rule of thumb: if a string method call isn't on the right-hand side of an `=`
# or inside a print/f-string, you've probably wasted it.
print()

# --- Methods that ask questions (they return True or False) ---
email = "Sidd@Example.COM"
print("startswith('Sidd'):", email.startswith("Sidd"))
print("endswith('.com')  :", email.endswith(".com"))         # False! case
print("endswith('.com')  :", email.lower().endswith(".com")) # True - normalise first
print("'@' in email      :", "@" in email)          # `in` searches for a substring
print("isdigit()         :", "12345".isdigit())     # all characters are digits?
print("isalpha()         :", "abc123".isalpha())    # all letters?
print()

# Chaining: each method returns a string, so you can call another on it.
# Read left to right: strip it, then lowercase it, then replace spaces.
raw_input_text = "  Sales Report 2024.CSV  "
slug = raw_input_text.strip().lower().replace(" ", "_")
print(f"'{raw_input_text}' -> '{slug}'")
print()

# --- find() and index() ---
sentence = "the quick brown fox"
print("find('brown')   :", sentence.find("brown"))     # 10 = start position
print("find('zebra')   :", sentence.find("zebra"))     # -1 = not found
# .index() does the same but raises ValueError when missing. Use .find() when
# "not there" is a normal possibility, .index() when it's a real problem.
print()


# =============================================================================
# PART 6 — split() AND join(): THE AUTOMATION WORKHORSES
# =============================================================================
print(LINE)
print("PART 6 — SPLIT AND JOIN")
print(LINE)

# These two are the most valuable string methods for data work. Learn them well.

# split() breaks a string into a LIST of pieces (lists are lesson 06).
csv_row = "Sidd,Chirkute,22,Mumbai"
fields = csv_row.split(",")
print("split on comma:", fields)
print("the third field:", fields[2])

# With no argument, split() splits on any run of whitespace - perfect for
# breaking a sentence into words, or parsing a log line.
words = "the quick brown fox".split()
print("split on whitespace:", words)
print("word count:", len(words))

# maxsplit limits how many splits happen - useful when only the first part is
# structured and the rest is free text.
log_line = "2024-05-01 ERROR Database connection failed on retry 3"
date, level, message = log_line.split(" ", 2)
print(f"date={date}  level={level}  message='{message}'")
print()

# join() is the exact opposite: glue a list of strings together.
# The syntax looks backwards at first. Read it as:
#     "the glue".join(the_pieces)
parts = ["2024", "05", "01"]
print("joined with '-':", "-".join(parts))
print("joined with '/':", "/".join(parts))
print("joined with '' :", "".join(parts))

# A real one: turn a list of names into a readable sentence.
attendees = ["Sidd", "Ana", "Marco"]
print("Attending: " + ", ".join(attendees))

# IMPORTANT: join() only works on strings. Numbers must be converted first,
# or you get: TypeError: sequence item 0: expected str instance, int found
scores = [90, 85, 77]
# ", ".join(scores)                       # would fail
print("Scores: " + ", ".join(str(s) for s in scores))   # converts each first
print()

# The classic round trip - split, change something, join back. This is 80% of
# real text automation:
filename = "quarterly sales report.txt"
clean_filename = "_".join(filename.split())
print(f"'{filename}' -> '{clean_filename}'")
print()


# =============================================================================
# PART 7 — A REAL EXAMPLE: CLEANING MESSY USER DATA
# =============================================================================
print(LINE)
print("PART 7 — REAL EXAMPLE: CLEANING SIGN-UP DATA")
print(LINE)

# This is close to code you'd genuinely write in a web backend. Users type
# inconsistently: stray spaces, random capitals, inconsistent formats. You
# normalise before storing, so that later comparisons and lookups work.

raw_signup = "   SIDD.Chirkute@Example.COM   "

email = raw_signup.strip().lower()          # trim, then normalise case
username = email.split("@")[0]              # everything before the @
domain = email.split("@")[1]                # everything after
display_name = username.replace(".", " ").title()

print(f"raw         : '{raw_signup}'")
print(f"stored email: '{email}'")
print(f"username    : '{username}'")
print(f"domain      : '{domain}'")
print(f"display name: '{display_name}'")

# Why normalising matters: without .lower(), "Sidd@X.com" and "sidd@x.com"
# would be treated as two different accounts, and your "email already
# registered" check would silently let duplicates through.
print()


# =============================================================================
# PART 8 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 8 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: forgetting methods return new strings (covered in PART 5 - it is
#   worth repeating because you WILL do it anyway).
#       text.upper()          # does nothing useful
#       text = text.upper()   # correct

# MISTAKE 2: comparing text without normalising.
print("'Sidd' == 'sidd' ->", "Sidd" == "sidd")                    # False
print("normalised       ->", "Sidd".lower() == "sidd".lower())    # True
#   Any time you compare user-typed text, .strip().lower() it first.

# MISTAKE 3: off-by-one with indexes.
demo = "hello"
print("last char, correct:", demo[len(demo) - 1])   # or simply demo[-1]
#   demo[len(demo)] would be IndexError. len is 5; valid indexes are 0-4.

# MISTAKE 4: building a big string with += inside a loop.
#   It works, but it copies the entire string every single time, so it gets
#   slow with thousands of items. Collect pieces in a list and "".join() them
#   at the end. (You'll see loops properly in lesson 07.)

# MISTAKE 5: assuming .split(",") is enough to parse CSV.
#   It breaks the moment a field contains a comma inside quotes, e.g.
#       Smith, John,"Flat 2, High St",London
#   For real CSV files, use the `csv` module (lesson 14). Use split() for
#   simple, self-made formats.

# MISTAKE 6: trying to change a character in place.
#   demo[0] = "H"    ->  TypeError: 'str' object does not support item assignment
#   Build a new string instead:
print("rebuilt:", "H" + demo[1:])
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# EXERCISE 1 — Initials
#   Given full_name = "Siddheshwar Vijay Chirkute", print "S.V.C."
#   Hint: split into words, take [0] of each, join with ".".
#
# EXERCISE 2 — Email validator (a rough one)
#   For each of these, print the address and whether it looks valid:
#       "sidd@example.com", "not-an-email", "a@b.co", "@nope.com"
#   Treat it as valid if it contains "@", has a "." after the "@", and has at
#   least one character before the "@".
#
# EXERCISE 3 — Filename cleaner (automation)
#   Turn "  My Report FINAL (v2).PDF  " into "my_report_final_(v2).pdf".
#   Steps: strip, lowercase, replace spaces with underscores.
#
# EXERCISE 4 — Log line parser
#   Given: "2024-05-01 14:32:07 ERROR Payment gateway timeout"
#   Print the date, the time, the level, and the message separately, then
#   print just the YEAR from the date. Use split() and slicing.
#
# EXERCISE 5 — Receipt table
#   Print a neat 3-column table (Item, Qty, Price) with aligned columns and
#   prices to 2 decimal places, using f-string alignment, for:
#       Coffee 2 3.50 / Sandwich 1 6.75 / Cookie 3 1.2
#   Then print a TOTAL row.
#
# EXERCISE 6 — Palindrome check
#   Check whether "A man a plan a canal Panama" is a palindrome (reads the same
#   backwards) once you remove spaces and ignore capitals.
#   Hint: .replace(" ", ""), .lower(), and the [::-1] slice.
#
# EXERCISE 7 — Word frequency, the manual way
#   Count how many words are in a sentence, and how many of them are longer
#   than 4 characters. (You can do this with split, len, and counting by hand
#   for now - lesson 07 will make it elegant.)

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   full_name = "Siddheshwar Vijay Chirkute"
#   parts = full_name.split()
#   initials = ".".join(p[0] for p in parts) + "."
#   print(initials)                      # -> S.V.C.
#
# EXERCISE 2
#   addr = "sidd@example.com"
#   has_at = "@" in addr
#   before = addr.split("@")[0] if has_at else ""
#   after = addr.split("@")[1] if has_at else ""
#   valid = has_at and len(before) > 0 and "." in after
#   print(addr, valid)
#   (The `x if y else z` form is lesson 05. Plain version: check `has_at`
#    first with an if statement.)
#
# EXERCISE 3
#   raw = "  My Report FINAL (v2).PDF  "
#   clean = raw.strip().lower().replace(" ", "_")
#   print(clean)                         # -> my_report_final_(v2).pdf
#
# EXERCISE 4
#   line = "2024-05-01 14:32:07 ERROR Payment gateway timeout"
#   date, time, level, message = line.split(" ", 3)
#   print(date, time, level, message, sep=" | ")
#   print("Year:", date[:4])             # or date.split("-")[0]
#
# EXERCISE 5
#   print(f"{'Item':<12}{'Qty':>5}{'Price':>10}")
#   print("-" * 27)
#   print(f"{'Coffee':<12}{2:>5}{3.50:>10.2f}")
#   print(f"{'Sandwich':<12}{1:>5}{6.75:>10.2f}")
#   print(f"{'Cookie':<12}{3:>5}{1.20:>10.2f}")
#   total = 2 * 3.50 + 1 * 6.75 + 3 * 1.20
#   print("-" * 27)
#   print(f"{'TOTAL':<12}{'':>5}{total:>10.2f}")
#
# EXERCISE 6
#   phrase = "A man a plan a canal Panama"
#   cleaned = phrase.replace(" ", "").lower()
#   print(cleaned == cleaned[::-1])      # -> True
#
# EXERCISE 7
#   sentence = "Python makes text processing genuinely straightforward"
#   words = sentence.split()
#   print("Words:", len(words))
#   long_words = [w for w in words if len(w) > 4]   # lesson 11 syntax
#   print("Longer than 4:", len(long_words), long_words)


print("=" * 70)
print("Lesson 02 complete. Next: 03_numbers_and_math.py")
print("=" * 70)

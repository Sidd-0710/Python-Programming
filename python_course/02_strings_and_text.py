r"""
===============================================================================
 LESSON 02 — STRINGS: WORKING WITH TEXT
===============================================================================

Time: about 75 minutes (there's a good place for a break halfway).
Assumes: lesson 01 (variables, types, f-strings).


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. write text that contains quotes, new lines and tabs          (PART 1)
  2. glue text together and repeat it                             (PART 2)
  3. show numbers neatly: 2 decimals, commas, lined-up columns    (PART 3)
  4. pull out single letters or chunks of text                    (PART 4)
  5. clean text up: remove spaces, change case, search it         (PART 5)
  6. split a sentence into words, and join words back together    (PART 6)

NEW WORDS - come back here whenever you forget one:

  string       text. Any value in quotes:  "hello"  'Sidd'  "42"
  character    one letter, digit, space or symbol inside a string
  index        the POSITION of a character. Counting starts at 0, not 1
  slice        a chunk of a string, taken by position:  word[0:3]
  method       a function that belongs to a value, used with a dot:
               name.upper()  means "give me name in capitals"
  escape       a backslash \ that changes the meaning of the next character:
               \n means "new line"
  whitespace   invisible characters: spaces, tabs, new lines
  list         several values in square brackets:  ["a", "b", "c"]
               (lesson 06 is all about lists - here you only need to
               recognise one)
  immutable    "can't be changed". A string can never be edited in place -
               you always make a NEW string instead


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
#                                 (== asks "are these equal?" - lesson 05)

# The reason both exist: it lets you include the other kind of quote inside.
print("It's a good day")             # apostrophe inside double quotes: easy
print('She said "hello" loudly')     # double quotes inside single quotes: easy

# If you need the same kind inside, ESCAPE it with a backslash.
# A backslash means "treat the next character literally, not as code".
print("She said \"hello\" loudly")   # \" means "a real quote mark, not the end"
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

# TRY IT NOW (1 minute):
#   Write ONE print() line that shows these two lines of output:
#       Roses are red
#       Violets are blue
#   (Answer: print("Roses are red\nViolets are blue") - the \n starts a new line.)


# =============================================================================
# PART 2 — COMBINING AND REPEATING
# =============================================================================
print(LINE)
print("PART 2 — COMBINING AND REPEATING")
print(LINE)

first_name = "Sidd"
last_name = "Chirkute"

# Concatenation ("joining") with + (works only between strings - see lesson 01).
full_name = first_name + " " + last_name   # "Sidd" + " " + "Chirkute"
print(full_name)

# Repetition with * (string times a number).
print("ab" * 3)                      # ababab
print("=" * 30)                      # a divider - this is the LINE trick
                                     # from the top of the file

# f-strings: the modern way. Everything in {braces} is evaluated and inserted.
age = 22
print(f"{first_name} {last_name} is {age} years old")

# f-strings can hold any expression, not just a plain variable name:
print(f"In 10 years: {age + 10}")
print(f"Uppercase: {first_name.upper()}")   # .upper() is in PART 5
print(f"Maths: {7 * 6}")

# The = suffix prints the expression AND its value. A brilliant debugging tool:
print(f"{age=}")                     # -> age=22
print(f"{age * 2=}")                 # -> age * 2=44
print()

# TRY IT NOW (1 minute):
#   Make a variable  city = "Pune"  and print an f-string that says:
#       Sidd lives in Pune
#   using first_name and city. Then print a line of 20 stars using *.


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
# The value itself never changes - only how it's SHOWN.
print(f"2 decimals:      {price:.2f}")      # 1234.57  (rounds for display)
print(f"0 decimals:      {price:.0f}")      # 1235
print(f"Thousands comma: {price:,.2f}")     # 1,234.57
print(f"As a percentage: {percent:.1%}")    # 7.3%
print()
#   How to read  :.2f  -  ":" starts the format spec, ".2" means 2 decimal
#   places, "f" means "show it as a decimal number". You'll mostly copy these
#   four; you don't need to invent new ones.

# Alignment - the key to readable terminal tables and reports.
#   <  left-align      >  right-align      ^  centre
# The number is the total width to pad out to.
#   {'Item':<15}  means "the text Item, left-aligned in a space 15 characters wide"
print(f"|{'Item':<15}|{'Qty':>5}|{'Price':>10}|")
print(f"|{'-' * 15}|{'-' * 5}|{'-' * 10}|")
print(f"|{'Keyboard':<15}|{3:>5}|{45.5:>10.2f}|")
print(f"|{'Monitor':<15}|{12:>5}|{229.99:>10.2f}|")
print(f"|{'Cable':<15}|{100:>5}|{3.2:>10.2f}|")
print()

# Zero-padding, handy for IDs, invoice numbers and timestamps.
print(f"Invoice INV-{count:05d}")           # INV-00042  (5 digits wide, 0-padded)
print()

# TRY IT NOW (1 minute):
#   Print the price 19.5 as  19.50  using :.2f.  Then print 0.25 as  25%
#   using :.0%.  (Answers: f"{19.5:.2f}" and f"{0.25:.0%}")


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
print("len()   :", len(word))    # 6  - how many characters (len = length)

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
#   The pattern is  [start:stop:step].  You'll use [start:stop] all the time;
#   the step version is rarer - [::-1] to reverse is the one worth remembering.

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
print("Preview:", article[:30] + "...")    # the first 30 characters, then ...
print()

# TRY IT NOW (2 minutes):
#   With  word = "Python",  predict each of these, then check by printing them:
#       word[2]     word[-1]     word[1:4]     word[:2]
#   (Answers: t   n   yth   Py)


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. You've learned how text is built and how to cut it
#  up. After the break: the tools that CLEAN text (PARTS 5-7).
# -----------------------------------------------------------------------------


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
print(f"replace()   : '{name.replace('Sidd', 'Sid')}'")   # swap "Sidd" for "Sid"
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
#   The same thing, one step per line - exactly what the chain above does:
#       step1 = raw_input_text.strip()       "Sales Report 2024.CSV"
#       step2 = step1.lower()                "sales report 2024.csv"
#       slug  = step2.replace(" ", "_")      "sales_report_2024.csv"
#   When a chain confuses you, split it up like this and print each step.
print()

# --- find() and index() ---
sentence = "the quick brown fox"
print("find('brown')   :", sentence.find("brown"))     # 10 = start position
print("find('zebra')   :", sentence.find("zebra"))     # -1 = not found
# .index() does the same but raises ValueError when missing. Use .find() when
# "not there" is a normal possibility, .index() when it's a real problem.
print()

# TRY IT NOW (2 minutes):
#   Start with  messy_name = "   aNA lopez  ".  Using methods, make it
#   "Ana Lopez" and print it. Remember to SAVE the result with =.
#   (Answer: clean_name = messy_name.strip().title())


# =============================================================================
# PART 6 — split() AND join(): THE AUTOMATION WORKHORSES
# =============================================================================
print(LINE)
print("PART 6 — SPLIT AND JOIN")
print(LINE)

# These two are the most valuable string methods for data work. Learn them well.

# split() breaks a string into a LIST of pieces (lists are lesson 06).
csv_row = "Sidd,Chirkute,22,Mumbai"
fields = csv_row.split(",")                 # cut the text at every comma
print("split on comma:", fields)
print("the third field:", fields[2])        # lists count from 0 too: [2] is the 3rd

# With no argument, split() splits on any run of whitespace - perfect for
# breaking a sentence into words, or parsing a log line.
words = "the quick brown fox".split()
print("split on whitespace:", words)
print("word count:", len(words))

# maxsplit limits how many splits happen - useful when only the first part is
# structured and the rest is free text.
log_line = "2024-05-01 ERROR Database connection failed on retry 3"
date, level, message = log_line.split(" ", 2)
#   In plain English: "split at spaces, but only the first 2 times" - so you
#   get exactly 3 pieces, and the whole message stays in one piece.
#   `date, level, message = ...` is lesson 01's multiple assignment.
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
#     ", ".join([90, 85, 77])                      # would fail - they're numbers
score_texts = [str(90), str(85), str(77)]           # turn each number into text
print("Scores: " + ", ".join(score_texts))
print()

# The classic round trip - split, change something, join back. This is 80% of
# real text automation:
filename = "quarterly sales report.txt"
clean_filename = "_".join(filename.split())
#   Step by step:  filename.split()  ->  ["quarterly", "sales", "report.txt"]
#                  "_".join(...)     ->  "quarterly_sales_report.txt"
print(f"'{filename}' -> '{clean_filename}'")
print()

# TRY IT NOW (2 minutes):
#   Start with  date_text = "2024/12/25".  Use split and join to print
#   2024-12-25.
#   (Answer: print("-".join(date_text.split("/"))))


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
username = email.split("@")[0]              # piece 0: everything before the @
domain = email.split("@")[1]                # piece 1: everything after
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
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * Strings are text in quotes. \n is a new line, \t a tab.
#   * + joins strings, * repeats them, f-strings mix in variables.
#   * Format specs after a colon:  {price:.2f}  {rate:.1%}  {name:<10}
#   * Indexes start at 0. word[0] is the first character, word[-1] the last.
#   * Slices  word[start:stop]  include start, EXCLUDE stop.
#   * Methods (upper, lower, strip, replace...) RETURN a new string - save it!
#   * text.split(",") makes a list of pieces; ", ".join(pieces) glues them back.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. With  s = "banana",  what is  s[0]?  s[-1]?  s[1:3]?
#   Q2. After  name = " Ana "  and  name.strip(),  what is name?
#   Q3. What does  "a,b,c".split(",")  give?
#   Q4. What does  "-".join(["1", "2", "3"])  give?
#   Q5. How do you show 3.14159 as 3.14 inside an f-string?
#
# ANSWERS
#   A1. "b",  "a",  "an"  (positions 1 and 2 - stop is excluded).
#   A2. Still " Ana ". strip() RETURNED a new string that nobody saved.
#       Write  name = name.strip().
#   A3. The list  ["a", "b", "c"].
#   A4. "1-2-3".
#   A5. f"{3.14159:.2f}"


# =============================================================================
# EXERCISES
# =============================================================================
#
# WARM-UP A (easy) — Shout it
#   Store your name in a variable and print it in CAPITAL letters.
#
# WARM-UP B (easy) — First and last
#   Print the FIRST letter and the LAST letter of your name, using [0] and [-1].
#
# WARM-UP C (easy) — Repeat
#   Print "ha" five times in a row (hahahahaha) using *.
#
# EXERCISE 1 (medium) — Initials
#   Given full_name = "Siddheshwar Vijay Chirkute", print "S.V.C."
#   Hint: split into words first. Each word is then words[0], words[1] and
#   words[2], and the first letter of a word is word[0].
#
# EXERCISE 2 (medium) — Email validator (a rough one)
#   For ONE address at a time, print the address and whether it looks valid.
#   Try it with each of:  "sidd@example.com", "not-an-email", "a@b.co", "@nope.com"
#   Treat it as valid if it contains "@", has a "." after the "@", and has at
#   least one character before the "@".
#   Hint: address.find("@") gives the position of the @ (or -1).
#
# EXERCISE 3 (easy) — Filename cleaner (automation)
#   Turn "  My Report FINAL (v2).PDF  " into "my_report_final_(v2).pdf".
#   Steps: strip, lowercase, replace spaces with underscores.
#
# EXERCISE 4 (medium) — Log line parser
#   Given: "2024-05-01 14:32:07 ERROR Payment gateway timeout"
#   Print the date, the time, the level, and the message separately, then
#   print just the YEAR from the date. Use split() and slicing.
#
# EXERCISE 5 (medium) — Receipt table
#   Print a neat 3-column table (Item, Qty, Price) with aligned columns and
#   prices to 2 decimal places, using f-string alignment, for:
#       Coffee 2 3.50 / Sandwich 1 6.75 / Cookie 3 1.2
#   Then print a TOTAL row.
#
# EXERCISE 6 (medium) — Palindrome check
#   Check whether "A man a plan a canal Panama" is a palindrome (reads the same
#   backwards) once you remove spaces and ignore capitals.
#   Hint: .replace(" ", ""), .lower(), and the [::-1] slice.
#
# EXERCISE 7 (challenge) — Word count
#   Count how many words are in a sentence. Then, for a sentence of 5 words,
#   count how many are longer than 4 characters by checking len() of each
#   word one at a time. (Lesson 07's loops make the second part much shorter.)

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   my_name = "Sidd"
#   print(my_name.upper())          # -> SIDD
#
# WARM-UP B
#   my_name = "Sidd"
#   print(my_name[0], my_name[-1])  # -> S d
#
# WARM-UP C
#   print("ha" * 5)                 # -> hahahahaha
#
# EXERCISE 1
#   full_name = "Siddheshwar Vijay Chirkute"
#   words = full_name.split()                   # ["Siddheshwar", "Vijay", "Chirkute"]
#   initials = words[0][0] + "." + words[1][0] + "." + words[2][0] + "."
#   print(initials)                             # -> S.V.C.
#   words[0][0] reads as "word number 0, then its letter number 0".
#   Once you know loops (lesson 07) and generators (lesson 11), this becomes:
#       ".".join(word[0] for word in words) + "."
#
# EXERCISE 2
#   address = "sidd@example.com"
#   at = address.find("@")               # position of the @, or -1 if missing
#   before = address[:at]                # the text before the @
#   after = address[at + 1:]             # the text after the @
#   valid = at > 0 and "." in after      # `and`: BOTH must be True (lesson 05)
#   print(address, valid)
#   Why `at > 0`: -1 means there's no @ at all, and 0 means the @ is the very
#   first character - so nothing comes before it. Both are invalid.
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
#   (sep=" | " tells print() what to put BETWEEN the items, instead of a space.)
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
#   sentence = "Python makes text processing easy"
#   words = sentence.split()
#   print("Words:", len(words))                              # -> 5
#   long_count = 0
#   long_count += len(words[0]) > 4      # True counts as 1, False as 0
#   long_count += len(words[1]) > 4
#   long_count += len(words[2]) > 4
#   long_count += len(words[3]) > 4
#   long_count += len(words[4]) > 4
#   print("Longer than 4:", long_count)                      # -> 3
#   Repetitive, right? That feeling is exactly why loops exist (lesson 07):
#       long_words = [w for w in words if len(w) > 4]        # lesson 11 syntax


print("=" * 70)
print("Lesson 02 complete. Next: 03_numbers_and_math.py")
print("=" * 70)

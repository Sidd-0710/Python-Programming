"""
===============================================================================
 LESSON 04 — GETTING INPUT FROM THE OUTSIDE WORLD
===============================================================================

Time: about 45 minutes (there's a good place for a break halfway).
Assumes: lessons 01-03.


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. ask the person using your program a question                 (PART 1)
  2. remember that their answer is ALWAYS text                    (PART 2)
  3. cope when they type something that isn't a number            (PART 3)
  4. keep asking until the answer makes sense                     (PART 4)
  5. give a program its input when you start it                   (PART 5)

NEW WORDS - come back here whenever you forget one:

  input        data coming INTO your program from outside - here, from the
               keyboard
  input()      the function that asks a question and waits for an answer
  prompt       the question text that input() shows, like "Your name? "
  convert      turn one type into another:  int("22")  turns text into 22
  validate     check that input makes sense BEFORE using it
  ValueError   the error int() raises when the text isn't a whole number
  try/except   "try this; if that error happens, do this instead"
               (a preview here - lesson 12 teaches it properly)
  loop         code that repeats (a preview here - lesson 07 teaches it)
  command line the terminal line you type to run a program
  argument     an extra word typed after the program's name on the command
               line:  python3 my_tool.py report.csv  -  report.csv is one

HOW TO TYPE ANSWERS: run this file from the terminal (or with the ▷ button,
which uses the terminal too). When it stops and waits, click in the terminal,
type your answer, and press Enter.


-------------------------------------------------------------------------------
 THEORY: A PROGRAM THAT CAN'T LISTEN IS A PARLOUR TRICK
-------------------------------------------------------------------------------

So far every value in your programs was typed by you, in the source code. That
makes them demos, not tools. A real program takes input from somewhere:

  SOURCE OF INPUT              YOU'LL MEET IT IN
  ---------------------------  ---------------------------------------------
  the keyboard  - input()      this lesson
  a file        - open()       lesson 13
  a CSV / JSON file            lesson 14
  the command line - sys.argv  this lesson (PART 5)
  a web request / API          lessons 21-22
  a database                   beyond this course

They differ in mechanics but share ONE crucial property, which is the real
lesson here:

        *** EVERYTHING ARRIVES AS TEXT, AND YOU CANNOT TRUST IT. ***

Text, because keyboards, files and network sockets move characters, not typed
values. Untrusted, because the human on the other end will eventually type
"twelve" into your age box, or leave it blank, or paste in 400 characters of
emoji. Professional code assumes this and copes with it.

This lesson is about that handshake: read text, convert it, check it, and
decide what to do when it's wrong.
"""

import sys        # "sys" = system: tools for talking to the terminal (PART 5)

LINE = "-" * 70


# -----------------------------------------------------------------------------
# A NOTE ABOUT THIS FILE'S `ask()` HELPER
# -----------------------------------------------------------------------------
# The real function for reading the keyboard is input(). It has one problem for
# a teaching file: if you run this script somewhere without a keyboard attached
# (an automated run, a CI server), input() crashes or hangs forever.
#
# So this file defines a tiny wrapper. It uses the genuine input() when a
# keyboard is available, and falls back to a sensible example answer when not.
# You'll fully understand `def` in lesson 10 - for now, read it as "make a
# reusable tool named ask".
#
# In plain English, ask("Your name? ", "Sidd") means:
#     "if a person is at the keyboard, ask them 'Your name? ' and give back
#      their answer; otherwise pretend they typed Sidd."
#
# IN YOUR OWN CODE, just call input() directly. This wrapper is a teaching aid.

def ask(prompt, example_answer):
    """Behaves like input(), but survives having no keyboard attached."""
    if sys.stdin.isatty():              # isatty() = "is a real terminal?"
        return input(prompt)
    print(f"{prompt}{example_answer}    <-- example answer (no keyboard here)")
    return example_answer


# =============================================================================
# PART 1 — input() BASICS
# =============================================================================
print(LINE)
print("PART 1 — READING FROM THE KEYBOARD")
print(LINE)

# input("prompt") does three things:
#   1. prints the prompt
#   2. stops the program dead and waits for the user to press Enter
#   3. hands back what they typed, ALWAYS as a string
#
# The real call looks like this:
#       name = input("What is your name? ")
# Here we use the ask() wrapper so the file runs anywhere:

name = ask("What is your name? ", "Sidd")
print(f"Hello, {name}!")
print(f"input() gave us a {type(name)}")
print()

# Put a trailing space at the end of your prompt ("Name: " not "Name:") so the
# cursor isn't jammed against the text. A small thing that makes your tools
# feel finished.

# TRY IT NOW (1 minute):
#   Run the file from the terminal and type your own name when it asks.
#   The greeting uses whatever you typed.


# =============================================================================
# PART 2 — THE GOLDEN RULE: input() ALWAYS RETURNS A STRING
# =============================================================================
print(LINE)
print("PART 2 — EVERYTHING IS A STRING")
print(LINE)

age_text = ask("How old are you? ", "22")

print(f"You typed: {age_text!r} which is a {type(age_text).__name__}")
# The !r in the f-string means "show it the way a programmer would" - with the
# quotes visible. Brilliant for spotting invisible problems like "22 " with a
# trailing space, which looks identical to "22" when printed normally.
# type(...).__name__ just gives the type's short name: str instead of <class 'str'>.

# THE BUG EVERY BEGINNER WRITES:
#       age_text + 1          -> TypeError: can only concatenate str to str
#       age_text * 2          -> "2222"  (repeats the text - no error, just
#                                         a silently wrong answer!)
print(f'age_text * 2 gives "{age_text * 2}" - text repeated, not doubled')

# THE FIX: convert, then calculate.
age = int(age_text)             # in plain English: "turn the text into a whole number"
print(f"int(age_text) * 2 gives {age * 2} - actual arithmetic")
print(f"In 10 years you'll be {age + 10}")
print()

# You'll often see the conversion done in one line. Perfectly fine:
#       age = int(input("How old are you? "))
# Read it inside-out: first input() asks, THEN int() converts the answer.
# Just be aware it will crash if they type anything non-numeric.

# TRY IT NOW (1 minute):
#   Run the file and answer the age question with the word  twelve.
#   Read the error's last line: ValueError. That's what PART 3 is about.


# =============================================================================
# PART 3 — WHEN CONVERSION FAILS
# =============================================================================
print(LINE)
print("PART 3 — INVALID INPUT")
print(LINE)

# int() raises ValueError on anything that isn't a clean whole number:
#       int("abc")      -> ValueError: invalid literal for int()
#       int("")         -> ValueError
#       int("12.5")     -> ValueError  (it's not a whole number)
#       int(" 42 ")     -> 42          (surrounding spaces ARE tolerated)
#       float("12.5")   -> 12.5        (float is more forgiving)

# You have two strategies for coping.

# STRATEGY A — LOOK BEFORE YOU LEAP: check it's convertible first.
# .isdigit() returns True only if every character is 0-9.
samples = ["42", "abc", "", "3.7", "-5", " 8 "]      # six test answers (a list)
print("Which of these survive int()?")
# In plain English: "for each sample in the list, check whether it's all
# digits, and print the answer". (A `for` loop - lesson 07.)
for sample in samples:
    looks_ok = sample.strip().isdigit()
    print(f"  {sample!r:<8} isdigit -> {looks_ok}")

# Note the gaps: isdigit() says False for "-5" (the minus sign isn't a digit)
# and for "3.7" (the dot isn't). It is a rough check, not a complete one.

# STRATEGY B — TRY IT AND CATCH THE FAILURE. This is the approach real Python
# code uses, and it handles every case correctly. Lesson 12 covers it properly;
# here is a preview so you know where this is going:
raw = "not a number"
try:                                    # "try to run the indented lines..."
    number = int(raw)
    print(f"Converted fine: {number}")
except ValueError:                      # "...and if a ValueError happens, run these instead"
    print(f"Could not convert {raw!r} to a number - using 0 instead")
    number = 0

print(f"number is now {number}")
print()

# WHY STRATEGY B WINS: int() knows the rules better than your check ever will
# (negatives, underscores in numbers, unicode digits, leading whitespace...).
# "Ask forgiveness, not permission" is idiomatic Python.


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. The key ideas are done: input is text, convert it,
#  and expect bad answers. After the break: patterns for real tools.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 4 — A VALIDATION LOOP (the standard interactive pattern)
# =============================================================================
print(LINE)
print("PART 4 — KEEP ASKING UNTIL IT'S VALID")
print(LINE)

# This is THE pattern for interactive command-line tools: loop until the input
# is acceptable. `while True` means "repeat forever", and `break` steps out of
# the loop. Lesson 07 covers loops properly - read this for the shape of it.
#
# In plain English:
#   repeat:
#       ask how many items
#       if the answer is a whole number above 0 -> accept it and STOP repeating
#       otherwise -> say what's wrong, and go round again
#       (after 3 tries, give up and use 1, so this demo can never get stuck)

attempts = 0
while True:
    attempts += 1
    quantity_text = ask("How many items? ", "3")

    if quantity_text.strip().isdigit() and int(quantity_text) > 0:
        quantity = int(quantity_text)
        print(f"Great - ordering {quantity} items.")
        break                       # valid: leave the loop

    print("  Please enter a whole number greater than 0.")

    if attempts >= 3:               # a safety valve so this demo can't hang
        quantity = 1
        print("  Too many attempts - defaulting to 1.")
        break

print(f"Final quantity: {quantity}")
print()

# TRY IT NOW (1 minute):
#   Run the file and answer "How many items?" with  abc,  then  0,  then  5.
#   Watch the loop go round until it gets a good answer.


# =============================================================================
# PART 5 — COMMAND-LINE ARGUMENTS (the automation way to take input)
# =============================================================================
print(LINE)
print("PART 5 — ARGUMENTS FROM THE COMMAND LINE")
print(LINE)

# input() is fine for a human sitting at a keyboard. But an automation script
# that runs at 3am on a schedule has nobody to answer its questions. Those
# scripts take their input as ARGUMENTS on the command line:
#
#       python3 04_input_and_conversion.py report.csv 2024
#
# sys.argv is a list of those words. argv[0] is always the script's own name.

print("sys.argv contains:", sys.argv)
print(f"Script name : {sys.argv[0]}")

# argv[1:] is everything AFTER the script name (slicing, from lesson 02).
user_args = sys.argv[1:]
if user_args:                   # "if the list isn't empty" (lesson 05)
    print(f"You passed {len(user_args)} argument(s): {user_args}")
else:
    print("No extra arguments passed.")
    print("Try running:  python3 04_input_and_conversion.py hello 42")

# Same golden rule applies - arguments arrive as strings and need converting.
# For anything beyond a couple of arguments, use the `argparse` module, which
# gives you --flags, help text and validation for free. See lesson 18.
print()

# TRY IT NOW (1 minute):
#   In the terminal, run:   python3 04_input_and_conversion.py hello 42
#   Look for the PART 5 output. Notice "42" arrived in quotes - it's text.


# =============================================================================
# PART 6 — A COMPLETE LITTLE TOOL
# =============================================================================
print(LINE)
print("PART 6 — PUTTING IT TOGETHER: TIP CALCULATOR")
print(LINE)

# Everything from lessons 01-04 in one small, genuinely useful program.

bill_text = ask("Bill amount: ", "87.40")
people_text = ask("Number of people: ", "4")
tip_text = ask("Tip percent [15]: ", "18")      # [15] tells the user the default

# Convert with sensible fallbacks if the input is unusable.
try:
    bill = float(bill_text)
except ValueError:
    print("  Bad bill amount - using 0")
    bill = 0.0

try:
    people = int(people_text)
    if people < 1:              # nobody can split a bill 0 ways
        people = 1
except ValueError:
    print("  Bad people count - using 1")
    people = 1

# An empty answer should mean "use the default", not "crash".
# In plain English: "if they typed something, use it; otherwise use 15".
if tip_text.strip():
    tip_percent = float(tip_text)
else:
    tip_percent = 15.0

tip_amount = bill * tip_percent / 100
total = bill + tip_amount
per_person = total / people

# Build the labels first, then line everything up in columns (lesson 02 PART 3).
tip_label = f"Tip @ {tip_percent}%"
each_label = f"Each (x{people})"

print()
print(f"  {'Bill':<12}{bill:>10.2f}")
print(f"  {tip_label:<12}{tip_amount:>10.2f}")
print(f"  {'-' * 22}")
print(f"  {'Total':<12}{total:>10.2f}")
print(f"  {each_label:<12}{per_person:>10.2f}")
print()


# =============================================================================
# PART 7 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 7 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: forgetting to convert. The silent version is the dangerous one:
#   "5" * 3 gives "555" with no error at all. Your program keeps running and
#   produces nonsense. Always convert at the boundary, the moment data enters.

# MISTAKE 2: not stripping whitespace. Users add trailing spaces constantly.
#   "yes " == "yes" is False. Get into the habit: .strip() everything.
answer = " YES "
print(f"raw comparison : {answer == 'yes'}")
print(f"normalised     : {answer.strip().lower() == 'yes'}")

# MISTAKE 3: assuming input() returns a number. It never does, not once, ever.

# MISTAKE 4: letting a crash be your validation. A script that dies with
#   ValueError in front of a user is unfinished work. Catch it and explain.

# MISTAKE 5: using input() inside a script meant to run automatically. It will
#   hang forever at 3am waiting for a keypress nobody will make. Use sys.argv
#   or a config file for unattended jobs.

# MISTAKE 6: trusting input for security-sensitive work. Never pass user text
#   straight into a shell command, a file path or a database query. That's how
#   injection attacks happen. Lessons 13 and 22 show the safe patterns.
print()


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * input("question ") asks, waits, and returns the answer AS TEXT.
#   * Convert before doing maths:  int(text)  or  float(text).
#   * Bad text makes int() raise ValueError. try/except catches it.
#   * .strip() and .lower() user answers before comparing them.
#   * A `while True` loop with `break` keeps asking until the answer is good.
#   * Automated scripts take input from sys.argv instead of input().
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. A user types 7 into  n = input("Number? ").  What is n + n?
#   Q2. How do you make it give 14 instead?
#   Q3. What does int("3.5") do?
#   Q4. Someone answers " Yes ". Why doesn't  answer == "yes"  work?
#   Q5. Why shouldn't a 3am scheduled script use input()?
#
# ANSWERS
#   A1. "77" - both are text, so + joins them.
#   A2. n = int(input("Number? "))  then  n + n  is 14.
#   A3. ValueError - int() only accepts whole numbers. Use float("3.5").
#   A4. The spaces and the capital Y. Compare  answer.strip().lower() == "yes".
#   A5. Nobody is there to answer, so it waits forever. Use sys.argv instead.


# =============================================================================
# EXERCISES
# =============================================================================
#
# Use ask("prompt ", "example") while experimenting so the file still runs
# start-to-finish. Swap in real input() once you're running it by hand.
#
# WARM-UP A (easy) — Echo
#   Ask for a favourite colour and print:  Nice, <colour> is a great colour.
#
# WARM-UP B (easy) — Double it
#   Ask for a number, convert it with int(), and print double that number.
#
# WARM-UP C (easy) — Tidy it
#   Ask for a name, then print it stripped of spaces and in CAPITALS.
#
# EXERCISE 1 (easy) — Greeting
#   Ask for a first name and a last name. Print a greeting using an f-string,
#   with both names Title Cased and stripped of stray spaces.
#
# EXERCISE 2 (easy) — Age in days
#   Ask for an age in years. Print the approximate number of days lived
#   (years * 365), formatted with thousands separators.
#
# EXERCISE 3 (medium) — Safe divider
#   Ask for two numbers. Print the result of dividing the first by the second,
#   to 3 decimal places. Handle BOTH bad input (not a number) and division by
#   zero, printing a helpful message instead of crashing.
#   Hint: one try: block can have two except: parts - one for ValueError, one
#   for ZeroDivisionError.
#
# EXERCISE 4 (challenge) — Yes/no question
#   Ask "Continue? (y/n)". Accept "y", "Y", "yes", "YES", " Yes " as yes, and
#   the same variations of "n"/"no" as no. Anything else -> ask again (limit
#   yourself to 3 tries).
#   Hint: copy the shape of the loop in PART 4.
#
# EXERCISE 5 (medium) — Unit converter menu
#   Ask the user to pick 1 (km to miles), 2 (kg to pounds) or 3 (C to F), then
#   ask for the value and print the converted result to 2 decimal places.
#   1 km = 0.621371 miles, 1 kg = 2.20462 pounds, F = C * 9/5 + 32.
#   (Choosing between 1, 2 and 3 uses if/elif - lesson 05. Peek at it, or
#   read the solution and come back to this after lesson 05.)
#
# EXERCISE 6 (medium) — Command-line version
#   Rewrite Exercise 2 to take the age from sys.argv[1] instead of input(),
#   printing a usage message if no argument was given. Run it with:
#       python3 04_input_and_conversion.py 22

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   colour = ask("Favourite colour? ", "blue")
#   print(f"Nice, {colour} is a great colour.")
#
# WARM-UP B
#   number = int(ask("A number: ", "21"))
#   print(number * 2)                          # -> 42
#
# WARM-UP C
#   name = ask("Name: ", "  sidd ")
#   print(name.strip().upper())                # -> SIDD
#
# EXERCISE 1
#   first = ask("First name: ", "sidd").strip().title()
#   last = ask("Last name: ", "chirkute").strip().title()
#   print(f"Hello, {first} {last}!")
#
# EXERCISE 2
#   years = int(ask("Age in years: ", "22"))
#   print(f"That's about {years * 365:,} days.")
#
# EXERCISE 3
#   try:
#       a = float(ask("First number: ", "10"))
#       b = float(ask("Second number: ", "3"))
#       print(f"{a} / {b} = {a / b:.3f}")
#   except ValueError:
#       print("Those weren't both numbers.")
#   except ZeroDivisionError:
#       print("Can't divide by zero.")
#
# EXERCISE 4
#   attempts = 0
#   while True:
#       attempts += 1
#       reply = ask("Continue? (y/n) ", "y").strip().lower()
#       if reply == "y" or reply == "yes":
#           print("Continuing.")
#           break
#       if reply == "n" or reply == "no":
#           print("Stopping.")
#           break
#       print("Please answer y or n.")
#       if attempts >= 3:
#           print("No valid answer - assuming no.")
#           break
#   The same shape as PART 4: ask, check, break out when happy, and a
#   safety valve after 3 tries.
#
# EXERCISE 5
#   choice = ask("1=km->mi, 2=kg->lb, 3=C->F: ", "1").strip()
#   value = float(ask("Value: ", "42"))
#   if choice == "1":
#       print(f"{value} km = {value * 0.621371:.2f} miles")
#   elif choice == "2":
#       print(f"{value} kg = {value * 2.20462:.2f} pounds")
#   elif choice == "3":
#       print(f"{value} C = {value * 9 / 5 + 32:.2f} F")
#   else:
#       print("Unknown choice.")
#
# EXERCISE 6
#   if len(sys.argv) < 2:
#       print("Usage: python3 04_input_and_conversion.py <age>")
#   else:
#       years = int(sys.argv[1])
#       print(f"That's about {years * 365:,} days.")
#   len(sys.argv) < 2 means "only the script's name was given - no age".


print("=" * 70)
print("Lesson 04 complete. Next: 05_conditionals_and_logic.py")
print("=" * 70)

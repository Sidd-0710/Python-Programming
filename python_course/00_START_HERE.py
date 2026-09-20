"""
===============================================================================
 LESSON 00 — START HERE: HOW PROGRAMMING (AND THIS COURSE) WORKS
===============================================================================

WELCOME.

If you have never written a line of code before, this is the right file. By the
end of this session you will understand what a program actually IS, how to run
one, how to read an error message without panicking, and how to work through
the rest of this course.

Time for this session: about 45 minutes.


-------------------------------------------------------------------------------
 NEW WORDS - read this list once; come back whenever a word confuses you
-------------------------------------------------------------------------------

  program       a list of instructions for the computer, saved in a file
  code          the instructions themselves - the text you write
  Python        the language we write those instructions in
  run           tell the computer to follow the instructions in a file
  terminal      the panel (usually at the bottom of VS Code) where you type
                commands and where your program's output appears
  output        whatever your program shows in the terminal
  print()       the instruction that shows something in the terminal
  comment       a note for humans, starting with #. Python ignores it
  error         Python stopping to tell you it couldn't follow an instruction
  bug           a mistake in code that makes it do the wrong thing

Every lesson in this course starts with a list like this one.


-------------------------------------------------------------------------------
 WHAT IS A PROGRAM?
-------------------------------------------------------------------------------

A program is a list of instructions written down in a language a computer can
follow. That's the whole idea.

Think of a recipe. A recipe is a list of instructions a cook follows, in order,
from top to bottom:

    1. Boil water
    2. Add pasta
    3. Wait 10 minutes
    4. Drain

A Python program is exactly the same, except the "cook" is your computer, and
it is extremely fast, extremely obedient, and extremely literal. It will do
precisely what you wrote - including your mistakes. It never guesses what you
meant.

That last sentence is the single most important thing to understand about
programming. When your code does something strange, the computer is not broken
and it is not being difficult. It is following your instructions perfectly.
Your job is to find where the instructions said something other than what you
intended.


-------------------------------------------------------------------------------
 WHAT IS PYTHON?
-------------------------------------------------------------------------------

Python is one particular language for writing those instructions. It was
designed to be readable by humans, which is why it's the standard first
language today.

A file ending in `.py` is a Python file. It is a plain text file - nothing
magical. The file you are reading right now is one.

When you "run" a Python file, a program called the Python INTERPRETER reads
your file from top to bottom, one line at a time, and does what each line says.


-------------------------------------------------------------------------------
 HOW TO RUN THIS FILE
-------------------------------------------------------------------------------

Three ways. Pick whichever is easiest for you:

 1. In VS Code: click the ▷ (play) button in the top-right corner of the editor.

 2. In VS Code's terminal (View menu -> Terminal), type:

        python3 00_START_HERE.py

    and press Enter.

 3. Right-click the file in VS Code's file list -> "Run Python File in Terminal".

Do it now. Run this file. Text will appear in the terminal panel at the bottom
of your screen. That text is coming from the code further down in this file.


-------------------------------------------------------------------------------
 HOW TO USE THIS COURSE
-------------------------------------------------------------------------------

Each numbered file is one learning session (45-90 minutes). For every file:

 STEP 1 - READ the file top to bottom, like a textbook chapter. Don't skip the
          long comment blocks; that's where the actual teaching is.

 STEP 2 - RUN the file. Watch the output appear. Match each piece of output to
          the line of code that produced it.

 STEP 3 - BREAK it. This is the step everybody skips and it is the most
          valuable one. Change a number. Delete a quote mark. Misspell a word.
          Run it again and read the error. You cannot damage anything. You
          learn what a rule IS by watching what happens when you violate it.

 STEP 4 - DO THE EXERCISES at the bottom of the file. Write the code yourself,
          with your own fingers. Reading code and writing code are different
          skills, the way reading music and playing an instrument are different
          skills. Every lesson starts with easy WARM-UPS - do those first.

 STEP 5 - Only after genuinely attempting an exercise, scroll to the SOLUTIONS
          section at the very bottom and compare. If your solution works but
          looks different from mine, that's fine - there are many correct
          answers.

Inside each lesson you'll also see:

  TRY IT NOW       a 1-2 minute task, right after the idea it practises.
                   Do it before you read on - it's where things "click".
  GOOD PLACE FOR A BREAK
                   the halfway point of a longer lesson. Take one.
  RECAP            a short summary, plus quick questions to test yourself.

A NOTE ON YOUR EXISTING FILES: you already wrote `FirstCode.py`, `var.py` and
`Mul_Ass.py`. You had a habit of commenting out the code after finishing it.
Don't do that here. Leave code runnable so you can come back, re-run it, and
tinker with it months from now when you've forgotten the details.


-------------------------------------------------------------------------------
 WHERE THIS IS GOING
-------------------------------------------------------------------------------

You said you want four things. Here is where each one appears in this course,
so you can see that the boring early stuff is not busywork:

  GOAL                         YOU'LL REACH IT IN
  ---------------------------  -------------------------------------------
  Understand fundamentals      Lessons 01-12 (the whole foundation)
  Automate repetitive tasks    Lessons 13-14, 18, and the project in 20
  Analyse and chart data       Lessons 06, 09, 14, 19
  Build web apps / backends    Lessons 16-17, 21-22

Every early concept is a tool you will pick up again later. Lists (lesson 06)
become rows of data. Dictionaries (lesson 09) become the JSON that web APIs
speak. Loops (lesson 07) become the thing that renames 400 files for you while
you drink coffee. Nothing here is filler.


-------------------------------------------------------------------------------
 TWO THINGS YOU NEED BEFORE ANY CODE: COMMENTS AND print()
-------------------------------------------------------------------------------

COMMENTS
Any line starting with a `#` is ignored completely by Python. It's a note for
humans. The giant block you have been reading is a different flavour of the
same idea: text wrapped in triple quotes (\"\"\" ... \"\"\") that isn't assigned to
anything is effectively a note too.

print()
`print(...)` displays something in the terminal. It is how your program talks
to you. For your first months of programming, `print()` is also your main
debugging tool: when you're confused about what a piece of code is doing, print
the values and look at them.

Now stop reading and look at the code below - then run the file.
"""

# =============================================================================
# PART 1 — YOUR FIRST INSTRUCTIONS
# =============================================================================

# This is a comment. Python skips it entirely.
# The line below is an instruction. Python runs it.
print("Hello. This text was produced by line 183 of 00_START_HERE.py.")

# print() can be called as many times as you like. Each call starts a new line
# in the terminal. Python runs them strictly in the order they appear.
print("Instruction 1 runs first.")
print("Instruction 2 runs second.")
print("Instruction 3 runs third.")

# An empty print() just prints a blank line. Useful for spacing out output so
# it's readable.
print()

# TRY IT NOW (1 minute):
#   Change the text inside the quotes of "Instruction 1 runs first." to any
#   sentence you like. Run the file. Find your sentence in the output.
#   Only the text INSIDE the quotes changes what's printed.


# =============================================================================
# PART 2 — ORDER MATTERS (THE RECIPE RULE)
# =============================================================================

# Python reads top to bottom. Always. There is no cleverness here.
# If you swapped the two lines below, the output would swap too.
print("Step 1: Boil the water.")
print("Step 2: Add the pasta.")
print()


# =============================================================================
# PART 3 — print() CAN SHOW MORE THAN ONE THING
# =============================================================================

# Separate items with commas. Python prints them in order with a space between.
print("Your name is", "Sidd", "and you are learning Python.")

# The things you print don't have to be text. Numbers work too.
print("2 plus 2 is", 2 + 2)

# Notice something important above: "2 plus 2 is" is in quotes, so Python
# treats it as literal text and prints it exactly. But 2 + 2 has no quotes, so
# Python treats it as arithmetic to actually perform. Quotes are the difference
# between "say this" and "work this out".
print("2 + 2")        # no arithmetic happens - it's just text
print(2 + 2)          # arithmetic happens - the answer is printed
print()

# TRY IT NOW (1 minute):
#   Add these two lines below this comment, and PREDICT what each prints
#   before you run the file:
#       print("10 * 5")
#       print(10 * 5)
#   (Answer: the first prints the text 10 * 5, the second prints 50.
#    In Python, * means multiply.)


# =============================================================================
# PART 4 — HOW TO READ AN ERROR MESSAGE
# =============================================================================

# You will see errors constantly. Professional developers see errors constantly.
# An error is not a failure or a telling-off; it is Python telling you, in
# detail, exactly where it got confused. It is the most useful output you get.
#
# Here is a typical error, and how to read it:
#
#     Traceback (most recent call last):
#       File "/Users/sidd/Python/python_course/00_START_HERE.py", line 12
#         print("hello"
#               ^
#     SyntaxError: '(' was never closed
#
# Read it BOTTOM TO TOP:
#
#   * LAST LINE first: `SyntaxError: '(' was never closed`
#     This is WHAT went wrong, in plain-ish English. Here: a bracket was opened
#     and never closed.
#
#   * Then the `line 12` part: WHERE it went wrong. Go to that line in VS Code.
#     (Careful: the real mistake is sometimes on the line just ABOVE the one
#     reported, especially with unclosed brackets and quotes.)
#
#   * The `^` character points at the exact spot Python got stuck.
#
# The three errors you will meet in your first week:
#
#   SyntaxError  — you broke a grammar rule. A missing quote, bracket or colon.
#                  Python couldn't even start running your file.
#   NameError    — you used a name Python has never heard of. Usually a typo,
#                  or you used something before creating it.
#   TypeError    — you tried to do something to a value that its type doesn't
#                  allow, like adding a number to a word.
#
# TRY THIS NOW (seriously, do it):
#   1. Remove the final `)` from the print line below.
#   2. Save and run the file.
#   3. Read the error.
#   4. Put the `)` back.
# You have just learned more about syntax errors than reading about them can
# teach you.
print("Errors are information, not judgement.")
print()


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. The next part is only a preview - relax while you
#  read it. You are NOT expected to understand it yet.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 5 — A TINY TASTE OF WHERE YOU'RE HEADED
# =============================================================================

# You won't understand every line here yet, and you are NOT supposed to. This
# is a preview - a photo of the destination before the hike. Come back and read
# it again after lesson 09 and it will be completely obvious.
#
# The plain-English notes on the right say what each line does. Just read
# those for now.

monthly_sales = [1200, 1450, 1100, 1800, 2100, 1950]   # six numbers, kept together
                                                        # under one name (a "list")

total = sum(monthly_sales)                     # add every number in the list
average = total / len(monthly_sales)           # divide by how many there are
best_month = max(monthly_sales)                # the biggest number

print("Six months of sales:", monthly_sales)
print("Total:", total)
print("Average per month:", average)
print("Best month:", best_month)

# And a bar chart, drawn with nothing but text.
# In plain English: "for each month, starting the count at 1, draw one # for
# every 100 of sales, and print the month number, the bar and the amount."
for month_number, amount in enumerate(monthly_sales, start=1):
    bar = "#" * (amount // 100)                # one '#' per 100 of sales
    print("Month", month_number, bar, amount)

print()
print("That was 10 lines of code doing real work. You'll write it yourself soon.")
print()


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * A program is a list of instructions. Python runs them top to bottom,
#     exactly as written - including your mistakes.
#   * print(...) shows something in the terminal. print() alone prints a blank
#     line.
#   * Text in quotes is printed exactly. Maths without quotes is worked out.
#   * Lines starting with # are comments - notes for humans.
#   * Read errors BOTTOM TO TOP: the last line says WHAT went wrong, the
#     "line N" part says WHERE.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. What does  print("3 + 4")  show? And  print(3 + 4)?
#   Q2. You swap two print lines. What happens to the output?
#   Q3. An error message ends with  NameError: name 'helo' is not defined.
#       What probably went wrong?
#   Q4. Does Python run a line that starts with #?
#
# ANSWERS
#   A1. The text  3 + 4  and then the number  7.
#   A2. The two outputs swap too. Python always goes top to bottom.
#   A3. A typo (helo instead of hello), or text that was meant to be in quotes.
#   A4. No. It's a comment.


# =============================================================================
# EXERCISES — do these before moving to lesson 01
# =============================================================================
#
# WARM-UP A (easy) — Hello, you
#   Write ONE print() line that prints:  Hello, my name is <your name>
#
# WARM-UP B (easy) — Spacing
#   Print two sentences with a BLANK line between them. (Hint: print() on
#   its own prints a blank line.)
#
# EXERCISE 1 (easy)
#   Below this comment block, write three print() lines that introduce
#   yourself: your name, what you want to build with Python, and how many
#   hours a week you plan to study.
#
# EXERCISE 2 (easy)
#   Make Python calculate something for you. Print the result of 15 * 24
#   WITHOUT working it out yourself first. Then print the text "15 * 24" as
#   literal text. Make sure you understand why the two lines differ.
#
# EXERCISE 3 (medium - and the important one)
#   Deliberately cause each of these three errors, one at a time. Run the file
#   after each, read the message, then fix it:
#     a) Delete a closing quote mark from any print line.   -> SyntaxError
#     b) Write:  print(hello)   with no quotes.             -> NameError
#     c) Write:  print("age: " + 22)                        -> TypeError
#   Write down, in a comment, what each error message said. You are training
#   yourself to read errors calmly.
#
# EXERCISE 4 (easy)
#   Change the `monthly_sales` numbers in PART 5 and re-run the file. Watch the
#   total, average and bar chart all update by themselves. That is the point of
#   programming: describe the process once, then change the inputs freely.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS  (try the exercises first - genuinely)
# =============================================================================
#
# WARM-UP A
#   print("Hello, my name is Sidd")
#
# WARM-UP B
#   print("I am learning Python.")
#   print()
#   print("It is going well.")
#
# EXERCISE 1
#   print("My name is Sidd.")
#   print("I want to build web backends and automate boring tasks.")
#   print("I plan to study 12 hours a week.")
#
# EXERCISE 2
#   print(15 * 24)     # -> 360   (Python does the arithmetic)
#   print("15 * 24")   # -> 15 * 24   (quotes mean 'this is just text')
#
# EXERCISE 3
#   a) SyntaxError: unterminated string literal
#      Python needs a matching pair of quotes to know where text ends.
#   b) NameError: name 'hello' is not defined
#      Without quotes, Python thinks `hello` is a variable name and goes
#      looking for it. There isn't one.
#   c) TypeError: can only concatenate str (not "int") to str
#      `+` means "join" for text and "add" for numbers. Python refuses to guess
#      which you meant when you mix them. Lesson 01 shows the fix.
#
# EXERCISE 4
#   No solution needed - just observe that the code adapted automatically.


print("=" * 70)
print("Lesson 00 complete. Next: 01_variables_and_data_types.py")
print("=" * 70)

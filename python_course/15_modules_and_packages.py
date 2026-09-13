"""
===============================================================================
 LESSON 15 — MODULES AND PACKAGES: ORGANISING REAL PROJECTS
===============================================================================

Time: about 55 minutes.
Assumes: lessons 01-14.


-------------------------------------------------------------------------------
 THEORY: WHEN ONE FILE ISN'T ENOUGH
-------------------------------------------------------------------------------

Everything you've written so far has lived in a single file. That's fine up to
a few hundred lines. Beyond that:

  * finding anything requires scrolling for ages
  * you can't reuse one useful function without copying it (and then you have
    two copies that slowly drift apart)
  * two people can't work on it at once
  * there's no way to say "this part is the public interface, that part is
    internal plumbing"

The answer is to split code across files and import between them.

  MODULE   Any .py file. `text_tools.py` is a module named `text_tools`.
  PACKAGE  A folder of modules containing an `__init__.py` file.
  LIBRARY  An informal word for a package someone else published.

You've already been importing all course long - `import math`, `import json`,
`from pathlib import Path`. This lesson shows what's actually happening, and
how to write your own.
"""

LINE = "-" * 70


# =============================================================================
# PART 1 — THE FOUR IMPORT FORMS
# =============================================================================
print(LINE)
print("PART 1 — IMPORT SYNTAX")
print(LINE)

# FORM 1 - import the whole module. Access things with a dot.
import math
print("  import math          ->", math.sqrt(16))

# FORM 2 - import specific names directly into your file.
from math import sqrt, pi
print("  from math import ... ->", sqrt(25), round(pi, 4))

# FORM 3 - import with an alias. Standard for long or conventional names.
import statistics as stats
print("  import ... as        ->", stats.mean([1, 2, 3, 4]))

# FORM 4 - import everything. AVOID THIS.
#     from math import *
# It dumps every name into your file, so you can no longer tell where anything
# came from, and it silently overwrites your own variables. The one exception
# is a deliberate re-export inside a package's __init__.py.

print()

# WHICH TO USE:
#   `import module` when you'll use several things from it, or when the module
#     name adds clarity at the call site (json.dumps is clearer than dumps)
#   `from module import name` when you use one or two things constantly
#     (Path, datetime) and the name is unambiguous
#   `as` when the name is long, or when there's a community convention
#     (`import pandas as pd`)

# WHERE IMPORTS GO: all at the TOP of the file, in three groups separated by
# blank lines - standard library first, then third-party packages, then your
# own modules. That's the PEP 8 convention and every Python codebase follows it.


# =============================================================================
# PART 2 — IMPORTING YOUR OWN CODE
# =============================================================================
print(LINE)
print("PART 2 — YOUR OWN MODULES")
print(LINE)

# Next to this lesson file there's a folder called `toolkit/`:
#
#     toolkit/
#         __init__.py       <- makes the folder a PACKAGE
#         text_tools.py     <- a module
#         money.py          <- a module
#
# Open those files after this lesson - they're short and commented.

# Import a module from inside the package:
from toolkit import text_tools, money

print("  text_tools.slugify:", text_tools.slugify("  Hello World! 2024  "))
print("  text_tools.initials:", text_tools.initials("Ana Maria Silva"))
print("  money.add_tax(100):", money.add_tax(100))
print()

# Import specific functions from a module inside the package:
from toolkit.text_tools import truncate
from toolkit.money import format_money, split_bill

long_title = "An Extremely Long Blog Post Title That Will Not Fit In The Sidebar"
print("  truncate:", truncate(long_title, 40))
print("  format_money:", format_money(1234.5))

per_person, grand = split_bill(187.40, 5, tip_rate=0.125)
print(f"  split_bill: {format_money(grand)} total, "
      f"{format_money(per_person)} each")
print()

# Because toolkit/__init__.py re-exports the popular names, this shorter form
# also works:
from toolkit import slugify
print("  shortcut import:", slugify("Python Is Fun"))

# Modules carry metadata too:
import toolkit
print("  toolkit.__version__:", toolkit.__version__)
print("  toolkit.__all__    :", toolkit.__all__)
print()

# A NOTE ON THIS COURSE'S FILENAMES: you cannot write `import 01_variables`,
# because a module name can't start with a digit - it isn't a valid Python
# identifier. That's why the numbered lesson files are meant to be RUN, while
# reusable code lives in properly named modules like `toolkit`.


# =============================================================================
# PART 3 — HOW PYTHON FINDS MODULES
# =============================================================================
print(LINE)
print("PART 3 — THE IMPORT SEARCH PATH")
print(LINE)

import sys

# When you write `import something`, Python searches, in order:
#   1. built-in modules compiled into the interpreter
#   2. every folder listed in sys.path
# sys.path starts with the folder containing the script you ran, which is why
# `from toolkit import ...` worked above with no configuration at all.

print("  Python looks in these places (first 4):")
for entry in sys.path[:4]:
    print(f"    {entry or '(the current folder)'}")
print(f"    ... and {len(sys.path) - 4} more")
print()

# Modules are cached after first import - importing twice does NOT run the file
# twice:
print("  already-loaded modules include:",
      [name for name in ("math", "json", "toolkit") if name in sys.modules])
print()

# ModuleNotFoundError is the error you'll hit. Its causes, in order of
# likelihood:
#   1. a typo in the name
#   2. the package isn't installed (`pip install requests`)
#   3. you're running from a different folder than you think
#   4. your own file is named the same as a standard library module - a file
#      called `json.py` in your folder will shadow the real json module and
#      cause deeply confusing errors. Never name a file after a stdlib module.

try:
    import nonexistent_module_xyz
except ModuleNotFoundError as error:
    print("  example failure:", error)
print()


# =============================================================================
# PART 4 — if __name__ == "__main__"
# =============================================================================
print(LINE)
print("PART 4 — THE __main__ GUARD")
print(LINE)

# You've seen this line in the toolkit modules and probably in code online:
#
#     if __name__ == "__main__":
#         main()
#
# WHAT IT DOES: `__name__` is a variable Python sets automatically in every
# module. Its value depends on HOW the file was started:
#
#   * Run directly (python3 myfile.py)  -> __name__ == "__main__"
#   * Imported by another file          -> __name__ == "myfile"
#
# So the guard means: "only do this when I'm the program being run, not when
# I'm being imported as a library".

print(f"  In THIS file, __name__ is {__name__!r}")
print(f"  In the imported module, __name__ is {text_tools.__name__!r}")
print()

# WHY IT MATTERS: without the guard, ALL top-level code in a module runs the
# moment it's imported. Import a file that prints a report and starts a server,
# and you get a report and a server - just from an import. The guard lets one
# file be both a reusable library AND a runnable script.

# Try it yourself:
#     python3 toolkit/text_tools.py        <- runs its self-test
#     (importing it above)                 <- ran nothing
print("  try: python3 toolkit/text_tools.py")
print()


# =============================================================================
# PART 5 — THE STANDARD LIBRARY AND THIRD-PARTY PACKAGES
# =============================================================================
print(LINE)
print("PART 5 — BATTERIES INCLUDED")
print(LINE)

# Python ships with ~200 modules, free and always available. This is called the
# "batteries included" philosophy, and it's a big part of why Python is so
# productive. Lesson 18 tours the most useful ones. A taste:

modules_tour = [
    ("math",        "sqrt, ceil, pi"),
    ("random",      "randint, choice, shuffle"),
    ("datetime",    "dates, times, durations"),
    ("pathlib",     "file paths"),
    ("json / csv",  "data formats"),
    ("re",          "regular expressions - pattern matching in text"),
    ("collections", "Counter, defaultdict, deque"),
    ("itertools",   "clever looping tools"),
    ("statistics",  "mean, median, stdev"),
    ("sqlite3",     "a complete SQL database, built in"),
    ("urllib",      "fetch things over HTTP"),
    ("argparse",    "professional command-line interfaces"),
    ("unittest",    "automated tests"),
]
for name, purpose in modules_tour:
    print(f"    {name:<14} {purpose}")
print()

# THIRD-PARTY PACKAGES come from PyPI (the Python Package Index) and are
# installed with pip:
#
#     python3 -m pip install requests
#
# The ones that matter for your stated goals:
#
#   WEB / BACKEND     flask or fastapi  - build web apps and APIs
#                     requests          - call other people's APIs
#                     sqlalchemy        - talk to databases
#
#   DATA ANALYSIS     pandas            - spreadsheets in code; the big one
#                     matplotlib        - charts
#                     numpy             - fast numeric arrays
#
#   AUTOMATION        openpyxl          - read/write real Excel files
#                     beautifulsoup4    - parse HTML from websites
#                     schedule          - run jobs at intervals
#
# ***** VIRTUAL ENVIRONMENTS *****
# Installing packages globally eventually breaks things: project A needs
# version 1 of a library, project B needs version 2. A virtual environment is a
# private package folder per project:
#
#     python3 -m venv .venv           # create it (once per project)
#     source .venv/bin/activate       # switch to it (Mac/Linux)
#     pip install requests            # installs INTO this project only
#     pip freeze > requirements.txt   # record exactly what's installed
#     deactivate                      # leave it
#
# On Windows the activate line is:  .venv\Scripts\activate
#
# Rule: one virtual environment per project, always. It costs 10 seconds and
# saves entire afternoons.
print()


# =============================================================================
# PART 6 — STRUCTURING A REAL PROJECT
# =============================================================================
print(LINE)
print("PART 6 — PROJECT LAYOUT")
print(LINE)

layout = """
    my_project/
        .venv/                  virtual environment (never commit this)
        README.md               what it is and how to run it
        requirements.txt        the packages it needs
        main.py                 the entry point you actually run
        config.json             settings, kept out of the code
        my_project/             the package with the real logic
            __init__.py
            models.py           data structures
            services.py         business logic
            utils.py            small shared helpers
        tests/
            test_services.py
        data/                   input files
        output/                 generated files (usually not committed)
"""
print(layout)

print("The principles behind that shape:")
print("  1. One responsibility per module - if you can't name it in two words,")
print("     it's doing too much.")
print("  2. main.py only wires things together; the logic lives in the package.")
print("  3. Settings live in a config file, not scattered through the code.")
print("  4. Anything generated goes in its own folder, separate from source.")
print("  5. Imports flow one way. If A imports B and B imports A, you get a")
print("     circular import error - and it's a sign the split is wrong.")
print()


# =============================================================================
# PART 7 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 7 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: naming your file after a standard library module. A `random.py` in
#   your folder shadows the real one, and `random.randint` mysteriously fails.

# MISTAKE 2: `from module import *`. Untraceable names, silent collisions.

# MISTAKE 3: circular imports. If a.py imports b.py and b.py imports a.py,
#   Python raises ImportError. Fix the design: extract the shared part into a
#   third module that both import.

# MISTAKE 4: top-level side effects in a module. Anything not inside a function
#   or the __main__ guard runs on import. Keep module level to definitions and
#   constants only.

# MISTAKE 5: forgetting __init__.py. Modern Python can sometimes cope without
#   it, but include it - it's where you define the package's public face.

# MISTAKE 6: installing everything globally instead of using a venv.

# MISTAKE 7: imports scattered through the file instead of at the top. Import
#   cost is paid once, so there's no performance reason to delay them, and it
#   hides your dependencies.

# MISTAKE 8: a "utils.py" that becomes a junk drawer of 60 unrelated functions.
#   When it grows past a screen, split it by topic.
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# EXERCISE 1 — Read the source
#   Open toolkit/text_tools.py and toolkit/money.py. Read every line. Then run
#   each one directly (python3 toolkit/money.py) and observe the __main__ guard
#   in action.
#
# EXERCISE 2 — Add a function
#   Add `word_count(text)` to toolkit/text_tools.py, returning a dict of word
#   -> count. Export it from __init__.py, then import and use it here.
#
# EXERCISE 3 — Build your own module
#   Create validators.py next to this file with: is_valid_email(text),
#   is_valid_phone(text), is_strong_password(text). Each returns a
#   (bool, reason) tuple. Give it a __main__ block that self-tests all three.
#   Import it here and run it over a list of test values.
#
# EXERCISE 4 — Make it a package
#   Turn validators.py into a package: a folder `validators/` with
#   __init__.py, email.py and password.py. Keep the same import interface
#   working from the caller's point of view.
#
# EXERCISE 5 — Explore the standard library
#   Pick three modules from PART 5's list that you haven't used. Read their
#   docs (python3 -m pydoc statistics, or docs.python.org), and write one
#   working example of each.
#
# EXERCISE 6 — Set up a virtual environment
#   In a NEW folder outside this course, create a venv, activate it, install
#   the `requests` package, write a two-line script that imports it, and
#   produce a requirements.txt. This is the standard start of every real
#   Python project - do it once by hand and it'll stick.
#
# EXERCISE 7 — Cause and fix a circular import
#   Create a.py that imports b.py, and b.py that imports a.py. Run it and read
#   the error. Then fix it by moving the shared piece into c.py.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 2
#   # in toolkit/text_tools.py
#   def word_count(text):
#       counts = {}
#       for word in text.lower().split():
#           word = word.strip(".,!?;:\"'")
#           if word:
#               counts[word] = counts.get(word, 0) + 1
#       return counts
#   # in toolkit/__init__.py add word_count to the import line and __all__
#
# EXERCISE 3
#   # validators.py
#   def is_valid_email(text):
#       text = text.strip()
#       if "@" not in text:
#           return False, "missing @"
#       local, _, domain = text.partition("@")
#       if not local:
#           return False, "nothing before the @"
#       if "." not in domain:
#           return False, "domain has no dot"
#       return True, "ok"
#
#   def is_valid_phone(text):
#       digits = [c for c in text if c.isdigit()]
#       if len(digits) < 10:
#           return False, f"only {len(digits)} digits"
#       return True, "ok"
#
#   def is_strong_password(text):
#       if len(text) < 8:
#           return False, "too short"
#       if not any(c.isdigit() for c in text):
#           return False, "needs a digit"
#       if not any(c.isalpha() for c in text):
#           return False, "needs a letter"
#       return True, "ok"
#
#   if __name__ == "__main__":
#       print(is_valid_email("sidd@example.com"))
#       print(is_valid_phone("+44 7700 900123"))
#       print(is_strong_password("hunter2024"))
#
# EXERCISE 4
#   validators/__init__.py:
#       from validators.email import is_valid_email
#       from validators.password import is_strong_password
#       __all__ = ["is_valid_email", "is_strong_password"]
#   Callers still write `from validators import is_valid_email` - the
#   reorganisation is invisible to them. That's the point of __init__.py.
#
# EXERCISE 7
#   The error is ImportError: cannot import name 'x' from partially
#   initialized module (most likely due to a circular import).
#   Fix: whatever both files need goes into c.py, and both import c.


print("=" * 70)
print("Lesson 15 complete. Next: 16_classes_and_objects.py")
print("=" * 70)

"""
===============================================================================
 LESSON 18 — THE STANDARD LIBRARY TOOLKIT
===============================================================================

Time: about 75 minutes.
Assumes: lessons 01-17.


-------------------------------------------------------------------------------
 THEORY: DON'T WRITE WHAT'S ALREADY WRITTEN
-------------------------------------------------------------------------------

Python ships with roughly 200 modules, already installed, already tested by
millions of people. This is the "batteries included" philosophy.

The single biggest productivity gap between a beginner and an experienced
developer is not typing speed or cleverness. It is KNOWING WHAT ALREADY EXISTS.
A beginner writes forty lines to count items; an experienced developer types
`Counter(items)` and moves on.

This lesson is a guided tour of the modules you'll genuinely reach for. You are
not expected to memorise it - you're expected to remember that it EXISTS, so
that next time you think "surely someone has solved this", you come back here.
"""

import collections
import datetime
import itertools
import os
import platform
import random
import re
import secrets
import statistics
import sys
import textwrap
import time
import uuid
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

LINE = "-" * 70


# =============================================================================
# PART 1 — datetime: DATES AND TIMES
# =============================================================================
print(LINE)
print("PART 1 — datetime")
print(LINE)

from datetime import date, timedelta

today = date.today()
now = datetime.datetime.now()

print("  today            :", today)
print("  now              :", now.strftime("%Y-%m-%d %H:%M:%S"))
print("  year / month / day:", today.year, today.month, today.day)
print("  weekday name     :", today.strftime("%A"))
print()

# ARITHMETIC with timedelta - the reason datetime is worth learning.
print("  in 30 days       :", today + timedelta(days=30))
print("  90 days ago      :", today - timedelta(days=90))

launch = date(2024, 1, 15)
elapsed = today - launch                 # subtracting dates gives a timedelta
print(f"  days since launch: {elapsed.days:,}")
print(f"  that's {elapsed.days / 365.25:.1f} years")
print()

# FORMATTING with strftime (string FROM time) - the codes worth knowing:
#   %Y 2026   %m 09   %d 13   %H 14   %M 30   %S 00
#   %B September   %b Sep   %A Sunday   %a Sun
print("  ISO format       :", today.isoformat())
print("  human readable   :", today.strftime("%d %B %Y"))
print("  for a filename   :", now.strftime("backup_%Y%m%d_%H%M%S.zip"))
print()

# PARSING with strptime (string PARSE time) - text into a real date:
parsed = datetime.datetime.strptime("2024-03-15", "%Y-%m-%d").date()
print("  parsed from text :", parsed, type(parsed).__name__)

# Once parsed, dates sort and compare correctly - which text dates do NOT do
# reliably unless they're in YYYY-MM-DD form:
dates = ["2024-03-15", "2023-12-01", "2024-01-20"]
real_dates = [datetime.datetime.strptime(d, "%Y-%m-%d").date() for d in dates]
print("  sorted properly  :", [str(d) for d in sorted(real_dates)])
print()

# TIMING code - how long did that take?
start = time.perf_counter()
sum(range(1_000_000))
print(f"  timed a loop     : {time.perf_counter() - start:.4f} seconds")
print()


# =============================================================================
# PART 2 — collections: BETTER CONTAINERS
# =============================================================================
print(LINE)
print("PART 2 — collections")
print(LINE)

from collections import Counter, defaultdict, deque, namedtuple

# --- Counter: counting, solved ---
words = "the cat sat on the mat the cat slept".split()
counts = Counter(words)
print("  Counter          :", counts)
print("  most_common(2)   :", counts.most_common(2))
print("  count of 'the'   :", counts["the"])
print("  unseen word      :", counts["zebra"], "(no KeyError - returns 0)")
print("  total items      :", counts.total())

# Counters support arithmetic, which is remarkably handy:
print("  subtract         :", Counter("aabbcc") - Counter("abc"))
print()

# --- defaultdict: no more "if key not in dict" ---
by_letter = defaultdict(list)            # missing keys auto-create a list
for word in words:
    by_letter[word[0]].append(word)
print("  defaultdict(list):", dict(by_letter))

tally = defaultdict(int)                 # missing keys auto-create 0
for word in words:
    tally[word] += 1                     # no .get() needed
print("  defaultdict(int) :", dict(tally))
print()

# --- deque: a fast queue, efficient at BOTH ends ---
# A list is slow to pop from the front (everything shifts). deque is not.
queue = deque(["job1", "job2", "job3"])
queue.append("job4")                     # add to the right
queue.appendleft("job0")                 # add to the left
print("  deque            :", list(queue))
print("  popleft()        :", queue.popleft(), "->", list(queue))

# maxlen gives you a rolling window for free - perfect for "the last N events":
recent = deque(maxlen=3)
for n in range(1, 7):
    recent.append(n)
print("  last 3 of 1-6    :", list(recent))
print()

# --- namedtuple: a tuple with named fields ---
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print("  namedtuple       :", p, "-> x =", p.x, ", y =", p.y)
print("  still a tuple    :", p[0], tuple(p))
# Use it when you want a lightweight record but a full class is overkill.
print()


# =============================================================================
# PART 3 — re: REGULAR EXPRESSIONS
# =============================================================================
print(LINE)
print("PART 3 — re (pattern matching in text)")
print(LINE)

# A regular expression is a mini-language for describing text patterns. It's
# dense and takes practice, but nothing else finds "every email in this
# document" so concisely.
#
# THE ESSENTIALS:
#   \d  a digit        \w  a letter/digit/underscore    \s  whitespace
#   .   any character  +   one or more    *   zero or more    ?   optional
#   ^   start          $   end            []  any one of these
#   ()  a capture group - the part you want to extract

text = """
Contact ana@example.com or sidd.c@company.co.uk for details.
Order 1001 shipped 2024-03-15, order 1002 shipped 2024-03-18.
Call 555-0101 or 555-0199.
"""

emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
print("  emails  :", emails)

dates_found = re.findall(r"\d{4}-\d{2}-\d{2}", text)
print("  dates   :", dates_found)

orders = re.findall(r"order (\d+)", text)     # the () captures just the number
print("  order ids:", orders)

phones = re.findall(r"\d{3}-\d{4}", text)
print("  phones  :", phones)
print()

# search() finds the first match; groups() pulls out the captured parts:
log_line = "2024-05-01 08:19:10 ERROR Payment gateway timeout"
match = re.search(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (\w+) (.*)", log_line)
if match:
    log_date, log_time, level, message = match.groups()
    print(f"  parsed log: date={log_date} time={log_time} level={level}")
    print(f"              message={message!r}")
print()

# sub() replaces - useful for redacting or cleaning:
print("  redacted:", re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[EMAIL]", text.strip().splitlines()[0]))
print("  cleaned :", re.sub(r"\s+", " ", "  too    much   space  ").strip())
print()

# ADVICE: use `re` when the pattern is genuinely irregular. For simple cases,
# .split(), .startswith() and `in` are clearer and faster. And always use raw
# strings (r"...") so backslashes survive.


# =============================================================================
# PART 4 — itertools: SMARTER LOOPING
# =============================================================================
print(LINE)
print("PART 4 — itertools")
print(LINE)

from itertools import chain, combinations, groupby, islice, product

print("  chain (join iterables) :", list(chain([1, 2], [3, 4], [5])))
print("  product (every combo)  :", list(product("AB", [1, 2])))
print("  combinations of 2      :", list(combinations(["a", "b", "c"], 2)))
print("  islice (a slice of any iterable):", list(islice(range(100), 5)))

# accumulate gives running totals - handy for cumulative charts:
from itertools import accumulate
print("  running totals         :", list(accumulate([10, 20, 30, 40])))

# groupby groups CONSECUTIVE equal items, so sort first:
records = [("EU", 100), ("AS", 50), ("EU", 200), ("US", 75), ("AS", 25)]
for region, group in groupby(sorted(records), key=lambda r: r[0]):
    amounts = [amount for _, amount in group]
    print(f"  groupby {region}: {amounts} = {sum(amounts)}")
print()


# =============================================================================
# PART 5 — statistics AND decimal
# =============================================================================
print(LINE)
print("PART 5 — statistics AND decimal")
print(LINE)

data = [23, 45, 12, 67, 34, 89, 21, 45, 33]
print("  mean    :", round(statistics.mean(data), 2))
print("  median  :", statistics.median(data))
print("  mode    :", statistics.mode(data))
print("  stdev   :", round(statistics.stdev(data), 2))
print("  quantiles:", [round(q, 1) for q in statistics.quantiles(data)])
print()

# decimal - exact arithmetic for money, fixing lesson 03's float problem:
print("  float   : 0.1 + 0.2 =", 0.1 + 0.2)
print("  Decimal : 0.1 + 0.2 =", Decimal("0.1") + Decimal("0.2"))

price = Decimal("19.99")
quantity = 3
total_cost = price * quantity
print(f"  exact total: {total_cost}")
print(f"  rounded    : {total_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}")

# ALWAYS build Decimals from STRINGS. Decimal(0.1) inherits the float's error;
# Decimal("0.1") is exact.
print("  from float :", Decimal(0.1))
print("  from string:", Decimal("0.1"))
print()


# =============================================================================
# PART 6 — os, sys, platform: TALKING TO THE SYSTEM
# =============================================================================
print(LINE)
print("PART 6 — SYSTEM INFORMATION")
print(LINE)

print("  python version :", sys.version.split()[0])
print("  platform       :", platform.system(), platform.release())
print("  cpu count      :", os.cpu_count())
print("  current folder :", Path.cwd().name)
print("  script name    :", Path(sys.argv[0]).name)
print("  home directory :", Path.home())

# Environment variables - the standard way to supply secrets and config to a
# program without putting them in the code:
print("  $HOME          :", os.environ.get("HOME", "(not set)"))
print("  $API_KEY       :", os.environ.get("API_KEY", "(not set - good)"))

# NEVER hard-code passwords or API keys in source. Read them from the
# environment, and keep them out of version control.
print()


# =============================================================================
# PART 7 — secrets, uuid, textwrap: SMALL BUT USEFUL
# =============================================================================
print(LINE)
print("PART 7 — ODDS AND ENDS")
print(LINE)

# secrets - cryptographically secure randomness. Use this, NOT `random`, for
# anything security-related: tokens, passwords, session ids.
print("  secure token   :", secrets.token_hex(16))
print("  secure choice  :", secrets.choice(["a", "b", "c"]))

alphabet = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
print("  random password:", "".join(secrets.choice(alphabet) for _ in range(16)))
print()

# uuid - globally unique identifiers, for database rows and file names.
print("  uuid4          :", uuid.uuid4())
print()

# textwrap - tidy paragraph formatting for terminal output and emails.
paragraph = ("Python ships with roughly two hundred modules, already installed "
             "and already tested by millions of people, which is why knowing "
             "what exists matters more than knowing how to write it.")
print("  wrapped to 60 columns:")
for line in textwrap.wrap(paragraph, width=60):
    print("    ", line)
print()

print("  shortened:", textwrap.shorten(paragraph, width=70, placeholder=" ..."))
print()


# =============================================================================
# PART 8 — argparse: PROPER COMMAND-LINE TOOLS
# =============================================================================
print(LINE)
print("PART 8 — argparse")
print(LINE)

# Lesson 04 used sys.argv directly. That's fine for one argument. For a real
# tool you want --flags, defaults, type conversion, validation and a --help
# page. argparse gives you all of it.
#
# A COMPLETE EXAMPLE (not run here, since this file takes no arguments):
#
#     import argparse
#
#     parser = argparse.ArgumentParser(description="Analyse a sales CSV.")
#     parser.add_argument("input_file", help="path to the CSV")
#     parser.add_argument("--output", "-o", default="report.txt",
#                         help="where to write the report")
#     parser.add_argument("--top", type=int, default=10,
#                         help="how many rows to show")
#     parser.add_argument("--region", choices=["EU", "AS", "US"],
#                         help="filter to one region")
#     parser.add_argument("--verbose", "-v", action="store_true",
#                         help="print extra detail")
#     args = parser.parse_args()
#
#     print(args.input_file, args.top, args.verbose)
#
# Then from the terminal:
#     python3 tool.py sales.csv --top 5 --region EU -v
#     python3 tool.py --help        <- generated for you, free
#
# Lesson 20 builds a real tool with this.
print("  (see the commented example in the source of this section)")
print()


# =============================================================================
# PART 9 — FINDING THINGS YOURSELF
# =============================================================================
print(LINE)
print("PART 9 — HOW TO EXPLORE")
print(LINE)

# dir() lists what's available on any object or module:
print("  useful names in statistics:")
print("   ", [n for n in dir(statistics) if not n.startswith("_")][:10])

# help() prints the documentation. Try these in a terminal:
#     python3 -c "help(str.split)"
#     python3 -m pydoc datetime
print("\n  str.split docs (first line):")
print("   ", str.split.__doc__.strip().splitlines()[0])

print("\n  Where to look things up:")
print("    docs.python.org/3/library/  - the official module index")
print("    help(thing) in a terminal   - offline, always available")
print("    dir(thing)                  - what can this object do?")
print()


# =============================================================================
# PART 10 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 10 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: reinventing something that exists. Before writing more than ten
#   lines of general-purpose logic, search the standard library.

# MISTAKE 2: using `random` for passwords or tokens. It's predictable. Use
#   `secrets`.

# MISTAKE 3: using floats for money. Use Decimal, or integer pennies.

# MISTAKE 4: Decimal(0.1) instead of Decimal("0.1").

# MISTAKE 5: storing dates as strings. Parse to date objects, and only format
#   back to text when displaying.

# MISTAKE 6: regex for everything. If .split() reads more clearly, use .split().

# MISTAKE 7: hard-coding secrets. Use os.environ.

# MISTAKE 8: importing a module inside a loop. Imports are cached, so it isn't
#   slow, but it's noise - put them at the top.
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# EXERCISE 1 — Date tools
#   Write functions: days_until(target_date), age_in_days(birth_date), and
#   next_friday(). Print the results for a few inputs.
#
# EXERCISE 2 — Counter practice
#   Read data/server.log, extract the log level from each line, and use Counter
#   to report the counts and the most common level. Compare how much shorter
#   this is than lesson 13's manual version.
#
# EXERCISE 3 — Regex extraction
#   From data/server.log, extract every IP address (pattern: \d+\.\d+\.\d+\.\d+)
#   and every duration in ms. Report the unique IPs and the longest duration.
#
# EXERCISE 4 — Password generator
#   Write generate_password(length=16, symbols=True) using `secrets`. Ensure at
#   least one digit, one uppercase and one symbol. Generate five.
#
# EXERCISE 5 — Statistics report
#   Load the quantities from data/sales.csv and print mean, median, mode,
#   standard deviation and quartiles. Then flag any value more than two
#   standard deviations from the mean as an outlier.
#
# EXERCISE 6 — Money done right
#   Redo lesson 14's revenue calculation using Decimal throughout. Compare the
#   final total against the float version and see if they differ.
#
# EXERCISE 7 — Build a CLI
#   Write wordcount.py using argparse: it takes a file path, an optional
#   --top N (default 10) and a --min-length flag, then prints the most common
#   words. Run it with --help and admire the free documentation.
#
# EXERCISE 8 — itertools challenge
#   Given a list of orders, use groupby to produce a per-region summary
#   (remember to sort first). Then use combinations to list every possible
#   pair of products that could be bundled together.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   def days_until(target):
#       return (target - date.today()).days
#   def age_in_days(birth):
#       return (date.today() - birth).days
#   def next_friday():
#       today = date.today()
#       ahead = (4 - today.weekday()) % 7 or 7      # 4 == Friday
#       return today + timedelta(days=ahead)
#
# EXERCISE 2
#   from collections import Counter
#   levels = Counter(line.split()[2]
#                    for line in (Path(__file__).parent / "data" / "server.log")
#                    .read_text(encoding="utf-8").splitlines() if line.strip())
#   print(levels, levels.most_common(1))
#
# EXERCISE 3
#   text = (Path(__file__).parent / "data" / "server.log").read_text(encoding="utf-8")
#   ips = set(re.findall(r"\d+\.\d+\.\d+\.\d+", text))
#   durations = [int(ms) for ms in re.findall(r"(\d+)ms", text)]
#   print(sorted(ips), max(durations))
#
# EXERCISE 4
#   import string
#   def generate_password(length=16, symbols=True):
#       pool = string.ascii_letters + string.digits
#       if symbols:
#           pool += "!@#$%^&*-_"
#       while True:
#           pw = "".join(secrets.choice(pool) for _ in range(length))
#           if (any(c.isdigit() for c in pw) and any(c.isupper() for c in pw)
#                   and (not symbols or any(c in "!@#$%^&*-_" for c in pw))):
#               return pw
#
# EXERCISE 5
#   import csv
#   with open(Path(__file__).parent / "data" / "sales.csv", newline="",
#             encoding="utf-8") as f:
#       quantities = [int(r["quantity"]) for r in csv.DictReader(f)]
#   mean, sd = statistics.mean(quantities), statistics.stdev(quantities)
#   print(mean, statistics.median(quantities), sd)
#   print("outliers:", [q for q in quantities if abs(q - mean) > 2 * sd])
#
# EXERCISE 7
#   import argparse
#   parser = argparse.ArgumentParser(description="Count words in a file.")
#   parser.add_argument("path")
#   parser.add_argument("--top", type=int, default=10)
#   parser.add_argument("--min-length", type=int, default=1)
#   args = parser.parse_args()
#   words = Path(args.path).read_text(encoding="utf-8").lower().split()
#   words = [w.strip(".,!?;:") for w in words if len(w) >= args.min_length]
#   for word, count in Counter(words).most_common(args.top):
#       print(f"{word:<15}{count:>5}")


print("=" * 70)
print("Lesson 18 complete. Next: 19_data_analysis.py")
print("=" * 70)

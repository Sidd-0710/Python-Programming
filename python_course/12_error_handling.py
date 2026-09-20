"""
===============================================================================
 LESSON 12 — ERROR HANDLING: CODE THAT SURVIVES REALITY
===============================================================================

Time: about 65 minutes (there's a good place for a break halfway).
Assumes: lessons 01-11.


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. recognise the errors you'll meet most often                  (PART 1)
  2. catch an error and carry on, instead of crashing             (PART 2)
  3. run clean-up code whatever happens                           (PART 3)
  4. raise your OWN errors when something is wrong                (PART 4)
  5. avoid the habits that hide bugs                              (PART 5)
  6. process a messy batch without one bad row stopping it all    (PART 6)

NEW WORDS - come back here whenever you forget one:

  exception     Python's name for an error that happens WHILE the program
                runs: ValueError, KeyError, ZeroDivisionError...
  raise         to set off an exception - "stop, something is wrong"
  catch         to handle an exception so the program doesn't crash
  try/except    try:  "attempt this"   except SomeError:  "if it fails, do this"
  else          (on a try) runs only if NOTHING went wrong
  finally       (on a try) runs ALWAYS, error or not - used for clean-up
  traceback     the long error report Python prints when nobody catches it
  custom exception  your own error type, like InsufficientFundsError
  isinstance()  asks "is this value of this type?":  isinstance(5, int) -> True


-------------------------------------------------------------------------------
 THEORY: THE DIFFERENCE BETWEEN A SCRIPT AND A TOOL
-------------------------------------------------------------------------------

Your code so far has assumed a perfect world: files exist, numbers are numbers,
the network is up, users type sensible things. Reality disagrees.

  * the CSV you process nightly arrives empty one morning
  * the API returns an error page instead of JSON
  * someone types "twelve" into the quantity box
  * the disk fills up halfway through writing
  * a key you expected isn't in the dictionary

A script CRASHES when this happens. A tool NOTICES, RESPONDS, and either
recovers or fails with an explanation a human can act on.

Error handling is the single clearest dividing line between "code that works on
my machine" and "code somebody else can rely on".


-------------------------------------------------------------------------------
 EXCEPTIONS: PYTHON'S ALARM SYSTEM
-------------------------------------------------------------------------------

When Python hits something it cannot do, it RAISES AN EXCEPTION. Think of it
as pulling an emergency cord: the current work stops instantly, and the alarm
travels up through whatever called it, looking for someone prepared to handle
it. If nobody is, the program stops and prints a traceback.

Crucially, the alarm is a specific, named thing you can catch selectively:
ValueError is different from FileNotFoundError is different from KeyError.


-------------------------------------------------------------------------------
 THE TWO PHILOSOPHIES
-------------------------------------------------------------------------------

  LBYL - "Look Before You Leap"
         Check conditions first:  if os.path.exists(path): open(path)

  EAFP - "Easier to Ask Forgiveness than Permission"
         Just try it, and handle failure:  try: open(path) except ...

Python strongly favours EAFP, for two reasons. First, your checks are never as
complete as the real operation's (a file can exist but be unreadable, or be
deleted in the microsecond between your check and your open). Second, it keeps
the normal path clean and puts error handling in one clearly marked place.
"""

LINE = "-" * 70


# =============================================================================
# PART 1 — THE EXCEPTIONS YOU'LL ACTUALLY MEET
# =============================================================================
print(LINE)
print("PART 1 — COMMON EXCEPTION TYPES")
print(LINE)

# Rather than describe them, let's trigger them and look. Each one is caught so
# the file keeps running.
#
# Each lambda (lesson 10) is a tiny function that does ONE risky thing. Keeping
# them in a list lets the loop below run each one inside a try, in turn.

examples = [
    ("int('abc')",          lambda: int("abc")),
    ("10 / 0",              lambda: 10 / 0),
    ("[1,2,3][99]",         lambda: [1, 2, 3][99]),
    ("{'a':1}['b']",        lambda: {"a": 1}["b"]),
    ("'age: ' + 22",        lambda: "age: " + 22),
    ("undefined_name",      lambda: undefined_name),          # noqa: F821
    ("open('no_such.txt')", lambda: open("no_such_file.txt")),
    ("'abc'.upper(1)",      lambda: "abc".upper(1)),
    ("[1,2].index(99)",     lambda: [1, 2].index(99)),
]

for label, operation in examples:
    try:
        operation()                         # run the risky thing...
    except Exception as error:              # ...and catch whatever it raises
        # type(error).__name__ gives the exception's class name as text
        print(f"  {label:<22} -> {type(error).__name__}: {error}")
print()

# THE ONES TO REMEMBER:
#   ValueError          right type, wrong value          int("abc")
#   TypeError           wrong type entirely              "a" + 1
#   KeyError            dict key missing                 d["nope"]
#   IndexError          list position doesn't exist      lst[99]
#   NameError           no such variable                 typo
#   AttributeError      no such method on that type      "s".push()
#   ZeroDivisionError   divided by zero
#   FileNotFoundError   the file isn't there
#   PermissionError     not allowed to read/write it


# =============================================================================
# PART 2 — try / except
# =============================================================================
print(LINE)
print("PART 2 — CATCHING EXCEPTIONS")
print(LINE)

# THE SHAPE:
#
#     try:
#         risky_thing()              <- code that might fail
#     except SomeError:
#         handle_it()                <- runs ONLY if that error occurred
#
# If nothing goes wrong, the except block is skipped entirely.

def to_int(text, fallback=0):
    """Convert text to an int, falling back to a default if it isn't one."""
    try:
        return int(text)
    except ValueError:
        return fallback

for sample in ["42", "abc", "", "  7  ", "3.9"]:
    print(f"  to_int({sample!r:<8}) -> {to_int(sample, fallback=-1)}")
print()

# CATCH SPECIFIC EXCEPTIONS, and handle each differently:
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        print("    (can't divide by zero - returning None)")
        return None
    except TypeError:
        print("    (those weren't both numbers - returning None)")
        return None

print("  safe_divide(10, 2) :", safe_divide(10, 2))
print("  safe_divide(10, 0) :", safe_divide(10, 0))
print("  safe_divide(10,'x'):", safe_divide(10, "x"))
print()

# Catch several types with one handler using a tuple:
def parse_config_value(raw):
    try:
        return int(raw.strip())
    except (ValueError, AttributeError):    # "either of these two errors"
        return None

print("  parse '  5 ':", parse_config_value("  5 "))
print("  parse None  :", parse_config_value(None))   # None has no .strip()
print()

# Capture the exception object with `as` to inspect or log it:
try:
    int("not a number")
except ValueError as error:                 # `error` now holds the details
    print(f"  caught: {error}")
    print(f"  its type: {type(error).__name__}")
print()

# TRY IT NOW (2 minutes):
#   Write a try/except that attempts  int("12.5")  and, if it fails with a
#   ValueError, prints "that's not a whole number".


# =============================================================================
# PART 3 — else AND finally
# =============================================================================
print(LINE)
print("PART 3 — else AND finally")
print(LINE)

# THE FULL SHAPE:
#
#     try:        the risky operation, kept as SMALL as possible
#     except:     what to do when it fails
#     else:       runs only if NO exception happened
#     finally:    runs ALWAYS - success, failure, even on return

def process(value):
    print(f"\n  processing {value!r}")
    try:
        number = int(value)
    except ValueError:
        print("    except: not a number")
        return None
    else:
        print("    else  : conversion succeeded, safe to continue")
        return number * 2
    finally:
        print("    finally: this runs no matter what")

print("  result:", process("21"))
print("  result:", process("oops"))
print()

# WHY `else` EXISTS: it keeps the try block minimal. Only the line that can
# actually raise goes in the try; everything that depends on its success goes
# in the else. That way you never accidentally catch an error from unrelated
# code further down.

# WHY `finally` MATTERS: cleanup. Closing files, releasing locks, disconnecting
# from a database - things that must happen even if the operation exploded.
# (For files specifically, the `with` statement in lesson 13 does this for you,
# which is why you'll rarely write finally by hand.)


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. You can now catch errors. After the break: raising
#  your own errors, the habits to avoid, and a real batch processor.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 4 — RAISING YOUR OWN EXCEPTIONS
# =============================================================================
print(LINE)
print("PART 4 — RAISING EXCEPTIONS")
print(LINE)

# Catching isn't the only half. Sometimes YOUR function is the one that has
# discovered a problem, and the honest response is to refuse to continue.

def set_age(age):
    """Validate and return an age, refusing nonsense."""
    if not isinstance(age, int):            # "if age is NOT a whole number..."
        raise TypeError(f"age must be an int, got {type(age).__name__}")
    if age < 0:
        raise ValueError(f"age cannot be negative (got {age})")
    if age > 150:
        raise ValueError(f"age {age} is not plausible")
    return age

for candidate in [30, -5, 200, "twenty"]:
    try:
        print(f"  set_age({candidate!r:<10}) -> {set_age(candidate)}")
    except (ValueError, TypeError) as error:
        print(f"  set_age({candidate!r:<10}) -> REJECTED: {error}")
print()

# WHY RAISE INSTEAD OF RETURNING None OR printing?
#   * None spreads silently - the caller stores it, and you get a baffling
#     error five functions later, far from the real cause
#   * printing is invisible to the calling code; it can't react
#   * raising is loud, immediate, carries an explanation, and the CALLER gets
#     to decide whether it's fatal
# Rule: fail fast, fail loudly, fail close to the cause.

# YOUR OWN EXCEPTION TYPES - for a real application, define names that mean
# something in your domain.
# (`class` is properly covered in lesson 16. For now: writing
#  `class SomethingError(Exception):` with a docstring underneath is ALL it
#  takes to create a new kind of error.)
class InsufficientFundsError(Exception):
    """Raised when an account lacks the funds for a withdrawal."""

class AccountFrozenError(Exception):
    """Raised when an account is frozen."""

def withdraw(balance, amount, frozen=False):
    if frozen:
        raise AccountFrozenError("this account is frozen")
    if amount > balance:
        raise InsufficientFundsError(f"balance {balance}, requested {amount}")
    return balance - amount

for balance, amount, frozen in [(100, 30, False), (100, 500, False), (100, 30, True)]:
    try:
        print(f"  withdraw({amount}) from {balance} -> {withdraw(balance, amount, frozen)}")
    except InsufficientFundsError as error:
        print(f"  withdraw({amount}) from {balance} -> declined: {error}")
    except AccountFrozenError as error:
        print(f"  withdraw({amount}) from {balance} -> blocked: {error}")

# The caller can now handle "not enough money" completely differently from
# "account frozen" - one might offer an overdraft, the other must call support.
# You couldn't do that if both returned False.
print()

# TRY IT NOW (2 minutes):
#   Write  def check_score(score):  that raises ValueError("score must be
#   0-100") when score is outside 0 to 100, and returns score otherwise.
#   Call it with 50 and with 150 (inside a try) and print what happens.


# =============================================================================
# PART 5 — WHAT NOT TO DO
# =============================================================================
print(LINE)
print("PART 5 — ANTI-PATTERNS")
print(LINE)

# ***** ANTI-PATTERN 1: THE BARE except *****
#
#     try:
#         do_something()
#     except:                # catches EVERYTHING
#         pass               # and says nothing  (`pass` = "do nothing")
#
# This is the worst line of code you can write. It swallows typos (NameError),
# swallows Ctrl+C (KeyboardInterrupt), swallows out-of-memory errors, and
# leaves you debugging a program that silently does nothing at all.
#
# If you genuinely must catch broadly, catch `Exception` (which excludes
# system-exit signals) and ALWAYS log what happened:

def risky():
    return int("boom")

try:
    risky()
except Exception as error:              # acceptable at a program's top level
    print(f"  unexpected failure: {type(error).__name__}: {error}")
print()

# ***** ANTI-PATTERN 2: A try BLOCK THAT'S TOO BIG *****
#
#     try:
#         data = load_file(path)        # this might raise ValueError
#         total = int(data["count"])    # so might this
#         save(total)                   # and this
#     except ValueError:
#         print("bad file")             # ...but WHICH one failed?
#
# Keep try blocks down to the operation you're actually guarding.

# ***** ANTI-PATTERN 3: USING EXCEPTIONS FOR NORMAL FLOW *****
# If a key being absent is completely routine, dict.get() is clearer than
# wrapping every lookup in try/except. Exceptions are for the EXCEPTIONAL.

# ***** ANTI-PATTERN 4: CATCHING AND IGNORING *****
#     except ValueError:
#         pass
# Occasionally legitimate, but 95% of the time it's a bug waiting to surface.
# At minimum, leave a comment explaining why ignoring is correct here.

# ***** ANTI-PATTERN 5: CATCHING WHAT YOU CAN'T HANDLE *****
# If your function can't do anything useful about the error, don't catch it.
# Let it travel up to code that can. Catching and re-raising unchanged is just
# noise - though re-raising WITH context is valuable:
def load_settings(raw):
    try:
        return int(raw)
    except ValueError as error:
        # "raise a NEW, clearer error, and remember the original as its cause"
        raise ValueError(f"invalid setting {raw!r} in config file") from error

try:
    load_settings("abc")
except ValueError as error:
    print(f"  enriched error: {error}")
    print(f"  original cause: {error.__cause__}")
print()


# =============================================================================
# PART 6 — REAL EXAMPLE: A ROBUST BATCH PROCESSOR
# =============================================================================
print(LINE)
print("PART 6 — REAL EXAMPLE: PROCESSING A MESSY BATCH")
print(LINE)

# THE KEY IDEA: one bad record must not kill the whole job. Catch per item,
# record the failure, carry on, and report at the end. This is the shape of
# almost every real automation script.

raw_records = [
    "101,Ana,249.99",
    "102,Sidd,89.50",
    "103,Marco,NOT_A_NUMBER",       # bad amount
    "104,Ana",                      # missing a field
    "105,Zara,675.25",
    "",                             # empty
    "106,Priya,-50.00",             # negative - invalid for our rules
]


def parse_record(line):
    """Parse one record, raising ValueError with a clear reason if it's bad."""
    parts = [p.strip() for p in line.split(",")]    # split at commas, trim each

    if len(parts) != 3:
        raise ValueError(f"expected 3 fields, found {len(parts)}")

    record_id, name, amount_text = parts

    if not record_id.isdigit():
        raise ValueError(f"id {record_id!r} is not a number")

    try:
        amount = float(amount_text)
    except ValueError:
        # `from None` hides the original, less helpful error message
        raise ValueError(f"amount {amount_text!r} is not a number") from None

    if amount < 0:
        raise ValueError(f"amount {amount} is negative")

    return {"id": int(record_id), "name": name, "amount": amount}


processed = []
failures = []

# In plain English: "for each line (numbered from 1): skip blanks; try to parse
# it; if it's good keep it, if it's bad write down WHY - and keep going".
for line_number, line in enumerate(raw_records, start=1):
    if not line.strip():
        continue                              # blank lines are expected, skip

    try:
        processed.append(parse_record(line))
    except ValueError as error:
        failures.append((line_number, line, str(error)))

print(f"  processed: {len(processed)}")
print(f"  failed   : {len(failures)}")
print()

if processed:
    total = sum(record["amount"] for record in processed)
    print(f"  total value: {total:,.2f}")
    print(f"  average    : {total / len(processed):,.2f}")

if failures:
    print("\n  Failures needing attention:")
    for line_number, line, reason in failures:
        print(f"    line {line_number}: {reason}")
        print(f"      raw: {line!r}")

# Note what this gives you: a complete run, a usable result from the good data,
# AND a precise list of what to fix. That report is what makes a script
# something a colleague can actually use.
print()


# =============================================================================
# PART 7 — DEFENSIVE HABITS THAT PREVENT ERRORS
# =============================================================================
print(LINE)
print("PART 7 — PREVENTION")
print(LINE)

# Not every problem needs try/except. Often a safer default is enough.

data = {"name": "Sidd"}
print("  dict.get with default :", data.get("age", "unknown"))

items = [1, 2, 3]
print("  slice can't IndexError:", items[10:20])       # -> [] rather than a crash

print("  guard before dividing :", 0 if not items else sum(items) / len(items))

text = None
print("  check before methods  :", text.upper() if text else "(nothing)")

# isinstance() checks a type before you rely on it:
value = "42"
print("  isinstance check      :", isinstance(value, str), isinstance(value, int))

# A good general rule: validate at the BOUNDARY (where data enters your
# program), then trust it internally. Don't re-check the same thing in twenty
# places - check once, convert once, and let the rest of your code assume it's
# clean.
print()


# =============================================================================
# PART 8 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 8 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: bare `except:` or `except Exception: pass`. Covered in PART 5.

# MISTAKE 2: catching an exception that can't happen there, giving false
#   confidence that the code is protected when it isn't.

# MISTAKE 3: putting the `return` in the wrong block so a value escapes
#   unvalidated.

# MISTAKE 4: catching a parent class before a child. `except Exception` before
#   `except ValueError` means the ValueError branch is unreachable - Python
#   matches top to bottom, and every exception is an Exception.
#   ORDER: most specific first, broadest last.

# MISTAKE 5: error messages that don't help.
#     print("Error!")                       useless
#     print(f"Could not read {path}: {e}")  actionable
#   Include WHAT failed, WHICH value caused it, and WHAT the user can do.

# MISTAKE 6: using exceptions where an if would do.

# MISTAKE 7: letting a partial write survive a failure. If a job fails halfway,
#   decide deliberately: roll back, or record where it stopped so it can resume.
print()


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * Errors while running are EXCEPTIONS: ValueError, KeyError, TypeError...
#   * try: ... except SomeError: ...  catches one and lets the program go on.
#   * Catch SPECIFIC errors. Never a bare  except:  that hides everything.
#   * else runs if nothing failed; finally runs no matter what.
#   * raise ValueError("clear message")  when YOUR code finds a problem.
#   * class MyError(Exception):  creates your own error type.
#   * In a batch job: catch per item, record failures, keep going, report.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. Which exception does  int("hello")  raise?  And  {"a": 1}["b"]?
#   Q2. What's wrong with  except: pass ?
#   Q3. When does a finally block run?
#   Q4. Your function gets a negative price. Return None, print, or raise?
#   Q5. In a loop over 1,000 records, where should the try go - around the
#       whole loop, or inside it around each record?
#
# ANSWERS
#   A1. ValueError.  KeyError.
#   A2. It hides EVERY error, even typos, so bugs become invisible.
#   A3. Always - whether the try succeeded, failed, or returned.
#   A4. Raise (a ValueError with a clear message). It's loud and the caller
#       decides what to do.
#   A5. Inside, around each record - so one bad record doesn't stop the rest.


# =============================================================================
# EXERCISES
# =============================================================================
#
# WARM-UP A (easy) — Your first catch
#   Wrap  int("abc")  in try/except ValueError and print "not a number"
#   instead of crashing.
#
# WARM-UP B (easy) — Divide safely
#   Try  10 / 0  and catch ZeroDivisionError, printing "can't divide by zero".
#
# WARM-UP C (easy) — Raise one
#   Create  number = 150.  If it's over 100, raise ValueError("too big").
#   Put it inside a try, catch the ValueError, and print its message.
#
# EXERCISE 1 (easy) — Safe converter
#   Write safe_float(text, default=0.0) that returns the float, or the default
#   if conversion fails. Test with "3.14", "abc", "", None and "  2.5  ".
#   Hint: float(None) raises TypeError, not ValueError - catch both.
#
# EXERCISE 2 (medium) — Calculator that won't die
#   Write calculate(a, operator, b) supporting + - * /. Raise a ValueError for
#   an unknown operator, and handle division by zero gracefully. Test all four
#   operators plus two failure cases.
#
# EXERCISE 3 (medium) — Retry
#   Write attempt_connection(attempt_number) that raises ConnectionError for
#   attempts 1 and 2, and returns "connected" from attempt 3 onwards. Then write
#   a loop that tries up to 5 times, catching the failure, printing the attempt
#   number, and stopping on success. Print a final message either way.
#
# EXERCISE 4 (medium) — Validate a user record
#   Write validate_user(data) taking a dict. Raise specific, informative
#   exceptions for: missing "email" key, email without "@", missing "age",
#   age not an int, age under 13. Test with 5 different broken dicts.
#
# EXERCISE 5 (challenge) — Batch processor
#   Extend PART 6's processor: also reject names shorter than 2 characters and
#   ids that are duplicated. Report duplicates separately from other failures.
#
# EXERCISE 6 (medium) — Custom exception hierarchy
#   Create a base ValidationError, then FieldMissingError and FieldFormatError
#   that inherit from it. Write code that catches them separately, and other
#   code that catches all three with a single `except ValidationError`.
#
# EXERCISE 7 (medium) — Spot the anti-pattern
#   Explain everything wrong with this, then rewrite it properly:
#       try:
#           data = load()
#           total = sum(x["amount"] for x in data)
#           save(total)
#           send_email(total)
#       except:
#           pass

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   try:
#       int("abc")
#   except ValueError:
#       print("not a number")
#
# WARM-UP B
#   try:
#       print(10 / 0)
#   except ZeroDivisionError:
#       print("can't divide by zero")
#
# WARM-UP C
#   number = 150
#   try:
#       if number > 100:
#           raise ValueError("too big")
#   except ValueError as error:
#       print(error)                   # -> too big
#
# EXERCISE 1
#   def safe_float(text, default=0.0):
#       try:
#           return float(text)
#       except (ValueError, TypeError):
#           return default
#   for t in ["3.14", "abc", "", None, "  2.5  "]:
#       print(repr(t), safe_float(t))
#
# EXERCISE 2
#   def calculate(a, operator, b):
#       if operator == "+":
#           return a + b
#       if operator == "-":
#           return a - b
#       if operator == "*":
#           return a * b
#       if operator == "/":
#           try:
#               return a / b
#           except ZeroDivisionError:
#               print("can't divide by zero")
#               return None
#       raise ValueError(f"unknown operator {operator!r}")
#
# EXERCISE 3
#   def attempt_connection(attempt_number):
#       if attempt_number < 3:
#           raise ConnectionError("network unreachable")
#       return "connected"
#
#   connected = False
#   for attempt in range(1, 6):
#       try:
#           print(attempt_connection(attempt))
#           connected = True
#           break                       # success: stop retrying
#       except ConnectionError as error:
#           print(f"attempt {attempt} failed: {error}")
#   if not connected:
#       print("gave up after 5 attempts")
#
# EXERCISE 4
#   def validate_user(data):
#       if "email" not in data:
#           raise KeyError("email is required")
#       if "@" not in data["email"]:
#           raise ValueError(f"invalid email {data['email']!r}")
#       if "age" not in data:
#           raise KeyError("age is required")
#       if not isinstance(data["age"], int):
#           raise TypeError("age must be an int")
#       if data["age"] < 13:
#           raise ValueError("must be 13 or older")
#       return True
#
# EXERCISE 5
#   seen_ids = set()
#   duplicates = []
#   # inside the loop, after parsing:
#   #   if record["id"] in seen_ids:
#   #       duplicates.append(record["id"])
#   #       continue
#   #   seen_ids.add(record["id"])
#   # and in parse_record, before the return:
#   #   if len(name) < 2:
#   #       raise ValueError(f"name {name!r} is too short")
#
# EXERCISE 6
#   class ValidationError(Exception):
#       pass
#   class FieldMissingError(ValidationError):
#       pass
#   class FieldFormatError(ValidationError):
#       pass
#   try:
#       raise FieldMissingError("email")
#   except FieldMissingError as e:
#       print("missing:", e)
#   try:
#       raise FieldFormatError("bad date")
#   except ValidationError as e:          # catches any subclass
#       print("validation problem:", e)
#
# EXERCISE 7
#   Problems: bare except hides every error including typos and Ctrl+C; `pass`
#   means failures are invisible; the try block covers four separate
#   operations so you can't tell which failed; a failure after save() but
#   before send_email() leaves inconsistent state.
#   Rewrite:
#       try:
#           data = load()
#       except FileNotFoundError as e:
#           print(f"Could not load data: {e}")
#           raise
#       try:
#           total = sum(x["amount"] for x in data)
#       except (KeyError, TypeError) as e:
#           print(f"Malformed record: {e}")
#           raise
#       save(total)
#       try:
#           send_email(total)
#       except ConnectionError as e:
#           print(f"Saved, but the email failed: {e}")   # non-fatal
#   (`raise` on its own, inside an except, re-raises the same error after
#    you've printed your message.)


print("=" * 70)
print("Lesson 12 complete. Next: 13_files_and_folders.py")
print("=" * 70)

"""
===============================================================================
 LESSON 13 — FILES AND FOLDERS: MAKING WORK PERSIST
===============================================================================

Time: about 80 minutes.
Assumes: lessons 01-12.


-------------------------------------------------------------------------------
 THEORY: EVERYTHING SO FAR HAS BEEN AMNESIAC
-------------------------------------------------------------------------------

Every variable you've created has vanished the moment the program ended.
That's fine for a calculator, useless for a tool. Files are how a program
remembers things between runs, and how it exchanges data with the rest of the
world - other programs, other people, other machines.

This is also THE lesson for your automation goal. Once you can list, read,
write, move and rename files in a loop, you can replace hours of clicking:

  * rename 3,000 photos by their date
  * merge 40 spreadsheets into one
  * scan a log folder every morning and email the errors
  * back up only the files that changed
  * strip a column out of every CSV in a directory


-------------------------------------------------------------------------------
 TWO THINGS TO GET STRAIGHT FIRST
-------------------------------------------------------------------------------

1. A PATH IS JUST TEXT DESCRIBING A LOCATION.
     ABSOLUTE:  /Users/sidd/Python/data/sales.csv   - from the filesystem root
     RELATIVE:  data/sales.csv                      - from where you are now

   Relative paths are relative to the CURRENT WORKING DIRECTORY, which is
   wherever the terminal happened to be when you started the program - NOT
   necessarily where your script file lives. This difference causes an enormous
   number of "it works when I run it from VS Code but not from the terminal"
   problems. PART 2 shows the fix.

2. YOU MUST CLOSE WHAT YOU OPEN.
   An open file holds an operating-system resource, and data you've written may
   sit in a buffer, not yet on disk, until it's closed. Forget to close and you
   get truncated files and locked resources. Python solves this with the `with`
   statement, which closes automatically - even if your code crashes midway.
   Use it every single time.
"""

from pathlib import Path
import os
import shutil

LINE = "-" * 70

# =============================================================================
# PART 1 — pathlib: THE MODERN WAY TO HANDLE PATHS
# =============================================================================
print(LINE)
print("PART 1 — PATHS")
print(LINE)

# You'll see two styles in the wild:
#   os.path.join("data", "sales.csv")     the old way - string functions
#   Path("data") / "sales.csv"            the modern way - path objects
# Use pathlib. It's cleaner, it handles Windows/Mac/Linux differences for you,
# and the / operator for joining paths is genuinely delightful.

# __file__ is a special variable: the path of THIS script. .resolve() makes it
# absolute, .parent gives the folder containing it.
HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"                    # note the / to join
WORK_DIR = HERE / "workspace"               # scratch space for this lesson

print("this script      :", Path(__file__).name)
print("its folder       :", HERE)
print("data folder      :", DATA_DIR)
print("current work dir :", Path.cwd())
print()

# THE LESSON: build paths from HERE, not from the current working directory.
# Then your script works no matter where it's launched from. This one habit
# prevents a whole category of bugs.

sales_file = DATA_DIR / "sales.csv"
print("a full path      :", sales_file)
print("  .name          :", sales_file.name)        # sales.csv
print("  .stem          :", sales_file.stem)        # sales
print("  .suffix        :", sales_file.suffix)      # .csv
print("  .parent        :", sales_file.parent)
print("  .exists()      :", sales_file.exists())
print("  .is_file()     :", sales_file.is_file())
print("  size in bytes  :", sales_file.stat().st_size)
print()

# Make sure our scratch folder exists. parents=True creates missing parents,
# exist_ok=True means "don't complain if it's already there".
WORK_DIR.mkdir(parents=True, exist_ok=True)
print("workspace ready  :", WORK_DIR.exists())
print()


# =============================================================================
# PART 2 — READING FILES
# =============================================================================
print(LINE)
print("PART 2 — READING")
print(LINE)

log_file = DATA_DIR / "server.log"

# --- The `with` statement: always use it ---
#
#     with open(path) as f:
#         ...use f...
#     # file is closed automatically here, even if an exception was raised
#
# "with" sets up something, gives it to you, and guarantees cleanup afterwards.

# METHOD 1 - read the entire file into one string. Simple, but loads everything
# into memory. Fine up to a few hundred MB; fatal for a 20GB log.
with open(log_file, "r", encoding="utf-8") as f:
    whole_text = f.read()

print(f"whole file: {len(whole_text)} characters, "
      f"{len(whole_text.splitlines())} lines")
print("first 60 chars:", repr(whole_text[:60]))
print()

# METHOD 2 - read into a list of lines.
with open(log_file, "r", encoding="utf-8") as f:
    lines = f.readlines()
print(f"readlines gave {len(lines)} items")
print("note the trailing newline:", repr(lines[0]))
print()

# METHOD 3 - LOOP OVER THE FILE DIRECTLY. This is the right default.
# It reads one line at a time, so memory use stays flat no matter how big the
# file is. This is how you process a 20GB log on a laptop.
error_count = 0
with open(log_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")            # strip the trailing newline
        if " ERROR " in line:
            error_count += 1
print(f"streamed the file and found {error_count} ERROR lines")
print()

# pathlib shortcuts for small files - no `with` needed:
print("read_text() length:", len(sales_file.read_text(encoding="utf-8")))
print()

# ALWAYS SPECIFY encoding="utf-8". Without it, Python uses a platform default
# that differs between machines, and your script mysteriously breaks on someone
# else's computer the first time a file contains an accent or an emoji.


# =============================================================================
# PART 3 — WRITING FILES
# =============================================================================
print(LINE)
print("PART 3 — WRITING")
print(LINE)

# THE MODES - the second argument to open():
#   "r"   read (default). Error if the file doesn't exist.
#   "w"   write. CREATES the file, or WIPES IT COMPLETELY if it exists.
#   "a"   append. Creates if needed, adds to the end, never destroys.
#   "x"   exclusive create. Errors if the file already exists - useful when
#         overwriting would be a disaster.
#   "rb"/"wb"  binary mode, for images, PDFs, zip files - no text decoding.
#
# ***** "w" IS DESTRUCTIVE AND IMMEDIATE. It empties the file the moment you
# open it, before you write a single byte. Double-check the path. *****

output_file = WORK_DIR / "report.txt"

with open(output_file, "w", encoding="utf-8") as f:
    f.write("SALES REPORT\n")               # write() does NOT add a newline
    f.write("=" * 40 + "\n")                # you add "\n" yourself
    f.write("Generated by lesson 13\n")

    # writelines() writes a list - also without adding newlines
    f.writelines([f"line {n}\n" for n in range(1, 4)])

    # print() can write to a file instead of the screen. It DOES add newlines,
    # which often makes it the more convenient choice:
    print("Written using print(file=...)", file=f)

print(f"wrote {output_file.name} ({output_file.stat().st_size} bytes)")
print("--- its contents ---")
print(output_file.read_text(encoding="utf-8"))

# Appending - the standard pattern for logs and audit trails:
with open(output_file, "a", encoding="utf-8") as f:
    f.write("This line was appended later.\n")

print("--- after appending ---")
print(output_file.read_text(encoding="utf-8"))

# pathlib shortcut for writing small files in one go:
(WORK_DIR / "quick.txt").write_text("written in one line\n", encoding="utf-8")
print("quick.txt says:", (WORK_DIR / "quick.txt").read_text(encoding="utf-8").strip())
print()


# =============================================================================
# PART 4 — LISTING AND FINDING FILES
# =============================================================================
print(LINE)
print("PART 4 — EXPLORING FOLDERS")
print(LINE)

# iterdir() lists the immediate contents of a folder.
print("contents of data/:")
for item in sorted(DATA_DIR.iterdir()):
    kind = "DIR " if item.is_dir() else "FILE"
    size = item.stat().st_size if item.is_file() else 0
    print(f"  [{kind}] {item.name:<20} {size:>8,} bytes")
print()

# glob() finds files matching a pattern - this is your automation superpower.
#   *       any characters
#   ?       one character
#   **      any depth of subfolders (with recursive glob)
print("all .csv files in data/:", [p.name for p in DATA_DIR.glob("*.csv")])
print("everything in data/    :", sorted(p.name for p in DATA_DIR.glob("*")))
print()

# rglob() searches recursively, through every subfolder:
python_files = sorted(HERE.glob("*.py"))
print(f"lesson files in this folder: {len(python_files)}")
for path in python_files[:5]:
    print(f"  {path.name}")
print("  ...")
print()

# A real automation query - "which files are biggest?"
sized = [(p.stat().st_size, p.name) for p in HERE.glob("*.py")]
print("three largest lesson files:")
for size, name in sorted(sized, reverse=True)[:3]:
    print(f"  {name:<34} {size:>8,} bytes")
print()


# =============================================================================
# PART 5 — COPYING, MOVING, RENAMING, DELETING
# =============================================================================
print(LINE)
print("PART 5 — MANAGING FILES")
print(LINE)

# Set up a small sandbox so we can safely demonstrate.
sandbox = WORK_DIR / "sandbox"
sandbox.mkdir(exist_ok=True)

# Create some dummy files to play with.
for name in ["report_2024.txt", "notes.txt", "photo.jpg", "data.csv"]:
    (sandbox / name).write_text(f"contents of {name}\n", encoding="utf-8")

print("created:", sorted(p.name for p in sandbox.iterdir()))

# COPY - shutil.copy2 preserves the timestamps as well as the contents.
shutil.copy2(sandbox / "notes.txt", sandbox / "notes_backup.txt")
print("after copy:", sorted(p.name for p in sandbox.iterdir()))

# RENAME / MOVE - the same operation. .rename() takes the new full path.
(sandbox / "photo.jpg").rename(sandbox / "holiday_photo.jpg")
print("after rename:", sorted(p.name for p in sandbox.iterdir()))

# A BULK RENAME - the thing you'd genuinely automate. Add a prefix to every
# .txt file:
for path in sorted(sandbox.glob("*.txt")):
    new_path = path.with_name(f"archive_{path.name}")
    path.rename(new_path)
print("after bulk rename:", sorted(p.name for p in sandbox.iterdir()))

# DELETE - unlink() for files, rmdir() for empty folders,
# shutil.rmtree() for a folder and everything in it.
(sandbox / "data.csv").unlink()
print("after delete:", sorted(p.name for p in sandbox.iterdir()))

# missing_ok=True stops it raising when the file is already gone:
(sandbox / "never_existed.txt").unlink(missing_ok=True)

# ***** SAFETY *****
# There is no recycle bin. unlink() and rmtree() are permanent and instant.
# Before writing any deletion loop:
#   1. Run it with the delete line commented out, PRINTING what it would touch
#   2. Read that list carefully
#   3. Only then uncomment
# Everyone who skips step 1 eventually deletes something they needed.
print()

# Organising files by extension - a genuinely useful script:
print("organising the sandbox by file type:")
for path in sorted(sandbox.iterdir()):
    if path.is_file():
        folder = sandbox / path.suffix.lstrip(".").upper()
        folder.mkdir(exist_ok=True)
        path.rename(folder / path.name)

for folder in sorted(p for p in sandbox.iterdir() if p.is_dir()):
    contents = sorted(p.name for p in folder.iterdir())
    print(f"  {folder.name}/: {contents}")
print()


# =============================================================================
# PART 6 — HANDLING FILE ERRORS
# =============================================================================
print(LINE)
print("PART 6 — WHEN FILES GO WRONG")
print(LINE)

# File work fails constantly in the real world - that's normal, not unusual.
# Lesson 12's try/except is essential here.

def read_config(path):
    """Read a file, returning a helpful message rather than crashing."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[missing] no file at {path}"
    except PermissionError:
        return f"[denied] not allowed to read {path}"
    except UnicodeDecodeError:
        return f"[encoding] {path} isn't valid UTF-8 text - is it binary?"
    except IsADirectoryError:
        return f"[not a file] {path} is a folder"

print(" ", read_config(DATA_DIR / "nope.txt")[:60])
print(" ", read_config(DATA_DIR)[:60])
print(" ", read_config(DATA_DIR / "config.json")[:40].replace("\n", " "))
print()

# The LBYL alternative, for when you just want a default:
path = DATA_DIR / "maybe.txt"
contents = path.read_text(encoding="utf-8") if path.exists() else "(default)"
print("  with an existence check:", contents)

# But remember lesson 12: exists() can be true and open() can still fail. For
# anything important, try/except is the more honest tool.
print()


# =============================================================================
# PART 7 — REAL EXAMPLE: A LOG ANALYSER THAT WRITES A REPORT
# =============================================================================
print(LINE)
print("PART 7 — REAL EXAMPLE: LOG ANALYSIS TO FILE")
print(LINE)

# Read a real log file, analyse it, and write a report. This is a complete,
# genuinely useful automation script - the kind you could schedule to run every
# morning (lesson 20 shows how to package it up).

def analyse_log(path):
    """Read a log file and return a summary dict."""
    summary = {
        "total": 0,
        "levels": {},
        "errors": [],
        "slowest": None,
        "users": set(),
    }

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            summary["total"] += 1
            parts = line.split(None, 3)
            if len(parts) < 4:
                continue
            date, time, level, message = parts

            summary["levels"][level] = summary["levels"].get(level, 0) + 1

            if level == "ERROR":
                summary["errors"].append(f"{time} {message}")

            if "logged in" in message:
                # "User ana logged in from ..." -> take the word after "User"
                words = message.split()
                if len(words) >= 2:
                    summary["users"].add(words[1])

    return summary


stats = analyse_log(log_file)

report_lines = [
    "SERVER LOG ANALYSIS",
    "=" * 50,
    f"Source file : {log_file.name}",
    f"Total lines : {stats['total']}",
    "",
    "Lines by level:",
]
for level, count in sorted(stats["levels"].items()):
    share = count / stats["total"]
    report_lines.append(f"  {level:<6} {count:>4}  ({share:.0%})  {'#' * count}")

report_lines += ["", f"Distinct users seen: {len(stats['users'])}"]
report_lines.append(f"  {', '.join(sorted(stats['users']))}")
report_lines += ["", f"Errors ({len(stats['errors'])}):"]
report_lines += [f"  {e}" for e in stats["errors"]]

report_path = WORK_DIR / "log_report.txt"
report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

print(f"wrote {report_path.name}:\n")
print(report_path.read_text(encoding="utf-8"))


# =============================================================================
# PART 8 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 8 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: opening with "w" when you meant "a", and wiping a file you needed.
#   "w" truncates immediately. Know which one you want before you type it.

# MISTAKE 2: not using `with`. If an exception fires before your .close(), the
#   file stays open and buffered writes may never reach disk.

# MISTAKE 3: relative paths that depend on where you launched the program.
#   Build paths from Path(__file__).parent instead.

# MISTAKE 4: forgetting that write() doesn't add newlines, producing one
#   enormous single-line file.

# MISTAKE 5: forgetting that read lines KEEP their "\n". Compare:
sample = "alpha\n"
print("  without strip:", repr(sample), "== 'alpha'?", sample == "alpha")
print("  with strip   :", repr(sample.strip()), "== 'alpha'?", sample.strip() == "alpha")

# MISTAKE 6: omitting encoding="utf-8" and getting UnicodeDecodeError on
#   someone else's machine.

# MISTAKE 7: reading a huge file with .read() and exhausting memory. Loop over
#   the file object instead.

# MISTAKE 8: deleting without a dry run. See the safety note in PART 5.

# MISTAKE 9: assuming a folder exists. Call .mkdir(parents=True, exist_ok=True)
#   before writing into it.
print()

# Clean up the sandbox so re-running this lesson starts fresh.
shutil.rmtree(sandbox, ignore_errors=True)
print("sandbox cleaned up; report files kept in workspace/")
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# Work inside the `workspace/` folder so you can't damage anything.
#
# EXERCISE 1 — Write and read back
#   Write a file containing your five favourite foods, one per line. Read it
#   back, strip the newlines, and print them numbered.
#
# EXERCISE 2 — Append a journal
#   Write a function log_entry(text) that appends a line to workspace/journal.txt
#   in the form "[entry N] text". Call it four times, then print the file.
#
# EXERCISE 3 — Word count tool
#   Read data/server.log and report: number of lines, number of words, number
#   of characters, and the 5 most common words (use a dict, lesson 09).
#
# EXERCISE 4 — Filter a file
#   Read data/server.log and write TWO new files into workspace/: errors.log
#   (only ERROR lines) and warnings.log (only WARN lines). Print how many
#   lines each received.
#
# EXERCISE 5 — Find and report
#   List every .py file in the course folder with its size in KB, sorted
#   largest first. Print a total at the bottom.
#
# EXERCISE 6 — Safe bulk renamer (do the dry run first!)
#   In workspace/, create 6 files named "IMG 001.JPG" through "IMG 006.JPG".
#   Write a renamer that converts them to "img_001.jpg" style. Run it FIRST in
#   dry-run mode that only prints what it would do, then for real.
#
# EXERCISE 7 — Deduplicate a file
#   Create a file with repeated lines. Write code producing a new file with
#   duplicates removed, preserving the original order (lesson 08 has the trick).
#
# EXERCISE 8 — Backup with a timestamp
#   Copy data/sales.csv into workspace/ with today's date in the filename, e.g.
#   sales_2026-09-13.csv. (Peek at lesson 18 for `datetime`, or use a fixed
#   string for now.)

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   foods_path = WORK_DIR / "foods.txt"
#   foods_path.write_text("dosa\nramen\npizza\nbiryani\ntacos\n", encoding="utf-8")
#   with open(foods_path, encoding="utf-8") as f:
#       for i, line in enumerate(f, start=1):
#           print(f"{i}. {line.strip()}")
#
# EXERCISE 2
#   journal = WORK_DIR / "journal.txt"
#   def log_entry(text):
#       existing = journal.read_text(encoding="utf-8").splitlines() if journal.exists() else []
#       with open(journal, "a", encoding="utf-8") as f:
#           f.write(f"[entry {len(existing) + 1}] {text}\n")
#   for note in ["started lesson 13", "learned pathlib", "wrote a file", "done"]:
#       log_entry(note)
#   print(journal.read_text(encoding="utf-8"))
#
# EXERCISE 3
#   text = (DATA_DIR / "server.log").read_text(encoding="utf-8")
#   words = text.split()
#   counts = {}
#   for w in words:
#       counts[w] = counts.get(w, 0) + 1
#   print(len(text.splitlines()), len(words), len(text))
#   for word, count in sorted(counts.items(), key=lambda p: p[1], reverse=True)[:5]:
#       print(word, count)
#
# EXERCISE 4
#   errors, warnings = [], []
#   with open(DATA_DIR / "server.log", encoding="utf-8") as f:
#       for line in f:
#           if " ERROR " in line:
#               errors.append(line)
#           elif " WARN " in line:
#               warnings.append(line)
#   (WORK_DIR / "errors.log").write_text("".join(errors), encoding="utf-8")
#   (WORK_DIR / "warnings.log").write_text("".join(warnings), encoding="utf-8")
#   print(len(errors), len(warnings))
#
# EXERCISE 5
#   files = [(p.stat().st_size, p.name) for p in HERE.glob("*.py")]
#   for size, name in sorted(files, reverse=True):
#       print(f"{name:<36}{size / 1024:>8.1f} KB")
#   print(f"{'TOTAL':<36}{sum(s for s, _ in files) / 1024:>8.1f} KB")
#
# EXERCISE 6
#   for n in range(1, 7):
#       (WORK_DIR / f"IMG {n:03d}.JPG").write_text("x", encoding="utf-8")
#   DRY_RUN = True
#   for path in sorted(WORK_DIR.glob("IMG *.JPG")):
#       new_name = path.name.lower().replace(" ", "_")
#       if DRY_RUN:
#           print(f"would rename {path.name} -> {new_name}")
#       else:
#           path.rename(path.with_name(new_name))
#
# EXERCISE 7
#   src = WORK_DIR / "dupes.txt"
#   src.write_text("a\nb\na\nc\nb\na\n", encoding="utf-8")
#   seen = set()
#   unique = []
#   for line in src.read_text(encoding="utf-8").splitlines():
#       if line not in seen:
#           seen.add(line)
#           unique.append(line)
#   (WORK_DIR / "unique.txt").write_text("\n".join(unique) + "\n", encoding="utf-8")
#
# EXERCISE 8
#   from datetime import date
#   target = WORK_DIR / f"sales_{date.today()}.csv"
#   shutil.copy2(DATA_DIR / "sales.csv", target)
#   print("backed up to", target.name)


print("=" * 70)
print("Lesson 13 complete. Next: 14_json_and_csv.py")
print("=" * 70)

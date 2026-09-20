"""
===============================================================================
 LESSON 20 — PROJECT: A REAL AUTOMATION TOOL
===============================================================================

Time: about 90 minutes (there's a good place for a break halfway).
Assumes: lessons 01-19.


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

This lesson is different: it's ONE complete program, built from small
functions. There's no new Python syntax to learn - only new ways of putting
what you know together.

HOW TO READ THIS FILE:
  1. Run it once with no arguments. It builds a practice folder of junk files
     and runs every feature on it - nothing of yours is touched.
  2. Read PARTS 1-6. Each is a small function that does ONE job.
  3. Read PART 7's main(). It's the "manager" that calls the other functions
     depending on which --flags you gave.
  4. Try the commands in the TRY IT NOW boxes.

NEW WORDS - come back here whenever you forget one:

  logging       a better print() for tools: every message gets a time and a
                level, and can go to a file AND the screen
  log level     how serious a message is: DEBUG, INFO, WARNING, ERROR
  config        settings kept in one place (often a JSON file) instead of
                scattered through the code
  dry run       "show me what you WOULD do, but don't do it". Essential for
                anything that moves or deletes files
  hash          a short "fingerprint" of a file's contents. Identical content
                always gives an identical hash
  exit code     a number a program hands back when it finishes: 0 = worked,
                anything else = failed. Other programs check it
  flag          a command-line option like --dry-run or --report
  cron          the Mac/Linux tool for running a program on a schedule


-------------------------------------------------------------------------------
 WHY THIS LESSON EXISTS
-------------------------------------------------------------------------------

Everything so far has been a lesson. This is a PROJECT: one complete, genuinely
useful program that combines functions, files, error handling, CSV, dicts, the
standard library and argparse into something you could actually schedule to run
every morning.

It also introduces the habits that separate a script from a tool:

  * a --dry-run mode, so you can see what it WOULD do before it does it
  * logging instead of scattered print() calls
  * a config file instead of hard-coded settings
  * exit codes, so other programs can tell whether it worked
  * a main() function and a __main__ guard

These habits matter enormously for AI engineering later: an agent that takes
actions on your behalf needs exactly this discipline - dry runs, logs, and the
ability to say "I failed" in a way the calling system understands.


-------------------------------------------------------------------------------
 THE TOOL WE'RE BUILDING: `filekeeper`
-------------------------------------------------------------------------------

It scans a folder and:
  1. reports what's there (count, size, types, oldest/newest)
  2. organises files into subfolders by type
  3. finds duplicate files by content
  4. archives files older than N days
  5. writes a log and a summary report

Run it from the terminal:

    python3 20_automation_project.py --help
    python3 20_automation_project.py --report
    python3 20_automation_project.py --organise --dry-run
    python3 20_automation_project.py --organise
    python3 20_automation_project.py --find-duplicates
    python3 20_automation_project.py --archive-older-than 30 --dry-run

With no arguments it runs a self-demo on a sandbox folder it creates itself, so
the file is safe to just run.
"""

import argparse
import hashlib
import json
import logging
import os
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK_DIR = HERE / "workspace"
SANDBOX = WORK_DIR / "filekeeper_demo"

LINE = "-" * 70


# =============================================================================
# PART 1 — LOGGING: GROWN-UP print()
# =============================================================================
#
# print() is fine while you're learning. A tool that runs unattended needs
# LOGGING, which gives you for free:
#   * severity levels (DEBUG / INFO / WARNING / ERROR / CRITICAL)
#   * timestamps on every line
#   * output to a file AND the screen at once
#   * the ability to turn detail up or down without editing code
#
# When your 3am job fails, the log is the only evidence you will have.
#
# You'll mostly USE a logger, not build one. Using it looks like:
#     logger.info("moved 3 files")        instead of   print("moved 3 files")
#     logger.warning("file already exists")
#     logger.error("cannot read folder")

def setup_logging(log_path, verbose=False):
    """Configure logging to both a file and the console."""
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("filekeeper")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()           # so re-running doesn't duplicate output

    # A "handler" is one place log messages go to.
    # The file gets everything, with full timestamps.
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
    )

    # The console gets a tidier view, and only INFO and above unless --verbose.
    console_handler = logging.StreamHandler(sys.stdout)
    if verbose:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("  %(levelname)-8s %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


# =============================================================================
# PART 2 — CONFIGURATION
# =============================================================================
#
# Settings that a user might want to change do NOT belong scattered through the
# code. Put them in one place - ideally a JSON file, so they can be edited
# without touching Python.

DEFAULT_CONFIG = {
    "type_folders": {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic"],
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".md", ".rtf"],
        "Spreadsheets": [".csv", ".xlsx", ".xls"],
        "Data": [".json", ".xml", ".yaml", ".yml"],
        "Archives": [".zip", ".tar", ".gz", ".7z"],
        "Code": [".py", ".js", ".html", ".css", ".sql"],
    },
    "ignore_names": [".DS_Store", "Thumbs.db", ".gitkeep"],
    "archive_folder": "_archive",
}


def load_config(path):
    """Load config from JSON, falling back to the defaults."""
    config = dict(DEFAULT_CONFIG)              # start with a copy of the defaults
    if path and Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        config.update(user_config)             # the user's settings win (lesson 09)
    return config


def folder_for_extension(extension, config):
    """Map a file extension to its destination folder name."""
    extension = extension.lower()
    for folder, extensions in config["type_folders"].items():
        if extension in extensions:
            return folder
    return "Other"


# =============================================================================
# PART 3 — SCANNING AND REPORTING
# =============================================================================

def scan_folder(folder, config):
    """Return a list of dicts describing every file in `folder`.

    Not recursive on purpose - organising a tree in place is a much riskier
    operation, and a tool should do the safe thing by default.
    """
    files = []
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.name in config["ignore_names"]:
            continue

        stat = path.stat()                     # size, dates and other details
        files.append({
            "path": path,
            "name": path.name,
            "extension": path.suffix.lower(),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "category": folder_for_extension(path.suffix, config),
        })
    return files


def human_size(num_bytes):
    """Turn a byte count into something a person can read: 2048 -> '2.0 KB'."""
    if num_bytes < 1024:
        return f"{num_bytes:,} B"
    size = num_bytes / 1024
    for unit in ("KB", "MB"):
        if size < 1024:
            return f"{size:,.1f} {unit}"
        size = size / 1024                     # too big - try the next unit up
    return f"{size:,.1f} GB"


def build_report(files):
    """Summarise a scan. Returns a dict - the caller decides how to show it."""
    if not files:
        return {"count": 0}

    by_category = defaultdict(list)
    for record in files:
        by_category[record["category"]].append(record)

    categories = {}
    for name, group in by_category.items():
        categories[name] = {"count": len(group),
                            "size": sum(f["size"] for f in group)}

    return {
        "count": len(files),
        "total_size": sum(f["size"] for f in files),
        "extensions": Counter(f["extension"] or "(none)" for f in files),
        "categories": categories,
        "oldest": min(files, key=lambda f: f["modified"]),
        "newest": max(files, key=lambda f: f["modified"]),
        "largest": max(files, key=lambda f: f["size"]),
    }


def size_of_category(pair):
    """For sorting (name, stats) pairs by their size."""
    return pair[1]["size"]


def print_report(report, logger):
    """Display a report. Separated from build_report so each does ONE job -
    which also means build_report can feed a web page or an email later."""
    if report["count"] == 0:
        logger.info("folder is empty - nothing to report")
        return

    logger.info(f"{report['count']} files, {human_size(report['total_size'])} total")
    logger.info("")
    logger.info(f"  {'category':<14}{'files':>7}{'size':>14}")
    logger.info("  " + "-" * 35)
    for name, stats in sorted(report["categories"].items(),
                              key=size_of_category, reverse=True):
        logger.info(f"  {name:<14}{stats['count']:>7}{human_size(stats['size']):>14}")

    logger.info("")
    logger.info(f"  largest : {report['largest']['name']} "
                f"({human_size(report['largest']['size'])})")
    # {date:%Y-%m-%d} formats a date right inside an f-string (lesson 18)
    logger.info(f"  oldest  : {report['oldest']['name']} "
                f"({report['oldest']['modified']:%Y-%m-%d})")
    logger.info(f"  newest  : {report['newest']['name']} "
                f"({report['newest']['modified']:%Y-%m-%d})")


# =============================================================================
# PART 4 — ORGANISING (with the all-important dry run)
# =============================================================================
#
# ***** THE DRY-RUN PRINCIPLE *****
# Any tool that MOVES or DELETES things must be able to describe what it would
# do without doing it. This is not politeness; it is the difference between
# "oops" and "disaster". Note how `dry_run` is threaded through as a parameter
# rather than being a global - that makes it obvious at every call site.

def organise_files(folder, files, config, logger, dry_run=True):
    """Move each file into a subfolder named after its category."""
    moved = 0
    skipped = 0

    for record in files:
        destination_folder = folder / record["category"]
        destination = destination_folder / record["name"]

        if destination.exists():
            logger.warning(f"skip {record['name']} - already exists at destination")
            skipped += 1
            continue

        if dry_run:
            logger.info(f"WOULD MOVE {record['name']} -> {record['category']}/")
        else:
            destination_folder.mkdir(exist_ok=True)
            record["path"].rename(destination)
            logger.info(f"moved {record['name']} -> {record['category']}/")
        moved += 1

    if dry_run:
        logger.info(f"would move {moved} files, skipped {skipped}")
    else:
        logger.info(f"moved {moved} files, skipped {skipped}")
    return moved, skipped


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. You've seen the building blocks: logging, config,
#  scanning, reporting and organising. After the break: duplicates, archiving,
#  and the main() function that ties it all together.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 5 — FINDING DUPLICATES BY CONTENT
# =============================================================================
#
# Two files with different names can hold identical content. Comparing byte by
# byte is slow; instead we compute a HASH - a short fingerprint of the content.
# Identical content always produces an identical hash.
#
# The two-stage trick below is what real duplicate-finders do: group by size
# first (instant, from the filesystem), and only hash within groups that have
# more than one file. Files of different sizes cannot possibly be duplicates,
# so this avoids reading most of the data at all.

def file_hash(path, chunk_size=65536):
    """Return a SHA-256 fingerprint of a file's contents."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:                  # "rb" = read binary
        while True:                              # read in chunks, not all at once
            chunk = f.read(chunk_size)
            if not chunk:                        # an empty chunk = end of the file
                break
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(files, logger):
    """Return a dict of hash -> list of files sharing that content."""
    # Stage 1: group by size.
    by_size = defaultdict(list)
    for record in files:
        by_size[record["size"]].append(record)

    candidates = [group for group in by_size.values() if len(group) > 1]
    logger.debug(f"{sum(len(g) for g in candidates)} files share a size - hashing those")

    # Stage 2: hash only the files that share a size.
    by_hash = defaultdict(list)
    for group in candidates:
        for record in group:
            by_hash[file_hash(record["path"])].append(record)

    duplicates = {}
    for fingerprint, group in by_hash.items():
        if len(group) > 1:                       # 2+ files with the same fingerprint
            duplicates[fingerprint] = group

    if duplicates:
        wasted = sum(g[0]["size"] * (len(g) - 1) for g in duplicates.values())
        logger.info(f"found {len(duplicates)} duplicate sets, "
                    f"wasting {human_size(wasted)}")
        for group in duplicates.values():
            names = ", ".join(r["name"] for r in group)
            logger.info(f"  identical ({human_size(group[0]['size'])}): {names}")
    else:
        logger.info("no duplicates found")

    return duplicates


# =============================================================================
# PART 6 — ARCHIVING OLD FILES
# =============================================================================

def archive_old_files(folder, files, days, config, logger, dry_run=True):
    """Move files older than `days` into an archive subfolder."""
    cutoff = datetime.now() - timedelta(days=days)      # "days ago" as a date
    archive_dir = folder / config["archive_folder"]

    old_files = [f for f in files if f["modified"] < cutoff]
    logger.info(f"{len(old_files)} files older than {days} days "
                f"(before {cutoff:%Y-%m-%d})")

    for record in old_files:
        if dry_run:
            logger.info(f"WOULD ARCHIVE {record['name']} "
                        f"({record['modified']:%Y-%m-%d})")
        else:
            archive_dir.mkdir(exist_ok=True)
            record["path"].rename(archive_dir / record["name"])
            logger.info(f"archived {record['name']}")

    return len(old_files)


# =============================================================================
# PART 7 — THE COMMAND-LINE INTERFACE
# =============================================================================

def build_parser():
    """Define the command-line interface.

    argparse gives you --help, type conversion and validation for free. Compare
    this to picking apart sys.argv by hand (lesson 04) - it's not even close.
    """
    parser = argparse.ArgumentParser(
        prog="filekeeper",
        description="Scan, organise, deduplicate and archive a folder.",
        epilog="Tip: always try --dry-run first.",
    )
    # nargs="?" = "this argument is optional"
    parser.add_argument("folder", nargs="?", default=None,
                        help="folder to work on (default: a demo sandbox)")
    # action="store_true" = "a switch: True if the flag is given, else False"
    parser.add_argument("--report", action="store_true",
                        help="show a summary of the folder")
    parser.add_argument("--organise", action="store_true",
                        help="move files into subfolders by type")
    parser.add_argument("--find-duplicates", action="store_true",
                        help="find files with identical contents")
    parser.add_argument("--archive-older-than", type=int, metavar="DAYS",
                        help="move files older than DAYS into the archive folder")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would happen, change nothing")
    parser.add_argument("--config", metavar="PATH",
                        help="path to a JSON config file")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="show debug detail")
    return parser


def create_demo_sandbox():
    """Build a throwaway folder with realistic junk in it."""
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    SANDBOX.mkdir(parents=True)

    demo_files = {
        "holiday.jpg": "IMAGE DATA " * 200,
        "holiday_copy.jpg": "IMAGE DATA " * 200,        # a deliberate duplicate
        "receipt.pdf": "PDF DATA " * 50,
        "notes.txt": "some notes",
        "notes_backup.txt": "some notes",               # another duplicate
        "sales_q1.csv": "a,b,c\n1,2,3\n",
        "sales_q2.csv": "a,b,c\n4,5,6\n",
        "config.json": '{"setting": true}',
        "script.py": "print('hello')\n",
        "archive.zip": "ZIP DATA " * 100,
        "mystery.xyz": "unknown format",
    }
    for name, content in demo_files.items():
        (SANDBOX / name).write_text(content, encoding="utf-8")

    # Backdate two files so --archive-older-than has something to find.
    # os.utime sets a file's "last accessed" and "last modified" times.
    old_time = (datetime.now() - timedelta(days=200)).timestamp()
    for name in ("receipt.pdf", "archive.zip"):
        os.utime(SANDBOX / name, (old_time, old_time))

    return SANDBOX


def main(argv=None):
    """The entry point. Returns an EXIT CODE: 0 means success.

    Exit codes are how one program tells another whether it worked. A shell
    script, a cron job or a CI pipeline checks this number to decide whether to
    carry on or raise an alarm. Returning 0 from a job that failed is how
    silent breakages happen.
    """
    args = build_parser().parse_args(argv)     # read the --flags

    # No folder given? Then run the safe demo on a sandbox.
    demo_mode = args.folder is None
    if demo_mode:
        folder = create_demo_sandbox()
    else:
        folder = Path(args.folder).expanduser()   # expanduser turns ~ into your home folder

    logger = setup_logging(WORK_DIR / "filekeeper.log", verbose=args.verbose)
    logger.info("=" * 60)
    logger.info(f"filekeeper starting on {folder}")
    if args.dry_run:
        logger.info("DRY RUN - nothing will be changed")

    if not folder.is_dir():
        logger.error(f"not a folder: {folder}")
        return 2                                  # a non-zero code means failure

    config = load_config(args.config)

    try:
        files = scan_folder(folder, config)
    except PermissionError as error:
        logger.error(f"cannot read folder: {error}")
        return 2

    # In demo mode with no flags, run everything so the file is a complete
    # demonstration. any([...]) is True if at least one flag was given.
    any_flag_given = any([args.report, args.organise, args.find_duplicates,
                          args.archive_older_than])
    do_all = demo_mode and not any_flag_given

    # The demo always uses a dry run for the risky steps; otherwise the user's
    # --dry-run choice decides.
    if do_all:
        dry_run = True
    else:
        dry_run = args.dry_run

    if args.report or do_all:
        logger.info("")
        logger.info("--- REPORT ---")
        print_report(build_report(files), logger)

    if args.find_duplicates or do_all:
        logger.info("")
        logger.info("--- DUPLICATES ---")
        find_duplicates(files, logger)

    if args.archive_older_than or do_all:
        logger.info("")
        logger.info("--- ARCHIVE ---")
        days = args.archive_older_than or 90      # 90 if no number was given
        archive_old_files(folder, files, days, config, logger, dry_run=dry_run)

    if args.organise or do_all:
        logger.info("")
        logger.info("--- ORGANISE ---")
        organise_files(folder, files, config, logger, dry_run=dry_run)

    logger.info("")
    logger.info(f"done. log written to {(WORK_DIR / 'filekeeper.log')}")
    if demo_mode:
        logger.info("this was a demo on a sandbox folder; nothing of yours was touched")
        logger.info("try: python3 20_automation_project.py --help")
    return 0                                      # success


# TRY IT NOW (5 minutes), in the terminal from the python_course folder:
#   1. python3 20_automation_project.py --help
#      Read the help text - argparse wrote all of it from build_parser().
#   2. python3 20_automation_project.py --report
#   3. python3 20_automation_project.py --organise --dry-run
#      Nothing moves. Now run it WITHOUT --dry-run, then look inside
#      workspace/filekeeper_demo/ - the files are in category folders.
#   4. Open workspace/filekeeper.log and find the timestamps.


# =============================================================================
# PART 8 — WHAT MAKES THIS A TOOL RATHER THAN A SCRIPT
# =============================================================================
#
#  1. DRY RUN        destructive actions can be previewed
#  2. LOGGING        there's a record of what happened, with timestamps
#  3. CONFIG         settings are data, not code
#  4. EXIT CODES     other programs can detect failure
#  5. --help         it explains itself
#  6. SMALL FUNCTIONS  each does one testable thing
#  7. SEPARATION     build_report() computes; print_report() displays. You can
#                    swap the display for an email or a web page without
#                    touching the logic.
#  8. SAFE DEFAULTS  non-recursive; demo mode when run with no arguments
#
# These same eight properties are exactly what you'll want when you give an AI
# agent the ability to act on real systems in lesson 23. An agent that can move
# files needs a dry run and a log far more urgently than this script does.


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * A real tool is many small functions plus one main() that calls them.
#   * logger.info / .warning / .error beat print(): times, levels, a log file.
#   * Keep settings in a config dict or JSON file, not scattered in code.
#   * Anything that moves or deletes files needs a --dry-run.
#   * A hash fingerprints file contents - equal hashes mean equal files.
#   * argparse turns --flags into args.flag_name, and writes --help for you.
#   * main() returns an exit code: 0 for success, non-zero for failure.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. Why does this tool have a --dry-run flag?
#   Q2. What's the advantage of logging over print()?
#   Q3. Why check file SIZES before hashing when looking for duplicates?
#   Q4. What exit code means "it worked"?
#   Q5. build_report() and print_report() are separate. Why?
#
# ANSWERS
#   A1. So you can see exactly what it would move before it moves anything.
#   A2. Timestamps, severity levels, and a permanent log file - evidence for
#       when something goes wrong while nobody was watching.
#   A3. Files of different sizes can't be identical - so most files never
#       need to be read at all.
#   A4. 0.
#   A5. One calculates, one displays. The same report could then go to an
#       email or a web page without changing the calculation.


# =============================================================================
# EXERCISES
# =============================================================================
#
# WARM-UP A (easy) — Read the help
#   Run  python3 20_automation_project.py --help  and match each option to its
#   add_argument line in build_parser().
#
# WARM-UP B (easy) — One feature at a time
#   Run  python3 20_automation_project.py --find-duplicates  and find the two
#   duplicate pairs in the output.
#
# WARM-UP C (easy) — Change a setting
#   In DEFAULT_CONFIG, add ".xyz" to the "Data" list. Run --organise --dry-run
#   and check that mystery.xyz now goes to Data/ instead of Other/.
#
# EXERCISE 1 (medium) — Add --largest N
#   Add a flag that prints the N largest files. Default to 5.
#
# EXERCISE 2 (challenge) — Delete duplicates safely
#   Add --delete-duplicates that keeps the OLDEST copy of each duplicate set
#   and removes the rest. It must refuse to run without --dry-run first being
#   shown, and must log every deletion.
#
# EXERCISE 3 (challenge) — Recursive mode
#   Add --recursive to make scan_folder walk subfolders (use rglob). Think
#   carefully about what --organise should then do, and what could go wrong.
#
# EXERCISE 4 (medium) — Write the report as JSON and CSV
#   Add --output FILE. If it ends .json write JSON, if .csv write CSV.
#
# EXERCISE 5 (medium) — Date-based folders
#   Add --by-date to organise into YYYY/MM folders from each file's modified
#   date instead of by type.
#
# EXERCISE 6 (easy) — A real config file
#   Write a filekeeper.json with your own categories, and run the tool with
#   --config filekeeper.json. Confirm your categories override the defaults.
#
# EXERCISE 7 (challenge) — Undo
#   Have --organise write a JSON manifest of every move it made. Add --undo
#   that reads the manifest and reverses them. This is a genuinely valuable
#   feature and a good exercise in careful thinking.
#
# EXERCISE 8 (medium) — Schedule it
#   On Mac/Linux, use `crontab -e` to run your tool every morning:
#       0 9 * * * /usr/bin/python3 /path/to/20_automation_project.py ~/Downloads --report
#   Check the log the next day. You have now automated something real.


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A, B and C
#   No code to compare - the output is the answer. For C, the ORGANISE section
#   should now say:  WOULD MOVE mystery.xyz -> Data/
#
# EXERCISE 1 — Add --largest N
#   parser.add_argument("--largest", type=int, nargs="?", const=5,
#                       metavar="N", help="show the N largest files")
#   # (const=5 is the value used when the flag is given without a number)
#   # then in main(), after the scan:
#   if args.largest:
#       logger.info("")
#       logger.info(f"--- {args.largest} LARGEST ---")
#       biggest_first = sorted(files, key=lambda f: f["size"], reverse=True)
#       for record in biggest_first[:args.largest]:
#           logger.info(f"  {record['name']:<30}{human_size(record['size']):>12}")
#
# EXERCISE 2 — Delete duplicates safely
#   def delete_duplicates(files, logger, dry_run=True):
#       """Keep the OLDEST copy of each duplicate set, remove the rest."""
#       duplicates = find_duplicates(files, logger)
#       freed = 0
#       for group in duplicates.values():
#           # oldest first, so ordered[0] is the keeper
#           ordered = sorted(group, key=lambda r: r["modified"])
#           keeper = ordered[0]
#           rest = ordered[1:]
#           logger.info(f"  keeping {keeper['name']} "
#                       f"({keeper['modified']:%Y-%m-%d})")
#           for record in rest:
#               freed += record["size"]
#               if dry_run:
#                   logger.info(f"    WOULD DELETE {record['name']}")
#               else:
#                   record["path"].unlink()
#                   logger.warning(f"    DELETED {record['name']}")
#       if dry_run:
#           logger.info(f"  would free {human_size(freed)}")
#       else:
#           logger.info(f"  freed {human_size(freed)}")
#       return freed
#
#   # Forcing a dry run first - the safety interlock the exercise asks for:
#   #   parser.add_argument("--delete-duplicates", action="store_true")
#   #   parser.add_argument("--i-have-reviewed-the-dry-run", action="store_true")
#   #   if (args.delete_duplicates and not args.dry_run
#   #           and not args.i_have_reviewed_the_dry_run):
#   #       logger.error("refusing to delete: run with --dry-run first, then "
#   #                    "re-run with --i-have-reviewed-the-dry-run")
#   #       return 2
#   # Making the dangerous path require an awkward, explicit flag is a real
#   # technique. The awkwardness IS the feature.
#
# EXERCISE 3 — Recursive mode
#   def scan_folder(folder, config, recursive=False):
#       if recursive:
#           paths = folder.rglob("*")
#       else:
#           paths = folder.iterdir()
#       files = []
#       for path in sorted(paths):
#           if not path.is_file() or path.name in config["ignore_names"]:
#               continue
#           ...same as before...
#       return files
#
#   # WHAT GOES WRONG with --organise --recursive:
#   #   1. You'd move files INTO category folders that your own scan then
#   #      re-discovers on a later run, shuffling them repeatedly.
#   #   2. Files from different subfolders with the same name collide.
#   #   3. You destroy the existing folder structure, which probably meant
#   #      something to whoever made it.
#   # Sensible answer: allow --recursive for --report and --find-duplicates
#   # (read-only operations), but refuse it for --organise. Encoding that
#   # refusal in the tool is better design than a warning in the README.
#
# EXERCISE 4 — Write the report as JSON and CSV
#   import csv
#   def write_report(report, path):
#       path = Path(path)
#       if path.suffix == ".json":
#           serialisable = {
#               "count": report["count"],
#               "total_size": report["total_size"],
#               "categories": report["categories"],
#               "extensions": dict(report["extensions"]),
#               "largest": report["largest"]["name"],
#           }
#           path.write_text(json.dumps(serialisable, indent=2), encoding="utf-8")
#       elif path.suffix == ".csv":
#           with open(path, "w", encoding="utf-8", newline="") as f:
#               writer = csv.writer(f)
#               writer.writerow(["category", "files", "bytes"])
#               for name, stats in sorted(report["categories"].items()):
#                   writer.writerow([name, stats["count"], stats["size"]])
#       else:
#           raise ValueError(f"unsupported output type: {path.suffix}")
#   # Note the Path objects and datetimes had to be converted - json.dumps
#   # cannot serialise them (lesson 14, mistake 7).
#
# EXERCISE 5 — Date-based folders
#   def organise_by_date(folder, files, logger, dry_run=True):
#       for record in files:
#           year = f"{record['modified']:%Y}"
#           month = f"{record['modified']:%m}"
#           subfolder = folder / year / month
#           destination = subfolder / record["name"]
#           if destination.exists():
#               logger.warning(f"skip {record['name']} - already there")
#               continue
#           if dry_run:
#               logger.info(f"WOULD MOVE {record['name']} -> {year}/{month}/")
#           else:
#               subfolder.mkdir(parents=True, exist_ok=True)
#               record["path"].rename(destination)
#
# EXERCISE 6 — A real config file
#   # filekeeper.json
#   {
#     "type_folders": {
#       "Photos": [".jpg", ".jpeg", ".png", ".heic"],
#       "Work": [".pdf", ".docx", ".xlsx"],
#       "Code": [".py", ".js", ".sql"]
#     },
#     "ignore_names": [".DS_Store"],
#     "archive_folder": "_old"
#   }
#   # then:  python3 20_automation_project.py ~/Downloads --config filekeeper.json --report
#   # load_config starts from a copy of DEFAULT_CONFIG and .update()s it with
#   # yours, so anything you leave out keeps its default.
#
# EXERCISE 7 — Undo
#   def organise_files(folder, files, config, logger, dry_run=True):
#       manifest = []
#       for record in files:
#           ...
#           if not dry_run:
#               record["path"].rename(destination)
#               manifest.append({"from": str(record["path"]),
#                                "to": str(destination)})
#       if manifest:
#           manifest_path = WORK_DIR / f"moves_{datetime.now():%Y%m%d_%H%M%S}.json"
#           manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
#           logger.info(f"undo manifest: {manifest_path.name}")
#       return len(manifest), 0
#
#   def undo_moves(manifest_path, logger, dry_run=True):
#       moves = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
#       # Reverse order matters: undo the last move first, so that if a later
#       # move depended on an earlier one you unwind cleanly.
#       for move in reversed(moves):
#           source = Path(move["to"])
#           target = Path(move["from"])
#           if not source.exists():
#               logger.warning(f"cannot undo - {source.name} is gone")
#               continue
#           if target.exists():
#               logger.warning(f"cannot undo - {target.name} already exists")
#               continue
#           if dry_run:
#               logger.info(f"WOULD RESTORE {source.name} -> {target.parent.name}/")
#           else:
#               target.parent.mkdir(parents=True, exist_ok=True)
#               source.rename(target)
#               logger.info(f"restored {source.name}")
#   # Writing the manifest BEFORE you need it is the whole trick. An undo you
#   # have to reconstruct afterwards from logs is not an undo.
#
# EXERCISE 8 — Schedule it
#   crontab -e      then add:
#       0 9 * * * /usr/bin/python3 /Users/sidd/Python/python_course/20_automation_project.py ~/Downloads --report >> ~/filekeeper_cron.log 2>&1
#
#   Field order is: minute hour day-of-month month day-of-week
#       0 9 * * *     every day at 09:00
#       */15 * * * *  every 15 minutes
#       0 9 * * 1     every Monday at 09:00
#
#   THREE THINGS THAT BITE EVERYONE THE FIRST TIME:
#     1. cron runs with a minimal PATH and environment. Use the FULL path to
#        python3 (`which python3`) and to your script.
#     2. cron has no terminal, so anything using input() hangs forever. This
#        is why lesson 04 insisted on sys.argv for unattended jobs.
#     3. Redirect output (>> file 2>&1) or you will never see the errors.
#   On macOS you may also need to grant cron Full Disk Access in
#   System Settings > Privacy & Security.


if __name__ == "__main__":
    # sys.exit() passes the return value of main() to the operating system as
    # the process's exit code.
    sys.exit(main())

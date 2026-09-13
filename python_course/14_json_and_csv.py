"""
===============================================================================
 LESSON 14 — JSON AND CSV: THE TWO FORMATS THAT RUN THE WORLD
===============================================================================

Time: about 75 minutes.
Assumes: lessons 01-13 (especially 09 dictionaries and 13 files).


-------------------------------------------------------------------------------
 THEORY: DATA HAS TO LEAVE YOUR PROGRAM SOMEHOW
-------------------------------------------------------------------------------

Your Python dictionaries and lists only exist inside a running Python process.
To save them, send them over a network, or hand them to a colleague using
Excel, they must be converted into text in an agreed format.

Two formats dominate, and they split the world neatly:

  CSV   "Comma-Separated Values". A grid: rows and columns, like a spreadsheet.
        FLAT - no nesting possible. Every value is text.
        -> spreadsheets, database exports, scientific data, financial reports
        -> this is the data-analysis format

  JSON  "JavaScript Object Notation". Nested dictionaries and lists as text.
        STRUCTURED - supports nesting, and preserves types (numbers stay
        numbers, booleans stay booleans).
        -> web APIs, config files, app settings, NoSQL databases
        -> this is the web format

CHOOSING: if your data is a table, use CSV. If it has structure and nesting,
use JSON. If you're talking to a web API, you have no choice - it's JSON.


-------------------------------------------------------------------------------
 THE KEY INSIGHT ABOUT JSON
-------------------------------------------------------------------------------

JSON maps almost perfectly onto Python types:

    JSON            PYTHON
    object {}   <-> dict
    array []    <-> list
    string      <-> str
    number      <-> int / float
    true/false  <-> True/False
    null        <-> None

So "working with a web API" is really just: receive text, convert it to a
dict, and use everything you learned in lesson 09. That's the whole trick.
"""

import json
import csv
from pathlib import Path

LINE = "-" * 70

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
WORK_DIR = HERE / "workspace"
WORK_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# PART 1 — JSON: PYTHON OBJECTS AS TEXT
# =============================================================================
print(LINE)
print("PART 1 — JSON BASICS")
print(LINE)

# FOUR FUNCTIONS, AND THE NAMING IS CONFUSING UNTIL YOU SEE THE PATTERN.
# The "s" stands for STRING:
#
#   json.dumps(obj)      object -> string        ("dump string")
#   json.loads(text)     string -> object        ("load string")
#   json.dump(obj, f)    object -> file
#   json.load(f)         file   -> object
#
# Remember: DUMP means "Python out to JSON", LOAD means "JSON in to Python".

user = {
    "name": "Sidd",
    "age": 22,
    "active": True,
    "score": 91.5,
    "tags": ["python", "beginner"],
    "address": {"city": "Mumbai", "country": "India"},
    "middle_name": None,
}

# Python -> JSON text
json_text = json.dumps(user)
print("compact JSON:")
print(" ", json_text)
print()

# indent= makes it human-readable. sort_keys= gives a stable order, which
# matters if you ever want to diff two config files in git.
print("pretty JSON:")
print(json.dumps(user, indent=2, sort_keys=True))
print()

# Note the conversions: True became true, None became null, and every key is
# now in double quotes. JSON is stricter than Python:
#   * double quotes only (no single quotes)
#   * no trailing commas
#   * no comments
#   * keys must be strings

# JSON text -> Python
restored = json.loads(json_text)
print("restored type :", type(restored).__name__)
print("restored['name']:", restored["name"])
print("nested access :", restored["address"]["city"])
print("round trip identical?", restored == user)
print()


# =============================================================================
# PART 2 — READING AND WRITING JSON FILES
# =============================================================================
print(LINE)
print("PART 2 — JSON FILES")
print(LINE)

config_path = DATA_DIR / "config.json"

# READ a JSON file - note json.load (no "s") takes the FILE object.
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

print("loaded config as a", type(config).__name__)
print("  app_name     :", config["app_name"])
print("  version      :", config["version"])
print("  debug        :", config["debug"], f"({type(config['debug']).__name__})")
print("  server port  :", config["server"]["port"])
print("  db engine    :", config["database"]["engine"])
print("  regions      :", config["allowed_regions"])
print("  first admin  :", config["admins"][0]["name"])
print()

# Notice `debug` came back as a real Python bool, and `port` as a real int -
# no conversion needed. That's JSON's advantage over CSV.

# Navigate safely when fields are optional (lesson 09's .get()):
print("  timeout      :", config.get("timeout", "not set - using default"))
print("  beta charts  :", config.get("features", {}).get("beta_charts"))
print()

# MODIFY and WRITE BACK - the standard config-editing pattern.
config["debug"] = True
config["server"]["workers"] = 8
config["features"]["beta_charts"] = True
config["last_updated"] = "2026-09-13"

out_path = WORK_DIR / "config_updated.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)

print(f"wrote {out_path.name}. First 12 lines:")
for line in out_path.read_text(encoding="utf-8").splitlines()[:12]:
    print("  ", line)
print("   ...")
print()

# pathlib one-liners for small files:
data = json.loads((DATA_DIR / "config.json").read_text(encoding="utf-8"))
print("read again via pathlib:", data["app_name"])
print()


# =============================================================================
# PART 3 — WHEN JSON GOES WRONG
# =============================================================================
print(LINE)
print("PART 3 — JSON ERRORS")
print(LINE)

# Malformed JSON raises json.JSONDecodeError (a subclass of ValueError).
broken_samples = [
    '{"name": "Sidd",}',                    # trailing comma
    "{'name': 'Sidd'}",                     # single quotes
    '{"name": "Sidd"',                      # unclosed brace
    "",                                     # empty
    "<html>404 Not Found</html>",           # an error page, not JSON at all
]

for sample in broken_samples:
    try:
        json.loads(sample)
        print(f"  {sample[:28]!r:<32} OK")
    except json.JSONDecodeError as error:
        print(f"  {sample[:28]!r:<32} {error.msg} (char {error.pos})")
print()

# That last case is real and common: an API returns an HTML error page instead
# of JSON, and your json.loads() explodes with a confusing message. Always
# wrap API parsing in try/except - lesson 21 does exactly this.

def load_json_safely(path, default=None):
    """Load JSON, returning `default` rather than raising."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"    (no file at {path.name} - using default)")
        return default
    except json.JSONDecodeError as error:
        print(f"    ({path.name} is not valid JSON: {error.msg})")
        return default

print("  missing file:", load_json_safely(DATA_DIR / "nope.json", default={}))
print()

# NOT EVERYTHING IS JSON-SERIALISABLE. Sets, dates and custom objects fail:
try:
    json.dumps({"tags": {"a", "b"}})
except TypeError as error:
    print("  sets can't be serialised:", error)
print("  fix - convert first:", json.dumps({"tags": sorted({"a", "b"})}))
print()


# =============================================================================
# PART 4 — CSV: THE SPREADSHEET FORMAT
# =============================================================================
print(LINE)
print("PART 4 — READING CSV")
print(LINE)

sales_path = DATA_DIR / "sales.csv"

# WHY NOT JUST line.split(",")? Because real CSV is subtler than it looks:
#   Smith, John,"Flat 2, High St",London
# The quoted field contains a comma that is NOT a separator. split(",") breaks
# it. The csv module handles quoting, escaping and embedded newlines correctly.
# Use it. Always.

# --- csv.reader: each row becomes a LIST ---
with open(sales_path, "r", encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)               # the first row is the column names
    first_rows = [next(reader) for _ in range(3)]

print("header    :", header)
for row in first_rows:
    print("row       :", row)
print()

# NOTE newline="" in the open() call. It's required by the csv module to handle
# line endings correctly across platforms. Just always include it.

# --- csv.DictReader: each row becomes a DICT keyed by the header ---
# THIS IS THE ONE TO USE. Accessing row["customer"] instead of row[2] is
# clearer and survives someone reordering the columns.
with open(sales_path, "r", encoding="utf-8", newline="") as f:
    orders = list(csv.DictReader(f))

print(f"loaded {len(orders)} orders")
print("first order as a dict:")
for key, value in orders[0].items():
    print(f"    {key:<12}: {value!r}")
print()

# ***** THE CSV GOLDEN RULE *****
# EVERY value from a CSV is a STRING. Look at the repr above: '12', not 12.
# You must convert before doing arithmetic, exactly like lesson 04's form data.

first = orders[0]
print("  quantity as text :", repr(first["quantity"]))
print("  text * 2 (wrong) :", first["quantity"] * 2)
print("  int() * 2 (right):", int(first["quantity"]) * 2)
print()


# =============================================================================
# PART 5 — A REAL CSV ANALYSIS
# =============================================================================
print(LINE)
print("PART 5 — ANALYSING SALES DATA")
print(LINE)

# Step 1 - load and CONVERT TYPES at the boundary. Do this once, up front, and
# the rest of your code can trust the data.
def load_orders(path):
    """Read the sales CSV into a list of dicts with proper types."""
    orders = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            try:
                row["order_id"] = int(row["order_id"])
                row["quantity"] = int(row["quantity"])
                row["unit_price"] = float(row["unit_price"])
                row["total"] = row["quantity"] * row["unit_price"]
            except ValueError as error:
                print(f"  skipping malformed row {row.get('order_id')}: {error}")
                continue
            orders.append(row)
    return orders


orders = load_orders(sales_path)
paid = [o for o in orders if o["status"] == "paid"]

print(f"{len(orders)} orders, {len(paid)} paid\n")

# Step 2 - aggregate with the dictionary patterns from lesson 09.
revenue_by_region = {}
revenue_by_product = {}
revenue_by_customer = {}

for order in paid:
    for field, target in (("region", revenue_by_region),
                          ("product", revenue_by_product),
                          ("customer", revenue_by_customer)):
        key = order[field]
        target[key] = target.get(key, 0) + order["total"]

def show(title, totals, top=None):
    print(f"  {title}")
    rows = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)
    for name, amount in rows[:top]:
        bar = "#" * int(amount / 25)
        print(f"    {name:<16}{amount:>10,.2f}  {bar}")
    print(f"    {'TOTAL':<16}{sum(totals.values()):>10,.2f}\n")

show("Revenue by region", revenue_by_region)
show("Revenue by product", revenue_by_product)
show("Top 3 customers", revenue_by_customer, top=3)

# Step 3 - some headline numbers.
total_revenue = sum(o["total"] for o in paid)
biggest = max(paid, key=lambda o: o["total"])
print(f"  Total paid revenue : {total_revenue:,.2f}")
print(f"  Average order      : {total_revenue / len(paid):,.2f}")
print(f"  Largest order      : #{biggest['order_id']} "
      f"{biggest['customer']} {biggest['total']:,.2f}")
print(f"  Units sold         : {sum(o['quantity'] for o in paid):,}")
print(f"  Statuses           : {sorted({o['status'] for o in orders})}")
print()


# =============================================================================
# PART 6 — WRITING CSV
# =============================================================================
print(LINE)
print("PART 6 — WRITING CSV")
print(LINE)

# DictWriter is the counterpart of DictReader.
summary_path = WORK_DIR / "revenue_by_region.csv"

with open(summary_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["region", "revenue", "share"])
    writer.writeheader()                            # don't forget this line
    for region, amount in sorted(revenue_by_region.items()):
        writer.writerow({
            "region": region,
            "revenue": round(amount, 2),
            "share": f"{amount / total_revenue:.1%}",
        })

print(f"wrote {summary_path.name}:")
print(summary_path.read_text(encoding="utf-8"))

# csv.writer with plain lists, if you don't need the dict structure:
rows_path = WORK_DIR / "top_orders.csv"
with open(rows_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "customer", "total"])
    for order in sorted(paid, key=lambda o: o["total"], reverse=True)[:5]:
        writer.writerow([order["order_id"], order["customer"],
                         round(order["total"], 2)])

print(f"wrote {rows_path.name}:")
print(rows_path.read_text(encoding="utf-8"))

# The quoting is handled for you - a customer called O'Brien, Jr. would be
# quoted correctly with no effort on your part.


# =============================================================================
# PART 7 — CONVERTING BETWEEN THE TWO
# =============================================================================
print(LINE)
print("PART 7 — CSV <-> JSON")
print(LINE)

# A genuinely common task: an API gives you JSON, but your colleague wants a
# spreadsheet. Or a CSV export needs feeding to a web service.

# CSV -> JSON
json_out = WORK_DIR / "orders.json"
slim = [
    {
        "id": o["order_id"],
        "customer": o["customer"],
        "region": o["region"],
        "total": round(o["total"], 2),
        "paid": o["status"] == "paid",
    }
    for o in orders
]
json_out.write_text(json.dumps(slim, indent=2), encoding="utf-8")
print(f"CSV -> JSON: wrote {len(slim)} records to {json_out.name}")
print("  first record:", json.dumps(slim[0]))
print()

# JSON -> CSV. This only works if the JSON is FLAT. Nested structures must be
# flattened first, because CSV has no way to represent nesting.
csv_out = WORK_DIR / "orders_from_json.csv"
loaded = json.loads(json_out.read_text(encoding="utf-8"))

with open(csv_out, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(loaded[0].keys()))
    writer.writeheader()
    writer.writerows(loaded)

print(f"JSON -> CSV: wrote {csv_out.name}")
print("  first 3 lines:")
for line in csv_out.read_text(encoding="utf-8").splitlines()[:3]:
    print("   ", line)
print()

# Flattening nested JSON for CSV export:
nested = {"name": "Sidd", "address": {"city": "Mumbai", "country": "India"}}
flat = {
    "name": nested["name"],
    "address_city": nested["address"]["city"],
    "address_country": nested["address"]["country"],
}
print("  flattened for CSV:", flat)
print()


# =============================================================================
# PART 8 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 8 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: forgetting everything from CSV is a string. int("12") first.

# MISTAKE 2: using split(",") instead of the csv module. Breaks on quoted
#   fields containing commas.

# MISTAKE 3: omitting newline="" when opening a CSV. On Windows you get a blank
#   line between every row.

# MISTAKE 4: forgetting writer.writeheader(), producing a headerless file that
#   DictReader then misreads.

# MISTAKE 5: confusing dump/dumps and load/loads. The "s" version works with
#   STRINGS; the plain version works with FILES.

# MISTAKE 6: assuming an API returned JSON. Check for JSONDecodeError - the
#   response may be an HTML error page.

# MISTAKE 7: trying to serialise a set, a date or a custom object.
#   Convert to a list/string first, or pass a `default=` function to dumps().
print("  serialising a set via default=:",
      json.dumps({"tags": {"b", "a"}}, default=sorted))

# MISTAKE 8: writing JSON without indent for a file humans will read, or WITH
#   indent for data sent over a network (wasted bytes).

# MISTAKE 9: losing leading zeros. A CSV of "007" becomes 7 if you int() it -
#   and Excel does this to phone numbers and postcodes constantly. If it's an
#   identifier rather than a quantity, keep it as a string.
print()


# =============================================================================
# EXERCISES
# =============================================================================
#
# EXERCISE 1 — JSON round trip
#   Build a dict describing three books (title, author, year, tags list).
#   Write it to workspace/books.json with indent=2, read it back, and print
#   each book on one line. Confirm the year is an int, not a string.
#
# EXERCISE 2 — Config editor
#   Load data/config.json. Write a function set_value(config, path, value)
#   where path is like "server.port", which updates the nested value. Use it
#   to change server.port to 9000 and features.dark_mode to False, then save.
#
# EXERCISE 3 — CSV summary
#   From data/sales.csv, print: total units sold per product, the number of
#   orders per status, and the month with the highest revenue (the date field
#   starts "2024-01" etc., so slice the first 7 characters).
#
# EXERCISE 4 — Filtered export
#   Write a new CSV into workspace/ containing only the EU orders, with columns
#   order_id, customer, product, total - where total is quantity * unit_price
#   rounded to 2 decimals.
#
# EXERCISE 5 — Per-customer report
#   Produce a JSON file where each key is a customer name and the value is a
#   dict with their order_count, total_spent and favourite_product.
#
# EXERCISE 6 — Handle a broken file
#   Create workspace/bad.json containing invalid JSON. Write a loader that
#   reports exactly what's wrong (message and character position) instead of
#   crashing.
#
# EXERCISE 7 — Merge two CSVs
#   Write a second small CSV of product categories (product,category). Join it
#   to the sales data so your report can show revenue by CATEGORY.
#   Hint: load the categories into a dict first, then look each product up.
#
# EXERCISE 8 — Detect bad rows
#   Write a validator over data/sales.csv reporting any row where: quantity
#   isn't a positive integer, unit_price isn't a positive number, or status
#   isn't one of paid/pending/refunded. Print a line per problem.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   books = [
#       {"title": "Dune", "author": "Herbert", "year": 1965, "tags": ["scifi"]},
#       {"title": "Emma", "author": "Austen", "year": 1815, "tags": ["classic"]},
#       {"title": "Ubik", "author": "Dick", "year": 1969, "tags": ["scifi"]},
#   ]
#   path = WORK_DIR / "books.json"
#   path.write_text(json.dumps(books, indent=2), encoding="utf-8")
#   for b in json.loads(path.read_text(encoding="utf-8")):
#       print(f"{b['title']} by {b['author']} ({b['year']}) {type(b['year'])}")
#
# EXERCISE 2
#   def set_value(config, dotted_path, value):
#       keys = dotted_path.split(".")
#       target = config
#       for key in keys[:-1]:
#           target = target[key]
#       target[keys[-1]] = value
#   cfg = json.loads((DATA_DIR / "config.json").read_text(encoding="utf-8"))
#   set_value(cfg, "server.port", 9000)
#   set_value(cfg, "features.dark_mode", False)
#   (WORK_DIR / "cfg.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
#
# EXERCISE 3
#   units, statuses, by_month = {}, {}, {}
#   for o in orders:
#       units[o["product"]] = units.get(o["product"], 0) + o["quantity"]
#       statuses[o["status"]] = statuses.get(o["status"], 0) + 1
#       month = o["date"][:7]
#       by_month[month] = by_month.get(month, 0) + o["total"]
#   print(units, statuses)
#   print(max(by_month, key=by_month.get))
#
# EXERCISE 4
#   eu = [o for o in orders if o["region"] == "EU"]
#   with open(WORK_DIR / "eu_orders.csv", "w", encoding="utf-8", newline="") as f:
#       w = csv.DictWriter(f, fieldnames=["order_id", "customer", "product", "total"])
#       w.writeheader()
#       for o in eu:
#           w.writerow({"order_id": o["order_id"], "customer": o["customer"],
#                       "product": o["product"], "total": round(o["total"], 2)})
#
# EXERCISE 5
#   report = {}
#   for o in orders:
#       entry = report.setdefault(o["customer"],
#                                 {"order_count": 0, "total_spent": 0.0, "products": {}})
#       entry["order_count"] += 1
#       entry["total_spent"] = round(entry["total_spent"] + o["total"], 2)
#       entry["products"][o["product"]] = entry["products"].get(o["product"], 0) + 1
#   for name, entry in report.items():
#       entry["favourite_product"] = max(entry["products"], key=entry["products"].get)
#       del entry["products"]
#   (WORK_DIR / "customers.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
#
# EXERCISE 6
#   bad = WORK_DIR / "bad.json"
#   bad.write_text('{"a": 1,}', encoding="utf-8")
#   try:
#       json.loads(bad.read_text(encoding="utf-8"))
#   except json.JSONDecodeError as e:
#       print(f"{e.msg} at line {e.lineno} column {e.colno} (char {e.pos})")
#
# EXERCISE 7
#   cat_path = WORK_DIR / "categories.csv"
#   cat_path.write_text("product,category\nWidget,Hardware\nGadget,Hardware\n"
#                       "Doohickey,Consumable\nSprocket,Machinery\n", encoding="utf-8")
#   with open(cat_path, encoding="utf-8", newline="") as f:
#       categories = {r["product"]: r["category"] for r in csv.DictReader(f)}
#   by_category = {}
#   for o in paid:
#       cat = categories.get(o["product"], "Unknown")
#       by_category[cat] = by_category.get(cat, 0) + o["total"]
#   print(by_category)
#
# EXERCISE 8
#   VALID_STATUSES = {"paid", "pending", "refunded"}
#   with open(sales_path, encoding="utf-8", newline="") as f:
#       for line_no, row in enumerate(csv.DictReader(f), start=2):
#           problems = []
#           if not row["quantity"].isdigit() or int(row["quantity"]) <= 0:
#               problems.append(f"bad quantity {row['quantity']!r}")
#           try:
#               if float(row["unit_price"]) <= 0:
#                   problems.append("non-positive price")
#           except ValueError:
#               problems.append(f"bad price {row['unit_price']!r}")
#           if row["status"] not in VALID_STATUSES:
#               problems.append(f"bad status {row['status']!r}")
#           if problems:
#               print(f"line {line_no}: {', '.join(problems)}")


print("=" * 70)
print("Lesson 14 complete. Next: 15_modules_and_packages.py")
print("=" * 70)

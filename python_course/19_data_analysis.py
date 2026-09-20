"""
===============================================================================
 LESSON 19 — DATA ANALYSIS FOUNDATIONS
===============================================================================

Time: about 85 minutes (there's a good place for a break halfway).
Assumes: lessons 01-18 (especially 09 dictionaries, 14 CSV, 18 statistics).


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. load a CSV into clean, correctly-typed records                (PART 1)
  2. describe a dataset before trusting it                         (PART 2)
  3. group records and total them up - the heart of analysis       (PART 3)
  4. see how numbers change month by month                         (PART 4)
  5. draw bar charts and histograms with plain text                (PART 5)
  6. combine two datasets, and save your results                   (PARTS 6-7)

NEW WORDS - come back here whenever you forget one:

  dataset       all the data you're analysing - here, a list of dicts
  record        one row of it - one dict, like one order
  column        one field across every record: "region", "quantity"
  clean         fix types and reject broken rows before analysing
  aggregate     boil many values down to one: a total, a count, an average
  group by      split records into groups (by region, by month...) and
                aggregate each group
  outlier       a value far away from the rest - an error, or your best
                customer. Always look before removing one
  median        the middle value when sorted - less fooled by outliers than
                the mean (average)
  time series   values over time: revenue per month
  join          attach data from a second dataset, matched by a shared key
  pandas        the popular data library that does all of this in one-liners
                (PART 8 shows it)

Every tool here is from lessons 06-18. The only new thing is putting them
together.


-------------------------------------------------------------------------------
 THEORY: WHAT DATA ANALYSIS ACTUALLY IS
-------------------------------------------------------------------------------

Stripped of jargon, every data analysis is the same five steps:

  1. LOAD      get the data into memory
  2. CLEAN     fix types, handle missing values, remove nonsense
  3. EXPLORE   how many rows? what's the range? what's normal?
  4. AGGREGATE group, count, sum, average - answer the actual question
  5. PRESENT   a table, a chart, a summary someone can act on

People associate this work with pandas, and pandas is genuinely excellent. But
doing it once with plain Python is worth far more to you right now, because:

  * pandas hides these steps behind one-liners. If you've never done them by
    hand you won't know what a one-liner is doing when it misbehaves.
  * A huge amount of real analysis happens on data too small or too oddly
    shaped to justify pandas.
  * Every pandas concept (a DataFrame, groupby, a join) maps directly onto
    something you'll build manually in this lesson.

So: this lesson does it the long way on purpose. PART 8 shows what the same
work looks like in pandas, so the transition is obvious when you're ready.


-------------------------------------------------------------------------------
 THE MENTAL MODEL
-------------------------------------------------------------------------------

    A DATASET is a list of records.
    A RECORD  is a dict mapping column names to values.

        [{"region": "EU", "amount": 249.99}, {"region": "AS", ...}, ...]

That's it. Everything else is loops and dictionaries over that shape.
"""

import csv
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

LINE = "-" * 70

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
WORK_DIR = HERE / "workspace"
WORK_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# PART 1 — LOAD AND CLEAN
# =============================================================================
print(LINE)
print("PART 1 — LOADING AND CLEANING")
print(LINE)

# THE MOST IMPORTANT HABIT IN DATA WORK: convert types once, at the boundary,
# and record anything you had to reject. Never analyse raw strings.

def load_sales(path):
    """Load the sales CSV into clean, typed records.

    Returns (records, problems) so nothing fails silently.
    """
    records = []
    problems = []

    with open(path, "r", encoding="utf-8", newline="") as f:
        # start=2 because line 1 of the file is the header
        for line_number, row in enumerate(csv.DictReader(f), start=2):
            try:
                record = {
                    "order_id": int(row["order_id"]),
                    "date": datetime.strptime(row["date"], "%Y-%m-%d").date(),
                    "customer": row["customer"].strip(),
                    "region": row["region"].strip().upper(),
                    "product": row["product"].strip(),
                    "quantity": int(row["quantity"]),
                    "unit_price": float(row["unit_price"]),
                    "status": row["status"].strip().lower(),
                }
            except (ValueError, KeyError) as error:
                problems.append((line_number, str(error)))
                continue

            # Derived columns - calculate once here, use everywhere later.
            record["revenue"] = round(record["quantity"] * record["unit_price"], 2)
            record["month"] = record["date"].strftime("%Y-%m")    # e.g. "2024-03"
            record["is_revenue"] = record["status"] == "paid"      # True / False
            records.append(record)

    return records, problems


sales, problems = load_sales(DATA_DIR / "sales.csv")

print(f"  loaded  : {len(sales)} records")
print(f"  rejected: {len(problems)}")
for line_number, reason in problems:
    print(f"    line {line_number}: {reason}")

print("\n  first record:")
for key, value in sales[0].items():
    print(f"    {key:<12}: {value!r}")
print()

# TRY IT NOW (1 minute):
#   Print the customer and revenue of the LAST record: sales[-1].


# =============================================================================
# PART 2 — EXPLORE: KNOW YOUR DATA BEFORE YOU TRUST IT
# =============================================================================
print(LINE)
print("PART 2 — EXPLORATORY SUMMARY")
print(LINE)

# Before answering any question, describe the dataset. Half of all analysis
# errors are caught right here - wrong row counts, unexpected categories,
# impossible values.

def describe_dataset(records):
    """Print a profile of the dataset, column by column."""
    print(f"  rows: {len(records)}   columns: {len(records[0])}")
    print()
    print(f"  {'column':<12}{'type':<10}{'unique':>8}{'missing':>9}  {'summary'}")
    print("  " + "-" * 68)

    for column in records[0]:
        values = [r[column] for r in records]          # every value in this column
        missing = sum(1 for v in values if v is None or v == "")
        unique = len(set(values))
        kind = type(values[0]).__name__

        # Numbers get min/max/mean; everything else gets its most common values.
        # (bool counts as a number in Python, so it's excluded on purpose.)
        if isinstance(values[0], (int, float)) and not isinstance(values[0], bool):
            summary = (f"min {min(values):,.2f}  max {max(values):,.2f}  "
                       f"mean {statistics.mean(values):,.2f}")
        else:
            common = Counter(values).most_common(2)
            summary = ", ".join(f"{v}({c})" for v, c in common)
            if unique > 2:
                summary += ", ..."

        print(f"  {column:<12}{kind:<10}{unique:>8}{missing:>9}  {summary[:34]}")


describe_dataset(sales)
print()

# Numeric distribution - are there outliers hiding in here?
revenues = [r["revenue"] for r in sales]
mean = statistics.mean(revenues)
sd = statistics.stdev(revenues)
q1, median, q3 = statistics.quantiles(revenues)    # the quarter points

print("  revenue distribution:")
print(f"    min {min(revenues):>10,.2f}")
print(f"    Q1  {q1:>10,.2f}")
print(f"    med {median:>10,.2f}")
print(f"    Q3  {q3:>10,.2f}")
print(f"    max {max(revenues):>10,.2f}")
print(f"    mean {mean:>9,.2f}   stdev {sd:,.2f}")

# An outlier here = more than 2 standard deviations away from the mean.
outliers = [r for r in sales if abs(r["revenue"] - mean) > 2 * sd]
print(f"\n  outliers (>2 standard deviations from the mean): {len(outliers)}")
for record in outliers:
    print(f"    order {record['order_id']}: {record['product']} "
          f"x{record['quantity']} = {record['revenue']:,.2f}")

# NOTE: an outlier is not automatically an error. It might be your best
# customer. Always LOOK at them before deciding to exclude anything - silently
# dropping real data is how analyses end up lying.
print()


# =============================================================================
# PART 3 — GROUPING AND AGGREGATION
# =============================================================================
print(LINE)
print("PART 3 — GROUP BY")
print(LINE)

# "Group by X, then calculate Y" is the core operation of all data analysis.
# Here it is written generically, once.

def group_by(records, key_field):
    """Split records into a dict of key -> list of records."""
    groups = defaultdict(list)          # lesson 18: missing keys start as []
    for record in records:
        groups[record[key_field]].append(record)
    return dict(groups)


def aggregate(groups, value_field):
    """Turn groups into a summary dict of statistics per group."""
    summary = {}
    for key, group in groups.items():
        values = [r[value_field] for r in group]
        summary[key] = {
            "count": len(values),
            "total": round(sum(values), 2),
            "mean": round(statistics.mean(values), 2),
            "min": min(values),
            "max": max(values),
        }
    return summary


def total_of(pair):
    """For sorting (key, summary) pairs by their total."""
    return pair[1]["total"]


paid = [r for r in sales if r["is_revenue"]]

for field in ("region", "product", "status"):
    # Status is the one field where we want EVERY order, not just paid ones -
    # otherwise the only status left would be "paid".
    if field == "status":
        records_to_use = sales
    else:
        records_to_use = paid
    summary = aggregate(group_by(records_to_use, field), "revenue")

    print(f"  BY {field.upper()}")
    print(f"    {'key':<14}{'n':>4}{'total':>12}{'mean':>10}{'max':>10}")
    print("    " + "-" * 50)
    for key, row in sorted(summary.items(), key=total_of, reverse=True):
        print(f"    {str(key):<14}{row['count']:>4}{row['total']:>12,.2f}"
              f"{row['mean']:>10,.2f}{row['max']:>10,.2f}")
    print()

# Those two small functions replaced what would otherwise be three near-identical
# blocks of code. This is exactly what pandas' .groupby().agg() does for you.

# TRY IT NOW (2 minutes):
#   Print aggregate(group_by(paid, "customer"), "revenue") and find the
#   customer with the biggest total by eye.


# =============================================================================
# PART 4 — TIME SERIES: TRENDS OVER TIME
# =============================================================================
print(LINE)
print("PART 4 — TREND OVER TIME")
print(LINE)

monthly = aggregate(group_by(paid, "month"), "revenue")
months = sorted(monthly)               # "2024-01", "2024-02", ... in order

print(f"  {'month':<10}{'orders':>8}{'revenue':>12}{'change':>10}")
print("  " + "-" * 42)
previous = None
for month in months:
    row = monthly[month]
    if previous is None:                # the first month has nothing to compare to
        change = "     -"
    else:
        pct = (row["total"] - previous) / previous
        change = f"{pct:>+9.1%}"        # the + shows a sign on rises too
    print(f"  {month:<10}{row['count']:>8}{row['total']:>12,.2f}{change}")
    previous = row["total"]

total_revenue = sum(monthly[m]["total"] for m in months)
first_month_total = monthly[months[0]]["total"]
last_month_total = monthly[months[-1]]["total"]
growth = (last_month_total - first_month_total) / first_month_total
print("  " + "-" * 42)
print(f"  {'TOTAL':<10}{sum(monthly[m]['count'] for m in months):>8}{total_revenue:>12,.2f}")
print(f"\n  overall change first to last month: {growth:+.1%}")

# Running total (cumulative revenue) - the shape of every "progress to target"
# chart you've ever seen:
print("\n  cumulative revenue:")
running = 0
for month in months:
    running += monthly[month]["total"]
    print(f"    {month}  {running:>10,.2f}  {'#' * int(running / 100)}")
print()


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. Load, clean, explore, group - that's the core of
#  data analysis, done. After the break: charts, joins and saving results.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 5 — CHARTS IN THE TERMINAL
# =============================================================================
print(LINE)
print("PART 5 — TEXT VISUALISATION")
print(LINE)

# You don't need matplotlib to SEE your data. A text bar chart takes four lines
# and works over SSH, in logs, and in an email.

def value_of(pair):
    return pair[1]


def bar_chart(data, title, width=40, symbol="#"):
    """Draw a horizontal bar chart from a dict of label -> number."""
    if not data:
        print(f"  {title}: no data")
        return

    largest = max(data.values())
    label_width = max(len(str(k)) for k in data)     # the longest label

    print(f"  {title}")
    for label, value in sorted(data.items(), key=value_of, reverse=True):
        if largest:
            filled = int(value / largest * width)    # the biggest bar is full width
        else:
            filled = 0
        bar = symbol * filled
        # {bar:<{width}} pads the bar to `width` characters - a width that is
        # itself a variable, so it goes in its own inner braces.
        print(f"    {str(label):<{label_width}} |{bar:<{width}}| {value:>10,.2f}")
    print()


def totals_only(summary):
    """Turn aggregate()'s output into a simple dict of key -> total."""
    result = {}
    for key, row in summary.items():
        result[key] = row["total"]
    return result


bar_chart(totals_only(aggregate(group_by(paid, "region"), "revenue")),
          "Revenue by region")

bar_chart(totals_only(aggregate(group_by(paid, "product"), "revenue")),
          "Revenue by product")

bar_chart(totals_only(monthly), "Revenue by month")


def histogram(values, buckets=6, width=30):
    """Show the distribution of a list of numbers.

    It splits the range from lowest to highest into equal buckets, counts how
    many values land in each, and draws a bar per bucket.
    """
    low = min(values)
    high = max(values)
    span = (high - low) / buckets or 1      # the width of each bucket (never 0)

    counts = [0] * buckets                  # one counter per bucket
    for v in values:
        index = int((v - low) / span)       # which bucket does v fall in?
        if index >= buckets:                # the very highest value lands just
            index = buckets - 1             # past the end - put it in the last one
        counts[index] += 1

    biggest_count = max(counts)
    print(f"  Distribution of {len(values)} values")
    for index in range(buckets):
        start = low + index * span
        end = start + span
        bar = "#" * int(counts[index] / biggest_count * width)
        print(f"    {start:>8,.0f}-{end:<8,.0f} |{bar:<{width}}| {counts[index]}")
    print()


histogram(revenues)


# =============================================================================
# PART 6 — JOINING TWO DATASETS
# =============================================================================
print(LINE)
print("PART 6 — JOINING DATA")
print(LINE)

# Real analysis nearly always combines sources: sales data plus product
# categories, orders plus customer details. The technique: build a LOOKUP DICT
# from the second dataset, then attach values while looping the first.

product_info = {
    "Widget":    {"category": "Hardware",   "cost": 2.10},
    "Gadget":    {"category": "Hardware",   "cost": 7.00},
    "Doohickey": {"category": "Consumable", "cost": 0.40},
    "Sprocket":  {"category": "Machinery",  "cost": 52.00},
}

# The join - and note the .get() default, so an unknown product doesn't crash
# the whole report.
for record in sales:
    info = product_info.get(record["product"], {"category": "Unknown", "cost": 0})
    record["category"] = info["category"]
    record["cost"] = round(info["cost"] * record["quantity"], 2)
    record["profit"] = round(record["revenue"] - record["cost"], 2)

paid = [r for r in sales if r["is_revenue"]]        # refresh after the join

print(f"  {'category':<14}{'revenue':>12}{'cost':>10}{'profit':>10}{'margin':>9}")
print("  " + "-" * 55)
for category, group in sorted(group_by(paid, "category").items()):
    revenue = sum(r["revenue"] for r in group)
    cost = sum(r["cost"] for r in group)
    profit = revenue - cost
    margin = profit / revenue if revenue else 0      # guard against dividing by 0
    print(f"  {category:<14}{revenue:>12,.2f}{cost:>10,.2f}"
          f"{profit:>10,.2f}{margin:>9.1%}")

total_rev = sum(r["revenue"] for r in paid)
total_profit = sum(r["profit"] for r in paid)
print("  " + "-" * 55)
print(f"  {'TOTAL':<14}{total_rev:>12,.2f}"
      f"{total_rev - total_profit:>10,.2f}{total_profit:>10,.2f}"
      f"{total_profit / total_rev:>9.1%}")
print()

# Now a question you couldn't answer before the join: which product makes the
# most money, as opposed to the most revenue?
by_revenue = {}
by_profit = {}
for product, group in group_by(paid, "product").items():
    by_revenue[product] = sum(r["revenue"] for r in group)
    by_profit[product] = sum(r["profit"] for r in group)

# max(a_dict, key=a_dict.get) = "the KEY whose VALUE is biggest"
print(f"  highest revenue: {max(by_revenue, key=by_revenue.get)}")
print(f"  highest profit : {max(by_profit, key=by_profit.get)}")
print()


# =============================================================================
# PART 7 — EXPORTING THE ANALYSIS
# =============================================================================
print(LINE)
print("PART 7 — SAVING RESULTS")
print(LINE)

# An analysis nobody can read is not finished. Write it out.

report_path = WORK_DIR / "sales_analysis.csv"
with open(report_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["month", "orders", "revenue",
                                           "profit", "avg_order"])
    writer.writeheader()
    for month in months:
        group = [r for r in paid if r["month"] == month]
        revenue = sum(r["revenue"] for r in group)
        writer.writerow({
            "month": month,
            "orders": len(group),
            "revenue": round(revenue, 2),
            "profit": round(sum(r["profit"] for r in group), 2),
            "avg_order": round(revenue / len(group), 2),
        })

print(f"  wrote {report_path.name}")
print(report_path.read_text(encoding="utf-8"))

# A plain-text summary for emailing. Work out each figure first, then write.
region_totals = totals_only(aggregate(group_by(paid, "region"), "revenue"))
best_region = max(region_totals, key=region_totals.get)
best_month = max(months, key=lambda m: monthly[m]["total"])
first_date = min(r["date"] for r in sales)
last_date = max(r["date"] for r in sales)
distinct_buyers = len({r["customer"] for r in sales})

summary_lines = [
    "SALES ANALYSIS SUMMARY",
    "=" * 46,
    f"Period          : {first_date} to {last_date}",
    f"Orders          : {len(sales)} ({len(paid)} paid)",
    f"Revenue         : {total_rev:,.2f}",
    f"Profit          : {total_profit:,.2f} ({total_profit / total_rev:.1%} margin)",
    f"Average order   : {total_rev / len(paid):,.2f}",
    f"Best region     : {best_region}",
    f"Best month      : {best_month}",
    f"Distinct buyers : {distinct_buyers}",
]
summary_path = WORK_DIR / "sales_summary.txt"
summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

print(f"  wrote {summary_path.name}:\n")
print(summary_path.read_text(encoding="utf-8"))


# =============================================================================
# PART 8 — WHAT THIS LOOKS LIKE IN PANDAS
# =============================================================================
print(LINE)
print("PART 8 — THE PANDAS VERSION (for later)")
print(LINE)

# Everything above, in the library you'll eventually use. Install it with:
#     python3 -m pip install pandas matplotlib
#
#     import pandas as pd
#
#     # PART 1 - load and clean
#     df = pd.read_csv("data/sales.csv", parse_dates=["date"])
#     df["revenue"] = df["quantity"] * df["unit_price"]
#     df["month"] = df["date"].dt.to_period("M")
#
#     # PART 2 - explore
#     df.info()
#     df.describe()
#     df.head()
#
#     # PART 3 - group and aggregate
#     paid = df[df["status"] == "paid"]
#     paid.groupby("region")["revenue"].agg(["count", "sum", "mean", "max"])
#
#     # PART 4 - time series
#     monthly = paid.groupby("month")["revenue"].sum()
#     monthly.pct_change()
#
#     # PART 6 - join
#     products = pd.DataFrame(product_info).T
#     df = df.merge(products, left_on="product", right_index=True)
#
#     # PART 5 - charts (matplotlib)
#     monthly.plot(kind="bar", title="Revenue by month")
#
#     # PART 7 - export
#     monthly.to_csv("workspace/monthly.csv")
#
# Notice every line maps onto something you just built by hand. `groupby` IS
# your group_by(). `agg` IS your aggregate(). `merge` IS your lookup dict. You
# now understand what the shortcuts are shortcutting - which means when a
# result looks wrong, you'll know where to look.
print("  (see the commented pandas translation in this section's source)")
print()


# =============================================================================
# PART 9 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 9 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: analysing without cleaning. Strings that look like numbers produce
#   silently wrong sums.

# MISTAKE 2: ignoring rejected rows. If 30% of your data failed to parse, every
#   conclusion is wrong. Always count and report what you dropped.

# MISTAKE 3: including refunded/cancelled records in revenue. Decide what
#   counts, write it down, and filter explicitly.

# MISTAKE 4: mean when you need median. One huge order drags the mean upward.
#   Skewed data -> use the median.
print(f"  revenue mean {mean:,.2f} vs median {median:,.2f} "
      f"- a {abs(mean - median) / median:.0%} difference")

# MISTAKE 5: dropping outliers without looking at them.

# MISTAKE 6: percentages of tiny samples. "50% growth" from 2 to 3 orders is
#   noise. Always show the underlying counts.

# MISTAKE 7: forgetting timezones and date formats. 03/04/2024 is March 4th in
#   the US and April 3rd in the UK. Use ISO dates (YYYY-MM-DD) everywhere.

# MISTAKE 8: no reproducibility. If your analysis is a series of manual edits,
#   you can't re-run it next month. A script can be re-run in one second.
print()


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * A dataset is a list of dicts. Load it, convert types ONCE, and keep a
#     list of rejected rows.
#   * Describe the data (counts, ranges, outliers) before answering questions.
#   * group_by + aggregate answers "total/average per region/product/month".
#   * Compare months with percentage change; add up a running total.
#   * Text bar charts need no libraries.
#   * Join datasets with a lookup dict and .get() with a default.
#   * Save results to CSV and a text summary - an analysis nobody sees is
#     unfinished.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. Why convert types when LOADING, rather than later?
#   Q2. What does group_by(paid, "region") give you?
#   Q3. One order is 10x bigger than the rest. Mean or median for "a typical
#       order"?
#   Q4. How do you attach each product's category to the sales records?
#   Q5. Revenue went from 2 orders to 3. Is "+50%" meaningful?
#
# ANSWERS
#   A1. So every later step can trust the data - and bad rows are caught in
#       one place.
#   A2. A dict: each region -> the list of paid records in that region.
#   A3. Median - the big order drags the mean up.
#   A4. Build a lookup dict (product -> info), then loop the sales and read
#       product_info.get(record["product"], default).
#   A5. Not really - the sample is tiny. Show the counts alongside.


# =============================================================================
# EXERCISES
# =============================================================================
#
# WARM-UP A (easy) — How big?
#   Print how many records are in `sales`, and how many are in `paid`.
#
# WARM-UP B (easy) — One record
#   Print the customer, product and revenue of the first record.
#
# WARM-UP C (easy) — Total it
#   Print the total revenue of all PAID orders, using sum() and a generator.
#
# EXERCISE 1 (medium) — Customer analysis
#   Produce a per-customer report: order count, total revenue, average order
#   value, favourite product, and first/last order date. Sort by total spend.
#
# EXERCISE 2 (medium) — Retention question
#   Which customers ordered in more than one month? Which ordered in every
#   month present in the data?
#
# EXERCISE 3 (medium) — Product performance
#   For each product: units sold, revenue, profit, margin, and its share of
#   total revenue as a percentage. Add a bar chart of margins.
#
# EXERCISE 4 (medium) — Failed orders
#   Analyse the non-paid orders: how much revenue is pending vs refunded, which
#   products and regions are worst affected, and what percentage of total
#   potential revenue is lost.
#
# EXERCISE 5 (challenge) — Your own generic tool
#   Write pivot(records, row_field, column_field, value_field) producing a
#   two-dimensional summary - e.g. regions down the side, months across the
#   top, revenue in the cells. Print it as a table.
#
# EXERCISE 6 (medium) — Moving average
#   Calculate a 2-month moving average of revenue and print it alongside the
#   actual monthly figures. Explain what it smooths out.
#
# EXERCISE 7 (medium) — Data quality report
#   Write check_quality(records) that reports: duplicate order_ids, negative
#   quantities or prices, and any status value outside the known set.
#
# EXERCISE 8 (challenge) — Analyse your own data
#   Export something real from your own life - a bank statement, Spotify
#   history, a spreadsheet from work - and run this lesson's pipeline over it.
#   Real data is messy in ways sample data never is, and that's the point.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   print(len(sales), len(paid))
#
# WARM-UP B
#   first = sales[0]
#   print(first["customer"], first["product"], first["revenue"])
#
# WARM-UP C
#   print(sum(r["revenue"] for r in paid))
#
# EXERCISE 1
#   customer_rows = []
#   for customer, group in group_by(paid, "customer").items():
#       revenue = sum(r["revenue"] for r in group)
#       favourite = Counter(r["product"] for r in group).most_common(1)[0][0]
#       first_date = min(r["date"] for r in group)
#       last_date = max(r["date"] for r in group)
#       customer_rows.append((revenue, customer, len(group), favourite,
#                             first_date, last_date))
#   for revenue, customer, count, favourite, first_date, last_date in sorted(
#           customer_rows, reverse=True):      # tuples sort by their FIRST item
#       print(f"{customer:<16}{count:>3} orders {revenue:>10,.2f} "
#             f"avg {revenue / count:>8,.2f} likes {favourite} "
#             f"({first_date} to {last_date})")
#   (.most_common(1)[0][0] = "the top (item, count) pair, then its item".)
#
# EXERCISE 2
#   all_months = {r["month"] for r in sales}
#   for customer, group in group_by(sales, "customer").items():
#       their_months = {r["month"] for r in group}
#       if len(their_months) > 1:
#           print("repeat customer:", customer)
#       if their_months == all_months:
#           print("ordered every month:", customer)
#
# EXERCISE 3
#   total = sum(r["revenue"] for r in paid)
#   margins = {}
#   for product, group in group_by(paid, "product").items():
#       revenue = sum(r["revenue"] for r in group)
#       profit = sum(r["profit"] for r in group)
#       units = sum(r["quantity"] for r in group)
#       margins[product] = profit / revenue * 100
#       print(f"{product:<12}{units:>6} units "
#             f"{revenue:>10,.2f} {profit:>10,.2f} {profit / revenue:>7.1%} "
#             f"{revenue / total:>7.1%} of revenue")
#   bar_chart(margins, "Margin % by product")
#
# EXERCISE 4
#   lost = [r for r in sales if not r["is_revenue"]]
#   potential = sum(r["revenue"] for r in sales)
#   for status, group in group_by(lost, "status").items():
#       amount = sum(r["revenue"] for r in group)
#       print(f"{status:<10}{len(group):>3} orders {amount:>10,.2f} "
#             f"({amount / potential:.1%} of potential)")
#
# EXERCISE 5
#   def pivot(records, row_field, column_field, value_field):
#       columns = sorted({r[column_field] for r in records})
#       print(f"{'':<10}" + "".join(f"{c:>12}" for c in columns))
#       for row_key, group in sorted(group_by(records, row_field).items()):
#           cells = ""
#           for c in columns:
#               cell_total = 0
#               for r in group:
#                   if r[column_field] == c:
#                       cell_total += r[value_field]
#               cells += f"{cell_total:>12,.2f}"
#           print(f"{row_key:<10}{cells}")
#   pivot(paid, "region", "month", "revenue")
#
# EXERCISE 6
#   totals = [monthly[m]["total"] for m in months]
#   for i, month in enumerate(months):
#       window = totals[max(0, i - 1):i + 1]      # this month and the one before
#       print(f"{month} actual {totals[i]:>10,.2f} moving avg "
#             f"{statistics.mean(window):>10,.2f}")
#   # A moving average smooths single-month spikes so the underlying trend
#   # becomes visible.
#
# EXERCISE 7
#   def check_quality(records):
#       id_counts = Counter(r["order_id"] for r in records)
#       duplicates = [order_id for order_id, count in id_counts.items() if count > 1]
#       print("duplicates:", duplicates)
#       print("bad quantity:", [r["order_id"] for r in records if r["quantity"] <= 0])
#       print("bad price:", [r["order_id"] for r in records if r["unit_price"] <= 0])
#       known = {"paid", "pending", "refunded"}
#       print("bad status:", [r["status"] for r in records if r["status"] not in known])
#   check_quality(sales)


print("=" * 70)
print("Lesson 19 complete. Next: 20_automation_project.py")
print("=" * 70)

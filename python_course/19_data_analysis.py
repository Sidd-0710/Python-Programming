"""
===============================================================================
 LESSON 19 — DATA ANALYSIS FOUNDATIONS
===============================================================================

Time: about 85 minutes.
Assumes: lessons 01-18 (especially 09 dictionaries, 14 CSV, 18 statistics).


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
            record["month"] = record["date"].strftime("%Y-%m")
            record["is_revenue"] = record["status"] == "paid"
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
        values = [r[column] for r in records]
        missing = sum(1 for v in values if v is None or v == "")
        unique = len(set(values))
        kind = type(values[0]).__name__

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
q1, median, q3 = statistics.quantiles(revenues)

print("  revenue distribution:")
print(f"    min {min(revenues):>10,.2f}")
print(f"    Q1  {q1:>10,.2f}")
print(f"    med {median:>10,.2f}")
print(f"    Q3  {q3:>10,.2f}")
print(f"    max {max(revenues):>10,.2f}")
print(f"    mean {mean:>9,.2f}   stdev {sd:,.2f}")

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
    groups = defaultdict(list)
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


paid = [r for r in sales if r["is_revenue"]]

for field in ("region", "product", "status"):
    groups = group_by(sales if field == "status" else paid, field)
    summary = aggregate(groups, "revenue")

    print(f"  BY {field.upper()}")
    print(f"    {'key':<14}{'n':>4}{'total':>12}{'mean':>10}{'max':>10}")
    print("    " + "-" * 50)
    for key, row in sorted(summary.items(), key=lambda p: -p[1]["total"]):
        print(f"    {str(key):<14}{row['count']:>4}{row['total']:>12,.2f}"
              f"{row['mean']:>10,.2f}{row['max']:>10,.2f}")
    print()

# Those two small functions replaced what would otherwise be three near-identical
# blocks of code. This is exactly what pandas' .groupby().agg() does for you.


# =============================================================================
# PART 4 — TIME SERIES: TRENDS OVER TIME
# =============================================================================
print(LINE)
print("PART 4 — TREND OVER TIME")
print(LINE)

monthly = aggregate(group_by(paid, "month"), "revenue")
months = sorted(monthly)

print(f"  {'month':<10}{'orders':>8}{'revenue':>12}{'change':>10}")
print("  " + "-" * 42)
previous = None
for month in months:
    row = monthly[month]
    if previous is None:
        change = "     -"
    else:
        pct = (row["total"] - previous) / previous
        change = f"{pct:>+9.1%}"
    print(f"  {month:<10}{row['count']:>8}{row['total']:>12,.2f}{change}")
    previous = row["total"]

total_revenue = sum(monthly[m]["total"] for m in months)
growth = (monthly[months[-1]]["total"] - monthly[months[0]]["total"]) / monthly[months[0]]["total"]
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


# =============================================================================
# PART 5 — CHARTS IN THE TERMINAL
# =============================================================================
print(LINE)
print("PART 5 — TEXT VISUALISATION")
print(LINE)

# You don't need matplotlib to SEE your data. A text bar chart takes four lines
# and works over SSH, in logs, and in an email.

def bar_chart(data, title, width=40, symbol="#"):
    """Draw a horizontal bar chart from a dict of label -> number."""
    if not data:
        print(f"  {title}: no data")
        return

    largest = max(data.values())
    label_width = max(len(str(k)) for k in data)

    print(f"  {title}")
    for label, value in sorted(data.items(), key=lambda p: -p[1]):
        filled = int(value / largest * width) if largest else 0
        bar = symbol * filled
        print(f"    {str(label):<{label_width}} |{bar:<{width}}| {value:>10,.2f}")
    print()


bar_chart({k: v["total"] for k, v in aggregate(group_by(paid, "region"), "revenue").items()},
          "Revenue by region")

bar_chart({k: v["total"] for k, v in aggregate(group_by(paid, "product"), "revenue").items()},
          "Revenue by product")

bar_chart({m: monthly[m]["total"] for m in months}, "Revenue by month")


def histogram(values, buckets=6, width=30):
    """Show the distribution of a list of numbers."""
    low, high = min(values), max(values)
    span = (high - low) / buckets or 1
    counts = Counter(min(int((v - low) / span), buckets - 1) for v in values)

    print(f"  Distribution of {len(values)} values")
    for index in range(buckets):
        start = low + index * span
        end = start + span
        count = counts.get(index, 0)
        bar = "#" * int(count / max(counts.values()) * width)
        print(f"    {start:>8,.0f}-{end:<8,.0f} |{bar:<{width}}| {count}")
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
    margin = profit / revenue if revenue else 0
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
by_profit = {p: sum(r["profit"] for r in g)
             for p, g in group_by(paid, "product").items()}
by_revenue = {p: sum(r["revenue"] for r in g)
              for p, g in group_by(paid, "product").items()}
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

# A plain-text summary for emailing:
summary_path = WORK_DIR / "sales_summary.txt"
summary_path.write_text("\n".join([
    "SALES ANALYSIS SUMMARY",
    "=" * 46,
    f"Period          : {min(r['date'] for r in sales)} to {max(r['date'] for r in sales)}",
    f"Orders          : {len(sales)} ({len(paid)} paid)",
    f"Revenue         : {total_rev:,.2f}",
    f"Profit          : {total_profit:,.2f} ({total_profit / total_rev:.1%} margin)",
    f"Average order   : {total_rev / len(paid):,.2f}",
    f"Best region     : {max(by_revenue, key=by_revenue.get)}",
    f"Best month      : {max(monthly, key=lambda m: monthly[m]['total'])}",
    f"Distinct buyers : {len({r['customer'] for r in sales})}",
]) + "\n", encoding="utf-8")

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
# EXERCISES
# =============================================================================
#
# EXERCISE 1 — Customer analysis
#   Produce a per-customer report: order count, total revenue, average order
#   value, favourite product, and first/last order date. Sort by total spend.
#
# EXERCISE 2 — Retention question
#   Which customers ordered in more than one month? Which ordered in every
#   month present in the data?
#
# EXERCISE 3 — Product performance
#   For each product: units sold, revenue, profit, margin, and its share of
#   total revenue as a percentage. Add a bar chart of margins.
#
# EXERCISE 4 — Failed orders
#   Analyse the non-paid orders: how much revenue is pending vs refunded, which
#   products and regions are worst affected, and what percentage of total
#   potential revenue is lost.
#
# EXERCISE 5 — Your own generic tool
#   Write pivot(records, row_field, column_field, value_field) producing a
#   two-dimensional summary - e.g. regions down the side, months across the
#   top, revenue in the cells. Print it as a table.
#
# EXERCISE 6 — Moving average
#   Calculate a 2-month moving average of revenue and print it alongside the
#   actual monthly figures. Explain what it smooths out.
#
# EXERCISE 7 — Data quality report
#   Write check_quality(records) that reports: missing values per column,
#   duplicate order_ids, dates outside a plausible range, negative quantities
#   or prices, and any status value outside the known set.
#
# EXERCISE 8 — Analyse your own data
#   Export something real from your own life - a bank statement, Spotify
#   history, a spreadsheet from work - and run this lesson's pipeline over it.
#   Real data is messy in ways sample data never is, and that's the point.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# EXERCISE 1
#   for customer, group in sorted(group_by(paid, "customer").items(),
#                                 key=lambda p: -sum(r["revenue"] for r in p[1])):
#       revenue = sum(r["revenue"] for r in group)
#       favourite = Counter(r["product"] for r in group).most_common(1)[0][0]
#       print(f"{customer:<16}{len(group):>3} orders {revenue:>10,.2f} "
#             f"avg {revenue / len(group):>8,.2f} likes {favourite} "
#             f"({min(r['date'] for r in group)} to {max(r['date'] for r in group)})")
#
# EXERCISE 2
#   months_per_customer = {c: {r["month"] for r in g}
#                          for c, g in group_by(sales, "customer").items()}
#   all_months = {r["month"] for r in sales}
#   print("repeat:", [c for c, m in months_per_customer.items() if len(m) > 1])
#   print("every month:", [c for c, m in months_per_customer.items() if m == all_months])
#
# EXERCISE 3
#   total = sum(r["revenue"] for r in paid)
#   for product, group in group_by(paid, "product").items():
#       revenue = sum(r["revenue"] for r in group)
#       profit = sum(r["profit"] for r in group)
#       print(f"{product:<12}{sum(r['quantity'] for r in group):>6} units "
#             f"{revenue:>10,.2f} {profit:>10,.2f} {profit / revenue:>7.1%} "
#             f"{revenue / total:>7.1%} of revenue")
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
#       table = {}
#       for row_key, group in group_by(records, row_field).items():
#           table[row_key] = {c: round(sum(r[value_field] for r in group
#                                          if r[column_field] == c), 2)
#                             for c in columns}
#       header = f"{'':<10}" + "".join(f"{c:>12}" for c in columns)
#       print(header)
#       for row_key in sorted(table):
#           cells = "".join(f"{table[row_key][c]:>12,.2f}" for c in columns)
#           print(f"{row_key:<10}{cells}")
#       return table
#   pivot(paid, "region", "month", "revenue")
#
# EXERCISE 6
#   totals = [monthly[m]["total"] for m in months]
#   for i, month in enumerate(months):
#       window = totals[max(0, i - 1):i + 1]
#       print(f"{month} actual {totals[i]:>10,.2f} moving avg "
#             f"{statistics.mean(window):>10,.2f}")
#   # A moving average smooths single-month spikes so the underlying trend
#   # becomes visible.
#
# EXERCISE 7
#   def check_quality(records):
#       ids = [r["order_id"] for r in records]
#       print("duplicates:", [i for i, c in Counter(ids).items() if c > 1])
#       print("bad quantity:", [r["order_id"] for r in records if r["quantity"] <= 0])
#       print("bad price:", [r["order_id"] for r in records if r["unit_price"] <= 0])
#       known = {"paid", "pending", "refunded"}
#       print("bad status:", [r["status"] for r in records if r["status"] not in known])


print("=" * 70)
print("Lesson 19 complete. Next: 20_automation_project.py")
print("=" * 70)

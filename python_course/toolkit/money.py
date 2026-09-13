"""Money helpers — an example module for lesson 15.

Note the deliberate design choice: these functions RETURN values and never
print. That is what makes them reusable - the caller decides whether the result
goes to a screen, a file, a web page or another calculation.
"""

DEFAULT_TAX_RATE = 0.20
CURRENCY_SYMBOL = "£"


def add_tax(amount, rate=DEFAULT_TAX_RATE):
    """Return `amount` with tax added, rounded to 2 decimal places."""
    if amount < 0:
        raise ValueError(f"amount cannot be negative (got {amount})")
    return round(amount * (1 + rate), 2)


def remove_tax(gross_amount, rate=DEFAULT_TAX_RATE):
    """Work backwards from a tax-inclusive figure to the net amount."""
    return round(gross_amount / (1 + rate), 2)


def format_money(amount, symbol=CURRENCY_SYMBOL, width=0):
    """Format a number as currency: 1234.5 -> '£1,234.50'."""
    return f"{symbol}{amount:>{width},.2f}"


def split_bill(total, people, tip_rate=0.0):
    """Split a bill evenly, optionally adding a tip.

    Returns a (per_person, grand_total) tuple.
    """
    if people < 1:
        raise ValueError("need at least one person to split a bill")
    grand_total = round(total * (1 + tip_rate), 2)
    return round(grand_total / people, 2), grand_total


if __name__ == "__main__":
    print("Self-test for money")
    print(" ", format_money(add_tax(100)))
    print(" ", split_bill(187.40, 5, tip_rate=0.125))

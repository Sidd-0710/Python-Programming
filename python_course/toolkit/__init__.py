"""
toolkit — a small example package used by lesson 15.

A folder becomes a PACKAGE when it contains this file, `__init__.py`. The file
runs once, the first time anything in the package is imported. It's the place
to decide what the package exposes to the outside world.

Here we re-export the most useful names so callers can write

    from toolkit import slugify

instead of the longer

    from toolkit.text_tools import slugify
"""

from toolkit.text_tools import slugify, initials, truncate
from toolkit.money import add_tax, format_money, split_bill

# __all__ declares the public API: the names `from toolkit import *` will take.
# It is documentation as much as mechanism - it says "these are supported, the
# rest are internal details that may change".
__all__ = [
    "slugify",
    "initials",
    "truncate",
    "add_tax",
    "format_money",
    "split_bill",
]

__version__ = "1.0.0"

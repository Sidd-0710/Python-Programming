"""Text helpers — an example module for lesson 15.

Everything here is built from lesson 02's string methods. The point of putting
them in a module is that ANY script can now reuse them with one import line,
instead of copying the code.
"""

# A module-level constant. Callers can read it as toolkit.text_tools.MAX_SLUG_LENGTH.
MAX_SLUG_LENGTH = 60


def slugify(text, separator="-"):
    """Turn arbitrary text into a URL-safe slug.

    >>> slugify("  Hello World! 2024  ")
    'hello-world-2024'
    """
    cleaned = []
    for character in text.strip().lower():
        if character.isalnum():
            cleaned.append(character)
        elif character in " _-":
            cleaned.append(separator)

    slug = "".join(cleaned)

    # Collapse runs of separators into one.
    while separator * 2 in slug:
        slug = slug.replace(separator * 2, separator)

    return slug.strip(separator)[:MAX_SLUG_LENGTH]


def initials(full_name, separator="."):
    """Return the initials of a name: 'Ana Maria Silva' -> 'A.M.S.'"""
    parts = [part for part in full_name.split() if part]
    if not parts:
        return ""
    return separator.join(part[0].upper() for part in parts) + separator


def truncate(text, length=40, suffix="..."):
    """Shorten text to `length` characters, adding a suffix if it was cut."""
    if len(text) <= length:
        return text
    return text[: length - len(suffix)].rstrip() + suffix


def _internal_helper():
    """A leading underscore means 'private' - not part of the public API.

    Python does not enforce this; it is a convention between developers. It
    tells a reader "don't rely on this, it may change without warning".
    """
    return "internal"


# This block runs ONLY when the file is executed directly:
#     python3 toolkit/text_tools.py
# It does NOT run when the module is imported. That makes it the perfect place
# for a quick self-test or demo. Lesson 15 explains the mechanism.
if __name__ == "__main__":
    print("Self-test for text_tools")
    print(" ", slugify("  Hello World! 2024  "))
    print(" ", initials("Ana Maria Silva"))
    print(" ", truncate("A rather long sentence that will not fit", 20))

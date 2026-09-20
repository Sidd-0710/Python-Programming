"""
===============================================================================
 LESSON 16 — CLASSES AND OBJECTS: BUNDLING DATA WITH BEHAVIOUR
===============================================================================

Time: about 85 minutes (there's a good place for a break halfway).
Assumes: lessons 01-15 (especially 09 dictionaries and 10 functions).


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. create your own TYPE of thing, with its own data and actions  (PART 1)
  2. understand `self` - the word every class uses                 (PART 2)
  3. share data between all objects, or keep it per object         (PART 3)
  4. make your objects work with print(), +, == and sorting        (PART 4)
  5. protect an object's data with properties                      (PART 5)
  6. build a real shopping cart from classes                       (PART 6)

NEW WORDS - come back here whenever you forget one:

  class         a BLUEPRINT for a kind of thing:  class Dog:
  object        one actual thing built from the blueprint:  rex = Dog(...)
                (also called an INSTANCE)
  attribute     a piece of data belonging to an object:  rex.name
  method        a function belonging to an object:  rex.bark()
  __init__      the method that runs automatically when an object is created.
                It sets up the object's starting data
  self          inside a class, means "THIS particular object"
  class attribute     data shared by EVERY object of the class
  instance attribute  data belonging to just ONE object
  dunder        "double underscore" methods like __init__ and __str__ that
                plug your class into Python's built-in behaviour
  property      a method that you use like an attribute - without brackets
  @             a DECORATOR: a label above a function that changes how it
                works.  @property  is the only one you need today

WHY THIS MATTERS FOR YOU: FastAPI describes every piece of API data as a class
(Pydantic models). If classes make sense, FastAPI will too.


-------------------------------------------------------------------------------
 THEORY: THE PROBLEM CLASSES SOLVE
-------------------------------------------------------------------------------

Here is a bank account built from what you already know:

    account = {"owner": "Sidd", "balance": 100.0}

    def deposit(account, amount):
        account["balance"] += amount

    def withdraw(account, amount):
        if amount > account["balance"]:
            raise ValueError("insufficient funds")
        account["balance"] -= amount

This works. But notice the friction:

  * The data and the functions that operate on it are separate. Nothing stops
    someone writing `account["balance"] = -9999` and bypassing every rule.
  * Every function must be passed the account explicitly.
  * Nothing guarantees an account dict has a "balance" key at all - a typo
    creates a new key silently.
  * With twenty such functions, which ones go with which kind of dict?

A CLASS bundles the data and the behaviour into one unit:

    account = BankAccount("Sidd", 100.0)
    account.deposit(50)
    account.withdraw(200)          # the account itself enforces the rule

The data and the rules that protect it now travel together. That's the whole
idea of object-oriented programming.


-------------------------------------------------------------------------------
 CLASS vs OBJECT: THE ONE DISTINCTION THAT MATTERS
-------------------------------------------------------------------------------

  A CLASS is a blueprint. It describes what something IS and what it can DO.
  An OBJECT (or INSTANCE) is one actual thing built from that blueprint.

  The class `BankAccount` is the concept. Sidd's account with £100 and Ana's
  account with £4,300 are two objects - separate data, same behaviour.

  Blueprint : house  ::  Class : object
  Recipe    : cake   ::  Class : object

You have been using objects since lesson 00. A string is an object of class
`str`, and `.upper()` is one of its methods. Lists are objects of class `list`.
Now you'll define your own types.


-------------------------------------------------------------------------------
 BE HONEST ABOUT WHEN YOU NEED THIS
-------------------------------------------------------------------------------

Beginners meet classes and immediately wrap everything in them. Don't. A dict
is often the right answer, and a plain function usually is too.

REACH FOR A CLASS WHEN:
  * you have data AND rules that must stay consistent with each other
  * you'll create many similar things with the same shape
  * you're modelling a real thing with state that changes over time
  * you find yourself passing the same three variables into every function

STICK WITH DICTS AND FUNCTIONS WHEN:
  * it's just data with no rules (an API response, a config file)
  * one function does the whole job
  * you'd be writing a class with one method and no state
"""

LINE = "-" * 70


# =============================================================================
# PART 1 — YOUR FIRST CLASS
# =============================================================================
print(LINE)
print("PART 1 — DEFINING A CLASS")
print(LINE)


class Dog:
    """A dog. The simplest possible useful class."""

    def __init__(self, name, breed, age):
        """Set up a new dog. Runs automatically when you create one."""
        # `self` refers to THIS PARTICULAR dog being created.
        # These are ATTRIBUTES - the object's own data.
        # In plain English: "this dog's name is the name we were given".
        self.name = name
        self.breed = breed
        self.age = age
        self.tricks = []          # each dog gets its OWN empty list

    def bark(self):
        """A METHOD - a function that belongs to the object."""
        return f"{self.name} says Woof!"

    def learn_trick(self, trick):
        """Methods can change the object's state."""
        self.tricks.append(trick)
        return f"{self.name} learned {trick}"

    def describe(self):
        """Methods can read the object's own attributes via self."""
        if self.tricks:
            trick_text = ", ".join(self.tricks)
        else:
            trick_text = "no tricks yet"
        return f"{self.name} is a {self.age}-year-old {self.breed} ({trick_text})"


# Creating objects. `Dog(...)` calls __init__ behind the scenes.
# In plain English: "build a new Dog from the blueprint, named Rex, a Labrador,
# aged 3 - and call it rex".
rex = Dog("Rex", "Labrador", 3)
bella = Dog("Bella", "Poodle", 5)

print(" ", rex.bark())
print(" ", bella.bark())
print(" ", rex.learn_trick("sit"))
print(" ", rex.learn_trick("roll over"))
print(" ", rex.describe())
print(" ", bella.describe(), "  <- Bella's tricks are separate from Rex's")
print()

# Attributes are read and written with a dot:
print("  rex.name:", rex.name)
rex.age = 4                          # a birthday
print("  after birthday:", rex.describe())
print()

# TRY IT NOW (2 minutes):
#   Create a third dog with your own choice of name, breed and age. Teach it
#   one trick, then print its describe().


# =============================================================================
# PART 2 — UNDERSTANDING self
# =============================================================================
print(LINE)
print("PART 2 — WHAT IS self?")
print(LINE)

# `self` confuses everyone at first. Here's the whole truth:
#
# When you write:      rex.bark()
# Python actually runs: Dog.bark(rex)
#
# It passes the object as the first argument automatically. `self` is just the
# name that first parameter conventionally gets. It is not a keyword - you
# could call it anything - but never do; every Python programmer expects `self`.

print("  rex.bark()      ->", rex.bark())
print("  Dog.bark(rex)   ->", Dog.bark(rex), "  <- identical")
print()

# CONSEQUENCES TO REMEMBER:
#   1. EVERY method needs `self` as its first parameter.
#      Forget it and you get: TypeError: bark() takes 0 positional arguments
#      but 1 was given - which is Python's confusing way of saying "you forgot
#      self".
#   2. To use an attribute inside a method you MUST write self.name, not name.
#      A bare `name` refers to a local variable, and you'll get a NameError.
#   3. Methods can call other methods on the same object via self.

class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        return self

    def double(self):
        self.count *= 2
        return self                  # returning self allows CHAINING

    def report(self):
        return f"count is {self.count}"


counter = Counter()
print(" ", counter.increment().increment().double().report())
#   Read it left to right: increment (1), increment again (2), double (4),
#   then report. Each method gives back the same counter, so the next one can
#   be called on it straight away.
print()


# =============================================================================
# PART 3 — CLASS ATTRIBUTES vs INSTANCE ATTRIBUTES
# =============================================================================
print(LINE)
print("PART 3 — SHARED vs PER-OBJECT DATA")
print(LINE)


class BankAccount:
    """A bank account that protects its own balance."""

    # CLASS ATTRIBUTE - shared by every account that exists.
    interest_rate = 0.02
    bank_name = "Python Savings"
    account_count = 0

    def __init__(self, owner, balance=0.0):
        # INSTANCE ATTRIBUTES - unique to this one account.
        self.owner = owner
        self.balance = balance
        self.transactions = []

        # Updating a class attribute affects all instances.
        BankAccount.account_count += 1
        self.account_number = f"ACC{BankAccount.account_count:05d}"

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount
        self.transactions.append(("deposit", amount))
        return self.balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self.balance:
            raise ValueError(
                f"insufficient funds: balance {self.balance:.2f}, "
                f"requested {amount:.2f}"
            )
        self.balance -= amount
        self.transactions.append(("withdraw", amount))
        return self.balance

    def add_interest(self):
        """Uses the CLASS attribute - change the rate once, every account
        follows."""
        interest = self.balance * self.interest_rate
        self.balance += interest
        self.transactions.append(("interest", interest))
        return interest

    def statement(self):
        lines = [f"{self.bank_name} - {self.account_number} ({self.owner})"]
        for kind, amount in self.transactions:
            lines.append(f"  {kind:<10}{amount:>10.2f}")
        lines.append(f"  {'BALANCE':<10}{self.balance:>10.2f}")
        return "\n".join(lines)


sidd_account = BankAccount("Sidd", 100.0)
ana_account = BankAccount("Ana", 4300.0)

sidd_account.deposit(250)
sidd_account.withdraw(80)
sidd_account.add_interest()

print(sidd_account.statement())
print()
print("  accounts created:", BankAccount.account_count)
print("  Ana's number    :", ana_account.account_number)
print("  shared rate     :", BankAccount.interest_rate)
print()

# The rules are now enforced by the object itself:
try:
    sidd_account.withdraw(999999)
except ValueError as error:
    print("  blocked:", error)
print()

# TRY IT NOW (2 minutes):
#   Deposit 50 into ana_account, then print ana_account.balance.
#   Then try ana_account.deposit(-5) and read the error.


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. You can now write classes, create objects, and use
#  self. After the break: making objects feel built-in, and a real example.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 4 — DUNDER METHODS: MAKING OBJECTS FEEL BUILT-IN
# =============================================================================
print(LINE)
print("PART 4 — SPECIAL (DUNDER) METHODS")
print(LINE)

# Methods with double underscores either side ("dunder" = double underscore)
# hook into Python's built-in syntax. __init__ is one you already know.
# Implementing others lets YOUR objects work with print(), len(), ==, +, and
# sorting - just like built-in types.
#
# You never CALL these yourself. Python calls them for you:
#     print(price)        -> Python calls price.__str__()
#     price + shipping    -> Python calls price.__add__(shipping)


class Money:
    """An amount of money, with arithmetic that behaves sensibly."""

    def __init__(self, amount, currency="GBP"):
        self.amount = round(amount, 2)
        self.currency = currency

    def __str__(self):
        """What print() shows. For humans."""
        symbols = {"GBP": "£", "USD": "$", "EUR": "€"}
        return f"{symbols.get(self.currency, '')}{self.amount:,.2f}"

    def __repr__(self):
        """What the interactive prompt and containers show. For developers.
        Aim for something you could paste back into code."""
        return f"Money({self.amount}, {self.currency!r})"

    def __add__(self, other):
        """Makes the + operator work."""
        if self.currency != other.currency:
            raise ValueError(f"cannot add {self.currency} to {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other):
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor):
        return Money(self.amount * factor, self.currency)

    def __eq__(self, other):
        """Makes == compare by VALUE rather than identity."""
        return (self.amount == other.amount
                and self.currency == other.currency)

    def __lt__(self, other):
        """Makes <, and therefore sorted(), work."""
        return self.amount < other.amount


price = Money(19.99)
shipping = Money(4.50)

print("  str  :", price)                          # uses __str__
print("  repr :", repr(price))                    # uses __repr__
print("  in a list:", [price, shipping])          # containers use __repr__
print("  price + shipping :", price + shipping)
print("  price * 3        :", price * 3)
print("  equality         :", Money(19.99) == Money(19.99))
print("  sorted           :", sorted([Money(30), Money(5), Money(12)]))
print()

try:
    Money(10, "GBP") + Money(10, "USD")
except ValueError as error:
    print("  currency guard:", error)
print()

# THE ONES WORTH KNOWING:
#   __init__    construction
#   __str__     print() and str()          - for humans
#   __repr__    debugging and containers   - for developers
#   __len__     len(obj)
#   __eq__      ==
#   __lt__      < and sorting
#   __add__     +
#   __contains__  the `in` operator
#   __getitem__ obj[key]
#   __iter__    makes it usable in a for loop
#
# ALWAYS define __repr__ on your classes. Without it, debugging shows
# `<__main__.Money object at 0x7f8b1c0d2e50>`, which tells you nothing.

# OPTIONAL DEPTH - a class that behaves like a list. Skim it now; come back
# when you need to build a collection of your own.
class Playlist:
    """A container class - shows __len__, __getitem__, __iter__, __contains__."""

    def __init__(self, name):
        self.name = name
        self.songs = []

    def add(self, song):
        self.songs.append(song)
        return self

    def __len__(self):
        return len(self.songs)

    def __getitem__(self, index):
        return self.songs[index]

    def __iter__(self):
        return iter(self.songs)

    def __contains__(self, song):
        return song in self.songs

    def __repr__(self):
        return f"Playlist({self.name!r}, {len(self.songs)} songs)"


playlist = Playlist("Focus")
playlist.add("Song A").add("Song B").add("Song C")

print(" ", repr(playlist))
print("  len()      :", len(playlist))
print("  indexing   :", playlist[0])
print("  slicing    :", playlist[1:])
print("  membership :", "Song B" in playlist)
print("  iteration  :", [s for s in playlist])
# Those five lines of dunder methods made Playlist behave like a built-in
# collection, which is exactly what a reader would expect it to do.
print()


# =============================================================================
# PART 5 — ENCAPSULATION: PUBLIC, PROTECTED, PROPERTIES
# =============================================================================
print(LINE)
print("PART 5 — CONTROLLING ACCESS")
print(LINE)

# Python has no truly private attributes. It uses conventions instead, and
# trusts developers to respect them:
#
#   self.name      PUBLIC    - use it freely
#   self._name     PROTECTED - "internal; don't rely on this" (convention only)
#   self.__name    PRIVATE   - name-mangled, genuinely awkward to reach
#                              (rarely needed - you can ignore this one)


class Temperature:
    """Demonstrates a property: an attribute with logic behind it."""

    def __init__(self, celsius=0.0):
        self._celsius = celsius          # the underscore says "internal"

    # @property turns the method below into something you READ like an
    # attribute: temp.celsius, with no brackets.
    @property
    def celsius(self):
        """Read like an attribute, but it's really a method call."""
        return self._celsius

    # @celsius.setter says "and THIS method runs when someone ASSIGNS
    # temp.celsius = something" - so we get a chance to check the value.
    @celsius.setter
    def celsius(self, value):
        """Runs on assignment - so we can VALIDATE."""
        if value < -273.15:
            raise ValueError(f"{value} is below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):
        """A COMPUTED attribute - no stored value, worked out on demand."""
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5 / 9      # reuses the validation above


temp = Temperature(21.5)
print("  celsius    :", temp.celsius)
print("  fahrenheit :", round(temp.fahrenheit, 1))

temp.fahrenheit = 100                    # looks like assignment, runs a method
print("  after setting F=100, celsius is", round(temp.celsius, 2))

try:
    temp.celsius = -300
except ValueError as error:
    print("  validation:", error)
print()

# WHY PROPERTIES ARE GREAT: you can start with a plain `self.celsius`
# attribute, and later add validation or computation WITHOUT changing a single
# line of calling code. In many languages you must write getters and setters up
# front just in case. In Python you add them only when you actually need them.

# TRY IT NOW (1 minute):
#   Set temp.celsius = 0 and print temp.fahrenheit. (Answer: 32.0)


# =============================================================================
# PART 6 — REAL EXAMPLE: A SHOPPING CART (WEB BACKEND SHAPE)
# =============================================================================
print(LINE)
print("PART 6 — REAL EXAMPLE: SHOPPING CART")
print(LINE)


class Product:
    """One item in a catalogue."""

    def __init__(self, sku, name, price, stock):
        self.sku = sku                   # "stock keeping unit" - a product code
        self.name = name
        self.price = price
        self.stock = stock

    def __repr__(self):
        return f"Product({self.sku!r}, {self.name!r}, {self.price})"

    def in_stock(self, quantity=1):
        return self.stock >= quantity


class CartItem:
    """One line in a cart: a product and how many of it."""

    def __init__(self, product, quantity):
        self.product = product           # an object inside an object
        self.quantity = quantity

    @property
    def line_total(self):
        return round(self.product.price * self.quantity, 2)

    def __repr__(self):
        return f"CartItem({self.product.name!r} x{self.quantity})"


class Cart:
    """A shopping cart that enforces its own rules."""

    TAX_RATE = 0.20
    FREE_SHIPPING_THRESHOLD = 50.00
    SHIPPING_COST = 4.99

    def __init__(self, customer):
        self.customer = customer
        self._items = {}                 # sku -> CartItem

    def add(self, product, quantity=1):
        if quantity < 1:
            raise ValueError("quantity must be at least 1")

        # How many of this product are in the cart already?
        if product.sku in self._items:
            already = self._items[product.sku].quantity
        else:
            already = 0

        if not product.in_stock(already + quantity):
            raise ValueError(
                f"only {product.stock} of {product.name} left "
                f"(you asked for {already + quantity})"
            )

        if product.sku in self._items:
            self._items[product.sku].quantity += quantity
        else:
            self._items[product.sku] = CartItem(product, quantity)
        return self

    def remove(self, sku):
        self._items.pop(sku, None)
        return self

    @property
    def subtotal(self):
        return round(sum(item.line_total for item in self._items.values()), 2)

    @property
    def shipping(self):
        if self.subtotal == 0 or self.subtotal >= self.FREE_SHIPPING_THRESHOLD:
            return 0.0
        return self.SHIPPING_COST

    @property
    def tax(self):
        return round(self.subtotal * self.TAX_RATE, 2)

    @property
    def total(self):
        return round(self.subtotal + self.tax + self.shipping, 2)

    def __len__(self):
        return sum(item.quantity for item in self._items.values())

    def __iter__(self):
        return iter(self._items.values())

    def __repr__(self):
        return f"Cart({self.customer!r}, {len(self)} items, {self.total})"

    def receipt(self):
        lines = [f"Receipt for {self.customer}", "-" * 44]
        for item in self:                # works because of __iter__ above
            lines.append(
                f"  {item.product.name:<20}{item.quantity:>3} x "
                f"{item.product.price:>6.2f} = {item.line_total:>7.2f}"
            )
        lines.append("-" * 44)
        lines.append(f"  {'Subtotal':<32}{self.subtotal:>10.2f}")
        lines.append(f"  {'Tax (20%)':<32}{self.tax:>10.2f}")
        lines.append(f"  {'Shipping':<32}{self.shipping:>10.2f}")
        lines.append(f"  {'TOTAL':<32}{self.total:>10.2f}")
        if self.shipping == 0 and self.subtotal > 0:
            lines.append("  (free shipping applied)")
        return "\n".join(lines)


catalogue = {
    "W1": Product("W1", "Widget", 4.99, 100),
    "G1": Product("G1", "Gadget", 12.50, 5),
    "S1": Product("S1", "Sprocket", 89.00, 2),
}

cart = Cart("Sidd")
cart.add(catalogue["W1"], 3).add(catalogue["G1"], 2).add(catalogue["W1"], 1)

print(cart.receipt())
print()
print("  repr:", repr(cart))

try:
    cart.add(catalogue["S1"], 10)
except ValueError as error:
    print("  stock guard:", error)
print()

# LOOK AT WHAT THE CLASSES BOUGHT US: the tax rate, the shipping rule and the
# stock check all live in exactly one place. A web page, an API endpoint and a
# nightly report could all use this same Cart and be guaranteed to agree.


# =============================================================================
# PART 7 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 7 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: forgetting `self` in the method definition.
#     def bark():     ->  TypeError about positional arguments

# MISTAKE 2: forgetting `self.` inside a method.
#     def describe(self):
#         return name         # NameError - there's no local `name`
#         return self.name    # correct

# MISTAKE 3: a MUTABLE CLASS ATTRIBUTE - the class version of lesson 10's
#   mutable default trap, and just as nasty:
class BrokenTeam:
    members = []                     # SHARED by every team!

    def add(self, name):
        self.members.append(name)

team_a = BrokenTeam()
team_b = BrokenTeam()
team_a.add("Sidd")
print("  team_b.members:", team_b.members, "<- Sidd leaked into the other team")

class FixedTeam:
    def __init__(self):
        self.members = []            # a fresh list per instance

fixed_a = FixedTeam()
fixed_b = FixedTeam()
fixed_a.members.append("Sidd")
print("  fixed_b.members:", fixed_b.members, "<- correctly empty")

# MISTAKE 4: no __repr__, making debugging miserable.

# MISTAKE 5: calling the class instead of an instance, or vice versa.
#     Dog.bark()        -> TypeError, no self supplied
#     rex.bark()        -> correct

# MISTAKE 6: writing a class where a function would do. If it has an __init__
#   and one method, it's a function wearing a costume.

# MISTAKE 7: giant classes. The same rule as functions: one responsibility. If
#   you can't describe the class in one sentence, split it.

# MISTAKE 8: confusing __str__ and __repr__. Define both; __repr__ especially.
print()


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * class Dog:  defines a blueprint.  rex = Dog("Rex", ...)  builds an object.
#   * __init__(self, ...) runs automatically to set up each new object.
#   * self means "this object". Use self.name inside methods.
#   * Attributes are the object's data (rex.name); methods are its actions
#     (rex.bark()).
#   * Class attributes are shared by all objects; self.x attributes are
#     per object. Never put a list or dict as a class attribute.
#   * Dunders (__str__, __repr__, __eq__, __add__...) plug into print, ==, +.
#   * @property makes a method readable like an attribute - and lets a setter
#     validate new values.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. What's the difference between a class and an object?
#   Q2. What does __init__ do, and when does it run?
#   Q3. Inside a method, why write self.name and not just name?
#   Q4. You forgot `self` in  def bark():.  What error do you get?
#   Q5. What does @property let you write?
#
# ANSWERS
#   A1. A class is the blueprint; an object is one thing built from it.
#   A2. It sets up a new object's starting data. It runs automatically when
#       you create the object:  Dog("Rex", ...).
#   A3. self.name is the object's attribute. A bare `name` would be a local
#       variable that doesn't exist - NameError.
#   A4. TypeError: bark() takes 0 positional arguments but 1 was given.
#   A5. temp.celsius (no brackets) instead of temp.celsius() - and a setter
#       can validate  temp.celsius = -300.


# =============================================================================
# EXERCISES
# =============================================================================
#
# WARM-UP A (easy) — A Cat
#   Write a Cat class whose __init__ takes a name. Give it a meow() method that
#   returns "<name> says meow". Create a cat and print its meow().
#
# WARM-UP B (easy) — Two cats
#   Create a second cat with a different name. Print both names, to see each
#   object keeps its own data.
#
# WARM-UP C (easy) — A method that changes things
#   Add a rename(new_name) method to Cat that changes self.name. Rename one cat
#   and print its meow() again.
#
# EXERCISE 1 (easy) — Rectangle
#   Write a Rectangle class with width and height. Give it area(), perimeter(),
#   an is_square property, and a __str__. Create three and print their details.
#
# EXERCISE 2 (medium) — Student
#   Write a Student class holding a name and a list of grades. Methods:
#   add_grade(), average (a property), best (a property), and a letter_grade()
#   method using lesson 05's rules. Handle the no-grades-yet case.
#
# EXERCISE 3 (medium) — BankAccount, extended
#   Add to PART 3's BankAccount: a transfer_to(other, amount) method that
#   withdraws from this account and deposits into the other one.
#   CHALLENGE: also add an overdraft_limit, and a history() method showing a
#   running balance after each transaction.
#
# EXERCISE 4 (medium) — Timer with dunders
#   Write a Duration class holding seconds. Implement __str__ ("1h 2m 3s"),
#   __add__, __lt__ and __eq__. Sort a list of them.
#
# EXERCISE 5 (medium) — Inventory with properties
#   Write an Item class where `quantity` is a property that refuses negatives,
#   and `total_value` is computed from quantity * unit_price. Prove the
#   validation works.
#
# EXERCISE 6 (challenge) — Convert a dict-based design
#   Take the `orders` data from lesson 14 and design an Order class for it.
#   Give it a `total` property and a `is_revenue` property (paid, not
#   refunded). Then rewrite one of lesson 14's reports using your class.
#
# EXERCISE 7 (challenge) — Deck of cards
#   Write Card and Deck classes. Deck should support len(), iteration,
#   shuffle(), deal(n), and printing. Use lesson 03's random module.
#
# EXERCISE 8 (medium) — When NOT to use a class
#   Find something in an earlier lesson that you could rewrite as a class, do
#   it, and then argue honestly with yourself about whether it's an
#   improvement. Sometimes the answer is no - that's a useful thing to notice.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   class Cat:
#       def __init__(self, name):
#           self.name = name
#       def meow(self):
#           return f"{self.name} says meow"
#   tom = Cat("Tom")
#   print(tom.meow())                  # -> Tom says meow
#
# WARM-UP B
#   luna = Cat("Luna")
#   print(tom.name, luna.name)         # -> Tom Luna
#
# WARM-UP C
#   # inside the Cat class:
#   def rename(self, new_name):
#       self.name = new_name
#   # then:
#   tom.rename("Thomas")
#   print(tom.meow())                  # -> Thomas says meow
#
# EXERCISE 1
#   class Rectangle:
#       def __init__(self, width, height):
#           self.width = width
#           self.height = height
#       def area(self):
#           return self.width * self.height
#       def perimeter(self):
#           return 2 * (self.width + self.height)
#       @property
#       def is_square(self):
#           return self.width == self.height
#       def __str__(self):
#           return f"{self.width}x{self.height} (area {self.area()})"
#       def __repr__(self):
#           return f"Rectangle({self.width}, {self.height})"
#
# EXERCISE 2
#   class Student:
#       def __init__(self, name):
#           self.name = name
#           self.grades = []
#       def add_grade(self, grade):
#           if not 0 <= grade <= 100:
#               raise ValueError("grade must be 0-100")
#           self.grades.append(grade)
#       @property
#       def average(self):
#           if not self.grades:
#               return None
#           return sum(self.grades) / len(self.grades)
#       @property
#       def best(self):
#           if not self.grades:
#               return None
#           return max(self.grades)
#       def letter_grade(self):
#           avg = self.average
#           if avg is None:
#               return "N/A"
#           if avg >= 90:
#               return "A"
#           if avg >= 80:
#               return "B"
#           if avg >= 70:
#               return "C"
#           if avg >= 60:
#               return "D"
#           return "F"
#
# EXERCISE 3
#   # inside the BankAccount class:
#   def transfer_to(self, other, amount):
#       self.withdraw(amount)          # raises if there isn't enough - good
#       other.deposit(amount)
#       return self.balance
#   # then:
#   sidd_account.transfer_to(ana_account, 50)
#   print(sidd_account.balance, ana_account.balance)
#   Note: withdraw runs FIRST. If it fails, nothing has been deposited - so
#   money can never appear from nowhere.
#
# EXERCISE 4
#   class Duration:
#       def __init__(self, seconds):
#           self.seconds = int(seconds)
#       def __str__(self):
#           hours = self.seconds // 3600
#           minutes = (self.seconds % 3600) // 60
#           secs = self.seconds % 60
#           return f"{hours}h {minutes}m {secs}s"
#       def __repr__(self):
#           return f"Duration({self.seconds})"
#       def __add__(self, other):
#           return Duration(self.seconds + other.seconds)
#       def __lt__(self, other):
#           return self.seconds < other.seconds
#       def __eq__(self, other):
#           return self.seconds == other.seconds
#   print(sorted([Duration(3723), Duration(60), Duration(600)]))
#
# EXERCISE 5
#   class Item:
#       def __init__(self, name, unit_price, quantity=0):
#           self.name = name
#           self.unit_price = unit_price
#           self.quantity = quantity          # goes through the setter below
#       @property
#       def quantity(self):
#           return self._quantity
#       @quantity.setter
#       def quantity(self, value):
#           if value < 0:
#               raise ValueError("quantity cannot be negative")
#           self._quantity = value
#       @property
#       def total_value(self):
#           return round(self.unit_price * self._quantity, 2)
#
# EXERCISE 7
#   import random
#   class Card:
#       SUITS = ["♠", "♥", "♦", "♣"]
#       RANKS = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
#       def __init__(self, rank, suit):
#           self.rank = rank
#           self.suit = suit
#       def __repr__(self):
#           return f"{self.rank}{self.suit}"
#   class Deck:
#       def __init__(self):
#           self.cards = []
#           for suit in Card.SUITS:
#               for rank in Card.RANKS:
#                   self.cards.append(Card(rank, suit))
#       def __len__(self):
#           return len(self.cards)
#       def __iter__(self):
#           return iter(self.cards)
#       def shuffle(self):
#           random.shuffle(self.cards)
#           return self
#       def deal(self, n):
#           dealt = self.cards[:n]           # the first n cards...
#           self.cards = self.cards[n:]      # ...are removed from the deck
#           return dealt


print("=" * 70)
print("Lesson 16 complete. Next: 17_inheritance.py")
print("=" * 70)

"""
===============================================================================
 LESSON 17 — INHERITANCE AND POLYMORPHISM
===============================================================================

Time: about 70 minutes (there's a good place for a break halfway).
Assumes: lesson 16.


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. build a new class ON TOP of an existing one                  (PART 1)
  2. treat different classes the same way in one loop             (PART 2)
  3. understand "duck typing" - Python's relaxed approach         (PART 3)
  4. force subclasses to provide certain methods                  (PART 4)
  5. choose between inheriting and simply HOLDING another object  (PART 5)

NEW WORDS - come back here whenever you forget one:

  inheritance   a class getting everything from another class, then adding
                or changing bits:  class Manager(Employee):
  parent class  the class being inherited FROM (also "base class")
  child class   the class that inherits (also "subclass")
  override      a child writing its own version of a parent's method
  super()       "the parent class" - used to run the parent's version of a
                method from inside the child
  polymorphism  "many forms": different classes answering the same method
                call, each in its own way
  isinstance()  "is this object this kind of thing (or a child of it)?"
  duck typing   "if it has the method I need, I don't care what class it is"
  abstract      a parent class that's only a template - it can't be used on
                its own, only through its children
  composition   an object HOLDING another object as an attribute (a Car
                holds an Engine) instead of inheriting from it

WHY THIS MATTERS FOR YOU: every FastAPI data model starts with
class Something(BaseModel):  - that's inheritance. Pydantic's BaseModel is the
parent; your class gets all its validation powers for free.


-------------------------------------------------------------------------------
 THEORY: SHARING BEHAVIOUR BETWEEN CLASSES
-------------------------------------------------------------------------------

Suppose you're building a payroll system with three kinds of employee. All of
them have a name, an ID and a start date. All of them can be described and
compared. But each is PAID differently.

Copy the shared parts into three classes and you have three copies of the same
code to keep in sync - a guaranteed source of bugs.

INHERITANCE says: write the shared part once in a PARENT class, then have each
CHILD class inherit it and change only what differs.

    class Employee:              <- the parent (also called base/superclass)
        ...shared behaviour...

    class Manager(Employee):     <- the child inherits everything
        ...only the differences...

POLYMORPHISM is the payoff. It means "many forms": you can treat every child as
if it were the parent, and each one does the right thing for its own type.

    for person in [manager, contractor, intern]:
        print(person.calculate_pay())      # each computes its own way

The loop doesn't know or care which kind it's holding. Adding a fourth employee
type requires no change to that loop at all. That is the real prize.


-------------------------------------------------------------------------------
 THE HONEST WARNING
-------------------------------------------------------------------------------

Inheritance is the most over-used idea in programming. Deep hierarchies become
impossible to follow, because to understand one method you must read five
files.

THE TEST: use inheritance only for a genuine "IS-A" relationship.
    A Manager IS AN Employee.           -> inheritance is right
    A Car HAS AN Engine.                -> use an attribute, not inheritance

Prefer COMPOSITION (an object holding other objects) over inheritance whenever
you're unsure. Keep hierarchies one or two levels deep.
"""

LINE = "-" * 70


# =============================================================================
# PART 1 — A BASIC HIERARCHY
# =============================================================================
print(LINE)
print("PART 1 — PARENT AND CHILD CLASSES")
print(LINE)


class Employee:
    """The parent class: everything every employee has in common."""

    company = "Acme Ltd"

    def __init__(self, name, employee_id):
        self.name = name
        self.employee_id = employee_id

    def describe(self):
        return f"{self.name} ({self.employee_id}) at {self.company}"

    def calculate_pay(self):
        """Subclasses are expected to replace this."""
        raise NotImplementedError("each employee type must define its own pay")

    def __repr__(self):
        # type(self).__name__ is the name of the object's actual class
        return f"{type(self).__name__}({self.name!r})"


# (Employee) in brackets means "start with everything Employee has".
class SalariedEmployee(Employee):
    """A child class. Inherits everything, adds and overrides some."""

    def __init__(self, name, employee_id, annual_salary):
        # super() calls the PARENT's version. Do this first so the shared
        # setup still happens - otherwise self.name would never be set.
        # In plain English: "do the normal Employee setup, then add my salary".
        super().__init__(name, employee_id)
        self.annual_salary = annual_salary

    def calculate_pay(self):
        """OVERRIDING: same method name, different behaviour."""
        return round(self.annual_salary / 12, 2)


class HourlyEmployee(Employee):
    OVERTIME_MULTIPLIER = 1.5

    def __init__(self, name, employee_id, hourly_rate, hours_worked=0):
        super().__init__(name, employee_id)
        self.hourly_rate = hourly_rate
        self.hours_worked = hours_worked

    def calculate_pay(self):
        normal = min(self.hours_worked, 160)          # at most 160 normal hours
        overtime = max(self.hours_worked - 160, 0)    # anything above 160 (never below 0)
        return round(normal * self.hourly_rate
                     + overtime * self.hourly_rate * self.OVERTIME_MULTIPLIER, 2)


class Manager(SalariedEmployee):
    """A child of a child. Two levels is plenty."""

    def __init__(self, name, employee_id, annual_salary, bonus_rate=0.10):
        super().__init__(name, employee_id, annual_salary)
        self.bonus_rate = bonus_rate
        self.reports = []

    def add_report(self, employee):
        self.reports.append(employee)
        return self

    def calculate_pay(self):
        """EXTENDING rather than replacing: call the parent, then add to it."""
        base = super().calculate_pay()            # the SalariedEmployee pay...
        return round(base * (1 + self.bonus_rate), 2)   # ...plus a bonus

    def describe(self):
        """Extending the parent's describe() too."""
        return f"{super().describe()} - manages {len(self.reports)}"


ana = SalariedEmployee("Ana", "E001", 54000)
marco = HourlyEmployee("Marco", "E002", 22.50, hours_worked=175)
sidd = Manager("Sidd", "E003", 72000, bonus_rate=0.15)
sidd.add_report(ana).add_report(marco)

for person in (ana, marco, sidd):
    print(f"  {person.describe()}")
    print(f"      monthly pay: {person.calculate_pay():>10,.2f}")
print()

# Children get the parent's attributes and methods for free:
print("  inherited class attribute:", marco.company)
print("  inherited __repr__      :", repr(marco))
print()

# TRY IT NOW (2 minutes):
#   Create  intern = HourlyEmployee("Priya", "E005", 15.00, hours_worked=80)
#   and print intern.describe() and intern.calculate_pay().
#   (describe() comes from Employee; calculate_pay() from HourlyEmployee.)


# =============================================================================
# PART 2 — POLYMORPHISM IN ACTION
# =============================================================================
print(LINE)
print("PART 2 — POLYMORPHISM")
print(LINE)

# The whole point: one loop, many types, correct behaviour for each.
payroll = [ana, marco, sidd]

total = 0
print(f"  {'Employee':<12}{'Type':<20}{'Pay':>12}")
print("  " + "-" * 44)
for person in payroll:
    pay = person.calculate_pay()        # each person uses THEIR OWN version
    total += pay
    print(f"  {person.name:<12}{type(person).__name__:<20}{pay:>12,.2f}")
print("  " + "-" * 44)
print(f"  {'TOTAL':<32}{total:>12,.2f}")
print()

# Adding a ContractorEmployee class later would need ZERO changes to this loop.
# That's the design win: code that's open to extension but closed to
# modification.

# isinstance() checks type membership, and understands inheritance:
print("  isinstance(sidd, Manager)          :", isinstance(sidd, Manager))
print("  isinstance(sidd, SalariedEmployee) :", isinstance(sidd, SalariedEmployee))
print("  isinstance(sidd, Employee)         :", isinstance(sidd, Employee))
print("  isinstance(marco, Manager)         :", isinstance(marco, Manager))

# OPTIONAL - the "method resolution order": exactly where Python looks, in
# order, when you call a method. Useful when you're confused about which
# version ran. You can skip this line for now.
print("  the chain:", " -> ".join(c.__name__ for c in type(sidd).__mro__))
print()


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. Inheritance and polymorphism - the core of this
#  lesson - are done. After the break: other ways to share behaviour.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 3 — DUCK TYPING: PYTHON'S PREFERRED APPROACH
# =============================================================================
print(LINE)
print("PART 3 — DUCK TYPING")
print(LINE)

# "If it walks like a duck and quacks like a duck, it's a duck."
#
# Python does not require a shared parent class for polymorphism. It only cares
# that the method EXISTS at call time. These two classes are unrelated, yet
# interchangeable - they both have an export() method:


class CsvExporter:
    def export(self, rows):
        lines = []
        for row in rows:
            lines.append(",".join(str(cell) for cell in row))
        return "\n".join(lines)


class MarkdownExporter:
    def export(self, rows):
        header = rows[0]
        lines = ["| " + " | ".join(str(c) for c in header) + " |",
                 "|" + "---|" * len(header)]
        for row in rows[1:]:
            lines.append("| " + " | ".join(str(c) for c in row) + " |")
        return "\n".join(lines)


data = [["name", "score"], ["Ana", 92], ["Sidd", 88]]

for exporter in (CsvExporter(), MarkdownExporter()):
    print(f"  {type(exporter).__name__}:")
    for line in exporter.export(data).splitlines():
        print("   ", line)
print()

# This is why Python code often has fewer classes and shallower hierarchies
# than Java or C#. You don't need to declare a shared interface - you just need
# matching method names. It's flexible, at the cost of errors showing up at run
# time rather than being caught in advance.


# =============================================================================
# PART 4 — ABSTRACT BASE CLASSES
# =============================================================================
print(LINE)
print("PART 4 — ABSTRACT BASE CLASSES")
print(LINE)

# When you DO want to guarantee that subclasses implement something, use the
# abc module. An abstract class cannot be instantiated, and Python refuses to
# create a subclass that hasn't filled in every abstract method.

from abc import ABC, abstractmethod


class PaymentMethod(ABC):
    """Every payment method must be able to charge and to describe itself."""

    def __init__(self, owner):
        self.owner = owner

    # @abstractmethod marks a method children MUST write themselves. The body
    # here is just a docstring - the parent deliberately doesn't implement it.
    @abstractmethod
    def charge(self, amount):
        """Subclasses MUST implement this."""

    @abstractmethod
    def display_name(self):
        """Subclasses MUST implement this too."""

    def receipt(self, amount):
        """A concrete method - shared by all subclasses, no need to repeat it."""
        return f"Charged {amount:.2f} to {self.display_name()} for {self.owner}"


class CreditCard(PaymentMethod):
    def __init__(self, owner, last_four):
        super().__init__(owner)
        self.last_four = last_four

    def charge(self, amount):
        return {"ok": True, "method": "card", "amount": amount}

    def display_name(self):
        return f"card ending {self.last_four}"


class BankTransfer(PaymentMethod):
    def __init__(self, owner, sort_code):
        super().__init__(owner)
        self.sort_code = sort_code

    def charge(self, amount):
        return {"ok": True, "method": "transfer", "amount": amount}

    def display_name(self):
        return f"bank account {self.sort_code}"


for method in (CreditCard("Sidd", "4242"), BankTransfer("Ana", "20-00-00")):
    print(" ", method.receipt(49.99))
    print("   ", method.charge(49.99))

try:
    PaymentMethod("Nobody")
except TypeError as error:
    print("\n  abstract classes can't be instantiated:")
    print("   ", str(error)[:70])
print()


# =============================================================================
# PART 5 — COMPOSITION: USUALLY THE BETTER CHOICE
# =============================================================================
print(LINE)
print("PART 5 — COMPOSITION OVER INHERITANCE")
print(LINE)

# Instead of inheriting behaviour, HOLD an object that provides it. This is
# more flexible, because you can swap the part at run time and combine parts
# freely.


class Engine:
    def __init__(self, horsepower, fuel):
        self.horsepower = horsepower
        self.fuel = fuel

    def start(self):
        return f"{self.fuel} engine ({self.horsepower}hp) started"


class GPS:
    def route(self, destination):
        return f"routing to {destination}"


class Car:
    """A Car HAS AN engine; it is not a kind of engine."""

    def __init__(self, model, engine, gps=None):
        self.model = model
        self.engine = engine          # composition: an Engine object inside the Car
        self.gps = gps                # an OPTIONAL part

    def start(self):
        return f"{self.model}: {self.engine.start()}"     # ask the engine to do it

    def navigate(self, destination):
        if self.gps is None:
            return f"{self.model} has no GPS fitted"
        return f"{self.model}: {self.gps.route(destination)}"


basic = Car("Runabout", Engine(90, "petrol"))
deluxe = Car("Voyager", Engine(320, "electric"), GPS())

for car in (basic, deluxe):
    print(" ", car.start())
    print(" ", car.navigate("Mumbai"))
print()

# Swap a part at run time - impossible with inheritance:
basic.engine = Engine(150, "hybrid")
print("  after an engine swap:", basic.start())
print()

print("  Rule of thumb:")
print("    IS-A  -> inheritance   (a Manager IS AN Employee)")
print("    HAS-A -> composition   (a Car HAS AN Engine)")
print("    unsure -> composition. It's easier to change your mind later.")
print()


# =============================================================================
# PART 6 — COMMON MISTAKES
# =============================================================================
print(LINE)
print("PART 6 — COMMON MISTAKES")
print(LINE)

# MISTAKE 1: forgetting super().__init__(). The parent's setup never runs, and
#   you get AttributeError later when a missing attribute is used.
class BrokenChild(Employee):
    def __init__(self, name):
        self.nickname = name              # forgot super().__init__()

try:
    BrokenChild("Zara").describe()
except AttributeError as error:
    print("  missing super().__init__():", error)

# MISTAKE 2: inheriting for code reuse rather than a real IS-A relationship.
#   If "a Foo IS A Bar" sounds wrong out loud, use composition.

# MISTAKE 3: deep hierarchies. Three or more levels and nobody can tell which
#   version of a method is actually running. Keep it shallow.

# MISTAKE 4: overriding a method with a different signature, so the polymorphic
#   loop breaks on one subclass. Keep parameters compatible.

# MISTAKE 5: a mutable class attribute shared across the whole hierarchy - the
#   same trap as lesson 16, now affecting every subclass too.

# MISTAKE 6: checking type(x) == Manager instead of isinstance(x, Manager).
#   The first fails for subclasses of Manager; isinstance handles them.

# MISTAKE 7: reaching for inheritance when a function would do. Not every
#   problem is a taxonomy.
print()


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * class Child(Parent):  inherits every attribute and method of Parent.
#   * A child can OVERRIDE a method by defining one with the same name.
#   * super().__init__(...) runs the parent's setup - always call it.
#     super().method() runs the parent's version, so you can extend it.
#   * Polymorphism: loop over mixed objects and call the same method on each.
#   * isinstance(obj, Parent) is True for children too.
#   * Duck typing: Python only needs the method to exist.
#   * ABC + @abstractmethod force children to write certain methods.
#   * IS-A -> inherit.  HAS-A -> hold it as an attribute (composition).
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. What does  class Manager(Employee):  mean?
#   Q2. Why must a child's __init__ call super().__init__(...)?
#   Q3. A Manager is passed to  isinstance(x, Employee).  True or False?
#   Q4. A Car and an Engine - inheritance or composition?
#   Q5. What happens if you try to create an object from an abstract class?
#
# ANSWERS
#   A1. Manager is a new class that starts with everything Employee has.
#   A2. Otherwise the parent's setup (self.name etc.) never runs, and those
#       attributes don't exist.
#   A3. True - a Manager IS an Employee.
#   A4. Composition. A car HAS an engine; it isn't a kind of engine.
#   A5. TypeError - abstract classes are templates, not usable objects.


# =============================================================================
# EXERCISES
# =============================================================================
#
# WARM-UP A (easy) — Override one method
#   Write class Animal with a speak() method returning "...". Write
#   class Dog(Animal) whose speak() returns "Woof". Print Dog().speak().
#
# WARM-UP B (easy) — One loop, two kinds
#   Loop over [Animal(), Dog()] and print each one's speak().
#
# WARM-UP C (easy) — isinstance
#   Print isinstance(Dog(), Animal) and isinstance(Animal(), Dog).
#   Make sure you can explain both answers.
#
# EXERCISE 1 (medium) — Shapes
#   Write a Shape base class with an abstract area() and perimeter(). Implement
#   Circle, Rectangle and Triangle. Loop over a list of mixed shapes, printing
#   each one's name and area, sorted by area.
#
# EXERCISE 2 (easy) — Extend the payroll
#   Add a ContractorEmployee (paid a fixed day rate for days worked) to PART 1.
#   Confirm the PART 2 report loop needs no changes at all.
#
# EXERCISE 3 (medium) — Notification system
#   Abstract Notifier with send(message). Implement EmailNotifier,
#   SmsNotifier and SlackNotifier (each just returns what it would do). Write
#   notify_all(notifiers, message) that uses them polymorphically.
#
# EXERCISE 4 (medium) — Animal hierarchy done properly
#   Animal -> Dog, Cat, Bird. Each overrides speak() and move(). Bird also has
#   can_fly. Show it working, then argue whether Penguin should inherit from
#   Bird - and what you'd do about fly().
#
# EXERCISE 5 (challenge) — Composition refactor
#   Take the Cart from lesson 16 and extract the pricing rules into a separate
#   PricingPolicy object that the Cart holds. Then create two policies
#   (standard and black-friday) and swap between them on the same cart.
#
# EXERCISE 6 (medium) — Duck typing
#   Write three unrelated classes that each have a `.to_dict()` method. Write
#   one function that serialises any of them to JSON. No shared parent.
#
# EXERCISE 7 (challenge) — Read the MRO
#   Build a small diamond: A, then B(A) and C(A), then D(B, C). Give each a
#   method with the same name and print D().method() plus D.__mro__. Work out
#   why that particular version ran.

# --- your exercise code goes below this line -------------------------------


# ---------------------------------------------------------------------------


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP A
#   class Animal:
#       def speak(self):
#           return "..."
#   class Dog(Animal):
#       def speak(self):
#           return "Woof"
#   print(Dog().speak())               # -> Woof
#
# WARM-UP B
#   for creature in [Animal(), Dog()]:
#       print(creature.speak())        # -> ...   then   Woof
#
# WARM-UP C
#   print(isinstance(Dog(), Animal))   # -> True  (a Dog IS an Animal)
#   print(isinstance(Animal(), Dog))   # -> False (not every Animal is a Dog)
#
# EXERCISE 1
#   from abc import ABC, abstractmethod
#   import math
#   class Shape(ABC):
#       @abstractmethod
#       def area(self):
#           ...
#       @abstractmethod
#       def perimeter(self):
#           ...
#   (`...` - three dots - is a real Python value meaning "nothing here yet".
#    It's a common placeholder body for abstract methods.)
#   class Circle(Shape):
#       def __init__(self, radius):
#           self.radius = radius
#       def area(self):
#           return math.pi * self.radius ** 2
#       def perimeter(self):
#           return 2 * math.pi * self.radius
#   class Rectangle(Shape):
#       def __init__(self, width, height):
#           self.width = width
#           self.height = height
#       def area(self):
#           return self.width * self.height
#       def perimeter(self):
#           return 2 * (self.width + self.height)
#   shapes = [Circle(3), Rectangle(4, 5)]
#   for shape in sorted(shapes, key=lambda s: s.area()):
#       print(type(shape).__name__, round(shape.area(), 2))
#
# EXERCISE 2
#   class ContractorEmployee(Employee):
#       def __init__(self, name, employee_id, day_rate, days_worked=0):
#           super().__init__(name, employee_id)
#           self.day_rate = day_rate
#           self.days_worked = days_worked
#       def calculate_pay(self):
#           return round(self.day_rate * self.days_worked, 2)
#   # payroll.append(ContractorEmployee("Zara", "E004", 400, 18))
#   # The report loop is untouched - that is polymorphism paying off.
#
# EXERCISE 3
#   class Notifier(ABC):
#       @abstractmethod
#       def send(self, message):
#           ...
#   class EmailNotifier(Notifier):
#       def send(self, message):
#           return f"EMAIL: {message}"
#   class SmsNotifier(Notifier):
#       def send(self, message):
#           return f"SMS: {message[:160]}"      # texts are short
#   def notify_all(notifiers, message):
#       results = []
#       for notifier in notifiers:
#           results.append(notifier.send(message))
#       return results
#
# EXERCISE 4
#   Penguin(Bird) is the classic argument against naive inheritance: it IS a
#   bird but cannot fly. Options: make fly() raise NotImplementedError (ugly),
#   or restructure so flying is a separate FlightBehaviour object held by the
#   bird - composition again.
#
# EXERCISE 6
#   import json
#   def serialise(obj):
#       return json.dumps(obj.to_dict(), indent=2)
#   # Works on ANY object with .to_dict() - no base class needed.
#
# EXERCISE 7
#   class A:
#       def who(self):
#           return "A"
#   class B(A):
#       def who(self):
#           return "B"
#   class C(A):
#       def who(self):
#           return "C"
#   class D(B, C):
#       pass
#   print(D().who())            # -> "B"
#   print([c.__name__ for c in D.__mro__])   # D, B, C, A, object
#   # Python searches left to right across the bases, so B wins.


print("=" * 70)
print("Lesson 17 complete. Next: 18_standard_library.py")
print("=" * 70)

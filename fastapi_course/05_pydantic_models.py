"""
===============================================================================
 FASTAPI COURSE - LESSON 05: PYDANTIC MODELS - VALIDATING DATA IN AND OUT
===============================================================================

Time: about 85 minutes (there's a good place for a break halfway).
Assumes: lessons 00-04.

THREE WAYS TO RUN THIS FILE:

    python 05_pydantic_models.py            the TOUR (read this first)
    python 05_pydantic_models.py --serve    a REAL server at /docs
    python 05_pydantic_models.py --check    grades your exercise answers


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. describe the shape of data once, as a model                   (PART 1)
  2. add rules to a field: ranges, lengths, patterns               (PART 2)
  3. use richer types: email, a fixed set of choices, optional,
     and a model inside a model                                    (PART 3)
  4. write your own rules when Field() can't say it                (PART 4)
  5. keep secrets out of responses with response_model             (PART 5)
  6. accept a deeply nested body, like an order                    (PART 6)
  7. apply a partial update without wiping other fields            (PART 7)
  8. reject unknown fields a client sneaks in                      (PART 8)

NEW WORDS - come back here whenever you forget one:

  Pydantic       the library FastAPI uses to check data. It works on its own
                 too - PART 1 uses it with no web server at all.
  model          a class describing the shape of some data: which fields it
                 has, what type each one is, and the rules they must follow
  BaseModel      the class your models inherit from (lesson 02 PART 5)
  field          one line inside a model:  price: float
  validation     checking data follows the rules
  ValidationError  the error Pydantic raises when it doesn't. FastAPI turns
                 that into a 422 response for you.
  Field(...)     extra rules for one field: gt=0, min_length=2, ...
  EmailStr       a type that only accepts something shaped like an email
  Literal[...]   a type that only accepts exactly the listed values
  nested model   a model used as the type of a field inside another model
  validator      your own checking function inside a model (PART 4)
  response_model the model FastAPI passes your reply through before sending.
                 Fields the model doesn't have are DROPPED - this is how you
                 stop passwords leaking.
  model_dump()   turn a model into a plain dict
  exclude_unset  "only the fields the client actually sent" (PART 7)
  schema         the description of a model that appears in /docs

PYTHON YOU NEED - all from lesson 02:
  * classes and inheritance     class UserCreate(UserBase):
  * type hints                  price: float
  * default values              stock: int = 0
  * decorators                  @field_validator("title")


-------------------------------------------------------------------------------
 THEORY: WHY MODELS EXIST
-------------------------------------------------------------------------------

A client can send your API ANYTHING:

    {"price": -500}      {"email": "not an email"}      {"is_admin": true}

Every value that arrives from outside is untrusted. You have two choices:

  A. Write checking code by hand in every route - dozens of `if` statements,
     repeated everywhere, and one forgotten check is a bug or a security hole.

  B. Describe the shape of the data ONCE, as a model class, and let Pydantic
     enforce it everywhere that model is used.

FastAPI is built around choice B. One model class does four jobs:

  1. VALIDATES   rejects data that breaks the rules (FastAPI -> 422)
  2. CONVERTS    "42" -> 42,  "2026-09-15" -> a real date object
  3. DOCUMENTS   every field, type and rule appears in /docs automatically
  4. SERIALISES  turns your data back into JSON-ready output


THE MOST IMPORTANT IDEA IN THIS LESSON: DIFFERENT MODELS FOR IN AND OUT
-----------------------------------------------------------------------
The data a client SENDS, the data you STORE, and the data you SEND BACK are
three different things, so they get three different models:

    UserCreate   what a client sends     username, email, password
    (a dict)     what you store          ..., hashed_password, is_active
    UserPublic   what you send back      username, email, id - NO password

Get this wrong and your API leaks password hashes. PART 5 shows it happening.
"""

import hashlib
from datetime import date, datetime, timezone
from typing import Literal

from fastapi import FastAPI
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from course_tools import check, section, show, start

app = FastAPI(
    title="Lesson 05 API",
    description="Validating data in and out with Pydantic models.",
    version="1.0.0",
)


def print_errors(error: ValidationError):
    """Print each problem in a ValidationError on one line: where, then what."""
    for problem in error.errors():
        where = ".".join(str(part) for part in problem["loc"]) or "(whole model)"
        print(f"      {where:<24} {problem['msg']}")


# =============================================================================
# PART 1 — A MODEL ON ITS OWN (no web server involved)
# =============================================================================
#
# Pydantic is a separate library. It works in any Python program - FastAPI
# just uses it. Seeing it alone first makes the FastAPI part obvious.
#
# A model is a class that inherits from BaseModel, with one type-hinted line
# per field. No __init__ - Pydantic generates it.

class Book(BaseModel):
    title: str
    pages: int
    price: float
    published: date            # a real date type, from the datetime module
    in_print: bool = True      # a default makes the field optional


def part1_demo():
    book = Book(title="Dune", pages="412", price=9.99, published="1965-08-01")
    print("  Book(title='Dune', pages='412', price=9.99, published='1965-08-01')")
    print(f"    book.pages     = {book.pages}   ({type(book.pages).__name__})"
          "   <- the text '412' became an int")
    print(f"    book.published = {book.published}   ({type(book.published).__name__})"
          "   <- the text became a date")
    print(f"    book.in_print  = {book.in_print}           <- the default was used")

    print("\n  book.model_dump()  -> a plain dict:")
    print("   ", book.model_dump())
    print("  book.model_dump_json()  -> JSON text, ready to send:")
    print("   ", book.model_dump_json())

    print("\n  Book.model_validate(a_dict)  -> build a model from a dict")
    print("  (this is what FastAPI does with every JSON body it receives):")
    data = {"title": "Refactoring", "pages": 448, "price": 47.99,
            "published": "2018-11-20"}
    print("   ", Book.model_validate(data))

    print("\n  Now BAD data. Pydantic raises ValidationError - and reports EVERY")
    print("  problem at once, not just the first one:")
    try:
        Book(title="Broken", pages=412.5, price="free", published="last tuesday")
    except ValidationError as error:
        print(f"    {error.error_count()} errors:")
        print_errors(error)

    print("\n  CONVERSION HAS LIMITS: '412' -> 412 is safe, so Pydantic does it.")
    print("  412.5 -> int would silently lose data, so it's an error instead.")

# TRY IT NOW (2 minutes):
#   In part1_demo above, change  pages="412"  to  pages="four hundred"  and
#   run the file. [A ValidationError: "Input should be a valid integer". The
#   model refused before a single line of your own code ran - that is the
#   whole idea of this lesson.]


# =============================================================================
# PART 2 — FIELD RULES WITH Field()
# =============================================================================
#
# A type alone says "this is a number". Field() adds rules about WHICH numbers.
# They're the same rules as Query()/Path() in lesson 04:
#
#   RULE                   APPLIES TO      MEANING
#   gt / ge / lt / le      numbers         > / >= / < / <=
#   min_length/max_length  text, lists     how long it may be
#   pattern                text            must match a regular expression
#   default                anything        the value when not sent
#   default_factory        lists, dicts    a FUNCTION that makes a fresh default
#
# A field with Field(...) but no `default` is still REQUIRED.

class ProductDraft(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(gt=0, le=100_000)          # 100_000 is just 100000
    discount_percent: int = Field(default=0, ge=0, le=90)
    sku: str = Field(pattern=r"^[A-Z]{3}-[0-9]{4}$")  # e.g. KEY-0042
    # default_factory=list calls list() for EVERY new object -> a fresh [] each
    # time. It's the explicit, always-safe form of lesson 02's None-then-create.
    tags: list[str] = Field(default_factory=list, max_length=5)


def part2_demo():
    draft = ProductDraft(name="Desk Lamp", price=24.50, sku="LMP-0042")
    print("  A valid draft:")
    print("   ", draft.model_dump())

    print("\n  One call breaking five rules:")
    try:
        ProductDraft(name="X", price=0, discount_percent=95, sku="lamp42",
                     tags=["a", "b", "c", "d", "e", "f"])
    except ValidationError as error:
        print_errors(error)


# =============================================================================
# PART 3 — RICHER TYPES: EMAIL, CHOICES, OPTIONAL AND NESTED MODELS
# =============================================================================

class Address(BaseModel):
    street: str = Field(min_length=1)
    city: str = Field(min_length=1)
    postcode: str = Field(min_length=3, max_length=10)
    country: str = Field(default="IN", min_length=2, max_length=2)


class Customer(BaseModel):
    name: str
    email: EmailStr                                 # checks it's a real email shape
    tier: Literal["standard", "vip"] = "standard"   # only these two values
    phone: str | None = None                        # optional, None if not sent
    address: Address                                # a model INSIDE a model


def part3_demo():
    customer = Customer(
        name="Priya",
        email="priya@example.com",
        address={"street": "12 MG Road", "city": "Pune", "postcode": "411001"},
    )
    print("  The nested dict became a real Address object:")
    print(f"    customer.address.city    = {customer.address.city}")
    print(f"    customer.address.country = {customer.address.country}   <- default")
    print(f"    customer.tier            = {customer.tier}   <- default")
    print(f"    customer.phone           = {customer.phone}   <- optional, not sent")

    print("\n  Bad data, including INSIDE the nested model. Look at the")
    print("  locations: address.postcode points exactly at the problem:")
    try:
        Customer(name="Priya", email="priya-at-example", tier="gold",
                 address={"street": "12 MG Road", "city": "Pune", "postcode": "4"})
    except ValidationError as error:
        print_errors(error)


# =============================================================================
# PART 4 — CUSTOM VALIDATORS: RULES Field() CAN'T EXPRESS
# =============================================================================
#
# Field() covers the common rules. For anything else, write a validator:
#
#   @field_validator("name")    checks/cleans ONE field. Runs after the type
#                               and Field() rules have passed. Return the
#                               (possibly cleaned) value, or raise ValueError.
#
#   @model_validator(mode="after")   checks the WHOLE object - for rules that
#                               involve more than one field, like "ends_at
#                               must be after starts_at". Return self.
#
# `@classmethod` on field validators: just include it, Pydantic requires it.
# `cls` is like `self`, but for the class instead of one object.

class EventCreate(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    starts_at: datetime
    ends_at: datetime
    attendee_emails: list[EmailStr] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def tidy_title(cls, value: str) -> str:
        # "  Team    lunch " -> "Team lunch": split on any whitespace, re-join
        cleaned = " ".join(value.split())
        if cleaned.lower() in ["untitled", "test", "event"]:
            raise ValueError("give the event a real title")
        return cleaned

    @field_validator("attendee_emails")
    @classmethod
    def no_duplicate_attendees(cls, emails: list[str]) -> list[str]:
        lowered = [email.lower() for email in emails]
        # a set keeps only unique values, so a shorter set means duplicates
        if len(set(lowered)) != len(lowered):
            raise ValueError("an attendee is listed more than once")
        return lowered

    @model_validator(mode="after")
    def ends_after_start(self) -> "EventCreate":
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


def part4_demo():
    event = EventCreate(
        title="  Team    lunch  ",
        starts_at="2026-09-20T12:00:00",
        ends_at="2026-09-20T13:30:00",
        attendee_emails=["Sidd@Example.com", "ana@example.com"],
    )
    print("  The validators CLEANED the data, not just checked it:")
    print(f"    title           = {event.title!r}")
    print(f"    attendee_emails = {event.attendee_emails}")
    print("  (!r in an f-string prints the quotes, so you can see the spaces are gone)")

    print("\n  A field validator failing:")
    try:
        EventCreate(title="untitled", starts_at="2026-09-20T12:00",
                    ends_at="2026-09-20T13:00")
    except ValidationError as error:
        print_errors(error)

    print("\n  The model validator failing - notice there's no single field to blame:")
    try:
        EventCreate(title="Retro", starts_at="2026-09-20T15:00",
                    ends_at="2026-09-20T14:00")
    except ValidationError as error:
        print_errors(error)


# =============================================================================
# PART 5 — IN vs OUT MODELS, OVER HTTP
# =============================================================================
#
# INHERITANCE, quickly: `class UserCreate(UserBase):` means "start with every
# field UserBase has, then add these". Shared fields are written once.

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-z0-9_]+$")
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=100)


class UserCreate(UserBase):          # IN: what the client sends
    password: str = Field(min_length=8, max_length=128)


class UserPublic(UserBase):          # OUT: what the client gets back
    id: int
    is_active: bool
    created_at: datetime


fake_users_db: list[dict] = []


def fake_hash(password: str) -> str:
    # A plain SHA-256 is NOT safe for real passwords (far too fast to brute
    # force). Lesson 09 replaces this with a proper password hasher.
    return "sha256$" + hashlib.sha256(password.encode()).hexdigest()


# response_model=UserPublic is the key line. Whatever the function returns,
# FastAPI passes it through UserPublic first: fields UserPublic doesn't have
# (like hashed_password) are DROPPED, and the result is checked against it.
@app.post("/users", response_model=UserPublic)
def create_user(user: UserCreate):
    # Build the stored record step by step.
    record = {"id": len(fake_users_db) + 1}
    record.update(user.model_dump(exclude={"password"}))   # every field but password
    record["hashed_password"] = fake_hash(user.password)
    record["is_active"] = True
    record["created_at"] = datetime.now(timezone.utc)
    fake_users_db.append(record)
    return record          # contains hashed_password - response_model strips it


@app.get("/users", response_model=list[UserPublic])
def list_users():
    return fake_users_db


# THE MISTAKE, ON PURPOSE: no response_model, so the raw dict goes out as-is.
# include_in_schema=False hides it from /docs - it only exists for the tour.
@app.get("/unsafe/users/{user_id}", include_in_schema=False)
def get_user_unsafe(user_id: int):
    for user in fake_users_db:
        if user["id"] == user_id:
            return user
    return {"error": "not found"}

# TRY IT NOW (2 minutes):
#   Delete  , response_model=UserPublic  from the @app.post("/users") line
#   above, and run the tour again. [hashed_password now appears in the POST
#   response as well. Put it back afterwards - one missing response_model is
#   the most common way real APIs leak data.]


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. You've seen the big idea: models check what comes
#  IN, and response_model controls what goes OUT. After the break: nested
#  bodies, partial updates, and locking models down.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 6 — NESTED BODIES: AN ORDER
# =============================================================================
#
# Real request bodies are rarely flat. Models nest as deeply as you need, and
# `list[OrderItem]` means "a list where EVERY element must be a valid OrderItem".

class OrderItem(BaseModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=1, le=100)
    # A real shop looks prices up on the SERVER - never trust a price the
    # client sends. It's in the body here only to keep the lesson about models.
    unit_price: float = Field(gt=0)


class OrderCreate(BaseModel):
    customer_email: EmailStr
    items: list[OrderItem] = Field(min_length=1)   # at least one item
    shipping_address: Address                       # reused from PART 3
    coupon: str | None = None


class OrderOut(BaseModel):
    order_id: int
    customer_email: EmailStr
    item_count: int
    subtotal: float
    discount: float
    total: float
    shipping_address: Address


COUPONS = {"SAVE10": 0.10, "WELCOME20": 0.20}
order_counter = [1000]      # a list so the function below can change the number


@app.post("/orders", response_model=OrderOut)
def create_order(order: OrderCreate):
    # order.items is a list of real OrderItem objects - use dots, not ["keys"]
    subtotal = 0.0
    item_count = 0
    for item in order.items:
        subtotal += item.quantity * item.unit_price
        item_count += item.quantity

    if order.coupon:
        rate = COUPONS.get(order.coupon, 0.0)      # unknown coupon -> no discount
    else:
        rate = 0.0
    discount = round(subtotal * rate, 2)

    order_counter[0] += 1
    return {
        "order_id": order_counter[0],
        "customer_email": order.customer_email,
        "item_count": item_count,
        "subtotal": round(subtotal, 2),
        "discount": discount,
        "total": round(subtotal - discount, 2),
        "shipping_address": order.shipping_address,
    }


# =============================================================================
# PART 7 — PARTIAL UPDATES: exclude_unset
# =============================================================================
#
# To change ONE field of a user (PATCH, lesson 06), the client sends only
# that field. So every field in an update model is optional:

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None


def part7_demo():
    stored = {"email": "sidd@example.com", "full_name": "Sidd"}
    print("  Stored user:", stored)

    changes = UserUpdate.model_validate({"full_name": "Siddheshwar"})
    print('\n  The client sent only: {"full_name": "Siddheshwar"}')

    print("\n  WRONG - model_dump() includes the fields they DIDN'T send, as None:")
    print("   ", changes.model_dump())
    wrong = stored.copy()                      # a copy, so `stored` is untouched
    wrong.update(changes.model_dump())         # .update() from lesson 01 PART 4
    print("    applying that would wipe the email:", wrong)

    print("\n  RIGHT - model_dump(exclude_unset=True) keeps only what was SENT:")
    print("   ", changes.model_dump(exclude_unset=True))
    right = stored.copy()
    right.update(changes.model_dump(exclude_unset=True))
    print("    applying that changes just the name:", right)

    clear = UserUpdate.model_validate({"full_name": None})
    print('\n  And if the client sends {"full_name": null} ON PURPOSE, it counts as')
    print("  sent - so they CAN clear a field deliberately:",
          clear.model_dump(exclude_unset=True))


# =============================================================================
# PART 8 — model_config: REJECTING UNKNOWN FIELDS
# =============================================================================
#
# Lesson 04 showed unknown fields being silently ignored. Usually fine - but
# imagine a client sending {"text": "hi", "is_admin": true} to an endpoint
# that later does `user.update(body)`. Rejecting fields you didn't define is
# a cheap defence against that ("mass assignment" attacks).
#
# model_config sets options for the whole model:
#   extra="forbid"             unknown fields -> validation error
#   str_strip_whitespace=True  "  hi  " -> "hi" for every text field

class CommentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    text: str = Field(min_length=1, max_length=500)
    rating: int | None = Field(default=None, ge=1, le=5)


@app.post("/comments")
def create_comment(comment: CommentCreate):
    return {"saved": comment.model_dump()}

# TRY IT NOW (2 minutes):
#   Delete the model_config line from CommentCreate and run the tour again.
#   [The sneaky {"is_admin": true} is now silently ACCEPTED and ignored
#   instead of rejected. Put the line back.]


# =============================================================================
# COMMON MISTAKES
# =============================================================================
#
# 1. Returning a stored dict with no response_model. Every internal field -
#    password hashes, internal notes - goes straight to the client. PART 5.
#
# 2. model_dump() instead of model_dump(exclude_unset=True) when applying a
#    partial update. Fields the client never mentioned get wiped. PART 7.
#
# 3. Forgetting `return value` in a field validator. The function returns
#    None, so the field silently BECOMES None.
#
# 4. Forgetting `return self` in a model validator - same problem, whole model.
#
# 5. `tags: list[str] = Field(default=[])` - works in Pydantic, but
#    default_factory=list says what you mean and is safe everywhere.
#
# 6. One giant model used for input AND output AND storage. Split them:
#    XCreate (in), XUpdate (partial in), XPublic (out).
#
# 7. Using dict syntax on a model: order["items"] -> TypeError.
#    Models use dots: order.items. model_dump() gives you a dict if you need one.


# =============================================================================
# Used by EXERCISE 4 - leave this here
# =============================================================================

fake_employees_db = [
    {"id": 1, "name": "Priya Sharma", "department": "Engineering",
     "salary": 145000, "personal_email": "priya.home@example.com"},
    {"id": 2, "name": "Tom Baker", "department": "Sales",
     "salary": 98000, "personal_email": "tom.b@example.com"},
]


# =============================================================================
# YOUR EXERCISE CODE GOES HERE - above the tour, so FastAPI registers it
# =============================================================================




# =============================================================================
# THE TOUR — runs when you execute this file with no flags
# =============================================================================

def tour(client):
    section("PART 1: A MODEL ON ITS OWN - no web server involved")
    part1_demo()

    section("PART 2: FIELD RULES WITH Field()")
    part2_demo()

    section("PART 3: EMAIL, CHOICES, OPTIONAL AND NESTED MODELS")
    part3_demo()

    section("PART 4: CUSTOM VALIDATORS")
    part4_demo()

    section("PART 5: IN vs OUT MODELS - now over HTTP")
    show(client, "POST", "/users", note="the body includes a password...",
         json={"username": "sidd", "email": "sidd@example.com",
               "full_name": "Sidd", "password": "correct-horse-battery"})
    print("\n  ...and the response has NO password and NO hashed_password.")
    print("  response_model=UserPublic removed them.")
    show(client, "POST", "/users", note="three rules broken at once",
         json={"username": "Sidd Dev", "email": "nope", "password": "short"})
    show(client, "GET", "/users", note="the list uses list[UserPublic] - still safe")
    show(client, "GET", "/unsafe/users/1",
         note="THE MISTAKE: the same data with NO response_model")
    print("\n  hashed_password just leaked to the client. One missing")
    print("  response_model is all it takes. This is why OUT models exist.")

    section("PART 6: NESTED BODIES - an order")
    show(client, "POST", "/orders", note="a valid order with a coupon",
         json={"customer_email": "ana@example.com",
               "items": [{"product_id": 1, "quantity": 2, "unit_price": 89.99},
                         {"product_id": 3, "quantity": 1, "unit_price": 32.50}],
               "shipping_address": {"street": "4 Park St", "city": "Kolkata",
                                    "postcode": "700016"},
               "coupon": "SAVE10"})
    response = show(client, "POST", "/orders", note="problems deep inside the body",
                    json={"customer_email": "ana@example.com",
                          "items": [{"product_id": 1, "quantity": 0, "unit_price": 89.99}],
                          "shipping_address": {"street": "4 Park St",
                                               "city": "Kolkata", "postcode": "7"}})
    print("\n  Each error's loc is the full path to the bad value:")
    for problem in response.json()["detail"]:
        print("    " + " -> ".join(str(part) for part in problem["loc"]))
    print("  (items -> 0 means the FIRST item in the list - lists count from 0)")

    section("PART 7: PARTIAL UPDATES - exclude_unset")
    part7_demo()

    section("PART 8: REJECTING UNKNOWN FIELDS")
    show(client, "POST", "/comments", note="extra spaces are stripped",
         json={"text": "   Great course!   ", "rating": 5})
    show(client, "POST", "/comments", note="a sneaky extra field",
         json={"text": "hi", "is_admin": True})

    section("SEE THE MODELS IN THE DOCS")
    print("  Run  python 05_pydantic_models.py --serve  and open /docs.")
    print("  Scroll to the bottom: the 'Schemas' section lists every model,")
    print("  every field, and every rule - generated from the classes above.")


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * A model is a class of type-hinted fields. Pydantic writes the __init__,
#     checks every value, converts what it safely can, and documents it.
#   * A failed check raises ValidationError, which FastAPI turns into a 422
#     listing EVERY problem at once, each with the exact location.
#   * Field() adds rules to one field (gt, min_length, pattern,
#     default_factory). A validator handles anything Field() can't express -
#     and can CLEAN a value, not just check it.
#   * Models nest: a field can be another model, or a list of them.
#   * IN and OUT are different models. response_model drops every field the
#     out-model doesn't have. That is how passwords stay out of responses.
#   * For a partial update use model_dump(exclude_unset=True), or you'll wipe
#     fields the client never mentioned.
#   * extra="forbid" rejects fields you didn't define.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. A client sends pages as "412". What does  pages: int  do with it?
#       And with "412.5"?
#   Q2. Which one line stops a stored password hash reaching the client?
#   Q3. A field validator checks a value but forgets to return it. What is
#       the field's value afterwards?
#   Q4. A PATCH sends only {"full_name": "X"}. Why is plain model_dump()
#       dangerous here?
#   Q5. When would you use a model validator instead of a field validator?
#
# ANSWERS
#   A1. "412" becomes the number 412 - a safe conversion. "412.5" is
#       rejected, because turning it into an int would silently lose data.
#   A2. response_model=UserPublic on the route.
#   A3. None - the function returned nothing, so the field becomes None.
#   A4. It includes every field the client did NOT send, as None, so applying
#       it wipes the email. Use exclude_unset=True.
#   A5. When the rule involves more than one field, like "ends_at must be
#       after starts_at".


# =============================================================================
# EXERCISES
# =============================================================================
#
# Write your code in the "YOUR EXERCISE CODE GOES HERE" space above the tour,
# then run:
#     python 05_pydantic_models.py --check
#
# Do the WARM-UPS first - each practises ONE idea from this lesson.
#
# WARM-UP 1 (easy) — A tiny model  (POST /notes)
#   Write a NoteCreate model with:
#       title   text, at least 2 characters
#       done    True/False, defaulting to False
#   Add POST /notes that just returns the note it was given.
#
# WARM-UP 2 (easy) — Hide a field  (GET /temperature)
#   Write a TemperatureOut model with ONLY a celsius field (a number).
#   Add GET /temperature with response_model=TemperatureOut, returning
#   {"celsius": 21.5, "sensor_id": "kitchen-3"}. The sensor_id must not
#   reach the client.
#
# EXERCISE 1 (medium) — A model with rules  (POST /products)
#   Write a ProductCreate model:
#       name    text, 2 to 100 characters
#       price   a number greater than 0
#       stock   a whole number, 0 or more, defaulting to 0
#       tags    a list of text, defaulting to an empty list
#   Keep products in a list called products_db. Add POST /products that
#   stores the product and returns {"id": <new id>, ...all its fields}.
#
# EXERCISE 2 (challenge) — A signup form  (POST /signup)
#   Write a SignupForm model:
#       username          3 to 20 characters. A field validator removes spaces
#                         from both ENDS, rejects a space INSIDE the name with
#                         a ValueError, and returns it lowercased.
#       email             a valid email
#       password          at least 8 characters
#       confirm_password  text
#   A model validator must raise ValueError if the two passwords differ.
#   Write a SignupOut model with ONLY username and email.
#   Add POST /signup with response_model=SignupOut that returns the form.
#
# EXERCISE 3 (easy) — Strict settings  (POST /settings)
#   Write a ThemeSettings model:
#       theme      exactly one of "light", "dark", "system"
#       font_size  a whole number from 10 to 32, defaulting to 14
#   Unknown fields must be REJECTED. POST /settings returns the settings.
#
# EXERCISE 4 (medium) — Hide private fields  (GET /employees/{employee_id})
#   fake_employees_db (above) contains salary and personal_email. Write an
#   EmployeePublic model with only id, name and department, and add the route
#   with response_model=EmployeePublic so the private fields never leave.
#   For now, only request ids that exist. An unknown id makes the route
#   return something that isn't an EmployeePublic, which FastAPI reports as
#   a 500 server error. Lesson 06 fixes that with a real 404.
#
# EXERCISE 5 (easy) — Read the schemas  (no automatic check)
#   Run --serve, open /docs, and find OrderCreate in the Schemas section.
#   Expand it until you reach Address. Then try POST /orders from /docs with
#   an empty items list and read the error.


def checks(client):
    check("the lesson's own POST /users still works",
          client.post("/users", json={"username": "check_user",
                                      "email": "check@example.com",
                                      "password": "long-enough-pw"}).status_code == 200)

    # --- WARM-UP 1 ---
    r = client.post("/notes", json={"title": "Buy milk"})
    check("WARM-UP 1: a valid note returns 200", r.status_code == 200)
    check("WARM-UP 1: done defaults to False",
          r.status_code == 200 and r.json().get("done") is False)
    check("WARM-UP 1: a 1-character title gives 422",
          client.post("/notes", json={"title": "x"}).status_code == 422)

    # --- WARM-UP 2 ---
    r = client.get("/temperature")
    check("WARM-UP 2: GET /temperature returns celsius",
          r.status_code == 200 and "celsius" in r.json())
    check("WARM-UP 2: response_model dropped sensor_id",
          r.status_code == 200 and "sensor_id" not in r.json())

    # --- EXERCISE 1 ---
    r = client.post("/products", json={"name": "Desk Lamp", "price": 24.5,
                                       "tags": ["home"]})
    body = r.json() if r.status_code == 200 else {}
    check("EXERCISE 1: a valid product returns 200", r.status_code == 200)
    check("EXERCISE 1: response has an id, and stock defaulted to 0",
          "id" in body and body.get("stock") == 0 and body.get("name") == "Desk Lamp")
    r = client.post("/products", json={"name": "No Tags", "price": 5})
    check("EXERCISE 1: tags defaults to an empty list",
          r.status_code == 200 and r.json().get("tags") == [])
    check("EXERCISE 1: price 0 gives 422",
          client.post("/products", json={"name": "Free", "price": 0}).status_code == 422)
    check("EXERCISE 1: a 1-character name gives 422",
          client.post("/products", json={"name": "A", "price": 5}).status_code == 422)
    check("EXERCISE 1: stock -1 gives 422",
          client.post("/products", json={"name": "Lamp", "price": 5,
                                         "stock": -1}).status_code == 422)

    # --- EXERCISE 2 ---
    good = {"username": "  Sidd_Dev ", "email": "sidd@example.com",
            "password": "supersecret1", "confirm_password": "supersecret1"}
    r = client.post("/signup", json=good)
    body = r.json() if r.status_code == 200 else {}
    check("EXERCISE 2: a valid signup returns 200", r.status_code == 200)
    check("EXERCISE 2: username is trimmed and lowercased -> 'sidd_dev'",
          body.get("username") == "sidd_dev")
    check("EXERCISE 2: the response contains NO password fields",
          r.status_code == 200 and "password" not in body
          and "confirm_password" not in body)
    check("EXERCISE 2: mismatched passwords give 422",
          client.post("/signup", json={**good, "confirm_password": "different1"}
                      ).status_code == 422)
    check("EXERCISE 2: a space inside the username gives 422",
          client.post("/signup", json={**good, "username": "sidd dev"}).status_code == 422)
    check("EXERCISE 2: a bad email gives 422",
          client.post("/signup", json={**good, "email": "sidd-at-example"}).status_code == 422)
    check("EXERCISE 2: a short password gives 422",
          client.post("/signup", json={**good, "password": "short",
                                       "confirm_password": "short"}).status_code == 422)

    # --- EXERCISE 3 ---
    r = client.post("/settings", json={"theme": "dark"})
    check("EXERCISE 3: {'theme': 'dark'} returns 200 with font_size 14",
          r.status_code == 200 and r.json().get("font_size") == 14
          and r.json().get("theme") == "dark")
    check("EXERCISE 3: theme 'blue' gives 422",
          client.post("/settings", json={"theme": "blue"}).status_code == 422)
    check("EXERCISE 3: font_size 50 gives 422",
          client.post("/settings", json={"theme": "light",
                                         "font_size": 50}).status_code == 422)
    check("EXERCISE 3: an unknown field gives 422",
          client.post("/settings", json={"theme": "dark",
                                         "is_admin": True}).status_code == 422)

    # --- EXERCISE 4 ---
    r = client.get("/employees/1")
    body = r.json() if r.status_code == 200 else {}
    check("EXERCISE 4: GET /employees/1 returns Priya Sharma",
          body.get("name") == "Priya Sharma" and body.get("department") == "Engineering")
    check("EXERCISE 4: salary and personal_email are NOT in the response",
          r.status_code == 200 and "salary" not in body and "personal_email" not in body)


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP 1
#   class NoteCreate(BaseModel):
#       title: str = Field(min_length=2, max_length=100)
#       done: bool = False
#
#   @app.post("/notes")
#   def create_note(note: NoteCreate):
#       return note
#
#   You can return the model itself - FastAPI turns it into JSON.
#
# WARM-UP 2
#   class TemperatureOut(BaseModel):
#       celsius: float
#
#   @app.get("/temperature", response_model=TemperatureOut)
#   def read_temperature():
#       return {"celsius": 21.5, "sensor_id": "kitchen-3"}
#
#   The route returns both fields; response_model keeps only celsius.
#
# EXERCISE 1
#   class ProductCreate(BaseModel):
#       name: str = Field(min_length=2, max_length=100)
#       price: float = Field(gt=0)
#       stock: int = Field(default=0, ge=0)
#       tags: list[str] = Field(default_factory=list)
#
#   products_db: list[dict] = []
#
#   @app.post("/products")
#   def create_product(product: ProductCreate):
#       record = {"id": len(products_db) + 1, **product.model_dump()}
#       products_db.append(record)
#       return record
#
# EXERCISE 2
#   class SignupForm(BaseModel):
#       username: str = Field(min_length=3, max_length=20)
#       email: EmailStr
#       password: str = Field(min_length=8)
#       confirm_password: str
#
#       @field_validator("username")
#       @classmethod
#       def clean_username(cls, value: str) -> str:
#           value = value.strip()
#           if " " in value:
#               raise ValueError("username can't contain spaces")
#           return value.lower()
#
#       @model_validator(mode="after")
#       def passwords_match(self) -> "SignupForm":
#           if self.password != self.confirm_password:
#               raise ValueError("passwords do not match")
#           return self
#
#   class SignupOut(BaseModel):
#       username: str
#       email: EmailStr
#
#   @app.post("/signup", response_model=SignupOut)
#   def signup(form: SignupForm):
#       return form
#
#   Returning the whole form is SAFE here because response_model=SignupOut
#   keeps only username and email. That's the point of the exercise.
#
# EXERCISE 3
#   class ThemeSettings(BaseModel):
#       model_config = ConfigDict(extra="forbid")
#
#       theme: Literal["light", "dark", "system"]
#       font_size: int = Field(default=14, ge=10, le=32)
#
#   @app.post("/settings")
#   def save_settings(settings: ThemeSettings):
#       return settings
#
#   You can return a model directly - FastAPI turns it into JSON.
#
# EXERCISE 4
#   class EmployeePublic(BaseModel):
#       id: int
#       name: str
#       department: str
#
#   @app.get("/employees/{employee_id}", response_model=EmployeePublic)
#   def get_employee(employee_id: int):
#       for employee in fake_employees_db:
#           if employee["id"] == employee_id:
#               return employee
#
#   If no employee matches, the loop ends and the function returns None.
#   None isn't a valid EmployeePublic, so FastAPI raises a 500 error. That's
#   the right instinct - FastAPI refuses to send data that breaks your
#   contract - and lesson 06's HTTPException turns it into a proper 404.
#
# EXERCISE 5
#   No code. The empty list fails Field(min_length=1) on items, and the
#   error's loc is ["body", "items"].


if __name__ == "__main__":
    start(app, tour, checks)


print("\nNext: python 06_crud_and_errors.py")

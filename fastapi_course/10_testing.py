"""
===============================================================================
 FASTAPI COURSE - LESSON 10: TESTING YOUR API WITH PYTEST
===============================================================================

Time: about 100 minutes (there's a good place for a break halfway).
Assumes: lessons 00-09.

FOUR WAYS TO USE THIS FILE:

    python 10_testing.py            the TOUR (read this first)
    python 10_testing.py --serve    the shop API as a real server at /docs
    pytest 10_testing.py -v         run every test in this file yourself
    python 10_testing.py --check    grades the TESTS you write


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. keep business rules in plain functions, so they're easy to test (PART 1)
  2. read the shop API you'll be testing                             (PART 2)
  3. write unit tests: call a function, check what comes back        (PART 3)
  4. give every test a fresh database with a fixture                 (PART 4)
  5. write API tests that send real requests                         (PART 5)
  6. swap a real email service for a fake one                        (PART 6)
  7. run pytest the way you will at work                             (PART 7)

NEW WORDS - come back here whenever you forget one:

  test         code that checks your code. A function named test_something.
  pytest       the tool that finds and runs those functions
  assert       "this must be true". If it isn't, the test fails.
  unit test    tests ONE plain function - no HTTP, no database. Fast.
  API test     sends a real request through TestClient to your app
  fixture      setup a test asks for by naming it as a parameter - exactly
               like a FastAPI dependency (lesson 07)
  isolation    every test starting from the same clean state, so tests can't
               break each other
  arrange,     the shape of nearly every good test: set it up, do the one
  act, assert  thing, check what happened
  parametrize  running the same test once per row of example data
  pytest.raises  checking that something DOES raise an error
  monkeypatch  changing something for ONE test, then putting it back
  fake         a stand-in for a real service (here: a mailer that records
               emails instead of sending them)
  happy path   the case where everything goes right. Bugs live elsewhere.
  boundary     the edge of a rule - "free shipping from $50" means testing
               $49.99 AND $50.00
  mutation     deliberately breaking the code to check your tests notice.
  testing      This lesson's grader does it to YOUR tests.
  regression   a bug that comes back. Tests are how you stop that.

PYTHON YOU NEED:
  * functions, and calling them            (lesson 02)
  * dicts and lists                        (lesson 01)
  * yield, for fixtures                    (lesson 07 PART 5)
  * f-strings, for readable assert messages


-------------------------------------------------------------------------------
 THEORY: WHY WRITE TESTS
-------------------------------------------------------------------------------

You change one line in the discount code. Did checkout still work? Did
cancelling an order still put the stock back? Did you just let customers read
each other's orders?

Clicking through /docs after every change doesn't scale past a handful of
routes, and you WILL forget one. A test is code that checks your code. A few
hundred of them run in seconds, identically, every single time.


WHAT A TEST LOOKS LIKE
----------------------
pytest runs every function whose name starts with test_. Inside, you use
Python's plain `assert` statement. If every assert holds, the test passes.

    def test_notebooks_cost_the_right_amount(client):
        # ARRANGE - set up what the test needs
        body = {"items": [{"product_id": 1, "quantity": 2}]}

        # ACT - do the ONE thing being tested
        response = client.post("/orders", headers=ASHA, json=body)

        # ASSERT - check what happened
        assert response.status_code == 201
        assert response.json()["total_cents"] == 2999

Arrange, Act, Assert. Nearly every good test has that shape.


TWO KINDS OF TEST IN A BACKEND
------------------------------
  UNIT TESTS   call one plain function directly: no HTTP, no database.
               Tiny and instant, so write lots. Best for business rules
               like "free shipping from $50".

  API TESTS    send real requests through TestClient to the real app, with
               a fresh test database. They test what clients actually
               experience: status codes, bodies, auth. These are the
               backbone of a backend's test suite.

(There's a third kind - end-to-end tests that drive a real browser against a
running system - but they're slow and fragile, so teams keep only a few.)


THE ONE IDEA THAT MATTERS MOST
------------------------------
A test is only worth something if it FAILS when the code is wrong. A test
that passes no matter what the code does is decoration.

So this lesson's grader doesn't just run your tests. It also runs them
against copies of the shop with real bugs slipped in, one bug at a time, and
checks that your tests notice each one. That's called MUTATION TESTING.

You've been using TestClient since lesson 03. Every tour was a test without
the asserts. Now you add them.
"""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from sqlalchemy.pool import StaticPool

from course_tools import check, section, show, start

LESSON_FILE = Path(__file__).resolve()
THIS_MODULE = sys.modules[__name__]


# =============================================================================
# PART 1 — THE BUSINESS RULES: PLAIN FUNCTIONS          would live in: pricing.py
# =============================================================================
#
# Money is stored as whole CENTS (an int), never as a float. Floats can't
# represent most decimals exactly: 0.1 + 0.2 == 0.30000000000000004. A shop
# that loses a fraction of a cent on every order gets audited. 1250 is $12.50.
#
# Keeping rules in plain functions, separate from the routes, is what makes
# them easy to unit test: no client, no database, just call the function.

COUPONS = {"SAVE10": 10, "HALFOFF": 50}         # code -> percent off
SHIPPING_CENTS = 499
FREE_SHIPPING_FROM_CENTS = 5000


def calculate_total(subtotal_cents: int, coupon: str | None = None) -> dict:
    """Work out an order's money, in whole cents.

    RULES - exercise 1 tests these:
      1. A coupon takes a percentage off the subtotal, rounded DOWN to a whole
         cent. Codes work in any case: "save10", "SAVE10" and "Save10" match.
      2. An unknown coupon raises ValueError.
      3. Shipping costs $4.99, but is FREE when the amount AFTER the discount
         is $50.00 or more.
      4. A negative subtotal raises ValueError.
    """
    if subtotal_cents < 0:
        raise ValueError("subtotal can't be negative")

    discount_cents = 0
    if coupon is not None:
        percent = COUPONS.get(coupon.upper())
        if percent is None:
            raise ValueError(f"Unknown coupon: {coupon}")
        discount_cents = subtotal_cents * percent // 100    # // rounds down

    after_discount = subtotal_cents - discount_cents
    shipping_cents = 0 if after_discount >= FREE_SHIPPING_FROM_CENTS else SHIPPING_CENTS
    return {
        "subtotal_cents": subtotal_cents,
        "discount_cents": discount_cents,
        "shipping_cents": shipping_cents,
        "total_cents": after_discount + shipping_cents,
    }


def line_total(unit_price_cents: int, quantity: int) -> int:
    return unit_price_cents * quantity


def format_money(cents: int) -> str:
    # :, adds thousands commas.  :02d pads to 2 digits, so 5 cents is "05".
    return f"${cents // 100:,}.{cents % 100:02d}"


# =============================================================================
# PART 2 — THE SHOP API UNDER TEST          would live in: models.py, routers/...
# =============================================================================
#
# Nothing new here - it's lessons 06 to 09 squeezed together. Read it quickly,
# then spend your time on PARTS 3 to 6, which are the tests.

engine = create_engine("sqlite://", poolclass=StaticPool,
                       connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    # Stored as plain text to keep this lesson short. A real app stores a HASH
    # of each API key, exactly like passwords in lesson 09.
    api_key: Mapped[str] = mapped_column(String(100), unique=True)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price_cents: Mapped[int]
    stock: Mapped[int]


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[str] = mapped_column(String(20), default="placed")
    subtotal_cents: Mapped[int]
    discount_cents: Mapped[int]
    shipping_cents: Mapped[int]
    total_cents: Mapped[int]

    lines: Mapped[list["OrderLine"]] = relationship(cascade="all, delete-orphan")


class OrderLine(Base):
    __tablename__ = "order_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    unit_price_cents: Mapped[int]


def seed_database(session: Session) -> None:
    session.add_all([
        Customer(name="Asha", email="asha@example.com", api_key="key-asha"),
        Customer(name="Ben", email="ben@example.com", api_key="key-ben"),
        Product(name="Notebook", price_cents=1250, stock=10),
        Product(name="Fountain pen", price_cents=3499, stock=3),
        Product(name="Ink bottle", price_cents=899, stock=0),
        Product(name="Desk lamp", price_cents=4999, stock=5),
    ])
    session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        if session.scalar(select(func.count(Customer.id))) == 0:
            seed_database(session)
    yield


app = FastAPI(title="Lesson 10 - Shop API",
              description="A small shop, built to be tested.",
              version="1.0.0", lifespan=lifespan)


def get_db():
    with Session(engine) as session:
        yield session


DbSession = Annotated[Session, Depends(get_db)]


# ---- An "external service", behind a dependency ----------------------------
# A real Mailer would call an email provider over HTTP. Tests must never do
# that: it's slow, it breaks when the provider is down, and it emails real
# people. Because routes GET their mailer from a dependency, a test can swap
# in a fake one with app.dependency_overrides (lesson 07 PART 8).

class Mailer:
    def send(self, to: str, subject: str, body: str) -> None:
        print(f"      [email to {to}] {subject}")


def get_mailer() -> Mailer:
    return Mailer()


MailerDep = Annotated[Mailer, Depends(get_mailer)]


def notify_order_placed(mailer: Mailer, customer: Customer, order: Order) -> None:
    mailer.send(to=customer.email, subject=f"Order #{order.id} confirmed",
                body=f"Thanks {customer.name}! Your total is {format_money(order.total_cents)}.")


def notify_order_cancelled(mailer: Mailer, customer: Customer, order: Order) -> None:
    mailer.send(to=customer.email, subject=f"Order #{order.id} cancelled",
                body="Your order was cancelled and will not be charged.")


# ---- Auth and lookups (lessons 07 and 09) ------------------------------------

def get_current_customer(db: DbSession,
                         x_api_key: Annotated[str | None, Header()] = None) -> Customer:
    if x_api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Missing X-Api-Key header",
                            headers={"WWW-Authenticate": "ApiKey"})
    customer = db.scalar(select(Customer).where(Customer.api_key == x_api_key))
    if customer is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid API key",
                            headers={"WWW-Authenticate": "ApiKey"})
    return customer


CurrentCustomer = Annotated[Customer, Depends(get_current_customer)]


def get_product_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product {product_id} not found")
    return product


def reserve_stock(product: Product, quantity: int) -> None:
    if quantity > product.stock:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Only {product.stock} of '{product.name}' in stock")
    product.stock -= quantity


def owns_order(customer: Customer, order: Order) -> bool:
    return order.customer_id == customer.id


def get_own_order(order_id: int, customer: CurrentCustomer, db: DbSession) -> Order:
    order = db.get(Order, order_id)
    if order is None or not owns_order(customer, order):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


OwnOrder = Annotated[Order, Depends(get_own_order)]


# ---- Schemas ------------------------------------------------------------------

class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price_cents: int
    stock: int


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=100)


class OrderCreate(BaseModel):
    items: list[OrderItemIn] = Field(min_length=1)
    coupon: str | None = None


class OrderLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int
    unit_price_cents: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    status: str
    subtotal_cents: int
    discount_cents: int
    shipping_cents: int
    total_cents: int
    lines: list[OrderLineOut]


# ---- Routes -------------------------------------------------------------------

@app.get("/products", response_model=list[ProductOut])
def list_products(db: DbSession):
    return db.scalars(select(Product).order_by(Product.id)).all()


@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: DbSession):
    return get_product_or_404(db, product_id)


@app.post("/orders", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def place_order(data: OrderCreate, customer: CurrentCustomer, db: DbSession,
                mailer: MailerDep):
    subtotal_cents = 0
    lines = []
    for item in data.items:
        product = get_product_or_404(db, item.product_id)
        reserve_stock(product, item.quantity)
        subtotal_cents += line_total(product.price_cents, item.quantity)
        lines.append(OrderLine(product_id=product.id, quantity=item.quantity,
                               unit_price_cents=product.price_cents))

    try:
        totals = calculate_total(subtotal_cents, data.coupon)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    # If anything above raised, nothing was committed: the session closes and
    # every stock change is thrown away. The whole order succeeds, or none of it.
    order = Order(customer_id=customer.id, lines=lines, **totals)
    db.add(order)
    db.commit()
    db.refresh(order)
    notify_order_placed(mailer, customer, order)
    return order


@app.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order: OwnOrder):
    return order


@app.post("/orders/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order: OwnOrder, customer: CurrentCustomer, db: DbSession,
                 mailer: MailerDep):
    if order.status == "cancelled":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Order is already cancelled")
    for line in order.lines:
        product = db.get(Product, line.product_id)
        product.stock += line.quantity
    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    notify_order_cancelled(mailer, customer, order)
    return order


# =============================================================================
# PART 3 — UNIT TESTS: CALLING FUNCTIONS DIRECTLY     would live in: tests/test_pricing.py
# =============================================================================
#
# Every test in this file is named test_example_... so the tour can run just
# these. In your own projects, any name starting with test_ works.

def test_example_small_order_pays_shipping():
    # Arrange + Act: one call is often enough for a pure function
    result = calculate_total(2000)

    # Assert the WHOLE result, not just one field - that catches more bugs
    assert result == {"subtotal_cents": 2000, "discount_cents": 0,
                      "shipping_cents": 499, "total_cents": 2499}


# ---- parametrize: one test, many cases ----------------------------------------
# Instead of four near-identical tests, list the cases. pytest runs the test
# once per row and reports each row separately - so you see exactly which
# case broke.
@pytest.mark.parametrize(("cents", "expected"), [
    (1250, "$12.50"),
    (5, "$0.05"),                 # a single-digit cents value - easy to get wrong
    (0, "$0.00"),
    (123456, "$1,234.56"),
])
def test_example_format_money(cents, expected):
    assert format_money(cents) == expected


# ---- pytest.raises: testing that errors happen ----------------------------------
# The test PASSES only if the code inside the `with` block raises ValueError.
# `match` also checks the error message contains that text.
def test_example_negative_subtotal_is_rejected():
    with pytest.raises(ValueError, match="negative"):
        calculate_total(-1)


# ---- monkeypatch: temporarily changing things -----------------------------------
# monkeypatch is a FIXTURE pytest gives you (PART 4 explains fixtures). It
# changes something for ONE test, then puts it back automatically - even if
# the test fails. Other tests never see the change.
def test_example_a_temporary_coupon(monkeypatch):
    monkeypatch.setitem(COUPONS, "STAFF25", 25)      # COUPONS["STAFF25"] = 25, for now

    result = calculate_total(8000, "STAFF25")

    assert result["discount_cents"] == 2000
    assert result["total_cents"] == 6000              # 6000 >= 5000: free shipping


# =============================================================================
# PART 4 — FIXTURES: SETUP THAT TESTS ASK FOR      would live in: tests/conftest.py
# =============================================================================
#
# A fixture is a function marked @pytest.fixture. A test asks for one by
# naming it as a parameter - exactly like FastAPI dependencies (lesson 07).
# pytest runs the fixture, and passes in what it yields.
#
# Code before `yield` is setup; code after `yield` is cleanup, run after the
# test finishes, pass OR fail. Lesson 07's yield dependency, again.
#
# THE MOST IMPORTANT FIXTURE: a FRESH database for EVERY test.
# If tests shared one database, a test that buys all the pens would break a
# later test that expects pens in stock - and the failures would change
# depending on which order tests ran in. Isolation makes every test stand alone.

@pytest.fixture
def client():
    test_engine = create_engine("sqlite://", poolclass=StaticPool,
                                connect_args={"check_same_thread": False})
    Base.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        seed_database(session)

    def get_test_db():
        with Session(test_engine) as session:
            yield session

    # Every route that asks for get_db now gets the test database instead.
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as test_client:
        yield test_client
    # Clean up ONLY what this fixture changed, so other overrides survive.
    app.dependency_overrides.pop(get_db, None)
    test_engine.dispose()


# A fake mailer that REMEMBERS what it was asked to send, instead of sending.
class FakeMailer:
    def __init__(self):
        self.sent: list[dict] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append({"to": to, "subject": subject, "body": body})


@pytest.fixture
def fake_mailer():
    mailer = FakeMailer()

    def use_the_fake_mailer():
        return mailer

    app.dependency_overrides[get_mailer] = use_the_fake_mailer
    yield mailer                      # the test can inspect mailer.sent
    app.dependency_overrides.pop(get_mailer, None)


# Plain constants are fine for simple shared values.
ASHA = {"X-Api-Key": "key-asha"}
BEN = {"X-Api-Key": "key-ben"}


# =============================================================================
# PART 5 — API TESTS: REQUESTS THROUGH TestClient    would live in: tests/test_orders.py
# =============================================================================

def test_example_list_products(client):
    response = client.get("/products")

    assert response.status_code == 200
    assert [p["name"] for p in response.json()] == [
        "Notebook", "Fountain pen", "Ink bottle", "Desk lamp"]


def test_example_unknown_product_is_404(client):
    response = client.get("/products/999")

    # Check the body too. A 404 from a MISSING ROUTE would also be a 404 -
    # the detail proves it came from our code.
    assert response.status_code == 404
    assert response.json() == {"detail": "Product 999 not found"}


# ---- Proof of isolation: these two tests can run in either order --------------
def test_example_isolation_buy_every_pen(client):
    response = client.post("/orders", headers=ASHA,
                           json={"items": [{"product_id": 2, "quantity": 3}]})
    assert response.status_code == 201
    assert client.get("/products/2").json()["stock"] == 0


def test_example_isolation_pens_are_back(client):
    # A brand-new database - the test above never happened, as far as we know.
    assert client.get("/products/2").json()["stock"] == 3


# TRY IT NOW (3 minutes):
#   In your terminal, run:
#       pytest 10_testing.py -k test_example -v
#   Then break one on purpose: change the expected stock in
#   test_example_isolation_pens_are_back from 3 to 2, run it again, and read
#   the failure. [pytest shows the assert, the actual value and the expected
#   one. Change it back. Seeing a test FAIL is how you know it works.]


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. You've seen unit tests, fixtures, a fresh database
#  per test, and API tests. After the break: faking an email service, the
#  pytest commands you'll use daily, and writing your own tests.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 6 — FAKING AN EXTERNAL SERVICE WITH A DEPENDENCY OVERRIDE
# =============================================================================

def test_example_cancelling_restocks_and_emails(client, fake_mailer):
    # ARRANGE: an order to cancel. Arranging through the API is fine - but the
    # asserts below are only about cancelling.
    placed = client.post("/orders", headers=ASHA,
                         json={"items": [{"product_id": 2, "quantity": 2}]})
    order_id = placed.json()["id"]

    # ACT
    response = client.post(f"/orders/{order_id}/cancel", headers=ASHA)

    # ASSERT: the response, the side effect on stock, and the email
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    assert client.get("/products/2").json()["stock"] == 3
    assert fake_mailer.sent[-1]["subject"] == f"Order #{order_id} cancelled"


def test_example_cannot_cancel_twice(client):
    order_id = client.post("/orders", headers=ASHA,
                           json={"items": [{"product_id": 1, "quantity": 1}]}).json()["id"]
    client.post(f"/orders/{order_id}/cancel", headers=ASHA)

    response = client.post(f"/orders/{order_id}/cancel", headers=ASHA)

    assert response.status_code == 409
    assert response.json()["detail"] == "Order is already cancelled"


# =============================================================================
# PART 7 — RUNNING PYTEST: THE COMMANDS YOU'LL ACTUALLY USE
# =============================================================================
#
#   pytest                          every test_*.py file under this folder
#   pytest 10_testing.py            one file (needed here: its name doesn't
#                                   start with test_, so pytest won't find it alone)
#   pytest 10_testing.py -v         one line per test, with its name
#   pytest 10_testing.py -k ex1     only tests whose name contains "ex1"
#   pytest 10_testing.py -x         stop at the first failure
#   pytest 10_testing.py -s         show print() output (normally hidden)
#   pytest 10_testing.py --tb=short shorter failure reports
#
# WARNINGS don't fail tests. pytest collects them in a "warnings summary" at
# the end. Read the file path first: a warning from .venv/.../site-packages
# (like the anyio "BlockingPortal" one you may see) comes from inside a
# library, not your code, and goes away when that library updates. A warning
# pointing at YOUR file is worth fixing.
#
# In a real project, tests live in a tests/ folder, shared fixtures go in
# tests/conftest.py (pytest loads it automatically), and the whole suite runs
# on every push to GitHub. Lesson 11's capstone is set up exactly like that.


# =============================================================================
# COMMON MISTAKES
# =============================================================================
#
# 1. Tests that depend on each other, or share a database. They pass alone,
#    fail together, and the failure moves around. One fresh database per test.
#
# 2. Only testing the happy path. Bugs live in the error paths: 401, 404, 409,
#    422, the boundary values. Most of your tests should be about those.
#
# 3. Asserting only the status code. A 200 with the wrong total is still a bug.
#
# 4. An assert that can never fail:
#        assert response.status_code == 200 or 201    # `or 201` is always True
#        assert response.status_code in (200, 201)     # what was meant
#
# 5. Testing a boundary from one side only. For "free from $50", test $49.99
#    AND $50.00. That's where off-by-one bugs hide.
#
# 6. Calling real external services (email, payments) from tests. Override
#    the dependency with a fake. PART 6.
#
# 7. Overrides that leak into other tests. Remove what you added, in fixture
#    cleanup, so one test's fake never affects the next.
#
# 8. Using floats for money, then asserting 0.1 + 0.2 == 0.3. Use cents.


# =============================================================================
# YOUR TESTS GO HERE - see EXERCISES below for what to write and how to name them
# =============================================================================




# =============================================================================
# THE GRADING MACHINERY - SCENERY, AND A SPOILER
# =============================================================================
#
# Skip this until you've finished the exercises - it lists the bugs the grader
# slips in, which gives the game away. After that, it's worth reading: it's
# ordinary monkeypatch and dependency_overrides code, and it's how the grader
# can break the shop without editing this file.

def bug_money_padding(monkeypatch):
    monkeypatch.setattr(THIS_MODULE, "format_money",
                        lambda cents: f"${cents // 100:,}.{cents % 100}")


def bug_shipping_boundary(monkeypatch):
    original = THIS_MODULE.calculate_total

    def broken(subtotal_cents, coupon=None):
        result = original(subtotal_cents, coupon)
        after_discount = result["subtotal_cents"] - result["discount_cents"]
        if after_discount == FREE_SHIPPING_FROM_CENTS:
            result["shipping_cents"] = SHIPPING_CENTS
            result["total_cents"] = after_discount + SHIPPING_CENTS
        return result

    monkeypatch.setattr(THIS_MODULE, "calculate_total", broken)


def bug_unknown_coupon_ignored(monkeypatch):
    original = THIS_MODULE.calculate_total

    def broken(subtotal_cents, coupon=None):
        if subtotal_cents >= 0 and coupon is not None and coupon.upper() not in COUPONS:
            coupon = None
        return original(subtotal_cents, coupon)

    monkeypatch.setattr(THIS_MODULE, "calculate_total", broken)


def bug_coupon_case_sensitive(monkeypatch):
    original = THIS_MODULE.calculate_total

    def broken(subtotal_cents, coupon=None):
        if coupon is not None and coupon not in COUPONS:
            raise ValueError(f"Unknown coupon: {coupon}")
        return original(subtotal_cents, coupon)

    monkeypatch.setattr(THIS_MODULE, "calculate_total", broken)


def bug_shipping_before_discount(monkeypatch):
    original = THIS_MODULE.calculate_total

    def broken(subtotal_cents, coupon=None):
        result = original(subtotal_cents, coupon)
        shipping = 0 if subtotal_cents >= FREE_SHIPPING_FROM_CENTS else SHIPPING_CENTS
        result["shipping_cents"] = shipping
        result["total_cents"] = subtotal_cents - result["discount_cents"] + shipping
        return result

    monkeypatch.setattr(THIS_MODULE, "calculate_total", broken)


def bug_stock_not_reduced(monkeypatch):
    def broken(product, quantity):
        if quantity > product.stock:
            raise HTTPException(status_code=409, detail="Not enough stock")

    monkeypatch.setattr(THIS_MODULE, "reserve_stock", broken)


def bug_oversell_allowed(monkeypatch):
    def broken(product, quantity):
        product.stock -= quantity

    monkeypatch.setattr(THIS_MODULE, "reserve_stock", broken)


def bug_quantity_ignored(monkeypatch):
    monkeypatch.setattr(THIS_MODULE, "line_total",
                        lambda unit_price_cents, quantity: unit_price_cents)


def bug_unknown_product_crash(monkeypatch):
    monkeypatch.setattr(THIS_MODULE, "get_product_or_404",
                        lambda db, product_id: db.get(Product, product_id))


def bug_auth_disabled(monkeypatch):
    def always_the_first_customer(db: DbSession) -> Customer:
        return db.scalar(select(Customer).order_by(Customer.id))

    monkeypatch.setitem(app.dependency_overrides, get_current_customer,
                        always_the_first_customer)


def bug_anyone_can_read(monkeypatch):
    monkeypatch.setattr(THIS_MODULE, "owns_order", lambda customer, order: True)


def bug_email_not_sent(monkeypatch):
    monkeypatch.setattr(THIS_MODULE, "notify_order_placed",
                        lambda mailer, customer, order: None)


def bug_email_wrong_recipient(monkeypatch):
    def broken(mailer, customer, order):
        mailer.send(to="orders@shop.example", subject=f"Order #{order.id} confirmed", body="")

    monkeypatch.setattr(THIS_MODULE, "notify_order_placed", broken)


def bug_email_sent_twice(monkeypatch):
    original = THIS_MODULE.notify_order_placed

    def broken(mailer, customer, order):
        original(mailer, customer, order)
        original(mailer, customer, order)

    monkeypatch.setattr(THIS_MODULE, "notify_order_placed", broken)


BUGS = {
    "money_padding": ("format_money drops the leading zero: 5 cents shows as $0.5",
                      bug_money_padding),
    "shipping_boundary": ("an order of exactly $50.00 is still charged shipping",
                          bug_shipping_boundary),
    "unknown_coupon_ignored": ("a made-up coupon is silently ignored, not rejected",
                               bug_unknown_coupon_ignored),
    "coupon_case_sensitive": ("coupons only work when typed in CAPITALS",
                              bug_coupon_case_sensitive),
    "shipping_before_discount": ("free shipping is judged BEFORE the coupon comes off",
                                 bug_shipping_before_discount),
    "stock_not_reduced": ("placing an order doesn't reduce the stock",
                          bug_stock_not_reduced),
    "oversell_allowed": ("you can order more than is in stock", bug_oversell_allowed),
    "quantity_ignored": ("the price ignores quantity: 3 notebooks cost the same as 1",
                         bug_quantity_ignored),
    "unknown_product_crash": ("an unknown product id crashes the server instead of 404",
                              bug_unknown_product_crash),
    "auth_disabled": ("the API key is ignored: every request acts as Asha",
                      bug_auth_disabled),
    "anyone_can_read": ("any customer can read any other customer's order",
                        bug_anyone_can_read),
    "email_not_sent": ("no confirmation email is sent", bug_email_not_sent),
    "email_wrong_recipient": ("the confirmation email goes to the shop, not the customer",
                              bug_email_wrong_recipient),
    "email_sent_twice": ("the confirmation email is sent twice", bug_email_sent_twice),
}

EXERCISE_BUGS = {
    1: ["shipping_boundary", "unknown_coupon_ignored", "coupon_case_sensitive",
        "shipping_before_discount"],
    2: ["stock_not_reduced", "oversell_allowed", "quantity_ignored", "unknown_product_crash"],
    3: ["auth_disabled", "anyone_can_read"],
    4: ["email_not_sent", "email_wrong_recipient", "email_sent_twice"],
}


# autouse=True: this fixture runs for EVERY test without being asked for.
# Normally it does nothing. When the grader sets the LESSON10_BUG environment
# variable, it slips that bug into the shop before the test runs - and
# monkeypatch takes it out again afterwards.
@pytest.fixture(autouse=True)
def inject_bug_for_grading(monkeypatch):
    bug_name = os.environ.get("LESSON10_BUG")
    if bug_name:
        _, apply_bug = BUGS[bug_name]
        apply_bug(monkeypatch)


def run_pytest(selection: str, bug: str | None = None,
               options: tuple[str, ...] = ()) -> subprocess.CompletedProcess:
    """Run this file's tests whose names contain `selection`, in a separate process."""
    command = [sys.executable, "-m", "pytest", str(LESSON_FILE), "-k", selection,
               "-p", "no:cacheprovider", "--no-header",
               # hide one warning that comes from inside a library, not this file
               "-W", "ignore:The anyio.abc.BlockingPortal alias is deprecated",
               *options]
    environment = {**os.environ, "LESSON10_BUG": bug or ""}
    return subprocess.run(command, capture_output=True, text=True,
                          cwd=LESSON_FILE.parent, env=environment)


def indent(text: str, spaces: int = 4) -> str:
    return "\n".join(" " * spaces + line for line in text.rstrip().splitlines())


# =============================================================================
# THE TOUR — runs when you execute this file with no flags
# =============================================================================

def tour(client):
    section("PART 1: A TEST IS JUST CODE THAT CHECKS CODE")
    assert format_money(1250) == "$12.50"
    print('  assert format_money(1250) == "$12.50"   -> nothing happens: it held')
    try:
        assert format_money(1250) == "$12.5"
    except AssertionError:
        print('  assert format_money(1250) == "$12.5"    -> AssertionError')
    print("\n  That's the whole trick. pytest finds every function named test_...,")
    print("  runs each one, and reports which ones raised.")

    section("PART 2: THE SHOP - through the same TestClient every tour has used")
    show(client, "GET", "/products/2")
    show(client, "POST", "/orders", note="2 notebooks with a lowercase coupon",
         headers=ASHA, json={"items": [{"product_id": 1, "quantity": 2}], "coupon": "save10"})
    print("\n  2500 - 250 discount = 2250, under $50, so 499 shipping: 2749.")
    print("  (The [email ...] line is the real Mailer. Tests swap in a fake.)")
    show(client, "POST", "/orders", note="Ink bottles are out of stock",
         headers=ASHA, json={"items": [{"product_id": 3, "quantity": 1}]})

    section("PART 3-6: RUNNING THE LESSON'S EXAMPLE TESTS")
    print("  $ pytest 10_testing.py -k test_example -v\n")
    result = run_pytest("test_example", options=("-v",))
    print(indent(result.stdout))
    print("\n  Every PASSED line is one test function - and each parametrize row")
    print("  of test_example_format_money counts as its own test.")

    section("WHAT A FAILING TEST LOOKS LIKE")
    print("  The same format_money tests, run against a copy of the shop with ONE")
    print("  bug slipped in: the cents lose their leading zero.\n")
    print("  $ pytest 10_testing.py -k test_example_format_money --tb=short\n")
    result = run_pytest("test_example_format_money", bug="money_padding",
                        options=("--tb=short",))
    print(indent(result.stdout))
    print("""
  HOW TO READ THAT, bottom to top:
    * "short test summary info" lists WHICH tests failed - [5-$0.05] means
      the parametrize row where cents=5 and expected="$0.05"
    * the line starting with E shows the assert that failed, with the ACTUAL
      value on the left and the EXPECTED value on the right
    * two rows passed and two failed - so the bug is narrowed down to
      "cents values under 10", before you've opened the code""")

    section("NOW WRITE YOUR OWN")
    print("  Read the EXERCISES at the bottom of this file, write your tests in")
    print("  the 'YOUR TESTS GO HERE' space, and run them as you go:")
    print()
    print("      pytest 10_testing.py -k test_ex1_ -v")
    print()
    print("  Then  python 10_testing.py --check  runs them against the real shop")
    print("  AND against broken copies of it, to prove they catch real bugs.")


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * A test is a function named test_something that uses plain `assert`.
#     pytest finds them, runs them, and tells you which ones raised.
#   * Arrange, Act, Assert: set it up, do the one thing, check what happened.
#   * Unit tests call a plain function - fast, so write lots. API tests go
#     through TestClient and check what a real client would see.
#   * A fixture is setup a test asks for by name. Give every test a FRESH
#     database, so tests can never break each other.
#   * parametrize runs one test over many rows; pytest.raises checks that an
#     error happens; monkeypatch changes something for one test only.
#   * Never call real email or payment services in a test - override the
#     dependency with a fake that records what it was asked to do.
#   * A test only earns its place if it FAILS when the code is wrong. Test
#     boundaries ($49.99 and $50.00) and error paths, not just the happy path.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. Two tests pass alone but fail when run together. What's the usual cause?
#   Q2. Why assert the body, not just the status code?
#   Q3. Why is  assert response.status_code == 200 or 201  useless?
#   Q4. The rule is "free shipping from $50". Which amounts should you test?
#   Q5. How do you test that an email was sent, without sending one?
#
# ANSWERS
#   A1. They share state - usually one database. Give each test a fresh one.
#   A2. A 200 with the wrong total is still a bug.
#   A3. `or 201` is always true, so the assert can never fail. Use
#       `in (200, 201)`.
#   A4. Both sides of the line: $49.99 and exactly $50.00.
#   A5. Override the mailer dependency with a fake that records the message,
#       then assert on what it recorded.


# =============================================================================
# EXERCISES — WRITE TESTS THAT CATCH BUGS
# =============================================================================
#
# This time you don't write API code - you write TESTS for the shop above, in
# the "YOUR TESTS GO HERE" space. Start each test's name with its exercise's
# prefix, so the grader can find it, then describe the behaviour:
#
#     def test_ex1_free_shipping_starts_at_exactly_50_dollars(): ...
#
# Run your tests while you work:
#     pytest 10_testing.py -k test_ex1_ -v
#
# HOW GRADING WORKS
#   python 10_testing.py --check  runs each exercise's tests:
#     1. against the shop exactly as written - they must all PASS
#     2. against copies of the shop with a real bug slipped in, one bug at a
#        time - at least one of your tests must FAIL for each bug
#   You aren't told the bugs in advance. Think about what COULD go wrong with
#   each rule, and write a test that would notice. (The grader names any bug
#   your tests miss.)
#
# Do the WARM-UPS first - one unit test and one API test, both named
# test_warmup_... They aren't graded against hidden bugs; they just have to
# pass, so you can get used to the two shapes.
#
# WARM-UP 1 (easy) — A unit test
#   Write test_warmup_line_total_multiplies_price_by_quantity() asserting that
#   line_total(1250, 3) == 3750. No client needed.
#
# WARM-UP 2 (easy) — An API test
#   Write test_warmup_products_list_has_four_items(client) asserting that
#   GET /products returns 200 and a list of 4 products. Note the `client`
#   parameter: that's the fixture from PART 4.
#
# EXERCISE 1 (medium) — Unit tests for calculate_total  (names start test_ex1_)
#   Test every rule in calculate_total's docstring. You don't need the client:
#   just call the function. 4 hidden bugs.
#   Hint: for any "from $50" rule, test both sides of the line.
#
# EXERCISE 2 (medium) — API tests for POST /orders  (names start test_ex2_)
#   Use the client fixture and ASHA's headers. Cover:
#     * a good order: 201, and the right total_cents (use a quantity of 2 or
#       more - think about why)
#     * the product's stock really goes down afterwards (GET /products/{id})
#     * ordering more than the stock -> 409
#     * a product id that doesn't exist -> 404
#     * quantity 0 -> 422
#   4 hidden bugs. The seeded products are in seed_database().
#
# EXERCISE 3 (medium) — Auth and ownership tests  (names start test_ex3_)
#     * POST /orders with no X-Api-Key header -> 401
#     * Asha can read her own order with GET /orders/{id} -> 200
#     * Ben reading Asha's order -> 404
#   2 hidden bugs.
#
# EXERCISE 4 (challenge) — Test the confirmation email without sending one  (test_ex4_)
#   Use the fake_mailer fixture. After Asha places an order, check that
#   exactly ONE email was sent, that it went to asha@example.com, and that its
#   subject contains the new order's id. 3 hidden bugs.


def checks(client):
    runs = [("test_example", None), ("test_warmup_", None)]
    for number, bug_names in EXERCISE_BUGS.items():
        selection = f"test_ex{number}_"
        runs.append((selection, None))
        runs.extend((selection, bug) for bug in bug_names)

    print(f"  Running your tests {len(runs)} times - once against the real shop, then")
    print("  once per hidden bug. This takes a few seconds...\n")
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(
            lambda run: run_pytest(run[0], bug=run[1], options=("-x", "-q")), runs))
    outcome = dict(zip(runs, results))

    check("the lesson's own example tests pass",
          outcome[("test_example", None)].returncode == pytest.ExitCode.OK)

    warm_up = outcome[("test_warmup_", None)]
    if warm_up.returncode == pytest.ExitCode.NO_TESTS_COLLECTED:
        check("WARM-UPS: found tests named test_warmup_...", False)
    else:
        check("WARM-UPS: found tests named test_warmup_...", True)
        check("WARM-UPS: your warm-up tests pass",
              warm_up.returncode == pytest.ExitCode.OK)
        if warm_up.returncode != pytest.ExitCode.OK:
            print(indent("\n".join(warm_up.stdout.splitlines()[-12:]), 9))

    for number, bug_names in EXERCISE_BUGS.items():
        selection = f"test_ex{number}_"
        clean = outcome[(selection, None)]
        if clean.returncode == pytest.ExitCode.NO_TESTS_COLLECTED:
            check(f"EXERCISE {number}: found tests named {selection}...", False)
        else:
            check(f"EXERCISE {number}: your tests pass against the real shop",
                  clean.returncode == pytest.ExitCode.OK)
            if clean.returncode != pytest.ExitCode.OK:
                print(indent("\n".join(clean.stdout.splitlines()[-12:]), 9))

        tests_are_usable = clean.returncode == pytest.ExitCode.OK
        for bug in bug_names:
            description, _ = BUGS[bug]
            caught = (tests_are_usable
                      and outcome[(selection, bug)].returncode == pytest.ExitCode.TESTS_FAILED)
            check(f"EXERCISE {number}: catches the bug - {description}", caught)


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# There are many good answers. What matters is that each bug makes at least
# one test fail - and that each test's NAME says what behaviour it protects.
#
# WARM-UP 1
#   def test_warmup_line_total_multiplies_price_by_quantity():
#       assert line_total(1250, 3) == 3750
#
# WARM-UP 2
#   def test_warmup_products_list_has_four_items(client):
#       response = client.get("/products")
#       assert response.status_code == 200
#       assert len(response.json()) == 4
#
#   Asking for `client` is what gives this test its own fresh database.
#
# EXERCISE 1
#   def test_ex1_shipping_is_charged_just_under_50_dollars():
#       assert calculate_total(4999)["shipping_cents"] == 499
#
#   def test_ex1_free_shipping_starts_at_exactly_50_dollars():
#       assert calculate_total(5000)["shipping_cents"] == 0
#
#   def test_ex1_coupon_takes_a_percentage_off_rounded_down():
#       assert calculate_total(1999, "SAVE10")["discount_cents"] == 199   # not 199.9
#
#   def test_ex1_coupon_codes_ignore_case():
#       assert calculate_total(8000, "save10") == calculate_total(8000, "SAVE10")
#
#   def test_ex1_unknown_coupon_is_rejected():
#       with pytest.raises(ValueError):
#           calculate_total(8000, "FREESTUFF")
#
#   def test_ex1_free_shipping_uses_the_amount_after_the_discount():
#       result = calculate_total(5500, "SAVE10")       # 5500 - 550 = 4950
#       assert result["shipping_cents"] == 499
#       assert result["total_cents"] == 5449
#
#   The last one is the subtle one. With subtotal 5500, "before discount" and
#   "after discount" give different answers ONLY because the discount crosses
#   the $50 line. Good tests pick inputs where the right and wrong
#   implementations disagree.
#
# EXERCISE 2
#   def order_body(product_id, quantity):
#       return {"items": [{"product_id": product_id, "quantity": quantity}]}
#
#   def test_ex2_good_order_is_201_with_the_right_total(client):
#       response = client.post("/orders", headers=ASHA, json=order_body(1, 3))
#       assert response.status_code == 201
#       assert response.json()["total_cents"] == 3 * 1250 + 499
#
#   def test_ex2_ordering_reduces_the_stock(client):
#       client.post("/orders", headers=ASHA, json=order_body(2, 2))
#       assert client.get("/products/2").json()["stock"] == 1
#
#   def test_ex2_more_than_the_stock_is_409(client):
#       response = client.post("/orders", headers=ASHA, json=order_body(2, 4))
#       assert response.status_code == 409
#
#   def test_ex2_unknown_product_is_404(client):
#       response = client.post("/orders", headers=ASHA, json=order_body(999, 1))
#       assert response.status_code == 404
#
#   def test_ex2_quantity_zero_is_422(client):
#       response = client.post("/orders", headers=ASHA, json=order_body(1, 0))
#       assert response.status_code == 422
#
#   Why quantity 2 or more: with quantity 1, "price x quantity" and "just
#   the price" are the same number, so the quantity_ignored bug hides.
#   order_body doesn't start with test_, so pytest treats it as a helper.
#
#   The crash bug makes the app raise an exception. TestClient re-raises it
#   inside the test, which counts as a failure - so the 404 test catches it.
#
# EXERCISE 3
#   def test_ex3_no_api_key_is_401(client):
#       response = client.post("/orders", json={"items": [{"product_id": 1, "quantity": 1}]})
#       assert response.status_code == 401
#
#   def test_ex3_customers_can_only_read_their_own_orders(client):
#       order_id = client.post("/orders", headers=ASHA, json={
#           "items": [{"product_id": 1, "quantity": 1}]}).json()["id"]
#       assert client.get(f"/orders/{order_id}", headers=ASHA).status_code == 200
#       assert client.get(f"/orders/{order_id}", headers=BEN).status_code == 404
#
#   Checking the owner gets 200 matters too: without it, a bug that hid
#   EVERY order would pass the "Ben gets 404" check.
#
# EXERCISE 4
#   def test_ex4_one_confirmation_email_goes_to_the_customer(client, fake_mailer):
#       response = client.post("/orders", headers=ASHA, json={
#           "items": [{"product_id": 1, "quantity": 1}]})
#       order_id = response.json()["id"]
#
#       assert len(fake_mailer.sent) == 1
#       email = fake_mailer.sent[0]
#       assert email["to"] == "asha@example.com"
#       assert str(order_id) in email["subject"]
#
#   `len(...) == 1` catches "not sent" AND "sent twice" in one line.


if __name__ == "__main__":
    start(app, tour, checks)
    print("\nNext: lesson 11 - the capstone project")

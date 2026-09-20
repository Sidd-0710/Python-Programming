"""
===============================================================================
 FASTAPI COURSE - LESSON 08: DATABASES WITH SQLALCHEMY
===============================================================================

Time: about 100 minutes (there's a good place for a break halfway).
Assumes: lessons 00-07.

THREE WAYS TO RUN THIS FILE:

    python 08_databases.py            the TOUR (uses a throwaway in-memory database)
    python 08_databases.py --serve    a REAL server using a database FILE,
                                      lesson08.db - your data survives restarts
    python 08_databases.py --check    grades your exercises


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. read and write a database with raw SQL, so the rest isn't magic (PART 1)
  2. describe your tables as Python classes                          (PART 2)
  3. create, read, update, delete and undo, using a session          (PART 3)
  4. give every request its own session                              (PART 4)
  5. turn database objects into API responses                        (PART 5)
  6. rewrite lesson 06's routes on top of a real database            (PART 6)
  7. let the database do the counting and averaging                  (PART 7)

NEW WORDS - come back here whenever you forget one:

  database     where your data lives on disk, so it survives a restart
  table        one kind of thing, stored in rows and columns (like lesson 01's
               list of dicts, with rules the database enforces)
  row          one item; column  one field of it
  primary key  the id column: unique for every row
  foreign key  a column pointing at another table's id. The database refuses
               a book whose author doesn't exist.
  unique       a rule saying no two rows may share a value
  index        extra bookkeeping that makes searching one column fast
  SQL          the language databases speak: SELECT, INSERT, UPDATE, DELETE
  SQL injection  the attack where text from a client becomes part of your SQL.
               Never build SQL with f-strings - PART 1 shows why.
  ORM          a library that writes the SQL for you from Python code
  SQLAlchemy   the ORM this course uses
  engine       the object that knows how to reach the database (one per app)
  session      one conversation with the database
  commit       save everything done in this session
  rollback     throw the unsaved changes away
  model        a class describing a TABLE (class Book(Base))
  schema       a Pydantic class describing what the API sends/receives.
               Two different things - don't mix them up.
  relationship an attribute like author.books that loads related rows
  cascade      "deleting this also deletes those"
  migration    changing an existing table safely, as a project grows
  seed         putting starter data in an empty database
  lifespan     code that runs once at server start, and once at stop
  N+1 queries  the classic slowness: one query for a list, then one MORE for
               every item in it

PYTHON YOU NEED:
  * classes and inheritance     class Book(Base)              (lesson 02)
  * with blocks                 with Session(engine) as ...   (lesson 02 PART 8)
  * yield dependencies          get_db()                      (lesson 07 PART 5)
  * ** to unpack a dict into arguments:
        Author(**{"name": "X", "country": "US"})
    is exactly  Author(name="X", country="US").  You'll see it a few times
    below; it saves listing every field by hand.


-------------------------------------------------------------------------------
 THEORY: WHY A DATABASE
-------------------------------------------------------------------------------

Lesson 06's tasks_db dict has three fatal problems:

  1. It disappears every time the server restarts.
  2. Production runs several copies of your server at once. Each copy would
     have its own separate dict, each with different data.
  3. "Books from 1960-1980 by Nigerian authors, sorted by title" means looping
     over every item, every time.

A database fixes all three: the data lives on disk, every copy of your server
talks to the same database, and it's built to search huge amounts of data fast.


TABLES, ROWS, COLUMNS - YOU ALREADY KNOW THIS SHAPE
---------------------------------------------------
Lesson 01 PART 5 said: each dictionary is a ROW, each key is a COLUMN. A
database table is exactly that - with rules the database enforces:

    authors                               books
    id | name              | country      id | title                | year | author_id
    ---+-------------------+--------      ---+----------------------+------+----------
     1 | Ursula K. Le Guin | US            1 | A Wizard of Earthsea | 1968 | 1
     2 | Haruki Murakami   | JP            2 | Norwegian Wood       | 1987 | 2
                                           3 | The Dispossessed     | 1974 | 1

  PRIMARY KEY   id - unique for every row
  FOREIGN KEY   books.author_id must match a real authors.id. The database
                refuses a book whose author doesn't exist.
  UNIQUE        no two authors with the same name - enforced by the
                DATABASE, even if your code forgets to check.


SQL: THE LANGUAGE DATABASES SPEAK
---------------------------------
    create  ->  INSERT INTO books (title, year) VALUES ('Dune', 1965)
    read    ->  SELECT title, year FROM books WHERE year > 1960 ORDER BY title
    update  ->  UPDATE books SET in_stock = 0 WHERE id = 3
    delete  ->  DELETE FROM books WHERE id = 3

The same four jobs as every lesson since 01. PART 1 runs real SQL.


AN ORM: WRITE PYTHON, GET SQL
-----------------------------
SQLAlchemy is an ORM - an Object-Relational Mapper. You write classes and
Python expressions; it writes the SQL for you:

    select(Book).where(Book.year > 1960).order_by(Book.title)

It also means switching databases is a one-line change - the URL:

    SQLite       the whole database is ONE FILE. No server to install.
                 Perfect for learning, tests and small apps.
                 sqlite:///lesson08.db
    PostgreSQL   a database SERVER - what most production backends use.
                 postgresql+psycopg://user:password@localhost:5432/mydb


THE SESSION
-----------
A Session is one conversation with the database. You add, change and delete
objects in it, and NOTHING is saved until session.commit(). If something
goes wrong, session.rollback() throws the unsaved changes away.

THE RULE IN FASTAPI: one session per request, opened by a yield dependency
(lesson 07 PART 5), and always closed afterwards.


TWO KINDS OF CLASS - DON'T MIX THEM UP
--------------------------------------
    class Book(Base)          SQLAlchemy MODEL    the table: what's STORED
    class BookOut(BaseModel)  Pydantic SCHEMA     the API: what's SENT/RECEIVED

The same idea as lesson 05's in/out models, one layer further down.
"""

import sqlite3
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import ForeignKey, String, create_engine, event, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    selectinload,
)
from sqlalchemy.pool import StaticPool
from sqlalchemy.schema import CreateTable

from course_tools import check, section, show, start


# =============================================================================
# PART 1 — RAW SQL FIRST, SO THE ORM ISN'T MAGIC
# =============================================================================
#
# sqlite3 is built into Python. This is what talking to a database looks like
# with no help at all. You won't write code like this in a FastAPI app -
# SQLAlchemy does it for you - but now you'll know what it's doing.

def part1_raw_sql_demo():
    db = sqlite3.connect(":memory:")       # a throwaway database in memory

    create = ("CREATE TABLE authors ("
              "id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, country TEXT)")
    db.execute(create)
    print(f"  {create}")

    # The ? marks are PLACEHOLDERS. The values travel separately from the SQL.
    db.execute("INSERT INTO authors (name, country) VALUES (?, ?)",
               ("Ursula K. Le Guin", "US"))
    db.execute("INSERT INTO authors (name) VALUES (?)", ("Haruki Murakami",))
    print("  INSERT INTO authors (name, country) VALUES (?, ?)   x2")

    db.execute("UPDATE authors SET country = ? WHERE name = ?", ("JP", "Haruki Murakami"))
    print("  UPDATE authors SET country = ? WHERE name = ?")

    print("  SELECT id, name, country FROM authors ORDER BY name")
    for row in db.execute("SELECT id, name, country FROM authors ORDER BY name"):
        print(f"      {row}")

    try:
        db.execute("INSERT INTO authors (name) VALUES (?)", ("Haruki Murakami",))
    except sqlite3.IntegrityError as error:
        print(f"\n  A duplicate name, refused BY THE DATABASE: {error}")

    # ---- SQL INJECTION: the most famous security bug there is ----
    evil_input = "nobody' OR '1'='1"
    unsafe_sql = f"SELECT name FROM authors WHERE name = '{evil_input}'"
    print("\n  NEVER build SQL with an f-string. Suppose a client sends the name:")
    print(f"      {evil_input}")
    print("  The f-string builds this SQL:")
    print(f"      {unsafe_sql}")
    print("  ...where '1'='1' is always true, so it returns EVERY row:",
          db.execute(unsafe_sql).fetchall())
    safe = db.execute("SELECT name FROM authors WHERE name = ?", (evil_input,)).fetchall()
    print("  With a ? placeholder, the same text is just an odd name:", safe)
    print("  (SQLAlchemy always uses placeholders. That's one reason to use it.)")
    db.close()

# TRY IT NOW (2 minutes):
#   Change evil_input above to  nobody' OR 1=1; --  and run the tour again.
#   [Same result: every row. The ; starts a second statement and -- comments
#   out the rest. This is how real databases get emptied. The ? placeholder
#   version stays safe whatever you put in it.]


# =============================================================================
# PART 2 — THE ENGINE AND THE MODELS                   would live in: database.py
# =============================================================================
#                                                             and models.py
# The ENGINE knows how to reach the database. Create ONE for the whole app.

IN_SERVE_MODE = "--serve" in sys.argv
DB_FILE = Path(__file__).resolve().parent / "lesson08.db"

if IN_SERVE_MODE:
    # A real file. echo=True prints every SQL statement in the server's
    # terminal - the best way to see what the ORM is actually doing.
    engine = create_engine(f"sqlite:///{DB_FILE}", echo=True,
                           connect_args={"check_same_thread": False})
else:
    # "sqlite://" with no file name = an in-memory database, fresh every run.
    # StaticPool makes every session share one connection - without it, each
    # new connection to an in-memory database would get its own EMPTY database.
    engine = create_engine("sqlite://", poolclass=StaticPool,
                           connect_args={"check_same_thread": False})

# check_same_thread=False: FastAPI runs plain `def` routes on several threads
# (lesson 03). SQLite refuses that by default; this setting allows it.


# An SQLite quirk: it ignores foreign keys unless you switch them on for each
# connection. PostgreSQL always enforces them. This runs on every new connection.
@event.listens_for(engine, "connect")
def turn_on_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


# Every model inherits from one Base class. Base keeps a list of all tables.
class Base(DeclarativeBase):
    pass


# THE MODEL SYNTAX, LINE BY LINE
#   __tablename__ = "authors"                the table's name in the database
#   id: Mapped[int] = mapped_column(primary_key=True)
#       Mapped[int]         the column holds an int, and CAN'T be empty (NOT NULL)
#       Mapped[str | None]  the column CAN be empty (NULL)
#       mapped_column(...)  extra column rules: primary_key, unique, default, length
#   books: Mapped[list["Book"]] = relationship(...)
#       NOT a column. A convenient Python attribute: author.books gives you
#       that author's Book objects, loaded from the books table for you.
#       "Book" is in quotes because the Book class is defined further down.

class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    country: Mapped[str | None] = mapped_column(String(2))

    # cascade="all, delete-orphan": deleting an author deletes their books too.
    # order_by: author.books always comes back oldest first.
    books: Mapped[list["Book"]] = relationship(
        back_populates="author", cascade="all, delete-orphan", order_by="Book.year")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)  # index: fast title search
    year: Mapped[int]
    pages: Mapped[int | None]
    in_stock: Mapped[bool] = mapped_column(default=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))

    # The other side of Author.books. back_populates links the two, so
    # book.author and author.books always agree.
    author: Mapped["Author"] = relationship(back_populates="books")


# =============================================================================
# PART 3 — THE SESSION: CRUD IN PYTHON
# =============================================================================
#
# This demo uses its OWN throwaway engine, so it doesn't disturb the API's data.

def indent(text: str, spaces: int = 6) -> str:
    return "\n".join(" " * spaces + line for line in str(text).splitlines())


def part3_session_demo():
    demo_engine = create_engine("sqlite://")
    Base.metadata.create_all(demo_engine)        # CREATE TABLE for every model

    # `with Session(...) as session:` - lesson 02 part 8. The session is closed
    # automatically at the end of the block.
    with Session(demo_engine) as session:
        # ---- CREATE ----
        le_guin = Author(name="Ursula K. Le Guin", country="US")
        session.add(le_guin)
        print(f"  CREATE: added an Author. Before commit, le_guin.id = {le_guin.id}")
        session.commit()
        print(f"          after commit,  le_guin.id = {le_guin.id}"
              "   <- the DATABASE picked the id")

        # Setting book.author fills in author_id for you.
        session.add_all([
            Book(title="A Wizard of Earthsea", year=1968, pages=183, author=le_guin),
            Book(title="The Left Hand of Darkness", year=1969, pages=304, author=le_guin),
            Book(title="The Dispossessed", year=1974, pages=387, author=le_guin),
        ])
        session.commit()

        # ---- READ MANY ----
        statement = select(Book).where(Book.year >= 1969).order_by(Book.title)
        print("\n  READ: this Python statement...")
        print("      select(Book).where(Book.year >= 1969).order_by(Book.title)")
        print("  ...becomes this SQL:")
        print(indent(statement))
        for book in session.scalars(statement):   # scalars(): give me Book objects
            print(f"      -> {book.title} ({book.year})")

        # ---- READ ONE, by primary key ----
        book = session.get(Book, 1)               # None if there's no such id
        print(f"\n  READ ONE: session.get(Book, 1) -> {book.title}")
        print(f"            book.author.name     -> {book.author.name}"
              "   <- the relationship")

        # ---- UPDATE: change the attribute, then commit ----
        book.in_stock = False
        session.commit()
        out_of_stock = session.scalars(
            select(Book.title).where(Book.in_stock == False)).all()  # noqa: E712
        print(f"\n  UPDATE: book.in_stock = False; commit -> out of stock: {out_of_stock}")

        # ---- DELETE ----
        session.delete(book)
        session.commit()
        remaining = session.scalar(select(func.count(Book.id)))
        print(f"  DELETE: session.delete(book); commit -> {remaining} books left")

        # TRY IT NOW (3 minutes):
        #   Comment out the  session.commit()  three lines below the
        #   `book.in_stock = False` line and run the tour.
        #   [The UPDATE line still prints the change - the object changed in
        #   memory - but nothing was saved. Forgetting commit() is the most
        #   common database bug there is.]

        # ---- ROLLBACK: the safety net ----
        session.add(Author(name="Ursula K. Le Guin"))    # a duplicate name
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            print("\n  ROLLBACK: a duplicate author broke the UNIQUE rule;")
            print("            rollback() discarded it and the session is usable again")
        print(f"            authors in the database: {session.scalar(select(func.count(Author.id)))}")


# =============================================================================
# PART 4 — CONNECTING THE DATABASE TO FASTAPI     would live in: database.py
# =============================================================================

SEED_DATA = [
    {"name": "Ursula K. Le Guin", "country": "US", "books": [
        {"title": "A Wizard of Earthsea", "year": 1968, "pages": 183},
        {"title": "The Left Hand of Darkness", "year": 1969, "pages": 304},
        {"title": "The Dispossessed", "year": 1974, "pages": 387},
    ]},
    {"name": "Chimamanda Ngozi Adichie", "country": "NG", "books": [
        {"title": "Half of a Yellow Sun", "year": 2006, "pages": 433},
        {"title": "Americanah", "year": 2013, "pages": 477},
    ]},
    {"name": "Haruki Murakami", "country": "JP", "books": [
        {"title": "Norwegian Wood", "year": 1987, "pages": 296, "in_stock": False},
        {"title": "Kafka on the Shore", "year": 2002, "pages": 505},
    ]},
]


def seed_database(session: Session) -> None:
    for entry in SEED_DATA:
        author = Author(name=entry["name"], country=entry["country"])
        # Book(**book) turns each dict into keyword arguments:
        #     Book(**{"title": "Dune", "year": 1965})
        #     is the same as  Book(title="Dune", year=1965)
        books = []
        for book in entry["books"]:
            books.append(Book(**book))
        author.books = books          # the relationship sets author_id for us
        session.add(author)
    session.commit()


# LIFESPAN: code that runs once when the server STARTS, and once when it STOPS.
# It's a context manager (lesson 02 part 8): before `yield` = startup,
# after `yield` = shutdown. @asynccontextmanager is what turns this function
# into one.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_all makes tables that don't exist yet. It NEVER changes a table
    # that already exists - see COMMON MISTAKES about migrations.
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        if session.scalar(select(func.count(Author.id))) == 0:
            seed_database(session)
    yield
    engine.dispose()                   # shutdown: close every connection


app = FastAPI(
    title="Lesson 08 - Library API",
    description="A real database behind the API, with SQLAlchemy.",
    version="1.0.0",
    lifespan=lifespan,
)


# ONE SESSION PER REQUEST - lesson 07 PART 5's yield dependency, for real.
# The `with` block closes the session after the response, and any changes
# that were never committed are thrown away.
def get_db():
    with Session(engine) as session:
        yield session


DbSession = Annotated[Session, Depends(get_db)]


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. You've seen SQL, the models, the session, and how
#  each request gets its own. After the break: the schemas, the routes, and
#  letting the database do the maths.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 5 — PYDANTIC SCHEMAS FOR THE API              would live in: schemas.py
# =============================================================================
#
# from_attributes=True: lets Pydantic read a SQLAlchemy object's ATTRIBUTES
# (book.title) instead of dictionary keys (book["title"]). Without it,
# returning a Book from a route fails with "Input should be a valid dictionary".

class AuthorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    country: str | None = Field(default=None, min_length=2, max_length=2)


class AuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country: str | None


class BookSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    year: int


class AuthorWithBooks(AuthorOut):
    books: list[BookSummary]        # read from the author.books relationship


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    year: int = Field(ge=1450, le=2100)
    pages: int | None = Field(default=None, ge=1)
    in_stock: bool = True
    author_id: int


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    year: int | None = Field(default=None, ge=1450, le=2100)
    pages: int | None = Field(default=None, ge=1)
    in_stock: bool | None = None

    # Lesson 06's guard: title/year/in_stock are NOT NULL columns, so an
    # explicit null would crash the database write.
    @model_validator(mode="after")
    def reject_null_for_required_fields(self) -> "BookUpdate":
        for name in ["title", "year", "in_stock"]:
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} can't be null")
        return self


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    year: int
    pages: int | None
    in_stock: bool
    author: AuthorOut               # nested - read from book.author


class BookPage(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[BookOut]


# =============================================================================
# PART 6 — THE ROUTES                          would live in: routers/authors.py
# =============================================================================                    and routers/books.py

authors_router = APIRouter(prefix="/authors", tags=["authors"])
books_router = APIRouter(prefix="/books", tags=["books"])


# Lesson 07's "valid item" dependency, now backed by the database.
# Because of dependency CACHING, valid_book and the route that uses it receive
# the SAME session. So a route can change the book valid_book loaded, and
# commit it.
def valid_author(author_id: int, db: DbSession) -> Author:
    author = db.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Author {author_id} not found")
    return author


def valid_book(book_id: int, db: DbSession) -> Book:
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Book {book_id} not found")
    return book


ValidAuthor = Annotated[Author, Depends(valid_author)]
ValidBook = Annotated[Book, Depends(valid_book)]


# ---- AUTHORS ----------------------------------------------------------------

@authors_router.post("", response_model=AuthorOut, status_code=status.HTTP_201_CREATED)
def create_author(data: AuthorCreate, db: DbSession):
    author = Author(**data.model_dump())
    db.add(author)
    # Let the DATABASE enforce uniqueness, instead of checking first. "Check,
    # then insert" has a gap: two requests can both pass the check at the same
    # moment. The UNIQUE rule has no gap.
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"An author named '{data.name}' already exists")
    db.refresh(author)          # reload from the database: fills in author.id
    return author


@authors_router.get("", response_model=list[AuthorOut])
def list_authors(db: DbSession):
    return db.scalars(select(Author).order_by(Author.name)).all()


@authors_router.get("/{author_id}", response_model=AuthorWithBooks)
def get_author(author: ValidAuthor):
    return author               # AuthorWithBooks reads author.books for us


@authors_router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author: ValidAuthor, db: DbSession):
    db.delete(author)           # cascade: their books are deleted too
    db.commit()


# ---- BOOKS ------------------------------------------------------------------

@books_router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(data: BookCreate, db: DbSession):
    if db.get(Author, data.author_id) is None:
        # 422, not 404: the URL /books is fine - it's the body that's wrong.
        raise HTTPException(status_code=422,
                            detail=f"Author {data.author_id} does not exist")
    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@books_router.get("", response_model=BookPage)
def list_books(
    db: DbSession,
    author_id: int | None = None,
    in_stock: bool | None = None,
    q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    sort: Literal["title", "year", "-year"] = "title",
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    # Build the query step by step. Nothing touches the database until the
    # statement is actually executed below.
    statement = select(Book)
    if author_id is not None:
        statement = statement.where(Book.author_id == author_id)
    if in_stock is not None:
        statement = statement.where(Book.in_stock == in_stock)
    if q is not None:
        # ilike = case-insensitive LIKE. % means "any text here". The value
        # still travels as a placeholder, so this is safe from injection.
        statement = statement.where(Book.title.ilike(f"%{q}%"))

    # The total BEFORE paging: count the rows the filtered query would return.
    total = db.scalar(select(func.count()).select_from(statement.subquery()))

    # A dict of the allowed sorts, then pick one by name. sort can only be
    # one of these three words, because Literal[...] already checked it.
    sort_options = {"title": Book.title, "year": Book.year,
                    "-year": Book.year.desc()}
    order = sort_options[sort]
    statement = (statement.order_by(order).offset(skip).limit(limit)
                 # Load every book's author in ONE extra query. Without this,
                 # BookOut touching book.author would run a separate query for
                 # EACH book - the "N+1 queries" problem.
                 .options(selectinload(Book.author)))

    return {"total": total, "skip": skip, "limit": limit,
            "items": db.scalars(statement).all()}


@books_router.get("/{book_id}", response_model=BookOut)
def get_book(book: ValidBook):
    return book


@books_router.patch("/{book_id}", response_model=BookOut)
def update_book(book: ValidBook, changes: BookUpdate, db: DbSession):
    # setattr(book, "pages", 305) is the same as book.pages = 305 - but works
    # when the field's name is in a variable (lesson 06's getattr, in reverse).
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book: ValidBook, db: DbSession):
    db.delete(book)
    db.commit()


# =============================================================================
# PART 7 — LETTING THE DATABASE DO THE MATHS
# =============================================================================
#
# func.count, func.avg, func.sum, func.min, func.max become SQL functions.
# The database calculates the answer and sends back one small result, instead
# of you downloading every row and looping.

@app.get("/stats", tags=["stats"])
def library_stats(db: DbSession):
    book_count = func.count(Book.id)
    per_author = db.execute(
        select(Author.name, book_count)
        .select_from(Author)
        .outerjoin(Book)                    # authors with 0 books still appear
        .group_by(Author.id)                # one result row per author
        .order_by(book_count.desc(), Author.name)
    ).all()
    average_pages = db.scalar(select(func.avg(Book.pages)))
    if average_pages is None:          # no books at all -> SQL's AVG is NULL
        rounded_average = None
    else:
        rounded_average = round(average_pages, 1)

    # each result row is a pair of values, unpacked into name and books
    per_author_list = []
    for name, books in per_author:
        per_author_list.append({"author": name, "books": books})

    return {
        "authors": db.scalar(select(func.count(Author.id))),
        "books": db.scalar(select(func.count(Book.id))),
        "average_pages": rounded_average,
        "books_per_author": per_author_list,
    }


app.include_router(authors_router)
app.include_router(books_router)


# =============================================================================
# COMMON MISTAKES
# =============================================================================
#
# 1. Forgetting db.commit(). The response even LOOKS right, because the object
#    changed in memory - then the session closes and the change is gone.
#
# 2. Returning a SQLAlchemy object when the Pydantic schema has no
#    from_attributes=True -> "Input should be a valid dictionary".
#
# 3. One global session shared by every request. Requests see each other's
#    half-finished changes. One session per request: get_db.
#
# 4. Building SQL with f-strings -> SQL injection. PART 1.
#
# 5. Catching IntegrityError without db.rollback(). The session stays broken
#    and every later query in it fails.
#
# 6. Adding a column to a model and expecting create_all to add it to an
#    existing table. It won't. Real projects use MIGRATIONS (the Alembic
#    library) to change existing tables safely. While learning with --serve,
#    just delete lesson08.db and restart.
#
# 7. N+1 queries: listing 50 books and touching book.author on each one runs
#    51 queries. selectinload() fixes it. With --serve, echo=True shows you.


# =============================================================================
# YOUR EXERCISE CODE GOES HERE - above the tour, so FastAPI registers it
# =============================================================================
# (Put exercise routes straight on the app: @app.get, @app.post, and so on.)




# =============================================================================
# THE TOUR — runs when you execute this file with no flags
# =============================================================================

def tour(client):
    section("PART 1: RAW SQL - what the ORM does for you")
    part1_raw_sql_demo()

    section("PART 2: THE TABLES SQLALCHEMY CREATED FROM THE MODELS")
    for table in [Author.__table__, Book.__table__]:
        print(indent(str(CreateTable(table).compile(engine)).strip(), 2))
        print()

    section("PART 3: THE SESSION - create, read, update, delete, rollback")
    part3_session_demo()

    section("PART 6: AUTHORS")
    show(client, "GET", "/authors", note="the seed data, loaded at startup by lifespan")
    show(client, "POST", "/authors", json={"name": "Octavia E. Butler", "country": "US"})
    show(client, "POST", "/authors", note="the UNIQUE rule -> IntegrityError -> 409",
         json={"name": "Haruki Murakami"})
    show(client, "GET", "/authors/1", note="an author WITH their books - a relationship")

    section("PART 6: BOOKS - filtering, sorting and paging in SQL")
    show(client, "GET", "/books?author_id=1&sort=-year&limit=2",
         note="Le Guin's books, newest first, 2 per page")
    show(client, "GET", "/books?q=OF&limit=1", note="case-insensitive title search")
    show(client, "POST", "/books",
         json={"title": "Kindred", "year": 1979, "pages": 264, "author_id": 4})
    show(client, "POST", "/books", note="an author that doesn't exist",
         json={"title": "Ghost Book", "year": 2020, "author_id": 99})

    section("PART 6: UPDATE AND DELETE")
    show(client, "PATCH", "/books/2", json={"in_stock": False, "pages": 305})
    show(client, "PATCH", "/books/2", note="an explicit null for a NOT NULL column",
         json={"title": None})
    show(client, "DELETE", "/books/2")
    show(client, "GET", "/books/2", note="really gone - from the database, not a dict")

    section("PART 7: THE DATABASE DOES THE MATHS")
    show(client, "GET", "/stats")
    show(client, "DELETE", "/authors/3", note="delete Murakami - cascade deletes his books")
    show(client, "GET", "/stats", note="2 fewer books, and Murakami is gone")

    section("NOW MAKE IT PERMANENT")
    print("  Everything above used a throwaway in-memory database. Now run:")
    print()
    print("      python 08_databases.py --serve")
    print()
    print("  It uses a real file, lesson08.db, next to this lesson.")
    print("   1. In /docs, create an author with POST /authors.")
    print("   2. Stop the server (Ctrl+C) and start it again.")
    print("   3. GET /authors - your author is still there. That's a database.")
    print()
    print("  Watch the terminal while you click: echo=True prints the exact SQL")
    print("  behind every request. Delete lesson08.db any time to start fresh.")


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * A database keeps data on disk, shared by every copy of your server, and
#     searches it fast. A table is lesson 01's list of dicts with real rules.
#   * NEVER build SQL with f-strings. Placeholders keep a client's text as
#     DATA instead of letting it become commands.
#   * An ORM writes SQL from Python: select(Book).where(Book.year > 1960).
#   * A model (class Book(Base)) describes the TABLE. A schema
#     (class BookOut(BaseModel)) describes the API. Two different classes.
#   * Nothing is saved until db.commit(). If a write fails, db.rollback()
#     clears the session so it can be used again.
#   * One session per request, from a yield dependency - never one global one.
#   * Let the DATABASE enforce uniqueness and do the counting; catch
#     IntegrityError and turn it into a 409.
#   * Relationships (author.books) load related rows; selectinload loads them
#     all in one extra query instead of one per item (N+1).
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. You change book.pages and return the book. It looks right in the
#       response, but the value is gone next time. What did you forget?
#   Q2. Why is  f"SELECT * FROM users WHERE name = '{name}'"  dangerous?
#   Q3. What's the difference between class Book(Base) and class
#       BookOut(BaseModel)?
#   Q4. Two requests create the same author name at the same instant. Why is
#       "check first, then insert" not enough?
#   Q5. Why does every request get its own session?
#
# ANSWERS
#   A1. db.commit().
#   A2. Text from the client becomes part of the SQL - it can end the string
#       and add commands of its own. Use placeholders.
#   A3. Book(Base) is the TABLE (what's stored). BookOut(BaseModel) is the
#       API shape (what's sent).
#   A4. Both can pass the check before either inserts. Only the database's
#       UNIQUE rule has no gap - so let it fail, and catch IntegrityError.
#   A5. So requests never see each other's half-finished, uncommitted work.


# =============================================================================
# EXERCISES — ADD BOOK REVIEWS
# =============================================================================
#
# Write your code in the "YOUR EXERCISE CODE GOES HERE" space above the tour,
# then run:
#     python 08_databases.py --check
#
# Do the WARM-UPS first - both are one short query each.
#
# WARM-UP 1 (easy) — Let the database count
#   Add GET /library/count returning {"authors": N, "books": M}. Use
#   db.scalar(select(func.count(Author.id))) - don't load the rows and use
#   len().
#
# WARM-UP 2 (easy) — The oldest book
#   Add GET /oldest-book returning {"title": ..., "year": ...} for the book
#   with the smallest year. Use  select(Book).order_by(Book.year).limit(1)
#   and db.scalars(...).first().
#
# EXERCISE 1 (challenge) — A new table, and creating rows
#   Write a Review model (table "reviews") with:
#       id        primary key
#       book_id   a foreign key to books.id
#       rating    int
#       comment   text up to 500 characters, optional
#   Write a ReviewCreate schema (rating 1 to 5; comment optional, max 500) and
#   a ReviewOut schema (id, book_id, rating, comment) with from_attributes.
#   Add POST /books/{book_id}/reviews -> 201 with the review. A book that
#   doesn't exist -> 404. Hint: the ValidBook dependency does that for you.
#   (lifespan runs create_all AFTER this whole file loads, so your new table
#   is created automatically.)
#
# EXERCISE 2 (medium) — Reading related rows
#   GET /books/{book_id}/reviews -> a LIST of that book's reviews, NEWEST
#   first (highest id first). Unknown book -> 404.
#
# EXERCISE 3 (challenge) — Aggregates
#   GET /books/{book_id}/rating ->
#       {"book_id": 1, "review_count": 3, "average_rating": 3.7}
#   average_rating is rounded to 1 decimal place, or None when the book has no
#   reviews. Let the database count and average (func.count, func.avg).
#
# EXERCISE 4 (easy) — Delete
#   DELETE /reviews/{review_id} -> 204, or 404 with detail "Review not found".
#
# STRETCH (no automatic check)
#   Try DELETE /books/1 after reviewing book 1. It fails: the foreign key
#   refuses to leave reviews pointing at a missing book. Fix it by adding
#       reviews: Mapped[list["Review"]] = relationship(cascade="all, delete-orphan")
#   to the Book model - then think about whether deleting reviews silently
#   is what a real library would want.


def checks(client):
    check("the lesson's own GET /books still works", client.get("/books").status_code == 200)

    # --- WARM-UP 1 ---
    author_count = len(client.get("/authors").json())
    book_total = client.get("/books").json()["total"]
    r = client.get("/library/count")
    body = r.json() if r.status_code == 200 else {}
    check("WARM-UP 1: GET /library/count returns the number of authors",
          r.status_code == 200 and body.get("authors") == author_count)
    check("WARM-UP 1: ...and the number of books",
          body.get("books") == book_total)

    # --- WARM-UP 2 ---
    r = client.get("/oldest-book")
    body = r.json() if r.status_code == 200 else {}
    check("WARM-UP 2: GET /oldest-book finds A Wizard of Earthsea (1968)",
          r.status_code == 200 and body.get("title") == "A Wizard of Earthsea"
          and body.get("year") == 1968)

    # --- EXERCISE 1 ---
    r = client.post("/books/1/reviews", json={"rating": 5, "comment": "A classic"})
    first = r.json() if r.status_code == 201 else {}
    check("EXERCISE 1: POST /books/1/reviews returns 201", r.status_code == 201)
    check("EXERCISE 1: the review has an id, book_id 1 and rating 5",
          "id" in first and first.get("book_id") == 1 and first.get("rating") == 5)
    check("EXERCISE 1: rating 6 gives 422",
          client.post("/books/1/reviews", json={"rating": 6}).status_code == 422)
    check("EXERCISE 1: rating 0 gives 422",
          client.post("/books/1/reviews", json={"rating": 0}).status_code == 422)
    # "Not Found" is FastAPI's reply when NO route matches - so it doesn't count
    r = client.post("/books/9999/reviews", json={"rating": 3})
    check("EXERCISE 1: reviewing a book that doesn't exist gives 404",
          r.status_code == 404 and r.json().get("detail") != "Not Found")

    client.post("/books/1/reviews", json={"rating": 4})
    client.post("/books/1/reviews", json={"rating": 2, "comment": "Not for me"})

    # --- EXERCISE 2 ---
    r = client.get("/books/1/reviews")
    reviews = r.json() if r.status_code == 200 else None
    check("EXERCISE 2: GET /books/1/reviews returns 3 reviews",
          isinstance(reviews, list) and len(reviews) == 3)
    check("EXERCISE 2: newest first (ratings 2, 4, 5)",
          isinstance(reviews, list) and [x.get("rating") for x in reviews] == [2, 4, 5])
    r = client.get("/books/9999/reviews")
    check("EXERCISE 2: an unknown book gives 404",
          r.status_code == 404 and r.json().get("detail") != "Not Found")

    # --- EXERCISE 3 ---
    r = client.get("/books/1/rating")
    check("EXERCISE 3: book 1 -> 3 reviews, average 3.7",
          r.status_code == 200
          and r.json() == {"book_id": 1, "review_count": 3, "average_rating": 3.7})
    r = client.get("/books/3/rating")
    check("EXERCISE 3: a book with no reviews -> count 0, average None",
          r.status_code == 200
          and r.json() == {"book_id": 3, "review_count": 0, "average_rating": None})

    # --- EXERCISE 4 ---
    if "id" in first:
        r = client.delete(f"/reviews/{first['id']}")
        check("EXERCISE 4: DELETE /reviews/{id} returns 204", r.status_code == 204)
        r = client.get("/books/1/rating")
        check("EXERCISE 4: ...and book 1 now has 2 reviews",
              r.status_code == 200 and r.json().get("review_count") == 2)
        r = client.delete(f"/reviews/{first['id']}")
        check("EXERCISE 4: deleting it again gives 404 'Review not found'",
              r.status_code == 404 and r.json().get("detail") == "Review not found")
    else:
        check("EXERCISE 4 needs EXERCISE 1 working first", False)


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP 1
#   @app.get("/library/count")
#   def library_count(db: DbSession):
#       return {
#           "authors": db.scalar(select(func.count(Author.id))),
#           "books": db.scalar(select(func.count(Book.id))),
#       }
#
# WARM-UP 2
#   @app.get("/oldest-book")
#   def oldest_book(db: DbSession):
#       book = db.scalars(select(Book).order_by(Book.year).limit(1)).first()
#       return {"title": book.title, "year": book.year}
#
#   limit(1) means the DATABASE sends back one row, not all of them.
#
# EXERCISE 1
#   class Review(Base):
#       __tablename__ = "reviews"
#
#       id: Mapped[int] = mapped_column(primary_key=True)
#       book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
#       rating: Mapped[int]
#       comment: Mapped[str | None] = mapped_column(String(500))
#
#   class ReviewCreate(BaseModel):
#       rating: int = Field(ge=1, le=5)
#       comment: str | None = Field(default=None, max_length=500)
#
#   class ReviewOut(BaseModel):
#       model_config = ConfigDict(from_attributes=True)
#
#       id: int
#       book_id: int
#       rating: int
#       comment: str | None
#
#   @app.post("/books/{book_id}/reviews", response_model=ReviewOut, status_code=201)
#   def create_review(book: ValidBook, data: ReviewCreate, db: DbSession):
#       review = Review(book_id=book.id, **data.model_dump())
#       db.add(review)
#       db.commit()
#       db.refresh(review)
#       return review
#
#   The rating rule lives in the SCHEMA, so bad ratings never reach the
#   database. You could also add a database CHECK constraint as a second line
#   of defence.
#
# EXERCISE 2
#   @app.get("/books/{book_id}/reviews", response_model=list[ReviewOut])
#   def list_reviews(book: ValidBook, db: DbSession):
#       statement = (select(Review)
#                    .where(Review.book_id == book.id)
#                    .order_by(Review.id.desc()))
#       return db.scalars(statement).all()
#
# EXERCISE 3
#   @app.get("/books/{book_id}/rating")
#   def book_rating(book: ValidBook, db: DbSession):
#       review_count, average = db.execute(
#           select(func.count(Review.id), func.avg(Review.rating))
#           .where(Review.book_id == book.id)
#       ).one()
#       return {
#           "book_id": book.id,
#           "review_count": review_count,
#           "average_rating": round(average, 1) if average is not None else None,
#       }
#
#   .one() returns the single result row, and `review_count, average = row`
#   unpacks its two values into two variables. With no reviews, SQL's AVG
#   returns NULL - which arrives in Python as None.
#
# EXERCISE 4
#   @app.delete("/reviews/{review_id}", status_code=204)
#   def delete_review(review_id: int, db: DbSession):
#       review = db.get(Review, review_id)
#       if review is None:
#           raise HTTPException(status_code=404, detail="Review not found")
#       db.delete(review)
#       db.commit()


if __name__ == "__main__":
    start(app, tour, checks)


print("\nNext: python 09_authentication.py")

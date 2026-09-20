"""
===============================================================================
 FASTAPI COURSE - LESSON 09: AUTHENTICATION - PASSWORDS, TOKENS AND ROLES
===============================================================================

Time: about 100 minutes (there's a good place for a break halfway).
Assumes: lessons 00-08.

THREE WAYS TO RUN THIS FILE:

    python 09_authentication.py            the TOUR (read this first)
    python 09_authentication.py --serve    a REAL server - use the Authorize
                                           button in /docs to log in
    python 09_authentication.py --check    grades your exercises


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. store passwords safely - and why a fast hash is not safe       (PART 1)
  2. hand out a signed token, and see why it can't be faked         (PART 2)
  3. keep users and their notes in the database                     (PART 3)
  4. write register and login endpoints                             (PART 4)
  5. turn a token back into "who is asking?"                        (PART 5)
  6. make sure people can only touch their OWN things               (PART 6)
  7. give admins extra powers with roles                            (PART 7)

NEW WORDS - come back here whenever you forget one:

  authentication  "who are you?" - fails with 401
  authorization   "are you allowed to?" - fails with 403
  hash            a one-way scramble of a password. You can make it from the
                  password, but never turn it back.
  salt            random bytes mixed into each hash, so two people with the
                  same password get different hashes
  slow hash       a password hash designed to take time ON PURPOSE, so
                  guessing billions of passwords is impractical (scrypt here)
  token           a note from the server saying "this is user 7, until 14:30"
  JWT             the token format used here: header.payload.signature
  signature       proof the token came from your server and wasn't edited
  SECRET_KEY      the secret used to sign tokens. Anyone who has it can
                  forge any token - keep it out of your code and out of git.
  signed vs       a JWT is SIGNED, not encrypted: anyone can READ the
  encrypted       payload, nobody can CHANGE it. Never put secrets inside.
  expiry (exp)    when the token stops working
  bearer token    a token sent as  Authorization: Bearer <token>
  form data       how a login is sent: username=...&password=... - NOT JSON
  ownership       the rule that your notes are yours (PART 6)
  role            "user" or "admin" - what someone is allowed to do
  timing attack   learning secrets from how LONG an answer takes. PART 1 and
                  PART 4 both defend against one.

PYTHON YOU NEED:
  * dependencies and chains of them     (lesson 07 PARTS 2-4)
  * a database session per request      (lesson 08 PART 4)
  * try / except                        (lesson 02 PART 6)
  * setattr(obj, "name", value) - the same as obj.name = value, but when the
    field's name is in a variable (used in the solutions)


-------------------------------------------------------------------------------
 THEORY: TWO QUESTIONS, TWO STATUS CODES
-------------------------------------------------------------------------------

  AUTHENTICATION   "Who are you?"           fails with 401 Unauthorized
  AUTHORIZATION    "Are you allowed to?"    fails with 403 Forbidden

Lesson 07 answered both with API keys, which suit PROGRAMS. People log in
with an email and a password. This lesson builds that, the standard way.


THE WHOLE FLOW, IN THREE REQUESTS
---------------------------------
  1. POST /auth/register   {"email": ..., "password": ...}
       The server stores the email and a HASH of the password - never the
       password itself.

  2. POST /auth/token      username=...&password=...   (form data)
       The server hashes what you typed, compares, and if it matches,
       returns a signed TOKEN: a tamper-proof note saying "this is user 7,
       valid until 14:30".

  3. GET /notes            Authorization: Bearer <the token>
       Every later request carries the token in a header. The server checks
       the signature and knows who you are - no password needed again.


WHY HASH PASSWORDS?
-------------------
Databases get stolen. It happens to large, careful companies. If you stored
passwords, every user's password is now public - and people reuse passwords
on their email and bank accounts.

A HASH is one-way: easy to compute from a password, impossible to turn back
into it. To check a login, hash what was typed and compare the two hashes.
Two more ingredients make it strong:

  SALT   random bytes mixed into each hash, so two people with the same
         password get DIFFERENT hashes
  SLOW   a good password hash takes tens of milliseconds ON PURPOSE -
         unnoticeable for one login, crippling for an attacker trying
         billions of guesses


WHY TOKENS?
-----------
HTTP is stateless (lesson 00): the server doesn't remember your previous
request. So EVERY request must prove who's asking. Sending the password every
time would be risky. Instead the server hands out a token once.

This lesson uses a JWT (JSON Web Token):

    eyJhbGciOiJIUzI1NiIs...  .  eyJzdWIiOiI3IiwiZXhw...  .  4pX9s0e2Kq...
    header (how it's signed)    payload (the data)          signature

The signature is made from the header, the payload and a SECRET_KEY only the
server knows. Change one character of the payload and the signature no
longer matches, so the server rejects it.

IMPORTANT: a JWT is SIGNED, not ENCRYPTED. Anyone holding one can READ its
payload. They just can't CHANGE it. Never put secrets inside a token.

And always use HTTPS in production - otherwise tokens and passwords travel
across the internet as readable text.
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import ForeignKey, String, Text, create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from sqlalchemy.pool import StaticPool

from course_tools import check, section, show, start


# =============================================================================
# PART 1 — HASHING PASSWORDS                             would live in: security.py
# =============================================================================
#
# scrypt is a strong, deliberately slow password hash built into Python's
# standard library, so there's nothing extra to install.
#
# In a production project, use a maintained library that picks good settings
# and can upgrade old hashes for you - pwdlib with argon2 is the current
# recommendation for FastAPI:  pip install "pwdlib[argon2]"
#
# The stored text holds everything needed to check a password later:
#     scrypt$<salt in hex>$<hash in hex>

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)                    # 16 random bytes
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    parts = stored.split("$")
    if len(parts) != 3 or parts[0] != "scrypt":
        return False
    salt = bytes.fromhex(parts[1])
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    # compare_digest takes the same time whether the first character or the
    # last one differs. A plain == stops at the first difference, and an
    # attacker can measure that tiny time gap to guess hashes piece by piece.
    return hmac.compare_digest(digest.hex(), parts[2])


def part1_hashing_demo():
    first = hash_password("correct-horse-battery")
    second = hash_password("correct-horse-battery")
    print("  The SAME password, hashed twice:")
    print(f"    {first[:70]}...")
    print(f"    {second[:70]}...")
    print("  Different, because each has its own random salt. Two users with the")
    print("  same password don't get matching hashes.")

    print("\n  Checking a login:")
    print("    verify_password('correct-horse-battery', stored) ->",
          verify_password("correct-horse-battery", first))
    print("    verify_password('Correct-horse-battery', stored) ->",
          verify_password("Correct-horse-battery", first), "  (one capital letter)")

    started = time.perf_counter()
    hash_password("timing-this-one")
    elapsed_ms = (time.perf_counter() - started) * 1000
    days = elapsed_ms / 1000 * 1_000_000_000 / 86_400
    print(f"\n  One hash took about {elapsed_ms:.0f} ms. SHA-256 takes well under a")
    print("  millionth of a second. At this speed, a billion guesses against ONE")
    print(f"  stolen hash would take about {days:,.0f} days on one processor core.")


# TRY IT NOW (2 minutes):
#   In part1_hashing_demo above, change n=2**14 in hash_password to n=2**10
#   and run the tour. [The "one hash took about N ms" line drops sharply -
#   and so does the number of days an attacker would need. Slowness IS the
#   protection. Put it back to 2**14.]


# =============================================================================
# PART 2 — JSON WEB TOKENS                               would live in: security.py
# =============================================================================
#
# SECRET_KEY signs every token. Anyone who knows it can create tokens for ANY
# user, so it must never be written in your code or committed to git.
# Real apps read it from an environment variable. Generate one with:
#     python -c "import secrets; print(secrets.token_hex(32))"
#
# If SECRET_KEY isn't set, this lesson makes a random one at startup. That's
# safe, but every restart invalidates all existing tokens - fine for learning,
# not for production.

SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
ALGORITHM = "HS256"               # HMAC with SHA-256: signed with one shared secret
ACCESS_TOKEN_MINUTES = 30         # short-lived: a stolen token stops working soon


def create_access_token(user_id: int, minutes: int = ACCESS_TOKEN_MINUTES) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),                          # SUBJECT: who (must be text)
        "iat": now,                                   # ISSUED AT
        "exp": now + timedelta(minutes=minutes),      # EXPIRES - PyJWT checks it
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def peek_at_payload(token: str) -> dict:
    """Read a token's payload WITHOUT checking it - exactly what an attacker can do."""
    payload_part = token.split(".")[1]
    padded = payload_part + "=" * (-len(payload_part) % 4)   # base64 needs padding back
    return json.loads(base64.urlsafe_b64decode(padded))


def forge_token(token: str, new_subject: str) -> str:
    """Edit a token's payload but keep the old signature - an attempted forgery."""
    header, _, signature = token.split(".")
    claims = peek_at_payload(token)
    claims["sub"] = new_subject
    new_payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).rstrip(b"=")
    return f"{header}.{new_payload.decode()}.{signature}"


def part2_jwt_demo():
    token = create_access_token(user_id=42)
    header, payload, signature = token.split(".")
    print("  A token for user 42 has three parts, separated by dots:")
    print(f"    header     {header}")
    print(f"    payload    {payload}")
    print(f"    signature  {signature}")

    print("\n  The payload is only base64-ENCODED. Anyone can read it:")
    print(f"    {peek_at_payload(token)}")
    print("  iat and exp are Unix timestamps: seconds since 1 January 1970.")

    print("\n  jwt.decode checks the signature AND the expiry, then returns the payload:")
    print(f"    {jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])}")

    somebody_elses_secret = secrets.token_hex(32)
    attacks = [
        ("payload edited to say user 1", forge_token(token, "1")),
        ("expired 5 minutes ago", create_access_token(42, minutes=-5)),
        ("signed with a different secret",
         jwt.encode({"sub": "42", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
                    somebody_elses_secret, algorithm=ALGORITHM)),
        ("not a token at all", "hello.world.token"),
    ]
    print("\n  Every kind of bad token is rejected:")
    for description, bad_token in attacks:
        try:
            jwt.decode(bad_token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"    {description:<32} -> ACCEPTED (this should never happen)")
        except jwt.InvalidTokenError as error:
            print(f"    {description:<32} -> {type(error).__name__}")

    print("\n  `algorithms=[ALGORITHM]` is REQUIRED. It stops an attacker choosing a")
    print("  weaker signing method by editing the token's header.")


# =============================================================================
# PART 3 — THE DATABASE                        would live in: database.py, models.py
# =============================================================================
#
# Lesson 08's setup. In-memory, even with --serve, to keep this lesson about
# auth - so accounts you create in /docs vanish when the server stops.

engine = create_engine("sqlite://", poolclass=StaticPool,
                       connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    full_name: Mapped[str | None] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")   # "user" or "admin"
    is_active: Mapped[bool] = mapped_column(default=True)

    notes: Mapped[list["Note"]] = relationship(back_populates="owner",
                                               cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    body: Mapped[str] = mapped_column(Text, default="")
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner: Mapped["User"] = relationship(back_populates="notes")


# A development-only admin account, so there's someone to test admin routes
# with. A real app creates its first admin with a one-off script instead.
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin-password-123")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        if session.scalar(select(User).where(User.email == ADMIN_EMAIL)) is None:
            session.add(User(email=ADMIN_EMAIL, full_name="Site Admin", role="admin",
                             hashed_password=hash_password(ADMIN_PASSWORD)))
            session.commit()
    yield


app = FastAPI(
    title="Lesson 09 - Auth API",
    description="Passwords, JWT tokens, ownership and roles.",
    version="1.0.0",
    lifespan=lifespan,
)


def get_db():
    with Session(engine) as session:
        yield session


DbSession = Annotated[Session, Depends(get_db)]


# =============================================================================
# PART 4 — REGISTER AND LOG IN                       would live in: routers/auth.py
# =============================================================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=100)


class UserOut(BaseModel):                  # NO hashed_password - lesson 05
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str | None
    role: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str                        # always "bearer" - part of the standard
    expires_in: int                        # seconds until the token expires


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: DbSession):
    user = User(email=data.email.lower(), full_name=data.full_name,
                hashed_password=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # A trade-off: this message tells anyone which emails have accounts.
        # Many sites accept that for friendlier signup. High-security apps say
        # "check your email" whatever happened, instead.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered")
    db.refresh(user)
    return user


# Checking a password against this when the email DOESN'T exist makes a failed
# login take the same time either way. Otherwise an attacker could find out
# which emails are registered just by timing the responses.
DUMMY_HASH = hash_password("this-password-matches-no-account")


# OAuth2PasswordRequestForm reads FORM data (username=...&password=...), not
# JSON, because that's what the OAuth2 standard says a login looks like. That's
# why python-multipart is installed, and why the Authorize button in /docs
# works with this endpoint out of the box.
#
# The standard calls the field "username". We put the EMAIL in it.
#
# Depends() with nothing inside means "the class itself is the dependency":
# FastAPI builds an OAuth2PasswordRequestForm from the request for you.
@auth_router.post("/token", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    user = db.scalar(select(User).where(User.email == form.username.lower()))
    # Always hash SOMETHING, so a login with an unknown email takes just as
    # long as one with a wrong password (see DUMMY_HASH above).
    if user is None:
        stored_hash = DUMMY_HASH
    else:
        stored_hash = user.hashed_password
    password_ok = verify_password(form.password, stored_hash)

    # ONE message for both "no such email" and "wrong password", for the same
    # reason as DUMMY_HASH: don't reveal which emails exist.
    if user is None or not password_ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="This account has been deactivated")

    return {"access_token": create_access_token(user.id), "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_MINUTES * 60}


# =============================================================================
# PART 5 — WHO IS MAKING THIS REQUEST?                would live in: dependencies.py
# =============================================================================
#
# OAuth2PasswordBearer is a ready-made dependency that:
#   * reads the header   Authorization: Bearer <token>   and returns the token
#   * answers 401 "Not authenticated" by itself if the header is missing
#   * adds the Authorize button to /docs, pointing at tokenUrl
#
# get_current_user builds on it - lesson 07's chain of dependencies, for real.

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    # 401 responses should say HOW to authenticate. WWW-Authenticate: Bearer does.
    def unauthorized(detail: str) -> HTTPException:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail,
                             headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except jwt.ExpiredSignatureError:
        # A separate message, so a frontend knows to send the user back to login.
        raise unauthorized("Token has expired")
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise unauthorized("Could not validate credentials")

    # A valid signature isn't enough: the account may have been deleted or
    # deactivated AFTER the token was issued. So look the user up every time.
    user = db.get(User, user_id)
    if user is None:
        raise unauthorized("Could not validate credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="This account has been deactivated")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(user: CurrentUser) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin access required")
    return user


users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/me", response_model=UserOut)
def read_me(user: CurrentUser):
    return user                  # one line: the dependency did all the work


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. Passwords, tokens, register, login and "who is
#  asking?" are done - that's authentication. After the break: authorization,
#  which is ownership and roles.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 6 — OWNERSHIP: YOUR NOTES ARE YOURS             would live in: routers/notes.py
# =============================================================================

class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(default="", max_length=10_000)


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    owner_id: int


# Someone else's note gets 404, NOT 403. A 403 would confirm "note 7 exists,
# it just isn't yours" - leaking information. As far as you're concerned,
# other people's notes don't exist.
def get_own_note(note_id: int, user: CurrentUser, db: DbSession) -> Note:
    note = db.get(Note, note_id)
    if note is None or note.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


OwnNote = Annotated[Note, Depends(get_own_note)]

# TRY IT NOW (3 minutes):
#   In get_own_note above, delete  or note.owner_id != user.id  and run the
#   tour. [Sidd can now read AND delete Ana's private note. One missing
#   condition is the whole difference between a private app and a public one.
#   Put it back.]

notes_router = APIRouter(prefix="/notes", tags=["notes"])


@notes_router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(data: NoteCreate, user: CurrentUser, db: DbSession):
    # owner_id comes from the TOKEN, never from the request body. If clients
    # could send owner_id, anyone could create notes as anyone else.
    note = Note(**data.model_dump(), owner_id=user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@notes_router.get("", response_model=list[NoteOut])
def list_my_notes(user: CurrentUser, db: DbSession):
    # Filtering by owner happens IN THE QUERY. Loading everyone's notes and
    # filtering in Python is slower, and one forgotten filter away from a leak.
    return db.scalars(select(Note).where(Note.owner_id == user.id)
                      .order_by(Note.id.desc())).all()


@notes_router.get("/{note_id}", response_model=NoteOut)
def get_note(note: OwnNote):
    return note


@notes_router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note: OwnNote, db: DbSession):
    db.delete(note)
    db.commit()


# =============================================================================
# PART 7 — ROLES                                       would live in: routers/admin.py
# =============================================================================

admin_router = APIRouter(prefix="/admin", tags=["admin"],
                         dependencies=[Depends(require_admin)])


@admin_router.get("/users", response_model=list[UserOut])
def list_all_users(db: DbSession):
    return db.scalars(select(User).order_by(User.id)).all()


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(notes_router)
app.include_router(admin_router)


# =============================================================================
# COMMON MISTAKES
# =============================================================================
#
# 1. Storing passwords as plain text, or with a FAST hash like md5 or sha256.
#    Use a slow, salted password hash. PART 1.
#
# 2. Writing SECRET_KEY in the code and committing it to git. Anyone who reads
#    the repository can then create a token for any user. Use an env variable.
#
# 3. jwt.decode(token, key) without algorithms=[...]. Always pass it.
#
# 4. Putting private data in the token payload. It's readable by anyone. PART 2.
#
# 5. Different login errors for "unknown email" and "wrong password". They
#    tell attackers which emails to target. PART 4.
#
# 6. 403 when nobody is logged in (that's 401), and 403 for someone else's
#    item (use 404, so its existence isn't revealed). PARTS 5 and 6.
#
# 7. Sending the login as JSON. OAuth2PasswordRequestForm expects FORM data,
#    so JSON gets a 422. The tour shows it.
#
# 8. Trusting a client-sent owner_id or role. Who someone is comes from the
#    token; what they may do comes from the database.
#
# 9. Long-lived tokens. A stolen token works until it expires. Keep access
#    tokens short. (Real apps pair them with REFRESH tokens - see below.)
#
# WHAT THIS LESSON DELIBERATELY LEAVES OUT - learn these next, in this order:
#   refresh tokens (stay logged in without long-lived access tokens),
#   rate-limiting the login route (slow down password guessing),
#   revoking tokens (log out everywhere, or after a password change),
#   email verification and password reset, and "Sign in with Google" (OAuth).


# =============================================================================
# YOUR EXERCISE CODE GOES HERE - above the tour, so FastAPI registers it
# =============================================================================
# (Put exercise routes straight on the app: @app.get, @app.patch, and so on.)




# =============================================================================
# THE TOUR — runs when you execute this file with no flags
# =============================================================================

def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def tour(client):
    section("PART 1: HASHING PASSWORDS")
    part1_hashing_demo()

    section("PART 2: JSON WEB TOKENS")
    part2_jwt_demo()

    section("PART 4: REGISTER")
    response = show(client, "POST", "/auth/register",
                    note="a password goes in, and never comes back out",
                    json={"email": "Sidd@Example.com", "password": "correct-horse-battery",
                          "full_name": "Sidd"})
    sidd_id = response.json()["id"]
    show(client, "POST", "/auth/register", note="the same email again",
         json={"email": "sidd@example.com", "password": "another-password"})
    show(client, "POST", "/auth/register", note="a password that's too short",
         json={"email": "ana@example.com", "password": "123"})
    client.post("/auth/register", json={"email": "ana@example.com",
                                        "password": "ana-secret-password"})

    section("PART 4: LOG IN - form data, not JSON")
    show(client, "POST", "/auth/token", note="the wrong password",
         data={"username": "sidd@example.com", "password": "wrong-password"})
    show(client, "POST", "/auth/token", note="an email with no account: the SAME message",
         data={"username": "nobody@example.com", "password": "wrong-password"})
    show(client, "POST", "/auth/token", note="sent as JSON by mistake - a classic",
         json={"username": "sidd@example.com", "password": "correct-horse-battery"})
    response = show(client, "POST", "/auth/token", note="correct - here's a token",
                    data={"username": "sidd@example.com",
                          "password": "correct-horse-battery"})
    sidd_token = response.json()["access_token"]
    ana_token = client.post("/auth/token", data={
        "username": "ana@example.com", "password": "ana-secret-password"}).json()["access_token"]

    section("PART 5: USING THE TOKEN")
    show(client, "GET", "/users/me", note="no Authorization header")
    show(client, "GET", "/users/me", note="with sidd's token", headers=bearer(sidd_token))
    show(client, "GET", "/users/me", note="a made-up token",
         headers=bearer("not.a.token"))
    show(client, "GET", "/users/me", note="a real token for sidd - but expired",
         headers=bearer(create_access_token(sidd_id, minutes=-5)))
    show(client, "GET", "/users/me", note="sidd's token, edited to claim user 1 (the admin)",
         headers=bearer(forge_token(sidd_token, "1")))

    section("PART 6: OWNERSHIP - everyone sees only their own notes")
    show(client, "POST", "/notes", headers=bearer(sidd_token),
         json={"title": "Sidd's plan", "body": "learn FastAPI"})
    response = show(client, "POST", "/notes", headers=bearer(ana_token),
                    json={"title": "Ana's diary", "body": "private thoughts"})
    ana_note_id = response.json()["id"]
    show(client, "GET", "/notes", note="sidd lists notes - only his own",
         headers=bearer(sidd_token))
    show(client, "GET", f"/notes/{ana_note_id}", note="sidd tries to read Ana's note",
         headers=bearer(sidd_token))
    show(client, "DELETE", f"/notes/{ana_note_id}", note="...or delete it",
         headers=bearer(sidd_token))
    show(client, "GET", f"/notes/{ana_note_id}", note="Ana can read it, of course",
         headers=bearer(ana_token))

    section("PART 7: ROLES")
    show(client, "GET", "/admin/users", note="sidd is logged in, but not an admin",
         headers=bearer(sidd_token))
    admin_token = client.post("/auth/token", data={
        "username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}).json()["access_token"]
    show(client, "GET", "/admin/users", note="the admin", headers=bearer(admin_token))

    section("TRY IT YOURSELF IN /docs")
    print("  python 09_authentication.py --serve   then open /docs")
    print()
    print("   1. POST /auth/register with your own email and password.")
    print("   2. Click the green Authorize button at the top of the page.")
    print("      Put your EMAIL in the 'username' box, plus your password.")
    print("   3. Every padlocked route now sends your token automatically.")
    print("      Try GET /users/me, then create and list some notes.")
    print(f"   4. Log out, and Authorize again as {ADMIN_EMAIL} /")
    print(f"      {ADMIN_PASSWORD} to use GET /admin/users.")


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * Never store a password. Store a SALTED, SLOW hash of it, and compare
#     hashes at login. Compare them with compare_digest, not ==.
#   * A token is a signed note saying who you are and until when. Signed, not
#     encrypted: readable by anyone, changeable by nobody.
#   * Always pass algorithms=[...] to jwt.decode, and keep SECRET_KEY out of
#     your code.
#   * Login takes FORM data (username + password) because that's the OAuth2
#     standard - which is also why /docs gets an Authorize button for free.
#   * Give the SAME error for "no such email" and "wrong password", and take
#     the same TIME, or you're telling attackers which emails exist.
#   * get_current_user turns a token into a user, and looks them up in the
#     database every time - so deactivating an account takes effect at once.
#   * Ownership: someone else's item is a 404, not a 403. Never trust an
#     owner_id or role sent by the client - take it from the token.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. Why is SHA-256 a bad choice for passwords, even though it's a hash?
#   Q2. Can someone read what's inside a JWT you gave them?
#   Q3. Someone requests another user's note. Which status code, and why?
#   Q4. Why does the server look the user up on every request, when the token
#       already says who they are?
#   Q5. Where does owner_id come from when creating a note?
#
# ANSWERS
#   A1. It's FAST, so an attacker with a stolen database can try billions of
#       guesses. Password hashes must be deliberately slow, and salted.
#   A2. Yes - the payload is only encoded, not encrypted. They just can't
#       change it without breaking the signature.
#   A3. 404. A 403 would confirm the note exists, which is itself a leak.
#   A4. The account may have been deleted or deactivated since the token was
#       issued. The token is still validly signed either way.
#   A5. From the TOKEN (the logged-in user), never from the request body.


# =============================================================================
# EXERCISES
# =============================================================================
#
# Write your code in the "YOUR EXERCISE CODE GOES HERE" space above the tour,
# then run:
#     python 09_authentication.py --check
#
# Do the WARM-UPS first - both are one short route each.
#
# WARM-UP 1 (easy) — A route only a logged-in user can reach
#   Add GET /users/me/email returning {"email": "<their email>"}, using
#   user: CurrentUser. Write NO checking code - the dependency gives you the
#   401 for free.
#
# WARM-UP 2 (easy) — Count your own things
#   Add GET /my-note-count returning {"notes": N}, where N is how many notes
#   the LOGGED-IN user has. Filter by owner in the query, like list_my_notes.
#
# EXERCISE 1 (medium) — Edit your own profile
#   PATCH /users/me with a body like {"full_name": "Priya Nair"} (full_name
#   optional, max 100 characters). Changes the LOGGED-IN user and returns
#   them as UserOut. No token -> 401 (the CurrentUser dependency does that).
#
# EXERCISE 2 (challenge) — Change your password
#   POST /users/me/password with {"current_password": ..., "new_password": ...}
#   new_password: at least 8 characters.
#   Wrong current_password -> 400 with detail "Current password is incorrect".
#   Success -> 204. Afterwards, logging in with the OLD password must fail and
#   the NEW one must work.
#
# EXERCISE 3 (medium) — Edit your own note
#   PATCH /notes/{note_id} with optional title and body. Only the owner may
#   edit it: anyone else gets 404, exactly like reading it. Returns NoteOut.
#
# EXERCISE 4 (challenge) — An admin action
#   POST /admin/users/{user_id}/deactivate -> 204. Sets is_active to False.
#       not an admin                     -> 403
#       no such user                     -> 404
#       an admin deactivating THEMSELF   -> 400
#   Once deactivated, that user's existing token gets 403 on /users/me, and
#   logging in gets 403. (Parts 4 and 5 already handle that - check how.)


def checks(client):
    def login(email: str, password: str) -> str | None:
        r = client.post("/auth/token", data={"username": email, "password": password})
        return r.json().get("access_token") if r.status_code == 200 else None

    def register_and_login(email: str, password: str) -> str | None:
        client.post("/auth/register", json={"email": email, "password": password})
        return login(email, password)

    admin = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    priya = register_and_login("priya@example.com", "priya-password-1")
    tom = register_and_login("tom@example.com", "tom-password-1")
    check("the lesson's own register and login still work", admin and priya and tom)
    if not (admin and priya and tom):
        return

    # --- WARM-UP 1 ---
    r = client.get("/users/me/email", headers=bearer(priya))
    check("WARM-UP 1: GET /users/me/email returns the logged-in user's email",
          r.status_code == 200 and r.json().get("email") == "priya@example.com")
    check("WARM-UP 1: no token gives 401",
          client.get("/users/me/email").status_code == 401)

    # --- WARM-UP 2 ---
    client.post("/notes", json={"title": "warm-up note"}, headers=bearer(priya))
    mine = client.get("/notes", headers=bearer(priya)).json()
    r = client.get("/my-note-count", headers=bearer(priya))
    check("WARM-UP 2: GET /my-note-count counts only that user's notes",
          r.status_code == 200 and r.json().get("notes") == len(mine))
    r = client.get("/my-note-count", headers=bearer(tom))
    check("WARM-UP 2: a different user gets their own count (0)",
          r.status_code == 200 and r.json().get("notes") == 0)

    # --- EXERCISE 1 ---
    r = client.patch("/users/me", json={"full_name": "Priya Nair"}, headers=bearer(priya))
    check("EXERCISE 1: PATCH /users/me returns 200 with the new name",
          r.status_code == 200 and r.json().get("full_name") == "Priya Nair")
    r = client.get("/users/me", headers=bearer(priya))
    check("EXERCISE 1: the change was saved (GET /users/me shows it)",
          r.json().get("full_name") == "Priya Nair")
    check("EXERCISE 1: no token gives 401",
          client.patch("/users/me", json={"full_name": "Hacker"}).status_code == 401)

    # --- EXERCISE 2 ---
    r = client.post("/users/me/password", headers=bearer(tom),
                    json={"current_password": "not-my-password", "new_password": "tom-new-password"})
    check("EXERCISE 2: a wrong current password gives 400 with the right detail",
          r.status_code == 400 and r.json().get("detail") == "Current password is incorrect")
    r = client.post("/users/me/password", headers=bearer(tom),
                    json={"current_password": "tom-password-1", "new_password": "short"})
    check("EXERCISE 2: a new password under 8 characters gives 422", r.status_code == 422)
    r = client.post("/users/me/password", headers=bearer(tom),
                    json={"current_password": "tom-password-1", "new_password": "tom-new-password"})
    check("EXERCISE 2: a correct change gives 204", r.status_code == 204)
    check("EXERCISE 2: the OLD password no longer logs in",
          login("tom@example.com", "tom-password-1") is None)
    check("EXERCISE 2: the NEW password logs in",
          login("tom@example.com", "tom-new-password") is not None)

    # --- EXERCISE 3 ---
    r = client.post("/notes", json={"title": "Priya's plan", "body": "step one"},
                    headers=bearer(priya))
    note_id = r.json().get("id")
    r = client.patch(f"/notes/{note_id}", json={"title": "Priya's better plan"},
                     headers=bearer(priya))
    check("EXERCISE 3: the owner can change the title",
          r.status_code == 200 and r.json().get("title") == "Priya's better plan")
    check("EXERCISE 3: the body was left unchanged",
          r.status_code == 200 and r.json().get("body") == "step one")
    r = client.patch(f"/notes/{note_id}", json={"title": "hacked"}, headers=bearer(tom))
    check("EXERCISE 3: another user gets 404", r.status_code == 404)
    check("EXERCISE 3: no token gives 401",
          client.patch(f"/notes/{note_id}", json={"title": "hacked"}).status_code == 401)

    # --- EXERCISE 4 ---
    priya_id = client.get("/users/me", headers=bearer(priya)).json()["id"]
    admin_id = client.get("/users/me", headers=bearer(admin)).json()["id"]
    check("EXERCISE 4: a non-admin gets 403",
          client.post(f"/admin/users/{priya_id}/deactivate",
                      headers=bearer(tom)).status_code == 403)
    # "Not Found" is FastAPI's reply when NO route matches - so it doesn't count
    r = client.post("/admin/users/99999/deactivate", headers=bearer(admin))
    check("EXERCISE 4: an unknown user gives 404",
          r.status_code == 404 and r.json().get("detail") != "Not Found")
    check("EXERCISE 4: an admin deactivating themself gets 400",
          client.post(f"/admin/users/{admin_id}/deactivate",
                      headers=bearer(admin)).status_code == 400)
    r = client.post(f"/admin/users/{priya_id}/deactivate", headers=bearer(admin))
    check("EXERCISE 4: the admin deactivating priya gets 204", r.status_code == 204)
    check("EXERCISE 4: priya's existing token now gets 403",
          r.status_code == 204
          and client.get("/users/me", headers=bearer(priya)).status_code == 403)
    r = client.post("/auth/token", data={"username": "priya@example.com",
                                         "password": "priya-password-1"})
    check("EXERCISE 4: priya can no longer log in (403)", r.status_code == 403)


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP 1
#   @app.get("/users/me/email")
#   def read_my_email(user: CurrentUser):
#       return {"email": user.email}
#
# WARM-UP 2
#   @app.get("/my-note-count")
#   def my_note_count(user: CurrentUser, db: DbSession):
#       total = db.scalar(select(func.count(Note.id))
#                         .where(Note.owner_id == user.id))
#       return {"notes": total}
#
#   func.count asks the DATABASE to count, instead of loading every note and
#   using len(). func is imported at the top of this lesson already.
#
# EXERCISE 1
#   class UserUpdate(BaseModel):
#       full_name: str | None = Field(default=None, max_length=100)
#
#   @app.patch("/users/me", response_model=UserOut)
#   def update_me(changes: UserUpdate, user: CurrentUser, db: DbSession):
#       for field, value in changes.model_dump(exclude_unset=True).items():
#           setattr(user, field, value)
#       db.commit()
#       db.refresh(user)
#       return user
#
#   Why db.commit() saves `user`: get_current_user loaded it with the SAME
#   session this route receives (lesson 07's dependency caching).
#
# EXERCISE 2
#   class PasswordChange(BaseModel):
#       current_password: str
#       new_password: str = Field(min_length=8, max_length=128)
#
#   @app.post("/users/me/password", status_code=204)
#   def change_password(data: PasswordChange, user: CurrentUser, db: DbSession):
#       if not verify_password(data.current_password, user.hashed_password):
#           raise HTTPException(status_code=400, detail="Current password is incorrect")
#       user.hashed_password = hash_password(data.new_password)
#       db.commit()
#
#   Asking for the current password stops someone who grabs an unlocked
#   laptop from locking the real owner out.
#
#   A limitation to notice: tokens issued BEFORE the change still work until
#   they expire. Real apps fix that with a "token version" number stored on
#   the user, put in each token, and bumped on every password change.
#
# EXERCISE 3
#   class NoteUpdate(BaseModel):
#       title: str | None = Field(default=None, min_length=1, max_length=120)
#       body: str | None = Field(default=None, max_length=10_000)
#
#   @app.patch("/notes/{note_id}", response_model=NoteOut)
#   def update_note(note: OwnNote, changes: NoteUpdate, db: DbSession):
#       for field, value in changes.model_dump(exclude_unset=True).items():
#           setattr(note, field, value)
#       db.commit()
#       db.refresh(note)
#       return note
#
#   All the ownership logic is in get_own_note, so this route can't get it
#   wrong. That's the payoff of lesson 07.
#
# EXERCISE 4
#   @app.post("/admin/users/{user_id}/deactivate", status_code=204)
#   def deactivate_user(user_id: int,
#                       admin: Annotated[User, Depends(require_admin)],
#                       db: DbSession):
#       if user_id == admin.id:
#           raise HTTPException(status_code=400,
#                               detail="You can't deactivate your own account")
#       user = db.get(User, user_id)
#       if user is None:
#           raise HTTPException(status_code=404, detail="User not found")
#       user.is_active = False
#       db.commit()
#
#   The 403s afterwards come for free: get_current_user and login both check
#   is_active. Because get_current_user reads the user from the database on
#   EVERY request, deactivation takes effect immediately - even though the
#   token itself is still validly signed.


if __name__ == "__main__":
    start(app, tour, checks)


print("\nNext: python 10_testing.py")

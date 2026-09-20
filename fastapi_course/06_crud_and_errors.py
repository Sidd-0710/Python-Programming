"""
===============================================================================
 FASTAPI COURSE - LESSON 06: CRUD, STATUS CODES AND ERRORS
===============================================================================

Time: about 90 minutes (there's a good place for a break halfway).
Assumes: lessons 00-05.

THREE WAYS TO RUN THIS FILE:

    python 06_crud_and_errors.py            the TOUR (read this first)
    python 06_crud_and_errors.py --serve    a REAL server at /docs
    python 06_crud_and_errors.py --check    grades your exercise answers

This is the lesson where it all comes together. You'll build a complete task
manager API - the same five jobs from lesson 01 PART 9, now as real endpoints
with real status codes and real error responses.


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL LEARN TO:
  1. write the three models one resource needs                     (PART 1)
  2. store things in a dict keyed by id, and hand out new ids      (PART 2)
  3. send a real 404 instead of {"error": "not found"}             (PART 3a)
  4. invent your own error type for business rules                 (PART 3b)
  5. reshape every 422 into a format you choose                    (PART 3c)
  6. create with 201, and say where the new thing lives            (PART 4)
  7. list with filters, search, sorting and pages                  (PART 5)
  8. tell PUT (replace) apart from PATCH (change part)             (PART 6)
  9. delete with 204, and add an action endpoint with a 409        (PARTS 7-8)

NEW WORDS - come back here whenever you forget one:

  resource       one kind of thing your API manages: tasks, users, orders
  CRUD           Create, Read, Update, Delete
  HTTPException  the error you RAISE to stop and send a status code:
                 raise HTTPException(status_code=404, detail="...")
  detail         the message inside an error response: {"detail": "..."}
  201 Created    success code for "I made a new thing"
  204 No Content success code for "done, and there's nothing to send back".
                 A 204 body MUST be empty.
  404 Not Found  that thing doesn't exist
  405            that path exists, but not with the method you used
  409 Conflict   it clashes with what's already there (duplicate title,
                 completing an already-completed task)
  422            the data broke a rule (FastAPI sends this for you)
  500            YOUR code crashed. Never show the client the details.
  exception      a function that turns one kind of error into a response,
  handler        registered with @app.exception_handler(...)
  Location       a header saying where the newly created thing lives
  type alias     a name for a type you'd otherwise repeat:
                 Priority = Literal["low", "medium", "high"]
  skip / limit   how many to jump over, and how many to return (paging)

PYTHON YOU NEED:
  * a dict keyed by id       tasks_db[7]          (lesson 01 PART 4)
  * list comprehensions      [t for t in ... if ...]   (lesson 01 PART 8)
  * passing a function as a value   results.sort(key=task_id_of)
                             (lesson 04 PART 0e - no brackets after the name)
  * your own exception class  class TaskRuleError(Exception)  (lesson 02)


-------------------------------------------------------------------------------
 THEORY: ONE RESOURCE, SIX ENDPOINTS
-------------------------------------------------------------------------------

A "resource" is one kind of thing your API manages: tasks, users, orders.
Almost every resource gets the same set of endpoints:

  JOB           METHOD + PATH          SUCCESS            USUAL FAILURES
  ------------  ---------------------  -----------------  -------------------
  create        POST   /tasks          201 Created        422 invalid body
  list          GET    /tasks          200 OK             422 bad query
  read one      GET    /tasks/{id}     200 OK             404 not found
  replace       PUT    /tasks/{id}     200 OK             404, 422
  change part   PATCH  /tasks/{id}     200 OK             404, 422
  delete        DELETE /tasks/{id}     204 No Content     404

Learn this table. You'll build it dozens of times, for every resource.


PUT vs PATCH
------------
  PUT    "here is the COMPLETE new version". Fields you leave out go back to
         their defaults. Like replacing a whole document.
  PATCH  "change ONLY these fields". Everything else stays. Like editing
         one cell in a spreadsheet. Uses lesson 05 PART 7's exclude_unset.

Most real apps mainly use PATCH. The tour shows both side by side.


ERRORS ARE PART OF YOUR API
---------------------------
Frontend developers write code like `if response.status == 404: show "not
found" page`. So your errors are a promise, just like your successful
responses:

  4xx = the CLIENT did something wrong -> tell them exactly what, so they
        can fix it
  5xx = YOUR code broke -> tell them nothing about internals (no stack
        traces, no SQL, no file paths). Log the details on the server.


THREE TOOLS FOR ERRORS, FROM SIMPLEST TO MOST POWERFUL
------------------------------------------------------
  1. raise HTTPException(status_code=404, detail="Task 7 not found")
       Stop right here and send this error. Lesson 02 part 6 promised this.

  2. A custom exception class + @app.exception_handler
       For business rules ("titles must be unique"), raised anywhere in your
       code. One handler turns every one of them into a response.

  3. A handler for RequestValidationError
       Reshapes EVERY automatic 422 into a format you choose.
"""

from datetime import date, datetime, timezone
from itertools import count
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Path, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, model_validator

from course_tools import check, section, show, start

app = FastAPI(
    title="Lesson 06 - Task Manager API",
    description="Complete CRUD with proper status codes and error handling.",
    version="1.0.0",
)


# =============================================================================
# PART 1 — THE MODELS: ONE FOR EACH JOB
# =============================================================================
#
# Lesson 05's rule, applied: separate models for create, update, and output.

# A type alias - a name for a type you'd otherwise repeat. Priority now means
# "exactly one of these three strings" wherever it's used.
Priority = Literal["low", "medium", "high"]


class TaskCreate(BaseModel):          # POST body, and PUT body
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    priority: Priority = "medium"
    due_date: date | None = None


class TaskUpdate(BaseModel):          # PATCH body - every field optional
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    priority: Priority | None = None
    due_date: date | None = None
    done: bool | None = None

    # A real bug this prevents: a client sends {"title": null}. It counts as
    # "sent" (lesson 05 PART 7), so it would set the title to None - and then
    # TaskOut, which says title is a str, would crash with a 500.
    #
    # model_fields_set is the set of field names the client actually SENT.
    # getattr(self, name) reads a field whose name is stored in a variable:
    # getattr(self, "title") is the same as self.title.
    @model_validator(mode="after")
    def reject_null_for_required_fields(self) -> "TaskUpdate":
        for name in ["title", "priority", "done"]:
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} can't be null - leave it out to keep the current value")
        return self


class TaskOut(BaseModel):             # every response that contains a task
    id: int
    title: str
    description: str | None
    priority: Priority
    due_date: date | None
    done: bool
    created_at: datetime
    updated_at: datetime


class TaskPage(BaseModel):            # the list endpoint's response
    total: int                        # how many tasks matched, across ALL pages
    skip: int
    limit: int
    items: list[TaskOut]              # just this page


# =============================================================================
# PART 2 — STORAGE: A DICT KEYED BY ID
# =============================================================================
#
# Lessons 03-05 used a LIST and looped to find an id. A DICT keyed by id is
# better: tasks_db[7] finds task 7 instantly, however many tasks there are.
#
#     tasks_db = {1: {"id": 1, "title": ...}, 2: {"id": 2, "title": ...}}
#
# `count(start=1)` makes a counter: next(task_ids) gives 1, then 2, then 3...
# Ids are never reused, even after a delete - just like a real database.
#
# Lesson 08 replaces all of this with a real database. The ROUTES barely change.

tasks_db: dict[int, dict] = {}
task_ids = count(start=1)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def insert_task(data: TaskCreate) -> dict:
    now = utc_now()
    task_id = next(task_ids)
    # Build the stored record: the new id, the fields the client sent, then
    # the fields the SERVER decides (never trust a client for these).
    record = {"id": task_id}
    record.update(data.model_dump())
    record["done"] = False
    record["created_at"] = now
    record["updated_at"] = now
    tasks_db[task_id] = record
    return record


# A few starting tasks, so --serve has data to show.
insert_task(TaskCreate(title="Write the API spec", priority="high",
                       due_date=date(2026, 9, 20)))
insert_task(TaskCreate(title="Set up the database",
                       description="Postgres locally, SQLite in tests"))
insert_task(TaskCreate(title="Buy coffee beans", priority="low"))


# =============================================================================
# PART 3 — ERROR TOOLS
# =============================================================================

# ---- 3a. The "get or 404" helper --------------------------------------------
#
# Three routes need "find task N, or stop with a 404". Write it ONCE.
# Raising HTTPException stops the function immediately - the route that called
# this helper stops too - and FastAPI sends:
#     404   {"detail": "Task 99 not found"}
#
# status.HTTP_404_NOT_FOUND is just the number 404 with a readable name.
# Both work; the names make code easier to scan.
def get_task_or_404(task_id: int) -> dict:
    task = tasks_db.get(task_id)            # .get gives None instead of crashing
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task {task_id} not found")
    return task

# In plain English: "give me task N. If there isn't one, stop everything and
# send a 404." Because it RAISES, the route that called it never continues -
# so routes can use it as one line and forget about the missing case.

# TRY IT NOW (2 minutes):
#   Change the detail text to something of your own, run the tour, and find
#   it in the GET /tasks/99 output. [That message is what a frontend
#   developer will see - write it for them, not for yourself.]


# ---- 3b. A custom exception for business rules ------------------------------
#
# HTTPException is fine inside routes. But a rule like "titles must be unique"
# might be checked deep inside helper code that shouldn't know about HTTP.
# So we make our OWN exception type, raise it anywhere, and teach FastAPI -
# once - how to turn it into a response.
#
# `class TaskRuleError(Exception)` inherits from Python's Exception, so it can
# be raised and caught. super().__init__(message) runs Exception's own setup.
class TaskRuleError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.code = code            # a short, stable code clients can check
        self.message = message      # a human-readable explanation


# This function runs whenever ANY route raises TaskRuleError.
# The response keeps the {"detail": ...} shape HTTPException uses, so clients
# read every error the same way - plus a machine-friendly code.
@app.exception_handler(TaskRuleError)
async def handle_task_rule_error(request: Request, error: TaskRuleError):
    return JSONResponse(status_code=error.status_code,
                        content={"detail": error.message, "code": error.code})


def ensure_unique_title(title: str, ignore_id: int | None = None) -> None:
    for task in tasks_db.values():
        if task["id"] != ignore_id and task["title"].lower() == title.lower():
            raise TaskRuleError(status.HTTP_409_CONFLICT, "duplicate_title",
                                f"A task called '{task['title']}' already exists (id {task['id']})")


# ---- 3c. Reshaping every 422 -------------------------------------------------
#
# Lesson 03 promised this. FastAPI's default 422 body is detailed but noisy
# for a frontend developer. This handler replaces it for the WHOLE app with:
#     {"detail": "Validation failed",
#      "errors": [{"field": "body.title", "message": "..."}]}
#
# 422 is written as a number here: its named constant was renamed in recent
# versions of Starlette (the library under FastAPI), and the number never changes.
@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, error: RequestValidationError):
    problems = []
    for problem in error.errors():
        field = ".".join(str(part) for part in problem["loc"])
        problems.append({"field": field, "message": problem["msg"]})
    return JSONResponse(status_code=422,
                        content={"detail": "Validation failed", "errors": problems})


# Another type alias: every {task_id} in this file gets the same rule.
TaskId = Annotated[int, Path(ge=1)]


# =============================================================================
# PART 4 — CREATE:  POST /tasks  ->  201 Created
# =============================================================================
#
# status_code=201 changes the SUCCESS code for this route.
#
# `response: Response` is a special parameter: FastAPI hands you the response
# object it's about to send, so you can add headers. A Location header telling
# the client where the new resource lives is standard practice after a 201.
@app.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, response: Response):
    ensure_unique_title(task.title)
    record = insert_task(task)
    response.headers["Location"] = f"/tasks/{record['id']}"
    return record


# =============================================================================
# PART 5 — READ:  GET /tasks  and  GET /tasks/{task_id}
# =============================================================================

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


# sort() needs a function that says WHAT to compare (lesson 04 PART 0e).
# These three give it one each - and a name you can read.
def task_id_of(task: dict) -> int:
    return task["id"]


def priority_rank_of(task: dict) -> int:
    return PRIORITY_RANK[task["priority"]]


def due_date_of(task: dict) -> date:
    if task["due_date"] is None:
        return date.max          # no due date -> sorts LAST
    return task["due_date"]


@app.get("/tasks", response_model=TaskPage)
def list_tasks(
    done: bool | None = None,
    priority: Priority | None = None,
    q: Annotated[str | None, Query(min_length=1, max_length=50,
                                   description="Search in title and description")] = None,
    sort: Literal["newest", "oldest", "priority", "due_date"] = "newest",
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    results = list(tasks_db.values())       # the dict's values, as a list

    if done is not None:
        results = [t for t in results if t["done"] == done]
    if priority is not None:
        results = [t for t in results if t["priority"] == priority]
    if q is not None:
        needle = q.lower()
        results = [t for t in results
                   if needle in t["title"].lower()
                   or needle in (t["description"] or "").lower()]

    # key=task_id_of hands over the FUNCTION itself - no brackets after it.
    if sort == "newest":
        results.sort(key=task_id_of, reverse=True)
    elif sort == "oldest":
        results.sort(key=task_id_of)
    elif sort == "priority":
        results.sort(key=priority_rank_of)
    else:
        results.sort(key=due_date_of)

    return {"total": len(results), "skip": skip, "limit": limit,
            "items": results[skip:skip + limit]}


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: TaskId):
    return get_task_or_404(task_id)          # one line, thanks to the helper


# =============================================================================
# PART 6 — UPDATE:  PUT (replace) and PATCH (change part)
# =============================================================================

@app.put("/tasks/{task_id}", response_model=TaskOut)
def replace_task(task_id: TaskId, task: TaskCreate):
    existing = get_task_or_404(task_id)
    ensure_unique_title(task.title, ignore_id=task_id)
    # model_dump() WITHOUT exclude_unset: every field is written, so anything
    # the client left out goes back to its default. That's what PUT means.
    existing.update(task.model_dump())
    existing["updated_at"] = utc_now()
    return existing


@app.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: TaskId, changes: TaskUpdate):
    existing = get_task_or_404(task_id)
    updates = changes.model_dump(exclude_unset=True)    # ONLY what was sent
    if "title" in updates:
        ensure_unique_title(updates["title"], ignore_id=task_id)
    existing.update(updates)
    existing["updated_at"] = utc_now()
    return existing

# TRY IT NOW (3 minutes):
#   In update_task above, change model_dump(exclude_unset=True) to plain
#   model_dump() and run the tour. [The PATCH in the tour now wipes the
#   description, because unsent fields arrive as None. Put it back - this is
#   the single most common PATCH bug.]


# -----------------------------------------------------------------------------
#  GOOD PLACE FOR A BREAK. Create, read, list and update are done - that's
#  most of any API. After the break: delete, action endpoints, and what
#  happens when your own code crashes.
# -----------------------------------------------------------------------------


# =============================================================================
# PART 7 — DELETE:  DELETE /tasks/{task_id}  ->  204 No Content
# =============================================================================
#
# 204 means "it worked, and there's nothing to send back". A 204 response must
# have an EMPTY body - so the function returns nothing at all.
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: TaskId):
    get_task_or_404(task_id)                 # 404 if it doesn't exist
    tasks_db.pop(task_id)                    # .pop removes a key from a dict


# =============================================================================
# PART 8 — ACTIONS THAT AREN'T PLAIN CRUD
# =============================================================================
#
# "Complete this task" could be PATCH {"done": true}. But when an action has
# its own rules, a dedicated endpoint - a verb under the resource - is clearer.
# Completing an already-completed task conflicts with the current state: 409.
@app.post("/tasks/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: TaskId):
    task = get_task_or_404(task_id)
    if task["done"]:
        raise TaskRuleError(status.HTTP_409_CONFLICT, "already_done",
                            f"Task {task_id} is already done")
    task["done"] = True
    task["updated_at"] = utc_now()
    return task


# =============================================================================
# PART 9 — WHEN YOUR CODE CRASHES: 500
# =============================================================================
#
# A bug that raises an exception nobody handles becomes a 500 Internal Server
# Error. The client sees only "Internal Server Error" - the traceback is
# printed in the SERVER's terminal, where only you can see it. That's correct:
# never send internal details to clients.
# include_in_schema=False keeps this route out of /docs.
@app.get("/debug/crash", include_in_schema=False)
def crash():
    tasks = []
    return {"first_task": tasks[0]}          # IndexError: the list is empty


# =============================================================================
# COMMON MISTAKES
# =============================================================================
#
# 1. `return HTTPException(...)` instead of `raise HTTPException(...)`.
#    Returning it sends a 200 with a strange body. Errors are RAISED.
#
# 2. Returning {"error": "not found"} with a 200 status (what lessons 03-05
#    did as a placeholder). Clients check the status code FIRST. A 200 says
#    "success", whatever the body says.
#
# 3. Returning a body from a 204 route. 204 must be empty. Return nothing.
#
# 4. PATCH with model_dump() instead of model_dump(exclude_unset=True) -
#    every unsent field gets wiped. Lesson 05 PART 7.
#
# 5. Using 400 for everything. Be specific: 404 missing, 409 conflicts with
#    current state, 422 invalid input, 401/403 for auth (lesson 09).
#
# 6. Putting internal details in error messages:
#       detail=f"SQL error: {error}"       # leaks your database structure
#    Log the details on the server; tell the client something safe.
#
# 7. Forgetting the unique-check on UPDATE, not just on create - a PATCH can
#    rename a task to a title that's already taken. (ignore_id handles the
#    case of a task keeping its own title.)


# =============================================================================
# YOUR EXERCISE CODE GOES HERE - above the tour, so FastAPI registers it
# =============================================================================




# =============================================================================
# THE TOUR — runs when you execute this file with no flags
# =============================================================================

def tour(client):
    section("PART 4: CREATE - POST /tasks")
    show(client, "POST", "/tasks", note="201 Created, plus a Location header",
         json={"title": "Review pull request", "priority": "high",
               "due_date": "2026-09-18"})
    show(client, "POST", "/tasks", note="invalid body - see the RESHAPED 422 (PART 3c)",
         json={"title": "", "priority": "urgent", "due_date": "someday"})
    show(client, "POST", "/tasks", note="a duplicate title - our TaskRuleError -> 409",
         json={"title": "buy COFFEE beans"})

    section("PART 5: READ - one task, and a missing one")
    show(client, "GET", "/tasks/1")
    show(client, "GET", "/tasks/99", note="HTTPException from get_task_or_404")
    show(client, "GET", "/tasks/0", note="breaks Path(ge=1) - a 422, before any lookup")

    section("PART 5: READ - the list, with filters and pages")
    show(client, "GET", "/tasks?priority=high&sort=due_date",
         note="all high-priority tasks, soonest due first")
    show(client, "GET", "/tasks?q=database", note="search title and description")
    show(client, "GET", "/tasks?sort=oldest&limit=1&skip=1",
         note="page 2 when pages are 1 task long. Note total vs items")
    show(client, "GET", "/tasks?limit=0", note="a bad query value - also reshaped")

    section("PART 6: PATCH - change only what you send")
    show(client, "PATCH", "/tasks/2", json={"priority": "high"})
    print("\n  The description 'Postgres locally, SQLite in tests' survived.")
    show(client, "PATCH", "/tasks/2", note="an explicit null for a required field",
         json={"title": None})
    show(client, "PATCH", "/tasks/99", json={"done": True})

    section("PART 6: PUT - replace the whole thing")
    show(client, "PUT", "/tasks/2", note="description and due_date NOT sent...",
         json={"title": "Set up the database", "priority": "low"})
    print("\n  ...so description went back to null. PUT replaces; PATCH edits.")

    section("PART 8: AN ACTION ENDPOINT, AND A 409")
    show(client, "POST", "/tasks/3/complete")
    show(client, "POST", "/tasks/3/complete", note="already done - conflicts with its state")

    section("PART 7: DELETE - 204, then gone")
    show(client, "DELETE", "/tasks/3", note="204 means success with an EMPTY body")
    show(client, "GET", "/tasks/3", note="it's really gone")
    show(client, "DELETE", "/tasks/3", note="deleting again is a 404")

    section("ERRORS YOU DIDN'T WRITE - FastAPI's defaults")
    show(client, "GET", "/projects", note="no such path -> 404")
    show(client, "DELETE", "/tasks", note="the path exists, but not with DELETE -> 405")

    section("PART 9: A BUG IN YOUR CODE -> 500")
    show(client, "GET", "/debug/crash")
    print("\n  The client learns nothing about the IndexError. With --serve, the")
    print("  full traceback appears in the server's terminal instead.")


# =============================================================================
# RECAP - WHAT YOU JUST LEARNED
# =============================================================================
#
#   * One resource, six endpoints: POST (201), GET list, GET one, PUT, PATCH,
#     DELETE (204). Learn that table once and every resource is the same.
#   * raise HTTPException(status_code=404, detail="...") - RAISE, never
#     return. A "get it or 404" helper turns the missing case into one line.
#   * Your own exception class + @app.exception_handler lets business rules
#     ("titles must be unique") live away from HTTP, in one place.
#   * A handler for RequestValidationError reshapes every 422 in the app.
#   * PUT replaces the whole thing; PATCH changes only what was sent, using
#     model_dump(exclude_unset=True).
#   * Pick the specific code: 404 missing, 409 conflicts with current state,
#     422 invalid data, 405 wrong method, 500 your bug (details stay secret).
#   * A dict keyed by id finds one item instantly - no loop needed.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. What's the difference between PUT and PATCH?
#   Q2. Why must a 204 response have an empty body?
#   Q3. A client asks to complete a task that's already done. Which code?
#   Q4. What goes wrong if you `return HTTPException(...)`?
#   Q5. Your code crashes with an IndexError. What should the client see?
#
# ANSWERS
#   A1. PUT sends the COMPLETE new version - anything left out goes back to
#       its default. PATCH changes only the fields that were sent.
#   A2. 204 means "no content" - it's a promise that there's nothing to read.
#   A3. 409 Conflict - the request clashes with the thing's current state.
#   A4. It's sent as a normal 200 response with an odd body. Errors are RAISED.
#   A5. Only "Internal Server Error" with a 500. The traceback belongs in your
#       server log, never in the response.


# =============================================================================
# EXERCISES — BUILD A CONTACTS API
# =============================================================================
#
# Build a second resource, /contacts, from scratch, using everything above.
# Write it in the "YOUR EXERCISE CODE GOES HERE" space, then run:
#     python 06_crud_and_errors.py --check
#
# Do the WARM-UPS first - they use the TASKS code that already exists, so
# they're two short routes each.
#
# WARM-UP 1 (easy) — Reuse the 404 helper
#   Add GET /tasks/{task_id}/title returning {"title": "<that task's title>"}.
#   Use get_task_or_404, so an unknown id answers 404 with no extra work.
#
# WARM-UP 2 (easy) — A summary route
#   Add GET /stats returning {"total": <how many tasks>, "done": <how many
#   are done>}. Count the done ones with a loop over tasks_db.values().
#
# A contact has:
#     id          int, set by the server
#     name        text, 1 to 100 characters
#     email       a valid email - no two contacts may share one
#     phone       text up to 20 characters, optional (None when not given)
#     favourite   bool, defaults to False
#
# You'll need ContactCreate, ContactUpdate and ContactOut models, a contacts_db
# dict, and an id counter. Store emails lowercased so the unique check can
# compare them (a field validator, or .lower() when saving).
#
# EXERCISE 1 (medium) — Create
#   POST /contacts -> 201 with the new contact (response_model=ContactOut).
#
# EXERCISE 2 (easy) — Read one
#   GET /contacts/{contact_id} -> 200, or 404 with the EXACT detail
#   "Contact not found". Write a get_contact_or_404 helper - you'll reuse it.
#
# EXERCISE 3 (medium) — Partial update
#   PATCH /contacts/{contact_id} -> changes only the fields sent; 404 (same
#   detail) if the contact doesn't exist.
#
# EXERCISE 4 (challenge) — List and search
#   GET /contacts -> a plain LIST of contacts (not a page object), with
#   optional query parameters:
#       q          case-insensitive search in the name
#       favourite  true/false filter
#       skip       default 0, at least 0
#       limit      default 20, between 1 and 100
#
# EXERCISE 5 (medium) — Unique emails
#   Creating a contact with an email that's already in use -> 409 Conflict.
#   (HTTPException or TaskRuleError both work.)
#
# EXERCISE 6 (easy) — Delete
#   DELETE /contacts/{contact_id} -> 204 with no body; 404 if it doesn't exist.
#
# STRETCH (no automatic check): make PATCH enforce unique emails too, and
# reject {"name": null} the way TaskUpdate does.


def checks(client):
    check("the lesson's own GET /tasks still works",
          client.get("/tasks").status_code == 200)

    # --- WARM-UP 1 ---
    r = client.get("/tasks/1/title")
    check("WARM-UP 1: GET /tasks/1/title returns its title",
          r.status_code == 200 and "title" in r.json())
    r = client.get("/tasks/99999/title")
    check("WARM-UP 1: an unknown id gives 404 from the helper",
          r.status_code == 404
          and "not found" in str(r.json().get("detail", "")).lower())

    # --- WARM-UP 2 ---
    listing = client.get("/tasks?limit=100").json()
    done_count = 0
    for task in listing["items"]:
        if task["done"]:
            done_count += 1
    r = client.get("/stats")
    body = r.json() if r.status_code == 200 else {}
    check("WARM-UP 2: GET /stats reports the total number of tasks",
          r.status_code == 200 and body.get("total") == listing["total"])
    check("WARM-UP 2: it also reports how many are done",
          body.get("done") == done_count)

    # --- EXERCISE 1 ---
    r = client.post("/contacts", json={"name": "Ana Lopez", "email": "ana@example.com",
                                       "phone": "555-0101"})
    created = r.json() if r.status_code == 201 else {}
    check("EXERCISE 1: POST /contacts returns 201 Created", r.status_code == 201)
    check("EXERCISE 1: the new contact has an id, and favourite is false",
          "id" in created and created.get("favourite") is False)
    check("EXERCISE 1: an invalid email gives 422",
          client.post("/contacts", json={"name": "Bad",
                                         "email": "not-an-email"}).status_code == 422)
    check("EXERCISE 1: an empty name gives 422",
          client.post("/contacts", json={"name": "",
                                         "email": "empty@example.com"}).status_code == 422)

    contact_id = created.get("id")
    if contact_id is None:
        check("EXERCISES 2-6 need EXERCISE 1 working first", False)
        return

    # --- EXERCISE 2 ---
    r = client.get(f"/contacts/{contact_id}")
    check("EXERCISE 2: GET /contacts/{id} returns the contact",
          r.status_code == 200 and r.json().get("name") == "Ana Lopez")
    r = client.get("/contacts/999999")
    check("EXERCISE 2: an unknown id gives 404 'Contact not found'",
          r.status_code == 404 and r.json().get("detail") == "Contact not found")

    # --- EXERCISE 3 ---
    r = client.patch(f"/contacts/{contact_id}", json={"favourite": True})
    body = r.json() if r.status_code == 200 else {}
    check("EXERCISE 3: PATCH favourite=true returns 200 with favourite true",
          body.get("favourite") is True)
    check("EXERCISE 3: fields that weren't sent are unchanged",
          body.get("name") == "Ana Lopez" and body.get("phone") == "555-0101")
    r = client.patch("/contacts/999999", json={"favourite": True})
    check("EXERCISE 3: PATCH on an unknown id gives 404 'Contact not found'",
          r.status_code == 404 and r.json().get("detail") == "Contact not found")

    # --- EXERCISE 4 ---
    client.post("/contacts", json={"name": "Marco Rossi", "email": "marco@example.com"})
    client.post("/contacts", json={"name": "Priya Nair", "email": "priya@example.com",
                                   "favourite": True})
    r = client.get("/contacts")
    everyone = r.json() if r.status_code == 200 else None
    check("EXERCISE 4: GET /contacts returns a list of all 3 contacts",
          isinstance(everyone, list) and len(everyone) == 3)
    r = client.get("/contacts?q=MARCO")
    found = r.json() if r.status_code == 200 else None
    check("EXERCISE 4: ?q=MARCO finds only Marco",
          isinstance(found, list) and [c.get("name") for c in found] == ["Marco Rossi"])
    r = client.get("/contacts?favourite=true")
    found = r.json() if r.status_code == 200 else None
    check("EXERCISE 4: ?favourite=true finds the 2 favourites",
          isinstance(found, list) and len(found) == 2
          and all(c.get("favourite") is True for c in found))
    r = client.get("/contacts?limit=1&skip=1")
    found = r.json() if r.status_code == 200 else None
    check("EXERCISE 4: ?limit=1&skip=1 returns exactly 1 contact",
          isinstance(found, list) and len(found) == 1)
    check("EXERCISE 4: ?limit=0 gives 422",
          client.get("/contacts?limit=0").status_code == 422)

    # --- EXERCISE 5 ---
    r = client.post("/contacts", json={"name": "Another Ana", "email": "ana@example.com"})
    check("EXERCISE 5: a duplicate email gives 409", r.status_code == 409)
    r = client.post("/contacts", json={"name": "Loud Ana", "email": "ANA@EXAMPLE.COM"})
    check("EXERCISE 5: the duplicate check ignores upper/lower case", r.status_code == 409)

    # --- EXERCISE 6 ---
    r = client.delete(f"/contacts/{contact_id}")
    check("EXERCISE 6: DELETE returns 204 with an empty body",
          r.status_code == 204 and not r.content)
    check("EXERCISE 6: the contact is really gone (GET -> 404)",
          client.get(f"/contacts/{contact_id}").status_code == 404)
    check("EXERCISE 6: deleting it again gives 404",
          client.delete(f"/contacts/{contact_id}").status_code == 404)


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP 1
#   @app.get("/tasks/{task_id}/title")
#   def get_task_title(task_id: TaskId):
#       task = get_task_or_404(task_id)
#       return {"title": task["title"]}
#
# WARM-UP 2
#   @app.get("/stats")
#   def task_stats():
#       done = 0
#       for task in tasks_db.values():
#           if task["done"]:
#               done += 1
#       return {"total": len(tasks_db), "done": done}
#
# MODELS AND STORAGE
#   class ContactCreate(BaseModel):
#       name: str = Field(min_length=1, max_length=100)
#       email: EmailStr
#       phone: str | None = Field(default=None, max_length=20)
#       favourite: bool = False
#
#   class ContactUpdate(BaseModel):
#       name: str | None = Field(default=None, min_length=1, max_length=100)
#       email: EmailStr | None = None
#       phone: str | None = Field(default=None, max_length=20)
#       favourite: bool | None = None
#
#   class ContactOut(BaseModel):
#       id: int
#       name: str
#       email: EmailStr
#       phone: str | None
#       favourite: bool
#
#   contacts_db: dict[int, dict] = {}
#   contact_ids = count(start=1)
#
#   def get_contact_or_404(contact_id: int) -> dict:
#       contact = contacts_db.get(contact_id)
#       if contact is None:
#           raise HTTPException(status_code=404, detail="Contact not found")
#       return contact
#
# EXERCISE 1 + EXERCISE 5
#   @app.post("/contacts", response_model=ContactOut, status_code=201)
#   def create_contact(contact: ContactCreate):
#       email = contact.email.lower()
#       for existing in contacts_db.values():
#           if existing["email"] == email:
#               raise HTTPException(status_code=409, detail="Email already in use")
#       contact_id = next(contact_ids)
#       record = {"id": contact_id}
#       record.update(contact.model_dump())
#       record["email"] = email          # keep the lowercased version
#       contacts_db[contact_id] = record
#       return record
#
#   Setting record["email"] AFTER the update() is what makes the lowercased
#   email win over the one the client sent.
#
# EXERCISE 2
#   @app.get("/contacts/{contact_id}", response_model=ContactOut)
#   def get_contact(contact_id: int):
#       return get_contact_or_404(contact_id)
#
# EXERCISE 3
#   @app.patch("/contacts/{contact_id}", response_model=ContactOut)
#   def update_contact(contact_id: int, changes: ContactUpdate):
#       contact = get_contact_or_404(contact_id)
#       contact.update(changes.model_dump(exclude_unset=True))
#       return contact
#
# EXERCISE 4
#   @app.get("/contacts", response_model=list[ContactOut])
#   def list_contacts(
#       q: str | None = None,
#       favourite: bool | None = None,
#       skip: Annotated[int, Query(ge=0)] = 0,
#       limit: Annotated[int, Query(ge=1, le=100)] = 20,
#   ):
#       results = list(contacts_db.values())
#       if q is not None:
#           results = [c for c in results if q.lower() in c["name"].lower()]
#       if favourite is not None:
#           results = [c for c in results if c["favourite"] == favourite]
#       return results[skip:skip + limit]
#
#   Note /contacts and /contacts/{contact_id} don't clash - different
#   numbers of path segments (lesson 04 exercise 5).
#
# EXERCISE 6
#   @app.delete("/contacts/{contact_id}", status_code=204)
#   def delete_contact(contact_id: int):
#       get_contact_or_404(contact_id)
#       contacts_db.pop(contact_id)
#
# STRETCH
#   Copy TaskUpdate's model_validator into ContactUpdate with ["name",
#   "email", "favourite"]. In update_contact, if "email" is in the updates,
#   lowercase it and run the same duplicate loop - skipping the contact
#   being edited, like ensure_unique_title's ignore_id.


if __name__ == "__main__":
    start(app, tour, checks, raise_server_exceptions=False)


print("\nNext: python 07_routers_and_dependencies.py")

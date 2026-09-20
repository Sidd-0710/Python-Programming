"""
===============================================================================
 FASTAPI COURSE - LESSON 11: THE CAPSTONE - A REAL, MULTI-FILE BACKEND
===============================================================================

Time: about 3 hours - 45 minutes to explore, the rest building real features.
Assumes: lessons 00-10.

FOUR WAYS TO USE IT:

    python 11_capstone_project.py            the TOUR (start here)
    python 11_capstone_project.py --serve    run the project at /docs, saving
                                             data to capstone/capstone.db
    python 11_capstone_project.py --check    grades your features and runs
                                             the project's test suite
    cd capstone   then   pytest              the tests, run the way every real
                                             project runs them

This file is only a GUIDE. The project itself lives in the capstone/ folder,
and that's where you'll write code for the exercises.


-------------------------------------------------------------------------------
 BEFORE YOU START - THE LESSON IN 30 SECONDS
-------------------------------------------------------------------------------

IN THIS LESSON YOU WILL:
  1. see how a real project is split into files, and why
  2. follow ONE request through nine of those files
  3. run the project for real, and run its test suite
  4. add three features to it yourself, plus tests - like a first week at work

HOW TO WORK THROUGH IT:
  * Run the tour first: it prints the file map and walks the whole API.
  * Then OPEN capstone/ in your editor and read the files in the order of
    the map below. Every idea in them came from lessons 03-10.
  * The exercises are written in the capstone/ files, not in this one.

NEW WORDS - come back here whenever you forget one:

  package        a folder of Python files that can be imported as one unit.
                 The empty __init__.py file is what marks it as a package.
  module         one .py file inside it
  import         the line that brings code from one file into another
  circular       two files each importing the other, so neither can finish
  import         loading. The layered list below is how projects avoid it.
  entry point    the one line that starts everything:
                 uvicorn app.main:app  = package `app`, file `main.py`,
                 variable `app` inside it
  conftest.py    a file of fixtures pytest loads automatically for the tests
                 beside it
  factory        a fixture that MAKES things on demand: make_user(),
  fixture        make_project() - so each test builds just what it needs
  many-to-many   a link table joining two tables both ways. Here,
                 ProjectMember joins users and projects - and carries a role.
  generic model  a response shape with a hole in it: Page[TaskOut] means
                 "a page whose items are TaskOut"
  health check   GET /health - what a load balancer calls to ask "alive?"
  environment    settings that change between your laptop and production,
  variable       read from the environment instead of edited in the code
  Docker         a way to package the app so it runs the same anywhere
  CI             a robot that runs your tests on every push


-------------------------------------------------------------------------------
 THEORY: FROM ONE FILE TO A PROJECT
-------------------------------------------------------------------------------

Every lesson so far fit in one file. Real backends don't, for good reasons:

  * you find code by WHERE it lives, not by scrolling 3,000 lines
  * a change to login can't accidentally break tasks
  * several people can work at once without editing the same file
  * the tests are organised the same way the code is

capstone/ is laid out the way most FastAPI projects are:

    capstone/
      app/                   the application - a Python PACKAGE
        __init__.py          empty: it marks app/ as a package, so
                             `from app.models import Task` works
        main.py              creates the app: middleware, errors, routers
        config.py            settings, read from environment variables
        database.py          engine, Base, get_db
        models.py            the database tables
        schemas.py           Pydantic request and response shapes
        security.py          password hashing and tokens
        dependencies.py      who is asking, and what they may touch
        routers/             auth.py  users.py  projects.py  tasks.py
      tests/
        conftest.py          shared fixtures - pytest loads it automatically
        test_auth.py  test_projects.py  test_tasks.py
      pytest.ini  requirements.txt  requirements-dev.txt  Dockerfile  README.md


IMPORTS FLOW IN ONE DIRECTION
-----------------------------
    main.py            imports  routers, config, database, models
    routers/*.py       import   dependencies, schemas, models, security, config
    dependencies.py    imports  database, models, security
    security.py        imports  config
    models.py          imports  database
    database.py        imports  config
    schemas.py         imports  nothing from the app
    config.py          imports  nothing from the app

Lower files never import higher ones: models.py never imports a router, and
nothing imports main.py except the tests. Break that rule and Python reports
"ImportError: cannot import name ... (most likely due to a circular import)":
two files, each waiting for the other to finish loading first.

`uvicorn app.main:app` reads as: the package `app`, its module `main`, and the
variable called `app` inside it.


WHAT THE PROJECT DOES
---------------------
A team task tracker - a tiny Trello or Jira:
  * people register and log in                                    (lesson 09)
  * anyone can create a PROJECT, and becomes its OWNER
  * the owner adds other users as MEMBERS
  * members create, assign, filter and update TASKS in the project
  * outsiders get 404; members trying owner-only actions get 403  (lesson 09)


WHAT'S NEW, COMPARED WITH LESSONS 03-10
---------------------------------------
  * settings from environment variables - and refusing to start in
    production without a SECRET_KEY                               config.py
  * a many-to-many relationship that carries extra data (a role)  models.py
  * a generic response model: Page[TaskOut]                       schemas.py
  * a base class that guards every PATCH against nulls            schemas.py
  * logging, a catch-all error handler, a health check            main.py
  * factory fixtures: make_user(), make_project(), make_task()    tests/conftest.py
"""

import os
import subprocess
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_DIR = HERE / "capstone"

# The project reads its settings the moment app.config is imported, so the
# environment must be ready BEFORE the import below. --serve keeps data in a
# file; the tour and the grader use a fresh in-memory database every run.
if "--serve" in sys.argv:
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{PROJECT_DIR / 'capstone.db'}")
else:
    os.environ["DATABASE_URL"] = "sqlite://"
    os.environ["ENVIRONMENT"] = "test"
    os.environ.setdefault("LOG_LEVEL", "WARNING")

# Make `import app` find capstone/app - the same thing pytest.ini's
# `pythonpath = .` does for the tests.
sys.path.insert(0, str(PROJECT_DIR))

from course_tools import check, section, show, start  # noqa: E402

try:
    from app.main import app  # noqa: E402
except Exception:
    traceback.print_exc()
    print("\n  The capstone app failed to load. The last lines above name the file")
    print("  and line with the problem - often a typo or a missing import in new code.")
    sys.exit(1)


PASSWORD = "password-123"

PROJECT_MAP = [
    ("README.md", "install, run, test and deploy - start here on a real job"),
    ("requirements.txt", "packages the app needs to run"),
    ("requirements-dev.txt", "plus the packages for development: pytest"),
    ("pytest.ini", "tells pytest where tests live and how to import app"),
    ("Dockerfile", "packages the app as a container for deployment"),
    (".gitignore", "files git should never commit: databases, caches"),
    ("app/__init__.py", "empty - marks app/ as a package"),
    ("app/main.py", "creates the app: CORS, logging, errors, routers"),
    ("app/config.py", "settings from environment variables"),
    ("app/database.py", "engine, Base, get_db"),
    ("app/models.py", "tables: User, Project, ProjectMember, Task"),
    ("app/schemas.py", "Pydantic shapes, Page[...], PartialUpdate"),
    ("app/security.py", "password hashing, JWT tokens"),
    ("app/dependencies.py", "CurrentUser, Membership, OwnerMembership, ..."),
    ("app/routers/__init__.py", "empty - marks routers/ as a package"),
    ("app/routers/auth.py", "POST /auth/register, POST /auth/token"),
    ("app/routers/users.py", "GET and PATCH /users/me"),
    ("app/routers/projects.py", "projects and their members"),
    ("app/routers/tasks.py", "tasks: create, filter, sort, page, update"),
    ("tests/conftest.py", "fixtures: client, make_user, make_project, make_task"),
    ("tests/test_auth.py", "registration, login, /users/me"),
    ("tests/test_projects.py", "ownership, membership, access rules"),
    ("tests/test_tasks.py", "filters, sorting, permissions"),
]

REQUEST_FLOW = """\
  POST /projects/1/tasks
  Authorization: Bearer eyJhbGciOi...
  {"title": "Write the homepage copy", "assignee_id": 2}

   1. app/main.py            log_requests middleware: request id, start the timer
   2. app/routers/tasks.py   FastAPI matches the route: create_task(...)
   3. app/dependencies.py    create_task asks for Membership, which asks for
                             CurrentUser, which asks for the token and a DbSession
   4. app/security.py        decode_access_token checks the signature -> user 1
   5. app/database.py        get_db opens the ONE session all of them share
   6. app/models.py          a ProjectMember row proves user 1 is in project 1
   7. app/schemas.py         the JSON body is validated as a TaskCreate
   8. app/routers/tasks.py   the assignee is checked, and a Task is saved
   9. app/schemas.py         the saved Task goes back out through TaskOut
  10. app/main.py            middleware adds X-Request-Id and X-Process-Time,
                             and logs one line about the request

  Nine files, one request - and each file did exactly one job."""

RUN_FOR_REAL = """\
  THE EASY WAY - through this guide:
      python 11_capstone_project.py --serve

  THE REAL WAY - how you'd start any FastAPI project on a job:
      cd capstone
      source ../.venv/bin/activate
      export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
      uvicorn app.main:app --reload

  --reload restarts the server every time you save a file (development only).
  Try leaving SECRET_KEY unset and restarting: every login stops working,
  because a new random key signs the tokens. That's why production requires it:

      ENVIRONMENT=production uvicorn app.main:app
      -> RuntimeError: SECRET_KEY must be set when ENVIRONMENT=production

  capstone/README.md covers configuration, Docker and deployment."""

ROADMAP = """\
  You can now build, secure, test and structure a real FastAPI backend.
  In the order I'd learn them next:

   1. PostgreSQL + Alembic    the production database, and migrations to
                              change tables without losing data
   2. Docker                  capstone/Dockerfile is a starting point
   3. Deploy it               Render, Railway or Fly.io - secrets as env vars
   4. CI                      run pytest on every push with GitHub Actions
   5. Async database access   async SQLAlchemy, once you're comfortable
   6. Background jobs, Redis  sending emails, caching, rate limiting
   7. Refresh tokens, OAuth   "stay logged in" and "Sign in with Google"

  The best next step of all: add the exercises below, then build your OWN
  project in this same shape, from an empty folder."""


def indent(text: str, spaces: int = 4) -> str:
    return "\n".join(" " * spaces + line for line in text.rstrip().splitlines())


def print_project_map():
    described = dict(PROJECT_MAP)
    ignored = {"__pycache__", ".pytest_cache"}
    on_disk = sorted(
        path.relative_to(PROJECT_DIR).as_posix()
        for path in PROJECT_DIR.rglob("*")
        if path.is_file() and not ignored.intersection(path.parts) and path.suffix != ".db"
    )
    ordered = ([name for name, _ in PROJECT_MAP if name in on_disk]
               + [name for name in on_disk if name not in described])
    total = 0
    for name in ordered:
        lines = len((PROJECT_DIR / name).read_text().splitlines())
        total += lines
        print(f"    {name:<26} {lines:>4}   {described.get(name, 'NEW - a file you added')}")
    print(f"\n    {len(ordered)} files, {total} lines - and every idea in them is from lessons 03-10.")


def run_project_pytest(*arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *arguments],
                          cwd=PROJECT_DIR, capture_output=True, text=True)


# ---- Small helpers for the tour and the grader ------------------------------

def api_user(client, email: str, full_name: str | None = None) -> dict:
    client.post("/auth/register", json={"email": email, "password": PASSWORD,
                                        "full_name": full_name})
    token = client.post("/auth/token", data={"username": email,
                                             "password": PASSWORD}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return {"id": client.get("/users/me", headers=headers).json()["id"],
            "email": email, "headers": headers}


def api_project(client, owner: dict, name: str, members: list[dict] = ()) -> int:
    project_id = client.post("/projects", json={"name": name},
                             headers=owner["headers"]).json()["id"]
    for member in members:
        client.post(f"/projects/{project_id}/members", json={"email": member["email"]},
                    headers=owner["headers"])
    return project_id


def api_task(client, user: dict, project_id: int, **fields) -> dict:
    return client.post(f"/projects/{project_id}/tasks", json={"title": "A task", **fields},
                       headers=user["headers"]).json()


def is_app_404(response) -> bool:
    """A 404 from the app's own code - not FastAPI's "no such route" 404."""
    return response.status_code == 404 and response.json().get("detail") != "Not Found"


# =============================================================================
# THE TOUR — runs when you execute this file with no flags
# =============================================================================

def tour(client):
    section("THE PROJECT, FILE BY FILE  (capstone/)")
    print_project_map()

    section("ONE REQUEST, THROUGH EVERY FILE")
    print(REQUEST_FLOW)

    section("ACCOUNTS  -  routers/auth.py, routers/users.py, security.py")
    show(client, "GET", "/health", note="what a load balancer checks: app AND database up?")
    show(client, "POST", "/auth/register",
         json={"email": "sidd@example.com", "password": PASSWORD, "full_name": "Sidd"})
    response = show(client, "POST", "/auth/token",
                    data={"username": "sidd@example.com", "password": PASSWORD})
    sidd_headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    sidd = {"id": 1, "email": "sidd@example.com", "headers": sidd_headers}
    ana = api_user(client, "ana@example.com", "Ana")
    tom = api_user(client, "tom@example.com", "Tom")
    print("\n  (ana@example.com and tom@example.com signed up the same way, off-screen.)")

    section("PROJECTS AND MEMBERS  -  routers/projects.py, dependencies.py")
    response = show(client, "POST", "/projects", note="whoever creates it becomes the owner",
                    headers=sidd_headers,
                    json={"name": "Website relaunch", "description": "New site by October"})
    project_id = response.json()["id"]
    show(client, "POST", f"/projects/{project_id}/members", note="the owner adds Ana",
         headers=sidd_headers, json={"email": "ana@example.com"})
    show(client, "POST", f"/projects/{project_id}/members", note="adding her again",
         headers=sidd_headers, json={"email": "ana@example.com"})
    show(client, "GET", f"/projects/{project_id}",
         note="Tom isn't a member - as far as he can tell, it doesn't exist",
         headers=tom["headers"])
    show(client, "PATCH", f"/projects/{project_id}",
         note="Ana is a member, but renaming needs the owner",
         headers=ana["headers"], json={"name": "Ana's project now"})

    section("TASKS  -  routers/tasks.py")
    response = show(client, "POST", f"/projects/{project_id}/tasks",
                    note="Sidd creates a task and assigns it to Ana", headers=sidd_headers,
                    json={"title": "Write the homepage copy", "priority": "high",
                          "due_date": "2026-10-01", "assignee_id": ana["id"]})
    homepage_id = response.json()["id"]
    show(client, "POST", f"/projects/{project_id}/tasks",
         note="assigning to Tom, who isn't in the project", headers=sidd_headers,
         json={"title": "Secret task", "assignee_id": tom["id"]})
    for title, priority, due_date in [("Pick a font", "low", None),
                                      ("Fix the signup bug", "high", "2020-01-15"),
                                      ("Book the photographer", "medium", "2026-09-30")]:
        api_task(client, sidd, project_id, title=title, priority=priority, due_date=due_date)
    print("\n  (Three more tasks created off-screen.)")
    show(client, "GET", f"/projects/{project_id}/tasks?overdue=true",
         note="past their due date and not done - a Page[TaskOut]", headers=ana["headers"])
    show(client, "PATCH", f"/tasks/{homepage_id}", note="Ana moves her task along",
         headers=ana["headers"], json={"status": "in_progress"})
    show(client, "DELETE", f"/tasks/{homepage_id}",
         note="Ana didn't create it and isn't the owner", headers=ana["headers"])

    section("NOT BUILT YET - THESE ARE YOUR EXERCISES")
    show(client, "GET", f"/projects/{project_id}/stats", headers=sidd_headers,
         note="exercise 2 - no such route yet, so FastAPI's own 404")
    show(client, "GET", f"/tasks/{homepage_id}/comments", headers=ana["headers"],
         note="exercise 1")

    section("THE PROJECT'S OWN TEST SUITE")
    print("  $ cd capstone && pytest -v\n")
    result = run_project_pytest("-v", "--no-header")
    print(indent(result.stdout))

    section("RUNNING IT FOR REAL")
    print(RUN_FOR_REAL)

    section("WHERE TO GO FROM HERE")
    print(ROADMAP)


# =============================================================================
# RECAP - WHAT THE PROJECT SHOWS YOU
# =============================================================================
#
#   * One job per file: config, database, models, schemas, security,
#     dependencies, routers. You find code by where it lives.
#   * Imports flow one way only - main imports routers, routers import
#     dependencies, and nothing lower ever imports something higher. That's
#     what prevents circular imports.
#   * Settings come from the environment, so the same code runs on your
#     laptop, in the tests and in production - and production REFUSES to
#     start without a SECRET_KEY.
#   * Access rules live in dependencies, so no route can forget them:
#     outsiders get 404, members who need the owner get 403.
#   * The tests mirror the code, share fixtures through conftest.py, and use
#     factory fixtures to build exactly what each test needs.
#
# QUICK SELF-CHECK - answer in your head first, then read the answers below.
#
#   Q1. What does `uvicorn app.main:app` actually name?
#   Q2. Why does models.py never import a router?
#   Q3. Where would you add a rule that applies to EVERY request?
#   Q4. A stranger asks for a project they're not a member of. 403 or 404?
#   Q5. Why is SECRET_KEY read from the environment instead of the code?
#
# ANSWERS
#   A1. The package `app`, the module `main.py` inside it, and the variable
#       `app` inside that.
#   A2. Imports flow one way. If models imported a router, and that router
#       imported models, Python could not finish loading either - a circular
#       import.
#   A3. Middleware in app/main.py (lesson 07 PART 7).
#   A4. 404 - a 403 would confirm the project exists.
#   A5. So it never lands in git, and so each environment can have its own.


# =============================================================================
# EXERCISES — BUILD FEATURES INTO THE REAL PROJECT
# =============================================================================
#
# Work in the capstone/ files, the way you would on a job. After each change:
#     python 11_capstone_project.py --check
# and from inside capstone/, run the tests the normal way:
#     pytest
#
# Do the WARM-UPS first - they're tiny, and they prove you can find your way
# around the project and run its tests.
#
# WARM-UP 1 (easy) — Add a route to an existing file
#   In app/main.py, next to the health check, add GET /version returning
#   {"name": settings.app_name, "version": "1.0.0"}. settings is already
#   imported in that file.
#
# WARM-UP 2 (easy) — Add a test file
#   Create capstone/tests/test_warmup.py with one test that asks for the
#   `client` fixture, calls GET /health, and asserts the status code is 200.
#   Run it with:  cd capstone && pytest tests/test_warmup.py -v
#
# EXERCISE 1 (challenge) — Comments on tasks   (4 files)
#   app/models.py
#       A Comment model, table "comments": id, task_id (foreign key tasks.id),
#       author_id (foreign key users.id), body (Text), created_at (default
#       utc_now). Also give Task this line, so deleting a task deletes its
#       comments instead of hitting a foreign key error:
#           comments: Mapped[list["Comment"]] = relationship(cascade="all, delete-orphan")
#   app/schemas.py
#       CommentCreate: body, 1 to 2000 characters.
#       CommentOut: id, task_id, author_id, body, created_at.
#   app/routers/comments.py   - a NEW file with its own router:
#       POST /tasks/{task_id}/comments -> 201. The author is the logged-in user.
#       GET  /tasks/{task_id}/comments -> a list, oldest first.
#       Only members of the task's project may use either. Everyone else gets
#       404. (A dependency in dependencies.py already does exactly that.)
#   app/main.py
#       Import the new router and include it.
#
# EXERCISE 2 (challenge) — Project stats   (app/schemas.py, app/routers/projects.py)
#   GET /projects/{project_id}/stats, members only:
#       {"total": 4, "by_status": {"todo": 2, "in_progress": 1, "done": 1}, "overdue": 1}
#   by_status always has all three keys, even when a count is 0. A task is
#   overdue when its due_date is before today AND it isn't done. Let the
#   database do the counting (func.count and group_by, lesson 08 PART 7).
#
# EXERCISE 3 (challenge) — "My tasks"   (app/routers/users.py)
#   GET /users/me/tasks -> a list of TaskOut: the tasks ASSIGNED to the
#   logged-in user that aren't done, in projects they're a member of.
#   Soonest due_date first; tasks without a due date last.
#
# EXERCISE 4 (medium) — Test your feature   (a new file: tests/test_comments.py)
#   Write at least 3 tests for exercise 1, using the fixtures in
#   tests/conftest.py. Include at least one error case. The grader runs the
#   WHOLE suite, so your tests and all the existing ones must pass.


def check_comments(client, owner, member, outsider):
    project_id = api_project(client, owner, "Comments check", [member])
    task = api_task(client, owner, project_id, title="Discuss me")
    url = f"/tasks/{task.get('id')}/comments"

    response = client.post(url, json={"body": "On it"}, headers=member["headers"])
    comment = response.json() if response.status_code == 201 else {}
    check("EXERCISE 1: a project member can comment (201)", response.status_code == 201)
    check("EXERCISE 1: the comment has id, task_id, author_id, body and created_at",
          {"id", "created_at"} <= comment.keys()
          and comment.get("task_id") == task.get("id")
          and comment.get("author_id") == member["id"]
          and comment.get("body") == "On it")

    client.post(url, json={"body": "Thanks!"}, headers=owner["headers"])
    response = client.get(url, headers=owner["headers"])
    comments = response.json() if response.status_code == 200 else None
    check("EXERCISE 1: GET lists the comments, oldest first",
          isinstance(comments, list) and [c.get("body") for c in comments] == ["On it", "Thanks!"])
    check("EXERCISE 1: an outsider can't add a comment (404)",
          is_app_404(client.post(url, json={"body": "hi"}, headers=outsider["headers"])))
    check("EXERCISE 1: an outsider can't read the comments (404)",
          is_app_404(client.get(url, headers=outsider["headers"])))
    check("EXERCISE 1: no token gives 401",
          client.post(url, json={"body": "hi"}).status_code == 401)
    check("EXERCISE 1: an empty comment gives 422",
          client.post(url, json={"body": ""}, headers=member["headers"]).status_code == 422)
    check("EXERCISE 1: a task that doesn't exist gives 404",
          is_app_404(client.post("/tasks/999999/comments", json={"body": "hi"},
                                 headers=member["headers"])))


def check_stats(client, owner, member, outsider):
    project_id = api_project(client, owner, "Stats check", [member])
    api_task(client, owner, project_id, title="Old todo", due_date="2020-01-01")
    api_task(client, owner, project_id, title="New todo")
    doing = api_task(client, owner, project_id, title="Doing")
    client.patch(f"/tasks/{doing['id']}", json={"status": "in_progress"}, headers=owner["headers"])
    done = api_task(client, owner, project_id, title="Done late", due_date="2020-01-01")
    client.patch(f"/tasks/{done['id']}", json={"status": "done"}, headers=owner["headers"])

    response = client.get(f"/projects/{project_id}/stats", headers=member["headers"])
    check("EXERCISE 2: a member gets correct stats (2 todo, 1 in progress, 1 done, 1 overdue)",
          response.status_code == 200 and response.json() == {
              "total": 4, "by_status": {"todo": 2, "in_progress": 1, "done": 1}, "overdue": 1})

    empty_id = api_project(client, owner, "Empty project")
    response = client.get(f"/projects/{empty_id}/stats", headers=owner["headers"])
    check("EXERCISE 2: a project with no tasks shows every count as 0",
          response.status_code == 200 and response.json() == {
              "total": 0, "by_status": {"todo": 0, "in_progress": 0, "done": 0}, "overdue": 0})
    check("EXERCISE 2: an outsider gets 404",
          is_app_404(client.get(f"/projects/{project_id}/stats", headers=outsider["headers"])))


def check_my_tasks(client, owner, member, outsider):
    first = api_project(client, owner, "My tasks 1", [member])
    second = api_project(client, outsider, "My tasks 2", [member])
    api_task(client, owner, first, title="Due later", assignee_id=member["id"],
             due_date="2030-10-01")
    api_task(client, outsider, second, title="Due soon", assignee_id=member["id"],
             due_date="2030-09-20")
    api_task(client, owner, first, title="No due date", assignee_id=member["id"])
    finished = api_task(client, owner, first, title="Finished", assignee_id=member["id"])
    client.patch(f"/tasks/{finished['id']}", json={"status": "done"}, headers=owner["headers"])
    api_task(client, owner, first, title="Nobody's")

    response = client.get("/users/me/tasks", headers=member["headers"])
    tasks = response.json() if response.status_code == 200 else None
    check("EXERCISE 3: open assigned tasks from every project, soonest first, undated last",
          isinstance(tasks, list)
          and [t.get("title") for t in tasks] == ["Due soon", "Due later", "No due date"])
    response = client.get("/users/me/tasks", headers=owner["headers"])
    check("EXERCISE 3: someone with nothing assigned gets an empty list",
          response.status_code == 200 and response.json() == [])
    check("EXERCISE 3: no token gives 401", client.get("/users/me/tasks").status_code == 401)


def checks(client):
    suite = run_project_pytest("-q")
    check("the project's test suite passes (the original tests, plus any you added)",
          suite.returncode == 0)
    if suite.returncode != 0:
        print(indent("\n".join(suite.stdout.splitlines()[-15:]), 9))

    # --- WARM-UPS ---
    response = client.get("/version")
    body = response.json() if response.status_code == 200 else {}
    check("WARM-UP 1: GET /version returns the app name and version",
          response.status_code == 200 and body.get("version") == "1.0.0"
          and body.get("name") == "Task Tracker API")

    collected = run_project_pytest("--collect-only", "-q", "tests/test_warmup.py")
    warm_up_count = sum("::" in line for line in collected.stdout.splitlines())
    check(f"WARM-UP 2: tests/test_warmup.py has at least 1 test (found {warm_up_count})",
          warm_up_count >= 1)

    people = [api_user(client, f"{name}@grader.example") for name in ["owner", "member", "outsider"]]
    for group in [check_comments, check_stats, check_my_tasks]:
        try:
            group(client, *people)
        except Exception as error:
            check(f"{group.__name__} crashed: {type(error).__name__}: {error}", False)

    collected = run_project_pytest("--collect-only", "-q", "tests/test_comments.py")
    test_count = sum("::" in line for line in collected.stdout.splitlines())
    check(f"EXERCISE 4: tests/test_comments.py has at least 3 tests (found {test_count})",
          test_count >= 3)


# =============================================================================
# SOLUTIONS
# =============================================================================
#
# WARM-UP 1
#   ---- app/main.py: next to the health check ----
#   @app.get("/version", tags=["health"])
#   def version():
#       return {"name": settings.app_name, "version": "1.0.0"}
#
# WARM-UP 2
#   ---- capstone/tests/test_warmup.py (new file) ----
#   def test_health_check_says_the_app_is_ok(client):
#       response = client.get("/health")
#       assert response.status_code == 200
#
#   Asking for `client` is what gives the test its own empty database -
#   conftest.py builds it. You never import anything to get a fixture.
#
# EXERCISE 1
#   ---- app/models.py: add to the Task class ----
#       comments: Mapped[list["Comment"]] = relationship(cascade="all, delete-orphan")
#
#   ---- app/models.py: a new class at the bottom ----
#   class Comment(Base):
#       __tablename__ = "comments"
#
#       id: Mapped[int] = mapped_column(primary_key=True)
#       task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True)
#       author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
#       body: Mapped[str] = mapped_column(Text)
#       created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
#
#   ---- app/schemas.py ----
#   class CommentCreate(BaseModel):
#       body: str = Field(min_length=1, max_length=2000)
#
#   class CommentOut(ORMModel):
#       id: int
#       task_id: int
#       author_id: int
#       body: str
#       created_at: datetime
#
#   ---- app/routers/comments.py (new file) ----
#   from fastapi import APIRouter, status
#   from sqlalchemy import select
#
#   from app.dependencies import CurrentUser, DbSession, MemberTask
#   from app.models import Comment
#   from app.schemas import CommentCreate, CommentOut
#
#   router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["comments"])
#
#   @router.post("", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
#   def add_comment(data: CommentCreate, task: MemberTask, user: CurrentUser, db: DbSession):
#       comment = Comment(task_id=task.id, author_id=user.id, body=data.body)
#       db.add(comment)
#       db.commit()
#       db.refresh(comment)
#       return comment
#
#   @router.get("", response_model=list[CommentOut])
#   def list_comments(task: MemberTask, db: DbSession):
#       statement = select(Comment).where(Comment.task_id == task.id).order_by(Comment.id)
#       return db.scalars(statement).all()
#
#   ---- app/main.py ----
#   from app.routers import auth, comments, projects, tasks, users
#   ...
#   app.include_router(comments.router)
#
#   A router prefix can contain a path parameter. MemberTask reads {task_id}
#   from it and does the whole "members only, 404 otherwise" rule - the new
#   routes contain no access checks of their own.
#
# EXERCISE 2
#   ---- app/schemas.py ----
#   class ProjectStats(BaseModel):
#       total: int
#       by_status: dict[str, int]
#       overdue: int
#
#   ---- app/routers/projects.py: new imports ----
#   from datetime import date
#   from sqlalchemy import func, select
#   (and add ProjectStats to the `from app.schemas import (...)` list)
#
#   ---- app/routers/projects.py: new route ----
#   @router.get("/{project_id}/stats", response_model=ProjectStats)
#   def project_stats(membership: Membership, db: DbSession):
#       rows = db.execute(
#           select(Task.status, func.count(Task.id))
#           .where(Task.project_id == membership.project_id)
#           .group_by(Task.status)
#       ).all()
#       counts = dict(rows)                  # [("todo", 2), ("done", 1)] -> {"todo": 2, "done": 1}
#       by_status = {name: counts.get(name, 0) for name in ["todo", "in_progress", "done"]}
#       overdue = db.scalar(
#           select(func.count(Task.id)).where(
#               Task.project_id == membership.project_id,
#               Task.status != "done",
#               Task.due_date < date.today(),
#           )
#       )
#       return {"total": sum(by_status.values()), "by_status": by_status, "overdue": overdue}
#
# EXERCISE 3
#   ---- app/routers/users.py: new imports ----
#   from sqlalchemy import and_, select
#   from app.models import ProjectMember, Task
#   (and add TaskOut to the `from app.schemas import ...` line)
#
#   ---- app/routers/users.py: new route ----
#   @router.get("/me/tasks", response_model=list[TaskOut])
#   def my_open_tasks(user: CurrentUser, db: DbSession):
#       statement = (
#           select(Task)
#           .join(ProjectMember, and_(ProjectMember.project_id == Task.project_id,
#                                     ProjectMember.user_id == user.id))
#           .where(Task.assignee_id == user.id, Task.status != "done")
#           .order_by(Task.due_date.asc().nulls_last(), Task.id)
#       )
#       return db.scalars(statement).all()
#
#   The join keeps only rows where the user has a membership in the task's
#   project. (Removing a member already unassigns their tasks, so it's a
#   second line of defence - cheap, and it keeps the rule true if that ever
#   changes.)
#
# EXERCISE 4
#   ---- tests/test_comments.py ----
#   def test_members_can_comment_on_a_task(client, make_user, make_project, make_task):
#       owner, member = make_user(), make_user()
#       task = make_task(owner, make_project(owner, members=[member]))
#
#       response = client.post(f"/tasks/{task['id']}/comments", json={"body": "On it"},
#                              headers=member["headers"])
#
#       assert response.status_code == 201
#       assert response.json()["author_id"] == member["id"]
#       assert response.json()["body"] == "On it"
#
#   def test_comments_are_listed_oldest_first(client, make_user, make_project, make_task):
#       owner = make_user()
#       task = make_task(owner, make_project(owner))
#       for body in ["first", "second"]:
#           client.post(f"/tasks/{task['id']}/comments", json={"body": body},
#                       headers=owner["headers"])
#
#       response = client.get(f"/tasks/{task['id']}/comments", headers=owner["headers"])
#
#       assert [c["body"] for c in response.json()] == ["first", "second"]
#
#   def test_outsiders_cannot_comment(client, make_user, make_project, make_task):
#       owner, outsider = make_user(), make_user()
#       task = make_task(owner, make_project(owner))
#
#       response = client.post(f"/tasks/{task['id']}/comments", json={"body": "hi"},
#                              headers=outsider["headers"])
#
#       assert response.status_code == 404
#
#   def test_an_empty_comment_is_rejected(client, make_user, make_project, make_task):
#       owner = make_user()
#       task = make_task(owner, make_project(owner))
#
#       response = client.post(f"/tasks/{task['id']}/comments", json={"body": ""},
#                              headers=owner["headers"])
#
#       assert response.status_code == 422


if __name__ == "__main__":
    start(app, tour, checks)
    print("\n  That's the course. Well done.")

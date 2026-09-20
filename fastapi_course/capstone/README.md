# Task Tracker API

A team task tracker built with FastAPI, SQLAlchemy and JWT authentication:
people register, create projects, invite members, and manage tasks together.

It's the capstone of the FastAPI course (lesson 11). It's laid out the way a
production FastAPI project usually is.

## Features

- Registration and login with hashed passwords and expiring JWT access tokens
- Projects with an owner and members (a many-to-many relationship with roles)
- Tasks with status, priority, assignee and due date
- Filtering, search, sorting and pagination on task lists
- Access rules enforced in one place (`app/dependencies.py`)
- Settings from environment variables, request logging, a health check
- A pytest suite that gives every test its own fresh database

## Layout

```
app/
  main.py            creates the app: middleware, error handler, routers
  config.py          settings from environment variables
  database.py        engine, Base, get_db (one session per request)
  models.py          SQLAlchemy tables
  schemas.py         Pydantic request and response models
  security.py        password hashing and JWT tokens
  dependencies.py    current user, project membership, pagination
  routers/           auth, users, projects, tasks
tests/
  conftest.py        fixtures: client, make_user, make_project, make_task
  test_*.py
```

## Run it locally

From the `capstone/` folder, with the course's virtual environment active:

```bash
pip install -r requirements-dev.txt
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs, register a user with `POST /auth/register`,
then click **Authorize** and log in with your email as the username.

## Configuration

| Variable               | Default                   | Notes                                     |
|------------------------|---------------------------|-------------------------------------------|
| `SECRET_KEY`           | random on every start     | **Required** when `ENVIRONMENT=production` |
| `DATABASE_URL`         | `sqlite:///./capstone.db` | e.g. `postgresql+psycopg://user:pass@host/db` |
| `ENVIRONMENT`          | `development`             | `development`, `test` or `production`     |
| `ACCESS_TOKEN_MINUTES` | `30`                      | How long a login lasts                    |
| `CORS_ORIGINS`         | `http://localhost:5173`   | Comma-separated frontend origins          |
| `LOG_LEVEL`            | `INFO`                    | `DEBUG`, `INFO`, `WARNING` or `ERROR`     |

## Tests

```bash
pytest            # the whole suite
pytest -v         # one line per test
pytest -k tasks   # only tests with "tasks" in their name
```

Tests use an in-memory database and never touch `capstone.db`.

## API at a glance

| Method | Path                                     | Who can call it                    |
|--------|------------------------------------------|------------------------------------|
| POST   | `/auth/register`                         | anyone                             |
| POST   | `/auth/token`                            | anyone (form data)                 |
| GET    | `/users/me`                              | logged in                          |
| PATCH  | `/users/me`                              | logged in                          |
| POST   | `/projects`                              | logged in (becomes the owner)      |
| GET    | `/projects`                              | logged in (their projects only)    |
| GET    | `/projects/{id}`                         | members                            |
| PATCH  | `/projects/{id}`                         | owner                              |
| DELETE | `/projects/{id}`                         | owner                              |
| POST   | `/projects/{id}/members`                 | owner                              |
| DELETE | `/projects/{id}/members/{user_id}`       | owner                              |
| POST   | `/projects/{id}/tasks`                   | members                            |
| GET    | `/projects/{id}/tasks`                   | members                            |
| GET    | `/tasks/{id}`                            | members                            |
| PATCH  | `/tasks/{id}`                            | members                            |
| DELETE | `/tasks/{id}`                            | owner, or the task's creator       |
| GET    | `/health`                                | anyone                             |

Outsiders get `404` for projects and tasks they can't access, so they can't
tell whether a project exists. Members who try an owner-only action get `403`.

## Deploying

```bash
docker build -t task-tracker .
docker run -p 8000:8000 \
  -e SECRET_KEY="..." \
  -e DATABASE_URL="postgresql+psycopg://user:pass@db-host:5432/tasks" \
  task-tracker
```

Before real users arrive:

- Use PostgreSQL, not SQLite. Add `psycopg[binary]` to `requirements.txt`. An
  SQLite file inside a container is lost whenever the container is replaced.
- Manage tables with Alembic migrations instead of `create_all` at startup.
- Serve over HTTPS. Most hosting platforms handle this for you.
- Set `CORS_ORIGINS` to your real frontend's address.

"""Fixtures shared by every test file. pytest loads conftest.py automatically."""

import os

# Settings are read the moment the app is imported, so set the environment
# FIRST: an in-memory database, so tests can never touch capstone.db.
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "WARNING")

from itertools import count  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import Base, get_db, make_engine  # noqa: E402
from app.main import app  # noqa: E402

PASSWORD = "password-123"


@pytest.fixture
def client():
    """A TestClient talking to the app, backed by a brand-new empty database."""
    engine = make_engine("sqlite://")
    Base.metadata.create_all(engine)

    def get_test_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)
    engine.dispose()


# FACTORY FIXTURES: instead of giving a test ONE user, give it a FUNCTION that
# makes users - so each test creates exactly what it needs, in one line:
#     owner, member = make_user(), make_user()

@pytest.fixture
def make_user(client):
    numbers = count(1)

    def _make_user(email: str | None = None, password: str = PASSWORD) -> dict:
        email = email or f"user{next(numbers)}@example.com"
        registered = client.post("/auth/register", json={"email": email, "password": password})
        # The text after the comma is printed if the assert fails. In setup
        # code like this, it tells you WHY the setup broke, not just that it did.
        assert registered.status_code == 201, registered.text
        login = client.post("/auth/token", data={"username": email, "password": password})
        assert login.status_code == 200, login.text
        return {
            "id": registered.json()["id"],
            "email": email,
            "headers": {"Authorization": f"Bearer {login.json()['access_token']}"},
        }

    return _make_user


@pytest.fixture
def make_project(client):
    def _make_project(owner: dict, name: str = "Website relaunch",
                      members: list[dict] | None = None) -> dict:
        created = client.post("/projects", json={"name": name}, headers=owner["headers"])
        assert created.status_code == 201, created.text
        project = created.json()
        for member in members or []:
            added = client.post(f"/projects/{project['id']}/members",
                                json={"email": member["email"]}, headers=owner["headers"])
            assert added.status_code == 201, added.text
        return project

    return _make_project


@pytest.fixture
def make_task(client):
    def _make_task(user: dict, project: dict, **fields) -> dict:
        body = {"title": "A task", **fields}
        created = client.post(f"/projects/{project['id']}/tasks", json=body,
                              headers=user["headers"])
        assert created.status_code == 201, created.text
        return created.json()

    return _make_task

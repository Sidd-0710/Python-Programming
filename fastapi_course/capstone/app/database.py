"""The database connection: one engine for the app, one session per request."""

from datetime import datetime, timezone

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.pool import StaticPool

from app.config import settings


class Base(DeclarativeBase):
    pass


def make_engine(url: str) -> Engine:
    if not url.startswith("sqlite"):
        # PostgreSQL and friends. pool_pre_ping replaces connections the
        # database server closed while they sat idle.
        return create_engine(url, pool_pre_ping=True)

    options = {"connect_args": {"check_same_thread": False}}
    if url in ("sqlite://", "sqlite:///:memory:"):
        options["poolclass"] = StaticPool      # one shared in-memory database
    engine = create_engine(url, **options)

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()

    return engine


engine = make_engine(settings.database_url)


def get_db():
    with Session(engine) as session:
        yield session


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

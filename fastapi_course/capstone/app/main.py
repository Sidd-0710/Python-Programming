"""The entry point: `uvicorn app.main:app` means "the variable app, in app/main.py"."""

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app import models  # noqa: F401 - importing the models registers their tables on Base
from app.config import settings
from app.database import Base, engine
from app.routers import auth, projects, tasks, users

logging.basicConfig(level=settings.log_level,
                    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s")
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fine for learning and tests. A production project creates and changes its
    # tables with migrations (the Alembic package) instead, so existing data
    # survives when a model changes.
    Base.metadata.create_all(engine)
    logger.info("%s started (environment=%s)", settings.app_name, settings.environment)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan,
              description="Projects, members and tasks - the course capstone.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex[:12]
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-Id"] = request_id
    response.headers["X-Process-Time"] = f"{elapsed_ms:.1f}ms"
    logger.info("%s %s -> %s in %.1fms [%s]", request.method, request.url.path,
                response.status_code, elapsed_ms, request_id)
    return response


# Any exception nobody handled: log everything for us, tell the client nothing.
@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, error: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["health"])
def health():
    # Load balancers call this to decide whether to send traffic here, so it
    # checks the database really answers - not just that Python is running.
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok", "environment": settings.environment}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)

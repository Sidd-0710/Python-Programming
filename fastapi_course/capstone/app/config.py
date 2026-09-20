"""Settings, read from environment variables.

The same code runs on your laptop, in the tests, and in production. What
changes between them - the database, the secret key - comes from the
environment, never from edits to the code:

    DATABASE_URL           where the data lives        default: sqlite:///./capstone.db
    SECRET_KEY             signs login tokens          REQUIRED in production
    ENVIRONMENT            development | test | production
    ACCESS_TOKEN_MINUTES   how long a login lasts      default: 30
    CORS_ORIGINS           comma-separated frontends   default: http://localhost:5173
    LOG_LEVEL              DEBUG | INFO | WARNING      default: INFO

Bigger projects use the pydantic-settings package for this. It does the same
job with less code, and can also read a .env file.
"""

import os
import secrets
from typing import Literal

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "Task Tracker API"
    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite:///./capstone.db"
    secret_key: str = Field(min_length=32)
    access_token_minutes: int = Field(default=30, ge=1)
    cors_origins: list[str] = ["http://localhost:5173"]
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


def load_settings() -> Settings:
    environment = os.environ.get("ENVIRONMENT", "development")

    secret_key = os.environ.get("SECRET_KEY")
    if secret_key is None:
        # Refusing to start is the safe failure. A production server quietly
        # using a random key would log every user out on each restart.
        if environment == "production":
            raise RuntimeError("SECRET_KEY must be set when ENVIRONMENT=production")
        secret_key = secrets.token_hex(32)

    origins = os.environ.get("CORS_ORIGINS")
    return Settings(
        environment=environment,
        database_url=os.environ.get("DATABASE_URL", "sqlite:///./capstone.db"),
        secret_key=secret_key,
        access_token_minutes=int(os.environ.get("ACCESS_TOKEN_MINUTES", "30")),
        cors_origins=origins.split(",") if origins else ["http://localhost:5173"],
        log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    )


settings = load_settings()

"""Password hashing and login tokens. Lesson 09, as a module."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    parts = stored.split("$")
    if len(parts) != 3 or parts[0] != "scrypt":
        return False
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(parts[1]), n=2**14, r=8, p=1)
    return hmac.compare_digest(digest.hex(), parts[2])


# Checked against when a login email doesn't exist, so failed logins take the
# same time either way and don't reveal which emails have accounts.
DUMMY_HASH = hash_password(secrets.token_hex(16))


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "iat": now,
               "exp": now + timedelta(minutes=settings.access_token_minutes)}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    """Return the user id inside a valid token. Raises jwt.InvalidTokenError otherwise."""
    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    try:
        return int(payload["sub"])
    except (KeyError, ValueError) as error:
        raise jwt.InvalidTokenError("token has no valid subject") from error

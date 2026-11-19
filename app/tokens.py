import os
from datetime import datetime, timedelta, timezone

import jwt

from app.exceptions import AuthenticationError

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_ENV_VAR = "JWT_SECRET_KEY"


def _get_secret() -> str:
    """Reads the signing secret from the environment, never from source code."""
    secret = os.environ.get(SECRET_ENV_VAR)
    if not secret:
        raise RuntimeError(f"{SECRET_ENV_VAR} is not set")
    return secret


def create_access_token(customer_id: int, expires_delta: timedelta | None = None) -> str:
    """Returns a signed token for this customer that expires after a set time."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(customer_id),
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, _get_secret(), algorithm=ALGORITHM)


def verify_access_token(token: str) -> int:
    """Returns the customer id from a valid token.
    Raises AuthenticationError if it is expired, tampered with or malformed."""
    secret = _get_secret()
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError):
        raise AuthenticationError("Invalid or expired token")
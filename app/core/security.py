"""JWT token utilities and password hashing helpers."""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any],
    settings: Settings,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": TOKEN_TYPE_ACCESS})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(
    data: dict[str, Any],
    settings: Settings,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta
        if expires_delta is not None
        else timedelta(days=settings.refresh_token_expire_days)
    )
    to_encode.update({"exp": expire, "type": TOKEN_TYPE_REFRESH})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str, settings: Settings) -> dict[str, Any]:
    """Decode and validate a JWT token signature and expiry."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def verify_jwt_token(
    token: str,
    settings: Settings,
    expected_type: str = TOKEN_TYPE_ACCESS,
) -> dict[str, Any]:
    """Decode a JWT and enforce token type and subject presence."""
    try:
        payload = decode_token(token, settings)
    except JWTError as exc:
        raise JWTError("Invalid or expired token") from exc

    token_type = payload.get("type")
    if token_type != expected_type:
        raise JWTError(f"Invalid token type: expected {expected_type}")

    if not payload.get("sub"):
        raise JWTError("Token missing subject claim")

    return payload

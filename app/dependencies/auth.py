"""Authentication dependency providers for FastAPI routes."""

import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import TOKEN_TYPE_ACCESS, decode_token
from app.db.session import get_db
from app.exceptions.http_exceptions import ForbiddenError, UnauthorizedError
from app.models.user import MARKETING_TEAM_MEMBER_ROLE, User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/marketing-team-member/login",
    auto_error=False,
)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    """Resolve the authenticated user from a Bearer JWT access token.

    Raises:
        UnauthorizedError: Missing, invalid, or expired token.
        ForbiddenError: User inactive or not a marketing team member.
    """
    if not token:
        raise UnauthorizedError(
            message="Authentication required.",
            code="UNAUTHORIZED",
        )

    try:
        payload = decode_token(token, settings)
    except JWTError as exc:
        raise UnauthorizedError(
            message="Invalid or expired token.",
            code="INVALID_TOKEN",
        ) from exc

    if payload.get("type") != TOKEN_TYPE_ACCESS:
        raise UnauthorizedError(
            message="Invalid token type.",
            code="INVALID_TOKEN",
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError(
            message="Invalid token subject.",
            code="INVALID_TOKEN",
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError as exc:
        raise UnauthorizedError(
            message="Invalid token subject.",
            code="INVALID_TOKEN",
        ) from exc

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise UnauthorizedError(
            message="User not found.",
            code="USER_NOT_FOUND",
        )

    if not user.is_active:
        raise ForbiddenError(
            message="Your account is inactive. Contact an administrator.",
            code="ACCOUNT_INACTIVE",
        )

    if user.role != MARKETING_TEAM_MEMBER_ROLE:
        raise ForbiddenError(
            message="You are not authorized to access this application.",
            code="ACCESS_DENIED",
        )

    return user


def get_current_active_marketing_member(
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the current authenticated marketing team member."""
    return current_user

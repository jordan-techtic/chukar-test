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


async def get_current_user_id(
    token: str | None = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> uuid.UUID:
    """Resolve and return the authenticated user ID from a Bearer JWT."""
    if not token:
        raise UnauthorizedError(
            message="Authentication required.",
            code="UNAUTHORIZED",
        )

    try:
        payload = decode_token(token, settings)
    except JWTError as exc:
        raise UnauthorizedError(
            message="Invalid or expired authentication token.",
            code="UNAUTHORIZED",
        ) from exc

    if payload.get("type") != TOKEN_TYPE_ACCESS:
        raise UnauthorizedError(
            message="Invalid or expired authentication token.",
            code="UNAUTHORIZED",
        )

    subject = payload.get("sub")
    if not subject:
        raise UnauthorizedError(
            message="Invalid or expired authentication token.",
            code="UNAUTHORIZED",
        )

    try:
        return uuid.UUID(str(subject))
    except ValueError as exc:
        raise UnauthorizedError(
            message="Invalid or expired authentication token.",
            code="UNAUTHORIZED",
        ) from exc


async def get_current_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> User:
    """Load the authenticated user and enforce active marketing team member role."""
    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise UnauthorizedError(
            message="Invalid or expired authentication token.",
            code="UNAUTHORIZED",
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

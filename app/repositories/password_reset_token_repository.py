"""Password reset token data access repository."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:
    """Encapsulates database queries for password reset tokens."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with a database session."""
        self._db = db

    def create(self, token: PasswordResetToken) -> PasswordResetToken:
        """Persist a new password reset token."""
        self._db.add(token)
        self._db.flush()
        self._db.refresh(token)
        return token

    def invalidate_existing_for_user(self, user_id: uuid.UUID) -> None:
        """Mark all unused tokens for a user as used."""
        now = datetime.now(UTC)
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
        )
        tokens = self._db.scalars(stmt).all()
        for token in tokens:
            token.used_at = now
        if tokens:
            self._db.flush()

"""Password reset token data access repository."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:
    """Encapsulates database queries for password reset tokens."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active SQLAlchemy session."""
        self._db = db

    def create_token(
        self,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> PasswordResetToken:
        """Persist a new password reset token."""
        token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self._db.add(token)
        self._db.commit()
        self._db.refresh(token)
        return token

    def invalidate_active_tokens_for_user(self, user_id: uuid.UUID) -> None:
        """Mark all unused tokens for a user as used."""
        now = datetime.now(UTC)
        statement = (
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=now)
        )
        self._db.execute(statement)
        self._db.commit()

    def get_valid_token(self, token_hash: str) -> PasswordResetToken | None:
        """Return an unused, unexpired token matching the given hash."""
        now = datetime.now(UTC)
        statement = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now,
        )
        return self._db.scalar(statement)

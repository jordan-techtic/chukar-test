"""User data access repository."""

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Encapsulates database queries for User records."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active SQLAlchemy session."""
        self._db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Return a user by primary key."""
        return self._db.get(User, user_id)

    def get_by_email_insensitive(self, email: str) -> User | None:
        """Return a user matching email case-insensitively."""
        statement = select(User).where(func.lower(User.email) == email.lower())
        return self._db.scalar(statement)

    def get_by_username_insensitive(self, username: str) -> User | None:
        """Return a user matching username case-insensitively."""
        statement = select(User).where(func.lower(User.username) == username.lower())
        return self._db.scalar(statement)

    def get_by_email_or_username(self, identifier: str) -> User | None:
        """Return a user matching email or username case-insensitively."""
        lowered = identifier.lower()
        statement = select(User).where(
            or_(
                func.lower(User.email) == lowered,
                func.lower(User.username) == lowered,
            )
        )
        return self._db.scalar(statement)

    def create(self, user: User) -> User:
        """Persist a new user record."""
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Persist changes to an existing user record."""
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

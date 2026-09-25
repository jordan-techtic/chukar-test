"""User data access repository."""

import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Encapsulates database queries for User entities."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with a database session."""
        self._db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Fetch a user by primary key."""
        return self._db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email address (case-insensitive)."""
        stmt = select(User).where(User.email == email.lower())
        return self._db.scalars(stmt).first()

    def get_by_username(self, username: str) -> User | None:
        """Fetch a user by username (case-insensitive)."""
        stmt = select(User).where(User.username == username.lower())
        return self._db.scalars(stmt).first()

    def get_by_email_or_username(self, identifier: str) -> User | None:
        """Fetch a user by email or username (case-insensitive)."""
        normalized = identifier.strip().lower()
        stmt = select(User).where(
            or_(User.email == normalized, User.username == normalized)
        )
        return self._db.scalars(stmt).first()

    def create(self, user: User) -> User:
        """Persist a new user record."""
        self._db.add(user)
        self._db.flush()
        self._db.refresh(user)
        return user

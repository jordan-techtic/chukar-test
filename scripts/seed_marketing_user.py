"""Seed an authorized marketing team member for development and testing."""

import argparse
import sys

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import MARKETING_TEAM_MEMBER_ROLE, User
from app.repositories.user_repository import UserRepository


def main() -> int:
    """Create a marketing team member user if one does not already exist."""
    parser = argparse.ArgumentParser(
        description="Seed a marketing team member user.",
    )
    parser.add_argument("--email", required=True, help="User email address")
    parser.add_argument("--username", required=True, help="Username")
    parser.add_argument("--password", required=True, help="Plain-text password")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        repo = UserRepository(db)
        existing = repo.get_by_email_or_username(args.email)
        if existing:
            print(f"User already exists: {existing.email}", file=sys.stderr)
            return 1

        existing_username = repo.get_by_username(args.username)
        if existing_username:
            print(f"Username already taken: {args.username}", file=sys.stderr)
            return 1

        user = User(
            email=args.email.lower(),
            username=args.username.lower(),
            password_hash=hash_password(args.password),
            is_active=True,
            role=MARKETING_TEAM_MEMBER_ROLE,
        )
        repo.create(user)
        db.commit()
        print(f"Created marketing team member: {user.email}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())

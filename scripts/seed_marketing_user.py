"""Seed an authorized marketing team member for development and testing."""

import argparse
import sys

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import MARKETING_TEAM_MEMBER_ROLE, User
from app.repositories.user_repository import UserRepository


def main() -> int:
    """Create or update a marketing team member user from CLI arguments."""
    parser = argparse.ArgumentParser(description="Seed a marketing team member user.")
    parser.add_argument("--email", required=True, help="User email address")
    parser.add_argument("--username", required=True, help="Unique username")
    parser.add_argument("--password", required=True, help="Plaintext password")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        repo = UserRepository(db)
        existing = repo.get_by_email_or_username(args.email)
        if existing is None:
            existing = repo.get_by_email_or_username(args.username)

        if existing is not None:
            existing.email = args.email
            existing.username = args.username
            existing.hashed_password = hash_password(args.password)
            existing.role = MARKETING_TEAM_MEMBER_ROLE
            existing.is_active = True
            repo.update(existing)
            print(f"Updated marketing team member: {existing.email}")
        else:
            user = User(
                email=args.email,
                username=args.username,
                hashed_password=hash_password(args.password),
                role=MARKETING_TEAM_MEMBER_ROLE,
                is_active=True,
            )
            repo.create(user)
            print(f"Created marketing team member: {user.email}")
        return 0
    except Exception as exc:
        print(f"Failed to seed user: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())

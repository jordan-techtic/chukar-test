"""Verify PostgreSQL database connectivity."""

import sys

from app.db.session import verify_database_connection


def main() -> int:
    """Exit 0 when the database is reachable, 1 otherwise."""
    if verify_database_connection():
        print("Database connection successful.")
        return 0
    print("Database connection failed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

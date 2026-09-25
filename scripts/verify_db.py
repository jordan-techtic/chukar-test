"""Verify PostgreSQL database connectivity."""

import sys

from app.db.session import verify_database_connection


def main() -> int:
    """Run a simple SELECT 1 query to confirm database connectivity."""
    try:
        verify_database_connection()
        print("Database connection OK")
        return 0
    except Exception as exc:
        print(f"Database connection failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

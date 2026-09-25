"""Initial migration baseline.

Revision ID: 0001_initial_migration
Revises:
Create Date: 2026-09-25

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "0001_initial_migration"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply baseline migration — no tables yet."""


def downgrade() -> None:
    """Revert baseline migration."""

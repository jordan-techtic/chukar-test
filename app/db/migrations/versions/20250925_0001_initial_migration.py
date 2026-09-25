"""Initial migration

Revision ID: 20250925_0001
Revises:
Create Date: 2025-09-25 00:00:00.000000

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "20250925_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Initial schema bootstrap — no tables yet."""


def downgrade() -> None:
    """Revert initial migration."""

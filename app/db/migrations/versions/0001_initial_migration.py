"""Initial migration baseline.

Revision ID: 0001_initial_migration
Revises:
Create Date: 2026-09-25

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "0001_initial_migration"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply baseline migration — no tables yet."""
    pass


def downgrade() -> None:
    """Revert baseline migration."""
    pass

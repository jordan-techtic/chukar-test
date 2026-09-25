"""Initial migration

Revision ID: 20250925_0001
Revises:
Create Date: 2025-09-25 00:00:00.000000

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "20250925_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Initial schema bootstrap — no tables yet."""
    pass


def downgrade() -> None:
    """Revert initial migration."""
    pass

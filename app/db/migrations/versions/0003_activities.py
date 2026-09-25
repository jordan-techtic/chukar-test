"""Create activities table.

Revision ID: 0003_activities
Revises: 0002_users_reset_tokens
Create Date: 2026-09-25

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_activities"
down_revision: str | None = "0002_users_reset_tokens"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create activities table with unique date+type constraint."""
    op.create_table(
        "activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("activity_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("activity_date", sa.Date(), nullable=False),
        sa.Column("campaign_code", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("activity_date", "activity_type", name="uq_activities_date_type"),
    )
    op.create_index("ix_activities_activity_type", "activities", ["activity_type"], unique=False)
    op.create_index("ix_activities_activity_date", "activities", ["activity_date"], unique=False)
    op.create_index("ix_activities_campaign_code", "activities", ["campaign_code"], unique=False)
    op.create_index("ix_activities_category", "activities", ["category"], unique=False)


def downgrade() -> None:
    """Drop activities table."""
    op.drop_index("ix_activities_category", table_name="activities")
    op.drop_index("ix_activities_campaign_code", table_name="activities")
    op.drop_index("ix_activities_activity_date", table_name="activities")
    op.drop_index("ix_activities_activity_type", table_name="activities")
    op.drop_table("activities")

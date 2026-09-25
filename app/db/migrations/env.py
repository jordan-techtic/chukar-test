"""Alembic migration environment configuration."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.db.base import Base

# Import models so Alembic can detect metadata changes.
import app.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _sync_database_url(url: str) -> str:
    """Return a sync PostgreSQL URL using psycopg2 for Alembic migrations."""
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


settings = get_settings()
config.set_main_option(
    "sqlalchemy.url",
    _sync_database_url(settings.database_url),
)


# --- alex:migration-history start (managed by Alex) ---
# Records every applied revision (who, where, when) in alembic_migration_history;
# alembic_version alone only keeps the current head.
import getpass as _alex_getpass
import logging as _alex_logging
import socket as _alex_socket
from datetime import datetime as _alex_datetime
from datetime import timezone as _alex_timezone

import sqlalchemy as _alex_sa

ALEX_MIGRATION_HISTORY_TABLE = "alembic_migration_history"
_alex_history = _alex_sa.Table(
    ALEX_MIGRATION_HISTORY_TABLE,
    _alex_sa.MetaData(),
    _alex_sa.Column("id", _alex_sa.Integer, primary_key=True, autoincrement=True),
    _alex_sa.Column("revision", _alex_sa.String(255), nullable=False),
    _alex_sa.Column("down_revisions", _alex_sa.String(255), nullable=True),
    _alex_sa.Column("direction", _alex_sa.String(16), nullable=False),
    _alex_sa.Column("is_stamp", _alex_sa.Boolean, nullable=False),
    _alex_sa.Column("description", _alex_sa.String(255), nullable=True),
    _alex_sa.Column("applied_by", _alex_sa.String(128), nullable=True),
    _alex_sa.Column("hostname", _alex_sa.String(255), nullable=True),
    _alex_sa.Column("applied_at", _alex_sa.DateTime(timezone=True), nullable=False),
)


def _alex_include_name(name, type_, parent_names):
    return not (type_ == "table" and name == ALEX_MIGRATION_HISTORY_TABLE)


def _alex_record_migration(ctx, step, heads, run_args):
    if ctx.as_sql or ctx.connection is None:
        return
    try:
        user = _alex_getpass.getuser()
    except Exception:
        user = None
    try:
        doc = (step.up_revision.doc or "") if step.up_revision is not None else ""
    except Exception:
        doc = ""
    row = {
        "revision": ",".join(step.up_revision_ids) or "base",
        "down_revisions": ",".join(step.down_revision_ids) or None,
        "direction": "upgrade" if step.is_upgrade else "downgrade",
        "is_stamp": bool(step.is_stamp),
        "description": doc.strip().splitlines()[0][:255] if doc.strip() else None,
        "applied_by": user,
        "hostname": _alex_socket.gethostname(),
        "applied_at": _alex_datetime.now(_alex_timezone.utc),
    }
    conn = ctx.connection
    try:
        with conn.begin_nested():
            _alex_history.create(conn, checkfirst=True)
            conn.execute(_alex_history.insert().values(**row))
    except Exception as exc:  # history must never block a migration
        _alex_logging.getLogger("alembic").warning(
            "Could not record migration history: %s", exc
        )


# --- alex:migration-history end ---


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        on_version_apply=_alex_record_migration,
        include_name=_alex_include_name,
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url")
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            on_version_apply=_alex_record_migration,
            include_name=_alex_include_name,
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

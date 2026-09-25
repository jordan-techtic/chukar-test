"""Database URL normalization helpers."""


def normalize_database_url(url: str) -> str:
    """Ensure PostgreSQL URLs use the psycopg2 driver for SQLAlchemy."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    return url

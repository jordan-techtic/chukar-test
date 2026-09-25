"""Database URL normalization helpers."""


def normalize_database_url(url: str) -> str:
    """Return a sync PostgreSQL URL using psycopg2 (project-installed driver).

    SQLAlchemy 2.x maps bare ``postgresql://`` to psycopg3 by default; this
    project uses ``psycopg2-binary`` instead.
    """
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url

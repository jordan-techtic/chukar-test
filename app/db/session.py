"""Database engine, session factory, and FastAPI dependency."""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.database_url import normalize_database_url

settings = get_settings()
engine = create_engine(
    normalize_database_url(settings.database_url),
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for the duration of a request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_database_connection() -> bool:
    """Return True if a simple SELECT 1 succeeds against the configured database."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

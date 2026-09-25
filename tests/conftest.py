"""Shared pytest fixtures."""

import os
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Set required environment variables before application imports.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:root@127.0.0.1:5432/marketing_cal",
)
os.environ.setdefault(
    "JWT_SECRET",
    "test-jwt-secret-key-for-pytest-only-minimum-length",
)
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
os.environ.setdefault("AUTH_STRATEGY", "jwt")
os.environ.setdefault(
    "CORS_ORIGINS",
    '["http://localhost:3000"]',
)
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("KLAVIYO_API_KEY", "pk_test_key")
os.environ.setdefault(
    "FRONTEND_RESET_URL",
    "http://localhost:3000/reset-password",
)

from app.core.config import get_settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import MARKETING_TEAM_MEMBER_ROLE, User  # noqa: E402


def _postgres_available(database_url: str) -> bool:
    """Return True if PostgreSQL is reachable."""
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def postgres_engine():
    """Session-scoped PostgreSQL engine; skipped if DB unavailable."""
    database_url = os.environ["DATABASE_URL"]
    if not _postgres_available(database_url):
        pytest.skip("PostgreSQL not available for integration tests")
    engine = create_engine(database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(postgres_engine) -> Generator[Session, None, None]:
    """Yield a transactional database session rolled back after each test."""
    connection = postgres_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def seed_user(db_session: Session) -> User:
    """Create an active marketing team member in the test database."""
    user = User(
        email="marketing.user@example.com",
        username="marketing_user",
        password_hash=hash_password("SecurePass1!"),
        is_active=True,
        role=MARKETING_TEAM_MEMBER_ROLE,
    )
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    return user


@pytest.fixture
def inactive_user(db_session: Session) -> User:
    """Create an inactive marketing team member in the test database."""
    user = User(
        email="inactive.user@example.com",
        username="inactive_user",
        password_hash=hash_password("SecurePass1!"),
        is_active=False,
        role=MARKETING_TEAM_MEMBER_ROLE,
    )
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    return user


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Return a basic FastAPI test client without database override."""
    get_settings.cache_clear()
    yield TestClient(app)
    get_settings.cache_clear()


@pytest.fixture
def db_client(db_session: Session) -> Generator[TestClient, None, None]:
    """Return a FastAPI test client with database session override."""

    def _override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
            db_session.flush()
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db] = _override_get_db
    get_settings.cache_clear()
    yield TestClient(app)
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def mock_klaviyo_client(monkeypatch) -> MagicMock:
    """Mock KlaviyoClient to prevent external API calls in tests."""
    mock = MagicMock()
    mock.send_password_reset_email.return_value = None
    monkeypatch.setattr(
        "app.services.auth_service.KlaviyoClient",
        lambda settings: mock,
    )
    return mock


@pytest.fixture
def settings():
    """Return application settings with a cleared cache."""
    get_settings.cache_clear()
    return get_settings()


@pytest.fixture
def sqlite_session() -> Generator[Session, None, None]:
    """In-memory SQLite session for unit tests that need a real Session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

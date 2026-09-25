"""Shared pytest fixtures."""

import os
from collections.abc import Generator
from unittest.mock import MagicMock
from urllib.parse import urlparse, urlunparse

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
    "TEST_DATABASE_URL",
    "postgresql://postgres:root@127.0.0.1:5432/marketing_cal_test",
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


def _resolve_test_database_url() -> str:
    """Return a dedicated test database URL, never the dev database."""
    explicit = os.environ.get("TEST_DATABASE_URL", "").strip()
    if explicit:
        return explicit

    base_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:root@127.0.0.1:5432/marketing_cal",
    )
    parsed = urlparse(base_url)
    db_name = parsed.path.lstrip("/") or "marketing_cal"
    if db_name.endswith("_test"):
        return base_url

    test_db_name = f"{db_name}_test"
    test_path = f"/{test_db_name}"
    return urlunparse(parsed._replace(path=test_path))


def _assert_safe_test_database(database_url: str) -> None:
    """Refuse integration tests against a non-test database name."""
    db_name = urlparse(database_url).path.lstrip("/")
    if not db_name.endswith("_test"):
        pytest.skip(
            "Integration tests require a dedicated test database URL "
            f"(database name must end with '_test', got '{db_name}'). "
            "Set TEST_DATABASE_URL to a separate database."
        )


@pytest.fixture(scope="session")
def postgres_engine():
    """Session-scoped PostgreSQL engine against a dedicated test database.

    Schema is created once if missing. Each test uses transaction rollbacks
    via db_session — tables are never dropped on teardown.
    """
    database_url = _resolve_test_database_url()
    _assert_safe_test_database(database_url)

    if not _postgres_available(database_url):
        pytest.skip(
            "PostgreSQL test database not available for integration tests. "
            f"Expected reachable database at: {database_url}"
        )

    engine = create_engine(database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    yield engine
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

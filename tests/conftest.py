"""Shared pytest fixtures for integration and unit tests."""

import os
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock
from urllib.parse import urlparse, urlunparse

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


def _ensure_psycopg2_url(url: str) -> str:
    """Normalize PostgreSQL URLs to use psycopg2 (installed driver)."""
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


# Environment defaults before application imports.
_default_db = _ensure_psycopg2_url(
    os.environ.get("DATABASE_URL", "postgresql://postgres:root@127.0.0.1:5432/marketing_cal")
)
_default_test_db = _ensure_psycopg2_url(
    os.environ.get("TEST_DATABASE_URL", "postgresql://postgres:root@127.0.0.1:5432/marketing_cal")
)
os.environ["DATABASE_URL"] = _ensure_psycopg2_url(os.environ.get("DATABASE_URL", _default_db))
os.environ["TEST_DATABASE_URL"] = _ensure_psycopg2_url(
    os.environ.get("TEST_DATABASE_URL", _default_test_db)
)
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-key-for-pytest-only-minimum-length")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
os.environ.setdefault("AUTH_STRATEGY", "jwt")
os.environ.setdefault("CORS_ORIGINS", '["http://localhost:3000"]')
os.environ.setdefault("ENVIRONMENT", "test")
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("KLAVIYO_API_KEY", "pk_test_key")
os.environ.setdefault("FRONTEND_RESET_URL", "http://localhost:3000/reset-password")

from app.core.config import get_settings
from app.core.security import (
    TOKEN_TYPE_ACCESS,
    create_access_token,
    hash_password,
)
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import MARKETING_TEAM_MEMBER_ROLE, User

# --- Test user credentials (5 distinct users) ---
ADMIN_EMAIL = "admin@test.com"
ADMIN_USERNAME = "admin_user"
ADMIN_PASSWORD = "TestAdmin123!"

REGULAR_EMAIL = "user@test.com"
REGULAR_USERNAME = "regular_user"
REGULAR_PASSWORD = "TestUser123!"

VIEWER_EMAIL = "viewer@test.com"
VIEWER_USERNAME = "viewer_user"
VIEWER_PASSWORD = "TestViewer123!"

INACTIVE_EMAIL = "inactive@test.com"
INACTIVE_USERNAME = "inactive_user"
INACTIVE_PASSWORD = "TestInactive123!"

NEW_USER_EMAIL = "newuser@test.com"
NEW_USER_PASSWORD = "NewUser123!"


def _sync_postgres_url(url: str) -> str:
    """Force psycopg2 driver for SQLAlchemy test engines."""
    return _ensure_psycopg2_url(url)


def _postgres_available(database_url: str) -> bool:
    """Return True if PostgreSQL is reachable."""
    try:
        engine = create_engine(_sync_postgres_url(database_url), pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False


def _resolve_test_database_url() -> str:
    """Return dedicated test database URL, never the dev database."""
    explicit = os.environ.get("TEST_DATABASE_URL", "").strip()
    if explicit:
        return explicit
    base_url = os.environ["DATABASE_URL"]
    parsed = urlparse(base_url)
    db_name = parsed.path.lstrip("/") or "marketing_cal"
    if db_name.endswith("_test"):
        return base_url
    return urlunparse(parsed._replace(path=f"/{db_name}_test"))


def _assert_safe_test_database(database_url: str) -> None:
    """Refuse integration tests against a non-test database name."""
    db_name = urlparse(database_url).path.lstrip("/")
    if not db_name.endswith("_test"):
        pytest.skip(
            f"Integration tests require database name ending with '_test', got '{db_name}'"
        )


def _insert_user(
    session: Session,
    *,
    email: str,
    username: str,
    password: str,
    role: str,
    is_active: bool,
) -> User:
    """Insert a user into the current test transaction."""
    user = User(
        email=email.lower(),
        username=username.lower(),
        password_hash=hash_password(password),
        is_active=is_active,
        role=role,
    )
    session.add(user)
    session.flush()
    session.refresh(user)
    return user


@pytest.fixture(scope="session")
def postgres_engine():
    """Session-scoped PostgreSQL engine; schema created once, never dropped."""
    database_url = _resolve_test_database_url()
    _assert_safe_test_database(database_url)
    if not _postgres_available(database_url):
        pytest.skip(f"PostgreSQL test database unavailable at {database_url}")
    engine = create_engine(_sync_postgres_url(database_url), pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(postgres_engine) -> Generator[Session, None, None]:
    """Transactional session rolled back after each test (truncate via rollback)."""
    connection = postgres_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Active marketing team member — primary authorized user (admin equivalent)."""
    return _insert_user(
        db_session,
        email=ADMIN_EMAIL,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        role=MARKETING_TEAM_MEMBER_ROLE,
        is_active=True,
    )


@pytest.fixture
def regular_user(db_session: Session) -> User:
    """Active marketing team member — standard authorized user."""
    return _insert_user(
        db_session,
        email=REGULAR_EMAIL,
        username=REGULAR_USERNAME,
        password=REGULAR_PASSWORD,
        role=MARKETING_TEAM_MEMBER_ROLE,
        is_active=True,
    )


@pytest.fixture
def viewer_user(db_session: Session) -> User:
    """Active user with wrong role — read-only/unauthorized for this app."""
    return _insert_user(
        db_session,
        email=VIEWER_EMAIL,
        username=VIEWER_USERNAME,
        password=VIEWER_PASSWORD,
        role="viewer",
        is_active=True,
    )


@pytest.fixture
def inactive_user(db_session: Session) -> User:
    """Inactive marketing team member — account exists but deactivated."""
    return _insert_user(
        db_session,
        email=INACTIVE_EMAIL,
        username=INACTIVE_USERNAME,
        password=INACTIVE_PASSWORD,
        role=MARKETING_TEAM_MEMBER_ROLE,
        is_active=False,
    )


@pytest.fixture
def new_user_credentials() -> dict:
    """Credentials for a user not yet in the database (registration/forgot-password tests)."""
    return {
        "email": NEW_USER_EMAIL,
        "username": "new_user",
        "password": NEW_USER_PASSWORD,
        "role": MARKETING_TEAM_MEMBER_ROLE,
        "is_active": True,
    }


@pytest.fixture
def all_db_users(admin_user, regular_user, viewer_user, inactive_user) -> dict[str, User]:
    """All four persisted test users keyed by fixture name."""
    return {
        "admin": admin_user,
        "regular": regular_user,
        "viewer": viewer_user,
        "inactive": inactive_user,
    }


@pytest.fixture(autouse=True)
def _disable_rate_limiting() -> Generator[None, None, None]:
    """Prevent slowapi shared counters from causing 429s across TestClient calls."""
    from app.core.rate_limit import limiter

    previous = limiter.enabled
    limiter.enabled = False
    yield
    limiter.enabled = previous


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Basic TestClient without DB override (health/docs tests)."""
    get_settings.cache_clear()
    yield TestClient(app)
    get_settings.cache_clear()


@pytest.fixture
def db_client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient with get_db overridden to transactional test session."""

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
    """Mock KlaviyoClient — no real HTTP calls to Klaviyo."""
    mock = MagicMock()
    mock.send_password_reset_email.return_value = None
    monkeypatch.setattr("app.services.auth_service.KlaviyoClient", lambda settings: mock)
    return mock


@pytest.fixture
def settings():
    """Application settings with cleared cache."""
    get_settings.cache_clear()
    return get_settings()


@pytest.fixture
def admin_access_token(admin_user, settings) -> str:
    """JWT access token for admin marketing team member."""
    return create_access_token({"sub": str(admin_user.id)}, settings)


@pytest.fixture
def regular_access_token(regular_user, settings) -> str:
    """JWT access token for regular marketing team member."""
    return create_access_token({"sub": str(regular_user.id)}, settings)


@pytest.fixture
def auth_headers_admin(admin_access_token) -> dict[str, str]:
    """Authorization header for admin user Bearer token."""
    return {"Authorization": f"Bearer {admin_access_token}"}


@pytest.fixture
def auth_headers_regular(regular_access_token) -> dict[str, str]:
    """Authorization header for regular user Bearer token."""
    return {"Authorization": f"Bearer {regular_access_token}"}


@pytest.fixture
def expired_access_token(admin_user, settings) -> str:
    """Expired JWT access token for auth rejection tests."""
    expire = datetime.now(UTC) - timedelta(minutes=5)
    payload = {"sub": str(admin_user.id), "exp": expire, "type": TOKEN_TYPE_ACCESS}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@pytest.fixture
def sqlite_session() -> Generator[Session, None, None]:
    """In-memory SQLite session for unit tests (non-PostgreSQL)."""
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


# Backward-compatible alias used by older tests
@pytest.fixture
def seed_user(admin_user) -> User:
    """Alias for admin_user fixture."""
    return admin_user

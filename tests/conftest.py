"""Shared pytest fixtures for integration and unit tests."""

import os
import secrets
import uuid
from collections.abc import Generator
from unittest.mock import patch
from urllib.parse import quote_plus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.database_url import normalize_database_url
from app.db.session import get_db
from app.main import create_app
from app.models.user import MARKETING_TEAM_MEMBER_ROLE, User

LOGIN_URL = "/api/v1/marketing-team-member/login"
FORGOT_PASSWORD_URL = "/api/v1/marketing-team-member/forgot-password"
HEALTH_URL = "/api/v1/health"
PROTECTED_PROBE_URL = "/api/v1/internal/protected-probe"


def _build_postgres_url(database: str) -> str:
    """Build a PostgreSQL URL from optional TEST_DB_* environment variables."""
    host = os.environ.get("TEST_DB_HOST", "127.0.0.1")
    port = os.environ.get("TEST_DB_PORT", "5432")
    user = quote_plus(os.environ.get("TEST_DB_USER", "postgres"))
    password = os.environ.get("TEST_DB_PASSWORD", "")
    credentials = f"{user}:{quote_plus(password)}" if password else user
    return f"postgresql://{credentials}@{host}:{port}/{database}"


if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = _build_postgres_url("marketing_cal")
if "TEST_DATABASE_URL" not in os.environ:
    os.environ["TEST_DATABASE_URL"] = _build_postgres_url("marketing_cal_test")
if "JWT_SECRET" not in os.environ:
    os.environ["JWT_SECRET"] = secrets.token_urlsafe(32)

os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
os.environ.setdefault("AUTH_STRATEGY", "jwt")
os.environ.setdefault("CORS_ORIGINS", '["http://localhost:3000"]')
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("KLAVIYO_API_KEY", "")

if "TEST_USER_PASSWORD" not in os.environ:
    os.environ["TEST_USER_PASSWORD"] = secrets.token_urlsafe(16)

TEST_PASSWORD = os.environ["TEST_USER_PASSWORD"]

# Five test personas mapped to this API's role model.
ADMIN_EMAIL = "admin@test.com"
ADMIN_USERNAME = "admin_user"
MEMBER_EMAIL = "user@test.com"
MEMBER_USERNAME = "marketing_member"
VIEWER_EMAIL = "viewer@test.com"
VIEWER_USERNAME = "viewer_user"
INACTIVE_EMAIL = "inactive@test.com"
INACTIVE_USERNAME = "inactive_user"
NEW_USER_EMAIL = "newuser@test.com"
NEW_USER_USERNAME = "new_user"

# Backward-compatible aliases used by legacy tests.
MARKETING_EMAIL = MEMBER_EMAIL
MARKETING_USERNAME = MEMBER_USERNAME
MARKETING_PASSWORD = TEST_PASSWORD
ADMIN_PASSWORD = TEST_PASSWORD
INACTIVE_PASSWORD = TEST_PASSWORD
WRONG_ROLE_EMAIL = ADMIN_EMAIL
WRONG_ROLE_USERNAME = ADMIN_USERNAME
WRONG_ROLE_PASSWORD = TEST_PASSWORD


def _seed_test_users(db: Session) -> None:
    """Insert the five canonical test personas (four in DB, one reserved for registration)."""
    personas = [
        User(
            email=ADMIN_EMAIL,
            username=ADMIN_USERNAME,
            hashed_password=hash_password(TEST_PASSWORD),
            role="admin",
            is_active=True,
        ),
        User(
            email=MEMBER_EMAIL,
            username=MEMBER_USERNAME,
            hashed_password=hash_password(TEST_PASSWORD),
            role=MARKETING_TEAM_MEMBER_ROLE,
            is_active=True,
        ),
        User(
            email=VIEWER_EMAIL,
            username=VIEWER_USERNAME,
            hashed_password=hash_password(TEST_PASSWORD),
            role="viewer",
            is_active=True,
        ),
        User(
            email=INACTIVE_EMAIL,
            username=INACTIVE_USERNAME,
            hashed_password=hash_password(TEST_PASSWORD),
            role=MARKETING_TEAM_MEMBER_ROLE,
            is_active=False,
        ),
    ]
    db.add_all(personas)
    db.commit()


def _truncate_all_tables(engine) -> None:
    """Remove rows between tests without dropping schema."""
    table_names = ", ".join(
        f'"{table.name}"' for table in reversed(Base.metadata.sorted_tables)
    )
    if not table_names:
        return
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture(scope="session")
def test_engine():
    """Create a session-scoped PostgreSQL engine and schema for integration tests."""
    get_settings.cache_clear()
    settings = get_settings()
    test_url = settings.test_database_url or settings.database_url
    engine = create_engine(normalize_database_url(test_url), pool_pre_ping=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session_factory(test_engine):
    """Provide a session factory bound to the test engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_client(test_engine, db_session_factory) -> Generator[TestClient, None, None]:
    """FastAPI TestClient backed by PostgreSQL with seeded users and table truncation."""
    testing_session = db_session_factory

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    get_settings.cache_clear()
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with testing_session() as db:
        _truncate_all_tables(test_engine)
        _seed_test_users(db)

    with patch(
        "app.clients.klaviyo_client.KlaviyoClient.send_password_reset_email",
    ):
        with TestClient(app) as test_client:
            yield test_client

    app.dependency_overrides.clear()
    _truncate_all_tables(test_engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient without database overrides (health/docs tests)."""
    get_settings.cache_clear()
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def member_access_token(db_client: TestClient) -> str:
    """Return a valid JWT access token for the active marketing team member."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": MEMBER_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()["data"]["tokens"]["access_token"]


@pytest.fixture
def admin_access_token_attempt(db_client: TestClient) -> None:
    """Admin users cannot obtain tokens; fixture documents expected denial."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": ADMIN_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 403


@pytest.fixture
def expired_access_token(db_client: TestClient) -> str:
    """Return an expired JWT access token for middleware rejection tests."""
    from datetime import timedelta

    settings = get_settings()
    login = db_client.post(
        LOGIN_URL,
        json={"email_or_username": MEMBER_EMAIL, "password": TEST_PASSWORD},
    )
    member_id = login.json()["data"]["user"]["id"]
    return create_access_token(
        {"sub": member_id},
        settings,
        expires_delta=timedelta(seconds=-1),
    )

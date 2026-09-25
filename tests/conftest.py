"""Shared pytest fixtures for integration and unit tests."""

import os
import secrets
from collections.abc import Generator
from urllib.parse import quote_plus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


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
    os.environ["TEST_DATABASE_URL"] = _build_postgres_url("marketing_cal_alex_test")
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

ADMIN_EMAIL = "marketing.user@example.com"
ADMIN_USERNAME = "marketing_user"
ADMIN_PASSWORD = os.environ["TEST_USER_PASSWORD"]
INACTIVE_EMAIL = "inactive.user@example.com"
INACTIVE_PASSWORD = os.environ["TEST_USER_PASSWORD"]
WRONG_ROLE_EMAIL = "admin.user@example.com"
WRONG_ROLE_USERNAME = "admin_user"
WRONG_ROLE_PASSWORD = os.environ["TEST_USER_PASSWORD"]


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient for HTTP integration tests."""
    from app.core.config import get_settings
    from app.main import create_app

    get_settings.cache_clear()
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def db_client() -> Generator[TestClient, None, None]:
    """Provide a TestClient wired to an isolated PostgreSQL test database."""
    from app.core.config import get_settings
    from app.core.security import hash_password
    from app.db.base import Base
    from app.db.database_url import normalize_database_url
    from app.db.session import get_db
    from app.main import create_app
    from app.models.user import MARKETING_TEAM_MEMBER_ROLE, User

    get_settings.cache_clear()
    settings = get_settings()
    test_url = settings.test_database_url or settings.database_url

    engine = create_engine(normalize_database_url(test_url), pool_pre_ping=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with testing_session() as db:
        db.add(
            User(
                email=ADMIN_EMAIL,
                username=ADMIN_USERNAME,
                hashed_password=hash_password(ADMIN_PASSWORD),
                role=MARKETING_TEAM_MEMBER_ROLE,
                is_active=True,
            )
        )
        db.add(
            User(
                email=INACTIVE_EMAIL,
                username="inactive_user",
                hashed_password=hash_password(INACTIVE_PASSWORD),
                role=MARKETING_TEAM_MEMBER_ROLE,
                is_active=False,
            )
        )
        db.add(
            User(
                email=WRONG_ROLE_EMAIL,
                username=WRONG_ROLE_USERNAME,
                hashed_password=hash_password(WRONG_ROLE_PASSWORD),
                role="admin",
                is_active=True,
            )
        )
        db.commit()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

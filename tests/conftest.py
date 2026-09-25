"""Shared pytest fixtures for integration and unit tests."""

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:root@127.0.0.1:5432/marketing_cal",
)
os.environ.setdefault(
    "TEST_DATABASE_URL",
    "postgresql://postgres:root@127.0.0.1:5432/marketing_cal_alex_test",
)
os.environ.setdefault(
    "JWT_SECRET",
    "test-jwt-secret-key-for-pytest-only-minimum-length",
)
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
os.environ.setdefault("AUTH_STRATEGY", "jwt")
os.environ.setdefault("CORS_ORIGINS", '["http://localhost:3000"]')
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("KLAVIYO_API_KEY", "pk_test_klaviyo_key")

ADMIN_EMAIL = "marketing.user@example.com"
ADMIN_USERNAME = "marketing_user"
ADMIN_PASSWORD = "SecurePass1!"
INACTIVE_EMAIL = "inactive.user@example.com"
INACTIVE_PASSWORD = "SecurePass1!"
WRONG_ROLE_EMAIL = "admin.user@example.com"
WRONG_ROLE_USERNAME = "admin_user"
WRONG_ROLE_PASSWORD = "SecurePass1!"


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

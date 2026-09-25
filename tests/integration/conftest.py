"""Integration test fixtures for marketing calendar API suite."""

from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token
from app.schemas.activity import KlaviyoPerformanceMetrics
from app.models.user import User
from tests.conftest import (
    INACTIVE_EMAIL,
    LOGIN_URL,
    MEMBER_EMAIL,
    TEST_PASSWORD,
    VIEWER_EMAIL,
)


@pytest.fixture
def member_auth_headers(db_client: TestClient) -> dict[str, str]:
    """Bearer token for the active marketing team member (regular user persona)."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": MEMBER_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    token = response.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def viewer_auth_headers(db_session_factory) -> dict[str, str]:
    """Bearer token for viewer persona — should be denied by get_current_user."""
    settings = get_settings()
    with db_session_factory() as db:
        user = db.query(User).filter(User.email == VIEWER_EMAIL).one()
        token = create_access_token({"sub": str(user.id)}, settings)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def inactive_member_auth_headers(db_session_factory) -> dict[str, str]:
    """Bearer token for inactive marketing member — should receive ACCOUNT_INACTIVE."""
    settings = get_settings()
    with db_session_factory() as db:
        user = db.query(User).filter(User.email == INACTIVE_EMAIL).one()
        token = create_access_token({"sub": str(user.id)}, settings)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def klaviyo_performance_enabled() -> Generator[None, None, None]:
    """Enable Klaviyo performance flag and mock external API for the duration of a test."""
    settings = get_settings()
    mock_metrics = KlaviyoPerformanceMetrics(
        revenue=1500.0,
        open_rate=0.42,
        click_rate=0.08,
        delivered_orders=120,
    )
    with (
        patch.object(settings, "klaviyo_performance_enabled", True),
        patch(
            "app.services.klaviyo_service.KlaviyoService.get_performance_for_campaign",
            return_value=mock_metrics,
        ),
        patch(
            "app.clients.klaviyo_client.KlaviyoClient.get_campaign_performance",
            return_value=mock_metrics,
        ),
    ):
        yield

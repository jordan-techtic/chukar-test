"""Unit tests for AuthService business logic."""

import os
import uuid
from unittest.mock import MagicMock

import pytest

from app.clients.klaviyo_client import KlaviyoClientError
from app.core.config import Settings
from app.exceptions.http_exceptions import ForbiddenError, UnauthorizedError
from app.models.user import MARKETING_TEAM_MEMBER_ROLE, User
from app.services.auth_service import AuthService


@pytest.fixture
def test_settings() -> Settings:
    """Return settings configured for unit tests."""
    return Settings(
        JWT_SECRET=os.environ["JWT_SECRET"],
        JWT_ALGORITHM=os.environ.get("JWT_ALGORITHM", "HS256"),
        KLAVIYO_API_KEY=os.environ.get("KLAVIYO_API_KEY", ""),
    )


@pytest.fixture
def active_user() -> User:
    """Return an active marketing team member model instance."""
    return User(
        id=uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
        email="marketing.user@example.com",
        username="marketing_user",
        hashed_password="hashed",
        role=MARKETING_TEAM_MEMBER_ROLE,
        is_active=True,
    )


@pytest.fixture
def inactive_user(active_user: User) -> User:
    """Return an inactive marketing team member model instance."""
    return User(
        id=active_user.id,
        email=active_user.email,
        username=active_user.username,
        hashed_password=active_user.hashed_password,
        role=MARKETING_TEAM_MEMBER_ROLE,
        is_active=False,
    )


def test_login_success_with_email(
    test_settings: Settings,
    active_user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Login with valid email credentials returns tokens and user summary."""
    db = MagicMock()
    klaviyo = MagicMock()
    service = AuthService(db, test_settings, klaviyo_client=klaviyo)

    monkeypatch.setattr(
        service._user_repo,
        "get_by_email_or_username",
        lambda _: active_user,
    )
    monkeypatch.setattr(
        "app.services.auth_service.verify_password",
        lambda _plain, _hash: True,
    )
    monkeypatch.setattr(
        "app.services.auth_service.create_access_token",
        lambda *_args, **_kwargs: "access-token",
    )
    monkeypatch.setattr(
        "app.services.auth_service.create_refresh_token",
        lambda *_args, **_kwargs: "refresh-token",
    )

    result = service.login(
        "marketing.user@example.com",
        os.environ["TEST_USER_PASSWORD"],
    )
    assert result.tokens.access_token == "access-token"
    assert result.tokens.refresh_token == "refresh-token"
    assert result.user.email == active_user.email


def test_login_unknown_user_raises_unauthorized(test_settings: Settings) -> None:
    """Unknown user should raise UnauthorizedError with INVALID_CREDENTIALS."""
    db = MagicMock()
    service = AuthService(db, test_settings, klaviyo_client=MagicMock())
    service._user_repo.get_by_email_or_username = MagicMock(return_value=None)

    with pytest.raises(UnauthorizedError) as exc_info:
        service.login("unknown@example.com", os.environ["TEST_USER_PASSWORD"])

    assert exc_info.value.code == "INVALID_CREDENTIALS"


def test_login_wrong_password_raises_unauthorized(
    test_settings: Settings,
    active_user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Wrong password should raise UnauthorizedError."""
    db = MagicMock()
    service = AuthService(db, test_settings, klaviyo_client=MagicMock())
    service._user_repo.get_by_email_or_username = MagicMock(return_value=active_user)
    monkeypatch.setattr(
        "app.services.auth_service.verify_password",
        lambda _plain, _hash: False,
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        service.login("marketing.user@example.com", "WrongPass1!")

    assert exc_info.value.code == "INVALID_CREDENTIALS"


def test_login_inactive_user_raises_forbidden(
    test_settings: Settings,
    inactive_user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Inactive user should raise ForbiddenError with ACCOUNT_INACTIVE."""
    db = MagicMock()
    service = AuthService(db, test_settings, klaviyo_client=MagicMock())
    service._user_repo.get_by_email_or_username = MagicMock(return_value=inactive_user)
    monkeypatch.setattr(
        "app.services.auth_service.verify_password",
        lambda _plain, _hash: True,
    )

    with pytest.raises(ForbiddenError) as exc_info:
        service.login(
            "marketing.user@example.com",
            os.environ["TEST_USER_PASSWORD"],
        )

    assert exc_info.value.code == "ACCOUNT_INACTIVE"


def test_login_wrong_role_raises_forbidden(
    test_settings: Settings,
    active_user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Non-marketing role should raise ForbiddenError with ACCESS_DENIED."""
    active_user.role = "admin"
    db = MagicMock()
    service = AuthService(db, test_settings, klaviyo_client=MagicMock())
    service._user_repo.get_by_email_or_username = MagicMock(return_value=active_user)
    monkeypatch.setattr(
        "app.services.auth_service.verify_password",
        lambda _plain, _hash: True,
    )

    with pytest.raises(ForbiddenError) as exc_info:
        service.login("admin.user@example.com", os.environ["TEST_USER_PASSWORD"])

    assert exc_info.value.code == "ACCESS_DENIED"


def test_forgot_password_unknown_email_same_response(test_settings: Settings) -> None:
    """Unknown email returns the same generic message."""
    db = MagicMock()
    klaviyo = MagicMock()
    service = AuthService(db, test_settings, klaviyo_client=klaviyo)
    service._user_repo.get_by_email_insensitive = MagicMock(return_value=None)

    result = service.forgot_password("unknown@example.com")
    assert "password reset link has been sent" in result.message.lower()
    klaviyo.send_password_reset_email.assert_not_called()


def test_forgot_password_existing_user_invokes_klaviyo(
    test_settings: Settings,
    active_user: User,
) -> None:
    """Registered active user triggers Klaviyo password reset delivery."""
    db = MagicMock()
    klaviyo = MagicMock()
    service = AuthService(db, test_settings, klaviyo_client=klaviyo)
    service._user_repo.get_by_email_insensitive = MagicMock(return_value=active_user)
    service._reset_repo.invalidate_active_tokens_for_user = MagicMock()
    service._reset_repo.create_token = MagicMock()

    result = service.forgot_password(active_user.email)
    assert "password reset link has been sent" in result.message.lower()
    klaviyo.send_password_reset_email.assert_called_once()
    service._reset_repo.create_token.assert_called_once()


def test_forgot_password_klaviyo_failure_still_returns_generic(
    test_settings: Settings,
    active_user: User,
) -> None:
    """Klaviyo failure should not change the generic response."""
    db = MagicMock()
    klaviyo = MagicMock()
    klaviyo.send_password_reset_email.side_effect = KlaviyoClientError("failed")
    service = AuthService(db, test_settings, klaviyo_client=klaviyo)
    service._user_repo.get_by_email_insensitive = MagicMock(return_value=active_user)
    service._reset_repo.invalidate_active_tokens_for_user = MagicMock()
    service._reset_repo.create_token = MagicMock()

    result = service.forgot_password(active_user.email)
    assert "password reset link has been sent" in result.message.lower()

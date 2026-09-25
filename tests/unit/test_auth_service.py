"""Unit tests for AuthService business logic."""

from unittest.mock import MagicMock

import pytest

from app.clients.klaviyo_client import KlaviyoClientError
from app.core.config import Settings
from app.exceptions.http_exceptions import ForbiddenError, UnauthorizedError
from app.models.user import MARKETING_TEAM_MEMBER_ROLE, User
from app.repositories.password_reset_token_repository import (
    PasswordResetTokenRepository,
)
from app.repositories.user_repository import UserRepository
from app.services.auth_service import FORGOT_PASSWORD_MESSAGE, AuthService


@pytest.fixture
def test_settings() -> Settings:
    """Return test settings."""
    return Settings(
        database_url="postgresql://postgres:root@127.0.0.1:5432/marketing_cal",
        jwt_secret="test-jwt-secret-key-for-pytest-only-minimum-length",
        frontend_reset_url="http://localhost:3000/reset-password",
        password_reset_token_expire_minutes=60,
        klaviyo_api_key="pk_test",
    )


@pytest.fixture
def active_user() -> User:
    """Return a mock active marketing team member."""
    user = MagicMock(spec=User)
    user.id = "550e8400-e29b-41d4-a716-446655440000"
    user.email = "marketing.user@example.com"
    user.username = "marketing_user"
    user.password_hash = "hashed"
    user.is_active = True
    user.role = MARKETING_TEAM_MEMBER_ROLE
    return user


def test_login_success_with_email(
    test_settings: Settings,
    active_user: User,
    monkeypatch,
) -> None:
    """Login succeeds with valid email credentials."""
    mock_db = MagicMock()
    mock_klaviyo = MagicMock()
    mock_repo = MagicMock(spec=UserRepository)
    mock_repo.get_by_email_or_username.return_value = active_user
    monkeypatch.setattr(
        "app.services.auth_service.UserRepository",
        lambda db: mock_repo,
    )
    monkeypatch.setattr(
        "app.services.auth_service.verify_password",
        lambda plain, hashed: True,
    )
    monkeypatch.setattr(
        "app.services.auth_service.create_access_token",
        lambda data, settings: "access-token",
    )
    monkeypatch.setattr(
        "app.services.auth_service.create_refresh_token",
        lambda data, settings: "refresh-token",
    )

    service = AuthService(mock_db, test_settings, klaviyo_client=mock_klaviyo)
    result = service.login("marketing.user@example.com", "SecurePass1!")

    assert result.access_token == "access-token"
    assert result.refresh_token == "refresh-token"
    assert result.user.email == active_user.email


def test_login_wrong_password_raises_unauthorized(
    test_settings: Settings,
    active_user: User,
    monkeypatch,
) -> None:
    """Login with wrong password raises UnauthorizedError."""
    mock_db = MagicMock()
    mock_repo = MagicMock(spec=UserRepository)
    mock_repo.get_by_email_or_username.return_value = active_user
    monkeypatch.setattr(
        "app.services.auth_service.UserRepository",
        lambda db: mock_repo,
    )
    monkeypatch.setattr(
        "app.services.auth_service.verify_password",
        lambda plain, hashed: False,
    )

    service = AuthService(mock_db, test_settings)
    with pytest.raises(UnauthorizedError) as exc_info:
        service.login("marketing.user@example.com", "WrongPass1!")
    assert exc_info.value.code == "INVALID_CREDENTIALS"


def test_login_unknown_user_raises_unauthorized(
    test_settings: Settings,
    monkeypatch,
) -> None:
    """Login with unknown user raises UnauthorizedError."""
    mock_db = MagicMock()
    mock_repo = MagicMock(spec=UserRepository)
    mock_repo.get_by_email_or_username.return_value = None
    monkeypatch.setattr(
        "app.services.auth_service.UserRepository",
        lambda db: mock_repo,
    )

    service = AuthService(mock_db, test_settings)
    with pytest.raises(UnauthorizedError) as exc_info:
        service.login("unknown@example.com", "SecurePass1!")
    assert exc_info.value.code == "INVALID_CREDENTIALS"


def test_login_inactive_user_raises_forbidden(
    test_settings: Settings,
    active_user: User,
    monkeypatch,
) -> None:
    """Login for inactive user raises ForbiddenError."""
    active_user.is_active = False
    mock_db = MagicMock()
    mock_repo = MagicMock(spec=UserRepository)
    mock_repo.get_by_email_or_username.return_value = active_user
    monkeypatch.setattr(
        "app.services.auth_service.UserRepository",
        lambda db: mock_repo,
    )
    monkeypatch.setattr(
        "app.services.auth_service.verify_password",
        lambda plain, hashed: True,
    )

    service = AuthService(mock_db, test_settings)
    with pytest.raises(ForbiddenError) as exc_info:
        service.login("marketing.user@example.com", "SecurePass1!")
    assert exc_info.value.code == "ACCOUNT_INACTIVE"


def test_login_wrong_role_raises_forbidden(
    test_settings: Settings,
    active_user: User,
    monkeypatch,
) -> None:
    """Login for user with wrong role raises ForbiddenError."""
    active_user.role = "other_role"
    mock_db = MagicMock()
    mock_repo = MagicMock(spec=UserRepository)
    mock_repo.get_by_email_or_username.return_value = active_user
    monkeypatch.setattr(
        "app.services.auth_service.UserRepository",
        lambda db: mock_repo,
    )
    monkeypatch.setattr(
        "app.services.auth_service.verify_password",
        lambda plain, hashed: True,
    )

    service = AuthService(mock_db, test_settings)
    with pytest.raises(ForbiddenError) as exc_info:
        service.login("marketing.user@example.com", "SecurePass1!")
    assert exc_info.value.code == "ACCESS_DENIED"


def test_forgot_password_existing_user_invokes_klaviyo(
    test_settings: Settings,
    active_user: User,
    monkeypatch,
) -> None:
    """Forgot password for registered user sends Klaviyo email."""
    mock_db = MagicMock()
    mock_klaviyo = MagicMock()
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user_repo.get_by_email.return_value = active_user
    mock_reset_repo = MagicMock(spec=PasswordResetTokenRepository)
    monkeypatch.setattr(
        "app.services.auth_service.UserRepository",
        lambda db: mock_user_repo,
    )
    monkeypatch.setattr(
        "app.services.auth_service.PasswordResetTokenRepository",
        lambda db: mock_reset_repo,
    )

    service = AuthService(mock_db, test_settings, klaviyo_client=mock_klaviyo)
    result = service.forgot_password("marketing.user@example.com")

    assert result.message == FORGOT_PASSWORD_MESSAGE
    mock_klaviyo.send_password_reset_email.assert_called_once()
    mock_reset_repo.invalidate_existing_for_user.assert_called_once()
    mock_reset_repo.create.assert_called_once()


def test_forgot_password_unknown_email_same_response(
    test_settings: Settings,
    monkeypatch,
) -> None:
    """Forgot password for unknown email returns generic message."""
    mock_db = MagicMock()
    mock_klaviyo = MagicMock()
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user_repo.get_by_email.return_value = None
    monkeypatch.setattr(
        "app.services.auth_service.UserRepository",
        lambda db: mock_user_repo,
    )

    service = AuthService(mock_db, test_settings, klaviyo_client=mock_klaviyo)
    result = service.forgot_password("unknown@example.com")

    assert result.message == FORGOT_PASSWORD_MESSAGE
    mock_klaviyo.send_password_reset_email.assert_not_called()


def test_forgot_password_klaviyo_failure_still_returns_generic(
    test_settings: Settings,
    active_user: User,
    monkeypatch,
) -> None:
    """Klaviyo failure does not expose error to client."""
    mock_db = MagicMock()
    mock_klaviyo = MagicMock()
    mock_klaviyo.send_password_reset_email.side_effect = KlaviyoClientError(
        "Failed"
    )
    mock_user_repo = MagicMock(spec=UserRepository)
    mock_user_repo.get_by_email.return_value = active_user
    mock_reset_repo = MagicMock(spec=PasswordResetTokenRepository)
    monkeypatch.setattr(
        "app.services.auth_service.UserRepository",
        lambda db: mock_user_repo,
    )
    monkeypatch.setattr(
        "app.services.auth_service.PasswordResetTokenRepository",
        lambda db: mock_reset_repo,
    )

    service = AuthService(mock_db, test_settings, klaviyo_client=mock_klaviyo)
    result = service.forgot_password("marketing.user@example.com")

    assert result.message == FORGOT_PASSWORD_MESSAGE

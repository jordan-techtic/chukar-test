"""CMC-50 integration tests: marketing team member login and forgot-password."""

import uuid
from datetime import timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from jose import JWTError, jwt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.security import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    verify_jwt_token,
)
from app.db.database_url import normalize_database_url
from app.models.password_reset_token import PasswordResetToken
from app.models.user import MARKETING_TEAM_MEMBER_ROLE
from tests.conftest import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    INACTIVE_EMAIL,
    WRONG_ROLE_EMAIL,
    WRONG_ROLE_PASSWORD,
)

LOGIN_URL = "/api/v1/marketing-team-member/login"
FORGOT_PASSWORD_URL = "/api/v1/marketing-team-member/forgot-password"


def test_cmc50_login_with_email_returns_tokens(db_client: TestClient) -> None:
    """Users can log in using registered email and password."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["tokens"]["access_token"]
    assert data["tokens"]["refresh_token"]


def test_cmc50_login_with_username_returns_tokens(db_client: TestClient) -> None:
    """Users can log in using registered username and password."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200


def test_cmc50_login_email_case_insensitive(db_client: TestClient) -> None:
    """Email login should be case-insensitive."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": ADMIN_EMAIL.upper(), "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200


def test_cmc50_login_unicode_username(db_client: TestClient) -> None:
    """Unicode usernames should be handled without server errors."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "usér_测试", "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 401


def test_cmc50_login_empty_password_422(db_client: TestClient) -> None:
    """Empty password should return validation error."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": ADMIN_EMAIL, "password": ""},
    )
    assert response.status_code == 422


def test_cmc50_login_unknown_user_401(db_client: TestClient) -> None:
    """Unknown user returns 401 INVALID_CREDENTIALS."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "nobody@example.com", "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_cmc50_login_invalid_password_401(db_client: TestClient) -> None:
    """Wrong password returns 401 INVALID_CREDENTIALS."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": ADMIN_EMAIL, "password": "WrongPass1!"},
    )
    assert response.status_code == 401


def test_cmc50_inactive_user_login_forbidden(db_client: TestClient) -> None:
    """Inactive users cannot log in."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": INACTIVE_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCOUNT_INACTIVE"


def test_cmc50_wrong_role_user_login_forbidden(db_client: TestClient) -> None:
    """Non-marketing team members are denied access."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": WRONG_ROLE_EMAIL, "password": WRONG_ROLE_PASSWORD},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCESS_DENIED"


def test_cmc50_access_token_has_access_type(db_client: TestClient) -> None:
    """Access tokens include type=access claim."""
    settings = get_settings()
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    token = response.json()["data"]["tokens"]["access_token"]
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    assert payload["type"] == TOKEN_TYPE_ACCESS


def test_cmc50_refresh_token_has_refresh_type(db_client: TestClient) -> None:
    """Refresh tokens include type=refresh claim."""
    settings = get_settings()
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    token = response.json()["data"]["tokens"]["refresh_token"]
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    assert payload["type"] == TOKEN_TYPE_REFRESH


def test_cmc50_expired_token_rejected() -> None:
    """Expired tokens are rejected during JWT verification."""
    settings = get_settings()
    expired_token = create_access_token(
        {"sub": str(uuid.uuid4())},
        settings,
        expires_delta=timedelta(seconds=-1),
    )
    with pytest.raises(JWTError):
        verify_jwt_token(expired_token, settings, expected_type=TOKEN_TYPE_ACCESS)


def test_cmc50_invalid_token_rejected() -> None:
    """Malformed tokens are rejected during JWT verification."""
    settings = get_settings()
    with pytest.raises(JWTError):
        verify_jwt_token("not-a-valid-jwt", settings, expected_type=TOKEN_TYPE_ACCESS)


def test_cmc50_forgot_password_initiates_recovery(db_client: TestClient) -> None:
    """Forgot password returns generic success message."""
    response = db_client.post(FORGOT_PASSWORD_URL, json={"email": ADMIN_EMAIL})
    assert response.status_code == 200
    assert "password reset link has been sent" in response.json()["data"]["message"].lower()


def test_cmc50_forgot_password_creates_reset_token_record(db_client: TestClient) -> None:
    """Forgot password persists a password reset token for registered users."""
    with patch("app.clients.klaviyo_client.KlaviyoClient.send_password_reset_email"):
        db_client.post(FORGOT_PASSWORD_URL, json={"email": ADMIN_EMAIL})

    from app.models.user import User

    settings = get_settings()
    test_url = settings.test_database_url or settings.database_url
    engine = create_engine(normalize_database_url(test_url))
    session = sessionmaker(bind=engine)()
    try:
        user = session.scalar(select(User).where(User.email == ADMIN_EMAIL))
        assert user is not None
        tokens = session.scalars(
            select(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
        ).all()
        assert len(tokens) >= 1
    finally:
        session.close()


def test_cmc50_forgot_password_email_case_insensitive(db_client: TestClient) -> None:
    """Forgot password email lookup is case-insensitive."""
    with patch("app.clients.klaviyo_client.KlaviyoClient.send_password_reset_email"):
        response = db_client.post(
            FORGOT_PASSWORD_URL,
            json={"email": ADMIN_EMAIL.upper()},
        )
    assert response.status_code == 200


def test_cmc50_forgot_password_inactive_user_no_klaviyo_call(
    db_client: TestClient,
) -> None:
    """Inactive users do not trigger Klaviyo password reset emails."""
    with patch(
        "app.clients.klaviyo_client.KlaviyoClient.send_password_reset_email",
    ) as mock_send:
        response = db_client.post(FORGOT_PASSWORD_URL, json={"email": INACTIVE_EMAIL})
    assert response.status_code == 200
    mock_send.assert_not_called()


def test_cmc50_forgot_password_unregistered_email_generic_200(
    db_client: TestClient,
) -> None:
    """Unregistered email returns same generic 200 without enumeration."""
    with patch(
        "app.clients.klaviyo_client.KlaviyoClient.send_password_reset_email",
    ) as mock_send:
        response = db_client.post(
            FORGOT_PASSWORD_URL,
            json={"email": "unknown.user@example.com"},
        )
    assert response.status_code == 200
    mock_send.assert_not_called()


def test_cmc50_forgot_password_invalid_email_422(db_client: TestClient) -> None:
    """Invalid email format returns 422 validation error."""
    response = db_client.post(FORGOT_PASSWORD_URL, json={"email": "not-an-email"})
    assert response.status_code == 422

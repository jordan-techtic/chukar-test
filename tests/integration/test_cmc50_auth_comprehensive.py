"""Comprehensive integration tests for CMC-50 marketing team member auth."""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH
from app.models.password_reset_token import PasswordResetToken
from app.models.user import MARKETING_TEAM_MEMBER_ROLE

LOGIN_URL = "/api/v1/marketing-team-member/login"
FORGOT_URL = "/api/v1/marketing-team-member/forgot-password"


# --- Happy path ---


def test_cmc50_login_with_email_returns_tokens(
    db_client: TestClient, admin_user, mock_klaviyo_client
) -> None:
    """CMC-50: Users can log in using registered email and password."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "admin@test.com", "password": "TestAdmin123!"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@test.com"
    assert data["user"]["role"] == MARKETING_TEAM_MEMBER_ROLE


def test_cmc50_login_with_username_returns_tokens(
    db_client: TestClient, regular_user, mock_klaviyo_client
) -> None:
    """CMC-50: Users can log in using registered username and password."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "regular_user", "password": "TestUser123!"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["user"]["username"] == "regular_user"


def test_cmc50_forgot_password_initiates_recovery(
    db_client: TestClient, admin_user, mock_klaviyo_client, db_session
) -> None:
    """CMC-50: Forgot password flow initiates for registered active user."""
    response = db_client.post(FORGOT_URL, json={"email": "admin@test.com"})
    assert response.status_code == 200
    assert "If an account exists" in response.json()["data"]["message"]
    mock_klaviyo_client.send_password_reset_email.assert_called_once()
    tokens = db_session.scalars(select(PasswordResetToken)).all()
    assert len(tokens) >= 1


# --- Access control ---


def test_cmc50_inactive_user_login_forbidden(
    db_client: TestClient, inactive_user, mock_klaviyo_client
) -> None:
    """CMC-50: Access restricted — inactive users cannot log in."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "inactive@test.com", "password": "TestInactive123!"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCOUNT_INACTIVE"


def test_cmc50_wrong_role_user_login_forbidden(
    db_client: TestClient, viewer_user, mock_klaviyo_client
) -> None:
    """CMC-50: Access restricted — non marketing_team_member role denied."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "viewer@test.com", "password": "TestViewer123!"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCESS_DENIED"


def test_cmc50_forgot_password_inactive_user_generic_response(
    db_client: TestClient, inactive_user, mock_klaviyo_client
) -> None:
    """CMC-50: Inactive user forgot-password returns generic 200, no Klaviyo call."""
    response = db_client.post(FORGOT_URL, json={"email": "inactive@test.com"})
    assert response.status_code == 200
    mock_klaviyo_client.send_password_reset_email.assert_not_called()


# --- Error cases ---


def test_cmc50_login_invalid_password_401(
    db_client: TestClient, admin_user, mock_klaviyo_client
) -> None:
    """CMC-50: Invalid credentials return 401 with stable error code."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "admin@test.com", "password": "WrongPass1!"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_cmc50_login_unknown_user_401(db_client: TestClient, mock_klaviyo_client) -> None:
    """CMC-50: Unknown user login returns 401 without enumeration leak."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "newuser@test.com", "password": "NewUser123!"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_cmc50_forgot_password_unregistered_email_generic_200(
    db_client: TestClient, mock_klaviyo_client
) -> None:
    """CMC-50: Unregistered email forgot-password returns same generic 200."""
    response = db_client.post(FORGOT_URL, json={"email": "newuser@test.com"})
    assert response.status_code == 200
    assert "If an account exists" in response.json()["data"]["message"]
    mock_klaviyo_client.send_password_reset_email.assert_not_called()


def test_cmc50_forgot_password_invalid_email_422(
    db_client: TestClient, mock_klaviyo_client
) -> None:
    """Error case: invalid email format returns 422 validation error."""
    response = db_client.post(FORGOT_URL, json={"email": "not-an-email"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# --- Edge cases ---


def test_cmc50_login_empty_password_422(db_client: TestClient, mock_klaviyo_client) -> None:
    """Edge case: empty password rejected by validation."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "admin@test.com", "password": ""},
    )
    assert response.status_code == 422


def test_cmc50_login_unicode_username_edge_case(
    db_client: TestClient, db_session, mock_klaviyo_client
) -> None:
    """Edge case: unicode username login when user exists with unicode username."""
    from app.core.security import hash_password
    from app.models.user import User

    user = User(
        email="unicode@test.com",
        username="usér_测试",
        password_hash=hash_password("Unicode1!"),
        is_active=True,
        role=MARKETING_TEAM_MEMBER_ROLE,
    )
    db_session.add(user)
    db_session.flush()
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "usér_测试", "password": "Unicode1!"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["user"]["username"] == "usér_测试"


def test_cmc50_login_email_case_insensitive(
    db_client: TestClient, admin_user, mock_klaviyo_client
) -> None:
    """Edge case: email lookup is case-insensitive."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "ADMIN@TEST.COM", "password": "TestAdmin123!"},
    )
    assert response.status_code == 200


def test_cmc50_forgot_password_email_case_insensitive(
    db_client: TestClient, regular_user, mock_klaviyo_client
) -> None:
    """Edge case: forgot-password accepts mixed-case email for registered user."""
    response = db_client.post(FORGOT_URL, json={"email": "USER@TEST.COM"})
    assert response.status_code == 200
    mock_klaviyo_client.send_password_reset_email.assert_called_once()


# --- Auth / JWT tests ---


def test_cmc50_login_access_token_is_access_type(
    db_client: TestClient, admin_user, mock_klaviyo_client
) -> None:
    """Auth: access token has type=access in JWT payload."""
    from app.core.security import decode_token

    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "admin@test.com", "password": "TestAdmin123!"},
    )
    payload = decode_token(response.json()["data"]["access_token"], get_settings())
    assert payload["type"] == TOKEN_TYPE_ACCESS


def test_cmc50_login_refresh_token_is_refresh_type(
    db_client: TestClient, admin_user, mock_klaviyo_client
) -> None:
    """Auth: refresh token has type=refresh in JWT payload."""
    from app.core.security import decode_token

    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "admin@test.com", "password": "TestAdmin123!"},
    )
    payload = decode_token(response.json()["data"]["refresh_token"], get_settings())
    assert payload["type"] == TOKEN_TYPE_REFRESH


def test_cmc50_expired_token_payload_rejected_by_decode(expired_access_token) -> None:
    """Auth: expired JWT raises on decode (simulates expired token rejection)."""
    from jose import JWTError
    from app.core.security import decode_token

    with pytest.raises(JWTError):
        decode_token(expired_access_token, get_settings())


def test_cmc50_invalid_token_string_rejected() -> None:
    """Auth: malformed token string rejected on decode."""
    from jose import JWTError
    from app.core.security import decode_token

    with pytest.raises(JWTError):
        decode_token("not.a.valid.jwt", get_settings())


# --- Data integrity ---


def test_cmc50_forgot_password_creates_reset_token_record(
    db_client: TestClient, regular_user, mock_klaviyo_client, db_session
) -> None:
    """Data integrity: forgot-password persists PasswordResetToken for active user."""
    before = db_session.scalars(select(PasswordResetToken)).all()
    db_client.post(FORGOT_URL, json={"email": "user@test.com"})
    after = db_session.scalars(select(PasswordResetToken)).all()
    assert len(after) == len(before) + 1
    assert after[-1].user_id == regular_user.id
    assert after[-1].expires_at > datetime.now(timezone.utc)

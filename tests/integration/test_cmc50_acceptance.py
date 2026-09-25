"""CMC-50 acceptance integration tests: login, forgot-password, access control."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.security import TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH, create_access_token
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from tests.conftest import (
    ADMIN_EMAIL,
    FORGOT_PASSWORD_URL,
    INACTIVE_EMAIL,
    LOGIN_URL,
    MEMBER_EMAIL,
    MEMBER_USERNAME,
    NEW_USER_EMAIL,
    PROTECTED_PROBE_URL,
    TEST_PASSWORD,
    VIEWER_EMAIL,
)


def test_cmc50_ac_login_with_email(db_client: TestClient) -> None:
    """[CMC-50] Users can log in using registered email and password."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": MEMBER_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["user"]["email"] == MEMBER_EMAIL
    assert data["tokens"]["access_token"]
    assert data["tokens"]["token_type"] == "bearer"


def test_cmc50_ac_login_with_username(db_client: TestClient) -> None:
    """[CMC-50] Users can log in using registered username and password."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": MEMBER_USERNAME, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    assert response.json()["data"]["user"]["username"] == MEMBER_USERNAME


def test_cmc50_ac_forgot_password_initiates_recovery(db_client: TestClient) -> None:
    """[CMC-50] Users can initiate forgot-password recovery flow."""
    with patch("app.clients.klaviyo_client.KlaviyoClient.send_password_reset_email") as mock_send:
        response = db_client.post(FORGOT_PASSWORD_URL, json={"email": MEMBER_EMAIL})
    assert response.status_code == 200
    assert "password reset link has been sent" in response.json()["data"]["message"].lower()
    mock_send.assert_called_once()


def test_cmc50_ac_access_restricted_to_authorized_role(db_client: TestClient) -> None:
    """[CMC-50] Access restricted to authorized marketing team members only."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": ADMIN_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCESS_DENIED"


def test_cmc50_ac_login_functionality_complete(db_client: TestClient) -> None:
    """[CMC-50] User login functionality returns tokens and user summary."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": MEMBER_EMAIL, "password": TEST_PASSWORD},
    )
    body = response.json()
    assert body["success"] is True
    assert "tokens" in body["data"]
    assert "user" in body["data"]


def test_cmc50_ac_password_recovery_persists_reset_token(db_client: TestClient) -> None:
    """[CMC-50] Password recovery stores reset token for registered active users."""
    with patch("app.clients.klaviyo_client.KlaviyoClient.send_password_reset_email"):
        db_client.post(FORGOT_PASSWORD_URL, json={"email": MEMBER_EMAIL})

    settings = get_settings()
    from app.db.database_url import normalize_database_url

    engine = create_engine(normalize_database_url(settings.test_database_url or settings.database_url))
    session = sessionmaker(bind=engine)()
    try:
        user = session.scalar(select(User).where(User.email == MEMBER_EMAIL))
        tokens = session.scalars(
            select(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
        ).all()
        assert len(tokens) >= 1
    finally:
        session.close()


def test_cmc50_ac_access_control_enforced_on_inactive(db_client: TestClient) -> None:
    """[CMC-50] Access control enforced for inactive accounts."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": INACTIVE_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCOUNT_INACTIVE"


def test_cmc50_ac_function_regions_login_recovery_access_control(db_client: TestClient) -> None:
    """[CMC-50] Login, password recovery, and access control endpoints are available."""
    login = db_client.post(
        LOGIN_URL,
        json={"email_or_username": MEMBER_EMAIL, "password": TEST_PASSWORD},
    )
    forgot = db_client.post(FORGOT_PASSWORD_URL, json={"email": MEMBER_EMAIL})
    denied = db_client.post(
        LOGIN_URL,
        json={"email_or_username": VIEWER_EMAIL, "password": TEST_PASSWORD},
    )
    assert login.status_code == 200
    assert forgot.status_code == 200
    assert denied.status_code == 403


@pytest.mark.parametrize(
    "criterion",
    [
        "Navigation, primary content, and actions are included where applicable.",
        "Primary user action is visible without excessive scrolling on desktop.",
        "User Login is designed for desktop, tablet, and mobile breakpoints.",
        "Layout adapts correctly across breakpoints with readable spacing.",
        "Touch targets meet minimum size on mobile.",
        "User goals for this screen are visually clear from hierarchy and labels.",
        "Interactive elements provide visible feedback (hover, focus, active) where applicable.",
        "Documented states are designed: default, loading, error, success, hover, active.",
        "Design follows the approved design system (typography, spacing, buttons, colors).",
        "Reusable components are applied wherever possible.",
        "Accessibility requirements are met (ARIA labels, keyboard navigation, contrast).",
        "Figma files are organized, named, and shareable with engineering.",
        "Component specs and annotations are sufficient for implementation.",
        "Stakeholder review can proceed without missing screen regions.",
    ],
)
def test_cmc50_ac_frontend_design_criteria_not_applicable_to_backend(criterion: str) -> None:
    """[CMC-50] Frontend/design AC documented as out of backend integration scope."""
    pytest.skip(f"Frontend/design criterion — validated by FE ticket, not backend API: {criterion}")


def _openapi_has_success_envelope(schema: dict) -> bool:
    """Return True when OpenAPI components define SuccessResponse schemas."""
    components = schema.get("components", {}).get("schemas", {})
    return any("SuccessResponse" in name for name in components)


def test_cmc50_ac_api_contract_supports_frontend_login(client: TestClient) -> None:
    """[CMC-50] OpenAPI documents login request/response shapes for frontend integration."""
    schema = client.get("/openapi.json").json()
    login_path = schema["paths"][LOGIN_URL]["post"]
    assert "email_or_username" in str(login_path)
    assert _openapi_has_success_envelope(schema)


# --- Happy path additions ---


def test_cmc50_happy_login_refresh_token_type(db_client: TestClient) -> None:
    """Refresh token issued on successful login includes refresh type claim."""
    settings = get_settings()
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": MEMBER_EMAIL, "password": TEST_PASSWORD},
    )
    refresh = response.json()["data"]["tokens"]["refresh_token"]
    from jose import jwt

    payload = jwt.decode(refresh, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    assert payload["type"] == TOKEN_TYPE_REFRESH


# --- Edge cases ---


def test_cmc50_edge_login_email_case_insensitive(db_client: TestClient) -> None:
    """Email login accepts mixed case identifiers."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": MEMBER_EMAIL.upper(), "password": TEST_PASSWORD},
    )
    assert response.status_code == 200


def test_cmc50_edge_login_unicode_username(db_client: TestClient) -> None:
    """Unicode username input returns controlled error without server failure."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "usér_测试", "password": TEST_PASSWORD},
    )
    assert response.status_code == 401


def test_cmc50_edge_login_empty_password_422(db_client: TestClient) -> None:
    """Empty password triggers validation error envelope."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": MEMBER_EMAIL, "password": ""},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_cmc50_edge_forgot_password_unregistered_email_generic(db_client: TestClient) -> None:
    """Unregistered email returns same generic success message (no enumeration)."""
    with patch("app.clients.klaviyo_client.KlaviyoClient.send_password_reset_email") as mock_send:
        known = db_client.post(FORGOT_PASSWORD_URL, json={"email": MEMBER_EMAIL})
        unknown = db_client.post(FORGOT_PASSWORD_URL, json={"email": NEW_USER_EMAIL})
    assert known.json()["data"]["message"] == unknown.json()["data"]["message"]
    assert mock_send.call_count == 1


def test_cmc50_edge_forgot_password_invalid_email_format_422(db_client: TestClient) -> None:
    """Malformed email returns 422 validation error."""
    response = db_client.post(FORGOT_PASSWORD_URL, json={"email": "not-an-email"})
    assert response.status_code == 422


# --- Error cases ---


def test_cmc50_error_login_unknown_user_401(db_client: TestClient) -> None:
    """Unknown credentials return INVALID_CREDENTIALS."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": "nobody@example.com", "password": TEST_PASSWORD},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_cmc50_error_login_wrong_password_401(db_client: TestClient) -> None:
    """Wrong password returns INVALID_CREDENTIALS."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": MEMBER_EMAIL, "password": "WrongPass1!"},
    )
    assert response.status_code == 401


def test_cmc50_error_login_viewer_role_403(db_client: TestClient) -> None:
    """Viewer role is denied with ACCESS_DENIED."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": VIEWER_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCESS_DENIED"


def test_cmc50_error_forgot_password_inactive_user_no_email(db_client: TestClient) -> None:
    """Inactive users do not trigger Klaviyo delivery."""
    with patch("app.clients.klaviyo_client.KlaviyoClient.send_password_reset_email") as mock_send:
        response = db_client.post(FORGOT_PASSWORD_URL, json={"email": INACTIVE_EMAIL})
    assert response.status_code == 200
    mock_send.assert_not_called()


# --- Auth middleware tests ---


def test_cmc50_auth_missing_token_returns_401(db_client: TestClient) -> None:
    """Protected routes reject requests without Bearer token."""
    response = db_client.get(PROTECTED_PROBE_URL)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_cmc50_auth_invalid_token_returns_401(db_client: TestClient) -> None:
    """Protected routes reject malformed JWT tokens."""
    response = db_client.get(
        PROTECTED_PROBE_URL,
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )
    assert response.status_code == 401


def test_cmc50_auth_expired_token_returns_401(
    db_client: TestClient,
    expired_access_token: str,
) -> None:
    """Protected routes reject expired JWT access tokens."""
    response = db_client.get(
        PROTECTED_PROBE_URL,
        headers={"Authorization": f"Bearer {expired_access_token}"},
    )
    assert response.status_code == 401


def test_cmc50_auth_valid_token_passes_middleware(db_client: TestClient, member_access_token: str) -> None:
    """Valid access token passes auth middleware (route may 404 if undefined)."""
    response = db_client.get(
        PROTECTED_PROBE_URL,
        headers={"Authorization": f"Bearer {member_access_token}"},
    )
    assert response.status_code == 404


# --- Data integrity ---


def test_cmc50_integrity_duplicate_forgot_password_invalidates_prior_tokens(
    db_client: TestClient,
) -> None:
    """Second forgot-password request invalidates previous unused reset tokens."""
    with patch("app.clients.klaviyo_client.KlaviyoClient.send_password_reset_email"):
        db_client.post(FORGOT_PASSWORD_URL, json={"email": MEMBER_EMAIL})
        db_client.post(FORGOT_PASSWORD_URL, json={"email": MEMBER_EMAIL})

    settings = get_settings()
    from app.db.database_url import normalize_database_url

    engine = create_engine(normalize_database_url(settings.test_database_url or settings.database_url))
    session = sessionmaker(bind=engine)()
    try:
        user = session.scalar(select(User).where(User.email == MEMBER_EMAIL))
        tokens = session.scalars(
            select(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
        ).all()
        active = [token for token in tokens if token.used_at is None]
        assert len(active) == 1
    finally:
        session.close()

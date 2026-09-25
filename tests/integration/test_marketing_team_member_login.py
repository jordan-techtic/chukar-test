"""Integration tests for marketing team member auth endpoints."""

from fastapi.testclient import TestClient

from tests.conftest import (
    INACTIVE_EMAIL,
    MEMBER_EMAIL,
    MEMBER_USERNAME,
    TEST_PASSWORD,
)


def test_post_login_email_returns_200_and_tokens(db_client: TestClient) -> None:
    """Login with email returns 200 and JWT tokens."""
    response = db_client.post(
        "/api/v1/marketing-team-member/login",
        json={"email_or_username": MEMBER_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["tokens"]["access_token"]
    assert body["data"]["tokens"]["refresh_token"]
    assert body["data"]["user"]["email"] == MEMBER_EMAIL


def test_post_login_username_returns_200_and_tokens(db_client: TestClient) -> None:
    """Login with username returns 200 and JWT tokens."""
    response = db_client.post(
        "/api/v1/marketing-team-member/login",
        json={"email_or_username": MEMBER_USERNAME, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["user"]["username"] == MEMBER_USERNAME


def test_post_login_invalid_credentials_401(db_client: TestClient) -> None:
    """Invalid credentials return 401 with INVALID_CREDENTIALS."""
    response = db_client.post(
        "/api/v1/marketing-team-member/login",
        json={"email_or_username": MEMBER_EMAIL, "password": "WrongPass1!"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


def test_post_login_inactive_user_403(db_client: TestClient) -> None:
    """Inactive user login returns 403 with ACCOUNT_INACTIVE."""
    response = db_client.post(
        "/api/v1/marketing-team-member/login",
        json={"email_or_username": INACTIVE_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 403
    body = response.json()
    assert body["error"]["code"] == "ACCOUNT_INACTIVE"


def test_post_login_validation_error_422(db_client: TestClient) -> None:
    """Missing password returns 422 validation error envelope."""
    response = db_client.post(
        "/api/v1/marketing-team-member/login",
        json={"email_or_username": MEMBER_EMAIL},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_post_forgot_password_registered_email_200(db_client: TestClient) -> None:
    """Forgot password for registered email returns 200 generic message."""
    response = db_client.post(
        "/api/v1/marketing-team-member/forgot-password",
        json={"email": MEMBER_EMAIL},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "password reset link has been sent" in body["data"]["message"].lower()


def test_post_forgot_password_unregistered_email_200_same_body(
    db_client: TestClient,
) -> None:
    """Forgot password for unknown email returns same generic 200 message."""
    registered = db_client.post(
        "/api/v1/marketing-team-member/forgot-password",
        json={"email": MEMBER_EMAIL},
    )
    unregistered = db_client.post(
        "/api/v1/marketing-team-member/forgot-password",
        json={"email": "unknown.user@example.com"},
    )
    assert registered.status_code == 200
    assert unregistered.status_code == 200
    assert registered.json()["data"]["message"] == unregistered.json()["data"]["message"]

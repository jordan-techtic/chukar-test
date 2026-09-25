"""Integration tests for marketing team member auth endpoints."""

from fastapi.testclient import TestClient


def test_post_login_email_returns_200_and_tokens(
    db_client: TestClient,
    seed_user,
) -> None:
    """POST login with email returns tokens and user summary."""
    response = db_client.post(
        "/api/v1/marketing-team-member/login",
        json={
            "email_or_username": "marketing.user@example.com",
            "password": "SecurePass1!",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Login successful."
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["user"]["email"] == "marketing.user@example.com"
    assert body["data"]["user"]["role"] == "marketing_team_member"


def test_post_login_username_returns_200_and_tokens(
    db_client: TestClient,
    seed_user,
) -> None:
    """POST login with username returns tokens."""
    response = db_client.post(
        "/api/v1/marketing-team-member/login",
        json={
            "email_or_username": "marketing_user",
            "password": "SecurePass1!",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["user"]["username"] == "marketing_user"


def test_post_login_invalid_credentials_401(
    db_client: TestClient,
    seed_user,
) -> None:
    """POST login with wrong password returns 401."""
    response = db_client.post(
        "/api/v1/marketing-team-member/login",
        json={
            "email_or_username": "marketing.user@example.com",
            "password": "WrongPass1!",
        },
    )
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


def test_post_login_inactive_user_403(
    db_client: TestClient,
    inactive_user,
) -> None:
    """POST login for inactive user returns 403."""
    response = db_client.post(
        "/api/v1/marketing-team-member/login",
        json={
            "email_or_username": "inactive.user@example.com",
            "password": "SecurePass1!",
        },
    )
    assert response.status_code == 403
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "ACCOUNT_INACTIVE"


def test_post_forgot_password_registered_email_200(
    db_client: TestClient,
    seed_user,
    mock_klaviyo_client,
) -> None:
    """POST forgot-password for registered email returns generic 200."""
    response = db_client.post(
        "/api/v1/marketing-team-member/forgot-password",
        json={"email": "marketing.user@example.com"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "If an account exists" in body["data"]["message"]
    mock_klaviyo_client.send_password_reset_email.assert_called_once()


def test_post_forgot_password_unregistered_email_200_same_body(
    db_client: TestClient,
    mock_klaviyo_client,
) -> None:
    """POST forgot-password for unknown email returns same generic 200."""
    response = db_client.post(
        "/api/v1/marketing-team-member/forgot-password",
        json={"email": "unknown@example.com"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "If an account exists" in body["data"]["message"]
    mock_klaviyo_client.send_password_reset_email.assert_not_called()


def test_post_login_validation_error_422(db_client: TestClient) -> None:
    """POST login with missing fields returns 422 validation error."""
    response = db_client.post(
        "/api/v1/marketing-team-member/login",
        json={"email_or_username": "user@example.com"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(body["error"]["details"], list)

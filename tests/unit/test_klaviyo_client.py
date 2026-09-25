"""Unit tests for KlaviyoClient adapter."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.clients.klaviyo_client import KlaviyoClient, KlaviyoClientError
from app.core.config import Settings


@pytest.fixture
def klaviyo_settings() -> Settings:
    """Return settings with Klaviyo API key configured."""
    return Settings(
        database_url="postgresql://postgres:root@127.0.0.1:5432/marketing_cal",
        jwt_secret="test-jwt-secret-key-for-pytest-only-minimum-length",
        klaviyo_api_key="pk_test_key",
        klaviyo_api_base_url="https://a.klaviyo.com",
        klaviyo_api_revision="2024-10-15",
    )


def test_send_password_reset_email_success(
    klaviyo_settings: Settings,
) -> None:
    """Successful Klaviyo API call completes without error."""
    client = KlaviyoClient(klaviyo_settings)
    mock_response = MagicMock()
    mock_response.status_code = 202

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        client.send_password_reset_email(
            to_email="user@example.com",
            reset_link="http://localhost:3000/reset?token=abc",
            user_name="testuser",
        )

        mock_client.post.assert_called_once()


def test_send_password_reset_email_retries_on_500(
    klaviyo_settings: Settings,
) -> None:
    """Klaviyo client retries on server errors."""
    client = KlaviyoClient(klaviyo_settings)
    fail_response = MagicMock()
    fail_response.status_code = 503
    success_response = MagicMock()
    success_response.status_code = 202

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.post.side_effect = [fail_response, success_response]
        mock_client_cls.return_value = mock_client

        with patch("time.sleep"):
            client.send_password_reset_email(
                to_email="user@example.com",
                reset_link="http://localhost:3000/reset?token=abc",
                user_name="testuser",
            )

        assert mock_client.post.call_count == 2


def test_send_password_reset_email_failure_after_retries(
    klaviyo_settings: Settings,
) -> None:
    """Klaviyo client raises after max retries exhausted."""
    client = KlaviyoClient(klaviyo_settings)
    fail_response = MagicMock()
    fail_response.status_code = 503

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.post.return_value = fail_response
        mock_client_cls.return_value = mock_client

        with patch("time.sleep"):
            with pytest.raises(KlaviyoClientError):
                client.send_password_reset_email(
                    to_email="user@example.com",
                    reset_link="http://localhost:3000/reset?token=abc",
                    user_name="testuser",
                )


def test_send_password_reset_email_missing_api_key(
    klaviyo_settings: Settings,
) -> None:
    """Missing API key raises KlaviyoClientError."""
    klaviyo_settings.klaviyo_api_key = ""
    client = KlaviyoClient(klaviyo_settings)
    with pytest.raises(KlaviyoClientError):
        client.send_password_reset_email(
            to_email="user@example.com",
            reset_link="http://localhost:3000/reset?token=abc",
            user_name="testuser",
        )


def test_send_password_reset_email_request_error_retries(
    klaviyo_settings: Settings,
) -> None:
    """Network errors trigger retry logic."""
    client = KlaviyoClient(klaviyo_settings)

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.post.side_effect = httpx.ConnectError("connection refused")
        mock_client_cls.return_value = mock_client

        with patch("time.sleep"):
            with pytest.raises(KlaviyoClientError):
                client.send_password_reset_email(
                    to_email="user@example.com",
                    reset_link="http://localhost:3000/reset?token=abc",
                    user_name="testuser",
                )

        assert mock_client.post.call_count == 3

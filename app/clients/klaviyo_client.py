"""Klaviyo API client for transactional password reset emails."""

import time
from typing import Any

import httpx

from app.core.config import Settings
from app.core.logging import logger


class KlaviyoClientError(Exception):
    """Raised when Klaviyo API communication fails after retries."""


class KlaviyoClient:
    """Encapsulates Klaviyo HTTP integration with retry logic."""

    MAX_RETRIES = 3
    BACKOFF_SECONDS = 1.0

    def __init__(self, settings: Settings) -> None:
        """Initialize client with application settings."""
        self._settings = settings
        self._api_key = settings.klaviyo_api_key
        self._base_url = settings.klaviyo_api_base_url.rstrip("/")

    def send_password_reset_email(
        self,
        *,
        to_email: str,
        reset_link: str,
        user_name: str,
    ) -> None:
        """Send a password reset email via Klaviyo Events API.

        Args:
            to_email: Recipient email address.
            reset_link: Password reset URL containing the token.
            user_name: Display name for email personalization.

        Raises:
            KlaviyoClientError: If the API call fails after all retries.
        """
        if not self._api_key:
            logger.error("KLAVIYO_API_KEY is not configured")
            raise KlaviyoClientError("Email service is not configured.")

        payload = self._build_event_payload(
            to_email=to_email,
            reset_link=reset_link,
            user_name=user_name,
        )
        headers = {
            "Authorization": f"Klaviyo-API-Key {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "revision": self._settings.klaviyo_api_revision,
        }
        url = f"{self._base_url}/api/events/"

        last_error: Exception | None = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                with httpx.Client(timeout=10.0) as client:
                    response = client.post(url, json=payload, headers=headers)
                if response.status_code in (200, 201, 202):
                    logger.info(
                        "Password reset email event sent to Klaviyo for {}",
                        to_email,
                    )
                    return
                if response.status_code >= 500:
                    last_error = KlaviyoClientError(
                        f"Klaviyo server error: HTTP {response.status_code}"
                    )
                    logger.warning(
                        "Klaviyo attempt {}/{} failed with HTTP {}",
                        attempt,
                        self.MAX_RETRIES,
                        response.status_code,
                    )
                else:
                    logger.error(
                        "Klaviyo client error HTTP {}: {}",
                        response.status_code,
                        response.text,
                    )
                    raise KlaviyoClientError(
                        "Failed to send password reset email."
                    )
            except httpx.RequestError as exc:
                last_error = exc
                logger.warning(
                    "Klaviyo attempt {}/{} request error: {}",
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )

            if attempt < self.MAX_RETRIES:
                time.sleep(self.BACKOFF_SECONDS * attempt)

        raise KlaviyoClientError(
            "Failed to send password reset email after retries."
        ) from last_error

    def _build_event_payload(
        self,
        *,
        to_email: str,
        reset_link: str,
        user_name: str,
    ) -> dict[str, Any]:
        """Build Klaviyo Events API v3 payload for password reset."""
        return {
            "data": {
                "type": "event",
                "attributes": {
                    "metric": {
                        "data": {
                            "type": "metric",
                            "attributes": {
                                "name": "Password Reset Requested",
                            },
                        }
                    },
                    "profile": {
                        "data": {
                            "type": "profile",
                            "attributes": {
                                "email": to_email,
                                "first_name": user_name,
                            },
                        }
                    },
                    "properties": {
                        "reset_link": reset_link,
                        "user_name": user_name,
                    },
                },
            }
        }

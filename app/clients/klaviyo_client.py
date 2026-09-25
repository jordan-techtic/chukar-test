"""Klaviyo API client for transactional password reset emails."""

import time
from typing import Any

import httpx

from app.core.config import Settings
from app.core.logging import logger

KLAVIYO_EVENTS_URL = "https://a.klaviyo.com/api/events/"
KLAVIYO_API_REVISION = "2024-02-15"
PASSWORD_RESET_METRIC_NAME = "Password Reset Requested"


class KlaviyoClientError(Exception):
    """Raised when Klaviyo API communication fails after retries."""


class KlaviyoClient:
    """Adapter for sending password reset events via the Klaviyo Events API."""

    def __init__(self, settings: Settings) -> None:
        """Initialize with application settings."""
        self._settings = settings

    def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
    ) -> None:
        """Trigger a Klaviyo password reset event with retry on transient failures."""
        api_key = self._settings.klaviyo_api_key.strip()
        if not api_key:
            raise KlaviyoClientError("Klaviyo API key is not configured.")

        reset_url = self._build_reset_url(reset_token)
        payload = self._build_event_payload(to_email, reset_token, reset_url)
        headers = {
            "Authorization": f"Klaviyo-API-Key {api_key}",
            "revision": KLAVIYO_API_REVISION,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        last_error: Exception | None = None
        max_attempts = max(1, self._settings.klaviyo_max_retries)

        for attempt in range(1, max_attempts + 1):
            try:
                with httpx.Client(timeout=10.0) as client:
                    response = client.post(KLAVIYO_EVENTS_URL, json=payload, headers=headers)

                if response.status_code < 400:
                    logger.info("Klaviyo password reset event sent for {}", to_email)
                    return

                if response.status_code >= 500 and attempt < max_attempts:
                    logger.warning(
                        "Klaviyo returned {} on attempt {}/{} for {}",
                        response.status_code,
                        attempt,
                        max_attempts,
                        to_email,
                    )
                    time.sleep(0.5 * attempt)
                    continue

                raise KlaviyoClientError(
                    f"Klaviyo API returned status {response.status_code}",
                )
            except httpx.RequestError as exc:
                last_error = exc
                if attempt < max_attempts:
                    logger.warning(
                        "Klaviyo request error on attempt {}/{} for {}: {}",
                        attempt,
                        max_attempts,
                        to_email,
                        exc,
                    )
                    time.sleep(0.5 * attempt)
                    continue
                raise KlaviyoClientError("Klaviyo request failed.") from exc

        raise KlaviyoClientError("Klaviyo request failed after retries.") from last_error

    def _build_reset_url(self, reset_token: str) -> str:
        """Construct the frontend password reset URL with the token."""
        base_url = self._settings.frontend_reset_url.rstrip("/")
        separator = "&" if "?" in base_url else "?"
        return f"{base_url}{separator}token={reset_token}"

    def _build_event_payload(
        self,
        to_email: str,
        reset_token: str,
        reset_url: str,
    ) -> dict[str, Any]:
        """Build Klaviyo Events API payload for password reset."""
        return {
            "data": {
                "type": "event",
                "attributes": {
                    "properties": {
                        "reset_token": reset_token,
                        "reset_url": reset_url,
                    },
                    "metric": {
                        "data": {
                            "type": "metric",
                            "attributes": {"name": PASSWORD_RESET_METRIC_NAME},
                        }
                    },
                    "profile": {
                        "data": {
                            "type": "profile",
                            "attributes": {"email": to_email},
                        }
                    },
                },
            }
        }

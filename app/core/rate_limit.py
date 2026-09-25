"""Rate limiting configuration using slowapi."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import Settings

limiter = Limiter(key_func=get_remote_address, enabled=True)


def configure_rate_limiting(settings: Settings) -> None:
    """Apply rate-limit on/off from application settings."""
    limiter.enabled = settings.rate_limiting_active

"""Rate limiting configuration using slowapi."""

from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import Settings, get_settings

settings: Settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
)


def configure_rate_limiting(app: FastAPI) -> None:
    """Attach the shared limiter instance to the FastAPI application."""
    app.state.limiter = limiter
